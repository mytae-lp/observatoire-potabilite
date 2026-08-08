# -*- coding: utf-8 -*-
"""
Test de bout en bout du moteur de réétalonnage, sans réseau.

    python3 tests/test_verdict.py

Il fabrique un bulletin complet fictif, l'ingère, et vérifie que les règles de
méthode du projet sont effectivement appliquées par les vues :

  1. la bascule 2016 -> 2026 est détectée ;
  2. un seuil différé (plomb 2036) ne produit pas de faux dépassement aujourd'hui ;
  3. une valeur non quantifiée dont la LQ dépasse le seuil strict est
     INDÉTERMINÉE, jamais conforme ;
  4. l'appariement par code_parametre, par libellé, par alias et par règle de
     famille fonctionne, et ce qui n'est apparié par aucun des quatre est visible ;
  5. un lot de lignes portant plusieurs prélèvements est REFUSÉ ;
  6. la limite déclarée par la source complète le référentiel sans jamais
     fabriquer de bascule ni de passé réglementaire.

À lancer après toute modification de common.py, ingest.py ou des vues.
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import duckdb  # noqa: E402
import build_db  # noqa: E402
import ingest  # noqa: E402
from common import SEUIL_COMPLET, norm  # noqa: E402

ECHECS = []
PREL = "TEST-0001"


def verifie(condition, message):
    print(("  ok   " if condition else "  ECHEC ") + message)
    if not condition:
        ECHECS.append(message)


def bulletin_fictif():
    """Un bulletin complet fabriqué : chaque ligne teste une règle précise."""
    rows = [
        # --- 1. LA BASCULE ---------------------------------------------------
        # ESA métolachlore : 0,42 µg/L. Au-dessus de la limite 2016 (0,1) et
        # sous celle de 2026 (0,9, métabolite classé non pertinent).
        # Apparié par code_parametre Hub'Eau.
        {"code_parametre": "6854", "libelle_parametre": "ESA metolachlore",
         "resultat_alphanumerique": "0,42", "resultat_numerique": 0.42,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=0,9 µg/L"},

        # Antimoine : 7 µg/L. Limite relevée de 5 à 10 en 2023 -> bascule.
        # La source déclare ici 5 µg/L : le RÉFÉRENTIEL prime (10), et l'écart
        # doit être signalé pour vérification.
        {"code_parametre": None, "libelle_parametre": "Antimoine",
         "resultat_alphanumerique": "7", "resultat_numerique": 7.0,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=5 µg/L"},

        # --- 2. SEUIL DIFFÉRÉ ------------------------------------------------
        # Plomb : 7 µg/L. Limite applicable AUJOURD'HUI 10 µg/L -> conforme.
        # Limite de 2036 : 5 µg/L -> dépassera. Ne doit PAS compter comme
        # dépassement 2026 (cf. CLAUDE.md §2.5).
        {"code_parametre": None, "libelle_parametre": "Plomb",
         "resultat_alphanumerique": "7", "resultat_numerique": 7.0,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=10 µg/L"},

        # --- 3. NON QUANTIFIÉ / INDÉTERMINÉ ---------------------------------
        # Somme de 4 PFAS non quantifiée, LQ = 0,004 µg/L, seuil strict
        # danois 0,002 µg/L : la LQ est au-dessus du seuil, on ne sait pas.
        {"code_parametre": "9268",
         "libelle_parametre": "Somme de 4 substances perfluoroalkylees (PFOA+PFNA+PFHXS+PFOS)",
         "resultat_alphanumerique": "<0,004", "resultat_numerique": 0.0,
         "libelle_unite": "µg/L"},

        # Un « 0 » sec : non quantifié, LQ inconnue. Ne doit jamais compter
        # comme une absence ni produire de verdict.
        {"code_parametre": None, "libelle_parametre": "Mercure",
         "resultat_alphanumerique": "0", "resultat_numerique": 0.0,
         "libelle_unite": "µg/L"},

        # --- 3bis. LE PLAFOND ANALYTIQUE (chantier C4) -----------------------
        # Hydrazide maléique non quantifiée avec une LQ de 0,5 µg/L, pour une
        # limite déclarée de 0,1. Le laboratoire ne voit RIEN dans la zone où
        # la conformité se joue : ce n'est ni un conforme ni un dépassement.
        # Valeurs authentiques — le corpus porte des LQ de 0,05 à 2,5 µg/L pour
        # cette molécule, soit un facteur 50 entre deux communes.
        {"code_parametre": "99905", "libelle_parametre": "Hydrazide maleique",
         "resultat_alphanumerique": "<0,5", "resultat_numerique": 0.0,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=0,1 µg/L"},

        # Le contre-exemple, et il est indispensable. La limite de qualité de la
        # bactériologie est ZÉRO, et la « LQ » d'un dénombrement vaut 1 : on ne
        # compte pas une demi-bactérie. Aucune LQ ne peut passer sous zéro —
        # déclarer cette ligne « aveugle » serait un faux positif, et il y en
        # aurait 69 dans le corpus, qui noieraient les 46 cas réels.
        #
        # Ce libellé-ci est celui de la source, et il ne rejoint AUCUNE ligne du
        # référentiel : son seuil vient de la limite déclarée, `seuil_strict`
        # reste vide. C'est l'état réel du corpus au 8 août 2026.
        {"code_parametre": "99906", "libelle_parametre": "Escherichia coli /100ml - MF",
         "resultat_alphanumerique": "<1", "resultat_numerique": 0.0,
         "libelle_unite": "n/(100mL)", "limite_qualite_parametre": "<=0 n/(100mL)"},

        # Le même cas, mais APPARIÉ au référentiel — libellé et unité exacts.
        # Il porte alors un `seuil_strict` de 0, et c'est lui qui vérifie que
        # `indetermine_strict` ne se perce pas non plus par le bas. Sans la
        # garde, cette ligne serait « indéterminée » : le corpus n'y échappait
        # que parce qu'aucun alias ne mène des libellés de la source à ces
        # trois lignes du référentiel.
        {"code_parametre": None, "libelle_parametre": "Enterocoques",
         "resultat_alphanumerique": "<1", "resultat_numerique": 0.0,
         "libelle_unite": "n/100mL"},

        # --- 4. APPARIEMENT --------------------------------------------------
        # Par alias : « nitrates » -> « Nitrates (en NO3) ».
        # 38 mg/L : conforme aux 50 mg/L, au-dessus du repère nourrisson 10.
        {"code_parametre": None, "libelle_parametre": "Nitrates",
         "resultat_alphanumerique": "38", "resultat_numerique": 38.0,
         "libelle_unite": "mg/L"},

        # Par libellé exact, avec un dépassement franc en 2016 ET en 2026.
        {"code_parametre": None, "libelle_parametre": "Nitrites (en NO2)",
         "resultat_alphanumerique": "0,8", "resultat_numerique": 0.8,
         "libelle_unite": "mg/L"},

        # Suffixe d'unité collé au libellé : doit rejoindre « Aluminium total »
        # (référence 200 µg/L) après normalisation, et non partir en orphelin.
        {"code_parametre": None, "libelle_parametre": "Aluminium total µg/l",
         "resultat_alphanumerique": "150", "resultat_numerique": 150.0,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=200 µg/L"},

        # --- 5. RÈGLE DE FAMILLE (les ~300 pesticides nommés) ----------------
        # Codes 999xx volontairement hors de la plage Hub'Eau réelle : le
        # référentiel grandit, et un code inventé au hasard finit par exister
        # pour de bon. « Boscalid » portait 1907, qui est le code de l'AMPA :
        # le faux paramètre s'appariait à une vraie ligne et faussait l'indice
        # de danger. Les tests l'ont vu.
        # Pesticide inconnu du référentiel, limite déclarée 0,1 µg/L :
        # rattaché à « Pesticide - substance individuelle ». Conforme.
        {"code_parametre": "99901", "libelle_parametre": "Boscalid",
         "resultat_alphanumerique": "0,05", "resultat_numerique": 0.05,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=0,1 µg/L"},

        # Même règle, mais au-dessus : dépassement 2016 ET 2026 (la limite
        # pesticide n'a pas bougé) -> surtout PAS une bascule.
        {"code_parametre": "99902", "libelle_parametre": "Quinmerac",
         "resultat_alphanumerique": "0,25", "resultat_numerique": 0.25,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=0,1 µg/L"},

        # --- 6. LIMITE DÉCLARÉE SEULE (hors référentiel) --------------------
        # Absent du référentiel : la limite déclarée donne la grille 2026 et
        # rien d'autre. Dépassement aujourd'hui, aucun verdict 2016.
        {"code_parametre": "99903", "libelle_parametre": "Manganese total",
         "resultat_alphanumerique": "60", "resultat_numerique": 60.0,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=50 µg/L"},

        # --- 7. AUCUN SEUIL DU TOUT -----------------------------------------
        # Ni référentiel, ni limite déclarée : mesure invisible, à signaler.
        {"code_parametre": "99904", "libelle_parametre": "Calcium",
         "resultat_alphanumerique": "80", "resultat_numerique": 80.0,
         "libelle_unite": "mg/L"},

        # Résultat qualitatif : ne doit rien casser.
        {"code_parametre": None, "libelle_parametre": "Aspect",
         "resultat_alphanumerique": "Aucune anomalie", "resultat_numerique": None,
         "libelle_unite": None},
    ]
    # Remplissage pour franchir SEUIL_COMPLET : le bulletin doit être COMPLET,
    # sinon aucune requête d'analyse ne le retiendra (CLAUDE.md §2.3).
    for i in range(SEUIL_COMPLET + 11 - len(rows)):
        rows.append({"code_parametre": None, "libelle_parametre": f"Remplissage {i:03d}",
                     "resultat_alphanumerique": "<0,01", "resultat_numerique": 0.0,
                     "libelle_unite": "µg/L"})
    for r in rows:
        r.update({"code_prelevement": PREL, "date_prelevement": "2025-03-14",
                  "code_commune": "17415", "nom_commune": "Saintes",
                  "code_departement": "17",
                  "code_installation_amont": "017000849",
                  "nom_installation_amont": "DICONCHE FILE 2 SAINTES",
                  "conclusion_conformite_prelevement":
                      "Eau d'alimentation conforme aux exigences de qualite en vigueur"})
    return rows


META = {
    "code_prelevement": PREL,
    "code_insee": "17415", "nom": "Saintes", "code_departement": "17",
    "code_installation_amont": "017000849",
    "nom_installation_amont": "DICONCHE FILE 2 SAINTES",
    "nom_distributeur": "Distributeur test", "nom_uge": "A.C. DE SAINTES",
    "codes_reseaux": "017000849", "noms_reseaux": "A.C. DE SAINTES (100 %)",
    "code_lieu_analyse": "L",
    "date_prelevement": "2025-03-14",
    "conclusion_conformite": "Eau d'alimentation conforme aux exigences de qualite en vigueur",
    "conf_limites_bact": "C", "conf_limites_pc": "C", "conf_references_pc": "C",
    "source_url": "fictif", "codes_postaux": "17100", "lon": -0.6328, "lat": 45.7455,
}


def main():
    tmp = tempfile.mkdtemp(prefix="obs-test-")
    db = os.path.join(tmp, "test.duckdb")
    try:
        build_db.build(db=db, reset=True)
        con = duckdb.connect(db)

        rows = bulletin_fictif()
        code_prel, nb, complet = ingest.ingest_bulletin(con, META, rows)
        print(f"\nbulletin ingéré : {code_prel} — {nb} paramètres, complet={complet}\n")

        print("0. normalisation des libellés")
        verifie(norm("Aluminium total µg/l") == "aluminium total",
                "suffixe d'unité retiré : « Aluminium total µg/l » -> « aluminium total »")
        verifie(norm("Uranium en µg/l") == "uranium",
                "suffixe « en µg/l » retiré")
        verifie(norm("Escherichia coli /100mL") == "escherichia coli",
                "suffixe « /100mL » retiré")
        verifie(norm("Nitrates (en NO3)") == "nitrates (en no3)",
                "« (en NO3) » n'est pas une unité : libellé intact")

        print("\n1. bulletin complet")
        verifie(complet is True, f"est_complet vrai ({nb} > {SEUIL_COMPLET})")
        verifie(code_prel == PREL, "le code_prelevement de la source fait foi")

        print("\n2. idempotence")
        ingest.ingest_bulletin(con, META, rows)
        n_pre = con.execute("SELECT COUNT(*) FROM prelevements").fetchone()[0]
        n_mes = con.execute("SELECT COUNT(*) FROM mesures").fetchone()[0]
        verifie(n_pre == 1, f"réingestion : 1 prélèvement et non {n_pre}")
        verifie(n_mes == nb, f"réingestion : {nb} mesures et non {n_mes}")

        print("\n3. un lot ne peut porter qu'un seul prélèvement")
        melange = [dict(rows[0]), dict(rows[1])]
        melange[1]["code_prelevement"] = "TEST-0002"
        try:
            ingest.ingest_bulletin(con, META, melange)
            verifie(False, "un lot hétérogène doit être refusé")
        except ingest.BulletinHeterogene:
            verifie(True, "un lot portant deux prélèvements est refusé")

        print("\n4. la bascule 2016 -> 2026")
        bascules = dict(con.execute("""
            SELECT libelle_parametre, resultat_num FROM v_mesures_verdict
            WHERE bascule_2016_2026
        """).fetchall())
        verifie("ESA metolachlore" in bascules,
                "ESA métolachlore 0,42 µg/L : bascule (0,1 -> 0,9)")
        verifie("Antimoine" in bascules, "Antimoine 7 µg/L : bascule (5 -> 10)")
        verifie("Nitrites (en NO2)" not in bascules,
                "Nitrites 0,8 mg/L : dépassement dans les deux grilles, pas une bascule")
        verifie("Quinmerac" not in bascules,
                "Quinmérac 0,25 µg/L : dépassement dans les deux grilles, pas une bascule")
        verifie("Manganese total" not in bascules,
                "une limite seulement déclarée ne peut PAS produire de bascule")

        print("\n5. seuil différé (plomb, 5 µg/L au 01/01/2036)")
        pb = con.execute("""
            SELECT depasse_2026, depasse_futur, seuil_2026, seuil_futur,
                   date_applicabilite_futur
            FROM v_mesures_verdict WHERE libelle_parametre = 'Plomb'
        """).fetchone()
        verifie(pb is not None, "plomb apparié au référentiel")
        if pb:
            verifie(pb[0] is False, f"plomb 7 µg/L : PAS un dépassement 2026 (limite {pb[2]})")
            verifie(pb[1] is True, f"plomb 7 µg/L : dépassera le seuil {pb[3]} au {pb[4]}")

        print("\n6. zéro n'est pas zéro / indéterminé")
        pfas = con.execute("""
            SELECT est_quantifie, lq, seuil_strict, indetermine_strict, depasse_strict
            FROM v_mesures_verdict WHERE code_parametre = '9268'
        """).fetchone()
        verifie(pfas is not None, "somme 4 PFAS appariée par code_parametre")
        if pfas:
            verifie(pfas[0] is False, "« <0,004 » lu comme non quantifié")
            verifie(pfas[1] == 0.004, f"LQ conservée ({pfas[1]})")
            verifie(pfas[3] is True,
                    f"LQ {pfas[1]} > seuil strict {pfas[2]} : INDÉTERMINÉ")
            verifie(pfas[4] is False, "un indéterminé n'est pas un dépassement")
        hg = con.execute("""
            SELECT est_quantifie, resultat_num, depasse_2026 FROM v_mesures_verdict
            WHERE libelle_parametre = 'Mercure'
        """).fetchone()
        if hg:
            verifie(hg[0] is False, "« 0 » sec lu comme non quantifié")
            verifie(hg[1] is None, "« 0 » sec ne produit pas de valeur 0.0")
            verifie(hg[2] is False, "« 0 » sec ne produit aucun verdict de dépassement")

        # UN SEUIL DE ZÉRO NE SE PERCE PAS PAR LE BAS (§8bis obligation 11).
        # La bactériologie exige l'absence et la LQ d'un dénombrement vaut 1 :
        # on ne compte pas une demi-bactérie. Sans cette garde, toute mesure
        # bactériologique non quantifiée passerait « indéterminée » — 69 dans le
        # corpus au 8 août 2026, qui n'y échappaient que parce qu'aucun alias ne
        # les rattachait au référentiel. Une règle qui ne tient que par une
        # lacune du catalogue n'est pas une règle.
        ent = con.execute("""
            SELECT est_quantifie, lq, seuil_strict, seuil_applicable,
                   indetermine_strict, depasse_strict, depasse_applicable
            FROM v_mesures_verdict WHERE libelle_parametre = 'Enterocoques'
        """).fetchone()
        verifie(ent is not None, "« Enterocoques » apparié au référentiel par libellé")
        if ent:
            verifie(ent[2] == 0.0 and ent[3] == 0.0,
                    f"son seuil et son repère strict valent zéro — absence exigée "
                    f"({ent[3]}, {ent[2]})")
            verifie(ent[1] == 1.0, f"LQ de dénombrement conservée ({ent[1]})")
            verifie(ent[4] is False,
                    "LQ 1 pour un seuil de 0 : PAS indéterminé — aucune LQ ne "
                    "passe sous zéro")
            verifie(ent[5] is False and ent[6] is False,
                    "et pas davantage un dépassement : rien n'a été quantifié")

        print("\n7. appariement")
        modes = dict(con.execute("""
            SELECT mode_appariement, COUNT(*) FROM v_mesures_ref
            WHERE mode_appariement IS NOT NULL GROUP BY 1
        """).fetchall())
        verifie(modes.get("code_parametre", 0) >= 2,
                f"appariement par code_parametre : {modes.get('code_parametre', 0)}")
        verifie(modes.get("libelle", 0) >= 1,
                f"appariement par libellé : {modes.get('libelle', 0)}")
        verifie(modes.get("alias", 0) >= 1,
                f"appariement par alias : {modes.get('alias', 0)}")
        verifie(modes.get("regle_famille", 0) >= 2,
                f"appariement par règle de famille : {modes.get('regle_famille', 0)}")
        alu = con.execute("""
            SELECT mode_appariement, seuil_2026, depasse_2026 FROM v_mesures_verdict
            WHERE libelle_parametre = 'Aluminium total µg/l'
        """).fetchone()
        verifie(alu is not None and alu[0] == 'libelle',
                "« Aluminium total µg/l » rejoint « Aluminium total » par libellé normalisé")
        nitr = con.execute("""
            SELECT resultat_num, seuil_2026, seuil_strict, depasse_2026, depasse_strict
            FROM v_mesures_verdict WHERE libelle_parametre = 'Nitrates'
        """).fetchone()
        verifie(nitr is not None, "« Nitrates » apparié via l'alias vers « Nitrates (en NO3) »")
        if nitr:
            verifie(nitr[3] is False, f"38 mg/L conforme à la limite {nitr[1]}")
            verifie(nitr[4] is True, f"38 mg/L au-dessus du repère nourrisson {nitr[2]}")

        print("\n8. règle de famille : les pesticides nommés")
        bos = con.execute("""
            SELECT mode_appariement, famille, seuil_2016, seuil_2026,
                   depasse_2026, regle_appliquee
            FROM v_mesures_verdict WHERE libelle_parametre = 'Boscalid'
        """).fetchone()
        verifie(bos is not None, "Boscalid, absent du référentiel, est tout de même noté")
        if bos:
            verifie(bos[0] == 'regle_famille', f"rattaché par règle ({bos[5]})")
            verifie(bos[2] == 0.1 and bos[3] == 0.1,
                    "hérite des DEUX grilles : 0,1 en 2016 comme en 2026")
            verifie(bos[4] is False, "0,05 µg/L conforme")
        quin = con.execute("""
            SELECT depasse_2016, depasse_2026, bascule_2016_2026
            FROM v_mesures_verdict WHERE libelle_parametre = 'Quinmerac'
        """).fetchone()
        if quin:
            verifie(quin[0] is True and quin[1] is True,
                    "Quinmérac 0,25 µg/L : dépassement dans les deux grilles")
            verifie(quin[2] is False, "et donc pas une bascule")

        print("\n9. limite déclarée seule : la grille d'aujourd'hui, et rien d'autre")
        mn = con.execute("""
            SELECT origine_seuil_2026, seuil_2026_effectif, depasse_2026,
                   seuil_2016, depasse_2016, seuil_strict, notee
            FROM v_mesures_verdict WHERE libelle_parametre = 'Manganese total'
        """).fetchone()
        verifie(mn is not None, "Manganèse noté grâce à la limite déclarée")
        if mn:
            verifie(mn[0] == 'declare', "origine du seuil : 'declare'")
            verifie(mn[2] is True, f"60 µg/L dépasse la limite déclarée {mn[1]}")
            verifie(mn[3] is None and mn[4] is False,
                    "aucun passé réglementaire inventé : seuil_2016 reste vide")
            verifie(mn[5] is None, "aucun seuil strict inventé")
            verifie(mn[6] is True, "la mesure compte comme notée")

        print("\n10. contrôle croisé référentiel / source")
        ec = con.execute("""
            SELECT libelle_parametre, seuil_2026_referentiel, limite_declaree_source
            FROM v_ecarts_referentiel_source
        """).fetchall()
        verifie(any(r[0] == 'Antimoine' for r in ec),
                "écart signalé : référentiel 10 µg/L contre 5 µg/L déclarés")
        anti = con.execute("""
            SELECT origine_seuil_2026, seuil_2026_effectif
            FROM v_mesures_verdict WHERE libelle_parametre = 'Antimoine'
        """).fetchone()
        verifie(anti[0] == 'referentiel' and anti[1] == 10.0,
                "en cas d'écart, le référentiel daté du projet prime")

        print("\n11. diagnostic des mesures sans aucun seuil")
        na = [r[0] for r in con.execute(
            "SELECT libelle_parametre FROM v_parametres_non_apparies").fetchall()]
        verifie("Calcium" in na, "Calcium (ni référentiel ni limite déclarée) est signalé")
        verifie("ESA metolachlore" not in na, "un paramètre apparié n'y figure pas")
        verifie("Boscalid" not in na, "un paramètre rattaché par règle n'y figure pas")

        print("\n12. agrégat par prélèvement")
        agg = con.execute("""
            SELECT nb_mesures_lues, nb_mesures_notees, pct_couverture,
                   nb_notees_referentiel, nb_notees_declare,
                   nb_depasse_2016, nb_depasse_2026, nb_bascules, nb_indetermines,
                   nb_ecarts_seuil, conclusion_conformite, nom_installation_amont
            FROM v_prelevement_verdict
        """).fetchone()
        verifie(agg[0] == nb, f"{nb} mesures lues")
        verifie(agg[1] < agg[0], f"{agg[1]} mesures notées sur {agg[0]} lues — "
                                 "le dénominateur est conservé")
        verifie(agg[4] >= 1, f"au moins une mesure notée par limite déclarée ({agg[4]})")
        verifie(agg[7] == 2, f"2 bascules comptées ({agg[7]})")
        verifie(agg[5] > agg[7], f"plus de dépassements 2016 ({agg[5]}) que de bascules")
        verifie(agg[8] >= 1, f"au moins un indéterminé compté ({agg[8]})")
        verifie(agg[9] >= 1, f"au moins un écart de seuil signalé ({agg[9]})")
        verifie("conforme" in (agg[10] or "").lower(),
                "le bulletin est déclaré conforme par l'administration")
        verifie(agg[11] == "DICONCHE FILE 2 SAINTES",
                "le point d'eau est porté par le prélèvement")

        print("\n13. la requête de la thèse")
        these = con.execute("""
            SELECT commune, date_prelevement, nb_bascules
            FROM v_prelevement_verdict
            WHERE est_complet AND nb_depasse_2026 = 0 AND nb_bascules > 0
        """).fetchall()
        # Le bulletin fictif comporte volontairement des dépassements 2026
        # (nitrites, quinmérac, manganèse) : il ne doit donc PAS ressortir.
        verifie(these == [],
                "bulletin avec dépassement 2026 exclu de la requête de la thèse")
        these2 = con.execute("""
            SELECT commune, nb_bascules FROM v_prelevement_verdict
            WHERE est_complet AND nb_bascules > 0
        """).fetchall()
        verifie(len(these2) == 1,
                "le bulletin ressort bien quand on ne filtre que sur les bascules")

        print("\n14. le verdict se rend à la DATE du prélèvement")
        # Un reclassement n'est pas rétroactif. Note d'information de la
        # délégation départementale de Charente-Maritime, 10/06/2024 :
        # « il n'y a pas de rétroactivité possible ; l'expression des
        # non-conformités mises en évidence avant le 29/04/2024 est maintenue ».
        for date, code in (("2023-06-01", "AVANT-0001"), ("2025-06-01", "APRES-0001")):
            r471 = {"code_parametre": None, "libelle_parametre": "Chlorothalonil R471811",
                    "resultat_alphanumerique": "0,5", "resultat_numerique": 0.5,
                    "libelle_unite": "µg/L", "code_prelevement": code,
                    "date_prelevement": date}
            ingest.ingest_bulletin(
                con, dict(META, code_prelevement=code, date_prelevement=date), [r471])
        avant = con.execute("""
            SELECT seuil_applicable, grille_applicable, depasse_applicable,
                   depasse_2026, bascule_2016_2026, bascule_datee
            FROM v_mesures_verdict WHERE code_prelevement = 'AVANT-0001'
        """).fetchone()
        apres = con.execute("""
            SELECT seuil_applicable, grille_applicable, depasse_applicable,
                   depasse_2026, bascule_2016_2026, bascule_datee
            FROM v_mesures_verdict WHERE code_prelevement = 'APRES-0001'
        """).fetchone()
        verifie(avant[0] == 0.1 and avant[1] == '2016',
                f"prélevé en 2023 : la grille de 2016 s'applique (seuil {avant[0]})")
        verifie(avant[2] is True,
                "R471811 à 0,5 µg/L en 2023 : NON-CONFORMITÉ, et elle le reste")
        verifie(apres[0] == 0.9 and apres[1] == '2026',
                f"prélevé en 2025 : la grille de 2026 s'applique (seuil {apres[0]})")
        verifie(apres[2] is False,
                "la MÊME valeur en 2025 : conforme — la limite a bougé, pas l'eau")
        verifie(avant[4] is True and apres[4] is True,
                "les deux sont des bascules au sens contrefactuel")
        verifie(avant[5] is False and apres[5] is True,
                "seule celle d'après le 29/04/2024 est une bascule DATÉE")

        print("\n15. cas réel Challet — le moteur contre l'ARS")
        # Bulletin 02800129116 du 10/03/2026. L'ARS conclut au dépassement
        # pour Atrazine déséthyl, Chloridazone desphényl, R417888, et à celui
        # de la valeur indicative 0,9 pour R471811. Valeurs authentiques.
        challet = [
            ("Chlorothalonil R417888", 0.136, "<=0,1 µg/L", True),
            ("Chlorothalonil R471811", 1.662, None, True),
            ("Atrazine desethyl", 0.11, "<=0,1 µg/L", True),
            ("Chloridazone desphenyl", 0.107, "<=0,1 µg/L", True),
            ("Chlorothalonil", None, "<=0,1 µg/L", False),
        ]
        lignes = [{"code_parametre": None, "libelle_parametre": lib,
                   "resultat_alphanumerique": (str(val).replace(".", ",") if val else "<0,005"),
                   "resultat_numerique": val or 0.0, "libelle_unite": "µg/L",
                   "limite_qualite_parametre": lim,
                   "code_prelevement": "CHALLET-2026", "date_prelevement": "2026-03-10"}
                  for lib, val, lim, _ in challet]
        ingest.ingest_bulletin(con, dict(META, code_prelevement="CHALLET-2026",
                                         date_prelevement="2026-03-10"), lignes)
        trouves = {r[0] for r in con.execute("""
            SELECT libelle_parametre FROM v_mesures_verdict
            WHERE code_prelevement = 'CHALLET-2026' AND depasse_applicable
        """).fetchall()}
        attendus = {lib for lib, _v, _l, dep in challet if dep}
        verifie(trouves == attendus,
                f"les 4 dépassements de l'ARS, ni plus ni moins ({len(trouves)} trouvé(s))")
        r417 = con.execute("""
            SELECT seuil_applicable, depasse_applicable FROM v_mesures_verdict
            WHERE code_prelevement = 'CHALLET-2026'
              AND libelle_parametre = 'Chlorothalonil R417888'
        """).fetchone()
        verifie(r417[0] == 0.1 and r417[1] is True,
                "R417888 à 0,136 µg/L dépasse 0,1 — pertinent, génotoxicité non exclue")
        r471 = con.execute("""
            SELECT seuil_applicable, limite_declaree, depasse_applicable
            FROM v_mesures_verdict WHERE code_prelevement = 'CHALLET-2026'
              AND libelle_parametre = 'Chlorothalonil R471811'
        """).fetchone()
        verifie(r471[1] is None,
                "la source ne déclare AUCUNE limite pour R471811 (valeur de vigilance)")
        verifie(r471[0] == 0.9 and r471[2] is True,
                "seul le référentiel daté du projet voit ce dépassement (1,662 > 0,9)")

        print("\n16. l'effort de recherche")
        eff = con.execute("""
            SELECT classe_effort, nb_parametres, nb_synthese_recherchees,
                   nb_mesures_notees, depassements_pour_mille
            FROM v_prelevement_verdict WHERE code_prelevement = ?
        """, [PREL]).fetchone()
        verifie(eff[0] == 'standard',
                f"{eff[1]} paramètres cherchés -> classe '{eff[0]}'")
        verifie(eff[2] >= 3,
                f"{eff[2]} substances de synthèse recherchées, quantifiées ou non")
        verifie(eff[4] is not None and eff[4] > 0,
                f"taux comparable calculé : {eff[4]} dépassements pour mille notés")
        from common import classe_effort as ce
        verifie((ce(150), ce(234), ce(359), ce(660))
                == ('restreinte', 'standard', 'approfondie', 'exhaustive'),
                "les quatre classes de profondeur d'analyse")
        verifie(con.execute(
            "SELECT COUNT(*) FROM v_effort_recherche").fetchone()[0] >= 1,
            "v_effort_recherche expose le bulletin, trié par effort décroissant")

        print("\n17. le panel — ce qu'on a cessé de chercher")
        # Trois bulletins complets sur une même commune fictive. Ils vérifient
        # les deux choses que les vues de panel doivent savoir faire : compter
        # ce qui disparaît, et dire si deux bulletins portent sur le MÊME point
        # d'eau — car un panel qui change entre deux captages différents n'est
        # pas une évolution (§2.3), et le code d'installation est vide sur un
        # tiers des bulletins réels.
        def panel_fictif(code, date, libelles, installation, reseaux):
            lignes = [{"code_parametre": None, "libelle_parametre": lib,
                       "resultat_alphanumerique": "<0,01", "resultat_numerique": 0.0,
                       "libelle_unite": "µg/L",
                       "code_prelevement": code, "date_prelevement": date}
                      for lib in libelles]
            meta = dict(META, code_prelevement=code, date_prelevement=date,
                        code_insee="28999", nom="Panelville", code_departement="28",
                        code_installation_amont=None,
                        nom_installation_amont=installation,
                        noms_reseaux=reseaux)
            return ingest.ingest_bulletin(con, meta, lignes)

        socle = [f"Substance A{i:03d}" for i in range(220)]
        garde = socle[:200]
        neuf = [f"Substance N{i:03d}" for i in range(10)]
        panel_fictif("PANEL-2024", "2024-05-02", socle,
                     "SOURCE DU HAUT", "PANELVILLE (100 %)")
        panel_fictif("PANEL-2026", "2026-05-02", garde + neuf,
                     "SOURCE DU BAS", "PANELVILLE (100 %)")
        # Bulletin récent SANS nom d'installation : le seul repère est le nom de
        # réseau, et il a perdu sa part de mélange en cours de route.
        panel_fictif("PANEL-2027", "2027-05-02", garde + neuf, None, "PANELVILLE")

        paires = con.execute("""
            SELECT prelevement_courant, panel_precedent, panel_courant,
                   nb_abandonnes, nb_nouveaux, meme_point_deau, identite_certaine
            FROM v_panel_evolution WHERE code_insee = '28999'
            ORDER BY date_courante
        """).fetchall()
        verifie(len(paires) == 2, f"{len(paires)} paire(s) de bulletins consécutifs")
        p1, p2 = paires
        verifie((p1[1], p1[2]) == (220, 210),
                f"panels lus : {p1[1]} puis {p1[2]} paramètres")
        verifie((p1[3], p1[4]) == (20, 10),
                f"20 abandonnés et 10 nouveaux ({p1[3]} et {p1[4]} trouvés)")
        verifie(p1[6] is True and p1[5] is False,
                "deux installations nommées et différentes : point d'eau différent, sans doute possible")
        verifie(p2[6] is False and p2[5] is True,
                "installation non renseignée : « PANELVILLE (100 %) » et « PANELVILLE » "
                "sont le même réseau — présumé, et dit comme tel")
        abandonnes = {r[0] for r in con.execute("""
            SELECT libelle_parametre FROM v_parametres_abandonnes
            WHERE cle_param LIKE 'substance a2%'
        """).fetchall()}
        verifie(len(abandonnes) == 20,
                f"les 20 substances retirées sont nommées ({len(abandonnes)} listées)")
        presence = con.execute("""
            SELECT nb_recherche, nb_bulletins FROM v_parametre_presence
            WHERE libelle_parametre = 'Substance A219' AND annee = 2024
        """).fetchone()
        verifie(presence == (1, 1),
                "v_parametre_presence affiche son dénominateur : "
                f"{presence[0]} bulletin(s) sur {presence[1]} cette année-là")

        # LE ZÉRO S'ÉCRIT. Ce contrôle disait exactement l'inverse jusqu'au
        # 8 août 2026 — « un paramètre qu'on ne cherche plus n'a plus de ligne
        # l'année suivante » — et il verrouillait un angle mort : le détecteur
        # à l'échelle était aveugle au seul cas qui l'intéresse vraiment,
        # l'abandon complet. Une absence de ligne ne se distingue pas d'une
        # année non documentée ; un 0 % avec son dénominateur, si (§2.4, §2.11).
        zero = con.execute("""
            SELECT nb_recherche, pct_bulletins, nb_bulletins
            FROM v_parametre_presence
            WHERE libelle_parametre = 'Substance A219' AND annee = 2026
        """).fetchone()
        verifie(zero is not None and zero[0] == 0 and zero[1] == 0.0,
                "un paramètre qu'on ne cherche plus garde une ligne, à 0 % — "
                + (f"{zero[0]} bulletin(s) sur {zero[2]}" if zero
                   else "AUCUNE LIGNE : l'abandon complet est invisible"))
        verifie(con.execute("""
            SELECT COUNT(*) FROM v_parametre_presence
            WHERE libelle_parametre = 'Substance N000' AND pct_bulletins = 0
        """).fetchone()[0] >= 1,
                "la grille est pleine des deux côtés : un paramètre apparu en "
                "2026 porte aussi ses années à 0 %, avant qu'on le cherche")

        # La strate départementale — le contre-feu. Elle dit si une chute est un
        # retrait de programme ou un corpus qui a changé de composition.
        strate = con.execute("""
            SELECT dept, nb_recherche, pct_bulletins
            FROM v_parametre_presence_dept
            WHERE libelle_parametre = 'Substance A219'
            ORDER BY dept, annee
        """).fetchall()
        verifie(strate and {r[0] for r in strate} == {"28"},
                "v_parametre_presence_dept borne l'univers au département : "
                "une substance cherchée dans le seul 28 ne produit pas de 0 % "
                f"trompeur dans le 17 ({sorted({r[0] for r in strate})} vus)")
        verifie(any(r[2] == 0.0 for r in strate),
                "et dans le département qui l'a cherchée, l'année de l'abandon "
                "est bien à 0 %")

        print("\n18. le mélange — ce qu'un réseau moyenne avant le robinet")
        # Chantier C7. Six bulletins fictifs, chacun sur un piège réel du
        # corpus : la part qui se lit, la somme qui se referme, la part qui
        # manque, la part ABSENTE qui n'est pas 100 %, le code de réseau
        # répété sous deux libellés (Berchères), et la station recodée qui
        # ferait croire à deux sources (Laparrouquial).
        def melange_fictif(code, insee, commune, inst_code, inst_nom,
                           codes_reseaux, noms_reseaux, nb_params=4):
            lignes = [{"code_parametre": None,
                       "libelle_parametre": f"{code} substance {i:03d}",
                       "resultat_alphanumerique": "<0,01", "resultat_numerique": 0.0,
                       "libelle_unite": "µg/L",
                       "code_prelevement": code, "date_prelevement": "2026-01-15"}
                      for i in range(nb_params)]
            meta = dict(META, code_prelevement=code, date_prelevement="2026-01-15",
                        code_insee=insee, nom=commune, code_departement=insee[:2],
                        code_installation_amont=inst_code,
                        nom_installation_amont=inst_nom,
                        codes_reseaux=codes_reseaux, noms_reseaux=noms_reseaux)
            return ingest.ingest_bulletin(con, meta, lignes)

        complet = SEUIL_COMPLET + 1
        # Un réseau alimenté par deux installations : 60 + 40 = 100.
        melange_fictif("MEL-A", "46999", "Mélangeville", "046999801", "SOURCE HAUTE",
                       "046999001", "MELANGEVILLE (60 %)", complet)
        melange_fictif("MEL-B", "46998", "Mélangeville-Bas", "046999802", "SOURCE BASSE",
                       "046999001", "MELANGEVILLE (40 %)", complet)
        # Une seule part connue, sur 30 % : 70 % viennent d'on ne sait où.
        melange_fictif("MEL-C", "46997", "Partielleville", "046999803", "USINE TIERS",
                       "046999002", "PARTIELLE (30 %)")
        # Même code de réseau, deux libellés : un doublon, pas un mélange.
        melange_fictif("MEL-D", "46996", "Doublonville", None, None,
                       "046999003|046999003", "DOUBLON|SECTEUR DOUBLON")
        # La station recodée : deux clés d'installation, mais l'une déclare
        # 100 % — le réseau n'est donc pas mélangé.
        melange_fictif("MEL-E", "46995", "Recodéville", "046999804", "STATION X",
                       "046999004", "RECODEE (100 %)")
        melange_fictif("MEL-F", "46994", "Recodéville-Bis", "046999805", "STATION X BIS",
                       "046999004", "RECODEE")

        ligne_a = con.execute("""
            SELECT nom_reseau, part_reseau_pct, nb_libelles FROM v_reseau_bulletin
            WHERE code_prelevement = 'MEL-A'
        """).fetchone()
        verifie(ligne_a == ("MELANGEVILLE", 60.0, 1),
                "la part se détache du nom : « MELANGEVILLE (60 %) » -> "
                f"réseau « {ligne_a[0]} », part {ligne_a[1]}")

        reconstitue = con.execute("""
            SELECT statut_melange, somme_parts_connues, part_non_attribuee,
                   nb_sources_identifiees, nb_sources_analysees, melange_lisible
            FROM v_melange_reseau WHERE code_reseau = '046999001'
        """).fetchone()
        verifie(reconstitue[:4] == ('melange_reconstitue', 100.0, 0.0, 2),
                "deux sources sous 100 % dont la somme se referme : mélange "
                f"reconstitué, rien de non attribué ({reconstitue[0]})")
        verifie(reconstitue[4] == 2 and reconstitue[5] is True,
                "et ses deux sources portent un bulletin complet : c'est là que "
                "l'hypothèse de dilution devient instruisible")

        partiel = con.execute("""
            SELECT statut_melange, somme_parts_connues, part_non_attribuee
            FROM v_melange_reseau WHERE code_reseau = '046999002'
        """).fetchone()
        verifie(partiel == ('melange_partiel', 30.0, 70.0),
                f"une part de 30 % laisse {partiel[2]} % d'origine inconnue — "
                "le chiffre du chantier")

        # LE PIÈGE CENTRAL : une part absente n'est pas une part de 100 %.
        # C'est le §2.4 transposé au mélange — l'absence d'information n'est
        # pas une information d'absence.
        muet = con.execute("""
            SELECT statut_melange, part_non_attribuee, melange_lisible,
                   nb_parts_declarees
            FROM v_melange_reseau WHERE code_reseau = '046999003'
        """).fetchone()
        verifie(muet == ('non_declare', None, False, 0),
                "aucune part déclarée : statut « non_declare » et part non "
                "attribuée à NULL — jamais 100, jamais 0")

        doublon = con.execute("""
            SELECT nb_reseaux_desservis, nb_libelles FROM v_melange_bulletin b
            JOIN v_reseau_bulletin r USING (code_prelevement)
            WHERE b.code_prelevement = 'MEL-D'
        """).fetchone()
        verifie(doublon == (1, 2),
                "un code de réseau répété sous deux libellés reste UN réseau "
                f"({doublon[0]} réseau, {doublon[1]} libellés)")

        recode = con.execute("""
            SELECT statut_melange, nb_sources_identifiees, melange_lisible
            FROM v_melange_reseau WHERE code_reseau = '046999004'
        """).fetchone()
        verifie(recode == ('source_unique_declaree', 2, False),
                "deux clés d'installation dont une déclare 100 % : une source "
                f"unique, pas un mélange ({recode[1]} clés vues)")

        verifie(con.execute("SELECT COUNT(*) FROM v_reseaux_illisibles").fetchone()[0] == 0,
                "aucun prélèvement dont les listes de codes et de noms de "
                "réseaux ne s'apparient : la décomposition n'écarte rien en silence")

        con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 62)
    if ECHECS:
        print(f"{len(ECHECS)} ÉCHEC(S) :")
        for e in ECHECS:
            print(f"  - {e}")
        sys.exit(1)
    print("tous les contrôles passent — le moteur applique les règles de méthode")


if __name__ == "__main__":
    main()

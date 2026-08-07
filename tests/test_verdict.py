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
        # Pesticide inconnu du référentiel, limite déclarée 0,1 µg/L :
        # rattaché à « Pesticide - substance individuelle ». Conforme.
        {"code_parametre": "1907", "libelle_parametre": "Boscalid",
         "resultat_alphanumerique": "0,05", "resultat_numerique": 0.05,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=0,1 µg/L"},

        # Même règle, mais au-dessus : dépassement 2016 ET 2026 (la limite
        # pesticide n'a pas bougé) -> surtout PAS une bascule.
        {"code_parametre": "1264", "libelle_parametre": "Quinmerac",
         "resultat_alphanumerique": "0,25", "resultat_numerique": 0.25,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=0,1 µg/L"},

        # --- 6. LIMITE DÉCLARÉE SEULE (hors référentiel) --------------------
        # Absent du référentiel : la limite déclarée donne la grille 2026 et
        # rien d'autre. Dépassement aujourd'hui, aucun verdict 2016.
        {"code_parametre": "1394", "libelle_parametre": "Manganese total",
         "resultat_alphanumerique": "60", "resultat_numerique": 60.0,
         "libelle_unite": "µg/L", "limite_qualite_parametre": "<=50 µg/L"},

        # --- 7. AUCUN SEUIL DU TOUT -----------------------------------------
        # Ni référentiel, ni limite déclarée : mesure invisible, à signaler.
        {"code_parametre": "1374", "libelle_parametre": "Calcium",
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

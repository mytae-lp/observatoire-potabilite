# -*- coding: utf-8 -*-
"""
Test de bout en bout du moteur de réétalonnage, sans réseau.

    python3 tests/test_verdict.py

Il fabrique un bulletin complet fictif, l'ingère, et vérifie que les quatre
règles de méthode du projet sont effectivement appliquées par les vues :

  1. la bascule 2016 -> 2026 est détectée ;
  2. un seuil différé (plomb 2036) ne produit pas de faux dépassement aujourd'hui ;
  3. une valeur non quantifiée dont la LQ dépasse le seuil strict est
     INDÉTERMINÉE, jamais conforme ;
  4. l'appariement par code_parametre, par libellé et par alias fonctionne,
     et ce qui n'est apparié par aucun des trois est visible.

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
from common import SEUIL_COMPLET  # noqa: E402

ECHECS = []


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
         "libelle_unite": "µg/L"},

        # Antimoine : 7 µg/L. Limite relevée de 5 à 10 en 2023 -> bascule.
        {"code_parametre": None, "libelle_parametre": "Antimoine",
         "resultat_alphanumerique": "7", "resultat_numerique": 7.0,
         "libelle_unite": "µg/L"},

        # --- 2. SEUIL DIFFÉRÉ ------------------------------------------------
        # Plomb : 7 µg/L. Limite applicable AUJOURD'HUI 10 µg/L -> conforme.
        # Limite de 2036 : 5 µg/L -> dépassera. Ne doit PAS compter comme
        # dépassement 2026 (c'était le bug corrigé, cf. CLAUDE.md §2.5).
        {"code_parametre": None, "libelle_parametre": "Plomb",
         "resultat_alphanumerique": "7", "resultat_numerique": 7.0,
         "libelle_unite": "µg/L"},

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

        # Non apparié : doit apparaître dans v_parametres_non_apparies.
        {"code_parametre": "99999", "libelle_parametre": "Parametre exotique inconnu",
         "resultat_alphanumerique": "1,5", "resultat_numerique": 1.5,
         "libelle_unite": "µg/L"},

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
        r.update({"code_prelevement": "TEST-0001", "date_prelevement": "2025-03-14",
                  "code_commune": "17415", "nom_commune": "Saintes",
                  "code_departement": "17",
                  "conclusion_conformite_prelevement":
                      "Eau d'alimentation conforme aux exigences de qualite en vigueur"})
    return rows


def main():
    tmp = tempfile.mkdtemp(prefix="obs-test-")
    db = os.path.join(tmp, "test.duckdb")
    try:
        build_db.build(db=db, reset=True)
        con = duckdb.connect(db)

        rows = bulletin_fictif()
        meta = {
            "code_insee": "17415", "nom": "Saintes", "code_departement": "17",
            "nom_installation": "Installation test", "nom_distributeur": "Distributeur test",
            "date_prelevement": "2025-03-14",
            "conclusion_conformite": rows[0]["conclusion_conformite_prelevement"],
            "conf_limites_bact": "C", "conf_limites_pc": "C", "conf_references_pc": "C",
            "source_url": "fictif",
        }
        code_prel, nb, complet = ingest.ingest_bulletin(con, meta, rows)

        print(f"\nbulletin ingéré : {code_prel} — {nb} paramètres, complet={complet}\n")

        print("1. bulletin complet")
        verifie(complet is True, f"est_complet vrai ({nb} > {SEUIL_COMPLET})")

        print("\n2. idempotence")
        ingest.ingest_bulletin(con, meta, rows)
        n_pre = con.execute("SELECT COUNT(*) FROM prelevements").fetchone()[0]
        n_mes = con.execute("SELECT COUNT(*) FROM mesures").fetchone()[0]
        verifie(n_pre == 1, f"réingestion : 1 prélèvement et non {n_pre}")
        verifie(n_mes == nb, f"réingestion : {nb} mesures et non {n_mes}")

        print("\n3. la bascule 2016 -> 2026")
        bascules = dict(con.execute("""
            SELECT libelle_parametre, resultat_num FROM v_mesures_verdict
            WHERE bascule_2016_2026
        """).fetchall())
        verifie("ESA metolachlore" in bascules,
                "ESA métolachlore 0,42 µg/L : bascule (0,1 -> 0,9)")
        verifie("Antimoine" in bascules, "Antimoine 7 µg/L : bascule (5 -> 10)")
        verifie("Nitrites (en NO2)" not in bascules,
                "Nitrites 0,8 mg/L : dépassement dans les deux grilles, pas une bascule")

        print("\n4. seuil différé (plomb, 5 µg/L au 01/01/2036)")
        pb = con.execute("""
            SELECT depasse_2026, depasse_futur, seuil_2026, seuil_futur,
                   date_applicabilite_futur
            FROM v_mesures_verdict WHERE libelle_parametre = 'Plomb'
        """).fetchone()
        verifie(pb is not None, "plomb apparié au référentiel")
        if pb:
            verifie(pb[0] is False, f"plomb 7 µg/L : PAS un dépassement 2026 (limite {pb[2]})")
            verifie(pb[1] is True, f"plomb 7 µg/L : dépassera le seuil {pb[3]} au {pb[4]}")

        print("\n5. zéro n'est pas zéro / indéterminé")
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

        print("\n6. appariement")
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
        nitr = con.execute("""
            SELECT resultat_num, seuil_2026, seuil_strict, depasse_2026, depasse_strict
            FROM v_mesures_verdict WHERE libelle_parametre = 'Nitrates'
        """).fetchone()
        verifie(nitr is not None, "« Nitrates » apparié via l'alias vers « Nitrates (en NO3) »")
        if nitr:
            verifie(nitr[3] is False, f"38 mg/L conforme à la limite {nitr[1]}")
            verifie(nitr[4] is True, f"38 mg/L au-dessus du repère nourrisson {nitr[2]}")

        print("\n7. diagnostic des non appariés")
        na = [r[0] for r in con.execute(
            "SELECT libelle_parametre FROM v_parametres_non_apparies").fetchall()]
        verifie("Parametre exotique inconnu" in na,
                "le paramètre inconnu est signalé comme non apparié")
        verifie(all("ESA metolachlore" != x for x in na),
                "un paramètre apparié n'apparaît pas dans les non appariés")

        print("\n8. agrégat par prélèvement")
        agg = con.execute("""
            SELECT nb_parametres, est_complet, nb_depasse_2016, nb_depasse_2026,
                   nb_bascules, nb_indetermines, conclusion_conformite
            FROM v_prelevement_verdict
        """).fetchone()
        verifie(agg[4] == 2, f"2 bascules comptées ({agg[4]})")
        verifie(agg[2] > agg[3],
                f"plus de dépassements en 2016 ({agg[2]}) qu'en 2026 ({agg[3]})")
        verifie(agg[5] >= 1, f"au moins un indéterminé compté ({agg[5]})")
        verifie("conforme" in (agg[6] or "").lower(),
                "le bulletin est déclaré conforme par l'administration")

        print("\n9. la requête de la thèse")
        these = con.execute("""
            SELECT commune, date_prelevement, nb_bascules
            FROM v_prelevement_verdict
            WHERE est_complet AND nb_depasse_2026 = 0 AND nb_bascules > 0
        """).fetchall()
        # Le bulletin fictif comporte volontairement un dépassement 2026
        # (nitrites) : il ne doit donc PAS ressortir. La requête est stricte.
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

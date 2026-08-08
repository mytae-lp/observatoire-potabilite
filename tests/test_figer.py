# -*- coding: utf-8 -*-
"""
Test de la sortie figée, sans réseau.

    python3 tests/test_figer.py

Vérifie que :
  1. chaque ligne figée porte l'empreinte du référentiel et la date de calcul ;
  2. l'empreinte change quand le référentiel change — sinon un verdict figé
     contre une grille modifiée deviendrait faux en silence, ce qui
     contredirait la thèse du projet avec ses propres outils ;
  3. deux versions coexistent : la comparaison est la trace du déplacement ;
  4. seules les mesures NOTÉES sont figées, et le dénominateur est conservé ;
  5. les sommes excluent les lignes agrégées (pas de double compte) et
     l'indice de danger ne porte que sur les substances de synthèse ;
  6. les trois statuts de couverture sont inscrits, y compris
     « non_documentee » — une absence de donnée doit rester visible.
"""
import os
import shutil
import sys
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, os.path.join(RACINE, "tests"))

import duckdb  # noqa: E402
import build_db  # noqa: E402
import figer  # noqa: E402
import ingest  # noqa: E402
from test_verdict import bulletin_fictif, META  # noqa: E402

ECHECS = []


def verifie(condition, message):
    print(("  ok   " if condition else "  ECHEC ") + message)
    if not condition:
        ECHECS.append(message)


def main():
    tmp = tempfile.mkdtemp(prefix="obs-fige-")
    db = os.path.join(tmp, "test.duckdb")
    try:
        build_db.build(db=db, reset=True)
        con = duckdb.connect(db)
        rows = bulletin_fictif()
        code_prel, nb, _ = ingest.ingest_bulletin(con, META, rows)

        print("\n1. empreinte du référentiel")
        v1 = figer.version_referentiel()
        verifie(len(v1) == 12 and all(c in "0123456789abcdef" for c in v1),
                f"empreinte de 12 caractères hexadécimaux ({v1})")
        verifie(figer.version_referentiel() == v1, "empreinte stable à contenu constant")
        # Simule un référentiel modifié : les règles de famille disparaissent.
        garde = figer.REGLES_CSV
        figer.REGLES_CSV = os.path.join(tmp, "absent.csv")
        v_modifie = figer.version_referentiel()
        figer.REGLES_CSV = garde
        verifie(v_modifie != v1,
                "l'empreinte change quand le référentiel change")

        print("\n2. estampillage")
        version, n = figer.figer(con)
        verifie(n == 1, f"1 bulletin figé ({n})")
        ligne = con.execute("""
            SELECT version_referentiel, calcule_le, commune, nb_mesures_lues,
                   nb_mesures_notees, pct_couverture, nb_bascules
            FROM analyses_figees
        """).fetchone()
        verifie(ligne[0] == v1, "la version du référentiel est inscrite")
        verifie(ligne[1] is not None, f"la date de calcul est inscrite ({ligne[1]})")
        verifie(ligne[3] == nb, f"{nb} mesures lues conservées comme dénominateur")
        verifie(ligne[4] < ligne[3], f"{ligne[4]} notées sur {ligne[3]} lues")
        verifie(ligne[6] == 2, f"2 bascules figées ({ligne[6]})")

        print("\n2bis. une commune qui a un bulletin figé est visible, même non demandée")
        # Défaut réel : `observer.py` n'inscrivait la couverture que des communes
        # DEMANDÉES. Une commune dont le bulletin sert de repli à sa voisine
        # restait absente de la carte alors que son analyse était en base — le
        # symétrique de la règle « non documentée ». Ici personne n'a appelé
        # figer_commune : c'est figer() qui doit l'avoir inscrite.
        implicite = con.execute("""
            SELECT statut, code_prelevement, nb_parametres FROM couverture_communes
            WHERE code_insee = '17415' AND version_referentiel = ?
        """, [v1]).fetchone()
        verifie(implicite is not None,
                "la commune du bulletin figé est inscrite d'office")
        verifie(implicite and implicite[0] == "analysee",
                "et elle l'est comme « analysée »")
        verifie(implicite and implicite[1] == code_prel,
                "avec le prélèvement qui la documente")

        print("\n3. ce qui est figé : les mesures notées, plus celles qui ont un repère strict")
        nfig = con.execute("SELECT COUNT(*) FROM verdicts_figes").fetchone()[0]
        verifie(nfig >= ligne[4],
                f"{nfig} verdicts figés pour {ligne[4]} mesures notées")
        calcium = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes WHERE libelle_parametre = 'Calcium'
        """).fetchone()[0]
        verifie(calcium == 0, "une mesure sans aucun seuil n'est pas figée")

        # Une mesure qui n'a QU'UN seuil strict doit être figée quand même :
        # c'est là que naît l'indéterminé (LQ du laboratoire au-dessus du
        # repère le plus protecteur), et le compteur du bulletin le compte.
        orphelines = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes
            WHERE seuil_2026_effectif IS NULL AND seuil_strict IS NOT NULL
        """).fetchone()[0]
        agrege_ind = con.execute("""
            SELECT nb_indetermines FROM analyses_figees WHERE version_referentiel = ?
        """, [v1]).fetchone()[0]
        detail_ind = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes
            WHERE version_referentiel = ? AND indetermine_strict
        """, [v1]).fetchone()[0]
        verifie(agrege_ind == detail_ind,
                f"les indéterminés du compteur ({agrege_ind}) sont tous dans le "
                f"détail ({detail_ind})"
                + (f" — dont {orphelines} sans seuil actuel" if orphelines else ""))

        print("\n3bis. le verdict à la date survit au figeage")
        # Défaut réel : `verdicts_figes` ne portait que `depasse_2026`. Une sortie
        # qui ne lit que les tables figées — ce qu'impose CLAUDE.md §8bis — ne
        # pouvait donc pas afficher le verdict rendu à la date du prélèvement, et
        # le détail contredisait le compteur du même écran.
        colonnes = {r[0] for r in con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'verdicts_figes'").fetchall()}
        for col in ("seuil_applicable", "grille_applicable", "depasse_applicable",
                    "bascule_datee", "indetermine_condition"):
            verifie(col in colonnes, f"verdicts_figes porte {col}")

        agrege, detail = con.execute("""
            SELECT (SELECT nb_depasse_applicable FROM analyses_figees
                    WHERE version_referentiel = ?),
                   (SELECT COUNT(*) FROM verdicts_figes
                    WHERE version_referentiel = ? AND depasse_applicable)
        """, [v1, v1]).fetchone()
        verifie(agrege == detail,
                f"le compteur ({agrege}) est d'accord avec son propre détail ({detail})")

        agrege_b, detail_b = con.execute("""
            SELECT (SELECT nb_bascules FROM analyses_figees WHERE version_referentiel = ?),
                   (SELECT COUNT(*) FROM verdicts_figes
                    WHERE version_referentiel = ? AND bascule_2016_2026)
        """, [v1, v1]).fetchone()
        verifie(agrege_b == detail_b,
                f"les bascules figées ({detail_b}) correspondent au compteur ({agrege_b})")

        # Portée volontairement restreinte aux mesures NOTÉES : depuis qu'on
        # fige aussi celles qui n'ont qu'un repère strict, il en existe qui
        # n'ont légitimement aucun seuil applicable aujourd'hui — c'est même
        # tout leur intérêt.
        sans_seuil = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes
            WHERE version_referentiel = ? AND seuil_applicable IS NULL
              AND seuil_2026_effectif IS NOT NULL
        """, [v1]).fetchone()[0]
        verifie(sans_seuil == 0,
                "toute mesure notée porte le seuil qui s'appliquait ce jour-là")

        print("\n3ter. un schéma figé obsolète est reconstruit, jamais gardé en silence")
        # `CREATE TABLE IF NOT EXISTS` ne dit rien quand la table existe avec
        # d'autres colonnes : un dépôt plus ancien garderait la sienne, et
        # l'insertion échouerait — ou pire, réussirait de travers.
        con.execute("DROP TABLE verdicts_figes")
        con.execute("CREATE TABLE verdicts_figes (code_prelevement VARCHAR, "
                    "version_referentiel VARCHAR, libelle_parametre VARCHAR)")
        figer.assurer_schema(con, verbeux=False)
        apres = [r[0] for r in con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'verdicts_figes' ORDER BY ordinal_position").fetchall()]
        verifie(apres == figer.COLONNES_ATTENDUES["verdicts_figes"],
                f"table reconstruite avec ses {len(apres)} colonnes")
        figer.figer(con, version=v1)
        verifie(con.execute(
            "SELECT COUNT(*) FROM verdicts_figes WHERE version_referentiel = ?",
            [v1]).fetchone()[0] == nfig, "et refigée sans perte")

        print("\n4. deux versions coexistent")
        figer.figer(con, version="ancienne-grille", calcule_le="2016-01-01")
        versions = [r[0] for r in con.execute(
            "SELECT DISTINCT version_referentiel FROM analyses_figees ORDER BY 1").fetchall()]
        verifie(len(versions) == 2,
                f"deux versions figées coexistent ({', '.join(versions)})")
        verifie(con.execute(
            "SELECT COUNT(*) FROM analyses_figees WHERE version_referentiel = 'ancienne-grille'"
        ).fetchone()[0] == 1, "la version antérieure n'a pas été écrasée")

        print("\n5. sommes et indice de danger")
        s = con.execute("""
            SELECT nb_synthese_quantifiees, charge_synthese_ug_l,
                   somme_pesticides_recalculee, indice_danger, indice_danger_n
            FROM analyses_figees WHERE version_referentiel = ?
        """, [v1]).fetchone()
        # Le bulletin fictif quantifie : ESA métolachlore 0,42 (metabolite),
        # Boscalid 0,05 et Quinmérac 0,25 (pesticides par règle de famille).
        verifie(s[0] == 3, f"3 substances de synthèse quantifiées ({s[0]})")
        verifie(abs(s[1] - 0.72) < 1e-6,
                f"charge cumulée 0,42 + 0,05 + 0,25 = 0,72 µg/L ({s[1]})")
        verifie(abs(s[2] - 0.72) < 1e-6,
                f"somme pesticides + métabolites recalculée ({s[2]})")
        # HI = 0,42/0,9 + 0,05/0,1 + 0,25/0,1 = 0,4667 + 0,5 + 2,5
        verifie(abs(s[3] - 3.4667) < 1e-3,
                f"indice de danger sur les seules substances de synthèse ({s[3]:.4f})")
        verifie(s[4] == 3, f"indice calculé sur 3 substances ({s[4]})")
        nitrates_dedans = con.execute("""
            SELECT COUNT(*) FROM v_mesures_verdict
            WHERE libelle_parametre = 'Nitrates' AND famille IN
                  ('pesticide','metabolite','PFAS','organique')
        """).fetchone()[0]
        verifie(nitrates_dedans == 0,
                "les minéraux (nitrates) n'entrent pas dans l'indice de danger")

        print("\n6. statuts de couverture")
        for insee, statut, prel, ailleurs in [
            ({"code_insee": "17415", "nom": "Saintes", "lon": -0.63, "lat": 45.74,
              "codes_postaux": "17100"}, "analysee", code_prel, None),
            ({"code_insee": "31088", "nom": "Brax", "lon": 1.27, "lat": 43.60,
              "codes_postaux": "31490"}, "rattachee_reseau", code_prel,
             "Bellegarde-Sainte-Marie"),
            ({"code_insee": "31035", "nom": "Aucamville", "lon": 1.43, "lat": 43.66,
              "codes_postaux": "31140"}, "non_documentee", None, None),
        ]:
            figer.figer_commune(con, insee, statut, v1,
                                code_prelevement=prel, commune_prelevement=ailleurs)
        # Filtré sur la version : la couverture est estampillée comme le reste,
        # et le test fige ici deux versions du même bulletin.
        cov = dict(con.execute(
            "SELECT statut, COUNT(*) FROM couverture_communes "
            "WHERE version_referentiel = ? GROUP BY 1", [v1]).fetchall())
        verifie(cov.get("analysee") == 1, "commune analysée inscrite")
        verifie(cov.get("rattachee_reseau") == 1, "commune rattachée à son réseau inscrite")
        verifie(cov.get("non_documentee") == 1,
                "commune NON DOCUMENTÉE inscrite — l'absence de donnée reste visible")
        brax = con.execute("""
            SELECT commune, commune_prelevement, lon FROM couverture_communes
            WHERE code_insee = '31088'
        """).fetchone()
        verifie(brax[0] == "Brax",
                "la commune rattachée garde SON identité, pas celle du lieu de prélèvement")
        verifie(brax[1] == "Bellegarde-Sainte-Marie",
                "le lieu réel du prélèvement est conservé pour l'affichage")
        verifie(brax[2] is not None,
                "les coordonnées sont présentes même sans prélèvement propre (cartographie)")

        con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 62)
    if ECHECS:
        print(f"{len(ECHECS)} ÉCHEC(S) :")
        for e in ECHECS:
            print(f"  - {e}")
        sys.exit(1)
    print("sortie figée conforme : estampillée, datée, et son dénominateur conservé")


if __name__ == "__main__":
    main()

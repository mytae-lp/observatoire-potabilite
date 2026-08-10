# -*- coding: utf-8 -*-
"""
Purge les versions de référentiel figées qui ne servent plus.

Quatre versions du même corpus ont fait passer `data/eau.duckdb` de 546 à
713 Mo en deux jours. Elles sont la trace de ce qui a été publié sous chaque
grille — mais cette trace est **reconstructible** : le référentiel est
versionné dans git, et refiger prend une vingtaine de minutes.

**Règle arrêtée par Yannick le 10 août 2026 : on garde la version publiée et
une seule antérieure.** Le reste se supprime.

Le script ne devine rien : il refuse d'agir si la version courante du
référentiel n'est pas figée, il liste ce qu'il va faire, et il faut `--faire`
pour qu'il écrive. Un VACUUM suit, sans quoi le fichier ne rend pas la place.

Usage :

    py -X utf8 src/purger_versions.py            # ce qui serait supprimé
    py -X utf8 src/purger_versions.py --faire
    py -X utf8 src/purger_versions.py --garder 3 --faire
"""

import argparse
import os
import sys

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

import figer  # noqa: E402

DB_PATH = os.path.join(RACINE, "data", "eau.duckdb")

# Les tables estampillées par une version de référentiel. Une version purgée
# doit disparaître de TOUTES, sinon une jointure ramène des orphelines.
TABLES = ("verdicts_figes", "analyses_figees", "couverture_communes", "lq_corpus")


def etat(con):
    """[(version, date de calcul, bulletins)] — la plus récente d'abord."""
    return con.execute("""
        SELECT version_referentiel, MAX(calcule_le), COUNT(*)
        FROM analyses_figees GROUP BY 1 ORDER BY MAX(calcule_le) DESC, 1
    """).fetchall()


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--garder", type=int, default=2,
                   help="nombre de versions conservées, la publiée comprise (défaut 2)")
    p.add_argument("--faire", action="store_true",
                   help="exécute ; sans lui, le script se contente de lister")
    a = p.parse_args()

    courante = figer.version_referentiel()
    con = duckdb.connect(DB_PATH)
    try:
        lignes = etat(con)
        versions = [r[0] for r in lignes]
        if courante not in versions:
            print(f"la version courante du référentiel ({courante}) n'est PAS figée.")
            print("refige d'abord : py -X utf8 src/figer.py")
            sys.exit(1)

        # La publiée d'abord, puis les plus récentes des autres.
        garder = [courante] + [v for v in versions if v != courante]
        garder = garder[:max(1, a.garder)]
        jeter = [v for v in versions if v not in garder]

        taille = os.path.getsize(DB_PATH) / 1024 / 1024
        print(f"base : {taille:.0f} Mo · {len(versions)} version(s) figée(s)\n")
        for v, d, n in lignes:
            marque = ("PUBLIÉE" if v == courante else
                      "conservée" if v in garder else "à supprimer")
            print(f"  {v}  {d}  {n:>5} bulletin(s)  — {marque}")

        if not jeter:
            print("\nrien à purger.")
            return
        if not a.faire:
            print(f"\n{len(jeter)} version(s) seraient supprimées. "
                  "Relance avec --faire pour agir.")
            return

        for v in jeter:
            for t in TABLES:
                try:
                    con.execute(f"DELETE FROM {t} WHERE version_referentiel = ?", [v])
                except duckdb.CatalogException:
                    pass          # une table peut ne pas exister sur un corpus ancien
            print(f"  supprimée : {v}")

        # Sans ceci, DuckDB garde les pages libérées et le fichier ne maigrit pas.
        con.execute("CHECKPOINT")
        con.close()
        con = duckdb.connect(DB_PATH)
        con.execute("VACUUM")
        con.execute("CHECKPOINT")
        apres = os.path.getsize(DB_PATH) / 1024 / 1024
        print(f"\nbase : {taille:.0f} Mo -> {apres:.0f} Mo")
        print("versions restantes :")
        for v, d, n in etat(con):
            print(f"  {v}  {d}  {n} bulletin(s)")
    finally:
        con.close()


if __name__ == "__main__":
    main()

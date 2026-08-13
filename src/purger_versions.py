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
    """
    [(version, date de calcul, bulletins, lignes ailleurs)] — la plus récente
    d'abord.

    **Les versions s'énumèrent sur TOUTES les tables estampillées, pas sur la
    seule `analyses_figees`.** Corrigé le 13 août 2026, après que la purge eut
    répondu « rien à purger » alors que `couverture_communes` portait quatre
    générations et `lq_corpus` trois. La cause : un refigeage complet réécrit
    `analyses_figees` sous la version courante et fait disparaître les
    anciennes de CETTE table — mais les autres gardent les leurs, orphelines et
    invisibles à qui ne regarde que la première. C'est le point aveugle relevé
    au §19.1 de `docs/REPRISE.md`, et il rendait la purge inopérante
    précisément quand elle servait.
    """
    vues = {}
    for t in TABLES:
        try:
            # Toutes ne portent pas `calcule_le` — `verdicts_figes` ne l'a pas,
            # la date vient alors d'une autre table de la même version.
            cols = {r[0] for r in con.execute(f"DESCRIBE {t}").fetchall()}
            quand = "MAX(calcule_le)" if "calcule_le" in cols else "NULL"
            for v, d, n in con.execute(f"""
                SELECT version_referentiel, {quand}, COUNT(*)
                FROM {t} GROUP BY 1
            """).fetchall():
                e = vues.setdefault(v, {"date": d, "bulletins": 0, "ailleurs": 0})
                if d and (not e["date"] or d > e["date"]):
                    e["date"] = d
                if t == "analyses_figees":
                    e["bulletins"] = n
                else:
                    e["ailleurs"] += n
        except duckdb.CatalogException:
            pass              # une table peut ne pas exister sur un corpus ancien
    return sorted(((v, e["date"], e["bulletins"], e["ailleurs"])
                   for v, e in vues.items()),
                  key=lambda r: (r[1] or "", r[0]), reverse=True)


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
        for v, d, n, ailleurs in lignes:
            marque = ("PUBLIÉE" if v == courante else
                      "conservée" if v in garder else "à supprimer")
            # Une génération orpheline n'a plus de bulletin mais garde des
            # lignes ailleurs : c'est exactement ce que l'ancienne énumération
            # ne voyait pas. La distinguer à l'affichage.
            quoi = (f"{n:>5} bulletin(s)" if n else "    — orpheline")
            print(f"  {v}  {d}  {quoi} + {ailleurs:>5} ligne(s) "
                  f"ailleurs  — {marque}")

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
        for v, d, n, ailleurs in etat(con):
            print(f"  {v}  {d}  {n} bulletin(s) + {ailleurs} ligne(s) ailleurs")
    finally:
        con.close()


if __name__ == "__main__":
    main()

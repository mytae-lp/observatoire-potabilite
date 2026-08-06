# -*- coding: utf-8 -*-
"""
Collecte Hub'Eau pour une liste de communes précises (commodité).

    python3 src/fetch_hubeau.py 17415 46040 82125
    python3 src/fetch_hubeau.py --tous 17415          # tous les bulletins complets

Pour un département entier, utiliser src/fetch_departement.py, qui ajoute
l'énumération des communes, le journal de reprise et le rapport de couverture.

Ce script fait des requêtes HTTP : environnement avec accès réseau depuis le
shell (ta machine, Claude Code), pas un bac à sable — voir CLAUDE.md §3.1.
"""
import sys
import time

import duckdb

import ingest
from common import DB_PATH, SEUIL_COMPLET
from fetch_departement import bulletin_meta, dates_completes, fetch_bulletin_rows, PAUSE_COMMUNE


def run(insee_list, tous=False, db=DB_PATH):
    con = duckdb.connect(db)
    try:
        for insee in insee_list:
            completes = dates_completes(insee, tous=tous)
            if not completes:
                print(f"[{insee}] aucun bulletin complet (> {SEUIL_COMPLET} paramètres) — ignoré")
                continue
            for date, _ in completes:
                rows = fetch_bulletin_rows(insee, date)
                dept = (rows[0].get("code_departement") if rows else None) or insee[:2]
                nom = rows[0].get("nom_commune") if rows else None
                _, nb, complet = ingest.ingest_bulletin(
                    con, bulletin_meta(insee, nom, dept, date, rows), rows
                )
                print(f"[{insee}] {date} — {nb} paramètres ingérés (complet={complet})")
                time.sleep(PAUSE_COMMUNE)
    finally:
        con.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Usage: python3 src/fetch_hubeau.py [--tous] <code_insee> [<code_insee> ...]")
        sys.exit(1)
    run(args, tous="--tous" in sys.argv)

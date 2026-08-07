# -*- coding: utf-8 -*-
"""
Collecte Hub'Eau pour une liste de communes précises.

    python3 src/fetch_hubeau.py 17415 31446        # codes INSEE
    python3 src/fetch_hubeau.py 31520              # code postal (résolu en INSEE)
    python3 src/fetch_hubeau.py --tous 17415       # tous les bulletins complets de chaque point

Pour un département entier, utiliser src/fetch_departement.py, qui ajoute
l'énumération des communes, le journal de reprise et le rapport de couverture.

Chaque point d'eau de la commune (installation de production amont) donne son
propre bulletin : si trois installations alimentent la commune, trois
bulletins sont collectés.

Ce script fait des requêtes HTTP : environnement avec accès réseau depuis le
shell (ta machine, Claude Code), pas un bac à sable — voir CLAUDE.md §3.1.
"""
import sys
import time

import duckdb

import ingest
import hubeau
from common import DB_PATH, SEUIL_COMPLET


def resoudre(code):
    """Code INSEE ou code postal -> [(code_insee, nom, extras), ...].

    Un code INSEE fait 5 caractères et peut comporter une lettre (Corse :
    2A004). Un code postal fait 5 chiffres. Les deux se ressemblent, donc on
    tente d'abord le code postal et on retombe sur l'INSEE si rien ne sort.
    """
    code = str(code).strip()
    if len(code) == 5 and code.isdigit():
        communes = hubeau.communes_par_code_postal(code)
        if communes:
            return [(c["code_insee"], c["nom"], c) for c in communes]
    return [(code, None, {})]


def run(codes, tous=False, db=DB_PATH):
    con = duckdb.connect(db)
    try:
        for code in codes:
            for insee, nom, extras in resoudre(code):
                etiquette = f"{insee} {nom or ''}".strip()
                if str(code) != insee:
                    etiquette = f"{code} -> {etiquette}"
                bulletins = hubeau.derniers_bulletins_complets(insee, tous=tous)
                if not bulletins:
                    print(f"[{etiquette}] aucun bulletin complet "
                          f"(> {SEUIL_COMPLET} paramètres) — ignoré")
                    continue
                for code_prel, rows in bulletins.items():
                    meta = hubeau.bulletin_meta(insee, nom, insee[:2], rows)
                    meta.update({"codes_postaux": extras.get("codes_postaux"),
                                 "lon": extras.get("lon"), "lat": extras.get("lat")})
                    _, nb, complet = ingest.ingest_bulletin(con, meta, rows)
                    print(f"[{etiquette}] {meta['date_prelevement']} "
                          f"{meta.get('nom_installation_amont') or 'installation non renseignée'} "
                          f"— {nb} paramètres (complet={complet})")
                time.sleep(hubeau.PAUSE_COMMUNE)
    finally:
        con.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Usage: python3 src/fetch_hubeau.py [--tous] <code_insee|code_postal> [...]")
        sys.exit(1)
    run(args, tous="--tous" in sys.argv)

# -*- coding: utf-8 -*-
"""
Collecte automatique à l'échelle d'un département.

    python3 src/fetch_departement.py --dept 17
    python3 src/fetch_departement.py --dept 17 --limite 10        # essai sur 10 communes
    python3 src/fetch_departement.py --dept 17 --depuis 2020 --tous
    python3 src/fetch_departement.py --dept 17 --rapport          # relit le journal, ne collecte rien

Ce script fait des requêtes HTTP : il doit tourner dans un environnement avec
accès réseau depuis le shell (ta machine, Claude Code) — pas dans un bac à
sable. Voir CLAUDE.md §3.1.

Ce qu'il fait :
  1. énumère les communes du département ;
  2. inventorie les prélèvements de chaque commune (champs réduits) ;
  3. retient, POUR CHAQUE POINT D'EAU, le dernier prélèvement complet
     (> 250 paramètres) — une commune alimentée par trois installations
     donne trois bulletins ;
  4. rapatrie chaque bulletin entier, l'ingère et journalise, de façon
     reprenable après coupure.

L'accès réseau est entièrement dans src/hubeau.py.
"""
import argparse
import collections
import json
import os
import sys
import time

import duckdb

import ingest
import hubeau
from common import DB_PATH, JOURNAL_DIR, SEUIL_COMPLET


# ---------------------------------------------------------------------------
# Journal de reprise
# ---------------------------------------------------------------------------
def chemin_journal(dept):
    os.makedirs(JOURNAL_DIR, exist_ok=True)
    return os.path.join(JOURNAL_DIR, f"dept_{dept}.jsonl")


def lire_journal(dept):
    """{code_insee: dernière entrée} — permet de reprendre où on s'est arrêté."""
    chemin = chemin_journal(dept)
    vu = {}
    if not os.path.exists(chemin):
        return vu
    with open(chemin, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                e = json.loads(ligne)
            except json.JSONDecodeError:
                continue
            if e.get("code_insee"):
                vu[e["code_insee"]] = e
    return vu


def ecrire_journal(dept, entree):
    with open(chemin_journal(dept), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entree, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Rapport de couverture
# ---------------------------------------------------------------------------
def rapport(dept, db=DB_PATH):
    vu = lire_journal(dept)
    if vu:
        etats = collections.Counter(e.get("etat") for e in vu.values())
        total = len(vu)
        print(f"\n=== Couverture département {dept} ===")
        print(f"communes traitées        : {total}")
        for etat, n in etats.most_common():
            print(f"  {etat:<22} {n:>5}  ({100*n/total:.1f} %)")

        ingerees = [e for e in vu.values() if e.get("etat") == "ingere"]
        if ingerees:
            params = [e.get("nb_parametres", 0) for e in ingerees]
            print(f"paramètres par bulletin  : min {min(params)}, médian "
                  f"{sorted(params)[len(params)//2]}, max {max(params)}")
            dates = sorted(e.get("date", "") for e in ingerees)
            print(f"dates de prélèvement     : {dates[0]} → {dates[-1]}")
            points = sum(e.get("nb_bulletins", 1) for e in ingerees)
            print(f"points d'eau analysés    : {points} pour {len(ingerees)} commune(s)")
    else:
        print(f"aucun journal pour le département {dept}")

    if not os.path.exists(db):
        return
    con = duckdb.connect(db, read_only=True)
    try:
        r = con.execute("""
            SELECT COUNT(*) FILTER (WHERE est_complet),
                   COUNT(*) FILTER (WHERE est_complet AND nb_depasse_2026 = 0
                                    AND nb_bascules > 0),
                   SUM(nb_bascules) FILTER (WHERE est_complet),
                   ROUND(AVG(pct_couverture) FILTER (WHERE est_complet), 1)
            FROM v_prelevement_verdict WHERE dept = ?
        """, [dept]).fetchone()
        print(f"\nen base — bulletins complets : {r[0] or 0}")
        print(f"          couverture moyenne des mesures : {r[3] or 0} %")
        print(f"          conformes 2026 AVEC bascule : {r[1] or 0}   <-- les cas")
        print(f"          bascules cumulées : {r[2] or 0}")
        na = con.execute("SELECT COUNT(*) FROM v_parametres_non_apparies").fetchone()[0]
        print(f"          libellés sans aucun seuil de comparaison : {na}")
        print("          (SELECT * FROM v_parametres_non_apparies LIMIT 40)")
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------
def traiter_commune(con, insee, nom, dept, depuis=None, tous=False):
    """Collecte et ingère tous les points d'eau complets d'une commune.
    Retourne la liste des bulletins ingérés."""
    bulletins = hubeau.derniers_bulletins_complets(insee, depuis=depuis, tous=tous)
    ingerees = []
    for code_prel, rows in bulletins.items():
        meta = hubeau.bulletin_meta(insee, nom, dept, rows)
        cp, nb, complet = ingest.ingest_bulletin(con, meta, rows)
        ingerees.append({
            "code_prelevement": cp,
            "date": meta["date_prelevement"],
            "nb_parametres": nb,
            "est_complet": complet,
            "installation": meta.get("nom_installation_amont"),
        })
    return ingerees


def run(dept, limite=None, depuis=None, tous=False, reprendre=True, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : python3 src/build_db.py")
        sys.exit(1)

    communes = hubeau.lister_communes(dept)
    vu = lire_journal(dept) if reprendre else {}
    if vu:
        print(f"journal   : {len(vu)} commune(s) déjà traitée(s), reprise")

    a_faire = [(i, n) for i, n in sorted(communes.items()) if i not in vu]
    if limite:
        a_faire = a_faire[:limite]
    print(f"à traiter : {len(a_faire)} commune(s)\n")

    con = duckdb.connect(db)
    t0 = time.time()
    stats = collections.Counter()
    try:
        for idx, (insee, nom) in enumerate(a_faire, 1):
            prefixe = f"[{idx}/{len(a_faire)}] {insee} {nom or ''}".strip()
            try:
                ingerees = traiter_commune(con, insee, nom, dept,
                                           depuis=depuis, tous=tous)
            except Exception as e:
                print(f"{prefixe} — ERREUR : {type(e).__name__}: {e}")
                ecrire_journal(dept, {"code_insee": insee, "nom": nom,
                                      "etat": "erreur", "message": str(e)})
                stats["erreur"] += 1
                continue

            if not ingerees:
                print(f"{prefixe} — aucun bulletin complet (> {SEUIL_COMPLET} paramètres)")
                ecrire_journal(dept, {"code_insee": insee, "nom": nom,
                                      "etat": "aucun_complet"})
                stats["aucun_complet"] += 1
                time.sleep(hubeau.PAUSE_COMMUNE)
                continue

            for b in ingerees:
                print(f"{prefixe} — {b['date']} : {b['nb_parametres']} paramètres "
                      f"({b['installation'] or 'installation non renseignée'})")
            dernier = max(ingerees, key=lambda b: b["date"])
            ecrire_journal(dept, {"code_insee": insee, "nom": nom, "etat": "ingere",
                                  "date": dernier["date"],
                                  "nb_parametres": dernier["nb_parametres"],
                                  "nb_bulletins": len(ingerees)})
            stats["ingere"] += 1
            time.sleep(hubeau.PAUSE_COMMUNE)
    except KeyboardInterrupt:
        print("\ninterruption — le journal permet de reprendre par la même commande")
    finally:
        con.close()

    duree = time.time() - t0
    print(f"\nterminé en {duree/60:.1f} min — "
          + ", ".join(f"{k}: {v}" for k, v in stats.most_common()))
    rapport(dept, db)


def main():
    p = argparse.ArgumentParser(description="Collecte Hub'Eau à l'échelle d'un département")
    p.add_argument("--dept", required=True, help="code département (ex. 17, 2A, 971)")
    p.add_argument("--limite", type=int, help="ne traiter que les N premières communes (essai)")
    p.add_argument("--depuis", help="année minimale de prélèvement (ex. 2020)")
    p.add_argument("--tous", action="store_true",
                   help="tous les bulletins complets de chaque point d'eau, pas seulement le dernier")
    p.add_argument("--reprendre-a-zero", action="store_true",
                   help="ignorer le journal et retraiter toutes les communes")
    p.add_argument("--rapport", action="store_true",
                   help="afficher la couverture sans rien collecter")
    a = p.parse_args()

    if a.rapport:
        rapport(a.dept)
        return
    run(a.dept, limite=a.limite, depuis=a.depuis, tous=a.tous,
        reprendre=not a.reprendre_a_zero)


if __name__ == "__main__":
    main()

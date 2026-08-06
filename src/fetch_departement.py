# -*- coding: utf-8 -*-
"""
Collecte automatique à l'échelle d'un département.

    python3 src/fetch_departement.py --dept 17
    python3 src/fetch_departement.py --dept 17 --limite 10        # essai sur 10 communes
    python3 src/fetch_departement.py --dept 17 --depuis 2015 --tous
    python3 src/fetch_departement.py --dept 17 --rapport          # relit le journal, ne collecte rien

Ce script fait des requêtes HTTP : il doit tourner dans un environnement avec
accès réseau depuis le shell (ta machine, Claude Code) — pas dans un bac à
sable. Voir CLAUDE.md §3.1.

Ce qu'il fait :
  1. énumère les communes du département (Hub'Eau communes_udi, repli geo.api.gouv.fr) ;
  2. pour chaque commune, compte les paramètres par date de prélèvement ;
  3. ne retient que les prélèvements COMPLETS (> 250 paramètres) — c'est la règle
     de méthode du projet, et accessoirement ce qui rend la collecte tenable :
     on télécharge quelques bulletins par commune, pas des dizaines de milliers
     de lignes de routine ;
  4. ingère et journalise, de façon reprenable après coupure.

Étiquette : pagination maximale, pause entre appels, reprise sur incident,
User-Agent identifiant le projet. L'API est un service public gratuit.
"""
import argparse
import collections
import json
import os
import sys
import time

import requests
import duckdb

import ingest
from common import DB_PATH, JOURNAL_DIR, SEUIL_COMPLET, USER_AGENT

BASE = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis"
BASE_UDI = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/communes_udi"
GEO = "https://geo.api.gouv.fr/departements/{dept}/communes"

PAGE = 5000
PAUSE = 0.3          # entre deux pages
PAUSE_COMMUNE = 0.5  # entre deux communes
MAX_TENTATIVES = 4

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})


# ---------------------------------------------------------------------------
# Accès réseau : une seule porte, avec temporisation et reprise
# ---------------------------------------------------------------------------
def _get(url, params):
    """GET avec retentative exponentielle. Respecte Retry-After sur 429."""
    attente = 2.0
    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            r = SESSION.get(url, params=params, timeout=90)
            if r.status_code == 429:
                delai = float(r.headers.get("Retry-After", attente))
                print(f"    429 — pause {delai:.0f}s")
                time.sleep(delai)
                attente *= 2
                continue
            if r.status_code in (500, 502, 503, 504):
                print(f"    {r.status_code} — nouvelle tentative dans {attente:.0f}s")
                time.sleep(attente)
                attente *= 2
                continue
            r.raise_for_status()
            return r.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            if tentative == MAX_TENTATIVES:
                raise
            print(f"    {type(e).__name__} — nouvelle tentative dans {attente:.0f}s")
            time.sleep(attente)
            attente *= 2
    raise RuntimeError(f"échec après {MAX_TENTATIVES} tentatives : {url}")


def _pages(url, params):
    """Itère sur les pages d'un endpoint Hub'Eau."""
    page = 1
    while True:
        j = _get(url, dict(params, size=PAGE, page=page))
        data = j.get("data", []) or []
        yield data
        if len(data) < PAGE or not j.get("next"):
            return
        page += 1
        time.sleep(PAUSE)


# ---------------------------------------------------------------------------
# 1. Énumération des communes
# ---------------------------------------------------------------------------
def communes_hubeau(dept):
    """Communes rattachées à une UDI dans ce département, selon Hub'Eau.
    Ce sont les seules susceptibles de porter des résultats d'analyse."""
    trouvees = {}
    for data in _pages(BASE_UDI, {"code_departement": dept,
                                  "fields": "code_commune,nom_commune"}):
        for row in data:
            code = row.get("code_commune")
            if code:
                trouvees[str(code)] = row.get("nom_commune")
    return trouvees


def communes_geo(dept):
    """Repli : toutes les communes du département (API Découpage administratif)."""
    j = _get(GEO.format(dept=dept), {"fields": "code,nom"})
    return {c["code"]: c.get("nom") for c in j}


def lister_communes(dept):
    try:
        c = communes_hubeau(dept)
        if c:
            print(f"communes  : {len(c)} rattachées à une UDI (Hub'Eau communes_udi)")
            return c
        print("communes  : communes_udi n'a rien renvoyé — repli geo.api.gouv.fr")
    except Exception as e:
        print(f"communes  : communes_udi indisponible ({e}) — repli geo.api.gouv.fr")
    c = communes_geo(dept)
    print(f"communes  : {len(c)} communes du département (geo.api.gouv.fr)")
    return c


# ---------------------------------------------------------------------------
# 2. Repérage des bulletins complets
# ---------------------------------------------------------------------------
def dates_counts(insee, depuis=None):
    """Nombre de paramètres par date de prélèvement pour une commune."""
    compte = collections.Counter()
    params = {"code_commune": insee, "fields": "date_prelevement"}
    if depuis:
        params["date_min_prelevement"] = f"{depuis}-01-01"
    for data in _pages(BASE, params):
        for row in data:
            d = row.get("date_prelevement")
            if d:
                compte[str(d)[:10]] += 1
    return sorted(compte.items(), key=lambda kv: kv[0], reverse=True)


def dates_completes(insee, depuis=None, tous=False, seuil=SEUIL_COMPLET):
    """Dates des prélèvements complets, la plus récente d'abord.
    Par défaut on ne garde que la plus récente ; --tous les prend toutes
    (nécessaire pour une série temporelle, plus coûteux)."""
    completes = [(d, n) for d, n in dates_counts(insee, depuis) if n > seuil]
    return completes if tous else completes[:1]


def fetch_bulletin_rows(insee, date):
    """Toutes les lignes du prélèvement de cette commune à cette date.

    Le filtre de date de l'API s'étant révélé peu fiable, on filtre côté
    client. L'API triant par date décroissante, on s'arrête dès qu'une page
    entière est passée sous la date cible."""
    rows = []
    for data in _pages(BASE, {"code_commune": insee}):
        rows += [d for d in data if str(d.get("date_prelevement", "")).startswith(date)]
        if data and all(str(d.get("date_prelevement", ""))[:10] < date for d in data):
            break
    return rows


def bulletin_meta(insee, nom, dept, date, rows):
    r0 = rows[0] if rows else {}
    return {
        "code_insee": insee,
        "nom": r0.get("nom_commune") or nom,
        "code_departement": r0.get("code_departement") or dept,
        "nom_installation": r0.get("nom_installation_amont") or r0.get("nom_reseau"),
        "nom_distributeur": r0.get("nom_distributeur"),
        "date_prelevement": date[:10],
        "conclusion_conformite": r0.get("conclusion_conformite_prelevement"),
        "conf_limites_bact": r0.get("conformite_limites_bact_prelevement"),
        "conf_limites_pc": r0.get("conformite_limites_pc_prelevement"),
        "conf_references_pc": r0.get("conformite_references_pc_prelevement"),
        "source_url": f"{BASE}?code_commune={insee}&date_min_prelevement={date[:10]}"
                      f"&date_max_prelevement={date[:10]}&size=5000",
    }


# ---------------------------------------------------------------------------
# 3. Journal de reprise
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
# 4. Rapport de couverture
# ---------------------------------------------------------------------------
def rapport(dept, db=DB_PATH):
    vu = lire_journal(dept)
    if not vu:
        print(f"aucun journal pour le département {dept}")
        return
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

    if os.path.exists(db):
        con = duckdb.connect(db, read_only=True)
        try:
            r = con.execute("""
                SELECT COUNT(*) FILTER (WHERE est_complet),
                       COUNT(*) FILTER (WHERE est_complet AND nb_depasse_2026 = 0
                                        AND nb_bascules > 0),
                       SUM(nb_bascules) FILTER (WHERE est_complet)
                FROM v_prelevement_verdict WHERE dept = ?
            """, [dept]).fetchone()
            print(f"\nen base — bulletins complets : {r[0] or 0}")
            print(f"          conformes 2026 AVEC bascule : {r[1] or 0}   <-- les cas")
            print(f"          bascules cumulées : {r[2] or 0}")
            na = con.execute("SELECT COUNT(*) FROM v_parametres_non_apparies").fetchone()[0]
            print(f"          libellés non appariés au référentiel : {na}")
            print("          (SELECT * FROM v_parametres_non_apparies LIMIT 40)")
        finally:
            con.close()


# ---------------------------------------------------------------------------
# 5. Boucle principale
# ---------------------------------------------------------------------------
def run(dept, limite=None, depuis=None, tous=False, reprendre=True, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : python3 src/build_db.py")
        sys.exit(1)

    communes = lister_communes(dept)
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
                completes = dates_completes(insee, depuis=depuis, tous=tous)
            except Exception as e:
                print(f"{prefixe} — ERREUR énumération : {e}")
                ecrire_journal(dept, {"code_insee": insee, "nom": nom,
                                      "etat": "erreur", "message": str(e)})
                stats["erreur"] += 1
                continue

            if not completes:
                print(f"{prefixe} — aucun bulletin complet (> {SEUIL_COMPLET} paramètres)")
                ecrire_journal(dept, {"code_insee": insee, "nom": nom,
                                      "etat": "aucun_complet"})
                stats["aucun_complet"] += 1
                time.sleep(PAUSE_COMMUNE)
                continue

            ingerees = []
            for date, n in completes:
                try:
                    rows = fetch_bulletin_rows(insee, date)
                    code_prel, nb, complet = ingest.ingest_bulletin(
                        con, bulletin_meta(insee, nom, dept, date, rows), rows
                    )
                    ingerees.append({"date": date, "code_prelevement": code_prel,
                                     "nb_parametres": nb, "est_complet": complet})
                    print(f"{prefixe} — {date} : {nb} paramètres (complet={complet})")
                except Exception as e:
                    print(f"{prefixe} — ERREUR {date} : {e}")
                    stats["erreur"] += 1
                time.sleep(PAUSE_COMMUNE)

            if ingerees:
                dernier = ingerees[0]
                ecrire_journal(dept, {"code_insee": insee, "nom": nom, "etat": "ingere",
                                      "date": dernier["date"],
                                      "nb_parametres": dernier["nb_parametres"],
                                      "nb_bulletins": len(ingerees)})
                stats["ingere"] += 1
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
    p.add_argument("--depuis", help="année minimale de prélèvement (ex. 2015)")
    p.add_argument("--tous", action="store_true",
                   help="tous les bulletins complets, pas seulement le dernier")
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

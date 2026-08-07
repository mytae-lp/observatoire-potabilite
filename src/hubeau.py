# -*- coding: utf-8 -*-
"""
Couche d'accès aux données publiques. Une seule porte vers le réseau.

Ce module ne connaît ni DuckDB ni le référentiel : il sait énumérer des
communes, repérer les bulletins complets et les rapatrier entiers.

Deux faits vérifiés sur l'API pilotent toute la logique de ce fichier
--------------------------------------------------------------------

1. **Un prélèvement chevauche les pages.** Avec `size=5000`, le prélèvement
   01700148852 de Saintes s'étale sur la fin de la page 1 et le début de la
   page 2. Toute logique qui s'arrête en fin de page tronque un bulletin —
   et un bulletin tronqué peut passer sous SEUIL_COMPLET et disparaître de
   l'analyse, ou pire y entrer amputé. D'où le repérage en deux temps :
   d'abord un inventaire à champs réduits (léger, exhaustif), ensuite le
   rapatriement ciblé des seuls bulletins retenus.

2. **Le filtre de date fonctionne, à condition de borner à J+1.**
   `date_max_prelevement=2026-03-05` renvoie 0 ligne parce que les
   horodatages de la journée (`2026-03-05T09:45:00Z`) sont postérieurs à
   `2026-03-05T00:00:00`. Avec `date_max=2026-03-06`, la journée entière
   revient. C'est ce qui permet de rapatrier un bulletin en un seul appel
   au lieu de retélécharger l'historique complet de la commune.

Étiquette (CLAUDE.md §3.2) : pagination maximale, pause entre appels,
retentative exponentielle, User-Agent identifiant le projet.
"""
import collections
import datetime
import time

import requests

from common import SEUIL_COMPLET, USER_AGENT

BASE = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis"
BASE_UDI = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/communes_udi"
GEO = "https://geo.api.gouv.fr/departements/{dept}/communes"
GEO_COMMUNES = "https://geo.api.gouv.fr/communes"

PAGE = 5000
PAUSE = 0.3          # entre deux pages
PAUSE_COMMUNE = 0.5  # entre deux communes
MAX_TENTATIVES = 4

# Champs strictement nécessaires au repérage des bulletins complets.
# Réduire la charge utile de 32 à 4 colonnes rend l'inventaire exhaustif
# abordable : on peut parcourir tout l'historique d'une commune sans peser
# sur un service public gratuit.
CHAMPS_INVENTAIRE = "code_prelevement,date_prelevement,code_installation_amont,nom_installation_amont"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})


# ---------------------------------------------------------------------------
# Accès réseau
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
# Code postal -> code INSEE
# ---------------------------------------------------------------------------
def communes_par_code_postal(cp):
    """
    Code postal -> [{code_insee, nom, population, lon, lat}, ...].

    Un code postal peut couvrir plusieurs communes : la fonction renvoie
    toujours une liste, jamais une valeur. Les coordonnées servent à la
    cartographie.
    """
    j = _get(GEO_COMMUNES, {"codePostal": str(cp).strip(),
                            "fields": "code,nom,codesPostaux,population,centre"})
    out = []
    for c in j or []:
        centre = (c.get("centre") or {}).get("coordinates") or [None, None]
        out.append({
            "code_insee": c["code"],
            "nom": c.get("nom"),
            "population": c.get("population"),
            "lon": centre[0],
            "lat": centre[1],
            "codes_postaux": "|".join(c.get("codesPostaux") or []),
        })
    return out


# ---------------------------------------------------------------------------
# Énumération des communes d'un département
# ---------------------------------------------------------------------------
def commune_par_insee(insee):
    """Code INSEE -> {code_insee, nom, population, lon, lat, codes_postaux}.
    Sert aussi à la cartographie : le centroïde vient de la même requête."""
    try:
        c = _get(f"{GEO_COMMUNES}/{insee}",
                 {"fields": "code,nom,codesPostaux,population,centre"})
    except Exception:
        return {"code_insee": insee, "nom": None, "population": None,
                "lon": None, "lat": None, "codes_postaux": None}
    centre = (c.get("centre") or {}).get("coordinates") or [None, None]
    return {"code_insee": c.get("code", insee), "nom": c.get("nom"),
            "population": c.get("population"), "lon": centre[0], "lat": centre[1],
            "codes_postaux": "|".join(c.get("codesPostaux") or []) or None}


def communes_geo(dept):
    """Communes du département (API Découpage administratif). Un appel, exact."""
    j = _get(GEO.format(dept=dept), {"fields": "code,nom"})
    return {c["code"]: c.get("nom") for c in j}


def communes_hubeau(dept):
    """
    Communes rattachées à une UDI dans ce département, selon Hub'Eau.

    ATTENTION — l'endpoint communes_udi IGNORE ses filtres : `code_departement`,
    `nom_departement` ou aucun filtre renvoient tous `count=544066`, la France
    entière, triée à partir de l'Ain (vérifié). Le filtrage est donc fait ici,
    côté client, et l'appel coûte 109 pages de 5000 lignes.

    C'est la raison pour laquelle ce n'est PAS la source par défaut : demander
    « le département 17 » ne doit pas déclencher le téléchargement du pays.
    """
    trouvees = {}
    for data in _pages(BASE_UDI, {"fields": "code_commune,nom_commune"}):
        for row in data:
            code = str(row.get("code_commune") or "")
            if code.startswith(str(dept)):
                trouvees[code] = row.get("nom_commune")
    return trouvees


def lister_communes(dept, via_udi=False):
    """
    Communes à parcourir pour un département.

    Par défaut geo.api.gouv.fr : un appel, exact, et une commune sans données
    ressort simplement sans bulletin complet. `via_udi=True` restreint aux
    communes rattachées à une UDI, au prix d'un balayage national.
    """
    if via_udi:
        c = communes_hubeau(dept)
        if c:
            print(f"communes  : {len(c)} rattachées à une UDI "
                  f"(Hub'Eau communes_udi, filtré côté client)")
            return c
        print("communes  : communes_udi n'a rien renvoyé — repli geo.api.gouv.fr")
    c = communes_geo(dept)
    print(f"communes  : {len(c)} communes du département (geo.api.gouv.fr)")
    return c


# ---------------------------------------------------------------------------
# 1. Inventaire : quels prélèvements existent, et de quelle taille
# ---------------------------------------------------------------------------
def inventaire_prelevements(insee, depuis=None):
    """
    code_prelevement -> {date, code_installation_amont, nom_installation_amont, nb_lignes}

    Parcours EXHAUSTIF de l'historique de la commune, à champs réduits. On ne
    s'arrête pas en cours de route : un prélèvement à cheval sur deux pages
    serait compté à moitié, et un bulletin complet paraîtrait incomplet.

    nb_lignes est le nombre de lignes du prélèvement, soit son nombre de
    paramètres (une ligne = un paramètre). Le compte définitif, après
    déduplication par libellé, est fait à l'ingestion.
    """
    params = {"code_commune": insee, "fields": CHAMPS_INVENTAIRE}
    if depuis:
        params["date_min_prelevement"] = f"{depuis}-01-01"

    inv = {}
    for data in _pages(BASE, params):
        for row in data:
            cp = row.get("code_prelevement")
            if not cp:
                continue
            e = inv.get(cp)
            if e is None:
                inv[cp] = {
                    "code_prelevement": cp,
                    "date": str(row.get("date_prelevement") or "")[:10],
                    "code_installation_amont": row.get("code_installation_amont"),
                    "nom_installation_amont": row.get("nom_installation_amont"),
                    "nb_lignes": 1,
                }
            else:
                e["nb_lignes"] += 1
    return inv


def selectionner_bulletins(inventaire, tous=False, seuil=SEUIL_COMPLET):
    """
    Inventaire -> les bulletins à rapatrier.

    Règle du projet : on repart du DERNIER bulletin complet de chaque point
    d'eau. Un point d'eau = une installation de production amont
    (`code_installation_amont`). Si une commune est alimentée par trois
    installations, les trois sont analysées — c'est la demande, et c'est
    aussi ce qui permettra plus tard de voir si un mélange conforme masque
    une ressource qui ne l'est pas.

    Les prélèvements sans installation amont renseignée sont regroupés sous
    une clé propre plutôt qu'écartés : les ignorer ferait disparaître des
    communes entières.
    """
    complets = [e for e in inventaire.values() if e["nb_lignes"] > seuil]
    par_point = collections.defaultdict(list)
    for e in complets:
        par_point[e["code_installation_amont"] or "SANS_INSTALLATION"].append(e)

    retenus = []
    for _point, liste in par_point.items():
        liste.sort(key=lambda e: (e["date"], e["code_prelevement"]), reverse=True)
        retenus += liste if tous else liste[:1]
    retenus.sort(key=lambda e: e["date"], reverse=True)
    return retenus


# ---------------------------------------------------------------------------
# 2. Rapatriement d'un bulletin, entier
# ---------------------------------------------------------------------------
def fetch_bulletin(insee, code_prelevement, date):
    """
    Toutes les lignes d'UN prélèvement, et de lui seul.

    Bornage à J+1 : `date_max_prelevement` est comparé à un horodatage, donc
    borner au jour même renvoie zéro ligne (vérifié). On filtre ensuite sur
    code_prelevement, parce qu'une commune peut avoir plusieurs prélèvements
    le même jour, sur des points différents — les fusionner produirait un
    faux bulletin (CLAUDE.md §2.3 : une analyse porte sur UN prélèvement).
    """
    d = datetime.date.fromisoformat(date[:10])
    lendemain = (d + datetime.timedelta(days=1)).isoformat()
    rows = []
    for data in _pages(BASE, {"code_commune": insee,
                              "date_min_prelevement": d.isoformat(),
                              "date_max_prelevement": lendemain}):
        rows += [r for r in data if str(r.get("code_prelevement")) == str(code_prelevement)]
    return rows


def reseaux_de_la_commune(insee, depuis=None):
    """
    Codes des réseaux (UDI) qui alimentent la commune, les plus récents d'abord.

    Lus dans les prélèvements de la commune eux-mêmes : `communes_udi` serait
    la source naturelle, mais cet endpoint ignore tous ses filtres (cf.
    communes_hubeau) et coûterait un balayage national.
    """
    params = {"code_commune": insee, "fields": "date_prelevement,reseaux"}
    if depuis:
        params["date_min_prelevement"] = f"{depuis}-01-01"
    vus = {}
    for data in _pages(BASE, params):
        for row in data:
            for r in (row.get("reseaux") or []):
                if isinstance(r, dict) and r.get("code"):
                    vus.setdefault(str(r["code"]), r.get("nom"))
        if vus:
            break  # la première page suffit : elle porte les prélèvements récents
    return vus


def inventaire_prelevements_reseau(code_reseau, depuis=None):
    """Comme inventaire_prelevements, mais à l'échelle d'un réseau de
    distribution. `code_reseau` EST un filtre valide de l'API (vérifié)."""
    params = {"code_reseau": code_reseau,
              "fields": CHAMPS_INVENTAIRE + ",code_commune,nom_commune"}
    if depuis:
        params["date_min_prelevement"] = f"{depuis}-01-01"
    inv = {}
    for data in _pages(BASE, params):
        for row in data:
            cp = row.get("code_prelevement")
            if not cp:
                continue
            e = inv.get(cp)
            if e is None:
                inv[cp] = {
                    "code_prelevement": cp,
                    "date": str(row.get("date_prelevement") or "")[:10],
                    "code_installation_amont": row.get("code_installation_amont"),
                    "nom_installation_amont": row.get("nom_installation_amont"),
                    "code_commune": row.get("code_commune"),
                    "nom_commune": row.get("nom_commune"),
                    "nb_lignes": 1,
                }
            else:
                e["nb_lignes"] += 1
    return inv


def bulletin_du_reseau(code_reseau, depuis=None):
    """
    Dernier bulletin complet du réseau, où qu'il ait été prélevé.

    Sert de repli pour une commune qui n'a aucun bulletin complet propre :
    c'est la même eau, prélevée dans une commune voisine du même réseau.
    Retourne (rows, code_commune_prelevement, nom_commune_prelevement) ou None.
    La commune de prélèvement DOIT être affichée dans toute sortie : sans elle,
    la fiche laisserait croire que l'analyse a eu lieu sur place.
    """
    inv = inventaire_prelevements_reseau(code_reseau, depuis=depuis)
    retenus = selectionner_bulletins(inv)
    if not retenus:
        return None
    e = max(retenus, key=lambda x: x["date"])
    rows = fetch_bulletin(e["code_commune"], e["code_prelevement"], e["date"])
    if not rows:
        return None
    return rows, e["code_commune"], e.get("nom_commune")


def derniers_bulletins_complets(insee, depuis=None, tous=False):
    """
    code_prelevement -> lignes complètes, pour chaque point d'eau de la commune.

    C'est la fonction d'entrée du projet : « donne-moi la dernière analyse
    complète de cette commune, et s'il y a trois points d'eau, les trois ».
    """
    inv = inventaire_prelevements(insee, depuis=depuis)
    out = {}
    for e in selectionner_bulletins(inv, tous=tous):
        rows = fetch_bulletin(insee, e["code_prelevement"], e["date"])
        if rows:
            out[e["code_prelevement"]] = rows
        time.sleep(PAUSE)
    return out


# ---------------------------------------------------------------------------
# 3. Métadonnées d'un bulletin
# ---------------------------------------------------------------------------
def bulletin_meta(insee, nom, dept, rows):
    """Lignes d'un prélèvement -> la ligne de la table `prelevements`."""
    r0 = rows[0] if rows else {}
    date = str(r0.get("date_prelevement") or "")[:10]
    reseaux = r0.get("reseaux") or []
    if isinstance(reseaux, list):
        noms_reseaux = "|".join(
            f"{r.get('nom')}" + (f" ({r['debit']})" if r.get("debit") else "")
            for r in reseaux if isinstance(r, dict) and r.get("nom")
        )
        codes_reseaux = "|".join(
            str(r.get("code")) for r in reseaux if isinstance(r, dict) and r.get("code")
        )
    else:
        noms_reseaux, codes_reseaux = str(reseaux), None

    return {
        "code_prelevement": str(r0.get("code_prelevement") or ""),
        "code_insee": insee,
        "nom": nom or r0.get("nom_commune"),
        "code_departement": dept or r0.get("code_departement"),
        "code_installation_amont": r0.get("code_installation_amont"),
        "nom_installation_amont": r0.get("nom_installation_amont"),
        "nom_distributeur": r0.get("nom_distributeur"),
        "nom_uge": r0.get("nom_uge"),
        "codes_reseaux": codes_reseaux or None,
        "noms_reseaux": noms_reseaux or None,
        "code_lieu_analyse": r0.get("code_lieu_analyse"),
        "date_prelevement": date,
        "conclusion_conformite": r0.get("conclusion_conformite_prelevement"),
        "conf_limites_bact": r0.get("conformite_limites_bact_prelevement"),
        "conf_limites_pc": r0.get("conformite_limites_pc_prelevement"),
        "conf_references_pc": r0.get("conformite_references_pc_prelevement"),
        "source_url": f"{BASE}?code_commune={insee}"
                      f"&date_min_prelevement={date}&size=5000",
    }

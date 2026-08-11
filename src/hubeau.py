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

3. **`sort` est honoré, et l'ordre par défaut est déjà décroissant.**
   Vérifié le 11 août 2026 sur le réseau `069000069` : sans tri et avec
   `sort=desc` la première page commence au 2026-05-29, avec `sort=asc` au
   2016-01-04. **On demande `desc` explicitement quand même** — un ordre par
   défaut non documenté peut changer sans préavis, et toute la logique
   d'arrêt anticipé en dépend.

   C'est ce fait qui débloque le 69. Le réseau CENTRE (Métropole de Lyon)
   porte **492 871 lignes, soit 99 pages**, et le coût d'une page croît avec
   la profondeur (5,6 s en page 1, 11,0 s en page 25). L'inventaire complet
   d'un tel réseau demande de l'ordre de la demi-heure — pendant laquelle le
   code d'avant n'imprimait pas une ligne. Trois soirées d'hypothèses fausses
   ont été dépensées à chercher un gel qui n'existait pas : le collecteur
   travaillait, et le superviseur le tuait toutes les dix minutes.
   Diagnostic complet : `docs/DIAGNOSTIC_69063_2026-08-11.md`.

Étiquette (CLAUDE.md §3.2) : pagination maximale, pause entre appels,
retentative exponentielle, User-Agent identifiant le projet. **Et ne pas
parcourir 493 000 lignes pour en retenir 399** — c'est la même règle.
"""
import collections
import datetime
import json
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

# Trois délais, et non un seul — parce qu'un `timeout=90` scalaire ne borne PAS
# la durée d'un appel
# ---------------------------------------------------------------------------
# Le `timeout` de `requests` est un délai d'INACTIVITÉ : il se déclenche quand
# rien n'arrive pendant N secondes, et il se réarme à chaque paquet reçu. Un
# serveur qui envoie un octet toutes les 80 secondes ne le déclenche jamais, et
# l'appel dure indéfiniment sans qu'aucune exception ne soit levée — donc sans
# que la retentative de `_get` puisse jouer, puisqu'elle attend une exception.
#
# C'est le défaut relevé au §14.7 de `docs/REPRISE.md`. Il n'était PAS la cause
# du blocage du 69 (celui-là était une pagination de 99 pages, cf. l'en-tête du
# module), mais il reste réel : il n'a simplement jamais été atteint.
#
# `TOTAL` est la borne dure, mesurée du début de la requête à la dernière
# donnée reçue. Elle est large — les pages les plus lourdes observées coûtent
# 5 à 11 s, et ~28 s en pagination profonde — pour ne jamais couper un appel
# sain ; elle sert à transformer un appel qui ne revient pas en une exception
# qui, elle, se retente.
TIMEOUT_CONNEXION = 10   # établir la connexion TCP/TLS
TIMEOUT_INACTIVITE = 90  # entre deux paquets
TIMEOUT_TOTAL = 300      # durée maximale d'un appel, toutes phases comprises
MORCEAU = 65536          # taille de lecture du corps

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
def _corps(r, debut):
    """
    Lit le corps de la réponse sans jamais dépasser `TIMEOUT_TOTAL`.

    On lit en flux et on vérifie l'horloge entre deux morceaux : c'est le seul
    moyen de borner la durée réelle d'un appel, l'horloge de `requests` étant
    remise à zéro par chaque paquet reçu. `iter_content` décompresse au passage
    (gzip/deflate), et `json.loads` reconnaît l'encodage d'un JSON en octets.
    """
    morceaux = []
    for morceau in r.iter_content(chunk_size=MORCEAU):
        morceaux.append(morceau)
        ecoule = time.time() - debut
        if ecoule > TIMEOUT_TOTAL:
            r.close()
            raise requests.Timeout(
                f"durée totale dépassée : {ecoule:.0f}s > {TIMEOUT_TOTAL}s "
                f"({sum(len(m) for m in morceaux)} octets reçus)")
    return json.loads(b"".join(morceaux) or b"{}")


def _get(url, params):
    """
    GET avec retentative exponentielle. Respecte Retry-After sur 429.

    Trois délais, pas un : connexion, inactivité, et **durée totale** — voir le
    bloc de constantes en tête de module pour la raison, qui n'est pas évidente.
    """
    attente = 2.0
    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            debut = time.time()
            r = SESSION.get(url, params=params, stream=True,
                            timeout=(TIMEOUT_CONNEXION, TIMEOUT_INACTIVITE))
            # `stream=True` laisse la connexion ouverte tant que le corps n'est
            # pas lu : sur les chemins où l'on repart sans le lire, il faut la
            # rendre explicitement, sinon le pool de la session se vide.
            if r.status_code == 429:
                delai = float(r.headers.get("Retry-After", attente))
                r.close()
                print(f"    429 — pause {delai:.0f}s")
                time.sleep(delai)
                attente *= 2
                continue
            if r.status_code in (500, 502, 503, 504):
                r.close()
                print(f"    {r.status_code} — nouvelle tentative dans {attente:.0f}s")
                time.sleep(attente)
                attente *= 2
                continue
            try:
                r.raise_for_status()
            except Exception:
                r.close()
                raise
            return _corps(r, debut)
        except (requests.Timeout, requests.ConnectionError) as e:
            if tentative == MAX_TENTATIVES:
                raise
            print(f"    {type(e).__name__} — nouvelle tentative dans {attente:.0f}s")
            time.sleep(attente)
            attente *= 2
    raise RuntimeError(f"échec après {MAX_TENTATIVES} tentatives : {url}")


def _pages(url, params, tri=None):
    """
    Itère sur les pages d'un endpoint Hub'Eau.

    **Cette fonction imprime.** Ce n'est pas du confort : sa version muette a
    coûté une soirée entière de diagnostic le 10 août 2026 (cf. le fait n° 3 de
    l'en-tête). Une pagination de 99 pages était indiscernable d'un processus
    gelé, et les trois hypothèses successives portaient toutes sur une panne
    qui n'existait pas. Un `print` par page rend la différence évidente au
    premier coup d'œil ; l'annonce du volume dès la page 1 la rend évidente
    *avant* d'attendre.

    `tri` — `"desc"` ou `"asc"`. Passé tel quel à l'API, qui l'honore.
    """
    p = dict(params, size=PAGE)
    if tri:
        p["sort"] = tri
    page, lus, t0 = 1, 0, time.time()
    while True:
        j = _get(url, dict(p, page=page))
        data = j.get("data", []) or []
        lus += len(data)
        total = j.get("count")
        if page == 1:
            if isinstance(total, int) and total > PAGE:
                print(f"    {total} lignes à parcourir, "
                      f"{-(-total // PAGE)} pages de {PAGE}")
        else:
            print(f"    page {page} — {lus} lignes lues"
                  + (f" sur {total}" if isinstance(total, int) else "")
                  + f", {time.time() - t0:.0f}s")
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


def communes_departement(dept):
    """
    Toutes les communes du département, **avec leurs centroïdes**, en UN appel.

    `communes_geo` ne demande que `code,nom` : à l'échelle du département, il
    fallait ensuite un `commune_par_insee` par commune pour obtenir lon/lat et
    les codes postaux — soit ~315 appels supplémentaires pour le Tarn, alors que
    l'API sait tout rendre d'un coup. Or `couverture_communes` porte les
    coordonnées, et **c'est ce que colorie la carte** (§8bis, obligation 4) :
    sans elles, une commune non documentée n'a nulle part où s'afficher.

    Retourne {code_insee: {code_insee, nom, population, lon, lat, codes_postaux}}.
    """
    j = _get(GEO.format(dept=dept),
             {"fields": "code,nom,codesPostaux,population,centre"})
    out = {}
    for c in j or []:
        centre = (c.get("centre") or {}).get("coordinates") or [None, None]
        out[c["code"]] = {
            "code_insee": c["code"],
            "nom": c.get("nom"),
            "population": c.get("population"),
            "lon": centre[0],
            "lat": centre[1],
            "codes_postaux": "|".join(c.get("codesPostaux") or []) or None,
        }
    return out


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
def fetch_bulletin(code_prelevement):
    """
    Toutes les lignes d'UN prélèvement, et de lui seul.

    **`code_prelevement` EST un filtre valide de l'API** — vérifié le 8 août
    2026 : `count` revient exactement égal au nombre de paramètres du bulletin,
    la réponse ne contient qu'un seul prélèvement, et l'appel coûte 0,1 s. C'est
    la voie la plus directe, et celle qui pèse le moins sur le service.

    Ce que faisait la version précédente, et pourquoi elle a été remplacée : on
    demandait toute la commune sur une fenêtre de deux jours, puis on écartait
    côté client ce qui n'était pas le bon prélèvement — une commune peut en
    porter plusieurs le même jour, sur des points différents, et les fusionner
    produirait un faux bulletin (§2.3). C'était juste, mais cela rapatriait des
    lignes pour les jeter, et à l'échelle d'un département cela se paie.

    Le savoir qui justifiait ce détour reste vrai et reste utile ailleurs :
    `date_max_prelevement` est comparé à un horodatage, donc **borner au jour
    même renvoie zéro ligne** ; il faut borner à J+1 (cf. l'en-tête du module).
    """
    rows = []
    for data in _pages(BASE, {"code_prelevement": code_prelevement}):
        rows += data
    # Garde-fou : si l'API cessait un jour d'honorer ce filtre — c'est
    # exactement ce que fait `communes_udi` — on ingérerait le contenu d'autres
    # prélèvements sans rien voir. Le contrôle coûte une comparaison.
    etrangeres = [r for r in rows
                  if str(r.get("code_prelevement")) != str(code_prelevement)]
    if etrangeres:
        raise RuntimeError(
            f"filtre code_prelevement non honoré : {len(etrangeres)} ligne(s) "
            f"étrangères sur {len(rows)} pour {code_prelevement}")
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


# Inventaires de réseau déjà faits pendant CE run — voir la docstring ci-dessous.
_INVENTAIRES_RESEAU = {}


def vider_cache_reseaux():
    """Oublie les inventaires de réseau mémorisés. Pour les tests."""
    _INVENTAIRES_RESEAU.clear()


def inventaire_prelevements_reseau(code_reseau, depuis=None,
                                   arret_au_premier_complet=True,
                                   seuil=SEUIL_COMPLET, memo=True):
    """
    Comme inventaire_prelevements, mais à l'échelle d'un réseau de
    distribution. `code_reseau` EST un filtre valide de l'API (vérifié).

    **Le résultat est PARTIEL par défaut, et c'est voulu.**
    ------------------------------------------------------
    Avec `arret_au_premier_complet`, on parcourt du plus récent vers le plus
    ancien et on s'arrête dès que le dernier bulletin complet est acquis. Sur
    le réseau CENTRE de la Métropole de Lyon cela ramène 99 pages à une ou
    deux : le bulletin retenu date du 2026-05-29, les 97 pages suivantes
    remontaient jusqu'en 2016 pour être jetées.

    **La règle du projet n'en est pas touchée.** Les deux seuls appelants —
    `bulletin_du_reseau` ici et `collecte._bulletin_du_reseau` — prennent
    `max(retenus, key=date)`, c'est-à-dire le plus récent et lui seul. On ne
    rétrécit donc pas le corpus, on cherche dans le bon sens. Un appelant qui
    aurait besoin de l'historique entier du réseau doit passer
    `arret_au_premier_complet=False` **et le dire**, sans quoi il travaillerait
    sur une fenêtre récente en croyant tenir tout.

    La condition d'arrêt n'est pas « j'ai vu un bulletin complet » mais **« j'ai
    vu un bulletin complet dont la date est strictement plus récente que la
    dernière date de la page »**. C'est ce qui protège du piège n° 1 de
    l'en-tête du module : un prélèvement chevauche les pages, et s'arrêter en
    fin de page le compterait à moitié. Tant qu'on est encore sur sa date, il
    peut avoir des lignes plus loin.

    Mémoïsation (`memo`) : à l'échelle du département, un même réseau est
    interrogé par toutes les communes qu'il dessert. `collecte._bulletin_du_reseau`
    mettait déjà le *bulletin* au cache disque, mais pas l'*inventaire* qui le
    précède — les quatre réseaux de la Métropole auraient donc été réinventoriés
    une fois par commune. C'est autant une question d'étiquette (§3.2) que de
    durée. La mémoire ne vit que le temps du processus : rien à invalider, une
    collecte relancée repart d'un inventaire frais.
    """
    cle = (str(code_reseau), depuis, bool(arret_au_premier_complet), seuil)
    if memo and cle in _INVENTAIRES_RESEAU:
        inv = _INVENTAIRES_RESEAU[cle]
        print(f"    inventaire du réseau {code_reseau} déjà fait "
              f"({len(inv)} prélèvements) — aucun appel")
        return inv

    params = {"code_reseau": code_reseau,
              "fields": CHAMPS_INVENTAIRE + ",code_commune,nom_commune"}
    if depuis:
        params["date_min_prelevement"] = f"{depuis}-01-01"
    inv = {}
    for data in _pages(BASE, params, tri="desc"):
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

        if not arret_au_premier_complet:
            continue
        # Les dates vides sont écartées du calcul : `min()` les prendrait pour
        # les plus anciennes et rendrait la comparaison ci-dessous vraie pour
        # n'importe quoi, donc l'arrêt prématuré sur un bulletin tronqué.
        dates = [str(r.get("date_prelevement") or "")[:10] for r in data]
        dates = [d for d in dates if d]
        if not dates:
            continue
        derniere = min(dates)
        acquis = [e for e in inv.values()
                  if e["nb_lignes"] > seuil and e["date"] > derniere]
        if acquis:
            e = max(acquis, key=lambda x: x["date"])
            print(f"    dernier bulletin complet du réseau acquis "
                  f"({e['date']}, {e['nb_lignes']} lignes) — "
                  f"pagination arrêtée, l'antérieur n'est pas demandé")
            break

    if memo:
        _INVENTAIRES_RESEAU[cle] = inv
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
    rows = fetch_bulletin(e["code_prelevement"])
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
        rows = fetch_bulletin(e["code_prelevement"])
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

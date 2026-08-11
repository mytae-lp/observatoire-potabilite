# -*- coding: utf-8 -*-
"""
La règle de couverture, écrite UNE fois — et le passage par le cache brut.

Ce module n'existe que pour supprimer une duplication qui allait devenir
coûteuse. Le dépôt portait **deux chemins de collecte qui ne faisaient pas la
même chose** :

| | `observer.py` | `fetch_departement.py` |
|---|---|---|
| repli sur le réseau | oui | **non** |
| écrit `couverture_communes` | oui | **non** |
| fige | oui | **non** |
| journal de reprise | **non** | oui |

Autrement dit, le script « prêt pour le département » aurait rempli
`prelevements` et `mesures` sans produire une seule ligne figée ni une seule
commune sur la carte — donc aucune page publiable, et pas de « non documentée »
alors que c'est précisément ce qu'un département entier devait enfin montrer.

C'est la leçon du chantier C8 rencontrée une deuxième fois : une règle recopiée
à deux endroits diverge à la première évolution, et personne ne le voit. Les
deux points d'entrée gardent donc ce qui leur est propre — `observer.py` résout
un code postal et restitue, `fetch_departement.py` énumère et journalise — mais
**la règle de couverture et le rapatriement vivent ici, et nulle part ailleurs.**

La règle de couverture (arrêtée le 7 août 2026)
-----------------------------------------------
1. bulletin complet propre à la commune                       -> `analysee`
2. sinon, bulletin complet du même réseau prélevé dans une
   commune voisine, la commune de prélèvement étant affichée  -> `rattachee_reseau`
3. sinon                                                      -> `non_documentee`

« Non documentée » n'est ni conforme ni non conforme : c'est une absence de
donnée, et elle doit rester visible comme telle (§2.4, §8bis obligation 4).

Collecter et ingérer sont deux gestes, et `con=None` les sépare
----------------------------------------------------------------
`traiter_commune(con=None, ...)` fait tout le travail réseau — inventaire,
règle de couverture, repli, écriture au cache brut — et **n'ouvre pas la
base**. C'est ce que `src/moisson.py` appelle pour moissonner plusieurs
départements en parallèle pendant que la base reste libre ; l'ingestion vient
ensuite, hors ligne, par `src/ingerer.py`.

Le mode sans base ne duplique pas la règle : c'est la même fonction, le même
ordre d'essais, le même statut rendu. Une deuxième version « allégée » de la
règle de couverture divergerait à la première retouche — c'est exactement la
duplication que ce module a été écrit pour supprimer.
"""
import collections
import threading

import brut
import hubeau
import ingest
from common import SEUIL_COMPLET
from console import dire

# Ce que la collecte a coûté, pour le rapport de fin de lot. Le cache n'est pas
# une optimisation discrète : savoir combien de bulletins n'ont PAS été demandés
# à Hub'Eau est la mesure de ce qu'on lui épargne (§3.2).
#
# Le verrou n'est pas du zèle : `Counter[k] += 1` est une lecture puis une
# écriture, et sous quatre fils de moisson deux incréments simultanés en
# perdent un. Un compteur faux ferait sous-estimer ce qu'on demande à un
# service public gratuit, ce qui est précisément le chiffre à ne pas fausser.
STATS = collections.Counter()
_VERROU_STATS = threading.Lock()


def compter(cle, n=1):
    with _VERROU_STATS:
        STATS[cle] += n


def reinitialiser_stats():
    with _VERROU_STATS:
        STATS.clear()


def rows_du_bulletin(code_prelevement, dept, cache=True):
    """
    Les lignes brutes d'un prélèvement — du cache si elles y sont, du réseau
    sinon, et dans ce cas écrites au cache avant d'être rendues.

    L'ordre compte : on écrit AVANT d'ingérer. Si l'ingestion échoue sur un cas
    non prévu, la matière première est déjà sauvée et la reprise ne repasse pas
    par le réseau — c'est tout l'objet de `brut.py`.
    """
    if cache:
        rows = brut.lire(dept, code_prelevement)
        if rows:
            compter("bulletins_du_cache")
            return rows, "cache"

    rows = hubeau.fetch_bulletin(code_prelevement)
    compter("bulletins_du_reseau")
    if rows and cache:
        brut.ecrire(dept, code_prelevement, rows)
    return rows, "reseau"


def _ingerer(con, insee, commune, rows, dept):
    """
    Métadonnées du bulletin, et son entrée en base **si une base est ouverte**.

    `con=None` est le mode moisson : la matière première est déjà au cache
    brut (`rows_du_bulletin` l'y a écrite), et l'ingestion se fera plus tard,
    hors ligne. On rend alors la même identité — code, nombre de paramètres,
    complétude — calculée par `ingest.identifier`, c'est-à-dire par le même
    code que l'ingestion réelle : la trace de moisson ne peut donc pas
    annoncer un nombre de paramètres différent de celui qui entrera en base.
    """
    meta = hubeau.bulletin_meta(insee, commune.get("nom"), dept, rows)
    meta.update({"codes_postaux": commune.get("codes_postaux"),
                 "lon": commune.get("lon"), "lat": commune.get("lat")})
    if con is None:
        return meta, ingest.identifier(meta, rows)
    return meta, ingest.ingest_bulletin(con, meta, rows)


def traiter_commune(con, commune, depuis=None, tous=False, repli=True,
                    cache=True, verbeux=True):
    """
    Collecte, ingère, et renvoie (statut, [code_prelevement], commune_prelevement).

    `commune` est un dictionnaire {code_insee, nom, lon, lat, codes_postaux} :
    les coordonnées viennent de l'énumération, elles ne sont pas redemandées ici.

    `con=None` — **moisson seule** : tout le réseau est fait, les bulletins
    sont écrits au cache brut, rien n'est écrit en base. Le triplet rendu est
    identique, donc le journal de reprise l'est aussi, et l'ingestion
    ultérieure n'a besoin d'aucun appel réseau.
    """
    insee = commune["code_insee"]
    dept = commune.get("dept") or insee[:2]
    inventaire = hubeau.inventaire_prelevements(insee, depuis=depuis)
    retenus = hubeau.selectionner_bulletins(inventaire, tous=tous)

    codes = []
    for e in retenus:
        rows, provenance = rows_du_bulletin(e["code_prelevement"], dept, cache=cache)
        if not rows:
            continue
        meta, (code_prel, nb, _complet) = _ingerer(con, insee, commune, rows, dept)
        codes.append(code_prel)
        if verbeux:
            marque = "" if provenance == "reseau" else "  [cache]"
            dire(f"  {meta['date_prelevement']}  "
                  f"{meta.get('nom_installation_amont') or 'installation non renseignée'}"
                  f"  — {nb} paramètres{marque}")

    if codes:
        compter("analysee")
        return "analysee", codes, None

    if not repli:
        compter("non_documentee")
        return "non_documentee", [], None

    # Repli : la même eau, prélevée ailleurs sur le même réseau.
    #
    # Le prélèvement est ingéré sous la commune où il a RÉELLEMENT eu lieu.
    # L'attacher à la commune étudiée serait faux, et ferait se disputer la même
    # clé par deux communes dès que la voisine serait analysée à son tour. Le
    # rattachement vit dans `couverture_communes`, pas dans le fait.
    reseaux = hubeau.reseaux_de_la_commune(insee, depuis=depuis)
    for code_reseau, nom_reseau in reseaux.items():
        trouve = _bulletin_du_reseau(code_reseau, depuis=depuis, cache=cache)
        if not trouve:
            continue
        rows, insee_prel, _nom_prel = trouve
        commune_prel = hubeau.commune_par_insee(insee_prel)
        meta, (code_prel, nb, _complet) = _ingerer(
            con, insee_prel, commune_prel, rows, insee_prel[:2])
        libelle = commune_prel.get("nom") or insee_prel
        if verbeux:
            dire(f"  {meta['date_prelevement']}  réseau {nom_reseau or code_reseau}"
                  f"  — {nb} paramètres, prélevé à {libelle}")
        compter("rattachee_reseau")
        return "rattachee_reseau", [code_prel], libelle

    if verbeux:
        dire(f"  aucun bulletin complet (> {SEUIL_COMPLET} paramètres), "
              f"ni pour la commune ni pour son réseau")
    compter("non_documentee")
    return "non_documentee", [], None


def _bulletin_du_reseau(code_reseau, depuis=None, cache=True):
    """
    Comme `hubeau.bulletin_du_reseau`, mais en passant par le cache brut.

    Recopié plutôt qu'appelé pour une seule raison : la version de `hubeau` va
    droit au réseau, et à l'échelle du département un même réseau est interrogé
    par toutes les communes qu'il dessert. Sans cache, le même bulletin serait
    redemandé autant de fois — huit pour le Moulin Galat.
    """
    inv = hubeau.inventaire_prelevements_reseau(code_reseau, depuis=depuis)
    retenus = hubeau.selectionner_bulletins(inv)
    if not retenus:
        return None
    e = max(retenus, key=lambda x: x["date"])
    dept = str(e.get("code_commune") or "")[:2] or None
    rows, _provenance = rows_du_bulletin(e["code_prelevement"], dept, cache=cache)
    if not rows:
        return None
    return rows, e["code_commune"], e.get("nom_commune")

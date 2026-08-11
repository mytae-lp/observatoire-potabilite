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

4. **Plusieurs fils peuvent moissonner en même temps, à une condition : que
   l'étiquette soit tenue GLOBALEMENT et non par appelant.** Les pauses
   `PAUSE` / `PAUSE_COMMUNE` sont locales à un fil : quatre fils qui les
   respectent chacun quadruplent le débit vu par Hub'Eau, et le §3.2 est
   violé sans que rien ne le dise. D'où le `REGULATEUR` ci-dessous, qui borne
   le débit **du processus entier** — nombre d'appels en vol et appels par
   seconde — et qui met **tous** les fils en retenue quand l'un d'eux reçoit
   un 429. En mono-fil il ne change rien à ce qui existait.

Étiquette (CLAUDE.md §3.2) : pagination maximale, pause entre appels,
retentative exponentielle, User-Agent identifiant le projet. **Et ne pas
parcourir 493 000 lignes pour en retenir 399** — c'est la même règle.
"""
import collections
import contextlib
import datetime
import json
import threading
import time

import requests

from common import SEUIL_COMPLET, USER_AGENT
from console import dire

BASE = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis"
BASE_UDI = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/communes_udi"
GEO = "https://geo.api.gouv.fr/departements/{dept}/communes"
GEO_COMMUNES = "https://geo.api.gouv.fr/communes"

# Taille de page. **`5000` n'est PAS le maximum**, contrairement à ce que ce
# fichier et le §3.2 de CLAUDE.md ont affirmé jusqu'au 11 août 2026.
#
# La documentation de l'API Qualité de l'eau potable dit, pour `resultats_dis` :
# « taille de page par défaut : 5000, taille max de la page : 20000 ». Vérifié
# en appelant l'API le 11 août 2026 : `size=20000` renvoie bien 20 000 lignes.
# Le dépôt écrivait « size=5000 (maximum accepté) » — une valeur supposée, prise
# pour vérifiée, et qui nous faisait demander **quatre fois plus de requêtes que
# nécessaire** pour la même donnée. C'est le §2.7 pris en défaut chez nous, et
# sur un sujet où il coûte : notre propre règle de politesse dit « pagination
# maximale », et nous ne la respections pas.
#
# PAGE_MAX n'est pas encore le défaut : le passer à 20 000 change le
# comportement de collecte et doit être mesuré, pas décrété. Ce qu'on sait au
# 11 août 2026 : une page de 20 000 coûte 20 à 31 s contre 5 à 11 s pour 5 000,
# soit un débit de lignes comparable — le gain n'est donc pas la vitesse, c'est
# de diviser par quatre le NOMBRE d'appels demandés au service, et de rendre
# les inventaires profonds (99 pages sur le réseau CENTRE de Lyon) quatre fois
# moins coûteux en requêtes.
PAGE = 5000
PAGE_MAX = 20000     # documenté ET vérifié le 11 août 2026

# Profondeur de pagination — la contrainte documentée qui n'est PAS appliquée
# -------------------------------------------------------------------------
# La documentation annonce : « la profondeur d'accès aux résultats (numéro de
# la page * nombre maximum de résultats dans une page) est limitée à 20 000
# enregistrements ». Si elle était appliquée, toute pagination au-delà de la
# page 4 (à size=5000) reviendrait vide — et `_pages` s'arrêterait là **sans
# erreur**, donc un inventaire tronqué en silence, donc des bulletins qui
# disparaissent de l'analyse (§2.3, le pire cas de ce module).
#
# Vérifié le 11 août 2026 : elle ne l'est pas. Pages pleines obtenues jusqu'à
# une profondeur de 450 000 (page 90 à size=5000), ce qui est cohérent avec les
# 99 pages réellement parcourues sur le Rhône. **Mais c'est une observation, pas
# une garantie** : le jour où elle serait appliquée, rien dans le code ne le
# signalerait. D'où le contrôle de fin de pagination dans `_pages`.
PROFONDEUR_DOCUMENTEE = 20000

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


class PaginationTronquee(RuntimeError):
    """
    L'API a cessé de servir avant d'avoir rendu le nombre de lignes annoncé.

    Une classe propre et non un `RuntimeError` nu, pour que l'appelant puisse
    la distinguer d'une panne réseau : celle-ci ne se retente pas à l'identique,
    elle demande de réduire la fenêtre de requête.
    """


# ---------------------------------------------------------------------------
# Régulateur de débit — l'étiquette du §3.2 tenue à l'échelle du processus
#
# Ce plafond est **le nôtre**, et la documentation a été lue avant de l'écrire.
#
# Vérifié le 11 août 2026 sur hubeau.eaufrance.fr — pages « APIs », « API
# Qualité de l'eau potable », « FAQ » et « À propos » : **aucune limite de
# débit, aucun quota d'appels, aucune règle de fréquence n'est publiée.** Les
# seules contraintes documentées sont structurelles : taille de page, longueur
# d'URL, profondeur de pagination (cf. PAGE ci-dessous).
#
# Ce que la page « À propos » annonce est un ENGAGEMENT DE SERVICE et non une
# autorisation : « les APIs Hub'Eau garantissent les meilleures performances de
# rapidité et de disponibilité (réponse à plus de 20 requêtes par seconde) ».
# C'est ce que le service se dit capable de servir, pas ce qu'un réutilisateur
# a le droit de demander. Confondre les deux serait lire un dimensionnement
# comme une permission — la même erreur que lire une limite déclarée comme un
# seuil réglementaire (§2.8).
#
# En l'absence de règle publiée, le plafond reste une décision du projet. Il
# est réglé pour que N fils ensemble ne pèsent pas plus que ce qu'un seul fil
# pesait avant — les mesures de collecte donnent 16 à 35 s par commune,
# dominées par l'attente des réponses, pas par nos pauses. Mesure du 11 août
# 2026 : ~2 500 communes moissonnées, **zéro 429 reçu**. C'est la preuve que ce
# rythme est accepté, pas la preuve de ce qui serait toléré au-delà.
#
# Deux bornes, parce qu'une seule ne suffit pas :
#   · `simultanes` — combien d'appels sont en vol au même instant. C'est ce
#     qui borne la charge instantanée sur le service ;
#   · `par_seconde` — la cadence moyenne d'ouverture d'un appel. C'est ce qui
#     borne la charge quand les réponses deviennent rapides.
#
# Et une retenue commune : un 429 reçu par un fil arrête TOUS les fils. Sans
# cela, les trois autres continueraient de frapper une porte qui vient de se
# fermer, ce qui est exactement le comportement que le §3.2 interdit.
# ---------------------------------------------------------------------------
class Regulateur:
    """Débit réseau global, partagé par tous les fils du processus."""

    def __init__(self, par_seconde=3.0, simultanes=1):
        self._verrou = threading.Lock()
        self._places = threading.BoundedSemaphore(simultanes)
        self._simultanes = simultanes
        self._intervalle = 1.0 / float(par_seconde)
        self._prochain = 0.0
        self._retenue = 0.0   # instant avant lequel personne ne repart
        # Ce qu'on a réellement demandé au service, et ce que ça nous a coûté
        # d'attente. Le §3.2 dit de ne jamais se comporter comme une charge
        # abusive ; encore faut-il savoir quelle charge on est. Sans ce
        # compteur, on discute d'un plafond sans connaître le débit — et on
        # décide d'augmenter le parallélisme sans savoir s'il sert à quelque
        # chose. `attente_cumulee` répond à la seule question qui compte pour
        # cela : est-ce le plafond qui nous freine, ou le service ?
        self._appels = 0
        self._attente = 0.0
        self._depart = None

    def regler(self, par_seconde=None, simultanes=None):
        """
        Change les bornes. À n'appeler qu'AVANT de lancer les fils : le
        sémaphore est remplacé, et le remplacer sous des fils en vol ferait
        perdre le compte des places.
        """
        with self._verrou:
            if par_seconde:
                self._intervalle = 1.0 / float(par_seconde)
            if simultanes:
                self._simultanes = int(simultanes)
                self._places = threading.BoundedSemaphore(int(simultanes))

    def etat(self):
        return {"simultanes": self._simultanes,
                "par_seconde": round(1.0 / self._intervalle, 2)}

    def bilan(self):
        """
        Ce qu'on a demandé au service, et si le plafond nous a freinés.

        `debit_reel` est le nombre d'appels ouverts par seconde, mesuré du
        premier au dernier. `part_freinee` est la fraction du temps des fils
        passée à attendre le régulateur plutôt que le réseau : proche de 0,
        c'est Hub'Eau qui donne le rythme et augmenter le parallélisme sert ;
        proche de 1, c'est NOTRE plafond qui donne le rythme et ajouter des
        ouvriers ne fera qu'allonger la file d'attente.
        """
        with self._verrou:
            appels, attente, depart = self._appels, self._attente, self._depart
        if not appels or depart is None:
            return {"appels": appels, "debit_reel": 0.0, "part_freinee": 0.0,
                    "plafond": round(1.0 / self._intervalle, 2)}
        duree = max(1e-6, time.monotonic() - depart)
        return {
            "appels": appels,
            "duree_s": round(duree, 1),
            "debit_reel": round(appels / duree, 2),
            "plafond": round(1.0 / self._intervalle, 2),
            "attente_cumulee_s": round(attente, 1),
            "part_freinee": round(attente / (duree * self._simultanes), 3),
        }

    def retenir(self, secondes):
        """Met tous les fils en attente — appelé sur 429 ou sur 5xx répétés."""
        with self._verrou:
            self._retenue = max(self._retenue, time.monotonic() + float(secondes))

    @contextlib.contextmanager
    def jeton(self):
        """Occupe une place et respecte la cadence, le temps d'un appel."""
        with self._places:
            t0 = time.monotonic()
            while True:
                with self._verrou:
                    maintenant = time.monotonic()
                    cible = max(self._prochain, self._retenue, maintenant)
                    delai = cible - maintenant
                    if delai <= 0:
                        self._prochain = maintenant + self._intervalle
                        self._appels += 1
                        self._attente += maintenant - t0
                        if self._depart is None:
                            self._depart = t0
                        break
                    # On ne réserve pas encore le créneau : une retenue
                    # commune peut arriver pendant qu'on dort, et il faudra
                    # la relire.
                time.sleep(min(delai, 5.0))
            yield


REGULATEUR = Regulateur()


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

    L'appel se fait sous un jeton du `REGULATEUR`, et **les attentes se font
    hors du jeton** : un fil qui patiente après un 503 rend sa place aux
    autres au lieu de la garder immobilisée. Un 429 met en revanche tout le
    monde en retenue — c'est le service qui demande le silence, pas un
    incident propre à un fil.
    """
    attente = 2.0
    for tentative in range(1, MAX_TENTATIVES + 1):
        differe = None
        try:
            with REGULATEUR.jeton():
                debut = time.time()
                r = SESSION.get(url, params=params, stream=True,
                                timeout=(TIMEOUT_CONNEXION, TIMEOUT_INACTIVITE))
                # `stream=True` laisse la connexion ouverte tant que le corps
                # n'est pas lu : sur les chemins où l'on repart sans le lire,
                # il faut la rendre explicitement, sinon le pool de la session
                # se vide.
                if r.status_code == 429:
                    delai = float(r.headers.get("Retry-After", attente))
                    r.close()
                    REGULATEUR.retenir(delai)
                    differe = ("429", delai)
                elif r.status_code in (500, 502, 503, 504):
                    code = r.status_code
                    r.close()
                    differe = (str(code), attente)
                else:
                    try:
                        r.raise_for_status()
                    except Exception:
                        r.close()
                        raise
                    return _corps(r, debut)
        except (requests.Timeout, requests.ConnectionError) as e:
            if tentative == MAX_TENTATIVES:
                raise
            dire(f"    {type(e).__name__} — nouvelle tentative dans {attente:.0f}s")
            time.sleep(attente)
            attente *= 2
            continue

        libelle, delai = differe
        if libelle == "429":
            dire(f"    429 — pause {delai:.0f}s, tous les fils en retenue")
        else:
            dire(f"    {libelle} — nouvelle tentative dans {delai:.0f}s")
        time.sleep(delai)
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

    **Une pagination qui s'arrête avant son compte lève une exception.**
    -------------------------------------------------------------------
    L'API documente une profondeur d'accès limitée à 20 000 enregistrements.
    Vérifié le 11 août 2026, elle ne l'applique pas — des pages pleines
    reviennent jusqu'à une profondeur de 450 000. Mais si elle venait à
    l'appliquer, une page profonde reviendrait vide, cette boucle s'arrêterait
    sur `len(data) < PAGE` **sans aucune erreur**, et l'inventaire serait
    tronqué en silence : des bulletins complets invisibles, donc des communes
    déclarées « non documentées » à tort. C'est le pire cas de ce module,
    exactement le §2.4 transposé à la collecte — une absence de donnée qui
    n'est pas une absence de fait.

    Le contrôle est une comparaison : l'API annonce `count`, on compte ce qu'on
    a lu. Un écart signifie qu'on n'a pas eu ce qui existe, et il vaut mieux
    échouer bruyamment. L'échec est rattrapable : la commune part au journal en
    « erreur », et la reprise la retente au lieu de la tenir pour faite.

    L'arrêt VOLONTAIRE d'un appelant (`inventaire_prelevements_reseau` casse la
    boucle dès le dernier bulletin complet acquis) ne déclenche rien : le
    contrôle est dans le `return` de la boucle, pas dans le `yield`. Un appelant
    qui referme le générateur n'y passe jamais.
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
                dire(f"    {total} lignes à parcourir, "
                      f"{-(-total // PAGE)} pages de {PAGE}")
        else:
            dire(f"    page {page} — {lus} lignes lues"
                  + (f" sur {total}" if isinstance(total, int) else "")
                  + f", {time.time() - t0:.0f}s")
        yield data
        if len(data) < PAGE or not j.get("next"):
            if isinstance(total, int) and lus < total:
                raise PaginationTronquee(
                    f"pagination interrompue à {lus} lignes sur {total} annoncées "
                    f"(page {page}, size={PAGE}, profondeur {page * PAGE}) — "
                    f"l'API a cessé de servir avant la fin. Si la profondeur "
                    f"documentée ({PROFONDEUR_DOCUMENTEE}) est désormais "
                    f"appliquée, il faut réduire la fenêtre de requête, pas "
                    f"ingérer un inventaire amputé.")
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
            dire(f"communes  : {len(c)} rattachées à une UDI "
                  f"(Hub'Eau communes_udi, filtré côté client)")
            return c
        dire("communes  : communes_udi n'a rien renvoyé — repli geo.api.gouv.fr")
    c = communes_geo(dept)
    dire(f"communes  : {len(c)} communes du département (geo.api.gouv.fr)")
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
_VERROUS_RESEAU = {}
_VERROU_REGISTRE = threading.Lock()


def _verrou_du_reseau(cle):
    """
    Un verrou par réseau, créé à la demande.

    Sans lui, la mémoïsation ne protège rien en moissonnage parallèle : quatre
    fils qui prennent quatre communes du même réseau arrivent ensemble, ne
    trouvent rien en mémoire, et lancent **quatre fois** le même inventaire.
    Sur le réseau CENTRE de la Métropole de Lyon, c'est quatre paginations
    profondes au lieu d'une — le contraire exact de ce que la mémoïsation
    cherchait à éviter, et une charge inutile sur un service public gratuit.

    Le verrou est pris autour de l'inventaire entier : le deuxième fil attend
    le premier, puis trouve le résultat en mémoire et ne fait aucun appel.
    """
    with _VERROU_REGISTRE:
        v = _VERROUS_RESEAU.get(cle)
        if v is None:
            v = _VERROUS_RESEAU[cle] = threading.Lock()
        return v


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

    En moissonnage parallèle, la mémoïsation est prise sous un **verrou par
    réseau** (`_verrou_du_reseau`) : sans lui, quatre fils arrivés ensemble sur
    le même réseau ne trouveraient rien en mémoire et lanceraient quatre fois
    le même inventaire.
    """
    cle = (str(code_reseau), depuis, bool(arret_au_premier_complet), seuil)
    if not memo:
        return _inventorier_reseau(code_reseau, depuis,
                                   arret_au_premier_complet, seuil)
    with _verrou_du_reseau(cle):
        if cle in _INVENTAIRES_RESEAU:
            inv = _INVENTAIRES_RESEAU[cle]
            dire(f"    inventaire du réseau {code_reseau} déjà fait "
                 f"({len(inv)} prélèvements) — aucun appel")
            return inv
        inv = _inventorier_reseau(code_reseau, depuis,
                                  arret_au_premier_complet, seuil)
        _INVENTAIRES_RESEAU[cle] = inv
        return inv


def _inventorier_reseau(code_reseau, depuis, arret_au_premier_complet, seuil):
    """L'inventaire lui-même, sans mémoire — appelé sous verrou."""
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
            dire(f"    dernier bulletin complet du réseau acquis "
                  f"({e['date']}, {e['nb_lignes']} lignes) — "
                  f"pagination arrêtée, l'antérieur n'est pas demandé")
            break

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

# -*- coding: utf-8 -*-
"""
Écrire à l'écran depuis plusieurs fils sans que les lignes se mélangent.

Ce module existe pour une raison précise, et elle est documentée en tête de
`hubeau.py` : **la trace d'exécution est un instrument de diagnostic du
projet**, pas du confort. Une pagination de 99 pages muette a coûté trois
soirées d'hypothèses fausses sur le Rhône. Le jour où quatre départements
sont moissonnés en même temps, une trace non attribuée coûterait la même
chose — on lirait « page 12 — 60 000 lignes lues » sans savoir de quel
département il s'agit, ni si les quatre avancent ou si trois sont bloqués.

Deux garanties, et rien d'autre :

  · **une ligne est écrite d'un seul tenant** — `print` n'est pas atomique,
    deux fils qui écrivent en même temps produisent des lignes entrelacées ;
  · **chaque ligne porte l'étiquette de son fil** — posée une fois par le
    fil qui prend une commune en charge, elle suit tous les appels qu'il fait,
    y compris au fond de `hubeau._pages` qui ne sait pas qui l'appelle.

En exécution mono-fil (`observer.py`, `fetch_departement.py`), l'étiquette est
vide et `dire()` se comporte exactement comme `print()`.
"""
import sys
import threading

_local = threading.local()
_VERROU = threading.Lock()


def etiqueter(prefixe):
    """Pose l'étiquette du fil courant. `None` ou `""` la retire."""
    _local.prefixe = prefixe or ""


def etiquette():
    return getattr(_local, "prefixe", "")


def dire(*morceaux):
    """Comme `print`, mais atomique et étiqueté."""
    texte = " ".join(str(m) for m in morceaux)
    prefixe = etiquette()
    if prefixe:
        # Une trace multi-lignes garde son étiquette sur CHAQUE ligne : sinon
        # la deuxième ligne d'un message est orpheline dès qu'un autre fil
        # s'intercale entre les deux.
        texte = "\n".join(prefixe + l for l in texte.split("\n"))
    with _VERROU:
        print(texte, flush=True)


def dire_brut(texte=""):
    """Une ligne sans étiquette — titres, totaux, séparateurs de rapport."""
    with _VERROU:
        print(texte, flush=True)


def erreur(*morceaux):
    """Comme `dire`, mais sur la sortie d'erreur."""
    texte = " ".join(str(m) for m in morceaux)
    prefixe = etiquette()
    with _VERROU:
        print(prefixe + texte, file=sys.stderr, flush=True)

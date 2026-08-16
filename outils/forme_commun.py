# -*- coding: utf-8 -*-
"""
Le socle des quatre mesures de forme — §7 de `docs/CONSIGNE_IMPLEMENTATION_FORME.md`.

Pourquoi un module commun
-------------------------
Les quatre outils partagent trois choses : le choix des pages à mesurer, le
serveur qui les sert, et la façon de passer d'un thème à l'autre. Recopier ces
règles quatre fois garantirait qu'elles divergent à la première retouche — c'est
la leçon que le dépôt a déjà apprise deux fois, sur la règle de couverture
(`src/collecte.py`) et sur les contrôles de prose importés plutôt que dupliqués.

Ce que ces outils mesurent, et ce qu'ils ne mesurent pas
-------------------------------------------------------
Ils mesurent **le site construit**, pas le code qui le construit. Ils ouvrent des
pages, lisent ce que le navigateur en fait, et comparent à un attendu écrit dans
la charte. Ils ne disent rien de la justesse des chiffres affichés : c'est le
rôle de `tests/test_sorties.py`, et les deux ne se remplacent pas.

Ils ne servent pas non plus à décider de la forme. Une mesure qui échoue signale
qu'une décision de `docs/CHARTE_GRAPHIQUE.md` n'est plus appliquée ; elle ne dit
pas laquelle prendre à la place.

Le serveur
----------
Les pages sont servies par un `http.server` éphémère sur un port libre, jamais
ouvertes en `file://` : les chemins relatifs des feuilles et des polices, et le
comportement du cache, ne sont pas les mêmes, et on mesurerait alors autre chose
que ce que le public reçoit.

Installation
------------
    py -X utf8 -m pip install -r outils/requirements-forme.txt
    py -X utf8 -m playwright install chromium

Playwright n'est **pas** dans `requirements.txt` : le VPS moissonne, ingère et
publie, il n'a aucune raison de porter 150 Mo de binaires de navigateur. Ces
outils sont un instrument d'atelier.
"""
from __future__ import annotations

import contextlib
import functools
import http.server
import os
import socket
import socketserver
import sys
import threading

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(RACINE, "site", "public")

# Les sept crans de l'échelle typographique — décision D2 de la charte.
# Le plancher absolu est 13 px : en dessous, la mesure de lisibilité échoue
# avant celle du contraste.
CRANS = (13, 15, 17, 19, 23, 30, 40)

# Les deux thèmes. `data-theme` est posé sur <html> ; « auto » est mesuré par
# `prefers-color-scheme`, parce qu'un visiteur qui n'a rien choisi est le cas
# le plus fréquent et le seul où les deux mécanismes doivent s'accorder.
THEMES = ("clair", "sombre")

# Les largeurs de la mesure de débordement. 320 est le plus petit téléphone
# encore en service ; 2560 un écran de bureau large. Les valeurs entre les deux
# ne sont pas régulières : elles visent les points de rupture connus — 768,
# 1080 (le repli du menu, cf. §7 de la consigne), 1100 et 1440 (les largeurs de
# page de D6).
LARGEURS = (320, 360, 390, 414, 480, 600, 768, 834, 900, 1024, 1080, 1100,
            1280, 1440, 1920, 2560)


def pages_a_mesurer(public: str = PUBLIC, avec_exemples: bool = True):
    """
    Les pages sur lesquelles les mesures font foi.

    Une par **type** de page, pas une par adresse : le site produit des dizaines
    de milliers de fiches et de briefs, mais ils partagent leur gabarit. Mesurer
    un exemplaire de chaque type couvre les formes ; mesurer les 28 000 couvrirait
    les mêmes formes 28 000 fois.

    Les exemplaires sont choisis pour leurs **cas limites**, pas au hasard : une
    fiche non conforme porte des barres rouges et des étiquettes que la fiche
    conforme n'a pas, et c'est là que le contraste échoue.
    """
    fixes = ["index.html", "carte.html", "communes.html", "methode.html",
             "sources.html", "substances.html", "reclassements.html"]
    trouvees = [p for p in fixes if os.path.exists(os.path.join(public, p))]

    if avec_exemples:
        for dossier in ("departement", "commune", "substance"):
            chemin = os.path.join(public, dossier)
            if not os.path.isdir(chemin):
                continue
            noms = sorted(f for f in os.listdir(chemin) if f.endswith(".html"))
            if not noms:
                continue
            # Le premier et le dernier : deux exemplaires suffisent à révéler
            # une forme qui dépend du contenu, et le tri rend le choix
            # reproductible d'une exécution à l'autre.
            choix = {noms[0], noms[-1]}
            trouvees += [f"{dossier}/{n}" for n in sorted(choix)]

    return trouvees


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):  # le serveur ne commente pas ce qu'il sert
        pass


@contextlib.contextmanager
def servir(dossier: str = PUBLIC):
    """Sert `dossier` sur un port libre, le temps de la mesure."""
    if not os.path.isdir(dossier):
        raise SystemExit(
            f"dossier absent : {dossier}\n"
            "Construire le site d'abord, ou passer --dossier.")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    gestionnaire = functools.partial(_Silencieux, directory=dossier)
    serveur = socketserver.TCPServer(("127.0.0.1", port), gestionnaire)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        serveur.shutdown()
        serveur.server_close()


def navigateur():
    """Chromium, ou un message qui dit quoi installer plutôt qu'une trace."""
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        raise SystemExit(
            "Playwright n'est pas installé.\n"
            "  py -X utf8 -m pip install -r outils/requirements-forme.txt\n"
            "  py -X utf8 -m playwright install chromium")
    return sync_playwright()


def poser_theme(page, theme: str):
    """
    Le thème, posé comme un visiteur le poserait.

    `data-theme` sur <html> pour le choix explicite, et `prefers-color-scheme`
    pour que les règles de média s'accordent. Poser l'un sans l'autre laisserait
    une partie de la feuille dans l'autre thème, et la mesure porterait sur un
    état que personne ne voit.
    """
    page.emulate_media(color_scheme="dark" if theme == "sombre" else "light")
    page.evaluate("t => document.documentElement.setAttribute('data-theme', t)",
                  "sombre" if theme == "sombre" else "clair")


def entete(titre: str, dossier: str, pages: list[str]) -> None:
    print("=" * 74)
    print(titre)
    print("=" * 74)
    print(f"  dossier : {dossier}")
    print(f"  pages   : {len(pages)}")
    print()


def bilan(echecs: list, unite: str) -> int:
    """Le compte-rendu final, et le code de sortie qui va avec."""
    print()
    print("-" * 74)
    if not echecs:
        print(f"0 {unite} — la mesure passe.")
        return 0
    print(f"{len(echecs)} {unite} :")
    for e in echecs[:40]:
        print(f"   {e}")
    if len(echecs) > 40:
        print(f"   … et {len(echecs) - 40} autre(s). "
              "Le compte ci-dessus est le nombre réel, pas le nombre affiché.")
    return 1


def dossier_demande(argv) -> str:
    """--dossier, ou site/public par défaut."""
    if "--dossier" in argv:
        return os.path.abspath(argv[argv.index("--dossier") + 1])
    return PUBLIC


def pages_demandees(argv, public) -> list[str]:
    """--page peut être répété pour restreindre la mesure à une page."""
    demandees = [argv[i + 1] for i, a in enumerate(argv) if a == "--page"]
    return demandees or pages_a_mesurer(public)

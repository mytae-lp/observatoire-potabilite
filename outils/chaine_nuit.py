#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La chaîne longue, enchaînée sans surveillance : refiger, reconstruire,
contrôler, publier.

POURQUOI UNE CHAÎNE ET NON QUATRE COMMANDES
-------------------------------------------
Parce qu'un refigeage raté à deux heures du matin ne doit pas se faire
reconstruire, et surtout pas se faire publier. Chaque étape barre la suivante :
la seule issue d'un échec est l'arrêt, jamais la poursuite sur un résultat
douteux. C'est le §2.13 transposé à l'exploitation — un faux positif coûte plus
cher qu'un faux négatif, donc mieux vaut ne rien publier que publier faux.

L'ORDRE, ET SA RAISON
---------------------
1. **Contrôles préalables** — tout ce qui peut faire échouer la nuit est
   vérifié AVANT la première étape longue : la présence du tampon, la place
   disque, et les identifiants de publication s'il faut publier. Découvrir à
   4 h qu'il manque un mot de passe après deux heures de refigeage est le
   gâchis qu'on évite ici.
2. **Tests du moteur** — 21 s, et ils fabriquent leur propre base. Ils passent
   AVANT le refigeage : s'ils échouent, une règle de méthode a cessé de
   s'appliquer et il ne faut surtout pas figer.
3. **Ingestion + refigeage complet** — l'étape longue.
4. **Construction du site** — dérive du figé.
5. **Contrôles de sortie** — ils lisent les pages CONSTRUITES, donc après.
6. **Publication** — seulement si tout le reste est vert, et seulement si on
   l'a demandée.

USAGE

    py -X utf8 outils/chaine_nuit.py                    # sans publier
    py -X utf8 outils/chaine_nuit.py --publier          # et publier à la fin
    py -X utf8 outils/chaine_nuit.py --depuis build     # reprendre en cours

Le journal est écrit dans `data/journal/nuit-<horodatage>.log`, et tout ce qui
sort des sous-processus y va aussi — c'est ce qu'on lira au réveil.
"""

import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = [sys.executable, "-X", "utf8"]

ETAPES = [
    ("moteur", "Tests du moteur — avant de figer quoi que ce soit",
     [["tests/test_verdict.py"], ["tests/test_figer.py"]]),
    ("figer", "Ingestion du tampon puis refigeage COMPLET du corpus",
     [["src/ingerer.py", "--tous", "--refiger"]]),
    ("build", "Construction de la vitrine",
     [["site/build_site.py"]]),
    ("sorties", "Contrôles sur les pages construites",
     [["tests/test_sorties.py"]]),
]


def journaliser(fh, texte=""):
    horo = datetime.now().strftime("%H:%M:%S")
    ligne = f"[{horo}] {texte}" if texte else ""
    print(ligne, flush=True)
    fh.write(ligne + "\n")
    fh.flush()


def pic_memoire(popen):
    """Mémoire maximale atteinte par le processus, en Mo. `None` si indisponible.

    Sur Windows, le système tient lui-même le compteur (`PeakWorkingSetSize`) :
    on le lit à la fin plutôt que de sonder pendant l'exécution. Un sondage
    périodique raterait une pointe entre deux mesures, ce qui est précisément
    l'inverse de ce qu'on cherche — on veut le maximum, pas une moyenne.

    À quoi ça sert : dimensionner une machine distante sans le deviner. Une
    étape qui culmine à 3 Go et une qui culmine à 12 Go ne se louent pas au
    même prix.

    Ne doit JAMAIS faire échouer la chaîne : toute erreur rend `None`.

    Sur Linux, cette fonction n'est PAS utilisable : `ru_maxrss` de
    RUSAGE_CHILDREN donne le maximum cumulé de tous les fils déjà récoltés, pas
    celui du dernier — une étape légère après une lourde afficherait la pointe
    de la lourde. C'est `surveiller_memoire()` qui s'en charge là-bas, en lisant
    le compteur propre au processus pendant qu'il tourne.
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD),
                        ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]

        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        ok = ctypes.WinDLL("psapi").GetProcessMemoryInfo(
            wintypes.HANDLE(int(popen._handle)), ctypes.byref(pmc), pmc.cb)
        return pmc.PeakWorkingSetSize / 2**20 if ok else None
    except Exception:
        return None


def surveiller_memoire(pid, arret, releve):
    """Sur Linux : suit la pointe mémoire PROPRE à ce processus.

    `/proc/<pid>/status` expose `VmHWM`, le plus haut niveau atteint depuis le
    démarrage du processus. Il est monotone, donc la dernière lecture réussie
    avant la disparition du processus EST la pointe — pas besoin d'attraper le
    bon instant.

    On sonde quand même en boucle plutôt qu'une seule fois à la fin : le
    fichier disparaît avec le processus, et une lecture unique arriverait
    souvent trop tard.
    """
    while not arret.is_set():
        try:
            with open(f"/proc/{pid}/status") as fh:
                for ligne in fh:
                    if ligne.startswith("VmHWM:"):
                        releve[0] = max(releve[0], int(ligne.split()[1]) / 1024)
                        break
        except (OSError, ValueError):
            return          # le processus est parti : la dernière valeur tient
        arret.wait(2)


# Relevé par étape, pour le récapitulatif final : (nom, minutes, pic en Mo).
RELEVE = []


def lancer(fh, argv):
    """Un sous-processus, sa sortie recopiée au journal. Rend son code."""
    journaliser(fh, f"  $ {' '.join(argv)}")
    t0 = time.time()
    p = subprocess.Popen(PYTHON + argv, cwd=RACINE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True,
                         encoding="utf-8", errors="replace", bufsize=1)

    veilleur, arret, releve = None, threading.Event(), [0.0]
    if os.name != "nt":
        veilleur = threading.Thread(target=surveiller_memoire,
                                    args=(p.pid, arret, releve), daemon=True)
        veilleur.start()

    for ligne in p.stdout:
        ligne = ligne.rstrip()
        print("    " + ligne, flush=True)
        fh.write("    " + ligne + "\n")
    p.wait()
    # Avant que l'objet Popen ne soit ramassé : le handle doit être encore ouvert.
    pic = pic_memoire(p)
    if veilleur:
        arret.set()
        veilleur.join(timeout=3)
        pic = releve[0] or None
    fh.flush()
    duree = (time.time() - t0) / 60
    RELEVE.append((os.path.basename(argv[0]), duree, pic))
    journaliser(fh, f"  → code {p.returncode}, {duree:.1f} min"
                    + (f", pointe mémoire {pic:.0f} Mo" if pic else ""))
    return p.returncode


def recapituler(fh):
    """Ce qu'il faut savoir au réveil pour dimensionner une machine distante.

    On ne conclut pas à la place du lecteur : on donne la pointe mesurée, ce
    qu'elle implique en RAM une fois arrondie au palier commercial, et le
    volume qui doit tenir sur le disque. Le choix reste éditorial — mais il
    n'est plus une devinette.
    """
    if not RELEVE:
        return
    journaliser(fh, "\n" + "=" * 66)
    journaliser(fh, "RELEVÉ — de quoi dimensionner un serveur distant")
    journaliser(fh, "=" * 66)
    journaliser(fh, f"  {'étape':26} {'durée':>10} {'pointe mémoire':>16}")
    for nom, minutes, pic in RELEVE:
        journaliser(fh, f"  {nom:26} {minutes:8.1f} min "
                        f"{(f'{pic:.0f} Mo' if pic else '—'):>16}")

    pics = [p for _, _, p in RELEVE if p]
    total = sum(m for _, m, _ in RELEVE)
    journaliser(fh, f"\n  durée cumulée : {total:.0f} min "
                    f"({total / 60:.1f} h)")
    if pics:
        crete = max(pics)
        # Les paliers courants chez les hébergeurs. On prend le premier qui
        # laisse de la marge : une base DuckDB grossit à chaque département.
        palier = next((g for g in (2, 4, 8, 16, 32) if g * 1024 > crete * 1.6),
                      64)
        journaliser(fh, f"  pointe la plus haute : {crete:.0f} Mo")
        journaliser(fh, f"  → RAM à prévoir : {palier} Go "
                        "(pointe × 1,6, arrondie au palier supérieur)")

    volumes = {}
    for rel in ("data/brut", "site/public", "data/dossiers"):
        chemin = os.path.join(RACINE, rel.replace("/", os.sep))
        if os.path.isdir(chemin):
            volumes[rel] = sum(
                os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(chemin) for f in fs) / 2**20
    base = os.path.join(RACINE, "data", "eau.duckdb")
    if os.path.exists(base):
        volumes["eau.duckdb"] = os.path.getsize(base) / 2**20
    if volumes:
        journaliser(fh, "\n  ce qui doit tenir sur le disque :")
        for rel, mo in sorted(volumes.items(), key=lambda kv: -kv[1]):
            journaliser(fh, f"    {rel:22} {mo:8.0f} Mo")
        journaliser(fh, f"    {'TOTAL':22} {sum(volumes.values()):8.0f} Mo"
                        "   — et il croît à chaque département")


def controles_prealables(fh, publier):
    """Tout ce qui peut faire rater la nuit, vérifié pendant qu'on est là."""
    soucis = []

    tampon = os.path.join(RACINE, "data", "brut")
    if not os.path.isdir(tampon) or not os.listdir(tampon):
        soucis.append("le cache brut `data/brut/` est vide — rien à ingérer")
    else:
        n = sum(len(fs) for _, _, fs in os.walk(tampon))
        journaliser(fh, f"  cache brut : {n} fichier(s)")

    libre = shutil.disk_usage(RACINE).free / 2**30
    journaliser(fh, f"  disque libre : {libre:.1f} Go")
    if libre < 5:
        soucis.append(f"moins de 5 Go libres ({libre:.1f}) — "
                      "la vitrine seule pèse plus d'un giga-octet")

    if publier:
        # On refuse MAINTENANT plutôt qu'après deux heures de refigeage.
        for cle in ("OBS_FTP_HOTE", "OBS_FTP_UTILISATEUR", "OBS_FTP_RACINE",
                    "OBS_FTP_MOTDEPASSE"):
            if not os.environ.get(cle, "").strip():
                soucis.append(
                    f"{cle} absent — la publication sans surveillance ne peut "
                    "pas demander de mot de passe")
        journaliser(fh, "  identifiants de publication : "
                        + ("complets" if not soucis else "INCOMPLETS"))
    return soucis


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--publier", action="store_true",
                   help="publier à la fin, si et seulement si tout est vert")
    p.add_argument("--depuis", choices=[e[0] for e in ETAPES],
                   help="reprendre à cette étape — et enchaîner les suivantes")
    p.add_argument("--seulement", choices=[e[0] for e in ETAPES],
                   help="ne faire QUE cette étape, sans enchaîner")
    p.add_argument("--simulation", action="store_true",
                   help="afficher ce qui serait lancé, sans rien exécuter")
    p.add_argument("--sauf", action="append", default=["donnees/verdicts.csv"],
                   help="motif écarté de la publication, répétable")
    a = p.parse_args()

    os.makedirs(os.path.join(RACINE, "data", "journal"), exist_ok=True)
    horo = datetime.now().strftime("%Y-%m-%d_%Hh%M")
    chemin = os.path.join(RACINE, "data", "journal", f"nuit-{horo}.log")

    with open(chemin, "w", encoding="utf-8") as fh:
        journaliser(fh, "=" * 66)
        journaliser(fh, f"CHAÎNE DE NUIT — {datetime.now():%d/%m/%Y %H:%M}")
        journaliser(fh, f"journal : {chemin}")
        journaliser(fh, "=" * 66)

        journaliser(fh, "\nContrôles préalables")
        soucis = controles_prealables(fh, a.publier)
        if soucis:
            for s in soucis:
                journaliser(fh, f"  ARRÊT — {s}")
            journaliser(fh, "\nRien n'a été lancé.")
            return 2

        depart = [e[0] for e in ETAPES].index(a.depuis) if a.depuis else 0
        t0 = time.time()
        for i, (cle, titre, commandes) in enumerate(ETAPES):
            # `--seulement` isole une étape ; `--depuis` reprend et enchaîne.
            # La distinction n'est pas cosmétique : `--depuis figer` lance un
            # refigeage COMPLET puis reconstruit et publie. Confondre les deux
            # est une erreur qu'on ne fait qu'une fois, et qui coûte des heures.
            if a.seulement and cle != a.seulement:
                continue
            if not a.seulement and i < depart:
                journaliser(fh, f"\n— {titre} — SAUTÉE (--depuis {a.depuis})")
                continue
            journaliser(fh, f"\n— {titre}")
            for argv in commandes:
                if a.simulation:
                    journaliser(fh, f"  (simulation) $ {' '.join(argv)}")
                    continue
                if lancer(fh, argv) != 0:
                    journaliser(fh, f"\nÉCHEC à l'étape « {cle} ». "
                                    "La chaîne s'arrête ici.")
                    journaliser(fh, "Rien n'a été publié. Reprendre avec "
                                    f"--depuis {cle} après correction.")
                    # Les mesures des étapes déjà passées restent utiles.
                    recapituler(fh)
                    return 1

        journaliser(fh, f"\nToutes les étapes sont passées "
                        f"({(time.time() - t0) / 60:.0f} min).")
        recapituler(fh)

        if a.publier and not a.seulement:
            journaliser(fh, "\n— Publication")
            argv = ["site/publier.py", "--certificat-non-verifie"]
            for motif in a.sauf:
                argv += ["--sauf", motif]
            if a.simulation:
                journaliser(fh, f"  (simulation) $ {' '.join(argv)}")
                return 0
            if lancer(fh, argv) != 0:
                journaliser(fh, "\nÉCHEC à la publication. Le site construit "
                                "est bon, seul l'envoi a échoué — relancer "
                                "site/publier.py, il reprendra le reliquat.")
                return 1
            journaliser(fh, "\nPublié.")
        else:
            journaliser(fh, "\nNon publié (--publier non demandé). "
                            "La vitrine construite attend dans site/public/.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

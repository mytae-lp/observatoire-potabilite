# -*- coding: utf-8 -*-
"""Le balisage produit parle-t-il le vocabulaire de la charte ?

Écrit le 16 août 2026, après une publication que rien n'a arrêtée.

CE QUI S'EST PASSÉ, et qu'aucun contrôle ne voyait. Le portage v2 a fait passer
toutes les pages sur `observatoire-v2.css`. Les pages de navigation avaient été
portées, la FICHE COMMUNALE non : elle émet toujours le vocabulaire d'avant.
4 919 fiches sont parties en ligne avec 16 % seulement du vocabulaire de leur
maquette. Les huit contrôles de `test_sorties.py` ont répondu « sorties
conformes » — parce qu'aucun ne compare ce qu'on écrit à ce que la charte
décrit. Ils vérifient la méthode, la traçabilité, la prose ; pas la forme.

Une page peut donc être juste, sourcée, datée, sans prescription — et illisible.
C'est ce trou-là que ce fichier bouche.

CE QU'IL MESURE. Pour chaque type de page ayant une maquette de référence :
la part du vocabulaire de la maquette effectivement employée par la page
produite. Ce n'est pas un contrôle de pixels — il ne dit pas que c'est BEAU. Il
dit que la page est bâtie avec les composants prévus, ce qui est vérifiable, et
suffit à attraper une page qui n'a pas été portée du tout.

CE QU'IL NE MESURE PAS, et il faut le savoir : un recouvrement de 100 % ne
garantit pas que les composants sont au bon endroit ni bien remplis. La
relecture humaine reste, comme pour le contrôle n° 8.

Usage :
    comparer_charte.py                      contrôle site/public
    comparer_charte.py --sortie /tmp/apercu contrôle un aperçu
    comparer_charte.py --seuil 0.85         durcit l'exigence
"""
import argparse
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTE_DEFAUT = os.path.join(
    os.path.dirname(os.path.dirname(RACINE)), "Charte_graphique_v2")

# maquette de référence -> comment retrouver la page produite correspondante
CORRESPONDANCES = [
    ("maquette-fiche-montech.html",   "commune/82125.html"),
    ("maquette-fiche-thiville.html",  "commune/28389.html"),
    ("maquette-fiche-tramayes.html",  "commune/71545.html"),
    ("maquette-accueil.html",         "index.html"),
    ("maquette-carte.html",           "carte.html"),
    ("maquette-methode.html",         "methode.html"),
    ("maquette-sources.html",         "sources.html"),
    ("maquette-substances.html",      "substances.html"),
    ("maquette-departement-31.html",  "departement/31.html"),
]

# Ces classes ne disent rien de la structure : elles varient d'une commune à
# l'autre (un verdict, un état). Les exiger reviendrait à demander que Thiville
# ait les mêmes dépassements que Montech.
VARIABLES = re.compile(r"--(conforme|attention|indetermine|bascule|depasse|"
                       r"ok|indet|souslq|repere|vise|hors|avere|suspect|nondoc|"
                       r"debut|fin|ici|deux|serie|gris)$")


def classes(chemin):
    txt = open(chemin, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"<style.*?</style>", "", txt, flags=re.S)
    txt = re.sub(r"<script.*?</script>", "", txt, flags=re.S)
    s = set()
    for a in re.findall(r'class="([^"]+)"', txt):
        s |= set(a.split())
    return s


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--sortie", default=os.path.join(RACINE, "site", "public"))
    p.add_argument("--charte", default=CHARTE_DEFAUT)
    p.add_argument("--seuil", type=float, default=0.80,
                   help="part minimale du vocabulaire de la maquette (défaut 0.80)")
    a = p.parse_args()

    if not os.path.isdir(a.charte):
        print(f"  charte introuvable : {a.charte}")
        print("  contrôle ignoré — il ne bloque pas ce qu'il ne peut pas voir.")
        return 0

    print(f"  charte  : {a.charte}")
    print(f"  produit : {a.sortie}")
    print(f"  seuil   : {a.seuil:.0%} du vocabulaire de la maquette\n")
    print(f"  {'page':<26} {'maquette':>9} {'produit':>8} {'commun':>7} {'part':>7}")

    echecs, examinees = [], 0
    for maquette, page in CORRESPONDANCES:
        m = os.path.join(a.charte, maquette)
        q = os.path.join(a.sortie, page)
        if not os.path.exists(m) or not os.path.exists(q):
            print(f"  {page:<26} {'—':>9} {'—':>8}   (absente, non contrôlée)")
            continue
        examinees += 1
        cm = {c for c in classes(m) if not VARIABLES.search(c)}
        cq = classes(q)
        commun = cm & cq
        part = len(commun) / len(cm) if cm else 1.0
        etat = "" if part >= a.seuil else "   <-- SOUS LE SEUIL"
        print(f"  {page:<26} {len(cm):>9} {len(cq):>8} {len(commun):>7} "
              f"{part:>6.0%}{etat}")
        if part < a.seuil:
            echecs.append((page, part, sorted(cm - cq)))

    if not examinees:
        print("\n  aucune correspondance vérifiable — contrôle sans objet.")
        return 0

    print()
    if not echecs:
        print(f"  les {examinees} page(s) contrôlée(s) emploient le vocabulaire "
              f"de leur maquette.")
        return 0

    for page, part, manquantes in echecs:
        print(f"  {page} — {part:.0%} du vocabulaire attendu")
        print(f"    {len(manquantes)} classe(s) de la maquette jamais émises :")
        print("      " + ", ".join(manquantes[:30]))
        if len(manquantes) > 30:
            print(f"      … et {len(manquantes) - 30} autres")
    print()
    print("  Une page très en dessous du seuil n'est pas mal habillée : elle")
    print("  n'a pas été portée. Publier reviendrait à mettre en ligne une")
    print("  page que personne n'a regardée.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

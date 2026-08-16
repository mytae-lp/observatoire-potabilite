# -*- coding: utf-8 -*-
"""
Mesure 3 du §7 — chaque page reste lisible sans JavaScript.

    py -X utf8 outils/mesure_sans_js.py
    py -X utf8 outils/mesure_sans_js.py --seuil 6000

**Attendu : le contenu principal présent partout, et plus de 6 000 caractères
de texte visible sur une fiche.**

Pourquoi cette mesure existe
----------------------------
La vitrine est un dossier de fichiers statiques, et la raison est écrite dans
`site/build_site.py` : *« un dossier de fichiers ne tombe pas en panne, ne coûte
rien à héberger, et sera encore lisible dans dix ans »*. Un site dont le contenu
n'apparaît qu'une fois le JavaScript exécuté n'a pas cette propriété — il dépend
d'un moteur qui, dans dix ans, aura changé.

Le JavaScript du site n'ajoute donc jamais de contenu : il **retire** (le filtre
de la carte, la recherche d'un département) ou il **réordonne** (le tri de
l'annuaire). Chacun de ces scripts porte la règle en commentaire ; cet outil
vérifie qu'elle tient encore.

Ce que la mesure ne peut pas prouver
------------------------------------
Elle compte des caractères et cherche des repères. Elle ne dit pas que la page
est *compréhensible* sans JavaScript — seulement qu'elle n'est pas vide. Une
fiche dont tous les paramètres seraient rendus mais dans le désordre passerait
cette mesure. La relecture reste humaine.
"""
from __future__ import annotations

import sys

sys.path.insert(0, __file__.rsplit("outils", 1)[0] + "outils")
from forme_commun import (bilan, dossier_demande, entete, navigateur,  # noqa: E402
                          pages_demandees, servir)

SEUIL_FICHE = 6000

# Ce que chaque type de page doit porter sans JavaScript. Ce sont des repères de
# contenu, pas de forme : un titre, une table, un verdict. S'ils manquent, la
# page ne dit plus ce pour quoi elle existe.
REPERES = {
    "index.html": ["Observatoire", "conforme"],
    "carte.html": ["département", "analyse"],
    "communes.html": ["commune"],
    "methode.html": ["mesure", "verdict"],
    "sources.html": ["Licence", "Hub'Eau"],
    "substances.html": ["paramètre"],
    "departement/": ["commune", "R1321"],
    "commune/": ["prélèvement", "paramètre"],
}

TEXTE_VISIBLE = r"""
() => {
  const it = document.createNodeIterator(document.body, NodeFilter.SHOW_TEXT);
  let n, out = 0;
  while ((n = it.nextNode())) {
    const e = n.parentElement;
    if (!e || ["SCRIPT","STYLE","NOSCRIPT","TITLE"].includes(e.tagName)) continue;
    const s = getComputedStyle(e);
    if (s.display === "none" || s.visibility === "hidden") continue;
    out += (n.nodeValue || "").trim().length;
  }
  return out;
}
"""


def _reperes_de(chemin):
    for cle, mots in REPERES.items():
        if chemin == cle or (cle.endswith("/") and chemin.startswith(cle)):
            return mots
    return []


def main():
    argv = sys.argv[1:]
    public = dossier_demande(argv)
    pages = pages_demandees(argv, public)
    seuil = int(argv[argv.index("--seuil") + 1]) if "--seuil" in argv else SEUIL_FICHE
    entete("MESURE 3 — lisibilité sans JavaScript", public, pages)

    echecs = []
    with servir(public) as base, navigateur() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(java_script_enabled=False)
        page = ctx.new_page()
        for chemin in pages:
            page.goto(f"{base}/{chemin}", wait_until="load")
            n = page.evaluate(TEXTE_VISIBLE)
            corps = page.inner_text("body")

            manquants = [m for m in _reperes_de(chemin) if m.lower() not in corps.lower()]
            if manquants:
                echecs.append(f"{chemin:30s} repère(s) absent(s) : {manquants}")

            # Le seuil de 6 000 ne vaut que pour les fiches : c'est là que le
            # contenu est le plus dépendant du script, puisque le détail des
            # paramètres est injecté depuis `const C` et `const PARAMS`.
            est_fiche = chemin.startswith("commune/")
            if est_fiche and n < seuil:
                echecs.append(f"{chemin:30s} {n} caractères < {seuil} attendus")
            elif n < 400:
                echecs.append(f"{chemin:30s} {n} caractères — page quasi vide")

            marque = "fiche" if est_fiche else "     "
            print(f"  {chemin:34s} {n:>7} caractères  {marque}")
        ctx.close()
        nav.close()

    return bilan(echecs, "page(s) illisible(s) sans JavaScript")


if __name__ == "__main__":
    raise SystemExit(main())

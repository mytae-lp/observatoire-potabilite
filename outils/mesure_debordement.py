# -*- coding: utf-8 -*-
"""
Mesure 2 du §7 — le débordement horizontal, de 320 à 2560 px.

    py -X utf8 outils/mesure_debordement.py
    py -X utf8 outils/mesure_debordement.py --page substances.html --coupable

**Attendu : 0 débordement**, sur chaque page et chaque largeur.

Le critère est `document.documentElement.scrollWidth <= window.innerWidth`. Un
site qui déborde oblige à faire glisser la page pour lire une fin de phrase ;
sur téléphone, c'est la première chose qu'on remarque et la dernière qu'on
pardonne.

Ce que la mesure a déjà attrapé, et qu'il faut savoir en la relisant :

- **le menu déployé réclamait 1 049 px de barre.** Le repli devait donc se
  déclencher à 1080 px et non à 900, sans quoi la barre débordait dans la
  fourchette 900-1080 — une plage étroite, jamais regardée à la main ;
- **`substances.html` débordait sur mobile** en v1 : `scrollWidth` 590 pour une
  fenêtre de 390. Un tableau de 1 243 lignes et 9 colonnes ne rentre pas, et
  c'est `.tableau-defile` qui le fait défiler **dans son cadre** au lieu de
  pousser la page entière.

`--coupable` remonte les éléments qui dépassent réellement du cadre. Sans lui on
sait qu'il y a débordement ; avec lui on sait quoi corriger. C'est la différence
entre une alarme et un diagnostic.
"""
from __future__ import annotations

import sys

sys.path.insert(0, __file__.rsplit("outils", 1)[0] + "outils")
from forme_commun import (LARGEURS, THEMES, bilan, dossier_demande,  # noqa: E402
                          entete, navigateur, pages_demandees, poser_theme,
                          servir)

# Les éléments qui dépassent du cadre. On ignore ceux dont un ancêtre défile
# volontairement (`overflow-x: auto`) : un tableau qui défile dans son cadre
# est la solution, pas le problème.
COUPABLES = r"""
() => {
  const W = document.documentElement.clientWidth;
  const dedans = e => {
    for (let p = e.parentElement; p; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox === "auto" || ox === "scroll" || ox === "hidden") return true;
    }
    return false;
  };
  const out = [];
  document.querySelectorAll("body *").forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    if (r.right <= W + 1 && r.left >= -1) return;
    if (dedans(e)) return;
    out.push({
      balise: e.tagName.toLowerCase(),
      classe: (e.getAttribute("class") || "").slice(0, 46),
      gauche: Math.round(r.left), droite: Math.round(r.right),
      largeur: Math.round(r.width),
    });
  });
  /* Le plus large d'abord : c'est presque toujours lui la cause, les autres
     étant ses enfants poussés avec lui. */
  return out.sort((a, b) => b.largeur - a.largeur).slice(0, 4);
}
"""


def main():
    argv = sys.argv[1:]
    public = dossier_demande(argv)
    pages = pages_demandees(argv, public)
    detail = "--coupable" in argv
    entete("MESURE 2 — débordement horizontal", public, pages)
    print(f"  largeurs: {len(LARGEURS)} de {LARGEURS[0]} à {LARGEURS[-1]} px")
    print(f"  soit {len(pages) * len(LARGEURS) * len(THEMES)} combinaisons")
    print()

    echecs = []
    with servir(public) as base, navigateur() as pw:
        nav = pw.chromium.launch()
        for theme in THEMES:
            page = nav.new_page(viewport={"width": 1280, "height": 900})
            for chemin in pages:
                pires = []
                for largeur in LARGEURS:
                    page.set_viewport_size({"width": largeur, "height": 900})
                    page.goto(f"{base}/{chemin}", wait_until="networkidle")
                    poser_theme(page, theme)
                    page.wait_for_timeout(60)
                    sw, iw = page.evaluate(
                        "() => [document.documentElement.scrollWidth,"
                        " window.innerWidth]")
                    if sw > iw:
                        ligne = (f"{theme:6s} {chemin:28s} {largeur:>5} px : "
                                 f"scrollWidth {sw} > {iw}")
                        if detail:
                            for c in page.evaluate(COUPABLES):
                                ligne += (f"\n      ↳ {c['balise']}."
                                          f"{c['classe']} "
                                          f"[{c['gauche']}…{c['droite']}]")
                        echecs.append(ligne)
                        pires.append(largeur)
                etat = "ok" if not pires else f"déborde à {pires}"
                print(f"  {theme:6s} {chemin:34s} {etat}")
            page.close()
        nav.close()

    return bilan(echecs, "débordement(s)")


if __name__ == "__main__":
    raise SystemExit(main())

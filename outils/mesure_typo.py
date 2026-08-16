# -*- coding: utf-8 -*-
"""
Mesure 4 du §7 — l'échelle typographique tient.

    py -X utf8 outils/mesure_typo.py
    py -X utf8 outils/mesure_typo.py --crans 13,15,17,19,23,30,40

**Attendu : aucune taille rendue hors des sept crans**, hors `clamp()`.

La décision D2 de la charte fixe sept crans — 13 / 15 / 17 / 19 / 23 / 30 / 40 —
un corps à 17 px et un plancher absolu à 13 px. Deux jetons échappent à la
règle, `--t-display` et `--t-chiffre`, parce qu'ils sont en `clamp()` et varient
donc continûment avec la fenêtre : l'outil les reconnaît à ce qu'ils sortent des
crans **en variant d'une largeur à l'autre**, et il ne les compte pas.

Le piège, et il revient à chaque fois
-------------------------------------
`small` et `.mono` déclarés en `em` réintroduisent des demi-pixels : `0.875em`
d'un parent à 17 px donne 14,875 px, qui n'est aucun cran. Une taille en `em`
n'est pas fausse en soi — elle le devient dès qu'elle multiplie un cran par un
facteur qui ne retombe pas sur un autre cran. C'est pour cela que la mesure
porte sur la taille **rendue** et non sur la feuille : la faute n'est visible
qu'une fois le calcul fait.

L'outil signale aussi tout texte **sous le plancher de 13 px**, qui est une
faute plus grave qu'un cran manqué : elle se voit à l'œil nu et exclut des
lecteurs.
"""
from __future__ import annotations

import sys

sys.path.insert(0, __file__.rsplit("outils", 1)[0] + "outils")
from forme_commun import (CRANS, bilan, dossier_demande, entete,  # noqa: E402
                          navigateur, pages_demandees, servir)

# Deux largeurs : ce qui bouge de l'une à l'autre est un `clamp()` assumé, ce
# qui reste hors crans aux deux est une faute. Sans cette comparaison, on ne
# peut pas distinguer les deux, et on finirait par blanchir toutes les tailles
# hors échelle sous prétexte qu'elles « pourraient » être fluides.
LARGEURS_TEST = (390, 1440)

TAILLES = r"""
() => {
  const vus = new Map();
  const it = document.createNodeIterator(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = it.nextNode())) {
    if (!(n.nodeValue || "").trim()) continue;
    const e = n.parentElement;
    if (!e || ["SCRIPT","STYLE","NOSCRIPT","TITLE"].includes(e.tagName)) continue;
    const s = getComputedStyle(e);
    if (s.display === "none" || s.visibility === "hidden") continue;
    const px = Math.round(parseFloat(s.fontSize) * 100) / 100;
    const cle = px + "|" + e.tagName.toLowerCase() + "|"
              + (e.getAttribute("class") || "").split(" ")[0];
    if (!vus.has(cle)) vus.set(cle, {
      px, balise: e.tagName.toLowerCase(),
      classe: (e.getAttribute("class") || "").slice(0, 34),
      exemple: (n.nodeValue || "").trim().slice(0, 34),
    });
  }
  return [...vus.values()];
}
"""


def main():
    argv = sys.argv[1:]
    public = dossier_demande(argv)
    pages = pages_demandees(argv, public)
    crans = ([float(x) for x in argv[argv.index("--crans") + 1].split(",")]
             if "--crans" in argv else list(CRANS))
    entete("MESURE 4 — échelle typographique", public, pages)
    print(f"  crans   : {', '.join(str(int(c)) for c in crans)} px")
    print(f"  plancher: {int(min(crans))} px")
    print()

    echecs, fluides = [], set()
    with servir(public) as base, navigateur() as pw:
        nav = pw.chromium.launch()
        page = nav.new_page()
        for chemin in pages:
            releves = {}
            for largeur in LARGEURS_TEST:
                page.set_viewport_size({"width": largeur, "height": 900})
                page.goto(f"{base}/{chemin}", wait_until="networkidle")
                page.wait_for_timeout(60)
                for t in page.evaluate(TAILLES):
                    cle = (t["balise"], t["classe"])
                    releves.setdefault(cle, {})[largeur] = t

            hors = []
            for cle, par_largeur in releves.items():
                tailles = {v["px"] for v in par_largeur.values()}
                # Une taille qui change avec la fenêtre est un clamp() assumé.
                if len(tailles) > 1:
                    fluides.add(f"{cle[0]}.{cle[1]}")
                    continue
                px = tailles.pop()
                if px in crans:
                    continue
                t = next(iter(par_largeur.values()))
                hors.append(px)
                gravite = "SOUS LE PLANCHER" if px < min(crans) else "hors crans"
                echecs.append(
                    f"{chemin:28s} {px:>6.2f} px  {gravite:16s} "
                    f"{t['balise']}.{t['classe']} « {t['exemple']} »")
            etat = "ok" if not hors else f"{len(hors)} taille(s) hors échelle"
            print(f"  {chemin:34s} {len(releves):4d} styles — {etat}")
        page.close()
        nav.close()

    if fluides:
        print()
        print(f"  i {len(fluides)} style(s) fluides, non comptés — clamp() assumé :")
        for f in sorted(fluides)[:8]:
            print(f"      {f}")

    return bilan(echecs, "taille(s) hors de l'échelle")


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""
Mesure 1 du §7 — le contraste, dans les deux thèmes.

    py -X utf8 outils/mesure_contraste.py
    py -X utf8 outils/mesure_contraste.py --page commune/28389.html
    py -X utf8 outils/mesure_contraste.py --dossier /tmp/site --pixels

**Attendu : 0 échec.**

Le seuil est celui de WCAG AA : 4,5:1 pour le texte courant, 3:1 dès 24 px, ou
dès 18,66 px en gras. Ce n'est pas une préférence esthétique — c'est ce qui
sépare un texte lisible d'un texte que certains lecteurs ne lisent pas.

Deux méthodes, et il faut les deux
----------------------------------
**Le fond calculé** couvre tout le site : pour chaque nœud de texte, on remonte
les ancêtres jusqu'au premier fond opaque et on compare. C'est rapide et exact
partout où le fond est une couleur.

**Les pixels réellement rendus** (`--pixels`) sont la seule méthode qui vaille
sur les **bandeaux photographiques** : une photographie n'a pas de couleur de
fond calculée, et `getComputedStyle` y répondrait « transparent » — donc rien.
La consigne §9.6 décrit la manœuvre, et elle est reprise ici telle quelle :
relever le rectangle de chaque nœud, rendre le contenu transparent **sans
toucher aux fonds**, capturer, puis comparer la couleur du texte au pixel **le
plus défavorable** de son rectangle. Pas au pixel moyen : un texte blanc sur une
goutte de rosée éclairée échoue sur la goutte, pas sur la moyenne.

Le piège qui a coûté une heure
------------------------------
Si une étiquette est **enfant** de son repère coloré, le contraste se mesure
contre le repère et non contre la carte : la mesure passe, et l'écran est
illisible. Repère et étiquette doivent être deux éléments séparés, le repère
dans un `::before`. L'outil ne peut pas détecter cette faute — il mesure ce
qu'on lui donne. Elle est notée ici parce que c'est là qu'on la relira.
"""
from __future__ import annotations

import sys

sys.path.insert(0, __file__.rsplit("outils", 1)[0] + "outils")
from forme_commun import (THEMES, bilan, dossier_demande, entete,  # noqa: E402
                          navigateur, pages_demandees, poser_theme, servir)

# Relevé des nœuds de texte et de leur fond effectif. Tout se passe dans la
# page : faire l'aller-retour en Python pour chaque nœud coûterait des minutes
# là où le navigateur le fait en une passe.
RELEVE = r"""
() => {
  const lum = c => {
    const f = c.map(v => { v /= 255; return v <= .03928 ? v/12.92
                                     : Math.pow((v + .055)/1.055, 2.4); });
    return .2126*f[0] + .7152*f[1] + .0722*f[2];
  };
  const rapport = (a, b) => {
    const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
    return (x + .05) / (y + .05);
  };
  /* Deux sérialisations, et elles n'ont pas la même échelle.
     `rgb()` / `rgba()` donnent 0-255 ; `color(srgb …)` — ce que Chromium
     produit pour un `color-mix()`, donc pour la barre translucide de la v2 —
     donne des flottants de 0 à 1. Les confondre transforme un fond papier en
     fond quasi noir, et l'outil annonce alors une trentaine d'échecs qui
     n'existent pas. Défaut réel, trouvé au premier emploi sur la v2. */
  const lire = s => {
    s = (s || "").trim();
    if (!s || s === "transparent" || s === "none") return null;
    const m = s.match(/[-\d.]+(?:e[-+]?\d+)?/gi);
    if (!m) return null;
    const v = m.map(Number);
    if (/^color\(/i.test(s)) {
      /* color(srgb r g b / a) — le premier nombre utile est r, et un éventuel
         indice de gamut n'apparaît pas dans cette forme. */
      const c = v.slice(0, 3).map(x => Math.round(Math.max(0, Math.min(1, x)) * 255));
      return {rgb: c, a: v.length > 3 ? v[3] : 1};
    }
    return {rgb: v.slice(0, 3), a: v.length > 3 ? v[3] : 1};
  };
  /* Le fond effectif : on remonte jusqu'au premier ancêtre opaque, en
     composant les couches semi-transparentes rencontrées en chemin. Un voile
     à 40 % sur un fond sombre ne donne pas le fond sombre. */
  const fond = n => {
    let couches = [];
    for (let e = n; e; e = e.parentElement) {
      const c = lire(getComputedStyle(e).backgroundColor);
      if (!c || c.a === 0) continue;
      couches.push(c);
      if (c.a === 1) break;
    }
    if (!couches.length) return [255, 255, 255];
    let base = couches[couches.length - 1];
    let out = base.rgb.slice();
    for (let i = couches.length - 2; i >= 0; i--) {
      const c = couches[i];
      out = out.map((v, k) => Math.round(c.rgb[k]*c.a + v*(1 - c.a)));
    }
    return out;
  };

  const sortie = [];
  const it = document.createNodeIterator(document.body, NodeFilter.SHOW_TEXT);
  let t;
  while ((t = it.nextNode())) {
    const texte = (t.nodeValue || "").trim();
    if (texte.length < 2) continue;
    const e = t.parentElement;
    if (!e || ["SCRIPT", "STYLE", "TITLE", "NOSCRIPT"].includes(e.tagName)) continue;
    const st = getComputedStyle(e);
    if (st.visibility === "hidden" || st.display === "none" || +st.opacity === 0) continue;
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;

    const px = parseFloat(st.fontSize);
    const gras = (parseInt(st.fontWeight, 10) || 400) >= 700;
    const seuil = (px >= 24 || (px >= 18.66 && gras)) ? 3 : 4.5;
    const av = lire(st.color);
    if (!av) continue;

    /* Un texte posé sur une image n'a pas de fond calculable : on le signale
       au lieu de le noter, et c'est --pixels qui le tranche. */
    let surImage = false;
    for (let x = e; x; x = x.parentElement) {
      if (getComputedStyle(x).backgroundImage !== "none") { surImage = true; break; }
      if (x.querySelector && x.matches(".bandeau, .bandeau-texte")) { surImage = true; break; }
    }

    const fd = fond(e);
    sortie.push({
      texte: texte.slice(0, 60), balise: e.tagName.toLowerCase(),
      classe: (e.getAttribute("class") || "").slice(0, 40),
      px, gras, seuil, surImage,
      rapport: Math.round(rapport(av.rgb, fd) * 100) / 100,
      rect: {x: r.x, y: r.y, w: r.width, h: r.height},
      couleur: av.rgb,
    });
  }
  return sortie;
}
"""

# Rendre le contenu invisible SANS toucher aux fonds : c'est ce qui permet de
# photographier le décor seul, sous le texte. Retirer le texte du DOM
# déplacerait la mise en page et on mesurerait un autre pixel.
EFFACER_TEXTE = """
  * { color: transparent !important; text-shadow: none !important; }
  .bandeau-fond, .bandeau-fond *, .bandeau-texte { visibility: visible !important; }
  p, h1, h2, h3, h4, span, a, li, td, th, b, em, div { text-decoration-color: transparent !important; }
"""


def _lum(c):
    f = []
    for v in c:
        v /= 255
        f.append(v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4)
    return .2126 * f[0] + .7152 * f[1] + .0722 * f[2]


def _rapport(a, b):
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def _pire_pixel(png_bytes, rect, largeur_page, couleur_texte):
    """Le pixel du rectangle qui donne le plus mauvais rapport."""
    try:
        from PIL import Image
    except ModuleNotFoundError:
        return None
    import io
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    ech = im.width / largeur_page if largeur_page else 1
    x0 = max(0, int(rect["x"] * ech))
    y0 = max(0, int(rect["y"] * ech))
    x1 = min(im.width, int((rect["x"] + rect["w"]) * ech))
    y1 = min(im.height, int((rect["y"] + rect["h"]) * ech))
    if x1 <= x0 or y1 <= y0:
        return None
    zone = im.crop((x0, y0, x1, y1))
    # Un échantillonnage suffit : on cherche le pire, pas une moyenne, et un
    # pas de 2 px ne peut pas manquer une zone claire de plus de 4 px.
    pire = None
    for py in range(0, zone.height, 2):
        for px in range(0, zone.width, 2):
            r = _rapport(couleur_texte, list(zone.getpixel((px, py))))
            if pire is None or r < pire:
                pire = r
    return round(pire, 2) if pire is not None else None


def main():
    argv = sys.argv[1:]
    public = dossier_demande(argv)
    pages = pages_demandees(argv, public)
    pixels = "--pixels" in argv
    entete("MESURE 1 — contraste (WCAG AA)", public, pages)

    echecs = []
    with servir(public) as base, navigateur() as pw:
        nav = pw.chromium.launch()
        for theme in THEMES:
            page = nav.new_page(viewport={"width": 1280, "height": 900})
            poser_theme(page, theme)
            for chemin in pages:
                page.goto(f"{base}/{chemin}", wait_until="networkidle")
                poser_theme(page, theme)
                page.wait_for_timeout(120)
                noeuds = page.evaluate(RELEVE)

                capture = None
                if pixels and any(n["surImage"] for n in noeuds):
                    page.add_style_tag(content=EFFACER_TEXTE)
                    capture = page.screenshot()
                    page.reload(wait_until="networkidle")
                    poser_theme(page, theme)

                for n in noeuds:
                    r = n["rapport"]
                    methode = "fond"
                    if n["surImage"] and capture is not None:
                        rp = _pire_pixel(capture, n["rect"], 1280, n["couleur"])
                        if rp is not None:
                            r, methode = rp, "pixels"
                    elif n["surImage"]:
                        continue  # sans --pixels, on ne prétend pas savoir
                    if r < n["seuil"]:
                        echecs.append(
                            f"{theme:6s} {chemin:28s} {r:5.2f} < {n['seuil']} "
                            f"({methode}) {n['balise']}.{n['classe']} "
                            f"« {n['texte'][:40]} »")
                print(f"  {theme:6s} {chemin:34s} {len(noeuds):4d} nœud(s)"
                      + ("  [pixels]" if capture is not None else ""))
            page.close()
        nav.close()

    if not pixels:
        print()
        print("  i Les textes posés sur une photographie ont été ignorés : "
              "relancer avec --pixels pour les mesurer (§9.6).")
    return bilan(echecs, "échec(s) de contraste")


if __name__ == "__main__":
    raise SystemExit(main())

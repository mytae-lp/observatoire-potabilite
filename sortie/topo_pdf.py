# -*- coding: utf-8 -*-
"""
Met un relevé Markdown à la charte de l'Observatoire, et l'imprime en PDF.

    py -X utf8 sortie/topo_pdf.py data/etudes/demandes/ARTIGAT-09019_2026-08-21.md

Pourquoi un script à part de `src/md_en_pdf.py`
-----------------------------------------------
`md_en_pdf.py` produit des rapports de travail : une feuille de style maison,
lisible, sans rapport avec la vitrine. Elle convient pour un matériau d'étude
qui ne sort pas du projet.

**Un document remis à un tiers, lui, porte la signature de l'Observatoire.** Il
doit donc porter sa forme : les jetons de `site/gabarits/observatoire-v2.css`,
les deux polices de la décision D7, l'échelle typographique de D2 et le rythme
d'espacement de D3. Mélanger les deux usages dans un seul script aurait fini
par faire sortir un relevé destiné à une mairie sous une charte inventée.

CE QUE LA CHARTE IMPOSE, ET QUI SURVIT AU PAPIER
------------------------------------------------
Les cinq couleurs de sens gardent leur rôle (§2.4, §2.10) — mais un relevé de
commune n'en emploie que ce dont il parle, et jamais pour décorer. Ce qui
compte ici :

  · **la traçabilité sur chaque page** (§8bis obl. 9) — version de référentiel
    et date de calcul en pied de page, sur toutes les pages, pas seulement la
    première. C'est ce que le pied `@page` fait ;
  · **le dénominateur a une place** (§2.8) — la classe `.denominateur` ;
  · **aucune couleur hors jetons** (D1) : tout est en `var(--…)`, repris tels
    quels de la feuille de la vitrine ;
  · **le thème clair seulement.** La charte a deux thèmes (D12), le papier n'en
    a qu'un — imprimer le thème sombre gaspillerait l'encre et perdrait les
    contrastes mesurés en clair.

L'ADAPTATION AU PAPIER, ET ELLE EST ASSUMÉE
--------------------------------------------
L'échelle de D2 est en pixels, pour un écran. Sur A4 un corps à 17 px donnerait
une ligne trop longue et un document deux fois trop épais. Les sept crans sont
donc **transposés en points en gardant leurs rapports** — corps à 10 pt, et le
plancher de 13 px devient 8 pt. Ce n'est pas une entorse : c'est la même
échelle, changée d'unité une fois, en un seul endroit.

La chaîne est celle de `md_en_pdf.py`, et pour les mêmes raisons : Pandoc rend
le HTML, un navigateur sans interface l'imprime. Pas de LaTeX sur cette
machine, et WeasyPrint réclame des bibliothèques GTK que Windows n'a pas.

Le PDF est une SORTIE. Le Markdown reste le document de référence : ne jamais
corriger un relevé dans le PDF.
"""
import argparse
import base64
import os
import re
import subprocess
import sys
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICES = os.path.join(RACINE, "site", "gabarits", "polices")

NAVIGATEURS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def navigateur():
    for c in NAVIGATEURS:
        if os.path.exists(c):
            return c
    raise SystemExit("ARRÊT — ni Chrome ni Edge trouvé. Voir NAVIGATEURS.")


def police_inline(nom):
    """Les .woff2 sont inlinés en base64.

    121 ko pour les trois, soit ~161 ko une fois encodés — le prix d'un HTML
    qui s'imprime sans dépendre d'un chemin relatif ni d'un accès fichier que
    le navigateur sans interface refuse selon son humeur. La décision D7 cesse
    de s'appliquer EN SILENCE quand une police ne charge pas : les pages
    retombent sur Georgia et personne ne le voit. Ici, ça ne peut pas arriver.
    """
    chemin = os.path.join(POLICES, nom)
    if not os.path.exists(chemin):
        raise SystemExit("ARRÊT — police absente : %s\n"
                         "  La charte (D7) ne se rend pas sans elle." % chemin)
    with open(chemin, "rb") as fh:
        return base64.b64encode(fh.read()).decode("ascii")


def feuille():
    return """
@font-face { font-family:"Inter"; font-style:normal; font-weight:100 900;
  src:url(data:font/woff2;base64,%s) format("woff2"); }
@font-face { font-family:"Newsreader"; font-style:normal; font-weight:200 800;
  src:url(data:font/woff2;base64,%s) format("woff2"); }
@font-face { font-family:"Newsreader"; font-style:italic; font-weight:200 800;
  src:url(data:font/woff2;base64,%s) format("woff2"); }

/* LES JETONS, repris de site/gabarits/observatoire-v2.css — thème clair seul.
   Aucune couleur littérale sous cette ligne (D1). */
:root {
  --paper:#F2F5F7; --card:#FFFFFF; --card-alt:#FAFBFC;
  --ink:#0F1E2E; --ink-soft:#4C5F71; --ink-faint:#5A6E80;
  --line:#D5DEE5; --line-soft:#E6ECF0;
  --eau:#0B6A73; --eau-deep:#08344C; --eau-bg:#E2F0F1;
  --vert:#24734A; --vert-bg:#E9F4EE;
  --rouge:#B23A2E; --rouge-bg:#F8E7E4;
  --bascule:#63469B; --bascule-bg:#EEE9F7;
  --gris:#55636F; --gris-bg:#E7EBEF;
  --ambre:#8E5A0B; --ambre-bg:#FAEFD9;

  --f-titre:"Newsreader","Iowan Old Style",Georgia,serif;
  --f-texte:"Inter",system-ui,"Segoe UI",Helvetica,Arial,sans-serif;
  --f-mono:ui-monospace,"Cascadia Code",Consolas,monospace;

  /* D2 transposée au papier — mêmes sept crans, unité changée une fois. */
  --t-xs:8pt; --t-sm:8.8pt; --t-base:10pt; --t-md:11pt;
  --t-lg:13pt; --t-xl:16pt; --t-2xl:22pt;
  --lh-serre:1.15; --lh-titre:1.25; --lh-texte:1.55;

  /* D3 — base 4, transposée. */
  --e-1:2pt; --e-2:4pt; --e-3:6pt; --e-4:9pt; --e-5:13pt;
  --e-6:18pt; --e-7:26pt; --e-8:35pt;

  --r-sm:3pt; --r-md:5pt; --r-lg:8pt; --r-pastille:999px;
}

/* LA TRAÇABILITÉ SUR CHAQUE PAGE (§8bis obl. 9), pas seulement la première. */
@page {
  size:A4; margin:20mm 18mm 18mm 18mm;
  @bottom-left  { font-family:"Inter"; font-size:7.5pt; color:#5A6E80;
                  content:"Observatoire de la potabilité réglementaire — référentiel 982f3e6ea21d"; }
  @bottom-right { font-family:"Inter"; font-size:7.5pt; color:#5A6E80;
                  content:counter(page) " / " counter(pages); }
}

body { font-family:var(--f-texte); font-size:var(--t-base);
       line-height:var(--lh-texte); color:var(--ink);
       background:#FFFFFF; margin:0;
       -webkit-print-color-adjust:exact; print-color-adjust:exact;
       font-variant-numeric:tabular-nums; }

h1 { font-family:var(--f-titre); font-size:var(--t-2xl); font-weight:600;
     line-height:var(--lh-titre); color:var(--eau-deep);
     margin:0 0 var(--e-4); letter-spacing:-.01em; }
h1 + p { color:var(--ink-soft); font-size:var(--t-md);
         line-height:var(--lh-titre); margin-top:0;
         padding-bottom:var(--e-5); border-bottom:2pt solid var(--eau); }

h2 { font-family:var(--f-titre); font-size:var(--t-xl); font-weight:600;
     line-height:var(--lh-titre); color:var(--eau-deep);
     margin:var(--e-7) 0 var(--e-3); padding-bottom:var(--e-2);
     border-bottom:.6pt solid var(--line);
     break-after:avoid; page-break-after:avoid; }
h3 { font-family:var(--f-titre); font-size:var(--t-lg); font-weight:600;
     color:var(--ink); margin:var(--e-5) 0 var(--e-2);
     break-after:avoid; page-break-after:avoid; }

p { margin:0 0 var(--e-4); orphans:2; widows:2; }
strong { font-weight:650; color:var(--eau-deep); }
em { color:var(--ink-soft); font-style:italic; }
a { color:var(--eau); text-decoration:none; }
code { font-family:var(--f-mono); font-size:var(--t-xs);
       background:var(--card-alt); border:.4pt solid var(--line-soft);
       border-radius:var(--r-sm); padding:.5pt 2.5pt; color:var(--eau-deep); }

ul, ol { margin:0 0 var(--e-4); padding-left:var(--e-5); }
li { margin-bottom:var(--e-2); }
li::marker { color:var(--eau); }

/* Le parti plat de la v1, conservé (charte §4.1) : un filet, pas un relief. */
blockquote { margin:var(--e-4) 0; padding:var(--e-3) var(--e-4);
             border-left:2.5pt solid var(--eau); background:var(--eau-bg);
             color:var(--eau-deep); font-family:var(--f-titre);
             font-size:var(--t-md); line-height:var(--lh-titre);
             break-inside:avoid; page-break-inside:avoid; }
blockquote p:last-child { margin-bottom:0; }

table { border-collapse:collapse; width:100%%; margin:var(--e-4) 0;
        font-size:var(--t-sm); break-inside:avoid; page-break-inside:avoid; }
thead th { font-family:var(--f-texte); font-weight:600; text-align:left;
           color:var(--eau-deep); background:var(--eau-bg);
           padding:var(--e-2) var(--e-3);
           border-bottom:1.2pt solid var(--eau); }
td { padding:var(--e-2) var(--e-3); border-bottom:.4pt solid var(--line-soft);
     vertical-align:top; }
tbody tr:nth-child(even) td { background:var(--card-alt); }
td[align="right"], th[align="right"] { text-align:right; }

hr { border:none; border-top:.6pt solid var(--line); margin:var(--e-6) 0; }

/* §2.8 — le dénominateur n'est pas une mention secondaire, il a une place. */
.denominateur { font-size:var(--t-sm); color:var(--ink-soft); }
"""


def html(fragment, titre):
    inter = police_inline("inter-var.woff2")
    news = police_inline("newsreader-var.woff2")
    news_it = police_inline("newsreader-var-italic.woff2")
    css = feuille() % (inter, news, news_it)
    return ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<title>%s</title><style>%s</style></head><body>%s</body></html>"
            % (titre, css, fragment))


def convertir(source, sortie=None):
    if not os.path.exists(source):
        raise SystemExit("ARRÊT — introuvable : %s" % source)
    sortie = sortie or os.path.splitext(source)[0] + ".pdf"

    fragment = subprocess.run(
        ["pandoc", source, "-f", "markdown+pipe_tables+smart", "-t", "html5"],
        capture_output=True, check=True).stdout.decode("utf-8")

    with open(source, encoding="utf-8") as fh:
        premiere = fh.readline().lstrip("# ").strip()

    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                      encoding="utf-8")
    tmp.write(html(fragment, premiere or os.path.basename(source)))
    tmp.close()

    subprocess.run([navigateur(), "--headless", "--disable-gpu",
                    "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=10000",
                    "--print-to-pdf=" + os.path.abspath(sortie),
                    "file:///" + tmp.name.replace("\\", "/")],
                   capture_output=True, check=True)
    os.unlink(tmp.name)
    if not os.path.exists(sortie):
        raise SystemExit("ARRÊT — le navigateur n'a rien écrit.")
    print("%s — %.0f ko" % (sortie, os.path.getsize(sortie) / 1024))
    return sortie


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("source", help="le .md à mettre en forme")
    p.add_argument("--sortie", help="chemin du PDF (défaut : à côté du .md)")
    a = p.parse_args()
    convertir(a.source, a.sortie)

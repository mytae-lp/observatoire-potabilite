# -*- coding: utf-8 -*-
"""
Convertit des rapports Markdown en PDF.

    py -X utf8 src/md_en_pdf.py data/etudes/conformite_sur_panel_reduit
    py -X utf8 src/md_en_pdf.py chemin/vers/un.md --sortie ailleurs/

Chaîne : Pandoc produit un HTML autonome, un navigateur sans interface
l'imprime en PDF. C'est le chemin le plus court sur cette machine — pas de
LaTeX installé, et WeasyPrint réclame des bibliothèques GTK que Windows n'a
pas. Chrome ou Edge sont là de toute façon.

Le PDF est une SORTIE, jamais une source : il se régénère à partir du Markdown,
qui reste le document de référence. Ne jamais corriger un rapport dans le PDF.
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVIGATEURS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
body { font-family: "Segoe UI", system-ui, sans-serif; font-size: 10.5pt;
       line-height: 1.5; color: #1c1c1c; max-width: none; }
h1 { font-size: 19pt; border-bottom: 2px solid #0E7C86; padding-bottom: 6px;
     color: #0E7C86; margin-top: 0; }
h2 { font-size: 14pt; margin-top: 22px; color: #0E7C86;
     border-bottom: 1px solid #d8e4e7; padding-bottom: 3px; }
h3 { font-size: 11.5pt; margin-top: 16px; color: #26404a; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt;
        page-break-inside: avoid; }
th { background: #eef4f6; text-align: left; padding: 5px 7px;
     border-bottom: 2px solid #0E7C86; }
td { padding: 4px 7px; border-bottom: 1px solid #e4e9eb; vertical-align: top; }
blockquote { border-left: 3px solid #0E7C86; background: #f4f9fa; margin: 12px 0;
             padding: 8px 12px; font-style: normal; }
code { background: #f0f2f3; padding: 1px 4px; border-radius: 3px;
       font-size: 9pt; }
strong { color: #12333c; }
hr { border: none; border-top: 1px solid #dde4e6; margin: 18px 0; }
em { color: #4a5a60; }
h2, h3 { page-break-after: avoid; }
"""


def navigateur():
    for c in NAVIGATEURS:
        if os.path.exists(c):
            return c
    raise SystemExit("aucun navigateur trouvé pour l'impression PDF.")


def convertir(md, sortie, nav):
    base = os.path.splitext(os.path.basename(md))[0]
    pdf = os.path.join(sortie, base + ".pdf")
    with tempfile.TemporaryDirectory() as tmp:
        css = os.path.join(tmp, "s.css")
        with open(css, "w", encoding="utf-8") as f:
            f.write(CSS)
        html = os.path.join(tmp, base + ".html")
        subprocess.run(
            ["pandoc", md, "-f", "gfm", "-t", "html5", "-s",
             "--metadata", "title=" + base, "--css", css,
             "--embed-resources", "-o", html],
            check=True, capture_output=True)
        subprocess.run(
            [nav, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             "--print-to-pdf=" + pdf, "--virtual-time-budget=4000",
             "file:///" + html.replace("\\", "/")],
            check=True, capture_output=True, timeout=180)
    return pdf if os.path.exists(pdf) else None


def main():
    p = argparse.ArgumentParser(description="Markdown -> PDF")
    p.add_argument("cible", help="un fichier .md, ou un dossier")
    p.add_argument("--sortie", help="dossier de destination (défaut : « pdf » "
                                    "dans le dossier de la cible)")
    a = p.parse_args()

    cible = a.cible if os.path.isabs(a.cible) else os.path.join(RACINE, a.cible)
    if os.path.isdir(cible):
        fichiers = sorted(glob.glob(os.path.join(cible, "*.md")))
        defaut = os.path.join(cible, "pdf")
    else:
        fichiers = [cible]
        defaut = os.path.join(os.path.dirname(cible), "pdf")
    if not fichiers:
        raise SystemExit("aucun fichier .md sous %s" % cible)

    sortie = a.sortie or defaut
    os.makedirs(sortie, exist_ok=True)
    nav = navigateur()
    print("navigateur : %s" % os.path.basename(nav))
    print("%d fichier(s) -> %s\n" % (len(fichiers), sortie))

    ok, ko = 0, []
    for md in fichiers:
        nom = os.path.basename(md)
        try:
            pdf = convertir(md, sortie, nav)
            if pdf:
                print("  ok   %-52s %6.0f Ko" % (nom, os.path.getsize(pdf) / 1024))
                ok += 1
            else:
                print("  ÉCHEC %s — pas de PDF produit" % nom)
                ko.append(nom)
        except subprocess.CalledProcessError as e:
            print("  ÉCHEC %s : %s" % (nom, (e.stderr or b"")[:160].decode(
                "utf-8", "replace")))
            ko.append(nom)
        except Exception as e:
            print("  ÉCHEC %s : %s" % (nom, str(e)[:160]))
            ko.append(nom)

    print("\n%d converti(s)%s" % (ok, ", %d en échec" % len(ko) if ko else ""))
    if ko:
        sys.exit(1)


if __name__ == "__main__":
    main()

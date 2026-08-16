# -*- coding: utf-8 -*-
"""Le squelette d'une page : son arborescence de classes, sans le contenu.

Une maquette de 306 ko ne se lit pas. Sa STRUCTURE, si : quelques centaines de
lignes. C'est elle qu'il faut reproduire, pas les chiffres de Montech — ceux-là
viennent de la base.

Usage :  squelette.py <fichier.html> [profondeur] [--sections]
"""
import re
import sys
from html.parser import HTMLParser

BLOCS = {"div", "section", "article", "aside", "header", "footer", "main",
         "nav", "table", "thead", "tbody", "tr", "ul", "ol", "li", "figure",
         "details", "form", "h1", "h2", "h3", "h4", "p", "span", "svg", "button"}
MUETS = {"span", "p", "li", "tr", "svg", "path", "button", "h3", "h4"}


class Squelette(HTMLParser):
    def __init__(self, profondeur):
        super().__init__(convert_charrefs=True)
        self.pile, self.lignes, self.max = [], [], profondeur
        self.dans_main = False
        self.vus = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "main":
            self.dans_main = True
        if tag in ("br", "img", "source", "input", "meta", "link"):
            return
        self.pile.append(tag)
        if not self.dans_main:
            return
        cl = d.get("class", "").strip()
        prof = len(self.pile) - 1
        if prof > self.max:
            return
        if tag in MUETS and not cl:
            return
        # Une même signature répétée (les lignes d'un tableau) ne s'écrit qu'une
        # fois : ce qui compte est la forme, pas le nombre de lignes.
        sig = (prof, tag, cl)
        if sig in self.vus:
            return
        self.vus.add(sig)
        marque = f"<{tag}>" if not cl else f"<{tag} class=\"{cl}\">"
        self.lignes.append("  " * prof + marque)

    def handle_endtag(self, tag):
        if tag == "main":
            self.dans_main = False
        for i in range(len(self.pile) - 1, -1, -1):
            if self.pile[i] == tag:
                del self.pile[i:]
                break


def main():
    chemin = sys.argv[1]
    prof = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 6
    txt = open(chemin, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"<style.*?</style>", "", txt, flags=re.S)
    txt = re.sub(r"<script.*?</script>", "", txt, flags=re.S)

    if "--sections" in sys.argv:
        # Les titres de section : le plan éditorial de la page.
        for m in re.finditer(r"<h([12345])[^>]*>(.*?)</h\1>", txt, flags=re.S):
            t = re.sub(r"<[^>]+>", "", m.group(2))
            t = re.sub(r"\s+", " ", t).strip()
            if t:
                print(f"  {'  ' * (int(m.group(1)) - 1)}h{m.group(1)}  {t[:88]}")
        return

    s = Squelette(prof)
    s.feed(txt)
    print("\n".join(s.lignes))


main()

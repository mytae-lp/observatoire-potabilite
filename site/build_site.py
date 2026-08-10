# -*- coding: utf-8 -*-
"""
Générateur de la vitrine publique.

    python3 site/build_site.py                 # tout le site dans site/public/
    python3 site/build_site.py --sortie /tmp/s # ailleurs

Pourquoi un site STATIQUE
-------------------------
Une ligne figée est une photographie datée : elle porte `version_referentiel`
et `calcule_le` précisément pour qu'on sache contre quelle grille elle a été
calculée. Un serveur qui rejouerait le verdict à chaque visite reproduirait, à
l'intérieur de l'outil, le défaut que l'outil dénonce — un « conforme » sans sa
date. Le site EST cette photographie ; git en garde l'historique, et comparer
deux publications montre le déplacement des seuils.

Accessoirement, un dossier de fichiers ne tombe pas en panne, ne coûte rien à
héberger, et sera encore lisible dans dix ans.

Ce que le site consomme
-----------------------
Trois tables figées, et rien d'autre (CLAUDE.md §8bis) :
    analyses_figees      un bulletin par ligne
    verdicts_figes       le détail paramètre par paramètre
    couverture_communes  le statut de chaque commune — ce que colorie la carte
Aucun verdict n'est recalculé ici.

Ce que le site ne fait pas
--------------------------
Il ne collecte rien et n'écrit rien en base : c'est le rôle de l'atelier local.
Un formulaire public qui déclencherait des appels Hub'Eau serait une charge
abusive sur un service public gratuit (§3.2), et une porte d'entrée.

Il ne recommande aucun équipement, aucune filtration, aucun produit — nulle
part, pas même en note (§2.2). Et il interroge la norme, jamais les acteurs qui
l'appliquent (§2.1).
"""
import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import sys
import unicodedata

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICI = os.path.join(RACINE, "site")
GABARITS = os.path.join(ICI, "gabarits")
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, os.path.join(RACINE, "sortie"))

from common import DB_PATH, SEUIL_COMPLET  # noqa: E402
import build_fiche as BF  # noqa: E402
import dossier_page as DP  # noqa: E402

GEOJSON = os.path.join(RACINE, "referentiel", "geo", "departements-simplifie.geojson")
REF_CSV = os.path.join(RACINE, "referentiel", "referentiel_seuils.csv")

PAGES = [("index.html", "Accueil"), ("carte.html", "Carte"),
         ("communes.html", "Communes"), ("substances.html", "Substances"),
         ("methode.html", "Méthode"), ("sources.html", "Sources & données")]


# ---------------------------------------------------------------------------
# Petits utilitaires
# ---------------------------------------------------------------------------
def h(s):
    """Échappement HTML. Les libellés viennent d'une source publique, pas d'un
    formulaire — mais un libellé de paramètre peut contenir « < » et casserait
    la page silencieusement."""
    return (str("" if s is None else s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def lire(*p):
    return open(os.path.join(GABARITS, *p), encoding="utf-8").read()


def ecrire(dest, contenu):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(contenu)
    return dest


def niveau_commune(statut, depasse, bascules, indetermines):
    """
    La couleur d'une commune sur la carte et dans les listes.

    « non documentée » a sa propre couleur, et ce n'est ni le vert ni le rouge :
    c'est une absence de donnée, pas un verdict (§8bis obligation 4). La bascule
    a la sienne aussi — c'est l'indicateur central du projet, le noyer dans
    l'ambre reviendrait à le rendre invisible.
    """
    if statut == "non_documentee":
        return "non_documentee"
    if statut == "rattachee_reseau":
        return "rattachee"
    if depasse:
        return "analysee-rouge"
    if bascules:
        return "analysee-bascule"
    if indetermines:
        return "analysee-ambre"
    return "analysee-vert"


DOT = {"analysee-rouge": "rouge", "analysee-bascule": "bascule",
       "analysee-ambre": "ambre", "analysee-vert": "vert",
       "rattachee": "vert", "non_documentee": "gris"}


# ---------------------------------------------------------------------------
# Squelette de page
# ---------------------------------------------------------------------------
# Empreinte du contenu de chaque ressource, ajoutée à son adresse. Sans elle,
# un visiteur qui a déjà consulté le site garde la feuille de style et le script
# de sa dernière visite : on republie une correction, et il continue de voir
# l'ancienne page sans que rien ne le signale. C'est la même idée que
# `version_referentiel` — une empreinte de contenu, pas un numéro qu'on pense à
# incrémenter.
EMPREINTES = {}


def empreinte(nom):
    if nom not in EMPREINTES:
        with open(os.path.join(GABARITS, nom), "rb") as fh:
            EMPREINTES[nom] = hashlib.sha256(fh.read()).hexdigest()[:8]
    return f"{nom}?v={EMPREINTES[nom]}"


def fil_ariane(fil, prefixe):
    """
    Le fil d'Ariane — accueil › département › commune › bulletin.

    Il n'est pas décoratif : le parcours du §8bis va du code postal au bulletin
    en passant par des niveaux intermédiaires, et un visiteur qui arrive sur une
    fiche par un lien direct n'a autrement aucun moyen de savoir où il est ni de
    remonter d'un cran.
    """
    if not fil:
        return ""
    bouts = []
    for i, (libelle, url) in enumerate(fil):
        dernier = i == len(fil) - 1
        if dernier or not url:
            bouts.append(f'<li aria-current="page">{h(libelle)}</li>')
        else:
            bouts.append(f'<li><a href="{prefixe}{h(url)}">{h(libelle)}</a></li>')
    return ('<nav class="fil" aria-label="Fil d\'Ariane"><div class="wrap">'
            f'<ol>{"".join(bouts)}</ol></div></nav>')


def page(titre, corps, page_courante, description, version, calcule_le,
         scripts="", sous_titre=None, formule=True, prefixe="", fil=None):
    """
    Le squelette commun. `prefixe` est le chemin de retour vers la racine —
    "" à la racine, "../" dans `commune/` et `departement/`.

    Il est passé explicitement plutôt que réparé après coup : la version
    précédente réécrivait les adresses d'une page déjà rendue par une chaîne de
    `.replace()`, une par entrée de menu. Ajouter une page au menu ou un
    sous-dossier au site demandait de penser à allonger la chaîne, sans quoi le
    lien pointait dans le vide — et rien ne l'aurait signalé.
    """
    nav = "".join(
        f'<li><a href="{prefixe}{f}"{" aria-current=\"page\"" if f == page_courante else ""}>{h(n)}</a></li>'
        for f, n in PAGES)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{h(titre)} — Observatoire de la potabilité réglementaire</title>
<meta name="description" content="{h(description)}">
<link rel="stylesheet" href="{prefixe}assets/{empreinte('observatoire.css')}">
</head>
<body>
<div class="masthead"><div class="wrap">
  <div class="eyebrow">Observatoire de la potabilité réglementaire · données ouvertes</div>
  <h1>{h(titre)}</h1>
  <p>{sous_titre or ''}</p>
  {'<div class="formule">« Ce n\'est pas l\'eau qui est devenue potable. C\'est la limite qui a bougé. »</div>' if formule else ''}
</div></div>
<nav class="nav" aria-label="Sections du site"><div class="wrap"><ul>{nav}</ul></div></nav>
{fil_ariane(fil, prefixe)}

<div class="wrap">
{corps}

<footer><div class="src">
  <strong>Sources &amp; licences.</strong> Mesures : SISE-Eaux (ministère chargé de la
  santé) via l'API Hub'Eau, sous Licence Ouverte 2.0. Référentiel de seuils, méthode
  et base : ODbL 1.0. Code : MIT. Fond de carte : contours départementaux IGN/Etalab,
  Licence Ouverte. Une réutilisation conforme aux licences n'engage pas l'Observatoire
  sur les conclusions qu'en tire le réutilisateur.
  <div class="tracab">
    <span><b>Version du référentiel :</b> {h(version)}</span>
    <span><b>Calculé le :</b> {h(calcule_le)}</span>
    <span><b>Porté par :</b> Éditions Mytae</span>
  </div>
</div></footer>
</div>
{scripts}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
def corpus(con, version):
    """
    Une ligne par commune couverte, avec ce qu'il faut pour la carte, la
    recherche et les listes. Le bulletin retenu est le plus récent du point
    d'eau le plus récemment prélevé.
    """
    return con.execute("""
        SELECT cc.code_insee, cc.commune, cc.dept, cc.codes_postaux,
               cc.lon, cc.lat, cc.statut, cc.commune_prelevement,
               cc.date_prelevement, cc.nb_parametres, cc.pct_couverture,
               a.nb_depasse_applicable, a.nb_bascules, a.nb_indetermines,
               a.classe_effort, a.depassements_pour_mille,
               a.nb_synthese_quantifiees, a.charge_synthese_ug_l,
               a.indice_danger, a.indice_danger_n, a.est_complet,
               a.nb_mesures_notees, a.nb_mesures_lues, a.nom_uge
        FROM couverture_communes cc
        LEFT JOIN analyses_figees a
               ON a.code_prelevement = cc.code_prelevement
              AND a.version_referentiel = cc.version_referentiel
        WHERE cc.version_referentiel = ?
        ORDER BY cc.commune
    """, [version]).fetchall()


def bulletins_de_la_these(con, version):
    """
    *Des bulletins complets, déclarés parfaitement conformes aujourd'hui, qui
    ne l'auraient pas été il y a dix ans.* Chaque ligne est un cas — c'est la
    requête qui porte la thèse du projet, et elle mérite d'être en page
    d'accueil plutôt qu'enfouie dans un fichier SQL.
    """
    return con.execute("""
        SELECT commune, code_insee, dept, date_prelevement, nb_bascules,
               nb_parametres, classe_effort, nb_mesures_notees, pct_couverture
        FROM analyses_figees
        WHERE version_referentiel = ?
          AND est_complet AND nb_depasse_applicable = 0 AND nb_bascules > 0
        ORDER BY nb_bascules DESC, commune
    """, [version]).fetchall()


# ---------------------------------------------------------------------------
# La carte
# ---------------------------------------------------------------------------
def projeter(lon, lat, lat0=46.6):
    """
    Projection conique très simple, suffisante à l'échelle de la France : on
    corrige la longitude par le cosinus de la latitude moyenne, sans quoi le
    pays paraît étiré d'est en ouest. Ce n'est pas un système géodésique et
    n'a pas à en être un — on positionne des points sur un fond, on ne mesure
    aucune distance.
    """
    return lon * math.cos(math.radians(lat0)), -lat


_GEO = {}


def geo_departements():
    """
    Le fond, lu une seule fois et indexé par code de département.

    L'indexation par département est ce qui permet de ne dessiner qu'un
    département sur sa propre page. Sans elle, chaque page départementale
    embarquerait les 174 Ko du fond national pour n'en montrer qu'un
    centième — mesuré le 9 août 2026 : le fond pèse 92 % de `carte.html`,
    un point de commune 203 octets. Le coût de la carte est dans le fond,
    et il est fixe.
    """
    if _GEO:
        return _GEO
    if not os.path.exists(GEOJSON):
        return _GEO
    geo = json.load(open(GEOJSON, encoding="utf-8"))
    for f in geo["features"]:
        code = str(f["properties"].get("code") or "").strip()
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        anneaux = [a for poly in polys for a in poly]
        _GEO[code] = {"nom": f["properties"].get("nom") or code, "anneaux": anneaux}
    return _GEO


def _centroide(anneau):
    """Centroïde d'un anneau fermé, formule des polygones. Sert à poser le
    nombre au milieu d'un département — la moyenne des sommets ne conviendrait
    pas, elle se déplace vers les côtes découpées, où les points abondent."""
    a = cx = cy = 0.0
    n = len(anneau)
    for i in range(n):
        x0, y0 = anneau[i]
        x1, y1 = anneau[(i + 1) % n]
        f = x0 * y1 - x1 * y0
        a += f
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    if abs(a) < 1e-12:                      # anneau dégénéré
        xs = [p[0] for p in anneau]
        ys = [p[1] for p in anneau]
        return sum(xs) / n, sum(ys) / n
    a *= 0.5
    return cx / (6 * a), cy / (6 * a)


# Les classes de couverture de la carte de France. Ce sont des PALIERS, pas une
# échelle continue : un département en porte 1 400 et un autre 1, et un dégradé
# linéaire écraserait tout le monde sauf le premier. Les paliers sont affichés
# en légende — une carte qui colorie sans dire ses seuils demande d'être crue.
PALIERS_COUVERTURE = [(200, "c4"), (50, "c3"), (10, "c2"), (1, "c1")]


def classe_couverture(n):
    for seuil, classe in PALIERS_COUVERTURE:
        if n >= seuil:
            return classe
    return "c0"


def carte_departements_svg(comptes, largeur=920, prefixe=""):
    """
    La France par département, coloriée par le **nombre d'analyses** qu'on en
    détient — et rien d'autre.

    Ce que cette carte ne montre pas, et c'est délibéré : **aucun verdict**. Un
    département n'a pas de qualité d'eau ; il a des bulletins, chacun prélevé un
    jour donné sur un point d'eau donné et noté contre la grille de ce jour-là.
    Colorier un département en vert ou en rouge fabriquerait exactement le profil
    synthétique que le §2.3 interdit. Ce qui se cumule légitimement à cette
    échelle, c'est **l'effort de connaissance** : combien d'analyses complètes
    nous détenons. C'est une mesure de ce qu'on sait, pas de ce qu'on a trouvé.

    Elle remplace la carte à points nationale, qui était illisible et le
    restait : mesuré le 9 août 2026 sur le Tarn, 53 points sur 314 (17 %)
    voyaient leur disque en recouvrir un autre, et 6 avaient leur centre caché
    sous un voisin. Le dixième centile de distance au plus proche voisin valait
    13 px pour des disques de 14 px de diamètre — réduire le rayon ne rattrapait
    rien, la densité des chefs-lieux restant la même.
    """
    geo = geo_departements()
    if not geo:
        return ('<p class="rappel">Fond de carte absent — '
                '<code>referentiel/geo/departements-simplifie.geojson</code>.</p>')

    xs, ys = [], []
    for d in geo.values():
        for anneau in d["anneaux"]:
            for lon, lat in anneau:
                x, y = projeter(lon, lat)
                xs.append(x)
                ys.append(y)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    marge = 14
    ech = (largeur - 2 * marge) / (maxx - minx)
    hauteur = (maxy - miny) * ech + 2 * marge

    def pt(lon, lat):
        x, y = projeter(lon, lat)
        return (x - minx) * ech + marge, (y - miny) * ech + marge

    zones = []
    for code, d in sorted(geo.items()):
        n = comptes.get(code, {}).get("bulletins", 0)
        nc = comptes.get(code, {}).get("communes", 0)
        traces, plus_grand, aire_max = [], None, -1.0
        for anneau in d["anneaux"]:
            trace, prev, pts = [], None, []
            for lon, lat in anneau:
                x, y = pt(lon, lat)
                pts.append((x, y))
                if prev and abs(x - prev[0]) < .5 and abs(y - prev[1]) < .5:
                    continue
                trace.append(f"{'M' if not trace else 'L'}{x:.1f},{y:.1f}")
                prev = (x, y)
            if len(trace) > 3:
                traces.append("".join(trace) + "Z")
                bx = max(p[0] for p in pts) - min(p[0] for p in pts)
                by = max(p[1] for p in pts) - min(p[1] for p in pts)
                if bx * by > aire_max:
                    aire_max, plus_grand = bx * by, (pts, bx, by)
        if not traces:
            continue

        titre = (f"{d['nom']} ({code}) — {n} analyse(s) complète(s), "
                 f"{nc} commune(s) documentée(s)" if n else
                 f"{d['nom']} ({code}) — pas encore collecté")
        forme = f'<path class="dept {classe_couverture(n)}" d="{"".join(traces)}"/>'

        # Le nombre, posé au centroïde — et seulement si le département est
        # assez grand pour l'accueillir. Un chiffre qui déborde de sa forme se
        # lit sur le voisin, et dit alors quelque chose de faux.
        etiquette = ""
        if n and plus_grand and plus_grand[1] > 26 and plus_grand[2] > 18:
            cx, cy = _centroide(plus_grand[0])
            etiquette = (f'<text class="etiq" x="{cx:.1f}" y="{cy:.1f}" '
                         f'text-anchor="middle" dominant-baseline="central">{n}</text>')

        if n:
            zones.append(f'<a class="zone" href="{prefixe}departement/{code}.html">'
                         f'<title>{h(titre)}</title>{forme}{etiquette}</a>')
        else:
            zones.append(f'<g class="zone-inerte"><title>{h(titre)}</title>{forme}</g>')

    return (f'<svg viewBox="0 0 {largeur:.0f} {hauteur:.0f}" role="img" '
            f'aria-label="Carte de France : nombre d\'analyses complètes détenues '
            f'par département">{"".join(zones)}</svg>')


def carte_svg(lignes, largeur=920, depts=None, lien_dept=None, prefixe="",
              focus=None, relier=None, rayon=5.5):
    """Fond départemental + un point par commune, en SVG produit ici même.

    Aucun serveur de tuiles n'est appelé : le visiteur ne laisse donc aucune
    trace chez un tiers en consultant la carte, et il n'y a pas de bannière de
    consentement à lui imposer.

    `depts` restreint le fond ET le cadrage à ces départements — c'est le zoom.
    Il n'y a pas d'autre zoom : le cadrage se calcule sur ce qu'on dessine, donc
    une carte du Tarn est un fond du Tarn, pas un fond de France recadré.
    Mesuré : sur une carte de France large de 926 px, le Tarn occupe 85 × 73 px,
    contre 926 × 793 sur sa propre page — environ 120 fois plus de surface pour
    y placer ses 314 communes. C'est la lisibilité qui impose ce découpage, pas
    le poids : un point ne coûte que 203 octets.

    `lien_dept` rend chaque département cliquable — c'est ce qui fait de la
    carte de France une porte d'entrée du parcours plutôt qu'une illustration.

    `focus` et `relier` servent la carte de situation d'une fiche : mettre en
    évidence la commune qu'on regarde, et **tracer le trait vers la commune où
    l'analyse a réellement été prélevée**. C'est l'obligation d'affichage n° 5
    du §8bis rendue visible au lieu d'être seulement écrite — à l'échelle, six
    communes sur dix lisent le bulletin d'une voisine, et une phrase en petits
    caractères ne suffit pas à le faire comprendre.
    """
    geo = geo_departements()
    if not geo:
        return ('<p class="rappel">Fond de carte absent — '
                '<code>referentiel/geo/departements-simplifie.geojson</code>.</p>')

    retenus = [(c, d) for c, d in sorted(geo.items())
               if depts is None or c in depts]
    if not retenus:
        return '<p class="rappel">Aucun contour départemental pour cette zone.</p>'

    xs, ys = [], []
    for _, d in retenus:
        for anneau in d["anneaux"]:
            for lon, lat in anneau:
                x, y = projeter(lon, lat)
                xs.append(x)
                ys.append(y)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    marge = 14
    ech = (largeur - 2 * marge) / max(1e-9, (maxx - minx))
    hauteur = (maxy - miny) * ech + 2 * marge

    def pt(lon, lat):
        x, y = projeter(lon, lat)
        return (x - minx) * ech + marge, (y - miny) * ech + marge

    # Décimation : à cette échelle, deux points distants de moins d'un demi-pixel
    # sont le même point. Le fichier source reste intact dans le dépôt.
    # Le seuil suit l'échelle : sur un seul département, un demi-pixel
    # représente une distance bien plus courte, donc on décime moins.
    chemins = []
    for code, d in retenus:
        traces = []
        for anneau in d["anneaux"]:
            trace, prev = [], None
            for lon, lat in anneau:
                x, y = pt(lon, lat)
                if prev and abs(x - prev[0]) < .5 and abs(y - prev[1]) < .5:
                    continue
                trace.append(f"{'M' if not trace else 'L'}{x:.1f},{y:.1f}")
                prev = (x, y)
            if len(trace) > 3:
                traces.append("".join(trace) + "Z")
        if not traces:
            continue
        forme = f'<path class="dept" d="{"".join(traces)}"/>'
        if lien_dept and lien_dept(code):
            chemins.append(
                f'<a class="zone" href="{h(lien_dept(code))}">'
                f'<title>{h(d["nom"])} ({h(code)})</title>{forme}</a>')
        else:
            chemins.append(forme)

    focus = set(focus or ())
    coord = {}
    points = []
    for c in sorted(lignes, key=lambda r: 0 if r["statut"] == "non_documentee" else 1):
        if c["lon"] is None or c["lat"] is None:
            continue
        if depts is not None and c["dept"] not in depts:
            continue
        x, y = pt(c["lon"], c["lat"])
        coord[c["code_insee"]] = (x, y)
        r = rayon if c["statut"] != "non_documentee" else rayon - 1
        vedette = c["code_insee"] in focus
        if vedette:
            r += 2.5
        titre = f"{c['commune']} ({c['dept']}) — {c['libelle_statut']}"
        points.append(
            f'<a class="pt{" vedette" if vedette else ""}" href="{prefixe}{c["url"]}" '
            f'aria-label="{h(titre)}">'
            f'<title>{h(titre)}</title>'
            f'<circle class="{c["niveau"]}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/></a>')

    # Le trait entre la commune et celle où l'analyse a été prélevée. Il n'est
    # tracé que si les deux points sont connus : une liaison approximative
    # dirait quelque chose de faux sur une carte, ce qu'une phrase absente ne
    # fait pas.
    lien = ""
    if relier and all(k in coord for k in relier):
        (x1, y1), (x2, y2) = coord[relier[0]], coord[relier[1]]
        lien = (f'<line class="emprunt" x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}"/>')

    return (f'<svg viewBox="0 0 {largeur:.0f} {hauteur:.0f}" '
            f'role="img" aria-label="Carte des communes documentées">'
            f'<g>{"".join(chemins)}</g>{lien}<g>{"".join(points)}</g></svg>')


# ---------------------------------------------------------------------------
# Les pages
# ---------------------------------------------------------------------------
def page_accueil(lignes, these, version, calcule_le, con):
    n_analysees = sum(1 for c in lignes if c["statut"] == "analysee")
    n_rattachees = sum(1 for c in lignes if c["statut"] == "rattachee_reseau")
    n_nondoc = sum(1 for c in lignes if c["statut"] == "non_documentee")
    n_bascules = sum(c["nb_bascules"] or 0 for c in lignes)
    n_depasse = sum(c["nb_depasse_applicable"] or 0 for c in lignes)
    n_bulletins = con.execute(
        "SELECT COUNT(*) FROM analyses_figees WHERE version_referentiel = ?",
        [version]).fetchone()[0]

    lignes_these = "".join(
        f"<tr><td><a href='commune/{h(t[1])}.html'>{h(t[0])}</a></td>"
        f"<td>{h(t[2])}</td><td class='num'>{h(BF._date_fr(t[3]))}</td>"
        f"<td class='num'><b style='color:var(--bascule)'>{t[4]}</b></td>"
        f"<td class='num'>{t[5]} · {h(t[6])}</td>"
        f"<td class='num'>{t[7]} ({BF._nb(t[8])} %)</td></tr>"
        for t in these)

    bloc_these = f"""
    <div class="tableau-communes">
      <table>
        <thead><tr><th>Commune</th><th>Dépt</th><th>Prélèvement</th>
          <th>Bascules</th><th>Effort de recherche</th><th>Paramètres notés</th></tr></thead>
        <tbody>{lignes_these}</tbody>
      </table>
    </div>
    <div class="rappel"><b>Comment lire ce tableau.</b> Chaque ligne est un bulletin
      complet, sans aucun dépassement à la date où il a été prélevé, et qui comporte
      pourtant au moins une mesure qui aurait dépassé la limite de 2016. L'eau n'a pas
      changé entre les deux lectures : la limite, si. L'effort de recherche est affiché
      parce qu'il conditionne tout le reste — on ne trouve que ce qu'on cherche.</div>
    """ if these else """
    <div class="rappel">Aucun bulletin du corpus actuel ne présente cette configuration.
      Ce n'est pas un résultat rassurant : c'est un corpus encore petit. La requête est
      publiée telle quelle et se remplira à mesure de la collecte.</div>
    """

    return f"""
  <div class="recherche">
    <h2>Quelle eau buvez-vous&nbsp;?</h2>
    <p style="margin:0;font-size:14px;color:var(--ink-soft)">Entrez un code postal, un
      code INSEE ou un nom de commune. La recherche se fait dans votre navigateur :
      aucune requête n'est envoyée, et ce que vous cherchez ne nous est pas transmis.</p>
    <div class="champ">
      <input id="q" type="search" inputmode="text" autocomplete="off"
             placeholder="17100, Saintes, 28068…" aria-label="Code postal, code INSEE ou nom de commune">
    </div>
    <ul class="resultats" id="resultats"></ul>
    <div class="aide">Le corpus ne couvre pas encore la France entière. Une commune
      absente n'est pas une commune dont l'eau serait bonne : c'est une commune qui
      n'a pas encore été collectée.</div>
  </div>

  <section><h3 class="sec">Le corpus, en chiffres</h3>
    <div class="chiffres">
      <div class="chiffre"><div class="n">{n_analysees + n_rattachees}</div>
        <div class="l">communes documentées<br>dont {n_rattachees} par le bulletin de leur réseau</div></div>
      <div class="chiffre"><div class="n">{n_bulletins}</div>
        <div class="l">bulletins complets analysés<br>plus de {SEUIL_COMPLET} paramètres chacun</div></div>
      <div class="chiffre bascule"><div class="n">{n_bascules}</div>
        <div class="l">bascules réglementaires<br>au-dessus de 2016, sous 2026</div></div>
      <div class="chiffre rouge"><div class="n">{n_depasse}</div>
        <div class="l">dépassements<br>à la date du prélèvement</div></div>
    </div>
    <div class="rappel"><b>Ces nombres ne se comparent pas d'une commune à l'autre.</b>
      Une commune qui fait chercher 700 paramètres a mécaniquement plus de chances d'en
      voir un dépasser qu'une commune qui en fait chercher 200 : comparer les comptes
      bruts pénalise la transparence. Les comparaisons se font sur les taux, et l'effort
      de recherche est affiché partout où elles apparaissent.
      {f"<br><br>{n_nondoc} commune(s) du corpus sont <b>non documentées</b> : aucun bulletin complet, ni pour elles ni pour leur réseau. Ce n'est ni « conforme » ni « non conforme » — c'est une absence de donnée, et elle reste visible sur la carte." if n_nondoc else ""}</div>
  </section>

  <section><h3 class="sec">La requête qui porte la thèse</h3>
    <p style="margin:0 0 12px;font-size:14px">Des bulletins <b>complets</b>, déclarés
      <b>parfaitement conformes</b> aujourd'hui, et qui ne l'auraient pas été il y a dix
      ans. C'est la démonstration matérielle du réétalonnage : ni une opinion, ni une
      estimation — une mesure, deux grilles, deux verdicts.</p>
    {bloc_these}
  </section>

  <section><h3 class="sec">Ce que cet outil est, et ce qu'il n'est pas</h3>
    <div class="prose">
      <h4>Il sépare la mesure du verdict</h4>
      <p>Une mesure est un fait physique : <i>0,092 µg/L d'ESA métolachlore, le 14 mars
        2025, à Saintes</i>. Ce fait ne change pas. Le verdict — « conforme » — est une
        convention administrative, et elle change dans le temps. La même eau, avec la
        même mesure, peut être non conforme en 2016 et conforme en 2026.</p>
      <h4>Il interroge la norme, pas les acteurs</h4>
      <p>Le sujet est la construction réglementaire du seuil. Ce n'est ni l'ARS, ni le
        distributeur, ni le maire, ni l'agriculteur. Un exploitant qui respecte une
        limite fixée par arrêté n'est pas en faute : c'est la limite qu'on examine.</p>
      <h4>Ce n'est pas un outil de prescription</h4>
      <p>Aucune recommandation de filtration, d'équipement, de traitement ou de produit
        n'y figure, et il n'y en aura jamais — pas même en note. Si vous vous interrogez
        sur votre eau, les interlocuteurs sont l'ARS de votre région, votre mairie, et
        les données publiques Orobnat.</p>
      <h4>Tout y est vérifiable</h4>
      <p>Chaque chiffre est dérivé de la base, chaque seuil porte sa source et son
        niveau de fiabilité, chaque écran porte la version de référentiel et la date de
        calcul qui l'ont produit. Les données brutes et le référentiel sont
        <a href="sources.html">téléchargeables</a>.</p>
    </div>
  </section>
"""


def comptes_departements(con, version, lignes):
    """Par département : le nombre d'analyses complètes détenues, et le nombre
    de communes documentées. Ce sont les deux seuls nombres que la carte
    nationale porte — aucun verdict ne s'y cumule."""
    par_dept = {}
    for r in con.execute("""
            SELECT dept, COUNT(*) FROM analyses_figees
            WHERE version_referentiel = ? GROUP BY dept""", [version]).fetchall():
        par_dept.setdefault(r[0], {})["bulletins"] = r[1]
    for dept, communes in par_departement(lignes).items():
        d = par_dept.setdefault(dept, {})
        d["communes"] = sum(1 for c in communes if c["statut"] != "non_documentee")
        d.setdefault("bulletins", 0)
    for d in par_dept.values():
        d.setdefault("communes", 0)
    return par_dept


def page_carte(lignes, version, calcule_le, comptes):
    svg = carte_departements_svg(comptes)
    total_b = sum(d["bulletins"] for d in comptes.values())
    total_c = sum(d["communes"] for d in comptes.values())
    n_dept = sum(1 for d in comptes.values() if d["bulletins"])

    lig = "".join(
        f"<tr><td><a href='departement/{h(code)}.html'>{h(_nom_dept(code))}</a>"
        f"<span class='grille'>département {h(code)}</span></td>"
        f"<td class='num'>{d['bulletins']}</td>"
        f"<td class='num'>{d['communes']}</td></tr>"
        for code, d in sorted(comptes.items()) if d["bulletins"])

    paliers = "".join(
        f'<span><i class="pal {classe}"></i> {libelle}</span>'
        for classe, libelle in (
            ("c1", "1 à 9 analyses"), ("c2", "10 à 49"), ("c3", "50 à 199"),
            ("c4", "200 et plus"), ("c0", "pas encore collecté")))

    return f"""
  <section style="margin-top:0">
    <div class="carte-bloc">{svg}
      <div class="carte-legende paliers">{paliers}</div>
    </div>
    <div class="rappel"><b>Cette carte ne dit rien de la qualité de l'eau, et c'est
      voulu.</b> Elle montre le <b>nombre d'analyses complètes</b> que l'Observatoire
      détient dans chaque département — autrement dit ce que l'on sait, pas ce que l'on
      a trouvé. Un département n'a pas de verdict : il a des bulletins, chacun prélevé
      un jour donné sur un point d'eau donné et noté contre la grille en vigueur ce
      jour-là. Colorier un département en vert ou en rouge reviendrait à fabriquer une
      moyenne sans date, qui ne pourrait être comparée à aucune norme.</div>
    <div class="rappel"><b>Un département foncé n'est pas un département en mauvais
      état : c'est un département bien documenté.</b> La lecture se fait donc à
      l'envers de l'habitude. Un département clair ou blanc n'a pas une eau meilleure —
      il n'a pas encore été collecté, et l'absence de donnée n'est pas une bonne
      nouvelle.</div>
    <div class="rappel"><b>Cliquez un département coloré</b> pour ouvrir sa page : la
      liste alphabétique de ses communes, ses gestionnaires déclarés, et le détail de
      chaque bulletin. Les départements non collectés ne mènent nulle part — un lien y
      serait une promesse que le corpus ne tient pas.</div>
  </section>

  <section><h3 class="sec">{n_dept} département(s) documenté(s) — {total_b} analyses, {total_c} communes</h3>
    <div class="tableau-communes">
      <table>
        <thead><tr><th>Département</th><th>Analyses complètes détenues</th>
          <th>Communes documentées</th></tr></thead>
        <tbody>{lig}</tbody>
      </table>
    </div>
    <div class="rappel">Le tableau reprend la carte pour qui ne peut pas la voir, et
      il est dans l'ordre des codes — pas dans celui des nombres. Un classement de
      départements par nombre d'analyses se lirait comme un palmarès, alors qu'il ne
      décrit que l'ordre dans lequel la collecte a eu lieu.</div>
    <div class="rappel">Le fond de carte est produit à la construction du site et
      incorporé à la page : aucune requête n'est adressée à un serveur de tuiles, donc
      aucune adresse IP de visiteur n'est transmise à un tiers. Les départements et
      collectivités d'outre-mer ne figurent pas encore sur ce fond.</div>
  </section>
"""


def par_departement(lignes):
    """Le corpus regroupé par département, dans l'ordre des codes.

    L'ordre est celui des codes, jamais celui d'un indicateur : un tableau de
    départements trié par nombre de dépassements serait un classement, et le
    §2.11 en interdit un qui n'afficherait pas l'effort de recherche de chaque
    terme. L'effort est affiché — en étendue, jamais en moyenne — et l'ordre
    reste neutre.
    """
    groupes = {}
    for c in lignes:
        groupes.setdefault(c["dept"], []).append(c)
    return dict(sorted(groupes.items()))


def _nom_dept(code):
    d = geo_departements().get(code)
    return d["nom"] if d else code


def _etendue_effort(communes):
    """De X à Y paramètres cherchés. Une étendue, pas une moyenne : une moyenne
    d'efforts de recherche n'appartient à aucun bulletin réel et se lirait comme
    une propriété du département, ce qu'elle n'est pas."""
    eff = [c["nb_parametres"] for c in communes if c["nb_parametres"]]
    if not eff:
        return "—"
    return f"{min(eff)}" if min(eff) == max(eff) else f"{min(eff)} à {max(eff)}"


def _initiale(nom):
    """Première lettre d'un nom de commune, accents rabattus. « Ébreuil » se
    range à E, et « L'Isle-sur-Tarn » à L : l'index alphabétique doit ranger
    comme un lecteur cherche, pas comme un octet se trie.

    Les **ligatures se traitent à part** : la décomposition NFD ne les défait
    pas, et « Œuf-en-Ternois » (62) se serait rangée sous une lettre « Œ » à
    elle seule, entre Z et le reste. Attrapé au contrôle, pas en production.
    """
    n = (nom or "").strip().lstrip("'’")
    for lig, rempl in (("Œ", "OE"), ("œ", "oe"), ("Æ", "AE"), ("æ", "ae")):
        n = n.replace(lig, rempl)
    n = unicodedata.normalize("NFD", n)
    n = "".join(ch for ch in n if unicodedata.category(ch) != "Mn").upper()
    return n[0] if n and n[0].isalpha() else "#"


def _ligne_commune(c, prefixe="", avec_dept=True, ancre=None):
    """Une ligne de commune, la même partout — liste nationale, page de
    département, résultat de recherche. Elle porte toujours son effort de
    recherche et son dénominateur : ce sont les obligations 1 et 2 du §8bis, et
    une ligne compacte est exactement l'endroit où l'on serait tenté de les
    laisser tomber."""
    url = f"{prefixe}commune/{c['code_insee']}.html"
    nom = (f"<a href='{url}'>{h(c['commune'])}</a>"
           if c["statut"] != "non_documentee" else h(c["commune"]))
    if c["statut"] == "non_documentee":
        detail = ("<td colspan='5' style='color:var(--gris)'>aucun bulletin complet, "
                  "ni pour la commune ni pour son réseau</td>")
    else:
        emprunt = (f"<span class='grille'>prélevé à {h(c['commune_prelevement'])}</span>"
                   if c["statut"] == "rattachee_reseau" else "")
        detail = (
            f"<td class='num'>{h(BF._date_fr(c['date_prelevement']))}{emprunt}</td>"
            f"<td class='num'>{c['nb_parametres'] or '—'}<span class='grille'>{h(c['classe_effort'] or '')}</span></td>"
            f"<td class='num'>{c['nb_mesures_notees'] or '—'} / {c['nb_mesures_lues'] or '—'}"
            f"<span class='grille'>{BF._nb(c['pct_couverture'])} % de couverture</span></td>"
            f"<td class='num'>{c['nb_depasse_applicable'] if c['nb_depasse_applicable'] is not None else '—'}"
            f"<span class='grille'>{BF._nb(c['depassements_pour_mille'])} ‰</span></td>"
            f"<td class='num'><b style='color:var(--bascule)'>{c['nb_bascules'] if c['nb_bascules'] is not None else '—'}</b></td>")
    col_dept = (f"<td><a href='{prefixe}departement/{h(c['dept'])}.html'>{h(c['dept'])}</a></td>"
                if avec_dept else "")

    # Les clés de tri et de recherche, portées par la ligne elle-même. Une
    # valeur absente vaut -1 et non 0 : « aucun dépassement » et « on ne sait
    # pas » ne doivent pas se ranger ensemble, sinon un tri décroissant par
    # dépassements présenterait les communes non documentées comme les plus
    # sûres du département (§2.4, les trois états).
    def cle(v):
        return -1 if v is None else v

    return (f"<tr{f' id=\"l-{ancre}\"' if ancre else ''} "
            f"data-niveau='{h(c['niveau'])}' data-statut='{h(c['statut'])}' "
            f"data-nom='{h((c['commune'] or '').lower())}' "
            f"data-insee='{h(c['code_insee'])}' "
            f"data-cp='{h((c['codes_postaux'] or '').replace(' ', ''))}' "
            f"data-effort='{cle(c['nb_parametres'])}' "
            f"data-couverture='{cle(c['pct_couverture'])}' "
            f"data-depassements='{cle(c['nb_depasse_applicable'])}' "
            f"data-taux='{cle(c['depassements_pour_mille'])}' "
            f"data-bascules='{cle(c['nb_bascules'])}' "
            f"data-date='{h(c['date_prelevement'] or '')}'>"
            f"<td>{nom}<span class='grille'>INSEE {h(c['code_insee'])}</span></td>"
            f"{col_dept}"
            f"<td><span class='st {h(c['statut'])}'>{h(c['libelle_statut'])}</span></td>"
            f"{detail}</tr>")


# Les cinq états, dans l'ordre où ils se lisent : ce que l'on sait, puis ce que
# l'on ne sait pas. L'ordre n'est pas anodin — mettre « non documentée » en
# dernier et en petit reviendrait à la traiter comme une note de bas de page,
# alors que c'est un état de plein droit (§8bis obligation 4).
ETATS_CARTE = [
    ("analysee-vert", "lg-vert",
     "commune analysée, aucun dépassement à la date du prélèvement"),
    ("analysee-bascule", "lg-bascule",
     "commune analysée, au moins une <b>bascule</b> : conforme aujourd'hui, "
     "pas selon la grille de 2016"),
    ("analysee-ambre", "lg-ambre",
     "commune analysée, sans dépassement, mais au moins une mesure "
     "<b>indéterminée</b> — la limite de quantification du laboratoire est "
     "au-dessus du seuil de comparaison"),
    ("analysee-rouge", "lg-rouge",
     "commune analysée, au moins un dépassement à la date du prélèvement"),
    ("rattachee", "lg-rattachee",
     "commune rattachée au réseau — l'analyse a été prélevée dans une commune "
     "voisine, sur la même eau"),
    ("non_documentee", "lg-nondoc",
     "commune <b>non documentée</b> — aucun bulletin complet, ni pour elle ni "
     "pour son réseau"),
]


def legende_carte(compte, filtrable=True):
    """
    La légende, qui est aussi le filtre.

    Deux raisons de ne pas en faire deux objets distincts. La première est de
    place : une légende de six lignes doublée d'une barre de filtres de six
    boutons dit deux fois la même chose. La seconde tient à la méthode — un
    filtre séparé se conçoit comme un réglage d'affichage, et on finit par
    proposer « masquer les non documentées » comme une commodité. Ici, masquer
    un état est un geste explicite du lecteur sur une légende qui continue d'en
    afficher le compte, barré : le nombre ne disparaît jamais de l'écran.

    Sans JavaScript, chaque bouton reste un libellé lisible et tout est affiché.
    """
    bouts = []
    for niveau, classe, texte in ETATS_CARTE:
        n = compte.get(niveau, 0)
        if not n:
            continue
        contenu = f'<i class="{classe}"></i> <span>{texte} — <b>{n}</b></span>'
        if filtrable:
            bouts.append(f'<button type="button" class="lg-btn" data-niveau="{niveau}" '
                         f'aria-pressed="true">{contenu}</button>')
        else:
            bouts.append(f"<span>{contenu}</span>")
    aide = ('<p class="lg-aide">Cliquez un état pour le retirer de la carte et du '
            'tableau. Son compte reste affiché : un état masqué n\'est pas un état '
            'qui n\'existe pas.</p>' if filtrable else "")
    return f'<div class="carte-legende">{"".join(bouts)}</div>{aide}'


RAPPEL_EFFORT = """
    <div class="rappel"><b>L'effort de recherche est dans le tableau, et il n'en sortira
      pas.</b> Le nombre de paramètres cherchés n'est pas un indicateur de qualité de
      l'eau : c'est un indicateur de transparence, et il se lit à l'envers. Une eau
      « correcte » sur 200 paramètres est une information plus faible qu'une eau
      « moyenne » sur 700 — la première n'a pas été beaucoup interrogée. C'est pourquoi
      la colonne des dépassements porte aussi un taux (‰ des paramètres notés) : seuls
      les taux se comparent d'une commune à l'autre.</div>
"""


def page_communes(lignes, version, calcule_le):
    """
    L'entrée du parcours : un département par ligne, et non plus toutes les
    communes d'un bloc.

    Mesuré le 9 août 2026 : une ligne de commune pèse environ 530 octets. À
    l'échelle visée — plusieurs milliers de communes —, la liste unique
    dépasserait 2,5 Mo d'un seul tenant, sans tri ni filtre, et personne ne la
    parcourrait. Le découpage par département n'est donc pas une commodité de
    présentation : c'est ce qui permet à chaque page de rester un fichier que
    l'on charge et que l'on lit.
    """
    groupes = par_departement(lignes)
    lig = []
    for dept, communes in groupes.items():
        n_ana = sum(1 for c in communes if c["statut"] == "analysee")
        n_rat = sum(1 for c in communes if c["statut"] == "rattachee_reseau")
        n_nd = sum(1 for c in communes if c["statut"] == "non_documentee")
        n_bas = sum(c["nb_bascules"] or 0 for c in communes)
        n_dep = sum(c["nb_depasse_applicable"] or 0 for c in communes)
        lig.append(
            f"<tr><td><a href='departement/{h(dept)}.html'>{h(_nom_dept(dept))}</a>"
            f"<span class='grille'>département {h(dept)}</span></td>"
            f"<td class='num'>{n_ana + n_rat}<span class='grille'>dont {n_rat} par le réseau</span></td>"
            f"<td class='num'>{n_nd or '—'}</td>"
            f"<td class='num'>{h(_etendue_effort(communes))}</td>"
            f"<td class='num'>{n_dep}</td>"
            f"<td class='num'><b style='color:var(--bascule)'>{n_bas}</b></td></tr>")

    return f"""
  <section style="margin-top:0">
    <div class="tableau-communes">
      <table>
        <thead><tr><th>Département</th><th>Communes documentées</th>
          <th>Non documentées</th><th>Effort de recherche</th>
          <th>Dépassements à la date</th><th>Bascules</th></tr></thead>
        <tbody>{"".join(lig)}</tbody>
      </table>
    </div>
    <div class="rappel"><b>Un département n'a pas de verdict, et ce tableau n'en donne
      pas.</b> Les nombres d'une ligne sont des <b>sommes de bulletins</b> — chacun
      prélevé un jour donné, sur un point d'eau donné, et noté contre la grille en
      vigueur ce jour-là. Ils ne décrivent pas « l'eau du département » : cet objet
      n'existe pas, il n'a pas de date, et il ne pourrait donc être noté contre aucune
      grille. Les lignes sont dans l'ordre des codes, pas dans celui d'un indicateur :
      un classement de départements demanderait, en plus de l'effort de recherche, que
      chacun ait été collecté avec la même profondeur — ce qui n'est pas le cas.</div>
    <div class="rappel">L'<b>effort de recherche</b> est donné en étendue — « de 234 à
      627 paramètres » — et jamais en moyenne. Une moyenne d'efforts n'appartient à
      aucun bulletin réel, et se lirait comme une propriété du territoire.</div>
  </section>
"""


def bloc_arretes(dept, nom_dept):
    """
    Les arrêtés préfectoraux — la section qui vient en premier, et qui est
    vide.

    Elle est écrite avant d'avoir les données, et elle le dit. Deux raisons de
    ne pas attendre. La première tient à la méthode : le projet distingue
    partout « il n'y a rien » de « nous ne savons pas » (§2.4), et une page qui
    tairait l'existence de ces actes laisserait croire qu'un bulletin conforme
    est toute l'histoire. La seconde est que **la partie réglementaire de cette
    section, elle, est déjà établie et sourcée** : ce que le préfet peut
    décider, pour combien de temps, et ce qu'il doit faire savoir. Seuls les
    actes de CE département manquent.

    Ce qu'il faut savoir avant de vouloir les collecter : **ils ne sont pas
    dans Hub'Eau**. Le contrôle sanitaire publie des mesures, pas des décisions.
    Les arrêtés vivent au recueil des actes administratifs de la préfecture, en
    PDF, sans format commun d'un département à l'autre — c'est une collecte
    d'une autre nature que celle de SISE-Eaux, et elle ne se fera pas par la
    même mécanique.
    """
    return f"""
  <section><h3 class="sec">Arrêtés préfectoraux — {h(nom_dept)}</h3>
    <div class="bandeau nonredige">
      <span class="ic">◻</span>
      <div><b>L'Observatoire ne détient pas encore ces actes pour ce département.</b>
        Cette section est vide, et elle le restera tant qu'ils n'auront pas été
        collectés. Une section absente aurait laissé croire qu'il n'y a rien à
        savoir ; il y a quelque chose à savoir, et nous ne l'avons pas encore.</div>
    </div>
    <div class="prose">
      <h4>Ce qu'un arrêté préfectoral peut décider sur l'eau</h4>
      <p>Un dépassement de limite de qualité n'aboutit pas seulement à une mention sur
        un bulletin. Il ouvre une procédure, et cette procédure produit des actes
        écrits qui ne figurent nulle part dans les données d'analyse.</p>
      <table><thead><tr><th>Article</th><th>Ce que le texte prévoit</th></tr></thead><tbody>
        <tr><td><code>R1321-26</code></td><td>Tout dépassement d'une limite de qualité est <b>signalé immédiatement au maire et à l'agence régionale de santé</b>, et une enquête est menée.</td></tr>
        <tr><td><code>R1321-27</code></td><td>La personne responsable de la distribution prend <b>« le plus rapidement possible les mesures correctives nécessaires »</b>, quelle qu'en soit la cause.</td></tr>
        <tr><td><code>R1321-29</code></td><td>Le préfet peut <b>« restreindre, voire interrompre la distribution »</b> lorsqu'un risque sanitaire est avéré.</td></tr>
        <tr><td><code>R1321-30</code></td><td><b>« Les consommateurs en sont informés immédiatement »</b> — sur le danger potentiel, les mesures engagées, et les conseils relatifs aux conditions de consommation.</td></tr>
        <tr><td><code>R1321-31</code></td><td>Si les mesures correctives n'ont pas suffi, une <b>dérogation</b> peut être demandée au préfet. Sa durée <b>ne peut excéder trois ans</b>.</td></tr>
        <tr><td><code>R1321-33</code></td><td>Une <b>seconde</b> dérogation de trois ans au maximum, « dans des circonstances exceptionnelles ».</td></tr>
        <tr><td><code>R1321-34</code></td><td><b>Abrogé</b> — la possibilité d'une troisième dérogation a été supprimée.</td></tr>
        <tr><td><code>R1321-35</code></td><td>Un <b>bilan</b> est obligatoire à l'issue de chaque période dérogatoire.</td></tr>
      </tbody></table>
      <p>Autrement dit : <b>une eau peut légalement rester au-dessus d'une limite
        pendant six ans au maximum</b>, sur décision écrite, motivée et bornée. C'est
        le pendant exact de ce que cet observatoire documente par ailleurs — la limite
        se déplace dans le temps, et l'eau peut aussi être autorisée à rester
        au-dessus d'elle pour une durée fixée.</p>

      <h4>Pourquoi ces actes ne sont pas dans nos données</h4>
      <p>Le contrôle sanitaire publie des <b>mesures</b> ; il ne publie pas les
        <b>décisions</b> prises à leur suite. Les arrêtés préfectoraux paraissent au
        recueil des actes administratifs de chaque préfecture, en PDF, sans format
        commun d'un département à l'autre. Les collecter est un travail d'une autre
        nature que l'interrogation d'une base d'analyses, et il reste à faire.</p>
      <p><b>Conséquence à garder en tête en lisant les pages qui suivent :</b> un
        bulletin déclaré conforme peut l'être au regard de la limite ordinaire, ou au
        regard d'une dérogation qui l'a temporairement déplacée pour cette commune-là.
        <b>Nous ne pouvons pas distinguer les deux</b>, et aucun chiffre de ce site ne
        prétend le faire. La question se pose à l'agence régionale de santé et à la
        préfecture, dont c'est l'information.</p>
    </div>
  </section>
"""


def page_departement(dept, communes, version, calcule_le):
    """
    Le niveau qui manquait entre la carte de France et la fiche d'une commune.

    Il porte trois choses qu'aucun autre écran ne peut porter : le département
    vu de près — donc lisible —, la liste de ses communes avec leurs trous, et
    les gestionnaires qui y sont déclarés. C'est aussi le seul endroit où les
    communes **non documentées** d'un territoire apparaissent ensemble : à
    l'échelle nationale elles se perdent, et leur nombre est précisément ce
    qu'un observatoire doit rendre visible.
    """
    n_ana = sum(1 for c in communes if c["statut"] == "analysee")
    n_rat = sum(1 for c in communes if c["statut"] == "rattachee_reseau")
    n_nd = sum(1 for c in communes if c["statut"] == "non_documentee")
    n_bas = sum(c["nb_bascules"] or 0 for c in communes)
    n_dep = sum(c["nb_depasse_applicable"] or 0 for c in communes)
    nom_dept = _nom_dept(dept)

    # Un code postal réel du département, pour que l'exemple du champ de
    # recherche soit un code qu'on peut effectivement taper ici.
    exemple_cp = next((cp for c in communes
                       for cp in (c["codes_postaux"] or "").replace(" ", "").split(",")
                       if cp), f"{dept}000")

    # La carte à points est passée en second et agrandie. Mesuré le 9 août 2026
    # sur ce même département : à 760 de large et 7 de rayon, 53 points sur 314
    # voyaient leur disque en recouvrir un autre et 6 disparaissaient sous un
    # voisin. À 1200 de large les distances augmentent de moitié, et un rayon de
    # 4 rend le recouvrement rare — mais le point d'entrée reste la liste, qui
    # ne souffre d'aucune densité.
    svg = carte_svg(communes, largeur=1200, depts={dept}, prefixe="../", rayon=4)
    n = {k: sum(1 for c in communes if c["niveau"] == k) for k in DOT}

    # Les gestionnaires déclarés par la source. `nom_uge` est le nom du
    # gestionnaire, pas celui de l'unité de distribution : deux communes qui
    # partagent un gestionnaire ne boivent pas nécessairement la même eau. Le
    # bloc le dit plutôt que de laisser le regroupement le suggérer.
    uge = {}
    for c in communes:
        if c["statut"] == "non_documentee" or not c["nom_uge"]:
            continue
        uge.setdefault(c["nom_uge"], []).append(c)
    bloc_uge = ""
    if uge:
        items = "".join(
            f"<li><b>{h(nom)}</b> — {len(cs)} commune(s) : "
            + ", ".join(f"<a href='../commune/{h(c['code_insee'])}.html'>{h(c['commune'])}</a>"
                        for c in sorted(cs, key=lambda x: x["commune"]))
            + f"<span class='grille'>effort de recherche : {h(_etendue_effort(cs))} paramètres</span></li>"
            for nom, cs in sorted(uge.items()))
        bloc_uge = f"""
  <section><h3 class="sec">Les gestionnaires déclarés — {len(uge)}</h3>
    <div class="prose"><ul>{items}</ul></div>
    <div class="rappel"><b>Ce regroupement est celui du gestionnaire, pas celui de
      l'eau.</b> Le champ utilisé est le nom d'exploitant déclaré avec le bulletin par
      la source : deux communes qui y figurent ensemble sont gérées par la même entité,
      ce qui ne veut pas dire qu'elles sont alimentées par le même captage ni par la
      même usine. Le lien entre un captage et une commune n'est pas exposé par les
      données publiques — il figure parmi ce que l'outil ne sait pas encore faire.</div>
  </section>
"""

    # La liste alphabétique, avec son index de lettres. C'est le point d'entrée
    # de la page : sur 314 communes, on cherche la sienne par son nom, pas en
    # promenant le curseur sur une carte.
    triees = sorted(communes, key=lambda x: (_initiale(x["commune"]), x["commune"]))
    lig, vues = [], []
    for c in triees:
        i = _initiale(c["commune"])
        neuve = i not in vues
        if neuve:
            vues.append(i)
        lig.append(_ligne_commune(c, prefixe="../", avec_dept=False,
                                  ancre=i if neuve else None))
    index = "".join(f'<a href="#l-{h(i)}">{h(i)}</a>' for i in vues)

    return f"""
  <section style="margin-top:0">
    <div class="chiffres">
      <div class="chiffre"><div class="n">{n_ana + n_rat}</div>
        <div class="l">communes documentées<br>dont {n_rat} par le bulletin de leur réseau</div></div>
      <div class="chiffre"><div class="n">{n_nd}</div>
        <div class="l">communes non documentées<br>ni bulletin propre, ni bulletin de réseau</div></div>
      <div class="chiffre bascule"><div class="n">{n_bas}</div>
        <div class="l">bascules réglementaires<br>au-dessus de 2016, sous 2026</div></div>
      <div class="chiffre rouge"><div class="n">{n_dep}</div>
        <div class="l">dépassements<br>à la date du prélèvement</div></div>
    </div>
  </section>

  {bloc_arretes(dept, nom_dept)}

  <section><h3 class="sec">Où se concentre ce que l'on sait</h3>
    <div class="carte-bloc">{svg}
      {legende_carte(n)}
    </div>
    <div class="rappel"><b>Ce que la carte colorie n'est pas la qualité de l'eau</b>, mais
      ce que l'on sait de l'eau de chaque commune, et contre quelle grille on l'a noté.
      Une commune grise n'est ni conforme ni non conforme : elle n'a pas encore été
      collectée, ou aucun bulletin complet n'existe pour elle ni pour son réseau.</div>
    <div class="rappel">Les communes se pressent autour des chefs-lieux : à cette
      densité, des points voisins se touchent. <b>Pour retrouver une commune précise,
      la recherche ci-dessous est exacte</b> — la carte sert à voir où porte l'effort
      de connaissance, pas à pointer un nom.</div>
  </section>

  <section><h3 class="sec">Trouver votre commune</h3>
    <div class="recherche-dept">
      <input id="q-dept" type="search" inputmode="text" autocomplete="off"
             placeholder="Nom de commune ou code postal — {h(exemple_cp)}"
             aria-label="Chercher une commune par son nom ou son code postal"
             aria-controls="tbl-communes">
      <p class="lg-aide" id="q-etat" role="status" aria-live="polite"></p>
    </div>
    <div class="rappel">La recherche se fait <b>dans votre navigateur</b> : rien n'est
      envoyé, et ce que vous cherchez ne nous est pas transmis. Sans JavaScript, le
      champ reste inerte et la liste complète s'affiche — la page ne dépend pas de lui
      pour être lisible.</div>
  </section>

  <section><h3 class="sec">Les {len(communes)} communes, par ordre alphabétique</h3>
    <nav class="index-alpha" id="index-alpha" aria-label="Aller à une lettre">{index}</nav>
    <div class="tableau-communes">
      <table id="tbl-communes">
        <thead><tr>
          <th aria-sort="ascending" data-tri="nom" data-type="texte">Commune</th>
          <th>Statut</th>
          <th data-tri="date" data-type="texte">Prélèvement</th>
          <th data-tri="effort" data-type="nombre">Effort de recherche</th>
          <th data-tri="couverture" data-type="nombre">Paramètres notés</th>
          <th data-tri="depassements" data-type="nombre">Dépassements à la date</th>
          <th data-tri="bascules" data-type="nombre">Bascules</th>
        </tr></thead>
        <tbody>{"".join(lig)}</tbody>
      </table>
    </div>
    <div class="rappel"><b>Les colonnes chiffrées se trient</b>, par un clic sur leur
      titre, dans un sens puis dans l'autre. Un tri décroissant par dépassements met en
      tête les communes où une mesure a franchi le seuil applicable le jour du
      prélèvement — <b>et non les plus mal loties</b> : une commune qui a fait chercher
      627 paramètres a mécaniquement plus d'occasions d'en voir un dépasser qu'une
      commune qui en a cherché 234. C'est pourquoi la colonne de l'effort de recherche
      reste à côté, et pourquoi le taux (‰) accompagne le compte.</div>
    <div class="rappel"><b>Les communes non documentées se rangent à part, jamais en
      tête d'un tri.</b> Elles n'ont pas « zéro dépassement » : elles n'ont pas de
      valeur du tout, et les faire passer pour les plus sûres du département serait
      l'erreur exacte que le troisième état sert à éviter.</div>
    {RAPPEL_EFFORT}
  </section>

  {bloc_uge}
"""


def page_substances(con, version, substances):
    """
    L'index des dossiers de substance.

    Il ne recopie rien des pages : il donne, pour chacune, la date à laquelle
    la règle a bougé et le nombre d'analyses que ce déplacement fait basculer.
    Le reste se lit sur la page.
    """
    if not substances:
        return """
  <section style="margin-top:0"><div class="prose">
    <p>Aucun dossier de substance n'est encore publié.</p>
  </div></section>"""

    lignes = []
    for slug, libelle, origine in substances:
        s = DP.seuil(con, libelle, version)
        c = DP.chiffres(con, libelle, version)
        deplacement = (f"{h(BF._nb(s[2]))} → {h(BF._nb(s[3]))} {h(s[1] or '')}"
                       if s and s[2] is not None and s[3] is not None else "—")
        date = h(BF._date_fr(s[4])) if s and s[4] else "sans date au référentiel"
        marque = ('<span class="pill">à relire</span>' if origine == "propose" else "")
        lignes.append(
            f'<tr><td><a href="substance/{h(slug)}.html">{h(libelle)}</a> {marque}</td>'
            f'<td>{deplacement}</td><td>{date}</td>'
            f'<td class="num">{c["bascules"]}</td>'
            f'<td class="num">{c["communes_bascule"]}</td>'
            f'<td class="num">{c["mesures"]}</td></tr>')

    return f"""
  <section style="margin-top:0"><div class="prose">
    <p>Une fiche communale répond à « qu'y a-t-il dans mon eau ? ». Ces pages-ci
      répondent à une autre question : <b>qu'est-ce que cette substance démontre ?</b>
      Une molécule, une date de reclassement, et deux verdicts opposés pour un même
      résultat — c'est là que le déplacement des seuils se voit le mieux.</p>
    <p class="bnote">Le nombre d'analyses porté par une substance ne se lit jamais seul :
      une substance n'est présente que dans les bulletins qui la cherchent, et la
      colonne « analyses » donne ce dénominateur. Une comparaison entre deux
      substances n'aurait pas de sens ici — elles ne sont pas cherchées dans les
      mêmes bulletins.</p>
  </div></section>

  <section><h3 class="sec">Les dossiers publiés</h3>
    <table><thead><tr>
      <th>Substance</th><th>Déplacement de la valeur</th><th>Applicable depuis</th>
      <th class="num">Analyses basculées</th><th class="num">Communes</th>
      <th class="num">Analyses</th>
    </tr></thead><tbody>{''.join(lignes)}</tbody></table>
    <p class="bnote">« Analyses basculées » : des mesures qui dépassaient la valeur
      applicable avant le reclassement et ne dépassent pas celle d'après. La mesure
      n'a pas changé — la règle, si.</p>
  </section>"""


def page_methode(con, version, calcule_le):
    sans_date = con.execute(
        "SELECT libelle, seuil_2016, seuil_2026 FROM v_seuils_sans_date ORDER BY libelle"
    ).fetchall() if _vue_existe(con, "v_seuils_sans_date") else []
    lignes_sd = "".join(f"<li>{h(s[0])} — {BF._nb(s[1])} → {BF._nb(s[2])}</li>"
                        for s in sans_date)

    return f"""
  <section style="margin-top:0"><div class="prose">
    <h4>La thèse : le réétalonnage réglementaire daté</h4>
    <p>Le projet sépare <b>la mesure</b> du <b>verdict</b>. Une mesure est un fait
      physique ; un verdict est une convention administrative, et cette convention se
      déplace. L'objet de l'outil est de rendre ce déplacement visible et vérifiable.</p>
    <p>Chaque mesure est donc notée trois fois :</p>
    <table><thead><tr><th>Grille</th><th>Question posée</th></tr></thead><tbody>
      <tr><td>2016</td><td>Cette eau aurait-elle été potable selon la norme d'il y a dix ans ?</td></tr>
      <tr><td>2026</td><td>Est-elle potable selon la norme en vigueur aujourd'hui ?</td></tr>
      <tr><td>stricte</td><td>Serait-elle potable selon la norme la plus protectrice au monde ?</td></tr>
    </tbody></table>
    <p>L'indicateur central est la <b>bascule</b> : une mesure au-dessus de la limite de
      2016 et sous celle de 2026. Un bulletin déclaré conforme et comportant des
      bascules est la démonstration matérielle du réétalonnage.</p>

    <h4>Seuls les bulletins complets comptent</h4>
    <p>Le contrôle sanitaire produit deux choses très différentes : beaucoup d'analyses
      de <b>routine</b> (20 à 30 paramètres — bactériologie, pH, nitrates, chlore) et
      très peu d'analyses <b>complètes</b> (200 à 700 paramètres, avec les pesticides,
      les métabolites, les PFAS, les métaux, les solvants). Mélanger les deux produit
      mécaniquement un résultat rassurant : les milliers de mesures de routine, toutes
      conformes, noient les rares mesures qui portent l'information.</p>
    <p>Le seuil retenu est de <b>{SEUIL_COMPLET} paramètres</b> sur un même prélèvement.
      Il n'arbitre rien : sur 964 prélèvements réels mesurés, la routine s'éteint vers
      100, les analyses complètes commencent à 236, et la tranche 150-199 est
      totalement vide.</p>
    <p>L'unité d'analyse est <b>un prélèvement</b> — un point d'eau, une date, dans son
      intégralité. Jamais une composition de « dernières valeurs connues » : cet objet
      n'existe pas, n'a pas de date, et ne peut donc être noté contre aucune grille datée.</p>

    <h4>L'effort de recherche se déclare</h4>
    <p>On ne trouve que ce qu'on cherche. Le nombre de paramètres recherchés n'est pas
      un indicateur de la qualité de l'eau : c'est un indicateur de l'<b>effort de
      recherche</b>, donc de transparence, et il se lit à l'envers. Comparer les nombres
      bruts de dépassements de deux communes qui n'ont pas cherché la même chose est un
      contresens, et cela pénalise celle qui a cherché davantage.</p>
    <p>D'où la règle : <b>aucune comparaison entre communes, aucun classement, sans
      afficher l'effort de recherche de chacune</b>, et des taux plutôt que des comptes.</p>

    <h4>Zéro n'est pas zéro : il y a trois états, pas deux</h4>
    <p>Dans les données SISE-Eaux, une valeur affichée <code>0</code> ou <code>&lt;
      0,01</code> signifie « inférieur au seuil de quantification du laboratoire », pas
      « absent ». C'est une limite de l'instrument, pas une propriété de l'eau.</p>
    <ul>
      <li><b>Conforme</b> — quantifié, sous le seuil.</li>
      <li><b>Dépassement</b> — quantifié, au-dessus du seuil.</li>
      <li><b>Indéterminé</b> — la limite de quantification du laboratoire est au-dessus
        du seuil de comparaison. On ne peut pas dire que l'eau respecte le seuil ; on
        peut seulement dire qu'on ne sait pas.</li>
    </ul>
    <p>Un indéterminé n'est jamais présenté comme un conforme. C'est l'erreur la plus
      facile à commettre et la plus dommageable.</p>

    <h4>Un verdict se rend à la date du prélèvement</h4>
    <p>Un reclassement n'est pas rétroactif. La note d'information de la délégation
      départementale de Charente-Maritime du 10 juin 2024 est formelle :</p>
    <blockquote>« Il n'y a pas de rétroactivité possible. C'est pourquoi l'expression des
      non-conformités mises en évidence avant le 29/04/2024 est maintenue. »</blockquote>
    <p>Une mesure de chlorothalonil R471811 à 0,5 µg/L prélevée en 2023 <b>est</b> une
      non-conformité, et elle le reste. La même valeur prélevée en 2025 est conforme.
      C'est la thèse du projet, écrite noir sur blanc par l'administration elle-même —
      et c'est pourquoi le seuil affiché sur chaque ligne de bulletin est celui qui
      s'appliquait <b>ce jour-là</b>, pas celui d'aujourd'hui.</p>

    <h4>Un seuil sans sa date d'applicabilité est faux</h4>
    <p>La directive (UE) 2020/2184 comporte des valeurs à application différée. Le plomb
      passe à 5 µg/L au <b>1<sup>er</sup> janvier 2036</b>, le chrome total à 25 µg/L à
      la même date ; aujourd'hui les limites applicables sont 10 et 50 µg/L. Une base qui
      inscrirait 5 µg/L comme seuil actuel produirait de faux dépassements.</p>
    {f"<p>Six lignes du référentiel portent un seuil qui a bougé sans qu'on sache exactement quand. Elles produisent un verdict potentiellement anachronique, et elles sont listées ici plutôt que tues :</p><ul>{lignes_sd}</ul>" if lignes_sd else ""}

    <h4>Toute affirmation chiffrée est sourcée, ou marquée</h4>
    <p>Chaque ligne du référentiel porte ses sources et un niveau de fiabilité :
      <code>verifie</code> (valeur lue dans un texte réglementaire ou une source primaire
      identifiée) ou <code>a_verifier</code> (valeur plausible, non confirmée sur source
      primaire). Une valeur <code>a_verifier</code> est signalée comme telle partout où
      elle apparaît, y compris ligne à ligne dans les bulletins.</p>
    <p>Une source doit couvrir <b>ce</b> paramètre précisément. Une source qui porte sur
      la substance d'à côté n'est pas une source : c'est ainsi qu'une erreur réelle s'est
      glissée dans ce projet — le chlorothalonil R417888 porté à 0,9 µg/L par analogie
      avec le R471811, alors que le même avis de l'ANSES conclut à 0,1 µg/L pour l'un et
      0,9 pour l'autre. L'erreur a été corrigée et elle est documentée.</p>

    <h4>L'effet cocktail, et pourquoi il reste encadré</h4>
    <p>La réglementation note substance par substance ; le corps boit le mélange. Le
      projet publie trois indicateurs de cumul, du plus solide au plus fragile : le
      dénombrement des substances de synthèse quantifiées, la charge massique cumulée,
      et un <b>indice de danger</b> par méthode simplifiée.</p>
    <p>Cet indice n'est <b>jamais nommé « risque »</b>, n'est jamais publié sans le nombre
      de substances qui le composent, et n'est jamais présenté comme un verdict de
      potabilité. Tant que les cadres de référence internationaux ne sont pas implémentés,
      il sert à classer des bulletins entre eux, pas à estimer un risque sanitaire.</p>

    <h4>Ce que l'outil ne sait pas encore faire</h4>
    <ul>
      <li><b>Les seuils dépendant de la ressource.</b> Le sélénium et le bore admettent
        des exceptions d'origine géologique. Rien dans les données ne dit si la condition
        est remplie : entre les deux valeurs, le résultat est déclaré indéterminé plutôt
        que non conforme.</li>
      <li><b>La dilution.</b> Si un réseau est alimenté par trois captages et qu'un seul
        est très dégradé, le mélange peut respecter la limite sans qu'aucune action n'ait
        été menée sur la pollution. Le lien captage → usine n'est pas exposé par les
        données publiques ; il ne pourra être établi que par inférence géographique, et
        devra alors être affiché comme une hypothèse.</li>
      <li><b>Le volet radiologique</b> et les <b>eaux embouteillées</b> : présents au
        référentiel ou en repères, non travaillés analytiquement.</li>
      <li><b>La couverture géographique.</b> Le moteur est prêt pour le département ; le
        corpus publié ici est encore restreint.</li>
    </ul>
  </div></section>
"""


def page_sources(con, version, calcule_le, exports):
    ref = list(csv.DictReader(open(REF_CSV, encoding="utf-8-sig"), delimiter=";"))
    a_verifier = [r for r in ref if (r.get("fiabilite") or "").strip() != "verifie"]

    def cell(r, k):
        return h((r.get(k) or "").strip() or "—")

    lignes = "".join(
        f"<tr><td>{cell(r,'libelle')}<span class='grille'>{cell(r,'famille')}</span></td>"
        f"<td class='num'>{cell(r,'seuil_2016')}</td>"
        f"<td class='num'>{cell(r,'seuil_2026')}</td>"
        f"<td class='num'>{cell(r,'seuil_strict')}</td>"
        f"<td class='num'>{cell(r,'unite')}</td>"
        f"<td>{cell(r,'sources')}</td>"
        f"<td>{'<span class=\"etat ind\">à vérifier</span>' if (r.get('fiabilite') or '').strip() != 'verifie' else '<span class=\"etat ok\">vérifié</span>'}</td></tr>"
        for r in sorted(ref, key=lambda x: ((x.get("famille") or ""), (x.get("libelle") or ""))))

    liste_exports = "".join(
        f"<li><a href='donnees/{h(f)}'>{h(f)}</a> — {h(d)} ({t} Ko)</li>"
        for f, d, t in exports)

    return f"""
  <section style="margin-top:0"><div class="prose">
    <h4>D'où viennent les données</h4>
    <p>Les mesures proviennent de <b>SISE-Eaux</b>, la base du contrôle sanitaire du
      ministère chargé de la santé, consultée via l'API publique <b>Hub'Eau</b>, sous
      Licence Ouverte 2.0. Elles ne sont ni retraitées ni corrigées : une mesure est un
      fait, elle est stockée telle qu'elle est publiée, avec sa limite de quantification
      quand la valeur n'est pas quantifiée.</p>
    <p>Le travail propre au projet est ailleurs : c'est le <b>référentiel daté de
      seuils</b>, la méthode, et le code. Le référentiel est un fichier CSV versionné,
      jamais recopié en dur dans un script — le sujet du projet étant la dérive des
      seuils dans le temps, git fournit ainsi ce qui manque partout ailleurs : un
      journal daté et attribué de chaque modification de seuil.</p>
    <p>Le fond de carte reprend les contours départementaux publiés par l'IGN via
      Etalab, sous Licence Ouverte.</p>

    <h4>Télécharger</h4>
    <ul>{liste_exports}</ul>
    <p>Les fichiers portent la version de référentiel <code>{h(version)}</code> et la
      date de calcul <code>{h(calcule_le)}</code>. Refiger après modification du
      référentiel produit une nouvelle version : les deux coexistent, et leur comparaison
      est la trace du déplacement.</p>

    <h4>Licences</h4>
    <ul>
      <li><b>Données brutes</b> (Hub'Eau / SISE-Eaux) : Licence Ouverte 2.0.</li>
      <li><b>Référentiel de seuils et base du projet</b> : ODbL 1.0 — partage à
        l'identique, mention de la source.</li>
      <li><b>Code</b> : MIT. <b>Documents et méthode</b> : CC BY-SA 4.0.</li>
    </ul>
    <p>Toute réutilisation doit mentionner l'Observatoire <b>sans le faire endosser</b>
      ses propres conclusions : la mention de source n'est pas une caution.</p>

    <h4>Le référentiel de seuils</h4>
    <p>{len(ref)} paramètres décrits à la main, dont <b>{len(a_verifier)}</b> encore en
      fiabilité « à vérifier ». Les autres paramètres d'un bulletin sont notés soit par
      une règle de famille écrite et auditable, soit par la limite que la source déclare
      avec la mesure — et une limite seulement déclarée ne peut jamais produire une
      bascule ni un verdict 2016 : on ne fabrique pas de passé réglementaire à partir de
      la grille du jour.</p>
  </div></section>

  <section><h3 class="sec">Référentiel — {len(ref)} paramètres</h3>
    <div class="tableau-communes">
      <table>
        <thead><tr><th>Paramètre</th><th>Seuil 2016</th><th>Seuil 2026</th>
          <th>Seuil strict</th><th>Unité</th><th>Sources</th><th>Fiabilité</th></tr></thead>
        <tbody>{lignes}</tbody>
      </table>
    </div>
  </section>
"""


def _vue_existe(con, nom):
    return bool(con.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = ?", [nom]).fetchone())


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
def exporter(con, version, dossier):
    """Les données du site, réutilisables telles quelles. Un observatoire qui
    ne rend pas ses données interrogeables se demande d'être cru sur parole."""
    os.makedirs(dossier, exist_ok=True)
    produits = []

    def dump(nom, requete, description):
        rows = con.execute(requete, [version]).fetchall()
        cols = [d[0] for d in con.description]
        chemin = os.path.join(dossier, nom)
        with open(chemin, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(cols)
            w.writerows(rows)
        produits.append((nom, description, max(1, round(os.path.getsize(chemin) / 1024))))

    dump("bulletins.csv",
         "SELECT * FROM analyses_figees WHERE version_referentiel = ? ORDER BY commune, date_prelevement",
         "un bulletin par ligne : verdicts, couverture, effort de recherche, sommes")
    dump("verdicts.csv",
         "SELECT * FROM verdicts_figes WHERE version_referentiel = ? ORDER BY code_prelevement, libelle_parametre",
         "le détail paramètre par paramètre, avec le seuil applicable à la date")
    dump("couverture_communes.csv",
         "SELECT * FROM couverture_communes WHERE version_referentiel = ? ORDER BY commune",
         "le statut de chaque commune, dont les non documentées")
    # La base du barème de finesse analytique (chantier C4). Les fiches
    # affirment « dix fois moins fin que la plus basse relevée » : la table qui
    # le dit doit être téléchargeable, sinon l'affirmation demande d'être crue
    # sur parole — et elle se déplacera avec le corpus.
    dump("lq_corpus.csv",
         "SELECT * FROM lq_corpus WHERE version_referentiel = ? ORDER BY libelle_parametre",
         "l'étendue des limites de quantification observées, paramètre par paramètre")

    shutil.copyfile(REF_CSV, os.path.join(dossier, "referentiel_seuils.csv"))
    produits.append(("referentiel_seuils.csv", "le référentiel daté de seuils, source de vérité du projet",
                     max(1, round(os.path.getsize(REF_CSV) / 1024))))
    return produits


# ---------------------------------------------------------------------------
def construire(destination=None, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : python3 src/build_db.py")
        sys.exit(1)

    public = destination or os.path.join(ICI, "public")
    con = duckdb.connect(db, read_only=True)
    try:
        # La grille publiée est celle que le référentiel produit AUJOURD'HUI,
        # pas la dernière calculée : deux versions figées le même jour ne se
        # départagent pas par une date.
        version, calcule_le = BF.version_a_publier(con)
        if not version:
            print("aucune analyse figée en base — lance d'abord src/observer.py")
            sys.exit(1)

        # --- le corpus, une ligne par commune -----------------------------
        cols = ["code_insee", "commune", "dept", "codes_postaux", "lon", "lat",
                "statut", "commune_prelevement", "date_prelevement", "nb_parametres",
                "pct_couverture", "nb_depasse_applicable", "nb_bascules",
                "nb_indetermines", "classe_effort", "depassements_pour_mille",
                "nb_synthese_quantifiees", "charge_synthese_ug_l", "indice_danger",
                "indice_danger_n", "est_complet", "nb_mesures_notees",
                "nb_mesures_lues", "nom_uge"]
        lignes = []
        for r in corpus(con, version):
            c = dict(zip(cols, r))
            c["niveau"] = niveau_commune(c["statut"], c["nb_depasse_applicable"],
                                         c["nb_bascules"], c["nb_indetermines"])
            c["dot"] = DOT[c["niveau"]]
            c["libelle_statut"] = {"analysee": "analysée",
                                   "rattachee_reseau": "rattachée au réseau",
                                   "non_documentee": "non documentée"}[c["statut"]]
            c["url"] = ("commune/" + c["code_insee"] + ".html"
                        if c["statut"] != "non_documentee" else "communes.html")
            lignes.append(c)

        these = bulletins_de_la_these(con, version)
        comptes = comptes_departements(con, version, lignes)

        # --- exports ------------------------------------------------------
        exports = exporter(con, version, os.path.join(public, "donnees"))

        # --- pages --------------------------------------------------------
        assets = os.path.join(public, "assets")
        os.makedirs(assets, exist_ok=True)
        for f in ("observatoire.css", "fiche.js", "recherche.js", "carte.js",
                  "tableau.js"):
            shutil.copyfile(os.path.join(GABARITS, f), os.path.join(assets, f))

        ecrire(os.path.join(public, "index.html"), page(
            "Quelle eau buvez-vous ?",
            page_accueil(lignes, these, version, calcule_le, con),
            "index.html",
            "Ce que le mot « conforme » ne dit pas sur l'eau du robinet : la même "
            "mesure, notée contre la norme de 2016, celle d'aujourd'hui, et la plus "
            "stricte au monde.", version, calcule_le,
            sous_titre="Un outil de conscience citoyenne, construit sur des données "
                       "ouvertes. Il sépare <b>la mesure</b>, qui est un fait, du "
                       "<b>verdict</b>, qui est une convention administrative datée.",
            scripts=f'<script src="assets/{empreinte("recherche.js")}"></script>'))

        ecrire(os.path.join(public, "carte.html"), page(
            "Carte de couverture",
            page_carte(lignes, version, calcule_le, comptes), "carte.html",
            "Combien d'analyses complètes l'Observatoire détient dans chaque "
            "département — une carte de ce que l'on sait, pas de ce que l'on a "
            "trouvé.", version, calcule_le,
            sous_titre="Chaque département porte le <b>nombre d'analyses complètes</b> "
                       "que nous en détenons. Un département n'a pas de verdict : la "
                       "couleur dit l'effort de connaissance, jamais la qualité de "
                       "l'eau.", formule=False,
            fil=[("Accueil", "index.html"), ("Carte de couverture", None)]))

        ecrire(os.path.join(public, "communes.html"), page(
            "Les communes du corpus",
            page_communes(lignes, version, calcule_le), "communes.html",
            "Le corpus département par département : communes documentées, communes "
            "non documentées, effort de recherche et bascules.", version, calcule_le,
            sous_titre="Le corpus se parcourt <b>par département</b>. Chaque ligne "
                       "porte son <b>effort de recherche</b> : sans lui, deux "
                       "territoires ne se comparent pas.", formule=False,
            fil=[("Accueil", "index.html"), ("Les communes du corpus", None)]))

        # --- une page par département documenté ---------------------------
        n_depts = pages_departements(lignes, version, calcule_le, public)

        ecrire(os.path.join(public, "methode.html"), page(
            "La méthode et ses garde-fous",
            page_methode(con, version, calcule_le), "methode.html",
            "Comment l'Observatoire note une mesure trois fois, pourquoi il ne "
            "retient que les bulletins complets, et ce qu'il ne sait pas encore faire.",
            version, calcule_le,
            sous_titre="Les règles ci-dessous ne sont pas des préférences de "
                       "présentation : ce sont les conditions auxquelles les chiffres "
                       "de ce site ont un sens.", formule=False,
            fil=[("Accueil", "index.html"), ("La méthode et ses garde-fous", None)]))

        ecrire(os.path.join(public, "sources.html"), page(
            "Sources, référentiel et données",
            page_sources(con, version, calcule_le, exports), "sources.html",
            "D'où viennent les mesures, comment le référentiel de seuils est "
            "construit, et où télécharger l'ensemble.", version, calcule_le,
            sous_titre="Tout ce qui est affiché ici est dérivé de fichiers publics et "
                       "reproductible. Les données sont téléchargeables.",
            formule=False,
            fil=[("Accueil", "index.html"), ("Sources, référentiel et données", None)]))

        # --- une page par substance dotée d'un dossier --------------------
        #
        # L'étage au-dessus de la fiche : le raisonnement se publie UNE fois et
        # se lie depuis chaque commune concernée, au lieu d'être recopié dans
        # chacune (cf. sortie/dossier_page.py).
        substances = DP.publiables()
        for slug, libelle, _o in substances:
            corps_s, titre_s, origine_s = DP.corps(con, slug, version, h, prefixe="../")
            d_s = (DP.charger()[0].get(slug) or DP.charger()[1].get(slug))
            ecrire(os.path.join(public, "substance", f"{slug}.html"), page(
                titre_s, corps_s, "substances.html",
                (d_s.get("chapeau") or titre_s)[:300],
                version, calcule_le, prefixe="../",
                sous_titre=h(d_s.get("titre") or ""),
                fil=[("Accueil", "index.html"), ("Substances", "substances.html"),
                     (titre_s, None)]))

        ecrire(os.path.join(public, "substances.html"), page(
            "Les substances, une par une",
            page_substances(con, version, substances), "substances.html",
            "Ce que chaque substance démontre du déplacement des seuils : une "
            "page par molécule, avec sa date de reclassement.",
            version, calcule_le,
            sous_titre="Une fiche communale dit ce qu'il y a dans une eau. Ces "
                       "pages-ci disent ce qu'une substance démontre — et la date "
                       "à laquelle la règle qui la note a changé.", formule=False,
            fil=[("Accueil", "index.html"), ("Les substances, une par une", None)]))

        # --- une page par commune documentée ------------------------------
        n_fiches = fiches_communes(con, version, lignes, public)

        # --- index de recherche ------------------------------------------
        index = [{"i": c["code_insee"], "n": c["commune"], "d": c["dept"],
                  "cp": [x for x in (c["codes_postaux"] or "").replace(" ", "").split(",") if x],
                  "s": c["statut"], "k": c["dot"],
                  "u": c["url"], "t": c["libelle_statut"],
                  "e": c["nb_parametres"], "b": c["nb_bascules"],
                  "x": c["nb_depasse_applicable"]}
                 for c in lignes]
        ecrire(os.path.join(public, "donnees", "index_communes.json"),
               json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    finally:
        con.close()

    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(public) for f in fs)
    print(f"vitrine générée : {public}")
    print(f"  référentiel version {version}, calculé le {calcule_le}")
    print(f"  {len(PAGES)} pages, {n_depts} page(s) de département, "
          f"{n_fiches} fiche(s) de commune, "
          f"{len(exports)} export(s) — {round(total/1024)} Ko au total")
    n_nd = sum(1 for c in lignes if c["statut"] == "non_documentee")
    if n_nd:
        print(f"  i {n_nd} commune(s) non documentée(s) : visibles sur la carte et "
              "dans la liste, sans fiche — il n'y a pas de bulletin à montrer.")
    print("  publication : déposer le contenu de ce dossier sur un hébergement statique")
    return public


def bloc_situation(c, communes_dept, commune_prelevement=None):
    """
    La carte de situation d'une fiche : où est cette commune dans son
    département, et — si le bulletin est emprunté — où l'eau a été prélevée.

    `commune_prelevement` n'est qu'un **nom** dans `couverture_communes` ; il
    faut le retrouver parmi les communes du département pour en connaître les
    coordonnées. Quand il ne s'y trouve pas — commune d'un autre département,
    libellé qui ne correspond pas —, aucun trait n'est tracé et la phrase reste
    seule. Un trait vers un point approximatif dirait sur une carte quelque
    chose de faux, ce que l'absence de trait ne fait pas.
    """
    voisine = None
    if commune_prelevement:
        cible = commune_prelevement.strip().casefold()
        for v in communes_dept:
            if (v["commune"] or "").strip().casefold() == cible:
                voisine = v
                break

    svg = carte_svg(communes_dept, largeur=560, depts={c["dept"]}, prefixe="../",
                    focus={c["code_insee"]} | ({voisine["code_insee"]} if voisine else set()),
                    relier=(c["code_insee"], voisine["code_insee"]) if voisine else None)

    if commune_prelevement:
        if voisine:
            phrase = (
                f"<b>Ce bulletin n'a pas été prélevé à {h(c['commune'])}.</b> Il l'a été "
                f"à <a href='../commune/{h(voisine['code_insee'])}.html'>"
                f"{h(commune_prelevement)}</a>, sur le réseau qui alimente les deux "
                f"communes — le trait le relie sur la carte. C'est la même eau, "
                f"analysée en un autre point : la commune n'a pas de bulletin complet "
                f"à elle.")
        else:
            phrase = (
                f"<b>Ce bulletin n'a pas été prélevé à {h(c['commune'])}</b>, mais à "
                f"{h(commune_prelevement)}, sur le réseau qui alimente les deux "
                f"communes. Cette commune n'étant pas dans le corpus de ce "
                f"département, la carte ne peut pas la situer.")
    else:
        phrase = (f"Le bulletin ci-dessous a été prélevé à {h(c['commune'])} même. "
                  f"Les autres points de la carte sont les communes du département "
                  f"que le corpus documente.")

    return f"""
  <section><h3 class="sec">Où cette eau a été prélevée</h3>
    <div class="carte-bloc situation">{svg}</div>
    <div class="rappel">{phrase}</div>
  </section>
"""


def pages_departements(lignes, version, calcule_le, public):
    """Une page par département documenté."""
    n = 0
    for dept, communes in par_departement(lignes).items():
        nom = _nom_dept(dept)
        n_nd = sum(1 for c in communes if c["statut"] == "non_documentee")
        ecrire(os.path.join(public, "departement", f"{dept}.html"), page(
            f"{nom} ({dept})",
            page_departement(dept, communes, version, calcule_le),
            "communes.html",
            f"Les {len(communes)} communes du corpus dans le département {nom} "
            f"({dept}) : effort de recherche, dépassements à la date, bascules, "
            f"et {n_nd} commune(s) non documentée(s).",
            version, calcule_le,
            sous_titre="Ce que l'Observatoire sait de l'eau de ce département — et "
                       "ce qu'il n'en sait pas. Un département n'a pas de verdict : "
                       "ce sont des bulletins datés, un par point d'eau.",
            formule=False, prefixe="../",
            fil=[("Accueil", "index.html"),
                 ("Les communes du corpus", "communes.html"),
                 (f"{nom} ({dept})", None)],
            scripts=(f'<script src="../assets/{empreinte("carte.js")}"></script>'
                     f'<script src="../assets/{empreinte("tableau.js")}"></script>')))
        n += 1
    return n


def fiches_communes(con, version, lignes, public):
    """
    Une page par commune documentée, bâtie sur le MÊME corps et le MÊME rendu
    que la fiche autonome — mêmes obligations d'affichage, mêmes trois états,
    même seuil applicable à la date.
    """
    # Deux fichiers de prose écrite ; le troisième niveau, la prose dérivée,
    # est calculé par bloc_commune() au moment de la construction.
    redactions, proposees = BF.charger_prose()

    # Les fiches vivent dans commune/ : l'accroche vers le dossier de substance
    # se préfixe ICI, une fois, plutôt que d'être réparée côté navigateur.
    accroches = {p: dict(d, u="../" + d["u"])
                 for p, d in DP.accroches(con, version).items()}

    corps = lire("corps_fiche.html")
    groupes = par_departement(lignes)
    n = 0
    for c in lignes:
        if c["statut"] == "non_documentee":
            continue
        insee = c["code_insee"]
        rat = BF.rattachements(con, version, [insee]).get(insee)
        if rat:
            ligne = con.execute("""
                SELECT a.*, p.conf_limites_bact, p.conf_limites_pc,
                       p.conf_references_pc, p.nom_distributeur,
                       a.nb_mesures_lues - a.nb_mesures_notees AS nb_sans_seuil
                FROM analyses_figees a
                JOIN prelevements p ON p.code_prelevement = a.code_prelevement
                WHERE a.version_referentiel = ? AND a.code_prelevement = ?
            """, [version, rat["code_prelevement"]]).fetchone()
            cols = [d[0] for d in con.description]
            if not ligne:
                continue
            lignes_c, code_prel = [(ligne, cols, rat)], rat["code_prelevement"]
        else:
            rows, cols = BF.analyses(con, version, [insee], historique=True)
            if not rows:
                continue
            lignes_c = [(r, cols, None) for r in rows]
            code_prel = None

        C, PARAMS, ORDER = {}, {}, []
        for ligne, cols, rattachement in lignes_c:
            a = dict(zip(cols, ligne))
            cle = f"{insee}-{a['date_prelevement']}"
            d_iso = str(a["date_prelevement"])
            C[cle] = BF.bloc_commune(
                con, ligne, cols,
                BF.pour_bulletin(redactions, insee, d_iso,
                                 a["code_prelevement"]), version,
                rattachement=rattachement,
                proposee=BF.pour_bulletin(proposees, insee, d_iso,
                                          a["code_prelevement"]),
                accroches=accroches)
            PARAMS[cle] = BF.bloc_parametres(con, a["code_prelevement"], version)
            ORDER.append(cle)
        # Le plus récent d'abord : c'est ce que l'habitant vient chercher.
        ORDER.sort(key=lambda k: C[k]["date_iso"], reverse=True)

        d0 = C[ORDER[0]]
        j = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
        switch = ('<div class="switch" id="switch" role="group" '
                  'aria-label="Choisir un prélèvement"></div>' if len(ORDER) > 1 else "")
        rappel_series = (
            '<div class="rappel">Plusieurs prélèvements complets sont disponibles pour '
            'cette commune. Chacun est un point dans le temps, sur un point d\'eau '
            'donné : ils se lisent l\'un après l\'autre, jamais moyennés — une moyenne '
            'de bulletins n\'a ni date ni grille, et ne peut donc être notée contre '
            'aucune.</div>' if len(ORDER) > 1 else "")

        situation = bloc_situation(c, groupes.get(c["dept"], []),
                                   rat["commune_prelevement"] if rat else None)

        html = page(
            d0["name"],
            f'{switch}{rappel_series}\n{corps}\n{situation}',
            "communes.html",
            f"Bulletin d'analyse complet de l'eau du robinet à {d0['name']} "
            f"({d0['insee']}), noté contre les grilles de 2016, d'aujourd'hui et la "
            f"plus stricte au monde.",
            version, calcule_le=d0["calcule_le"],
            sous_titre=f"{h(d0['sub'])} — bulletin du {h(d0['date'])}",
            formule=False, prefixe="../",
            fil=[("Accueil", "index.html"),
                 ("Les communes du corpus", "communes.html"),
                 (f"{_nom_dept(c['dept'])} ({c['dept']})",
                  f"departement/{c['dept']}.html"),
                 (d0["name"], None)],
            scripts=("<script>\n"
                     f"const KPI_LABELS={j(BF.KPI_LABELS)};\n"
                     f"const C={j(C)};\nconst PARAMS={j(PARAMS)};\n"
                     f"const ORDER={j(ORDER)};\n</script>\n"
                     f'<script src="../assets/{empreinte("fiche.js")}"></script>'))

        ecrire(os.path.join(public, "commune", f"{insee}.html"), html)
        n += 1
    return n


def main():
    p = argparse.ArgumentParser(description="Génère la vitrine publique statique")
    p.add_argument("--sortie", help="dossier de destination (défaut : site/public)")
    a = p.parse_args()
    construire(destination=a.sortie)


if __name__ == "__main__":
    main()

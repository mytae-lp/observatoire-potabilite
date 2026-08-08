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

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICI = os.path.join(RACINE, "site")
GABARITS = os.path.join(ICI, "gabarits")
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, os.path.join(RACINE, "sortie"))

from common import DB_PATH, SEUIL_COMPLET  # noqa: E402
import build_fiche as BF  # noqa: E402

GEOJSON = os.path.join(RACINE, "referentiel", "geo", "departements-simplifie.geojson")
REF_CSV = os.path.join(RACINE, "referentiel", "referentiel_seuils.csv")

PAGES = [("index.html", "Accueil"), ("carte.html", "Carte"),
         ("communes.html", "Communes"), ("methode.html", "Méthode"),
         ("sources.html", "Sources & données")]


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


def page(titre, corps, page_courante, description, version, calcule_le,
         scripts="", sous_titre=None, formule=True):
    nav = "".join(
        f'<li><a href="{f}"{" aria-current=\"page\"" if f == page_courante else ""}>{h(n)}</a></li>'
        for f, n in PAGES)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{h(titre)} — Observatoire de la potabilité réglementaire</title>
<meta name="description" content="{h(description)}">
<link rel="stylesheet" href="assets/{empreinte('observatoire.css')}">
</head>
<body>
<div class="masthead"><div class="wrap">
  <div class="eyebrow">Observatoire de la potabilité réglementaire · données ouvertes</div>
  <h1>{h(titre)}</h1>
  <p>{sous_titre or ''}</p>
  {'<div class="formule">« Ce n\'est pas l\'eau qui est devenue potable. C\'est la limite qui a bougé. »</div>' if formule else ''}
</div></div>
<nav class="nav" aria-label="Sections du site"><div class="wrap"><ul>{nav}</ul></div></nav>

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


def carte_svg(lignes, largeur=920):
    """Fond départemental + un point par commune, en SVG produit ici même.

    Aucun serveur de tuiles n'est appelé : le visiteur ne laisse donc aucune
    trace chez un tiers en consultant la carte, et il n'y a pas de bannière de
    consentement à lui imposer.
    """
    if not os.path.exists(GEOJSON):
        return ('<p class="rappel">Fond de carte absent — '
                '<code>referentiel/geo/departements-simplifie.geojson</code>.</p>')
    geo = json.load(open(GEOJSON, encoding="utf-8"))

    anneaux = []
    for f in geo["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for anneau in poly:
                anneaux.append(anneau)

    xs, ys = [], []
    for anneau in anneaux:
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

    # Décimation : à cette échelle, deux points distants de moins d'un demi-pixel
    # sont le même point. Le fichier source reste intact dans le dépôt.
    chemins = []
    for anneau in anneaux:
        d, prev = [], None
        for lon, lat in anneau:
            x, y = pt(lon, lat)
            if prev and abs(x - prev[0]) < .5 and abs(y - prev[1]) < .5:
                continue
            d.append(f"{'M' if not d else 'L'}{x:.1f},{y:.1f}")
            prev = (x, y)
        if len(d) > 3:
            chemins.append('<path class="dept" d="' + "".join(d) + 'Z"/>')

    points = []
    for c in sorted(lignes, key=lambda r: 0 if r["statut"] == "non_documentee" else 1):
        if c["lon"] is None or c["lat"] is None:
            continue
        x, y = pt(c["lon"], c["lat"])
        r = 5.5 if c["statut"] != "non_documentee" else 4.5
        titre = f"{c['commune']} ({c['dept']}) — {c['libelle_statut']}"
        points.append(
            f'<a class="pt" href="{c["url"]}" aria-label="{h(titre)}">'
            f'<title>{h(titre)}</title>'
            f'<circle class="{c["niveau"]}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/></a>')

    return (f'<svg viewBox="0 0 {largeur:.0f} {hauteur:.0f}" '
            f'role="img" aria-label="Carte des communes documentées">'
            f'<g>{"".join(chemins)}</g><g>{"".join(points)}</g></svg>')


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


def page_carte(lignes, version, calcule_le):
    n = {k: sum(1 for c in lignes if c["niveau"] == k) for k in DOT}
    svg = carte_svg(lignes)
    return f"""
  <section style="margin-top:0">
    <div class="carte-bloc">{svg}
      <div class="carte-legende">
        <span><i class="lg-vert"></i> commune analysée, aucun dépassement à la date du prélèvement — {n['analysee-vert']}</span>
        <span><i class="lg-bascule"></i> commune analysée, au moins une <b>bascule</b> : conforme aujourd'hui, pas selon la grille de 2016 — {n['analysee-bascule']}</span>
        <span><i class="lg-rouge"></i> commune analysée, au moins un dépassement à la date du prélèvement — {n['analysee-rouge']}</span>
        <span><i class="lg-rattachee"></i> commune rattachée au réseau — l'analyse a été prélevée dans une commune voisine, sur la même eau — {n['rattachee']}</span>
        <span><i class="lg-nondoc"></i> commune <b>non documentée</b> — aucun bulletin complet, ni pour elle ni pour son réseau — {n['non_documentee']}</span>
      </div>
    </div>
    <div class="rappel"><b>Gris n'est pas une couleur neutre, c'est un troisième état.</b>
      Une commune non documentée n'est ni conforme ni non conforme : on ne sait pas.
      La faire disparaître de la carte reviendrait à présenter une absence de donnée
      comme une bonne nouvelle. Un cercle ambre existe aussi : la commune est analysée,
      sans dépassement, mais au moins une mesure est <b>indéterminée</b> — la limite de
      quantification du laboratoire est au-dessus du seuil de comparaison, et on ne peut
      donc pas affirmer que le seuil est respecté.</div>
    <div class="rappel">Le fond de carte est produit à la construction du site et
      incorporé à la page : aucune requête n'est adressée à un serveur de tuiles, donc
      aucune adresse IP de visiteur n'est transmise à un tiers. Les départements et
      collectivités d'outre-mer ne figurent pas encore sur ce fond.</div>
  </section>
"""


def page_communes(lignes, version, calcule_le):
    lig = []
    for c in lignes:
        url = f"commune/{c['code_insee']}.html"
        nom = (f"<a href='{url}'>{h(c['commune'])}</a>"
               if c["statut"] != "non_documentee" else h(c["commune"]))
        if c["statut"] == "non_documentee":
            detail = "<td colspan='5' style='color:var(--gris)'>aucun bulletin complet, ni pour la commune ni pour son réseau</td>"
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
        lig.append(
            f"<tr><td>{nom}<span class='grille'>INSEE {h(c['code_insee'])}</span></td>"
            f"<td>{h(c['dept'])}</td>"
            f"<td><span class='st {h(c['statut'])}'>{h(c['libelle_statut'])}</span></td>"
            f"{detail}</tr>")

    return f"""
  <section style="margin-top:0">
    <div class="tableau-communes">
      <table>
        <thead><tr><th>Commune</th><th>Dépt</th><th>Statut</th><th>Prélèvement</th>
          <th>Effort de recherche</th><th>Paramètres notés</th>
          <th>Dépassements à la date</th><th>Bascules</th></tr></thead>
        <tbody>{"".join(lig)}</tbody>
      </table>
    </div>
    <div class="rappel"><b>L'effort de recherche est dans le tableau, et il n'en sortira
      pas.</b> Le nombre de paramètres cherchés n'est pas un indicateur de qualité de
      l'eau : c'est un indicateur de transparence, et il se lit à l'envers. Une eau
      « correcte » sur 200 paramètres est une information plus faible qu'une eau
      « moyenne » sur 700 — la première n'a pas été beaucoup interrogée. C'est pourquoi
      la colonne des dépassements porte aussi un taux (‰ des paramètres notés) : seuls
      les taux se comparent d'une commune à l'autre.</div>
  </section>
"""


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

        # --- exports ------------------------------------------------------
        exports = exporter(con, version, os.path.join(public, "donnees"))

        # --- pages --------------------------------------------------------
        assets = os.path.join(public, "assets")
        os.makedirs(assets, exist_ok=True)
        for f in ("observatoire.css", "fiche.js"):
            shutil.copyfile(os.path.join(GABARITS, f), os.path.join(assets, f))
        shutil.copyfile(os.path.join(GABARITS, "recherche.js"),
                        os.path.join(assets, "recherche.js"))

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
            page_carte(lignes, version, calcule_le), "carte.html",
            "Les communes documentées par l'Observatoire, et celles qui ne le sont "
            "pas — l'absence de donnée reste visible.", version, calcule_le,
            sous_titre="Ce que la carte colorie n'est pas la qualité de l'eau : c'est "
                       "<b>ce que l'on sait</b> de l'eau de chaque commune, et contre "
                       "quelle grille on l'a noté.", formule=False))

        ecrire(os.path.join(public, "communes.html"), page(
            "Les communes du corpus",
            page_communes(lignes, version, calcule_le), "communes.html",
            "Toutes les communes documentées, avec leur effort de recherche, leur "
            "taux de couverture et leurs bascules.", version, calcule_le,
            sous_titre="Chaque ligne porte son <b>effort de recherche</b> et son "
                       "<b>dénominateur</b> : sans eux, deux communes ne se comparent "
                       "pas.", formule=False))

        ecrire(os.path.join(public, "methode.html"), page(
            "La méthode et ses garde-fous",
            page_methode(con, version, calcule_le), "methode.html",
            "Comment l'Observatoire note une mesure trois fois, pourquoi il ne "
            "retient que les bulletins complets, et ce qu'il ne sait pas encore faire.",
            version, calcule_le,
            sous_titre="Les règles ci-dessous ne sont pas des préférences de "
                       "présentation : ce sont les conditions auxquelles les chiffres "
                       "de ce site ont un sens.", formule=False))

        ecrire(os.path.join(public, "sources.html"), page(
            "Sources, référentiel et données",
            page_sources(con, version, calcule_le, exports), "sources.html",
            "D'où viennent les mesures, comment le référentiel de seuils est "
            "construit, et où télécharger l'ensemble.", version, calcule_le,
            sous_titre="Tout ce qui est affiché ici est dérivé de fichiers publics et "
                       "reproductible. Les données sont téléchargeables.",
            formule=False))

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
    print(f"  {len(PAGES)} pages, {n_fiches} fiche(s) de commune, "
          f"{len(exports)} export(s) — {round(total/1024)} Ko au total")
    n_nd = sum(1 for c in lignes if c["statut"] == "non_documentee")
    if n_nd:
        print(f"  i {n_nd} commune(s) non documentée(s) : visibles sur la carte et "
              "dans la liste, sans fiche — il n'y a pas de bulletin à montrer.")
    print("  publication : déposer le contenu de ce dossier sur un hébergement statique")
    return public


def fiches_communes(con, version, lignes, public):
    """
    Une page par commune documentée, bâtie sur le MÊME corps et le MÊME rendu
    que la fiche autonome — mêmes obligations d'affichage, mêmes trois états,
    même seuil applicable à la date.
    """
    # Deux fichiers de prose écrite ; le troisième niveau, la prose dérivée,
    # est calculé par bloc_commune() au moment de la construction.
    redactions, proposees = BF.charger_prose()

    corps = lire("corps_fiche.html")
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
                BF.pour_bulletin(redactions, insee, d_iso), version,
                rattachement=rattachement,
                proposee=BF.pour_bulletin(proposees, insee, d_iso))
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

        html = page(
            d0["name"],
            f'{switch}{rappel_series}\n{corps}',
            "communes.html",
            f"Bulletin d'analyse complet de l'eau du robinet à {d0['name']} "
            f"({d0['insee']}), noté contre les grilles de 2016, d'aujourd'hui et la "
            f"plus stricte au monde.",
            version, calcule_le=d0["calcule_le"],
            sous_titre=f"{h(d0['sub'])} — bulletin du {h(d0['date'])}",
            formule=False,
            scripts=("<script>\n"
                     f"const KPI_LABELS={j(BF.KPI_LABELS)};\n"
                     f"const C={j(C)};\nconst PARAMS={j(PARAMS)};\n"
                     f"const ORDER={j(ORDER)};\n</script>\n"
                     f'<script src="assets/{empreinte("fiche.js")}"></script>')
        ).replace('href="assets/', 'href="../assets/') \
         .replace('src="assets/', 'src="../assets/') \
         .replace('href="index.html"', 'href="../index.html"') \
         .replace('href="carte.html"', 'href="../carte.html"') \
         .replace('href="communes.html"', 'href="../communes.html"') \
         .replace('href="methode.html"', 'href="../methode.html"') \
         .replace('href="sources.html"', 'href="../sources.html"')

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

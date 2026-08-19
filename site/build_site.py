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
import glob
import gzip
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

from common import DB_PATH, SEUIL_COMPLET, departements_publies  # noqa: E402
import build_fiche as BF  # noqa: E402
import dossier_page as DP  # noqa: E402
import dossier_panel_reduit as DPR  # noqa: E402
import identite as ID_SUB  # noqa: E402
import indicateurs as IND  # noqa: E402

GEOJSON = os.path.join(RACINE, "referentiel", "geo", "departements-simplifie.geojson")
REF_CSV = os.path.join(RACINE, "referentiel", "referentiel_seuils.csv")

# LE MENU, EN DEUX NIVEAUX depuis le 17 août 2026.
#
# À plat, il atteignait onze entrées avec « À propos » — 1 049 px de barre
# mesurés à neuf, et il se repliait déjà à 1080 px. Onze libellés alignés ne se
# lisent plus : ils se balaient. Le regroupement n'est donc pas cosmétique, il
# rend au menu sa fonction, qui est de dire en un coup d'œil ce que le site
# contient.
#
# Trois premiers niveaux sans deroule-menu — l'accueil, les dossiers — parce que
# ce sont les deux portes que le projet veut voir prendre. Le reste se range
# par question posée : où regarder, comment c'est fait, qui le fait.
#
# `None` en première position marque un groupe ; il n'a pas de page à lui.
# **Un intitulé de groupe qui serait aussi un lien** aurait produit exactement
# le défaut de l'index des dossiers : un libellé qui promet une page et n'en
# ouvre aucune.
#
# Les mentions légales ne sont PAS ici. Elles vivent au pied, avec
# l'avertissement et les licences : c'est là qu'un lecteur les cherche, et une
# entrée de menu de plus pour un texte consulté deux fois l'an se paierait sur
# tous les autres.
# « Carte » et non « Collecte » depuis le 19 août 2026, demande de Yannick :
# c'est la page la plus manipulable du site, et son intitulé doit le dire. La
# maquette l'appelait déjà ainsi — le code avait dérivé, pas la charte.
#
# CE QUI NE CHANGE PAS, ET NE DOIT PAS : le titre de la page reste « Où en est
# la collecte » et son chapô continue d'annoncer que ce qu'elle montre « n'est
# pas l'état de l'eau, c'est l'avancement d'un travail ». Sous le seul mot
# « Carte », un lecteur croirait à une carte de la qualité de l'eau — ce que le
# projet refuse d'être. Le menu nomme l'outil, la page dit ce qu'elle montre.
PAGES = [
    ("index.html", "Accueil", None),
    ("dossiers.html", "Dossiers", None),
    (None, "Explorer", [("communes.html", "Communes"),
                        ("carte.html", "Carte"),
                        ("substances.html", "Substances"),
                        ("reclassements.html", "Reclassements")]),
    (None, "Méthode", [("methode.html", "Méthode"),
                       ("sources.html", "Sources & données")]),
    (None, "Le projet", [("a-propos.html", "À propos"),
                         ("contact.html", "Contact")]),
]

# Les pages de navigation, à plat — pour tout ce qui compte ou parcourt sans
# se soucier du regroupement. Dérivée, jamais recopiée : deux listes de pages
# divergent à la première entrée ajoutée, et c'est déjà arrivé une fois sur la
# barre de la page de contact.
PAGES_PLATES = [(f, n) for f, n, sous in PAGES if f] + \
               [(f, n) for _f, _n, sous in PAGES if sous for f, n in sous]

# Le texte légal, au pied de chaque page.
PAGES_PIED = [("mentions-legales.html", "Mentions légales")]


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

    verdict = ("analysee-rouge"   if depasse else
               "analysee-bascule" if bascules else
               "analysee-ambre"   if indetermines else
               "analysee-vert")

    # UNE COMMUNE RATTACHÉE GARDE SON VERDICT.
    # Corrigé le 12 août 2026, sur demande de Yannick. Ce test sortait ici en
    # renvoyant « rattachee », AVANT de regarder le verdict : une commune
    # desservie par le point de prélèvement d'une autre — Ramonville-Saint-Agne
    # en dessert des dizaines dans le 31 — ressortait blanche sur la carte, non
    # pas faute de donnée mais parce que sa couleur était calculée puis jetée.
    # Elle porte maintenant les deux informations à la fois : l'emprunt (moitié
    # blanche) et le verdict du bulletin emprunté (moitié colorée).
    # Le §8bis obligation 5 demande de dire quand l'analyse est empruntée ; il
    # ne demande pas d'effacer ce qu'elle dit.
    # `niveau` reste « rattachee » : c'est la clé de la légende, du filtre et
    # des lignes du tableau, et un état rattaché reste un état à part entière.
    # La couleur du verdict voyage à côté, dans `teinte` — voir plus bas.
    if statut == "rattachee_reseau":
        return "rattachee"
    return verdict


def teinte_commune(statut, depasse, bascules, indetermines):
    """
    La couleur du VERDICT, indépendamment du statut de la commune.

    Elle n'a de sens que pour les communes rattachées : partout ailleurs elle
    est déjà portée par `niveau`. Une commune rattachée a un verdict — celui du
    bulletin emprunté — que la carte calculait puis jetait.
    """
    if statut != "rattachee_reseau":
        return None
    if depasse:
        return "rattachee-rouge"
    if bascules:
        return "rattachee-bascule"
    if indetermines:
        return "rattachee-ambre"
    return "rattachee-vert"


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
    # PAS DE `<ol><li>` — corrigé le 17 août 2026, sur remarque de Yannick.
    # La feuille v2 ne porte aucune règle pour `.fil ol` ni `.fil li` : les
    # éléments de liste restaient donc des blocs, et le fil s'empilait
    # verticalement en repoussant tout l'en-tête vers le bas. La maquette
    # n'emploie pas de liste — des `<a>` séparés par des `<span>` —, et
    # `.fil a` comme `.fil span` sont déjà stylés. On produit ce que la charte
    # décrit plutôt que d'ajouter deux règles pour rattraper autre chose.
    bouts = []
    for i, (libelle, url) in enumerate(fil):
        if i:
            bouts.append("<span>›</span>")
        if i == len(fil) - 1 or not url:
            bouts.append(f'<span aria-current="page">{h(libelle)}</span>')
        else:
            bouts.append(f'<a href="{prefixe}{h(url)}">{h(libelle)}</a>')
    return ('<nav class="fil" aria-label="Fil d\'Ariane"><div class="zone zone-large">'
            f'{"".join(bouts)}</div></nav>')


# La marque, inlinée. 625 octets : une seconde requête coûterait plus cher que
# l'octet économisé, et l'inline permettra de faire suivre la teinte au thème le
# jour où c'est utile (consigne §0). Le même fichier est servi en `rel=icon`.
MARQUE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" role="img" '
    'aria-label="Observatoire de la potabilité réglementaire">'
    '<path d="M16 2.5C16 2.5 5.5 14.2 5.5 20.2a10.5 10.5 0 0 0 21 0C26.5 14.2 '
    '16 2.5 16 2.5Z" fill="#0B6A73"/>'
    '<rect x="8.4" y="17.1" width="15.2" height="2.1" rx="1.05" fill="#F2F5F7" '
    'opacity=".95"/>'
    '<rect x="11.6" y="22.3" width="12" height="2.1" rx="1.05" fill="#7FD4DA"/>'
    '</svg>')

# Le thème, restauré AVANT le premier rendu. Ces quatre lignes sont dans le
# `<head>` et nulle part ailleurs : dans un fichier externe, ou en fin de page,
# le visiteur qui a choisi le thème sombre verrait d'abord une page claire, puis
# un basculement. C'est le seul script du site qui doit bloquer le rendu, et
# c'est pour cela qu'il est réduit à sa plus simple expression.
THEME_AVANT_RENDU = (
    "<script>try{var t=localStorage.getItem('theme');"
    "if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}</script>")


def barre(page_courante, prefixe):
    """
    La barre fine et collante, qui remplace le bandeau de titre.

    Le bandeau v1 portait le `h1`, le sous-titre et la formule sur toute la
    largeur, à chaque page. Il coûtait la moitié d'un écran de téléphone avant
    le premier mot utile, et répétait sept fois la même citation. La barre ne
    porte que ce qui sert à se déplacer : la marque, le menu, le thème.

    Le menu se replie **à 1080 px** et pas à 900 : déployé, il réclame 1 049 px
    de barre. Mesuré, et c'est la mesure 2 du §7 qui l'avait attrapé — dans la
    plage 900-1080, la barre débordait sans que personne ne regarde jamais là.

    LES SOUS-MENUS SONT DES `<details>`, ET C'EST LE POINT.
    Un menu déroulant fabriqué en JavaScript disparaît quand le script ne
    charge pas ; ici quatre des sept pages du site deviendraient alors
    inatteignables. `<details>/<summary>` ouvre au clic **et au clavier** sans
    une ligne de script, annonce son état replié ou déployé aux lecteurs
    d'écran sans un seul attribut ARIA à tenir à jour, et se ferme à Échap. Le
    script n'ajoute qu'un confort : refermer les autres quand on en ouvre un.

    Le groupe qui contient la page courante s'ouvre à la construction — un
    lecteur ne doit pas avoir à deviner sous quel intitulé se range la page
    qu'il est en train de lire.
    """
    morceaux = []
    for fichier, nom, sous in PAGES:
        if not sous:
            courant = ' aria-current="page"' if fichier == page_courante else ""
            morceaux.append(f'<li><a href="{prefixe}{fichier}"{courant}>{h(nom)}</a></li>')
            continue
        ici = any(f == page_courante for f, _ in sous)
        entrees = "".join(
            f'<li><a href="{prefixe}{f}"'
            f'{" aria-current=\"page\"" if f == page_courante else ""}>{h(n)}</a></li>'
            for f, n in sous)
        morceaux.append(
            f'<li class="a-sous"><details class="deroule{" deroule--ici" if ici else ""}"'
            f'{" open" if ici else ""}>'
            f'<summary>{h(nom)}'
            f'<svg class="deroule-fleche" viewBox="0 0 24 24" fill="none" aria-hidden="true"'
            f' stroke="currentColor" stroke-width="2" stroke-linecap="round"'
            f' stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>'
            f'</summary><ul class="deroule-menu">{entrees}</ul></details></li>')
    liens = "".join(morceaux)
    return f"""<header class="barre">
  <div class="zone zone-large barre-i">
    <a class="marque" href="{prefixe}index.html" aria-label="Accueil de l'Observatoire">
      {MARQUE_SVG}
      <span class="marque-txt"><b>Observatoire</b><span>de la potabilité réglementaire</span></span>
    </a>
    <button class="bouton-theme burger" id="burger" aria-expanded="false"
            aria-controls="menu" aria-label="Ouvrir le menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
           stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <ul class="menu" id="menu">{liens}</ul>
    <button class="bouton-theme" id="theme"
            aria-label="Basculer entre thème clair et sombre"
            title="Thème clair / sombre">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
           stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/>
        <path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"/>
      </svg>
    </button>
  </div>
</header>"""


# Une photographie par page de navigation, et **la même à chaque visite**. Une
# image tirée au hasard donnerait à la page une humeur variable ; la page
# Méthode a *sa* photographie.
#
# Les fiches communales et les briefs de substance n'en ont aucune, et ce n'est
# pas un oubli : une fiche rend un verdict sur l'eau de quelqu'un, elle s'ouvre
# sur le nom de la commune et sur le verdict. Un brief sera tiré à plus de mille
# exemplaires — une photographie par page en ferait une galerie, et coûterait
# 200 ko à chaque ouverture pour une image qui ne dit rien de la molécule.
#
# Le crédit se lit **comme une source** — titre, date, heure, auteur, œuvre —
# parce que c'est la grammaire du site : rien n'est publié sans sa provenance.
# Les dates viennent de l'EXIF des originaux, pas du nom de fichier.
BANDEAUX = {
    "index.html":         ("bandeau-fils-rayonnants", "Fils de rosée", "29 juin 2022, 7 h 23"),
    "carte.html":         ("bandeau-fil-unique", "Un fil, au matin", "9 juin 2022, 8 h 11"),
    "communes.html":      ("bandeau-brin-perle", "Brin perlé", "1er juin 2022, 7 h 29"),
    "substances.html":    ("bandeau-toile-grosses", "Toile chargée", "9 juin 2022, 8 h 14"),
    "reclassements.html": ("bandeau-toile-doree", "Toile dorée", "13 juin 2022, 8 h 11"),
    "methode.html":       ("bandeau-fil-lumiere", "Fil dans la lumière", "25 mai 2022, 7 h 51"),
    "sources.html":       ("bandeau-plume", "Plume et rosée", "26 mai 2022, 9 h 15"),
    "departement":        ("bandeau-serie-gouttes", "Sept gouttes sur une tige", "20 juin 2022, 12 h 05"),
    # SANS DATE, ET C'EST VOULU. L'EXIF a été retiré des copies du dépôt, et les
    # dates ci-dessus viennent des originaux, sur la machine de Yannick. Écrire
    # une date approchée pour aligner la ligne serait inventer une source — le
    # crédit se lit comme une source, et une source fausse est pire qu'une
    # source incomplète (§2.7). Le troisième terme est donc vide, et
    # `bandeau()` sait ne rien afficher. À compléter le jour où l'EXIF revient.
    "dossiers.html":      ("bandeau-toile-perlee", "Toile perlée", ""),
    "dossier":            ("bandeau-branche-toile", "Branche et toile", ""),
}


def bandeau(cle, titre, sous_titre, fil, prefixe, formule=False):
    """
    Le bandeau photographique : la photo en fond, le texte par-dessus.

    **La lisibilité tient à un filtre, pas à un dégradé.** C'est écrit dans la
    feuille (`brightness(.52) saturate(1.25)` plus un voile uniforme léger), et
    il ne faut pas y revenir : trois autres approches ont été essayées et
    rejetées, dont un dégradé opaque qui produisait « un gros pâté bleu » et
    faisait disparaître l'image.

    `alt=""` : l'image est décorative, l'information est dans le crédit.
    """
    ref = BANDEAUX.get(cle)
    if not ref:
        return ""
    fichier, oeuvre, quand = ref
    return f"""<div class="accroche bandeau bandeau--photo">
  <div class="bandeau-fond" aria-hidden="true">
    <picture>
      <source srcset="{prefixe}assets/{fichier}.webp" type="image/webp">
      <img src="{prefixe}assets/{fichier}.jpg" alt="">
    </picture>
  </div>
  <div class="bandeau-texte">
    <div class="zone zone-large bandeau-i">
      {fil_ariane(fil, prefixe)}
      <div class="bandeau-txt">
        <p class="surtitre">Observatoire de la potabilité réglementaire</p>
        <h1>{h(titre)}</h1>
        {f'<p class="chapo">{sous_titre}</p>' if sous_titre else ''}
        {'<p class="formule">« Ce n\'est pas l\'eau qui est devenue potable. C\'est la limite qui a bougé. »</p>' if formule else ''}
      </div>
      <p class="bandeau-credit"><b>{h(oeuvre)}</b>{f" — {h(quand)}" if quand else ""}.
        Photographie Maude&nbsp;Mytae, série <em>Quand l'eau rencontre la terre</em>,
        Éditions Mytae. Tous droits réservés.</p>
    </div>
  </div>
</div>"""


def pied(version, calcule_le, corpus=None, prefixe=""):
    """Le pied : l'avertissement, les licences, la traçabilité et le légal.

    L'avertissement est le seul texte du site qui protège son lecteur plutôt
    que de l'informer. Il passe en `.avert` — un bloc à filet ambre —, alors
    qu'il s'affichait sans style depuis toujours : la classe n'était définie
    nulle part, ni en v1 ni dans la première v2 (consigne §10.3).

    Les mentions légales sont ici et non au menu (décision du 17 août 2026) :
    c'est au pied qu'on les cherche, et une entrée de menu pour un texte
    consulté deux fois l'an se paierait sur toutes les autres.
    """
    corpus_html = (f"<span><b>Corpus</b> <code>{h(corpus)}</code></span>"
                   if corpus else "")
    legal = "".join(f'<a href="{prefixe}{f}">{h(n)}</a>' for f, n in PAGES_PIED)
    return f"""<footer class="pied">
  <div class="zone zone-large">
    <p class="avert"><strong>Avertissement.</strong> Cet observatoire est un outil
      d'information citoyenne. Il rapproche des mesures publiques d'un référentiel de
      seuils daté que nous construisons et documentons nous-mêmes : <strong>ce
      rapprochement peut comporter des erreurs</strong>. Les valeurs affichées ici
      n'ont aucun caractère officiel et ne remplacent pas les conclusions sanitaires
      de l'agence régionale de santé. Pour tout usage engageant — démarche
      administrative, litige, décision de santé — reportez-vous aux sources
      officielles et faites vérifier ces éléments par un tiers compétent. Les
      références sur la qualité de votre eau restent votre ARS, votre mairie et le
      rapport annuel de votre service d'eau.</p>
    <p><b>Sources &amp; licences.</b> Mesures : SISE-Eaux (ministère chargé de la
      santé) via l'API Hub'Eau, sous Licence Ouverte 2.0. Référentiel de seuils,
      méthode et base : ODbL 1.0. Code : MIT. Fond de carte : contours départementaux
      IGN/Etalab, Licence Ouverte. Une réutilisation conforme aux licences n'engage
      pas l'Observatoire sur les conclusions qu'en tire le réutilisateur.</p>
    <div class="tracab">
      <span><b>Version du référentiel</b> <code>{h(version)}</code></span>
      <span><b>Calculé le</b> <code>{h(calcule_le)}</code></span>
      {corpus_html}
      <span><b>Porté par</b> Éditions Mytae</span>
    </div>
    <div class="pied-legal">{legal}</div>
  </div>
</footer>"""


def page(titre, corps, page_courante, description, version, calcule_le,
         scripts="", sous_titre=None, formule=True, prefixe="", fil=None,
         largeur="std", titre_dans_corps=False, og_titre=None,
         og_description=None, corpus=None, cle_bandeau=None):
    """
    Le squelette commun, forme v2.

    `prefixe` est le chemin de retour vers la racine — "" à la racine, "../"
    dans `commune/` et `departement/`. Il est passé explicitement plutôt que
    réparé après coup : la version d'avant réécrivait les adresses d'une page
    déjà rendue par une chaîne de `.replace()`, une par entrée de menu. Ajouter
    une page au menu demandait de penser à allonger la chaîne, sans quoi le lien
    pointait dans le vide — et rien ne l'aurait signalé.

    `largeur` choisit la mesure de la page (décision D6) : `prose` pour un texte
    suivi, `std` par défaut, `large` pour une carte ou un annuaire. La `.wrap` à
    1000 px disparaît.

    **`titre_dans_corps`** est l'échafaudage du portage, et il a vocation à
    disparaître. La forme cible met le `h1` dans le corps de chaque page — dans
    le bandeau photographique, quand il y en a un. Mais les fonctions de page
    n'émettent pas encore de `h1`, et le squelette v1 le fournissait : le retirer
    d'un coup laisserait chaque page sans titre de niveau 1, ce qui est une
    régression d'accessibilité et de référencement. Tant qu'une page ne fournit
    pas le sien, le squelette pose une accroche standard ; quand elle le
    fournit, elle passe `titre_dans_corps=True` et le squelette s'efface.

    `og_titre` diffère volontairement de `titre` : l'un sert le moteur de
    recherche, l'autre arrête le défilement dans un fil social. Ne pas les
    fusionner (consigne §4.1 de la communication).
    """
    # « pleine » : `main` reste NU et chaque section porte sa propre zone.
    # C'est ce que demande la charte v2 d'une page en sections — la règle
    # `main > section.section:nth-of-type(even)` y pose un fond alterné qui va
    # d'un bord à l'autre, ce qu'un `main` centré et borné rend impossible.
    zone = {"prose": "zone-prose", "std": "zone-std", "large": "zone-large",
            "pleine": ""}[largeur]

    # Le bandeau photographique, quand la page en a un. Il porte alors le fil
    # d'Ariane et le `h1` : les deux sont dedans, sur la photo, pas au-dessus.
    # Les pages qui n'en ont pas — fiches communales, briefs de substance —
    # gardent l'accroche sobre, et c'est une décision éditoriale, pas un
    # manque (cf. BANDEAUX).
    # `cle_bandeau` distingue TROIS états, et l'idiome `or` n'en distinguait que
    # deux — c'est ce qui a mis la photographie de la page Communes en tête des
    # 4 919 fiches communales et des 1 255 briefs de substance, publiées ainsi
    # le 16 août :
    #   None  -> non précisé, on prend la clé de la page (comportement par défaut)
    #   ""    -> refus explicite : pas de photographie, accroche sobre
    #   "xxx" -> emprunt d'une autre clé (cf. la page de contact)
    # La chaîne vide étant fausse en Python, `cle_bandeau or page_courante`
    # transformait le refus explicite en défaut silencieux. Le test doit porter
    # sur `is None`, jamais sur la véracité.
    cle_photo = page_courante if cle_bandeau is None else cle_bandeau
    photo = ("" if titre_dans_corps
             else bandeau(cle_photo, titre, sous_titre, fil, prefixe, formule))
    if photo:
        accroche, fil_hors_bandeau = photo, ""
    else:
        fil_hors_bandeau = fil_ariane(fil, prefixe)
        accroche = "" if titre_dans_corps else f"""
<div class="accroche">
  <div class="zone {zone}">
    <p class="surtitre">Observatoire de la potabilité réglementaire</p>
    <h1>{h(titre)}</h1>
    {f'<p class="chapo">{sous_titre}</p>' if sous_titre else ''}
    {'<p class="formule">« Ce n\'est pas l\'eau qui est devenue potable. C\'est la limite qui a bougé. »</p>' if formule else ''}
  </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(titre)} — Observatoire de la potabilité réglementaire</title>
<meta name="description" content="{h(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Observatoire de la potabilité réglementaire">
<meta property="og:title" content="{h(og_titre or titre)}">
<meta property="og:description" content="{h(og_description or description)}">
<meta property="og:image" content="{prefixe}assets/partage.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#08344C" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0C1620" media="(prefers-color-scheme: dark)">
<link rel="icon" type="image/svg+xml" href="{prefixe}assets/marque.svg">
<link rel="preload" as="font" type="font/woff2" href="{prefixe}assets/inter-var.woff2" crossorigin>
<link rel="stylesheet" href="{prefixe}assets/{empreinte('polices.css')}">
<link rel="stylesheet" href="{prefixe}assets/{empreinte('observatoire-v2.css')}">
{THEME_AVANT_RENDU}
</head>
<body>
{barre(page_courante, prefixe)}
{fil_hors_bandeau}
{accroche}
<main class="{f'zone {zone} accroche-suite' if zone else 'accroche-suite'}">
{corps}
</main>

{pied(version, calcule_le, corpus, prefixe)}
<script src="{prefixe}assets/{empreinte('barre.js')}"></script>
{scripts}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Départements publiables
# ---------------------------------------------------------------------------
# `None` = on publie tout ce qui est figé. Sinon, un tuple de codes.
#
# Pourquoi ce garde-fou existe. La base accumule des retombées d'essais : une
# commune collectée à la main, un département entamé par l'exemple de la
# documentation. Le 11 août 2026 elle portait ainsi des morceaux du 71 (14
# communes sur 563), du 32, du 65 et de l'01 (un bulletin) à côté de cinq
# départements réellement complets. Publier ces morceaux peindrait la carte
# d'un « non documenté » qui n'est pas un fait sur l'eau mais un fait sur notre
# collecte — et le §8bis fait de « non documentée » une catégorie visible, donc
# lue comme une information. **Un département à moitié collecté ment davantage
# qu'un département absent.**
#
# La liste est explicite et ne se déduit pas : un journal de moisson peut
# annoncer « terminé » sur une énumération elle-même incomplète (§13.4, point 6).
# C'est une décision éditoriale, elle se prend à la main.
DEPTS_PUBLIES = None


# « 99 » est la convention INSEE pour l'étranger. Le corpus en porte une
# commune — VENTIMILLE ITALIE, prélevée le 26 novembre 2025 —, entrée par une
# unité de distribution transfrontalière. Elle comptait comme un département
# dans les totaux de couverture et n'apparaissait sur aucune carte, le fond
# n'ayant pas de contour « 99 ».
#
# **Écartée de la vitrine, décision de Yannick du 16 août 2026 : la carte est
# française.** Écartée de l'AFFICHAGE seulement — la mesure reste en base, elle
# a été faite et elle est vraie. C'est la règle du projet : on ne supprime pas
# une donnée parce qu'elle dérange une carte, on dit pourquoi on ne la montre
# pas.
DEPTS_HORS_FRANCE = ("99",)


def _filtre_dept(colonne="dept"):
    """Fragment SQL restreignant aux départements publiables, et ses paramètres."""
    hors = (f" AND {colonne} NOT IN "
            f"({','.join('?' * len(DEPTS_HORS_FRANCE))})")
    args = list(DEPTS_HORS_FRANCE)
    if not DEPTS_PUBLIES:
        return hors, args
    return (f" AND {colonne} IN ({','.join('?' * len(DEPTS_PUBLIES))})" + hors,
            list(DEPTS_PUBLIES) + args)


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
               a.nb_mesures_notees, a.nb_mesures_lues, a.nom_uge,
               -- Le réseau réellement déclaré avec le bulletin. `nom_uge` est le
               -- GESTIONNAIRE : deux communes qui le partagent ne boivent pas
               -- forcément la même eau, et le rattachement, lui, s'est fait par
               -- réseau (`collecte.py`). Grouper sur le gestionnaire faisait
               -- donc afficher un regroupement que la donnée ne dit pas.
               a.noms_reseaux,
               -- Le plafond analytique du bulletin (§8bis obligation 11) : ce
               -- que le laboratoire ne pouvait pas voir. Il était calculé,
               -- figé, affiché sur la fiche — et absent de la liste, c'est-à-
               -- dire de l'endroit où l'on compare les communes entre elles.
               a.nb_aveugles, a.aveugles_pour_mille,
               -- La clé du bulletin retenu : elle sert à rattacher les comptes
               -- par registre hormonal, calculés en une requête pour tout le
               -- corpus plutôt qu'une par commune.
               cc.code_prelevement
        FROM couverture_communes cc
        LEFT JOIN analyses_figees a
               ON a.code_prelevement = cc.code_prelevement
              AND a.version_referentiel = cc.version_referentiel
        WHERE cc.version_referentiel = ?""" + _filtre_dept("cc.dept")[0] + """
        ORDER BY cc.commune
    """, [version] + _filtre_dept()[1]).fetchall()


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
          AND est_complet AND nb_depasse_applicable = 0 AND nb_bascules > 0""" + _filtre_dept()[0] + """
        ORDER BY nb_bascules DESC, commune
    """, [version] + _filtre_dept()[1]).fetchall()


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
# Les bornes de repli, avec la date du corpus qui les a produites — sans elle
# on ne peut pas savoir qu'elles ont vieilli. Elles ne servent que si la
# distribution est trop pauvre pour en calculer (moins de cinq départements).
BORNES_REPLI = (750, 1200, 1700, 2500)
BORNES_REPLI_DATE = "16 août 2026"


def bornes_couverture(comptes):
    """
    Les quatre bornes des cinq classes de la carte, **calculées sur ce qu'elles
    décrivent**.

    Ce ne sont pas des seuils réglementaires : rien ne fixe qu'un département
    « bien documenté » commence à 1 200 analyses. Ce sont des quintiles, et ils
    doivent suivre le corpus — sans quoi ils cessent de discriminer sans que
    rien ne le signale.

    C'est exactement ce qui s'était produit : l'échelle d'origine — 1-9, 10-49,
    50-199, 200 et plus — rangeait **21 départements sur 30 dans la même
    classe**, alors qu'ils vont de 445 à 5 327 analyses. La carte avait cinq
    couleurs et n'en montrait que deux. La consigne proposait de nouvelles
    bornes fixes ; les calculer évite d'avoir à les refaire au prochain
    département.

    Les départements à **zéro** sont exclus du calcul : ils ont leur classe à
    eux, `c0`, et les compter tirerait toutes les bornes vers le bas.
    """
    valeurs = sorted(d["bulletins"] for d in comptes.values() if d["bulletins"])
    if len(valeurs) < 5:
        return BORNES_REPLI

    def quintile(p):
        # Rang le plus proche, puis arrondi à un nombre qui se lit : une borne
        # à 1 187 n'apprend rien de plus qu'une borne à 1 200, et se retient
        # beaucoup moins bien.
        #
        # **Vers le haut, et jamais sous un pas.** Le corpus porte des
        # départements à une ou deux analyses — une commune rapatriée seule,
        # pas une collecte. Arrondir au plus proche ramenait la première borne
        # à zéro, et la légende annonçait « moins de 0 analyses » sur une
        # classe vide. Le plancher fait de cette première classe ce qu'elle
        # doit être : les départements à peine effleurés.
        v = valeurs[min(len(valeurs) - 1, int(round(p * (len(valeurs) - 1))))]
        pas = 50 if v < 1000 else 100
        return max(pas, -(-v // pas) * pas)

    bornes = [quintile(p) for p in (.2, .4, .6, .8)]
    # Deux quintiles peuvent tomber sur la même valeur si la distribution est
    # tassée. On écarte alors les doublons plutôt que de produire une classe
    # vide, qui ferait croire à un palier que personne n'occupe.
    sorties = []
    for b in bornes:
        if not sorties or b > sorties[-1]:
            sorties.append(b)
    while len(sorties) < 4:
        sorties.append(sorties[-1] + 1)
    return tuple(sorties[:4])


def classe_couverture(n, bornes=BORNES_REPLI):
    if not n:
        return "c0"
    for i, b in enumerate(bornes):
        if n < b:
            return f"c{i + 1}"
    return "c5"


def libelles_paliers(bornes):
    """« moins de 750 », « 750 à 1 199 »… — la légende dit ses bornes.

    Une carte qui colorie sans afficher ses seuils demande d'être crue, et
    surtout : sans eux, personne ne peut voir qu'une échelle a cessé de
    discriminer.
    """
    def n(x):
        return f"{x:,}".replace(",", " ")
    out = [("c1", f"moins de {n(bornes[0])} analyses")]
    for i in range(len(bornes) - 1):
        out.append((f"c{i + 2}", f"{n(bornes[i])} à {n(bornes[i + 1] - 1)}"))
    out.append((f"c{len(bornes) + 1}", f"{n(bornes[-1])} et plus"))
    out.append(("c0", "pas encore collecté"))
    return out


def carte_departements_svg(comptes, largeur=920, prefixe="", bornes=None):
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
    bornes = bornes or bornes_couverture(comptes)
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
        forme = (f'<path class="dept {classe_couverture(n, bornes)}" '
                 f'd="{"".join(traces)}"/>')

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

        # LE CERCLE BICOLORE DES COMMUNES RATTACHÉES.
        # Moitié gauche blanche : l'analyse vient d'ailleurs, du point de
        # prélèvement d'une autre commune du même réseau. Moitié droite : le
        # verdict de ce bulletin, qui vaut pour l'eau qui arrive ici.
        # Le demi-disque est un arc de rayon r allant du haut au bas du cercle,
        # refermé par la corde verticale — donc exactement la moitié.
        classe = c["niveau"]
        if c.get("teinte"):
            classe += " " + c["teinte"]
        forme = f'<circle class="{classe}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
        if c.get("teinte"):
            forme += (f'<path class="demi-emprunt" '
                      f'd="M {x:.1f},{y - r:.1f} A {r},{r} 0 0 0 {x:.1f},{y + r:.1f} Z"/>')

        points.append(
            f'<a class="pt{" vedette" if vedette else ""}" href="{prefixe}{c["url"]}" '
            f'aria-label="{h(titre)}">'
            f'<title>{h(titre)}</title>{forme}</a>')

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
REFUS = [
    ("Interroger la norme, jamais accuser les acteurs.",
     "Le sujet est la construction réglementaire du seuil — jamais l'agence de "
     "santé, le distributeur, le maire ou l'agriculteur."),
    ("Outil de conscience, pas de prescription.",
     "Aucune marque, aucun produit, aucun conseil individuel, nulle part, pas "
     "même en note."),
    ("Aucune valeur écrite sans sa source,",
     "et une source qui porte sur la substance d'à côté n'est pas une source."),
    ("Aucun verdict sans son dénominateur.",
     "« 323 substances notées sur 383 » accompagne toute conclusion."),
    ("Aucune comparaison sans l'effort de recherche de chaque terme,",
     "et un département se compare d'abord à lui-même."),
    ("Aucune série dans le temps à liste variable",
     "— sinon une baisse des recherches passe pour une baisse des détections."),
    ("Un faux positif coûte plus cher qu'un faux négatif.",
     "Dans le doute, le verdict n'est pas prononcé : il est listé comme "
     "indéterminé."),
    ("Un effet n'est jamais attribué à un texte qui lui est postérieur.",
     "Une cause écrite après le fait qu'elle prétend expliquer n'est pas une "
     "cause."),
]

def chiffres_dossiers(con, version):
    """
    Les nombres des cartes qui SUIVENT le corpus, calculés à la construction.

    Trois cartes seulement en portent : les autres citent un fait daté qui ne
    bouge plus — la rupture du Tarn (627 → 344), les six enquêtes de sourçage,
    les 2 653 communes de l'erreur du 13 août. Figer ce qui est daté et
    calculer ce qui vit, c'est la même règle des deux côtés (§2.10).

    Les maquettes portaient ces trois nombres en dur, et ils avaient déjà
    vieilli quand elles nous sont arrivées : la maquette de l'index annonce
    « 390 paramètres sans terme de comparaison » là où la vue en compte 380.
    Un chiffre d'accroche écrit à la main est un chiffre faux à retardement —
    le constat est celui de `page_accueil`, et il vaut ici mot pour mot.
    """
    ou, args = _filtre_dept()
    bascules, sans_seuil = con.execute(f"""
        SELECT COALESCE(SUM(nb_bascules), 0),
               COALESCE(SUM(nb_mesures_lues - nb_mesures_notees), 0)
        FROM analyses_figees WHERE version_referentiel = ?{ou}
    """, [version] + args).fetchone()

    # `v_parametres_sans_seuil`, et NON `v_parametres_non_apparies` : la carte
    # parle de ce que le projet ne juge pas, pas de ce qu'il n'a pas su
    # rapprocher du référentiel. Les deux ont eu la même réponse tant que le
    # référentiel était pauvre ; le chantier C11 a rompu cette identité le
    # 15 août 2026 (CLAUDE.md §4).
    n_param = con.execute(
        "SELECT COUNT(*) FROM v_parametres_sans_seuil").fetchone()[0]

    # LE CHIFFRE DE LA CARTE VIENT DE LA MÊME LECTURE QUE LE DOSSIER.
    # Écrit à la main de part et d'autre, l'accueil aurait fini par annoncer
    # 18 communes pendant que le dossier en montrerait 39 — et c'est le lecteur
    # qui aurait raison de ne plus croire ni l'un ni l'autre.
    panel = DPR.faits()
    return {"bascules": bascules, "sans_seuil": sans_seuil,
            "parametres_sans_seuil": n_param,
            "panel_communes": panel["n_communes"],
            "panel_instruites": panel["instruites"],
            "panel_departements": panel["departements_balayes"],
            "panel_controles": panel["n_controles"]}


def _n(x):
    """12345 -> « 12 345 ». L'espace fine insécable est le séparateur du site."""
    return f"{x:,}".replace(",", " ")


# Les huit dossiers. Le chiffre de tête et le titre viennent de
# COMMUNICATION_OBSERVATOIRE §2.6 ; l'ordre est le sien — le plus fort en tête,
# l'erreur du projet en clôture, parce qu'annoncer l'aveu vaut mieux que de le
# cacher au milieu.
#
# `chiffre` est un triplet (tête, mot du milieu, queue) — « 627 → 344 » et
# « 18 communes » sont la même forme, avec ou sans queue. Un appelable reçoit
# les nombres calculés ; une valeur littérale est un fait daté qui ne bouge
# plus. Rien entre les deux : un nombre qui vit et qu'on écrit à la main est
# exactement ce que ce fichier ne veut plus contenir.
#
# `etat` commande la balise : « publie » rend un <a>, tout le reste un <div>.
# Une carte « en préparation » qui serait un lien mènerait à une page absente,
# et c'est le coût le plus élevé qu'un index puisse faire payer (consigne §11.1).
DOSSIERS = [
    {"cl": "dossier--phare dossier--rouge", "num": "01", "etat": "publie",
     "lien": "dossier-panel-reduit.html",
     "chiffre": lambda c: (_n(c["panel_communes"]), "communes", ""),
     "titre": "Une conformité peut s'obtenir en cessant de mesurer",
     "corps":
         "49 substances étaient en dépassement à la dernière analyse complète, et "
         "n'ont plus été mesurées depuis au moins deux ans. Le « total des "
         "pesticides » est une limite opposable, et c'est une somme : cesser d'en "
         "mesurer les termes rend l'agrégat incalculable.",
     "corps_index":
         "49 paramètres étaient en dépassement à la dernière analyse complète, et "
         "n'ont plus été mesurés depuis deux à dix ans. Le «&nbsp;total des "
         "pesticides&nbsp;» est une limite opposable, et c'est une <b>somme</b>&nbsp;: "
         "cesser d'en mesurer les termes rend l'agrégat incalculable.",
     # 61 et 55 viennent de `ANALYSE_2026-08-12.md`, qui les tire du corpus figé
     # et non de la synthèse : ils restent dans l'argument versionné. 555 est
     # dans la synthèse, donc il se calcule. La frontière est là, et nulle part
     # ailleurs.
     "precision": lambda c:
         "Sur 61 analyses complètes de ces communes, 55 sont non conformes. "
         f"<b>{_n(c['panel_controles'])} contrôles de routine</b> ont eu lieu "
         "depuis&nbsp;: ce n'est jamais un abandon de surveillance.",
     "pied": 'Lire le dossier <span aria-hidden="true">→</span>',
     "tag": lambda c: "Ouvert le 12 août 2026 · "
                      f"{c['panel_communes']} communes instruites une à une",
     "tag_accueil": "sujet le plus avancé · ouvert le 12 août 2026"},

    {"cl": "dossier--bascule", "num": "02", "etat": "attente",
     # La carte parle du déplacement des seuils : son nombre est celui des
     # mesures qui basculent, la même somme que l'accueil affiche déjà.
     "chiffre": lambda c: (_n(c["bascules"]), "mesures", ""),
     "titre": "Le déplacement des seuils",
     "corps":
         "Des bulletins déclarés conformes aujourd'hui qui ne l'auraient pas été il "
         "y a dix ans. Cas d'école : le chlorothalonil R471811, dont un "
         "reclassement déplace deux verdicts le même jour — sa propre limite, et le "
         "périmètre du total des pesticides dont il sort.",
     "corps_index":
         "Des bulletins déclarés conformes aujourd'hui qui ne l'auraient pas été il "
         "y a dix ans. Cas d'école&nbsp;: le chlorothalonil R471811, dont un "
         "reclassement déplace deux verdicts le même jour.",
     "pied": 'Les chiffres sont sur <a href="reclassements.html">reclassements</a>',
     "tag_accueil": "sujet fondateur"},

    {"cl": "dossier--ambre", "num": "03", "etat": "attente",
     "chiffre": ("200", "vs", "700"),
     "titre": "On ne trouve que ce qu'on cherche",
     "corps":
         "Une eau « correcte » sur 200 substances est une information plus faible "
         "qu'une eau « moyenne » sur 700. Le nombre de substances recherchées n'est "
         "pas un indicateur de qualité : c'est un indicateur d'effort. Sans cette "
         "précaution, un territoire qui cherche bien passe pour un territoire qui "
         "va mal.",
     "corps_index":
         "Une eau «&nbsp;correcte&nbsp;» sur 200 substances est une information plus "
         "faible qu'une eau «&nbsp;moyenne&nbsp;» sur 700. Le nombre de substances "
         "recherchées est un indicateur d'effort, pas de qualité.",
     "pied": 'La règle est dans <a href="methode.html">la méthode</a>',
     "tag_accueil": "effort de recherche"},

    {"cl": "dossier--gris", "num": "04", "etat": "attente",
     "chiffre": ("627", "→", "344"),
     "titre": "La liste change, pas l'eau",
     "corps":
         "Dans le Tarn, 298 substances disparaissent de la liste en trois semaines. "
         "Mais la lecture naïve est fausse, et le projet l'a écartée lui-même : à "
         "liste constante, le Tarn est plat sur onze ans. Le mécanisme est "
         "administratif — la liste est régionale, et figée par les marchés "
         "pluriannuels d'analyses.",
     "corps_index":
         "Dans le Tarn, 298 substances disparaissent de la liste en trois semaines. "
         "La lecture naïve est fausse et le projet l'a écartée lui-même&nbsp;: à "
         "liste constante, le Tarn est plat sur onze ans.",
     "pied": "Rupture de panel 2019-2020",
     "tag_accueil": "rupture du panel 2019-2020"},

    {"cl": "dossier--gris", "num": "05", "etat": "attente",
     "chiffre": lambda c: (_n(c["sans_seuil"]), "mesures", ""),
     "titre": "Ce sur quoi rien ne se prononce",
     "corps":
         "Des substances effectivement recherchées, effectivement mesurées, "
         "qu'aucun texte ne compare à quoi que ce soit. Ce n'est pas un défaut du "
         "projet : c'est un fait sur la norme. Une part massive de ce que les "
         "laboratoires mesurent n'a aucune limite opposable en face.",
     "corps_index":
         "Des substances effectivement recherchées et mesurées, qu'aucun texte ne "
         "compare à quoi que ce soit. Ce n'est pas un défaut du projet&nbsp;: c'est "
         "un fait sur la norme.",
     "pied": lambda c:
         f"{c['parametres_sans_seuil']} paramètres sans terme de comparaison, dans "
         '<a href="substances.html">le répertoire</a>',
     "tag_accueil": "trouvé le 12 août 2026"},

    {"cl": "dossier--gris", "num": "06", "etat": "attente",
     "chiffre": ("0", "≠", "0"),
     "titre": "Zéro n'est pas zéro",
     "corps":
         "Un résultat à zéro signifie « en dessous de ce que le laboratoire sait "
         "mesurer », jamais « absent ». Un laboratoire qui ne trouve rien ne mesure "
         "pas zéro. Et il y a trois états, jamais deux : conforme, dépassement, et "
         "<b>indéterminé</b>.",
     "corps_index":
         "Un résultat à zéro signifie «&nbsp;en dessous de ce que le laboratoire sait "
         "mesurer&nbsp;», jamais «&nbsp;absent&nbsp;». Et il y a trois états, jamais "
         "deux&nbsp;: conforme, dépassement, <b>indéterminé</b>.",
     "pied": 'Règle d\'affichage, dans <a href="methode.html">la méthode</a>',
     "tag_accueil": "règle d'affichage"},

    {"cl": "dossier--eau", "num": "07", "etat": "attente",
     "chiffre": ("6", "/", "6"),
     "titre": "Des substances sans aucune règle au monde",
     "corps":
         "Six enquêtes de sourçage, six fois la même réponse : il n'existe nulle "
         "part de valeur opposable à laquelle comparer cette mesure. Le projet a "
         "refusé d'en choisir une — choisir une valeur, c'est produire le verdict "
         "au lieu de le constater.",
     "corps_index":
         "Six enquêtes de sourçage, six fois la même réponse&nbsp;: il n'existe nulle "
         "part de valeur opposable. Le projet a refusé d'en choisir une — choisir "
         "une valeur, c'est produire le verdict au lieu de le constater.",
     "pied": "Enquêtes rendues",
     "tag_accueil": "enquêtes rendues"},

    {"cl": "dossier--aveu", "num": "08", "etat": "attente",
     "chiffre": ("2 653", "communes", ""),
     "titre": "Le mot employé fait partie du résultat",
     "corps":
         "Le site écrivait « eau du réseau X » en désignant en réalité le "
         "gestionnaire. Un même gestionnaire exploite souvent plusieurs réseaux, "
         "qui ne distribuent pas la même eau. La phrase était sur 2 829 fiches ; "
         "135 regroupements réunissaient des communes qui ne boivent pas la même "
         "eau. Corrigé le jour même — et raconté ici.",
     "corps_index":
         "Le site écrivait «&nbsp;eau du réseau X&nbsp;» en désignant en réalité le "
         "gestionnaire. La phrase était sur 2 829 fiches&nbsp;; 135 regroupements "
         "réunissaient des communes qui ne boivent pas la même eau. Corrigé le jour "
         "même.",
     "tag": "Erreur du projet · corrigée le 13 août 2026",
     "pied": "À raconter en entier",
     "tag_accueil": "erreur du projet, corrigée le 13 août 2026"},
]


def _valeur(v, ctx):
    """Une entrée de `DOSSIERS` est soit un fait daté, soit un calcul."""
    return v(ctx) if callable(v) else v


# Les quatre temps de la fabrication d'un dossier, en pied d'index. Le
# quatrième n'est pas « fourni » : c'est la relecture humaine, et c'est elle
# qui limite le débit.
FABRICATION = [
    ("1 · le fait", "Une requête, pas une intuition",
     "Un dossier part d'un balayage du corpus figé, reproductible, dont le "
     "script est au dépôt. Le fait est vérifiable ligne à ligne dans les "
     "fichiers publiés.", True),
    ("2 · le dénominateur", "Sur combien, et cherché où",
     "Aucun compte n'est publié sans ce sur quoi il porte. «&nbsp;{communes} "
     "communes&nbsp;» ne s'écrit jamais sans «&nbsp;sur {instruites} "
     "instruites, dans {departements} départements&nbsp;».", True),
    ("3 · le partage", "Établi, et non établi",
     "Les deux listes sont écrites côte à côte, jamais l'une sous l'autre. "
     "C'est la pièce la plus importante&nbsp;: elle empêche le constat de "
     "glisser vers le procès.", True),
    ("4 · la relecture", "Une personne, pas un lot",
     "Chaque dossier nomme des communes, donc des exploitants implicites. Rien "
     "n'est publié sans une lecture humaine, phrase par phrase. C'est ce qui "
     "limite le débit à {debit}.", False),
]


def page_a_propos(con, version, calcule_le):
    """
    « Pourquoi ce site existe » — le mot personnel, la méthode, puis la zone
    Éditions Mytae.

    AUCUN CHIFFRE DE CORPUS N'EST ÉCRIT DANS LE GABARIT, et c'est la raison
    d'être de cette fonction. Le document de réécriture du 19 août 2026 en
    portait quatre, arrêtés au 13 août : 25 284 analyses, 17 départements,
    1 151 bascules, 772 bulletins. Six jours plus tard le corpus avait doublé.
    Une page qui reproche aux autres leurs chiffres non datés ne peut pas
    publier les siens périmés — ils se recalculent donc à chaque construction,
    et la page affiche la date à côté.

    Les huit refus sont rendus ICI, dépliables, et non derrière un lien : le
    document demandait « une page autonome et citable », qui n'existe pas. Les
    mettre sous la main du lecteur vaut mieux qu'un lien vers une ancre de
    l'accueil — et évite d'annoncer une page qui n'est pas écrite.
    """
    ou, args = _filtre_dept()
    n_bulletins, n_bascules, n_these, n_depts = con.execute(f"""
        SELECT COUNT(*), COALESCE(SUM(nb_bascules), 0),
               COUNT(*) FILTER (WHERE est_complet AND nb_depasse_applicable = 0
                                  AND nb_bascules > 0),
               COUNT(DISTINCT dept)
        FROM analyses_figees WHERE version_referentiel = ?{ou}
    """, [version] + args).fetchone()

    refus = "".join(f"<li><b>{h(fort)}</b> {suite}</li>" for fort, suite in REFUS)

    corps = lire("a-propos-corps.html")
    for cle, val in (("n_bulletins", _n(n_bulletins)),
                     ("n_bascules", _n(n_bascules)),
                     ("n_these", _n(n_these)),
                     ("n_depts", str(n_depts)),
                     ("calcule_le", BF._date_fr(calcule_le)),
                     ("version", version),
                     ("refus", refus)):
        corps = corps.replace("{{" + cle + "}}", val)
    return corps


def page_dossier_panel_reduit(version):
    """
    Le premier dossier — « une conformité peut s'obtenir en cessant de mesurer ».

    Les douze sections du §11.2 de la consigne, dans leur ordre, et cet ordre
    porte l'argument : le mécanisme AVANT tout chiffre, les 555 contrôles AVANT
    la liste des abandons, l'hypothèse écartée AVANT celle retenue, et
    « établi / non établi » côte à côte avant la conclusion.

    **Le partage entre ce qui se calcule et ce qui s'écrit.** Tout ce que la
    synthèse figée porte vient de `dossier_panel_reduit` — les quatre nombres,
    les dix-huit communes, les douze paramètres, la chronologie, la géographie,
    et jusqu'aux deux mesures du contraste, lues dans le dossier commune de
    Nottonville. Ce qui reste en dur ici vient de `ANALYSE_2026-08-12.md`, le
    fichier d'argument versionné : les 61 analyses complètes dont 55 non
    conformes, et la série de nitrates 60 → 38,7 → 11,1, que l'étude d'ensemble
    ne porte pas sous forme datée (consigne §11.5).

    **Deux écarts à la maquette, tranchés par Yannick le 17 août 2026** :
    le tableau des paramètres rend ses **douze lignes réelles** là où la
    maquette en fond deux paires et n'en montre que dix — réunir deux
    métabolites distincts ferait disparaître un abandon du décompte ; et la
    chronologie rend **huit barres** au lieu de sept, 2017 compris bien qu'il
    vaille zéro — une année sautée fait lire un cycle là où il y a un trou.
    """
    f = DPR.faits()
    NITRATE, PESTICIDE = "Nitrates (en NO3)", "Atrazine déséthyl"
    ctr = DPR.contraste("28283", [NITRATE, PESTICIDE])

    # --- 3. les dix-huit communes ---------------------------------------
    lignes_c = "".join(
        f'<tr><td data-v="{h(c["commune"])}"><b class="commune">{h(c["commune"])}</b> '
        f'<span style="color:var(--ink-faint)">({h(c["dept"])})</span></td>'
        f'<td class="num" data-v="{c["nb_depassements"]}">{c["nb_depassements"]}</td>'
        f'<td class="num" data-v="{c["nb_abandonnes"]}">{c["nb_abandonnes"]}</td>'
        f'<td class="num" data-v="{c["nb_controles_depuis"]}">{c["nb_controles_depuis"]}</td>'
        f'<td class="num" data-v="{c["plus_ancien_mois"]}">'
        f'<b>{c["plus_ancien_mois"]}</b> mois</td></tr>'
        for c in f["communes"])

    # --- 4. ce qui cesse d'être mesuré ----------------------------------
    def _plage(p):
        return (f'{p["mois_min"]} mois' if p["mois_min"] == p["mois_max"]
                else f'{p["mois_min"]} à {p["mois_max"]} mois')

    # Les deux premiers sont mis en avant : ce sont eux le résultat.
    lignes_p = "".join(
        f'<tr><td>{"<b class=\"commune\">" if i < 2 else ""}{h(p["libelle"])}'
        f'{"</b>" if i < 2 else ""}</td>'
        f'<td class="num">{"<b class=\"commune\">" if i < 2 else ""}{p["communes"]}'
        f'{"</b>" if i < 2 else ""}</td>'
        f'<td>{_plage(p)}</td></tr>'
        for i, p in enumerate(f["parametres"]))

    # --- 6. la chronologie ----------------------------------------------
    barres = "".join(
        f'<div class="chrono-ligne{" chrono-ligne--pic" if a["pic"] else ""}">'
        f'<span class="chrono-an">{a["annee"]}</span>'
        f'<span class="chrono-piste"><i style="width:{a["part"]}%"></i></span>'
        f'<span class="chrono-n">{a["n"]}</span></div>'
        for a in f["chronologie"])
    pics = [str(a["annee"]) for a in f["chronologie"] if a["pic"]]
    pics_txt = ", ".join(pics[:-1]) + " et " + pics[-1] if len(pics) > 1 else "".join(pics)

    # --- 8. la géographie ------------------------------------------------
    lignes_g = "".join(
        f'<tr><td>{h(d["nom"] or "—")} ({h(d["code"])})</td>'
        f'<td class="num">{d["instruites"]}</td>'
        f'<td class="num">{f"<b>{d["avec_abandon"]}</b>" if d["avec_abandon"] else 0}</td></tr>'
        for d in f["departements"])
    tete = f["departements"][0]
    n_tete = next((d["avec_abandon"] for d in f["departements"]
                   if d["code"] == tete["code"]), 0)

    return f"""
<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Le mécanisme, en trois temps</h2>
    <div class="pieces">
      <div class="piece"><span class="tag">1</span>
        <h3>Une analyse complète trouve des dépassements</h3>
        <p>Plus de 200 paramètres. Elle relève un ou plusieurs dépassements, et l'administration
          prononce une <b>non-conformité</b>.</p></div>
      <div class="piece"><span class="tag">2</span>
        <h3>Les suivantes sont des contrôles de routine</h3>
        <p>Vingt à quarante paramètres, tels que <b>la réglementation les prescrit</b> entre deux
          analyses complètes.</p></div>
      <div class="piece piece--fournie"><span class="tag">3</span>
        <h3>Ces contrôles ne portent plus les paramètres en cause</h3>
        <p>Ils concluent «&nbsp;conforme aux exigences de qualité en vigueur <b>pour l'ensemble des
          paramètres mesurés</b>&nbsp;». Clause exacte, et que personne ne lit.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Le résultat, en quatre nombres</h2>
    <div class="chiffres">
      <div class="chiffre rouge"><span class="n">{f["n_communes"]}</span>
        <span class="l">communes sur {f["instruites"]} instruites<br>dans
          {f["departements_balayes"]} départements publiés</span></div>
      <div class="chiffre rouge"><span class="n">{f["n_parametres"]}</span>
        <span class="l">paramètres en dépassement<br>plus mesurés depuis au moins
          {f["mois_abandon"] // 12} ans</span></div>
      <div class="chiffre"><span class="n">{_n(f["n_controles"])}</span>
        <span class="l">contrôles de routine depuis<br>l'eau est suivie de près</span></div>
      <div class="chiffre gris"><span class="n">{f["plus_ancien_mois"]}</span>
        <span class="l">mois pour le plus ancien abandon<br>dix ans</span></div>
    </div>
    <p class="bnote"><b>Sur les 61 analyses complètes que le corpus détient pour ces
      {f["n_communes"]} communes, 55 sont non conformes — 90&nbsp;%. Et pour 15 communes sur
      {f["n_communes"]}, elles le sont toutes.</b> Ce ne sont pas des accidents ponctuels&nbsp;:
      c'est un état.</p>
    <p class="bnote"><b>{_n(f["n_controles"])} contrôles, ce n'est pas un abandon de
      surveillance</b> — c'est même l'inverse. Ces eaux sont suivies de près, sur un périmètre
      restreint. Le dire est nécessaire, sinon tout ce qui suit se lit de travers.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Les {f["n_communes"]} communes</h2>
    <p class="chapo" style="margin-bottom:var(--e-5)">Rangées par ancienneté du plus ancien
      abandon. Les en-têtes trient&nbsp;: <b>aucun ordre n'est le bon</b>, et un classement par
      nombre de dépassements dirait d'abord l'effort de recherche.</p>
    <div class="tableau tableau--annuaire">
      <div class="tableau-defile">
        <table data-triable>
          <thead>
            <tr>
              <th data-type="txt" aria-sort="none"><button class="th-tri" type="button">Commune</button></th>
              <th class="num" data-type="num" aria-sort="none"><button class="th-tri" type="button">Dépassements</button></th>
              <th class="num" data-type="num" aria-sort="none"><button class="th-tri" type="button">Abandonnés</button></th>
              <th class="num" data-type="num" aria-sort="none"><button class="th-tri" type="button">Contrôles depuis</button></th>
              <th class="num" data-type="num" aria-sort="descending"><button class="th-tri" type="button">Plus ancien abandon</button></th>
            </tr>
          </thead>
          <tbody>{lignes_c}</tbody>
        </table>
      </div>
    </div>
    <p class="bnote">«&nbsp;Abandonnés&nbsp;» : parmi les paramètres en dépassement à la dernière
      analyse complète, ceux dont la dernière mesure a plus de {f["mois_abandon"]} mois. <b>Un
      paramètre recontrôlé une fois puis laissé compte ici comme abandonné</b> : ce qui se mesure
      est l'ancienneté de la dernière mesure, pas son existence.</p>
    <p class="bnote">Un dossier commune par commune existe pour chacune, avec la liste datée de ses
      analyses. Ils sont dans le dépôt, sous
      <code>data/etudes/conformite_sur_panel_reduit/</code>.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Ce qui cesse d'être mesuré — et ce n'est pas n'importe quoi</h2>
    <div class="tableau" style="max-width:var(--l-standard)">
      <div class="tableau-defile">
        <table>
          <thead><tr><th>Paramètre</th><th class="num">Communes</th>
            <th>Ancienneté de la dernière mesure</th></tr></thead>
          <tbody>{lignes_p}</tbody>
        </table>
      </div>
    </div>
    <p class="bnote" style="margin-top:var(--e-5)"><b>Ce sont des métabolites de pesticides, et
      surtout ceux de l'atrazine.</b> L'atrazine est interdite en France depuis 2003&nbsp;; ce sont
      ses produits de dégradation qui persistent dans les nappes vingt ans après. Le paramètre le
      plus souvent laissé de côté est précisément celui qui témoigne d'une contamination ancienne
      et durable.</p>
    <p class="bnote">Les libellés sont ceux de la source, sans retouche&nbsp;: deux métabolites du
      métazachlore comptent pour deux lignes, et non pour une. <b>Les réunir ferait disparaître un
      abandon du décompte.</b></p>

    <h3 class="sec" style="margin-top:var(--e-8)">Le mécanisme qui mérite d'être vu</h3>
    <p class="chapo" style="margin-bottom:var(--e-5)">Le «&nbsp;total des pesticides
      analysés&nbsp;» est laissé de côté dans <b>12 communes sur {f["n_communes"]}</b>. Ce n'est
      pas un paramètre comme les autres&nbsp;: c'est une <b>limite de qualité opposable</b> —
      0,5 µg/L — et c'est une <b>somme</b>.</p>
    <p class="note note--attention"><b>Une somme ne se mesure pas&nbsp;: elle se calcule à partir
      de ses termes.</b> Cesser de mesurer les pesticides individuels ne fait donc pas seulement
      disparaître chaque pesticide de l'affichage — <b>cela rend l'agrégat opposable
      incalculable</b>. Le paramètre le plus protecteur du dispositif s'éteint de lui-même quand
      ses composants s'éteignent.</p>
    <p class="bnote">C'est la règle du projet appliquée à l'inverse&nbsp;: <em>une somme ne se
      compare jamais sans sa date et son périmètre</em> — ici, le périmètre est vide.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Quand les arrêts ont-ils lieu&nbsp;?</h2>
    <p class="chapo" style="margin-bottom:var(--e-5)"><b>Une hypothèse séduisante, et
      fausse&nbsp;: «&nbsp;vingt ans après l'interdiction&nbsp;».</b> L'atrazine est interdite en
      2003&nbsp;; Thiville cesse de la suivre en octobre 2023. Vingt ans tout juste. <b>Le corpus
      ne porte pas cette règle</b> — Oinville-Saint-Liphard s'arrête en 2016, Gas et Nottonville en
      2018.</p>
    <div class="chrono">{barres}</div>
    <p class="bnote" style="margin-top:var(--e-6)"><b>Ce que la chronologie montre&nbsp;: des
      pics.</b> {h(pics_txt)} — deux à trois ans d'écart, régulièrement. C'est la signature d'un
      <b>cycle</b>, pas d'une décision prise molécule par molécule. Les années sans arrêt sont
      montrées aussi&nbsp;: <b>une année sautée ferait lire un cycle là où il y a un trou.</b></p>
    <p class="bnote">Le mécanisme candidat est connu&nbsp;: les <b>marchés pluriannuels d'analyses
      des ARS</b>, qui figent la liste régionale des paramètres recherchés pour la durée du marché
      (instruction DGS/EA4/2020/177, source <code>REG-05</code>).</p>
    <p class="note note--attention"><b>Formulation tenue, et elle n'est pas négociable&nbsp;:</b>
      «&nbsp;arrêts groupés en {h(pics_txt)}, <b>compatibles avec</b> des renouvellements de
      marché&nbsp;» — jamais «&nbsp;causés par&nbsp;». Établir la cause demanderait les marchés
      eux-mêmes&nbsp;: date de notification, durée, liste annexée. <b>Ces documents sont
      publics</b>, et c'est le chantier qui prolonge cette étude.</p>
    <p class="bnote">C'est exactement le piège déjà rencontré sur le Tarn, où une rupture de panel
      de janvier 2020 avait failli être attribuée à une instruction de <b>décembre 2020</b> —
      postérieure de onze mois. <b>Attribuer un effet à une date qui l'arrange</b> est l'erreur que
      le projet s'interdit, transposée du seuil au programme d'analyse.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Le contraste, commune par commune</h2>
    <p class="chapo" style="margin-bottom:var(--e-5)">Partout le même partage, et il est
      net&nbsp;: <b>les nitrates continuent d'être mesurés</b>, 27 à 37 fois selon les communes, la
      dernière il y a trois ou quatre mois. <b>Les pesticides ne le sont plus</b>&nbsp;: zéro à deux
      fois, la dernière il y a trois à dix ans.</p>

    <p class="surtitre" style="margin-bottom:var(--e-2)">Nottonville (28283) — même commune, même eau, même robinet</p>
    <div class="contraste">
      <div class="suivi">
        <span class="lib">{h(NITRATE)}</span>
        <span class="val">{ctr[NITRATE]["mesures_depuis"]} mesures</span>
        <p>La dernière le {h(BF._date_fr(ctr[NITRATE]["derniere_mesure"]))}, il y a
          {ctr[NITRATE]["mois"]} mois. Ils étaient à
          <b>{h(ctr[NITRATE]["valeur"])}&nbsp;{h(ctr[NITRATE]["unite"])}</b> pour une limite de
          {h(ctr[NITRATE]["limite"])}.</p>
      </div>
      <div class="abandon">
        <span class="lib">{h(PESTICIDE)}</span>
        <span class="val">{ctr[PESTICIDE]["mesures_depuis"]} mesure</span>
        <p>Une seule, le {h(BF._date_fr(ctr[PESTICIDE]["derniere_mesure"]))}, et jamais depuis —
          {ctr[PESTICIDE]["mois"]} mois. Elle était à
          <b>{h(ctr[PESTICIDE]["valeur"])}&nbsp;{h(ctr[PESTICIDE]["unite"])}</b> pour une limite de
          {h(ctr[PESTICIDE]["limite"])}.</p>
      </div>
    </div>

    <p class="bnote" style="margin-top:var(--e-6)"><b>Et là où le nitrate a été traité, ça se
      voit.</b> À Nottonville il passe de <b>60 mg/L</b> à <b>38,7</b> puis <b>11,1</b> en huit
      mois, et il y reste. <b>Quelque chose a été fait, et ça a marché.</b> Il faut le dire aussi
      nettement que le reste — c'est ce qui rend le silence sur les pesticides visible par
      contraste, et c'est aussi ce qui prouve qu'une valeur peut baisser pour de bon.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">La géographie — et la prudence qu'elle impose</h2>
    <p class="chapo" style="margin-bottom:var(--e-5)"><b>{n_tete} des {f["n_communes"]} communes
      sont en {h(tete["nom"])}</b>, la Beauce. Les autres sont en Tarn-et-Garonne et dans le
      Gers.</p>
    <div class="tableau" style="max-width:var(--l-standard)">
      <div class="tableau-defile">
        <table>
          <thead><tr><th>Département</th><th class="num">Communes instruites</th>
            <th class="num">Avec abandon</th></tr></thead>
          <tbody>{lignes_g}</tbody>
        </table>
      </div>
    </div>
    <p class="note note--attention" style="margin-top:var(--e-5)"><b>Ce tableau ne se lit pas comme
      une carte de France.</b> Deux réserves, et elles sont dirimantes.</p>
    <p class="bnote"><b>L'{h(tete["nom"])} pèse {tete["instruites"]} des {f["instruites"]} communes
      instruites</b>, parce que c'est le département le plus profondément collecté du corpus —
      plusieurs analyses complètes par commune, là où d'autres n'en ont qu'une. <b>Un département
      mieux documenté produit mécaniquement plus de candidats.</b> On ne trouve que ce qu'on
      cherche, et aucune comparaison de territoires ne se fait sans afficher l'effort de chaque
      terme.</p>
    <p class="bnote"><b>Le corpus couvrait {f["departements_balayes"]} départements au moment de
      l'étude, pas la France.</b> Rien ici ne dit ce qu'il en est ailleurs.</p>
    <p class="bnote">Ce qui reste vrai malgré ces réserves&nbsp;: <b>la Beauce est une zone de
      grande culture céréalière, et les paramètres laissés de côté sont ceux des herbicides de
      maïs.</b> La cohérence entre le territoire et les molécules n'est pas un artefact de
      collecte.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Qui décide de ce qui est analysé</h2>
    <p class="chapo" style="margin-bottom:var(--e-5)"><b>Ce n'est pas l'exploitant, et ce n'est pas
      décidé commune par commune.</b> La liste des paramètres recherchés lors d'un contrôle
      sanitaire est <b>régionale</b>, et elle est figée par les <b>marchés pluriannuels d'analyses
      passés par les ARS</b>&nbsp;: le laboratoire retenu applique, pour la durée du marché, le
      catalogue qui y est annexé.</p>
    <p class="note note--attention"><b>Un exploitant n'a pas la main sur ce qu'on mesure chez
      lui.</b> Chercher la responsabilité du côté de la commune ou du distributeur serait donc
      doublement faux&nbsp;: contraire à la règle du projet — interroger la norme, jamais les
      acteurs — et contraire au mécanisme.</p>
    <p class="bnote"><b>Chantier ouvert, et il est documentaire, pas informatique&nbsp;:</b>
      retrouver les marchés d'analyses de l'ARS Centre-Val de Loire — date de notification, durée,
      liste de paramètres annexée. Ces pièces sont publiques. Elles transformeraient
      «&nbsp;compatible avec un renouvellement de marché&nbsp;» en fait établi, <b>ou
      l'infirmeraient</b>.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Ce que ce dossier établit — et ce qu'il n'établit pas</h2>
    <p class="chapo" style="margin-bottom:var(--e-6)">Les deux listes sont écrites côte à côte, et
      jamais l'une sous l'autre&nbsp;: <b>c'est la pièce la plus importante du dossier.</b></p>
    <div class="etabli">
      <div class="etabli-oui">
        <h3>Établi, et vérifiable ligne à ligne</h3>
        <ul>
          <li>Dans <b>{f["n_communes"]} communes</b>, des paramètres qui rendaient l'eau non
            conforme lors de la dernière analyse complète <b>ne sont plus mesurés depuis deux à dix
            ans</b>.</li>
          <li>Leur <b>dernière valeur connue était au-dessus de la limite</b> applicable ce
            jour-là.</li>
          <li>Les <b>{_n(f["n_controles"])} contrôles</b> qui ont suivi concluent
            «&nbsp;conforme aux exigences de qualité en vigueur <b>pour l'ensemble des paramètres
            mesurés</b>&nbsp;».</li>
          <li>Les arrêts se <b>groupent en {h(pics_txt)}</b>.</li>
        </ul>
      </div>
      <div class="etabli-non">
        <h3>Non établi, et à ne jamais écrire</h3>
        <ul>
          <li><b>Que ces eaux seraient aujourd'hui non conformes.</b> Personne ne le sait, et c'est
            exactement le point. Une ressource peut avoir été abandonnée, une interconnexion
            réalisée, un traitement installé — les nitrates de Nottonville prouvent que ça arrive.
            <b>L'absence de mesure ne dit rien sur la présence.</b></li>
          <li><b>Une intention.</b> Écrire «&nbsp;on a cessé de mesurer pour ne plus voir&nbsp;»
            serait une accusation que la donnée ne porte pas.</li>
          <li><b>Un défaut de surveillance.</b> {_n(f["n_controles"])} contrôles en quelques
            années, ce n'est pas un abandon.</li>
          <li><b>Une cause aux arrêts groupés.</b> «&nbsp;Compatible avec&nbsp;» n'est pas
            «&nbsp;causé par&nbsp;».</li>
        </ul>
      </div>
    </div>
    <p class="note" style="margin-top:var(--e-6)"><b>La question, elle, est légitime et elle est
      forte&nbsp;:</b> <em>un bulletin peut être déclaré conforme sur un panel qui ne contient plus
      ce qui l'avait rendu non conforme.</em> La conformité affichée ne dit alors rien de
      l'eau — elle dit ce qu'on a regardé. <b>Et quand le dernier regard large date de dix ans,
      elle ne dit plus grand-chose du tout.</b></p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Ce que ça demande au projet</h2>
    <div class="pieces">
      <div class="piece piece--fournie"><span class="tag">1 · en cours</span>
        <h3>Une alerte sur la fiche de chaque commune</h3>
        <p><b>«&nbsp;Aucune analyse complète (plus de 200 paramètres) depuis X mois.&nbsp;»</b>
          Avec ses deux compléments obligatoires&nbsp;: le <b>nombre de contrôles</b> intervenus
          depuis, sans quoi l'alerte se lit comme un abandon&nbsp;; et le <b>nom des paramètres</b>
          qui étaient en dépassement et ne sont plus mesurés, qui est l'information neuve.</p></div>
      <div class="piece"><span class="tag">2 · outillé</span>
        <h3>Étendre le balayage</h3>
        <p>À chaque nouveau département dès que son ingestion est terminée. Le script est fait pour
          ça, et la synthèse qu'il produit est datée&nbsp;: <b>ce dossier se rejoue, il ne se
          retape pas.</b></p></div>
      <div class="piece"><span class="tag">3 · à instruire</span>
        <h3>Reprendre le critère</h3>
        <p>Il exige aujourd'hui un dépassement à la dernière analyse complète. <b>Une commune
          conforme en apparence, dont un paramètre approchait la limite et n'est plus mesuré,
          échappe au filtre.</b></p></div>
      <div class="piece"><span class="tag">4 · règle</span>
        <h3>Ne rien publier sans relecture humaine</h3>
        <p>Chaque dossier nomme une commune et un exploitant implicite. La nommer ne suffit
          pas&nbsp;: il faut vérifier commune par commune <b>qu'aucune phrase ne glisse du constat
          vers le procès</b>.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Limites de l'étude</h2>
    <p class="bnote"><b>Le corpus couvrait {f["departements_balayes"]} départements</b> sur 96 au
      moment du balayage, et inégalement.</p>
    <p class="bnote"><b>Le critère de dépassement</b> est lu sur la limite de qualité <b>déclarée
      par la source</b> dans chaque résultat, pas sur le référentiel daté du projet. Les limites
      exprimées en plage — pH, conductivité — sont écartées faute de pouvoir être comparées sans
      risque de faux positif.</p>
    <p class="bnote"><b>Deux communes sur {f["candidates"]} n'ont rendu aucun résultat</b>
      exploitable par l'API&nbsp;: {f["candidates"]} candidates, {f["instruites"]} instruites.</p>
    <p class="bnote"><b>Les analyses de routine ne sont pas dans le corpus</b>&nbsp;: elles ont été
      lues directement sur Hub'Eau pour cette étude. <b>Un rejeu ultérieur peut donc donner des
      chiffres légèrement différents</b> si l'administration complète ses données.</p>

    <div class="tracab" style="margin-top:var(--e-7)">
      <span><b>Données</b> <code>Hub'Eau · qualite_eau_potable/resultats_dis</code></span>
      <span><b>Consultée le</b> <code>{h(f["date_consultation"])}</code></span>
      <span><b>Corpus</b> <code>{h(version)}</code></span>
      <span><b>Méthode</b> <code>{h(f["script"])}</code></span>
      <span><b>Synthèse</b> <code>{h(os.path.basename(f["source"]))}</code></span>
    </div>
  </div>
</section>
"""


def page_dossiers(con, version, publies):
    """
    L'index des dossiers — et l'état de chacun, dit et non deviné.

    `publies` est l'ensemble des adresses de dossier que CETTE construction a
    réellement écrites. L'état ne se déclare donc pas dans une table qu'on
    penserait à mettre à jour : il se constate. Une carte dont la page n'existe
    pas reste un `<div>`, et le jour où la page est écrite, la carte devient un
    lien sans que personne n'ait rien à basculer.

    C'est le même mécanisme que la pastille « dossier » du répertoire des
    substances, et pour la même raison : un lecteur qui clique et tombe sur
    rien perd confiance, et c'est le coût le plus élevé qu'une page d'index
    puisse faire payer (consigne §11.1).
    """
    ctx = chiffres_dossiers(con, version)
    n_publies = sum(1 for d in DOSSIERS if d.get("lien") in publies)

    cartes = []
    for d in DOSSIERS:
        lien = d.get("lien") if d.get("lien") in publies else None
        etat = ("publié", "pill--dossier") if lien else ("en préparation", "pill--relire")
        cl = d["cl"] + ("" if lien else " dossier--attente")

        bouts = [f'<span class="pill {etat[1]} dossier-etat">{h(etat[0])}</span>',
                 f'<span class="dossier-num">{h(d["num"])}</span>']
        if d.get("tag"):
            # La carte 08 marque son étiquette d'un modificateur : « erreur du
            # projet » ne se lit pas comme les sept autres étiquettes.
            sup = " dossier-tag--aveu" if d["cl"] == "dossier--aveu" else ""
            bouts.append(f'<span class="dossier-tag{sup}">'
                         f'{h(_valeur(d["tag"], ctx))}</span>')
        if d.get("chiffre"):
            tete, milieu, queue = _valeur(d["chiffre"], ctx)
            bouts.append(f'<span class="dossier-chiffre">{h(tete)} '
                         f'<span>{h(milieu)}</span>'
                         + (f' {h(queue)}' if queue else "") + '</span>')
        bouts.append(f'<h3>{h(d["titre"])}</h3>')
        bouts.append(f'<p>{d.get("corps_index") or d["corps"]}</p>')
        if d.get("precision"):
            bouts.append('<p class="dossier-precision">'
                         f'{_valeur(d["precision"], ctx)}</p>')
        if d.get("pied"):
            bouts.append(f'<span class="dossier-pied">'
                         f'{_valeur(d["pied"], ctx)}</span>')

        corps = "".join(bouts)
        cartes.append(f'<a class="dossier {cl}" href="{h(lien)}">{corps}</a>'
                      if lien else f'<div class="dossier {cl}">{corps}</div>')

    # La phrase d'état se calcule elle aussi. Écrite en dur, elle annoncerait
    # « un seul dossier est écrit » le jour où il y en aurait deux — et l'index
    # dirait le contraire de la liste qu'il porte.
    total = len(DOSSIERS)
    if n_publies == 0:
        etat_liste = (f"<b>Aucun dossier n'est encore publié.</b> Les {total} "
                      "sujets sont instruits — les chiffres existent, la "
                      "relecture non. Ils sont listés ici parce que les taire "
                      "donnerait à croire que le projet n'a rien trouvé.")
    elif n_publies == 1:
        etat_liste = (f"<b>Un seul dossier est écrit à ce jour.</b> Les "
                      f"{total - 1} autres sont instruits — les chiffres "
                      "existent, la relecture non. Ils sont listés ici parce "
                      "que les taire donnerait à croire que le projet n'a "
                      "trouvé qu'une chose.")
    else:
        etat_liste = (f"<b>{n_publies} dossiers sont écrits à ce jour</b>, sur "
                      f"{total} sujets instruits. Les autres attendent leur "
                      "relecture, pas leurs chiffres.")

    # « 0 dossier(s) publié(s) » ne se publie pas : la parenthèse de pluriel est
    # une commodité de développeur, elle n'a rien à faire dans une page lue.
    if n_publies == 0:
        debit = f"aucun dossier publié sur {total} instruits"
    elif n_publies == 1:
        debit = f"un dossier publié sur {total} instruits"
    else:
        debit = f"{n_publies} dossiers publiés sur {total} instruits"

    pieces = "".join(
        f'<div class="piece{" piece--fournie" if fourni else ""}">'
        f'<span class="tag">{h(tag)}</span><h3>{h(titre)}</h3>'
        f'<p>{corps.format(communes=ctx["panel_communes"], instruites=ctx["panel_instruites"], departements=ctx["panel_departements"], debit=debit)}</p></div>'
        for tag, titre, corps, fourni in FABRICATION)

    return f"""
<section class="section">
  <div class="zone zone-large">
    <p class="bnote"><b>Un dossier n'est pas un article d'opinion.</b> Chacun part d'un fait
      vérifiable ligne à ligne dans les données publiées, expose ce qu'il établit <b>et ce qu'il
      n'établit pas</b>, et interroge la norme — jamais ceux qui l'appliquent. Un dossier qui ne
      peut pas séparer les deux n'est pas publié.</p>
    <p class="bnote">{etat_liste}</p>

    <div class="dossier-liste-tete" style="margin-top:var(--e-7)">
      <h2 class="sec" style="margin:0;border:0;padding:0">Les {total} sujets</h2>
    </div>

    <div class="dossiers">{"".join(cartes)}</div>

    <p class="bnote" style="margin-top:var(--e-6)"><b>Pourquoi un dossier «&nbsp;erreur du
      projet&nbsp;» figure dans la même liste que les autres.</b> Un observatoire qui ne publie que
      ce qui l'arrange demande qu'on le croie. Celui-ci publie ses corrections au même endroit et
      dans la même forme que ses trouvailles.</p>
  </div>
</section>

<section class="section">
  <div class="zone zone-large">
    <h2 class="sec">Comment un dossier se construit</h2>
    <div class="pieces">{pieces}</div>
  </div>
</section>
"""


def page_accueil(lignes, these, version, calcule_le, con):
    """
    L'accueil : la question du lecteur, la réponse chiffrée, puis les portes.

    La réécriture du lot 4 tient à un constat de la communication : le site
    énonçait une méthode, puis faisait défiler avant de montrer qu'elle produit
    quelque chose. **Une méthode sans résultat se lit comme une intention.** Le
    résultat chiffré est donc dans le premier écran.

    Tous les nombres sont **calculés**. Les maquettes les portaient en dur, et
    ils étaient justes au 13 août 2026 ; ils ont vieilli en trois jours — le
    corpus est passé de 25 284 à 34 823 analyses. Un chiffre d'accueil écrit à
    la main est un chiffre faux à retardement.
    """
    n_rattachees = sum(1 for c in lignes if c["statut"] == "rattachee_reseau")
    n_nondoc = sum(1 for c in lignes if c["statut"] == "non_documentee")
    n_documentees = sum(1 for c in lignes if c["statut"] != "non_documentee")

    # Les totaux du CORPUS, pas de la dernière ligne de chaque commune. La
    # version d'avant sommait `lignes`, qui ne porte qu'un bulletin par
    # commune : elle sous-comptait tout ce que le corpus contient d'historique.
    ou, args = _filtre_dept()
    tot = con.execute(f"""
        SELECT COUNT(*), COALESCE(SUM(nb_bascules), 0),
               COALESCE(SUM(nb_depasse_applicable), 0),
               COUNT(*) FILTER (WHERE est_complet AND nb_depasse_applicable = 0
                                  AND nb_bascules > 0),
               COUNT(DISTINCT dept)
        FROM analyses_figees WHERE version_referentiel = ?{ou}
    """, [version] + args).fetchone()
    n_bulletins, n_bascules, n_depasse, n_these, n_depts = tot

    def n(x):
        return f"{x:,}".replace(",", " ")

    lignes_these = "".join(
        f"<tr><td><a href='commune/{h(t[1])}.html'>{h(t[0])}</a></td>"
        f"<td>{h(t[2])}</td><td class='num'>{h(BF._date_fr(t[3]))}</td>"
        f"<td class='num'><b>{t[4]}</b></td>"
        f"<td class='num'>{t[5]} · {h(t[6])}</td>"
        f"<td class='num'>{t[7]} ({BF._nb(t[8])} %)</td></tr>"
        for t in these[:12])

    bloc_these = f"""
    <div class="tableau"><div class="tableau-defile">
      <table>
        <thead><tr><th>Commune</th><th>Dépt</th><th>Prélèvement</th>
          <th>Bascules</th><th>Effort de recherche</th><th>Substances notées</th></tr></thead>
        <tbody>{lignes_these}</tbody>
      </table>
    </div></div></div>
    <p class="note note--gris"><b>Comment lire ce tableau.</b> Chaque ligne est un
      bulletin complet, sans aucun dépassement à la date où il a été prélevé, et qui
      comporte pourtant au moins une mesure qui aurait dépassé la limite de 2016. L'eau
      n'a pas changé entre les deux lectures : la limite, si. L'effort de recherche est
      affiché parce qu'il conditionne tout le reste — on ne trouve que ce qu'on
      cherche.</p>
    """ if these else """
    <p class="note note--gris">Aucun bulletin du corpus actuel ne présente cette
      configuration. Ce n'est pas un résultat rassurant : c'est un corpus encore petit.
      La requête est publiée telle quelle et se remplira à mesure de la collecte.</p>
    """

    ctx = chiffres_dossiers(con, version)
    cartes = "".join(
        f'<article class="dossier {d["cl"]}">'
        + (f'<div class="dossier-chiffre">'
           f'{h(" ".join(x for x in _valeur(d["chiffre"], ctx) if x))}</div>'
           if d.get("chiffre") else "")
        + f'<h3>{h(d["titre"])}</h3><p>{d["corps"]}</p>'
        f'<p class="dossier-tag">{h(d["tag_accueil"])}</p></article>'
        for d in DOSSIERS)

    liste_refus = "".join(
        f"<li><b>{h(fort)}</b> {suite}</li>" for fort, suite in REFUS)

    return f"""
  <p class="chapo">L'Observatoire sépare <b>la mesure</b>, qui est un fait physique, du
    <b>verdict</b>, qui est une convention administrative datée. Chaque mesure publique
    du contrôle sanitaire y est renotée contre trois grilles : celle de 2016, celle
    d'aujourd'hui, et la plus protectrice identifiée dans le monde.</p>
  <p>Il ne dit pas si votre eau est bonne. <b>Il dit contre quelle règle on l'a jugée, à
    quelle date cette règle a été écrite, ce qu'on a cherché, ce qu'on n'a pas cherché,
    et ce que l'analyse ne pouvait pas voir.</b></p>
  <p>Sur les {n(n_bulletins)} analyses complètes du corpus, <b>{n(n_bascules)} mesures
    dépassaient la limite de 2016 et ne dépassent pas celle de 2026</b>. Même eau, même
    mesure, deux verdicts opposés.</p>

  <div class="cherche">
    <h2>Votre commune</h2>
    <div class="champ">
      <input id="q" type="search" inputmode="text" autocomplete="off"
             placeholder="Code postal, code INSEE ou nom de commune"
             aria-label="Code postal, code INSEE ou nom de commune">
    </div>
    <ul class="resultats" id="resultats"></ul>
    <p class="aide">La recherche se fait dans votre navigateur : aucune requête n'est
      envoyée, et ce que vous cherchez ne nous est pas transmis.</p>
  </div>
  <div class="deux-notes">
    <p class="note note--gris"><b>Le corpus ne couvre pas encore la France entière, et
      il n'y a aucun mystère à cela.</b> Cet observatoire est fait par une seule
      personne, un citoyen concerné par la qualité de son eau, sur son temps, ses
      ressources et son matériel — sans financement, public ou privé. Collecter un
      département entier demande cinq à sept heures ; la collecte se poursuit,
      département par département.</p>
    <p class="note note--gris"><b>Ce qui est délibéré, en revanche, c'est de ne rien
      publier à moitié.</b> Tant qu'un département n'est pas collecté en entier, il
      n'apparaît pas ici : un département à moitié collecté ment davantage qu'un
      département absent. Une commune absente n'est donc pas une commune dont l'eau
      serait bonne — c'est une commune dont le tour n'est pas encore venu.</p>
  </div>

  <section class="section"><h2>Le corpus au {h(BF._date_fr(calcule_le))}</h2>
    <div class="nombres">
      <div class="stat stat--bascule"><div class="num">{n(n_bascules)}</div>
        <div class="lib"><b>mesures</b> · bascules réglementaires<br>
          elles dépassaient la limite de 2016, elles ne dépassent pas celle de 2026.
          Réparties dans {n(n_these)} bulletins déclarés conformes</div></div>
      <div class="stat stat--rouge"><div class="num">{n(n_depasse)}</div>
        <div class="lib"><b>mesures</b> · dépassements à la date<br>
          au-dessus de la limite qui s'appliquait <b>le jour du prélèvement</b> — et non
          de celle d'aujourd'hui</div></div>
    </div>
    <div class="nombres-socle">
      <div class="stat-petit"><b>{n(n_documentees)} communes</b> documentées, dont
        {n(n_rattachees)} par le bulletin de leur réseau</div>
      <div class="stat-petit"><b>{n(n_bulletins)} analyses complètes</b>, plus de
        {SEUIL_COMPLET} substances chacune, sur {n_depts} départements</div>
    </div>
    <p class="note note--gris"><b>Ces nombres ne se comparent pas d'une commune à
      l'autre.</b> Une commune qui fait chercher 700 substances a mécaniquement plus de
      chances d'en voir une dépasser qu'une commune qui en fait chercher 200 : comparer
      les comptes bruts pénalise la transparence. Les comparaisons se font sur les taux,
      et l'effort de recherche est affiché partout où elles apparaissent.</p>
    {f'''<p class="note note--gris"><b>{n(n_nondoc)} communes</b> du corpus n'ont aucun
      bulletin complet, ni pour elles ni pour leur réseau. Ce n'est ni « conforme » ni
      « non conforme » — c'est une absence de donnée, et elle reste visible sur la
      carte.</p>''' if n_nondoc else ""}
  </section>

  <section class="section"><h2>Sept mécanismes trouvés en chemin, et une erreur du projet</h2>
    <p class="chapo">Aucun n'était visé au départ. Chacun est un sujet à lui seul, et
      chacun porte sa date : le corpus grossit, et un chiffre sans sa date est un
      chiffre faux.</p>
    <div class="dossiers">{cartes}</div>
  </section>

  <section class="section">
    <div class="figure-tete">
      <h2>Conformes aujourd'hui, non conformes en 2016</h2>
      <p class="chapo">Des bulletins <b>complets</b>, déclarés <b>parfaitement
        conformes</b>, qui ne l'auraient pas été il y a dix ans. Ni une opinion, ni une
        estimation : une mesure, deux grilles, deux verdicts. <b>Voici les douze
        premières des {n(n_these)} lignes ; la requête qui les produit est publiée avec
        la méthode.</b></p>
    </div>
    {bloc_these}
  </section>

  <section class="section"><h2>Et maintenant ?</h2>
    <p class="chapo">Ce que ces données permettent de faire — et ce qu'elles ne diront
      jamais. L'Observatoire ne recommande rien : ni équipement, ni traitement, ni
      produit, ni conduite individuelle. Il n'a pas d'avis sur votre robinet. Mais une
      fois la fiche de votre commune lue, vous savez des choses précises et datées, et
      ces choses se demandent.</p>
    <div class="portes">
      <div class="porte">
        <h3>Vous habitez ici</h3>
        <p>Lisez la fiche de votre commune jusqu'au bout, en particulier ce que
          l'analyse n'a <b>pas</b> cherché. Puis, si vous voulez aller plus loin, ces
          questions ont toutes une réponse publique :</p>
        <ul>
          <li>quelle est la liste des substances recherchées sur mon réseau, et depuis
            quand est-elle celle-là ?</li>
          <li>une substance déjà mesurée en dépassement chez moi est-elle toujours
            recherchée aujourd'hui ?</li>
          <li>quelles limites applicables à mon eau changeront de valeur à une date
            déjà fixée ?</li>
        </ul>
        <p>Elles s'adressent à l'ARS de votre région, à votre mairie et à votre
          exploitant, et elles portent sur des documents publics. Ce ne sont pas des
          accusations : ce sont des <b>questions de dénombrement</b>.</p>
      </div>
      <div class="porte">
        <h3>Vous êtes élu, association ou collectif</h3>
        <p>Une commune, un syndicat des eaux, une association d'usagers peuvent obtenir
          ce que l'Observatoire n'a pas encore : le <b>marché d'analyses</b> de leur
          région, avec la liste de substances qui lui est annexée. C'est la pièce qui
          manque pour passer d'une compatibilité à une démonstration.</p>
        <p><b>Ce que l'Observatoire peut fournir :</b> l'extraction complète de votre
          commune, de votre réseau ou de votre département, en CSV, avec la version du
          référentiel qui l'a produite. Gratuitement, sous licence ouverte, sans
          contrepartie.</p>
      </div>
      <div class="porte">
        <h3>Vous enquêtez, vous enseignez, vous cherchez</h3>
        <p>Toutes les données sont réutilisables, les seuils sont versionnés et
          journalisés, et chaque bulletin publié porte la version du référentiel qui a
          servi à le noter. Les requêtes qui produisent les chiffres de cette page sont
          exposées avec la méthode.</p>
        <p class="porte-liens"><a href="methode.html">La méthode</a> ·
          <a href="sources.html">Sources &amp; licences</a> ·
          <a href="substances.html">Le répertoire des substances</a></p>
      </div>
    </div>
  </section>

  <section class="section section--sombre">
    <h2>Huit refus, écrits chacun après une erreur réellement commise</h2>
    <p class="chapo">Ce ne sont pas des précautions décoratives. C'est ce qui rend le
      travail contestable point par point — donc solide. <b>Si vous trouvez une entorse
      à l'un de ces huit points sur ce site, écrivez-nous : la correction sera publiée,
      datée, avec sa portée mesurée. C'est déjà arrivé.</b></p>
    <ol class="refus">{liste_refus}</ol>
  </section>

  <section class="section signature">
    <h2>Qui fait ça</h2>
    <p>L'Observatoire est le travail d'une <b>personne seule</b>, un citoyen concerné
      par la qualité de son eau, mené sur son temps et ses ressources propres — sans
      financement public ni privé, sans publicité, sans partenariat industriel. Les
      données viennent du contrôle sanitaire officiel (SISE-Eaux, ministère chargé de
      la santé) ; le référentiel de seuils, la méthode et le code sont publiés sous
      licence ouverte et versionnés. <b>Rien de ce qui est vendu ailleurs sur ce site
      n'apparaît dans une fiche communale.</b></p>
  </section>
"""
def comptes_departements(con, version, lignes):
    """Par département : le nombre d'analyses complètes détenues, et le nombre
    de communes documentées. Ce sont les deux seuls nombres que la carte
    nationale porte — aucun verdict ne s'y cumule."""
    par_dept = {}
    for r in con.execute("""
            SELECT dept, COUNT(*) FROM analyses_figees
            WHERE version_referentiel = ?""" + _filtre_dept()[0] + """
            GROUP BY dept""", [version] + _filtre_dept()[1]).fetchall():
        par_dept.setdefault(r[0], {})["bulletins"] = r[1]
    for dept, communes in par_departement(lignes).items():
        d = par_dept.setdefault(dept, {})
        d["communes"] = sum(1 for c in communes if c["statut"] != "non_documentee")
        d.setdefault("bulletins", 0)
    for d in par_dept.values():
        d.setdefault("communes", 0)
    return par_dept


def page_carte(lignes, version, calcule_le, comptes):
    bornes = bornes_couverture(comptes)
    svg = carte_departements_svg(comptes, bornes=bornes)
    total_b = sum(d["bulletins"] for d in comptes.values())
    total_c = sum(d["communes"] for d in comptes.values())
    n_dept = sum(1 for d in comptes.values() if d["bulletins"])

    # Combien de départements dans chaque classe. C'est ce compte, et lui seul,
    # qui permet de voir qu'une échelle a cessé de discriminer : l'échelle
    # d'origine rangeait 21 départements sur 30 dans la même classe, et rien à
    # l'écran ne le disait.
    par_classe = {}
    for d in comptes.values():
        par_classe.setdefault(classe_couverture(d["bulletins"], bornes),
                              []).append(d)
    # **« Documenté » et « collecté » ne sont pas la même chose**, et la jauge
    # ne doit compter que le second. Neuf départements du corpus portent une à
    # trois analyses : une commune rapatriée seule, souvent pour éprouver un
    # cas, jamais une collecte. Les faire entrer dans « X départements
    # collectés en entier » serait une affirmation fausse — du même ordre que
    # présenter une commune non documentée comme conforme.
    n_metropole = 96
    n_collectes = sum(1 for d in comptes.values()
                      if d["bulletins"] >= bornes[0])
    n_effleures = n_dept - n_collectes
    n_reste = n_metropole - n_collectes

    lig = "".join(
        f"<tr><td><a href='departement/{h(code)}.html'>{h(_nom_dept(code))}</a>"
        f"<span class='grille'>département {h(code)}</span></td>"
        f"<td class='num'>{d['bulletins']}</td>"
        f"<td class='num'>{d['communes']}</td></tr>"
        for code, d in sorted(comptes.items()) if d["bulletins"])

    paliers = "".join(
        f'<span><i class="pal {classe}"></i> {libelle} — '
        f'<b>{len(par_classe.get(classe, []))}</b> département(s)</span>'
        for classe, libelle in libelles_paliers(bornes))

    part = 100 * n_collectes / n_metropole
    effleures = (f" S'y ajoutent <b>{n_effleures}</b> départements où une ou "
                 f"quelques communes seulement ont été rapatriées : ils "
                 f"apparaissent sur la carte, mais ils ne sont pas collectés."
                 if n_effleures else "")
    return f"""
  <section style="margin-top:0">
    <div class="jauges">
      <div class="jg jg--neutre" style="--pct:{part:.1f}%">
        <div class="jg-lg"><span><b>{n_collectes} départements</b> collectés, sur
          les <b>{n_metropole} de métropole</b></span><b>{part:.0f} %</b></div>
        <div class="jg-piste"><em></em></div>
      </div>
    </div>
    <p class="chapo"><b>{total_b}</b> analyses complètes, <b>{total_c}</b> communes
      documentées. Il reste <b>{n_reste}</b> départements à collecter.{effleures}</p>
    <div class="rappel"><b>Cette jauge n'est pas une jauge de seuil.</b> Une couverture
      qui progresse n'est pas une limite dont on s'approche : elle n'a ni zone
      d'approche à 85 %, ni repère plus strict, et elle n'est ni bonne ni mauvaise.
      Réutiliser telle quelle la barre qui sert aux mesures serait un contresens — d'où
      le modificateur qui lui retire l'un et l'autre.</div>

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
    <div class="rappel"><b>Un département fortement coloré n'est pas un département en
      mauvais état : c'est un département bien documenté.</b> La lecture se fait donc à
      l'envers de l'habitude. Un département pâle ou vide n'a pas une eau meilleure — il
      n'a pas encore été collecté, et l'absence de donnée n'est pas une bonne
      nouvelle.</div>
    <div class="rappel"><b>Les bornes de la légende suivent le corpus, elles ne sont pas
      des seuils.</b> Rien ne fixe qu'un département « bien documenté » commence à telle
      valeur : ce sont des quintiles, recalculés à chaque construction. Le compte de
      chaque classe est affiché à côté — sans lui, on ne peut pas voir qu'une échelle a
      cessé de discriminer, ce qui est précisément arrivé à la précédente.</div>
    <div class="rappel"><b>Cliquez un département coloré</b> pour ouvrir sa page : la
      liste alphabétique de ses communes, ses gestionnaires déclarés, et le détail de
      chaque bulletin. Les départements non collectés ne mènent nulle part — un lien y
      serait une promesse que le corpus ne tient pas.</div>
  </section>

  <section><h3 class="sec">Pourquoi ce n'est pas plus</h3>
    <div class="prose">
      <p>La question se pose ici, et pas ailleurs : c'est en voyant son département
        vide qu'on se la pose. <b>L'Observatoire est tenu par une personne.</b> Chaque
        département demande cinq à sept heures — moissonner les bulletins commune par
        commune en respectant le débit d'un service public gratuit, les verser, les
        figer contre le référentiel daté, puis construire et publier.</p>
      <p>Ce n'est donc pas un choix éditorial : aucun département n'a été écarté, aucun
        n'a été jugé moins intéressant qu'un autre. <b>L'ordre de collecte est l'ordre
        dans lequel le travail a pu se faire</b>, et le tableau ci-dessous est rangé par
        code pour que rien n'y ressemble à un palmarès.</p>
      <p>Un département absent n'est pas un département sans problème. C'est un
        département dont nous ne savons rien — et sur ce site, ces deux choses ne se
        confondent jamais.</p>
    </div>
  </section>

  <section><h3 class="sec">{n_dept} département(s) documenté(s) — {total_b} analyses, {total_c} communes</h3>
    <div class="tableau"><div class="tableau-defile">
      <table>
        <thead><tr><th>Département</th><th>Analyses complètes détenues</th>
          <th>Communes documentées</th></tr></thead>
        <tbody>{lig}</tbody>
      </table>
    </div></div>
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


def _cellule_hormonale(g):
    """
    Les trois registres hormonaux d'une commune, côte à côte et **jamais
    additionnés à l'écran** (§2.6, §2.15).

    Le total existe comme clé de tri — c'est ce qui permet de remonter en
    quelques secondes les communes les plus chargées — mais il ne s'affiche
    pas comme un fait : « 17 perturbateurs endocriniens » réunirait sous un
    même mot une substance reconnue par le droit européen, une substance que
    la littérature soupçonne, et une substance dont la question n'a jamais été
    instruite. Les deux dernières ne sont pas des perturbateurs avérés ; la
    troisième n'est même pas un « non ». Les fondre en un chiffre serait le
    faux positif que le troisième état sert précisément à éviter.
    """
    if not g:
        return "<td class='num hormo'>—</td>"
    return (f"<td class='num hormo'>"
            f"<b class='h-av' title=\"statut avéré au sens du droit européen\">"
            f"{g['avere']}</b>"
            f"<span class='h-sep'>·</span>"
            f"<b class='h-su' title=\"suspecté par la littérature scientifique, "
            f"sans statut réglementaire\">{g['suspecte']}</b>"
            f"<span class='h-sep'>·</span>"
            f"<b class='h-nd' title=\"question non instruite au référentiel — "
            f"ce n'est pas un « non »\">{g['non_documente']}</b></td>")


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
        detail = ("<td colspan='7' style='color:var(--gris)'>aucun bulletin complet, "
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
            f"<td class='num'><b style='color:var(--bascule)'>{c['nb_bascules'] if c['nb_bascules'] is not None else '—'}</b></td>"
            # Ce que le laboratoire ne pouvait pas voir (§8bis obligation 11).
            # Le taux accompagne le compte : un bulletin qui cherche 700
            # paramètres en aura mécaniquement plus qu'un qui en cherche 200,
            # et le compte brut ne se compare pas d'une commune à l'autre.
            f"<td class='num'>{c['nb_aveugles'] if c.get('nb_aveugles') is not None else '—'}"
            f"<span class='grille'>{BF._nb(c.get('aveugles_pour_mille'))} ‰</span></td>"
            f"{_cellule_hormonale(c.get('hormonal'))}")
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
            f"data-aveugles='{cle(c.get('nb_aveugles'))}' "
            # La somme des trois registres : clé de tri, jamais énoncé. Voir
            # `_cellule_hormonale`. Sans bulletin, -1 et non 0 — « aucune
            # substance trouvée » et « on n'a pas cherché » ne se rangent pas
            # ensemble.
            f"data-hormonal='{-1 if not c.get('hormonal') else sum(c['hormonal'].values())}' "
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
     "voisine, sur la même eau. <b>Le point est en deux moitiés</b> : la "
     "blanche dit que l'analyse vient d'ailleurs, l'autre porte le verdict de "
     "ce bulletin, qui vaut pour l'eau qui arrive ici"),
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
    <div class="tableau"><div class="tableau-defile">
      <table>
        <thead><tr><th>Département</th><th>Communes documentées</th>
          <th>Non documentées</th><th>Effort de recherche</th>
          <th>Dépassements à la date</th><th>Bascules</th></tr></thead>
        <tbody>{"".join(lig)}</tbody>
      </table>
    </div></div>
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
  <section class="section"><h2>Deux documents publics diraient ce que cette page ne peut pas dire</h2>
    <p class="chapo">Ce ne sont pas des lacunes de la collecte : ces documents existent,
      ils sont publics, et ils ne sont pas dans les données d'analyse. Les nommer vaut
      mieux que laisser croire que le bulletin dit tout.</p>

    <div class="pieces">
      <div class="piece">
        <h3>Le marché d'analyses de la région</h3>
        <p>Il fixe <b>quelles substances le laboratoire doit chercher</b>, et à quelle
          finesse. C'est lui, et non l'état de la ressource, qui explique qu'un
          département cherche 627 paramètres et un autre 234 — et qu'un même
          département en cherche deux fois moins qu'il y a six ans.</p>
        <p class="note note--gris"><b>Non détenu.</b> Ces marchés sont publiés au profil
          d'acheteur de chaque agence régionale de santé, en pièces jointes, sans format
          commun.</p>
      </div>
      <div class="piece">
        <h3>Les arrêtés préfectoraux de {h(nom_dept)}</h3>
        <p>Ils portent les <b>décisions</b> prises après un dépassement : mesures
          correctives, restriction d'usage, interruption de distribution, et surtout les
          <b>dérogations</b> qui autorisent une eau à rester au-dessus d'une limite.</p>
        <p class="note note--gris"><b>Non détenus.</b> Le contrôle sanitaire publie des
          mesures, pas des décisions. Les arrêtés paraissent au recueil des actes
          administratifs de la préfecture, en PDF, sans format commun d'un département
          à l'autre.</p>
      </div>
    </div>

    <div class="verdict-bloc verdict-bloc--bascule">
      <h2>Une eau peut légalement rester au-dessus d'une limite pendant six ans</h2>
      <p>Lorsque les mesures correctives n'ont pas suffi, le préfet peut accorder une
        <b>dérogation</b> : trois ans au maximum, renouvelable une fois dans des
        circonstances exceptionnelles. La possibilité d'une troisième a été
        <b>abrogée</b> — quelqu'un a jugé, à un moment, qu'elle était de trop.</p>
      <p><b>Conséquence directe pour cette page :</b> un bulletin déclaré conforme peut
        l'être au regard de la limite ordinaire, ou au regard d'une dérogation qui l'a
        temporairement déplacée pour cette commune-là. <b>Nous ne pouvons pas
        distinguer les deux</b>, et aucun chiffre de ce site ne prétend le faire. La
        question se pose à l'agence régionale de santé et à la préfecture.</p>
    </div>

    <details class="plus">
      <summary>Afficher les 8 articles qui organisent cette procédure</summary>
      <div class="tableau"><div class="tableau-defile">
      <table><thead><tr><th>Article</th><th>Ce que le texte prévoit</th></tr></thead><tbody>
        <tr><td><code>R1321-26</code></td><td>Tout dépassement d'une limite de qualité est <b>signalé immédiatement au maire et à l'agence régionale de santé</b>, et une enquête est menée.</td></tr>
        <tr><td><code>R1321-27</code></td><td>La personne responsable de la distribution prend <b>« le plus rapidement possible les mesures correctives nécessaires »</b>, quelle qu'en soit la cause.</td></tr>
        <tr><td><code>R1321-29</code></td><td>Le préfet peut <b>« restreindre, voire interrompre la distribution »</b> lorsqu'un risque sanitaire est avéré.</td></tr>
        <tr><td><code>R1321-30</code></td><td><b>« Les consommateurs en sont informés immédiatement »</b> — sur le danger potentiel, les mesures engagées, et les conseils relatifs aux conditions de consommation.</td></tr>
        <tr><td><code>R1321-31</code></td><td>Si les mesures correctives n'ont pas suffi, une <b>dérogation</b> peut être demandée au préfet. Sa durée <b>ne peut excéder trois ans</b>.</td></tr>
        <tr><td><code>R1321-33</code></td><td>Une <b>seconde</b> dérogation de trois ans au maximum, « dans des circonstances exceptionnelles ».</td></tr>
        <tr><td><code>R1321-34</code></td><td><b>Abrogé</b> — la possibilité d'une troisième dérogation a été supprimée.</td></tr>
        <tr><td><code>R1321-35</code></td><td>Un <b>bilan</b> est obligatoire à l'issue de chaque période dérogatoire.</td></tr>
      </tbody></table></div></div>
      <p class="note note--gris">Le pendant exact de ce que cet observatoire documente
        par ailleurs : la limite se déplace dans le temps, et l'eau peut aussi être
        autorisée à rester au-dessus d'elle, pour une durée écrite.</p>
    </details>

    <div class="piece piece--fournie">
      <h3>Ce que l'Observatoire fournit, lui</h3>
      <p>Tout ce qui est affiché sur cette page est dérivé de fichiers publics et
        <b>téléchargeable</b> : un bulletin par ligne, le détail paramètre par
        paramètre avec le seuil applicable à sa date, le statut de chaque commune, et
        le référentiel daté de seuils qui a servi à noter.</p>
      <p><a class="lien-fort" href="../sources.html">Les données et leurs licences</a></p>
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

    # Le regroupement se fait par RÉSEAU RÉEL, décision de Yannick du 13 août
    # 2026. Il se faisait sur `nom_uge`, qui est le GESTIONNAIRE — et le
    # regroupement affiché n'était alors pas celui qui avait servi à rattacher
    # la commune à son bulletin (`collecte.py` retient un `code_reseau`).
    # Mesuré le 13 août : 135 groupes sur 505 réunissaient des communes qui ne
    # sont pas sur le même réseau, soit 2 653 communes. Le cas qui l'a montré :
    # « SICOVAL AEP — 35 communes » recouvrait quatre configurations de réseau,
    # et Venerque, qui ne déclare jamais ce gestionnaire, y figurait quand même.
    reseaux, sans_reseau = {}, []
    for c in communes:
        if c["statut"] == "non_documentee":
            continue
        nom = (c.get("noms_reseaux") or "").strip()
        if not nom:
            # Troisième état : le bulletin ne déclare aucun réseau. Le ranger
            # sous son gestionnaire serait affirmer un rattachement que la
            # source ne donne pas.
            if c["nom_uge"]:
                sans_reseau.append(c)
            continue
        reseaux.setdefault(nom, []).append(c)

    def _item(nom, cs):
        # Les gestionnaires déclarés pour ce réseau : le plus souvent un seul.
        # Il est nommé, mais il ne commande plus le regroupement.
        gest = sorted({c["nom_uge"] for c in cs if c["nom_uge"]})
        mention = (f" <span class='grille'>gestionnaire : {h(', '.join(gest))}</span>"
                   if gest else "")
        return (f"<li><b>{h(nom)}</b> — {len(cs)} commune(s) : "
                + ", ".join(f"<a href='../commune/{h(c['code_insee'])}.html'>{h(c['commune'])}</a>"
                            for c in sorted(cs, key=lambda x: x["commune"]))
                + mention
                + f"<span class='grille'>effort de recherche : {h(_etendue_effort(cs))} paramètres</span></li>")

    bloc_uge = ""
    if reseaux:
        items = "".join(_item(nom, cs) for nom, cs in sorted(reseaux.items()))
        reste = ""
        if sans_reseau:
            noms = ", ".join(
                f"<a href='../commune/{h(c['code_insee'])}.html'>{h(c['commune'])}</a>"
                for c in sorted(sans_reseau, key=lambda x: x["commune"]))
            reste = f"""
    <div class="rappel"><b>{len(sans_reseau)} commune(s) sans réseau déclaré</b> :
      {noms}. Le bulletin qui les documente ne nomme aucun réseau de distribution.
      Elles ne sont rangées sous aucun groupe plutôt que sous celui de leur
      gestionnaire : ce serait affirmer un rattachement que la source ne donne pas.</div>"""
        bloc_uge = f"""
  <section><h3 class="sec">Les réseaux de distribution — {len(reseaux)}</h3>
    <div class="prose"><ul>{items}</ul></div>
    <div class="rappel"><b>Ce regroupement est celui du réseau, pas celui du
      gestionnaire.</b> C'est le réseau qui a servi à rattacher chaque commune au
      bulletin qui la documente, et c'est donc lui qui dit quelles communes reçoivent
      la même eau. Un même gestionnaire exploite souvent plusieurs réseaux
      distincts : les réunir sous son nom laissait croire à une eau commune que la
      donnée ne dit pas.</div>
    <div class="rappel"><b>Un réseau commun n'est pas un captage commun.</b> Le lien
      entre un captage et une commune n'est pas exposé par les données publiques — il
      figure parmi ce que l'outil ne sait pas encore faire.</div>{reste}
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
  <div class="fiche-tete fiche-tete--seule">
    <div class="verdict-bloc verdict-bloc--indetermine">
      <h2>Cette page ne classe pas ce département</h2>
      <p>Un département n'a pas de verdict. Il a des <b>bulletins</b>, chacun prélevé un
        jour donné sur un point d'eau donné, et noté contre la grille en vigueur ce
        jour-là. Les nombres ci-dessous sont des <b>sommes</b> : ils disent ce que l'on
        sait de ce territoire, jamais l'état de son eau.</p>
    </div>
    <div class="nombres">
      <div class="stat"><div class="num">{n_ana + n_rat}</div>
        <div class="lib">communes documentées<br>dont {n_rat} par le bulletin de leur réseau</div></div>
      <div class="stat"><div class="num">{n_nd}</div>
        <div class="lib">communes non documentées<br>ni bulletin propre, ni bulletin de réseau</div></div>
      <div class="stat stat--bascule"><div class="num">{n_bas}</div>
        <div class="lib">bascules réglementaires<br>au-dessus de 2016, sous 2026</div></div>
      <div class="stat stat--rouge"><div class="num">{n_dep}</div>
        <div class="lib">dépassements<br>à la date du prélèvement</div></div>
    </div>
  </div>

  <section class="section"><h2>Où se concentre ce que l'on sait</h2>
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

  <section class="section"><h2>Trouver votre commune</h2>
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

  <section class="section"><h2>Les {len(communes)} communes, par ordre alphabétique</h2>
    <nav class="index-alpha" id="index-alpha" aria-label="Aller à une lettre">{index}</nav>
    <div class="tableau tableau--annuaire"><div class="tableau-defile">
      <table id="tbl-communes">
        <thead><tr>
          <th aria-sort="ascending" data-tri="nom" data-type="texte">Commune</th>
          <th>Statut</th>
          <th data-tri="date" data-type="texte">Prélèvement</th>
          <th data-tri="effort" data-type="nombre">Effort de recherche</th>
          <th data-tri="couverture" data-type="nombre">Paramètres notés</th>
          <th data-tri="depassements" data-type="nombre">Dépassements à la date</th>
          <th data-tri="bascules" data-type="nombre">Bascules</th>
          <th data-tri="aveugles" data-type="nombre">Hors de portée du laboratoire</th>
          <th data-tri="hormonal" data-type="nombre">Statut hormonal des substances trouvées
            <span class="grille">avéré · suspecté · non documenté</span></th>
        </tr></thead>
        <tbody>{"".join(lig)}</tbody>
      </table>
    </div></div></div>
    <div class="rappel"><b>Les colonnes chiffrées se trient</b>, par un clic sur leur
      titre, dans un sens puis dans l'autre. Un tri décroissant par dépassements met en
      tête les communes où une mesure a franchi le seuil applicable le jour du
      prélèvement — <b>et non les plus mal loties</b> : une commune qui a fait chercher
      627 paramètres a mécaniquement plus d'occasions d'en voir un dépasser qu'une
      commune qui en a cherché 234. C'est pourquoi la colonne de l'effort de recherche
      reste à côté, et pourquoi le taux (‰) accompagne le compte.</div>
    <div class="rappel"><b>« Hors de portée du laboratoire »</b> : le nombre de
      substances cherchées que l'analyse ne pouvait pas voir — le laboratoire ne
      sait les détecter qu'au-dessus d'une valeur elle-même supérieure à la limite
      à laquelle on les compare. Sous cette valeur, on ne peut pas dire que la
      limite est respectée : on peut seulement dire qu'on ne sait pas. <b>Ce n'est
      pas une négligence</b> — c'est ce que l'instrument du jour savait faire, et
      c'est pourquoi le taux (‰) accompagne le compte.</div>
    <div class="rappel"><b>« Statut hormonal des substances trouvées »</b> : trois
      nombres, jamais un seul, et jamais additionnés. Le premier compte les
      substances <b>avérées</b> perturbatrices au sens du droit européen ; le
      deuxième celles que la <b>littérature scientifique soupçonne</b>, sans statut
      réglementaire ; le troisième celles dont la question <b>n'a pas été
      instruite</b> — et « non documenté » n'est pas « non ». Ces trois-là ne
      disent pas la même chose et ne se remplacent pas : les réunir sous un même
      mot ferait passer une question ouverte pour une réponse. Le tri, lui, se fait
      sur les trois réunis, pour trouver vite les communes à regarder de près.
      <b>Un nombre élevé n'est pas un verdict sanitaire</b> : une commune qui fait
      chercher 700 substances en trouvera mécaniquement plus qu'une qui en cherche
      200 — la colonne de l'effort de recherche reste à côté pour cette raison.</div>
    <div class="rappel"><b>Les communes non documentées se rangent à part, jamais en
      tête d'un tri.</b> Elles n'ont pas « zéro dépassement » : elles n'ont pas de
      valeur du tout, et les faire passer pour les plus sûres du département serait
      l'erreur exacte que le troisième état sert à éviter.</div>
    {RAPPEL_EFFORT}
  </section>

  {bloc_uge}

  {bloc_arretes(dept, nom_dept)}
"""


FAMILLE_EN_CLAIR = {
    "pesticide": "Pesticides", "metabolite": "Métabolites de pesticides",
    "metal": "Métaux", "metalloide": "Métalloïdes", "mineral": "Minéraux",
    "organique": "Composés organiques", "PFAS": "PFAS",
    "sous-produit desinfection": "Sous-produits de désinfection",
    "microbiologique": "Microbiologie", "radiologique": "Radiologique",
    "organoleptique": "Organoleptique", "equilibre": "Équilibre calcocarbonique",
    "nitrates": "Nitrates", "nitrites": "Nitrites",
}


def page_substances(con, version, repertoire, dossiers):
    """
    Le répertoire — TOUT ce que le corpus cherche dans l'eau, paramètre par paramètre.

    C'est ce qu'un lecteur attend en cliquant « Substances » : *qu'a-t-on
    cherché dans mon eau, et qu'est-ce que c'est ?* Jusqu'au 15 août 2026 cette
    adresse portait les quatre dossiers rédigés — quatre métabolites — et
    laissait croire que le projet n'en suivait que quatre. Les dossiers ont
    leur propre entrée désormais : `reclassements.html`.

    **Le tableau ne classe pas et ne compare pas** (§2.11). Il est rangé par
    famille puis par ordre alphabétique, jamais par nombre de dépassements :
    deux molécules ne sont pas cherchées dans les mêmes bulletins, et les
    aligner par leur compte ferait un palmarès dont le premier facteur serait
    l'effort de recherche.
    """
    par_famille = {}
    for f in repertoire:
        par_famille.setdefault(f["famille"] or "", []).append(f)

    total = len(repertoire)
    corpus = repertoire[0]["corpus"] if repertoire else 0
    compte = {k: sum(1 for f in repertoire if f["origine_seuil"] == k)
              for k in ("ligne", "regle", "declare", "absent")}
    jamais = sum(1 for f in repertoire if not f["quantifiees"])

    blocs = []
    for cle in sorted(par_famille, key=lambda c: (c == "", FAMILLE_EN_CLAIR.get(c, c))):
        molecules = sorted(par_famille[cle], key=lambda f: f["libelle"].lower())
        titre = FAMILLE_EN_CLAIR.get(cle, cle) or "Famille non renseignée"
        lignes = []
        for f in molecules:
            nature = (DP.NATURE_EN_CLAIR.get(f["nature"], "—")
                      if f["seuil_2026"] is not None else "rien à quoi comparer")
            valeur = (f'{h(BF._nb(f["seuil_2026"]))} {h(f["unite"] or "")}'
                      if f["seuil_2026"] is not None else "—")
            if f["seuil_2016"] is not None and f["seuil_2016"] != f["seuil_2026"]:
                valeur = (f'{h(BF._nb(f["seuil_2016"]))} → ' + valeur)
            depuis = (h(BF._date_fr(f["date_applicabilite"]))
                      if f["date_applicabilite"] else "—")
            pastille = ('<span class="pill">dossier</span>'
                        if f["slug"] in dossiers else "")
            lignes.append(
                f'<tr><td><a href="substance/{h(f["slug"])}.html">{h(f["libelle"])}</a>'
                f' {pastille}</td><td>{h(nature)}</td><td>{valeur}</td>'
                f'<td>{depuis}</td>'
                f'<td class="num">{f["mesures"]}</td>'
                f'<td class="num">{f["quantifiees"]}</td>'
                f'<td class="num">{f["communes_quantifiee"]}</td></tr>')
        # Le répertoire compte 1 243 paramètres, dont 612 pesticides : une
        # famille entière déroulée fait perdre la page. Les 25 premiers, le
        # reste sous un repli qui dit son nombre — jamais tronqué (§2.8).
        def tableau(rangs):
            return ('<div class="tableau"><div class="tableau-defile"><table>'
                    '<thead><tr><th>Substance</th><th>Nature</th>'
                    '<th>Valeur de comparaison</th><th>Applicable depuis</th>'
                    '<th class="num">Cherché</th><th class="num">Quantifié</th>'
                    '<th class="num">Communes</th></tr></thead><tbody>'
                    + "".join(rangs) + '</tbody></table></div></div>')

        corps_f = tableau(lignes[:25])
        if len(lignes) > 25:
            corps_f += (f'<details class="plus"><summary>Afficher les '
                        f'{len(lignes) - 25} autres de cette famille</summary>'
                        + tableau(lignes[25:]) + '</details>')
        blocs.append(f'<section><h3 class="sec">{h(titre)} — {len(molecules)}'
                     f'</h3>{corps_f}</section>')

    filtre = (f'<div class="filtre-rep">'
              f'<input id="q-rep" type="search" autocomplete="off" '
              f'placeholder="Filtrer : nom de substance, famille…" '
              f'aria-label="Filtrer le répertoire">'
              f'<output id="n-rep" for="q-rep">{total} paramètres</output>'
              f'</div>')

    return f"""
  <section style="margin-top:0"><div class="prose">
    <p><b>{total} paramètres</b> ont été cherchés au moins une fois dans les
      {corpus} bulletins complets du corpus. Chacun a sa page : ce qu'il est,
      à quoi on le compare et depuis quand, et ce que le corpus en dit.</p>
    <p class="bnote"><b>Ce tableau ne classe rien.</b> Il est rangé par famille
      puis par ordre alphabétique, jamais par nombre de dépassements. Deux
      paramètres ne sont pas cherchés dans les mêmes bulletins : les aligner par
      leur compte ferait un palmarès dont le premier facteur serait l'effort de
      recherche, pas l'état de l'eau. La colonne « cherché » est le
      dénominateur, et elle ne se sépare jamais des deux suivantes.</p>
  </div></section>

  <section><h3 class="sec">Ce que le projet peut dire, et ce qu'il ne peut pas</h3>
    <div class="tableau"><div class="tableau-defile">
    <table><thead><tr><th>D'où vient le terme de comparaison</th>
      <th class="num">Paramètres</th><th>Ce que ça permet</th></tr></thead><tbody>
      <tr><td>Une ligne du référentiel qui lui est propre</td>
        <td class="num">{compte['ligne']}</td>
        <td>valeur sourcée et datée, verdict au sens plein</td></tr>
      <tr><td>Une règle de famille</td><td class="num">{compte['regle']}</td>
        <td>noté avec son groupe, sans valeur lue pour lui</td></tr>
      <tr><td>La limite déclarée par la source</td><td class="num">{compte['declare']}</td>
        <td>aucun verdict 2016, aucune bascule (§2.8)</td></tr>
      <tr><td>Aucun</td><td class="num">{compte['absent']}</td>
        <td>mesuré, mais aucun verdict n'est prononcé</td></tr>
    </tbody></table></div></div>
    <p class="bnote"><b>La majorité des paramètres est notée par une règle de
      famille, pas par une valeur lue pour elle.</b> C'est ce que fait aussi
      l'administration, et ce n'est pas un défaut — mais le taire ferait passer
      ce répertoire pour un travail de sourçage paramètre par paramètre qu'il
      n'est pas. Le §2.8 impose de distinguer les trois sources de seuil ; cette
      page les compte.</p>
    <p class="bnote"><b>{jamais} paramètres n'ont jamais été quantifiés</b> dans
      le corpus. Cela ne veut pas dire qu'ils sont absents : aucune analyse ne
      les a vus au-dessus de la limite de quantification du laboratoire, ce qui
      n'est pas la même chose (§2.4).</p>
  </section>
{filtre}
  <div class="repertoire">{''.join(blocs)}</div>"""


def page_reclassements(con, version, substances):
    """
    L'index des dossiers de substance — les valeurs qui ont bougé.

    À ne pas confondre avec `page_substances`, qui est le répertoire de TOUT ce
    que le corpus cherche. Cette page-ci ne porte que les quelques molécules
    dont un texte a déplacé la valeur et dont le déplacement a été rédigé et
    relu. Les deux étaient confondues sous le nom « Substances » jusqu'au
    15 août 2026 : un lecteur qui cliquait « Substances » tombait sur quatre
    métabolites et pouvait croire que le projet n'en suit que quatre.

    Il ne recopie rien des pages : il donne, pour chacune, la NATURE de la
    valeur qui la note, la date à laquelle cette valeur a bougé et le nombre
    d'analyses que ce déplacement fait basculer. Le reste se lit sur la page.

    **La colonne de nature n'est pas un ornement : sans elle la page ment.**
    Les dossiers publiés sont des métabolites reclassés « non pertinents » —
    leur 0,9 µg/L est une valeur de vigilance, pas une limite de qualité
    opposable. Un tableau qui aligne « 0,1 → 0,9 µg/L, applicable depuis le
    29 avril 2024 » sans le dire fait lire un relâchement de limite là où il y
    a eu sortie du périmètre opposable. C'est le §9.3(b) de `docs/REPRISE.md`
    transposé de la fiche à l'index, et le §2.13 cinquième cas : un
    reclassement de pertinence déplace deux verdicts, celui de la substance et
    celui du total des pesticides dont elle sort le même jour.
    """
    if not substances:
        return """
  <section style="margin-top:0"><div class="prose">
    <p>Aucun dossier de substance n'est encore publié.</p>
  </div></section>"""

    lignes, corpus, metabolites, a_verifier, naturelles = [], 0, 0, [], set()
    for slug, libelle, origine in substances:
        s = DP.seuil(con, libelle, version)
        c = DP.chiffres(con, libelle, version)
        corpus = c["corpus"] or corpus
        if (c["famille"] or "") == "metabolite":
            metabolites += 1
        if s and (s[7] or "") != "verifie":
            a_verifier.append(libelle)
        deplacement = (f"{h(BF._nb(s[2]))} → {h(BF._nb(s[3]))} {h(s[1] or '')}"
                       if s and s[2] is not None and s[3] is not None else "—")
        date = h(BF._date_fr(s[4])) if s and s[4] else "sans date au référentiel"
        naturelles.add(c["nature"])
        nature = h(DP.NATURE_EN_CLAIR.get(c["nature"], "—"))
        marque = ('<span class="pill">à relire</span>' if origine == "propose" else "")
        drapeau = ('<span class="pill">à vérifier</span>'
                   if s and (s[7] or "") != "verifie" else "")
        lignes.append(
            f'<tr><td><a href="substance/{h(slug)}.html">{h(libelle)}</a> '
            f'{marque}{drapeau}</td>'
            f'<td>{nature}</td><td>{deplacement}</td><td>{date}</td>'
            f'<td class="num">{c["bascules"]}</td>'
            f'<td class="num">{c["communes_bascule"]}</td>'
            f'<td class="num">{c["mesures"]}</td></tr>')

    # §2.12 — le 0,1 µg/L d'avant n'est pas lu dans un texte de 2016 pour un
    # métabolite : il vient de l'instruction de décembre 2020. L'index invoque
    # la grille de 2016 une fois par ligne ; il doit donc le dire une fois.
    note_metabolites = ("" if not metabolites else
                        f'\n    <p class="bnote">{DP.NOTE_METABOLITE}</p>')

    # Ce que chaque nature autorise à conclure — pris à la même source que les
    # pages elles-mêmes, et restreint aux natures effectivement présentes dans
    # le tableau. Recopier ces phrases ici en ferait une seconde version, qui
    # divergerait de celle des pages à la première retouche.
    note_natures = "".join(
        f'\n    <p class="bnote"><b>{h(DP.NATURE_EN_CLAIR[n])}.</b> '
        f'{DP.PORTEE_NATURE[n]}</p>'
        for n in ("limite", "reference", "vigilance", "referentiel_sans_statut")
        if n in naturelles)

    note_fiabilite = ("" if not a_verifier else f"""
    <p class="bnote"><b>Valeur en « à vérifier » :</b>
      {h(', '.join(a_verifier))}. Le seuil n'a pas été lu sur une source primaire
      en session ; il est signalé comme tel et ne s'arrondit jamais en
      « vérifié ».</p>""")

    return f"""
  <section style="margin-top:0"><div class="prose">
    <p>Le <a href="substances.html">répertoire</a> dit ce que le corpus cherche
      dans l'eau, molécule par molécule. Ces pages-ci répondent à une autre
      question : <b>qu'est-ce que cette substance démontre ?</b> Une molécule,
      une date de reclassement, et deux verdicts opposés pour un même résultat —
      c'est là que le déplacement des seuils se voit le mieux.</p>
    <p class="bnote">Le nombre d'analyses porté par une substance ne se lit jamais seul :
      une substance n'est présente que dans les bulletins qui la cherchent, et la
      colonne « analyses » donne ce dénominateur, sur les {corpus} bulletins complets
      du corpus. Une comparaison entre deux substances n'aurait pas de sens ici —
      elles ne sont pas cherchées dans les mêmes bulletins.</p>
  </div></section>

  <section><h3 class="sec">Les dossiers publiés</h3>
    <div class="tableau"><div class="tableau-defile">
    <table><thead><tr>
      <th>Substance</th><th>Nature de la valeur</th>
      <th>Déplacement de la valeur</th><th>Applicable depuis</th>
      <th class="num">Analyses basculées</th><th class="num">Communes</th>
      <th class="num">Analyses</th>
    </tr></thead><tbody>{''.join(lignes)}</tbody></table></div></div>

    <p class="bnote"><b>La nature de la valeur commande la lecture de toute la
      ligne.</b> Aligner des natures différentes dans une même colonne de
      chiffres sans les distinguer ferait lire un relâchement de limite là où il
      n'y en a pas eu.</p>{note_natures}
    <p class="bnote">« Analyses basculées » : des mesures qui dépassaient la valeur
      applicable avant le reclassement et ne dépassent pas celle d'après. La mesure
      n'a pas changé — la règle, si.</p>{note_metabolites}{note_fiabilite}
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
    <div class="tableau"><div class="tableau-defile">
    <table><thead><tr><th>Grille</th><th>Question posée</th></tr></thead><tbody>
      <tr><td>2016</td><td>Cette eau aurait-elle été potable selon la norme d'il y a dix ans ?</td></tr>
      <tr><td>2026</td><td>Est-elle potable selon la norme en vigueur aujourd'hui ?</td></tr>
      <tr><td>stricte</td><td>Serait-elle potable selon la norme la plus protectrice au monde ?</td></tr>
    </tbody></table></div></div>
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

    <h4>Comment cet indice est calculé, exactement</h4>
    <p>Publier un chiffre sans sa formule, c'est demander qu'on le croie. Voici donc
      le calcul entier, tel que le programme l'exécute.</p>
    <p><b>Pour chaque substance retenue, on divise la valeur mesurée par la limite qui
      lui est applicable, et on additionne ces fractions.</b> Une substance à la moitié
      de sa limite apporte 0,5. Deux substances chacune à la moitié de la leur
      apportent 1,0 — l'équivalent d'une limite entière occupée, alors qu'aucune des
      deux n'a franchi la sienne. C'est tout le propos.</p>
    <div class="tableau"><div class="tableau-defile">
    <table><thead><tr><th>Substance</th><th>Mesurée</th><th>Limite</th>
      <th class="num">Fraction</th></tr></thead><tbody>
      <tr><td>ESA métolachlore</td><td>0,42 µg/L</td><td>0,9 µg/L</td>
        <td class="num">0,4667</td></tr>
      <tr><td>Boscalid</td><td>0,05 µg/L</td><td>0,1 µg/L</td>
        <td class="num">0,5</td></tr>
      <tr><td>Quinmérac</td><td>0,25 µg/L</td><td>0,1 µg/L</td>
        <td class="num">2,5</td></tr>
      <tr><td colspan="3"><b>Indice, sur 3 substances</b></td>
        <td class="num"><b>3,4667</b></td></tr>
    </tbody></table></div></div>
    <p class="bnote">Cet exemple n'est pas une commune réelle : c'est le bulletin de
      contrôle du programme, revérifié à chaque exécution des tests.</p>
    <p><b>Quatre règles décident de ce qui entre dans la somme :</b></p>
    <ul>
      <li><b>seulement les substances effectivement quantifiées.</b> Une substance
        cherchée et non trouvée n'apporte rien — et surtout pas zéro, puisqu'un
        laboratoire qui ne trouve rien ne mesure pas zéro. L'indice est donc un
        <b>plancher</b> ;</li>
      <li><b>jamais les lignes de somme</b>, sans quoi le « total des pesticides »
        serait compté en même temps que les substances qui le composent ;</li>
      <li><b>seulement les substances de synthèse</b> — pesticides, métabolites,
        PFAS, composés organiques ;</li>
      <li><b>seulement quand une limite existe.</b> Sans limite au dénominateur, il
        n'y a pas de fraction à calculer.</li>
    </ul>
    <p><b>Pourquoi les minéraux sont écartés, et ce n'est pas un choix de confort.</b>
      Un premier calcul incluant tous les paramètres notés a été fait, puis abandonné :
      sur un bulletin réel, le potassium, les chlorures, les sulfates et le sodium
      pesaient plus lourd que tous les micropolluants réunis et portaient le total
      au-dessus de 1 — sans qu'aucune substance de synthèse n'y soit pour rien.
      Additionner une fraction de la référence en sodium à une fraction de la limite
      d'un pesticide n'a pas de sens : ce ne sont pas les mêmes objets, et ces limites
      n'ont pas la même nature.</p>
    <p><b>Conséquence, et c'est pourquoi le nombre de substances est toujours
      affiché :</b> une substance dont la famille chimique n'est pas connue n'entre pas
      dans l'indice, même mesurée, même au-dessus de sa limite. Sans le nombre qui
      l'accompagne, un indice n'est pas interprétable.</p>
    <p class="bnote"><b>Deux limites que nous devons dire.</b> Le dénominateur est une
      limite réglementaire, pas une dose de référence toxicologique : une limite de
      qualité intègre aussi de la faisabilité analytique et de l'histoire. Diviser une
      mesure par elle donne « quelle part de la limite est occupée », et non « quelle
      part d'une dose sans effet est atteinte ». Et l'indice est calculé contre la
      grille en vigueur aujourd'hui, non contre celle applicable le jour du
      prélèvement : c'est une lecture contrefactuelle, pas le verdict rendu à
      l'époque.</p>

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
        f"<li><a href='donnees/{h(f)}'>{h(f)}</a> — {h(d)} ({_poids(t)}"
        f"{', comprimé' if f.endswith('.gz') else ''})</li>"
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

    <h4>Comment citer l'Observatoire</h4>
    <p>Ces fichiers sont sous <b>ODbL 1.0</b>. La licence demande une mention, et nous en
      écrivons la forme — <b>elle est due dès l'usage public</b>, pas seulement si vous
      redistribuez les fichiers&nbsp;: dès que vous publiez une carte, un tableau, un article
      chiffré ou une application qui s'appuie dessus.</p>
    <p class="note note--attention">Contient des informations de l'<b>Observatoire de la
      potabilité réglementaire</b> (Éditions Mytae), mises à disposition
      <a href="index.html">ici</a> sous
      <a href="https://opendatacommons.org/licenses/odbl/1-0/" rel="license noopener"
         target="_blank">Open Database License (ODbL) 1.0</a>.</p>
    <p class="bnote"><b>Le lien pointe vers l'accueil</b>, et non vers une page intérieure&nbsp;:
      c'est là que se trouvent la méthode, les limites et la traçabilité sans lesquelles un
      chiffre de ce projet ne veut rien dire. Nous n'interdisons à personne de lier la page de
      son choix — nous disons seulement où l'attribution renvoie.</p>
    <p class="bnote">Quand la place le permet&nbsp;: <b>Observatoire de la potabilité
      réglementaire</b> — <a href="index.html">eau.yannick-mytae.fr</a> — un projet des
      <a href="https://editions.mytae.fr/" rel="noopener" target="_blank">Éditions Mytae</a>,
      porté par <a href="https://yannick-mytae.fr/" rel="noopener" target="_blank">Yannick
      Mytae</a>. <b>La mention courte suffit toujours</b> — une obligation trop lourde ne
      serait pas respectée.</p>
    <p class="bnote"><b>Les mesures, elles, ne sont pas à nous.</b> Elles viennent de SISE-Eaux
      via Hub'Eau, sous Licence Ouverte 2.0, et chacun peut aller les chercher. Ce que l'ODbL
      couvre est le <b>rapprochement</b>&nbsp;: un référentiel de seuils daté et sourcé, et les
      verdicts qu'il produit. Et <b>citer n'est pas être approuvé</b> — voir
      <a href="mentions-legales.html">les mentions légales</a>.</p>
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
    <div class="tableau"><div class="tableau-defile">
      <table>
        <thead><tr><th>Paramètre</th><th>Seuil 2016</th><th>Seuil 2026</th>
          <th>Seuil strict</th><th>Unité</th><th>Sources</th><th>Fiabilité</th></tr></thead>
        <tbody>{lignes}</tbody>
      </table>
    </div></div>
  </section>
"""


def _vue_existe(con, nom):
    return bool(con.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = ?", [nom]).fetchone())


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
def _cellule(v):
    """Un booléen sort en 1/0.

    `True`/`False` est le `repr` de Python, pas une convention CSV : R lit
    `TRUE`, Excel ne sait pas trancher, et cela coûtait 4 à 5 octets par valeur
    sur treize colonnes booléennes — 78 Mo du seul verdicts.csv, mesuré le
    10 août 2026.
    """
    return (1 if v else 0) if isinstance(v, bool) else v


def exporter(con, version, dossier):
    """Les données du site, réutilisables telles quelles. Un observatoire qui
    ne rend pas ses données interrogeables se demande d'être cru sur parole.

    Deux règles de forme, arrêtées le 10 août 2026 après mesure :

    - **le gros export est comprimé et découpé par département.** Le détail
      paramètre par paramètre pesait 291 Mo pour 1 265 589 lignes, et croît
      avec chaque département collecté. Comprimé il tombe d'un facteur ~12, et
      découpé il évite de faire télécharger la France pour lire le Tarn — ce
      qui est aussi la maille de comparaison du §2.11. La compression est faite
      ICI, une fois : demander à un hébergement mutualisé de gziper des
      centaines de Mo à chaque téléchargement serait le déplacer, pas le régler.
    - **les petits exports restent en CSV nu**, directement ouvrables. Les
      comprimer ajouterait une manipulation pour un gain négligeable.

    Ce qui n'a PAS été retiré : `version_referentiel`, pourtant constante dans
    un export donné et donc 14,5 Mo de répétition. L'obligation 9 du §8bis veut
    que chaque sortie porte sa traçabilité, et la compression rend une colonne
    constante à peu près gratuite : il n'y avait pas d'arbitrage à faire.
    """
    os.makedirs(dossier, exist_ok=True)

    # Le détail est découpé : les fichiers d'une construction précédente ne se
    # recouvrent pas forcément (un département qui sort du corpus, l'ancien
    # verdicts.csv monolithique). Sans ce ménage ils resteraient sur place, et
    # seraient publiés — site/publier.py envoie ce qu'il trouve.
    for reste in os.listdir(dossier):
        if reste == "verdicts.csv" or (reste.startswith("verdicts_")
                                       and reste.endswith(".csv.gz")):
            os.remove(os.path.join(dossier, reste))

    produits = []

    def dump(nom, requete, description, params=None):
        rows = con.execute(requete, params if params is not None
                           else [version]).fetchall()
        cols = [d[0] for d in con.description]
        chemin = os.path.join(dossier, nom)
        lignes = ([_cellule(v) for v in r] for r in rows)
        if nom.endswith(".gz"):
            ouvrir = lambda: gzip.open(chemin, "wt", encoding="utf-8-sig",  # noqa: E731
                                       newline="", compresslevel=9)
        else:
            ouvrir = lambda: open(chemin, "w", encoding="utf-8-sig",  # noqa: E731
                                  newline="")
        with ouvrir() as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(cols)
            w.writerows(lignes)
        produits.append((nom, description, os.path.getsize(chemin)))

    dump("bulletins.csv",
         "SELECT * FROM analyses_figees WHERE version_referentiel = ?"
         + _filtre_dept()[0] + " ORDER BY commune, date_prelevement",
         "un bulletin par ligne : verdicts, couverture, effort de recherche, sommes",
         params=[version] + _filtre_dept()[1])

    # Le détail, découpé par département. Le rattachement passe par la commune
    # du prélèvement lui-même, pas par celle qui l'emprunte.
    DETAIL = """
        SELECT v.* FROM verdicts_figes v
        JOIN prelevements p ON p.code_prelevement = v.code_prelevement
        JOIN communes c ON c.code_insee = p.code_insee
        WHERE v.version_referentiel = ?{filtre}
        ORDER BY v.code_prelevement, v.libelle_parametre"""
    depts = [r[0] for r in con.execute("""
        SELECT DISTINCT c.code_departement
        FROM verdicts_figes v
        JOIN prelevements p ON p.code_prelevement = v.code_prelevement
        JOIN communes c ON c.code_insee = p.code_insee
        WHERE v.version_referentiel = ?""" + _filtre_dept("c.code_departement")[0] + """
        ORDER BY 1""", [version] + _filtre_dept()[1]).fetchall()]
    for d in depts:
        dump(f"verdicts_{d}.csv.gz",
             DETAIL.format(filtre=" AND c.code_departement = ?"),
             "le détail paramètre par paramètre, avec le seuil applicable à la "
             f"date — {_nom_dept(d)} ({d})",
             params=[version, d])

    dump("couverture_communes.csv",
         "SELECT * FROM couverture_communes WHERE version_referentiel = ?"
         + _filtre_dept()[0] + " ORDER BY commune",
         "le statut de chaque commune, dont les non documentées",
         params=[version] + _filtre_dept()[1])
    # La base du barème de finesse analytique (chantier C4). Les fiches
    # affirment « dix fois moins fin que la plus basse relevée » : la table qui
    # le dit doit être téléchargeable, sinon l'affirmation demande d'être crue
    # sur parole — et elle se déplacera avec le corpus.
    dump("lq_corpus.csv",
         "SELECT * FROM lq_corpus WHERE version_referentiel = ? ORDER BY libelle_parametre",
         "l'étendue des limites de quantification observées, paramètre par paramètre")

    shutil.copyfile(REF_CSV, os.path.join(dossier, "referentiel_seuils.csv"))
    # L'ATTRIBUTION, DÉPOSÉE À CÔTÉ DES FICHIERS.
    #
    # Elle n'est PAS mise en en-tête des CSV, et c'est un arbitrage : une ligne
    # de commentaire en tête casse `read_csv` chez qui ne l'attend pas, et la
    # promesse de ces exports est d'être « directement ouvrables ». Une
    # attribution qui casse le fichier qu'elle accompagne ne sera pas
    # respectée, elle sera supprimée.
    #
    # Déposée à côté, elle voyage avec le dossier — c'est ce qu'on télécharge —
    # et elle se lit sans outil. C'est le meilleur compromis trouvé ; si un
    # jour les exports partent fichier par fichier, la question se reposera.
    with open(os.path.join(dossier, "ATTRIBUTION.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(f"""OBSERVATOIRE DE LA POTABILITÉ RÉGLEMENTAIRE — attribution
================================================================

Ces fichiers sont mis à disposition sous Open Database License (ODbL) 1.0.
   https://opendatacommons.org/licenses/odbl/1-0/

MENTION À REPRENDRE, et elle est due dès l'usage public — pas seulement si
vous redistribuez ces fichiers, mais dès que vous publiez une carte, un
tableau, un article chiffré ou une application qui s'appuie dessus :

   Contient des informations de l'Observatoire de la potabilité
   réglementaire (Éditions Mytae), https://eau.yannick-mytae.fr/,
   sous Open Database License (ODbL) 1.0.

Le lien pointe vers l'accueil : c'est là que se trouvent la méthode, les
limites et la traçabilité sans lesquelles un chiffre de ce projet ne veut
rien dire.

   Observatoire   https://eau.yannick-mytae.fr/
   Éditions Mytae https://editions.mytae.fr/
   Yannick Mytae  https://yannick-mytae.fr/

CE QUE CES FICHIERS SONT
Les mesures brutes viennent de SISE-Eaux (ministère chargé de la santé) via
l'API publique Hub'Eau, sous Licence Ouverte 2.0 — elles ne nous
appartiennent pas et chacun peut aller les chercher. Ce qui est à nous, et
que l'ODbL couvre, est le RAPPROCHEMENT : un référentiel de seuils daté et
sourcé, et les verdicts qu'il produit.

PARTAGE À L'IDENTIQUE
Une base dérivée publiquement utilisée reste sous ODbL, et vous devez en
offrir une copie lisible par machine (ODbL §4.4 et §4.6).

ATTRIBUTION N'EST PAS CAUTION
Citer l'Observatoire ne vaut pas approbation de ce qui en est tiré. Le
projet ne recommande aucun équipement, aucun traitement domestique de l'eau
et aucun produit.

Version du référentiel : {version}
Licences complètes : LICENCE.md du dépôt.
""")
    produits.append(("ATTRIBUTION.txt",
                     "la mention à reprendre, et ce qu'elle couvre",
                     os.path.getsize(os.path.join(dossier, "ATTRIBUTION.txt"))))

    produits.append(("referentiel_seuils.csv", "le référentiel daté de seuils, source de vérité du projet",
                     os.path.getsize(REF_CSV)))
    return produits


def _poids(octets):
    """Ko en dessous du mégaoctet, Mo au-delà — un « 23 000 Ko » ne se lit pas."""
    return (f"{octets / 1048576:.1f} Mo" if octets >= 1048576
            else f"{max(1, round(octets / 1024))} Ko")


# ---------------------------------------------------------------------------
def construire(destination=None, db=DB_PATH, depts=None, communes=None,
               sans_fiches=False, depts_fiches=None, legal_incomplet=False):
    """
    `communes` — un jeu de codes INSEE, et c'est un outil d'APERÇU, pas de
    publication. Ajouté le 16 août 2026 : juger une fiche demandait jusque-là
    de reconstruire le site entier, quatre heures, ou au mieux trois
    départements, trente-cinq minutes. Pour regarder trois fiches, c'est un
    prix qui décourage de regarder — et une forme qu'on ne regarde pas est une
    forme qu'on publie sans la voir. C'est exactement ce qui vient d'arriver
    aux fiches communales.

    Le reste du site est produit normalement : l'accueil et les pages de
    département continuent de lier TOUTES les communes, dont les fiches ne
    seront pas écrites. Les liens y sont donc morts. C'est admis pour un
    aperçu, et c'est pourquoi ce mode refuse d'écrire dans `site/public`.
    """
    global DEPTS_PUBLIES
    # Sans `--depts`, on lit la source de vérité du dépôt plutôt que de publier
    # tout ce qui traîne dans la base. `--depts` reste possible pour un essai,
    # mais il ne doit pas devenir la façon normale de publier : trois copies
    # d'une même liste divergent à la première retouche.
    depts = depts or departements_publies()
    DEPTS_PUBLIES = tuple(depts) if depts else None
    if DEPTS_PUBLIES:
        print(f"départements publiés : {', '.join(DEPTS_PUBLIES)} "
              f"({len(DEPTS_PUBLIES)}, depuis referentiel/departements_publies.csv)")
    else:
        print("ATTENTION — aucun département déclaré publiable : on publie TOUT "
              "ce qui est figé, y compris les départements à moitié collectés.\n"
              "  renseigne referentiel/departements_publies.csv")
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
                "nb_mesures_lues", "nom_uge", "noms_reseaux", "nb_aveugles",
                "aveugles_pour_mille", "code_prelevement"]
        # Les trois registres hormonaux, en UNE requête pour tout le corpus.
        hormonal = IND.compter_hormonal(con, version)
        lignes = []
        for r in corpus(con, version):
            c = dict(zip(cols, r))
            c["hormonal"] = hormonal.get(c["code_prelevement"])
            c["niveau"] = niveau_commune(c["statut"], c["nb_depasse_applicable"],
                                         c["nb_bascules"], c["nb_indetermines"])
            c["teinte"] = teinte_commune(c["statut"], c["nb_depasse_applicable"],
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

        # --- ce qui a été publié, pour que le contrôle puisse le savoir ------
        # Sans ce fichier, `tests/test_sorties.py` compare les pages produites à
        # la couverture du corpus ENTIER et signale comme manquantes les communes
        # des départements volontairement écartés. Le contrôle doit vérifier
        # qu'aucune commune PUBLIÉE n'a été oubliée, pas qu'on a tout publié.
        os.makedirs(public, exist_ok=True)
        with open(os.path.join(public, "departements_publies.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(DEPTS_PUBLIES) + "\n" if DEPTS_PUBLIES else "")

        # --- pages --------------------------------------------------------
        assets = os.path.join(public, "assets")
        os.makedirs(assets, exist_ok=True)
        for f in ("observatoire.css", "observatoire-v2.css", "polices.css",
                  "fiche.js", "recherche.js", "carte.js", "tableau.js", "tri.js",
                  "barre.js", "marque.svg", "partage.png"):
            shutil.copyfile(os.path.join(GABARITS, f), os.path.join(assets, f))
        # Les polices et les bandeaux, à plat dans `assets/`. Les trois `.woff2`
        # sont déjà sous-ensemblés au jeu français — 34, 41 et 46 ko — et les
        # bandeaux existent en JPEG et en WebP, le `<picture>` choisissant.
        for dossier in ("polices", "photos"):
            source = os.path.join(GABARITS, dossier)
            if not os.path.isdir(source):
                continue
            for f in sorted(os.listdir(source)):
                shutil.copyfile(os.path.join(source, f),
                                os.path.join(assets, f))

        # --- la page de contact -------------------------------------------
        # Son corps vit dans `gabarits/contact-corps.html` et non ici : c'est du
        # HTML éditorial, pas de la composition, et il n'a rien à faire dans un
        # fichier Python. Elle passe par `page()` comme les autres, et c'est le
        # point : la version livrée portait sa propre barre de navigation
        # recopiée à la main, qui aurait divergé de PAGES à la première entrée
        # ajoutée, et appelait encore `observatoire.css` au lieu de la v2.
        #
        # `cle_bandeau` réutilise la photographie de la page Communes. La règle
        # « une photographie par page de navigation » est donc entamée, mais
        # l'alternative était pire : la page livrée datait le même cliché du
        # 10 juin 2022 quand BANDEAUX le date du 1er juin, et les dates viennent
        # de l'EXIF des originaux. Deux dates pour un même fichier, l'une des
        # deux est fausse — on ne l'inscrit pas avant de savoir laquelle.
        #
        # `contact.php` est le SEUL fichier exécuté du site. Il est copié depuis
        # `gabarits/` par la construction, donc suivi par le manifeste de
        # `publier.py` : posé à la main sur le serveur, il aurait survécu aux
        # publications sans jamais être mis à jour.
        shutil.copyfile(os.path.join(GABARITS, "contact.php"),
                        os.path.join(public, "contact.php"))
        ecrire(os.path.join(public, "contact.html"), page(
            "Écrire à l'Observatoire",
            lire("contact-corps.html"),
            "contact.html",
            "Signaler une erreur, verser une source primaire, demander la "
            "collecte d'un département. Formulaire sans captcha, sans service "
            "tiers et sans cookie.", version, calcule_le,
            formule=False, cle_bandeau="communes.html",
            og_titre="Écrire à l'Observatoire",
            sous_titre="Une erreur repérée, une source à verser, un département "
                       "à collecter, une demande de la presse : <b>tout ce qui "
                       "rend le travail plus juste est bienvenu.</b>"))

        ecrire(os.path.join(public, "index.html"), page(
            "Quelle eau buvez-vous ?",
            page_accueil(lignes, these, version, calcule_le, con),
            "index.html",
            "Ce que le mot « conforme » ne dit pas sur l'eau du robinet : la même "
            "mesure, notée contre la norme de 2016, celle d'aujourd'hui, et la plus "
            "stricte au monde.", version, calcule_le,
            formule=False,
            sous_titre="Un outil de conscience citoyenne, construit sur des données "
                       "ouvertes. Il sépare <b>la mesure</b>, qui est un fait, du "
                       "<b>verdict</b>, qui est une convention administrative datée.",
            scripts=f'<script src="assets/{empreinte("recherche.js")}"></script>'))

        # LE PREMIER DOSSIER. Écrit AVANT l'index, et l'ordre compte : c'est
        # cet ensemble qui décide si la carte 01 sera un lien ou un `<div>`.
        # Rien à basculer à la main le jour où le deuxième arrivera.
        ecrire(os.path.join(public, "dossier-panel-reduit.html"), page(
            "Une conformité peut s'obtenir en cessant de mesurer",
            page_dossier_panel_reduit(version), "dossiers.html",
            "Dans 18 communes, des paramètres en dépassement à la dernière "
            "analyse complète n'ont plus été mesurés depuis deux à dix ans. "
            "La conformité affichée dit alors ce qu'on a regardé.",
            version, calcule_le, formule=False, largeur="large",
            cle_bandeau="dossier",
            sous_titre="Un bulletin peut être déclaré conforme sur un panel qui ne "
                       "contient plus ce qui l'avait rendu non conforme. "
                       "<b>L'absence de mesure ne dit rien sur la présence</b> — "
                       "et c'est exactement le point.",
            fil=[("Accueil", "index.html"), ("Les dossiers", "dossiers.html"),
                 ("Conformité sur panel réduit", None)],
            scripts=f'<script src="assets/{empreinte("tri.js")}"></script>'))
        dossiers_publies = {"dossier-panel-reduit.html"}
        # --- à propos, et le texte légal ----------------------------------
        ecrire(os.path.join(public, "a-propos.html"), page(
            "Pourquoi ce site existe",
            page_a_propos(con, version, calcule_le), "a-propos.html",
            "Qui porte l'Observatoire de la potabilité réglementaire, ce qu'il "
            "cherche à rendre visible, et ce qu'il s'interdit.",
            version, calcule_le, formule=False, cle_bandeau="",
            sous_titre="Ce que «&nbsp;conforme&nbsp;» veut dire, et depuis quand.",
            fil=[("Accueil", "index.html"), ("À propos", None)]))

        # LES MENTIONS LÉGALES NE SE PUBLIENT PAS À MOITIÉ.
        # Le corps porte des marques `A_COMPLETER` là où l'information manquait
        # et n'a pas été inventée. Une mention légale approximative est pire
        # qu'une mention absente : elle a l'air d'en être une, et personne ne
        # revient la relire. La construction compte les marques et le dit fort ;
        # `--legal-incomplet` est le geste explicite qui accepte de la produire
        # quand même, pour la relire en local.
        corps_legal = lire("mentions-legales-corps.html")
        n_trous = corps_legal.count("A_COMPLETER")
        if n_trous and not legal_incomplet:
            print(f"  ! mentions-legales.html NON écrite : {n_trous} information(s) "
                  "manquante(s) marquées A_COMPLETER dans "
                  "gabarits/mentions-legales-corps.html.\n"
                  "    Les compléter, ou passer --legal-incomplet pour relire "
                  "la page en local.")
        else:
            if n_trous:
                print(f"  ! mentions-legales.html écrite avec {n_trous} trou(s) "
                      "A_COMPLETER — NE PAS PUBLIER.")
            ecrire(os.path.join(public, "mentions-legales.html"), page(
                "Mentions légales",
                corps_legal, "mentions-legales.html",
                "Éditeur, hébergeur, licences et données personnelles de "
                "l'Observatoire de la potabilité réglementaire.",
                version, calcule_le, formule=False, cle_bandeau="",
                fil=[("Accueil", "index.html"), ("Mentions légales", None)]))

        ecrire(os.path.join(public, "dossiers.html"), page(
            "Les dossiers",
            page_dossiers(con, version, dossiers_publies), "dossiers.html",
            "Les pièces d'enquête de l'Observatoire : ce que chacune établit, "
            "ce qu'elle n'établit pas, et sur combien de communes elle porte.",
            version, calcule_le, formule=False, largeur="large",
            # Le chapô de la maquette, mot pour mot : il dit la seule chose que
            # le lecteur doit savoir avant la liste — aucun de ces huit sujets
            # n'était cherché, ils sont sortis de la donnée.
            sous_titre="Huit mécanismes trouvés en chemin. <b>Aucun n'était visé "
                       "au départ&nbsp;:</b> ils sont sortis de la donnée, et chacun "
                       "porte sa date — le corpus grossit, et un chiffre sans sa "
                       "date est un chiffre faux.",
            fil=[("Accueil", "index.html"), ("Les dossiers", None)]))

        ecrire(os.path.join(public, "carte.html"), page(
            "Où en est la collecte",
            page_carte(lignes, version, calcule_le, comptes), "carte.html",
            "Combien d'analyses complètes l'Observatoire détient dans chaque "
            "département — l'avancement d'un travail, pas une carte de la qualité "
            "de l'eau.", version, calcule_le,
            sous_titre="Ce que montre cette page n'est pas l'état de l'eau, c'est "
                       "<b>l'avancement d'un travail</b>. Chaque département porte le "
                       "nombre d'analyses complètes que nous en détenons.",
            formule=False, largeur="large",
            og_titre="Où en est la collecte de l'Observatoire",
            fil=[("Accueil", "index.html"), ("Où en est la collecte", None)]))

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

        # --- une page par molécule cherchée -------------------------------
        #
        # Deux étages, une seule adresse par molécule. Toutes reçoivent le
        # brief dérivé ; les quelques-unes dont le déplacement a été rédigé et
        # relu reçoivent le dossier long à la place — c'est l'ordre de
        # préséance de `dossier_page` : auteur, puis proposé, puis dérivé.
        #
        # Le répertoire est construit en UNE passe (cf. DP.repertoire) : les
        # requêtes par molécule coûtent un balayage chacune, et à 1 243
        # molécules elles balaieraient la table des verdicts des milliers de
        # fois.
        substances = DP.publiables()
        dossiers = {s for s, _l, _o in substances}
        # Les adresses de substance RÉELLEMENT écrites : c'est ce jeu qui
        # autorise la fiche à faire un lien. Le déduire d'un libellé à
        # l'aveugle produirait des liens morts sur des milliers de fiches,
        # et rien ne les signalerait.
        slugs_substances = set(dossiers)
        identites = ID_SUB.charger()
        rep = DP.repertoire(con, version)

        for slug, libelle, _o in substances:
            corps_s, titre_s, origine_s = DP.corps(con, slug, version, h, prefixe="../")
            d_s = (DP.charger()[0].get(slug) or DP.charger()[1].get(slug))
            ecrire(os.path.join(public, "substance", f"{slug}.html"), page(
                titre_s, corps_s, "reclassements.html",
                (d_s.get("chapeau") or titre_s)[:300],
                version, calcule_le, prefixe="../",
                sous_titre=h(d_s.get("titre") or ""),
                fil=[("Accueil", "index.html"),
                     ("Reclassements", "reclassements.html"), (titre_s, None)]))

        slugs_substances |= {f["slug"] for f in rep}
        for f in rep:
            if f["slug"] in dossiers:
                continue                     # le dossier long l'emporte
            ecrire(os.path.join(public, "substance", f'{f["slug"]}.html'), page(
                f["libelle"],
                DP.brief(f, identites, h, prefixe="../"), "substances.html",
                f'Ce que le corpus cherche et trouve sous « {f["libelle"]} » : '
                f'à quoi ce paramètre est comparé, depuis quand, et dans '
                f'combien de bulletins elle est recherchée.',
                version, calcule_le, prefixe="../", formule=False,
                # Refus explicite de photographie, comme la fiche communale :
                # une photographie par page de NAVIGATION, pas une photographie
                # répétée en tête de 1 255 briefs. Sans ce refus, la clé de page
                # `substances.html` leur donnait le cliché du répertoire.
                cle_bandeau="",
                fil=[("Accueil", "index.html"),
                     ("Substances", "substances.html"), (f["libelle"], None)]))

        # LE FILTRE ET LES REPLIS SE CONTREDISENT, et c'est le seul point
        # délicat de cette page : une ligne repliée ne se laisse pas trouver.
        # Dès qu'une recherche est en cours, tous les replis s'ouvrent ; ils
        # se referment quand le champ est vidé. Sans ça, chercher « atrazine »
        # dans une famille de 612 molécules ne rendrait rien alors qu'elle y
        # est — un silence qui se lit comme une absence (§2.4, transposé).
        script_rep = """<script>
(function(){
  var q = document.getElementById('q-rep'), n = document.getElementById('n-rep');
  if (!q) return;
  var lignes = [].slice.call(document.querySelectorAll('.repertoire tbody tr'));
  var sections = [].slice.call(document.querySelectorAll('.repertoire section'));
  var replis = [].slice.call(document.querySelectorAll('.repertoire details'));
  var total = n.textContent;
  q.addEventListener('input', function(){
    var t = q.value.trim().toLowerCase(), vus = 0;
    replis.forEach(function(d){ d.open = !!t; });
    lignes.forEach(function(tr){
      var ok = !t || tr.textContent.toLowerCase().indexOf(t) !== -1;
      tr.hidden = !ok; if (ok) vus++;
    });
    sections.forEach(function(s){
      s.hidden = !s.querySelector('tbody tr:not([hidden])');
    });
    n.textContent = t ? (vus + ' entree' + (vus > 1 ? 's' : '') + ' affichee'
                             + (vus > 1 ? 's' : '')) : total;
  });
})();
</script>"""
        ecrire(os.path.join(public, "substances.html"), page(
            "Ce qu'on cherche dans l'eau",
            page_substances(con, version, rep, dossiers), "substances.html",
            "Le répertoire des paramètres recherchés dans le corpus : ce qu'ils "
            "sont, à quoi ils sont comparés, et dans combien de bulletins.",
            version, calcule_le,
            sous_titre="Une fiche communale dit ce qu'il y a dans une eau. Ce "
                       "répertoire dit ce qu'on y a cherché — et ce que le projet "
                       "peut, ou ne peut pas, en conclure.", formule=False,
            scripts=script_rep,
            fil=[("Accueil", "index.html"), ("Ce qu'on cherche dans l'eau", None)]))

        ecrire(os.path.join(public, "reclassements.html"), page(
            "Les valeurs qui ont bougé",
            page_reclassements(con, version, substances), "reclassements.html",
            "Ce que chaque substance démontre du déplacement des seuils : une "
            "page par molécule, avec sa date de reclassement.",
            version, calcule_le,
            sous_titre="Ces pages disent ce qu'une substance démontre — et la "
                       "date à laquelle la règle qui la note a changé.",
            formule=False,
            fil=[("Accueil", "index.html"), ("Les valeurs qui ont bougé", None)]))

        # --- une page par commune documentée ------------------------------
        #
        # LE SEUL POSTE COÛTEUX DE TOUTE LA CONSTRUCTION, et depuis le 16 août
        # il l'est douze fois plus : une page par prélèvement, 45 617 fichiers,
        # 4 h 55. Tout ce qui précède — les huit pages communes, la carte, les
        # départements, les 1 243 pages de substance — tient en quelques
        # minutes. Corriger une virgule sur `methode.html` ne doit donc pas
        # coûter cinq heures.
        if sans_fiches:
            existantes = len(glob.glob(os.path.join(public, "commune", "*.html")))
            print(f"  fiches de commune NON reconstruites (--sans-fiches) : "
                  f"{existantes} page(s) laissées en place")
            # Les anciennes fiches restent valides : `empreinte()` versionne
            # les feuilles par une chaîne de requête (`?v=…`), pas par le nom
            # du fichier. Une fiche non reconstruite continue donc de charger
            # la feuille servie aujourd'hui, avec une empreinte périmée dans
            # l'adresse — le navigateur la recharge, il ne la manque pas.
            n_fiches = existantes
        else:
            n_fiches = fiches_communes(con, version, lignes, public,
                                       communes, depts_fiches,
                                       slugs_substances)

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
    print(f"  {len(PAGES_PLATES)} pages, {n_depts} page(s) de département, "
          f"{n_fiches} fiche(s) de commune, "
          f"{len(exports)} export(s) — {_poids(total)} au total")
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
            formule=False, prefixe="../", largeur="large",
            cle_bandeau="departement",
            fil=[("Accueil", "index.html"),
                 ("Les communes du corpus", "communes.html"),
                 (f"{nom} ({dept})", None)],
            scripts=(f'<script src="../assets/{empreinte("carte.js")}"></script>'
                     f'<script src="../assets/{empreinte("tableau.js")}"></script>')))
        n += 1
    return n


def fiches_communes(con, version, lignes, public, communes=None,
                    depts_fiches=None, slugs=None):
    """
    Une page par commune documentée, bâtie sur le MÊME corps et le MÊME rendu
    que la fiche autonome — mêmes obligations d'affichage, mêmes trois états,
    même seuil applicable à la date.
    """
    # Plus de prose écrite depuis le 10 août 2026 : la fiche communale ne
    # porte que le dérivé et les accroches vers les dossiers de substance.
    # Le raisonnement se relit UNE fois par substance, pas 678 fois par commune.

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
        if communes and insee not in communes:
            continue
        # AJOUT D'UN DÉPARTEMENT SANS TOUT REFAIRE. Le reste du site — carte,
        # index de recherche, pages de département, totaux de l'accueil — est
        # bâti sur le corpus ENTIER quelques lignes plus haut : le nouveau
        # département y entre partout. Seules les fiches sont restreintes, et
        # celles des autres départements restent en place telles quelles.
        # À ne pas confondre avec `--depts`, qui restreint ce qui est PUBLIÉ et
        # effacerait les autres de la carte.
        if depts_fiches and c["dept"] not in depts_fiches:
            continue
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

        # `A` garde la ligne brute de chaque bulletin : les sections rendues en
        # Python y lisent les dénominateurs et les décomptes figés.
        C, PARAMS, ORDER, A = {}, {}, [], {}
        for ligne, cols, rattachement in lignes_c:
            a = dict(zip(cols, ligne))
            # La clé est le code de prélèvement, jamais la date (§2.3) : deux
            # points d'eau de la même commune sont souvent prélevés le même
            # jour, et la clé datée en écrasait un silencieusement.
            cle = a["code_prelevement"]
            d_iso = str(a["date_prelevement"])
            C[cle] = BF.bloc_commune(
                con, ligne, cols, None, version,
                rattachement=rattachement, accroches=accroches,
                # Le chapô de l'en-tête nomme le département, il n'en donne
                # pas le code : « Tarn-et-Garonne · réseau FINHAN », pas
                # « 82 · réseau FINHAN ».
                nom_dept=_nom_dept(c["dept"]))
            PARAMS[cle] = BF.bloc_parametres(con, a["code_prelevement"], version)
            A[cle] = a
            ORDER.append(cle)
        # Le plus récent d'abord : c'est ce que l'habitant vient chercher.
        ORDER.sort(key=lambda k: C[k]["date_iso"], reverse=True)

        j = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
        situation = bloc_situation(c, groupes.get(c["dept"], []),
                                   rat["commune_prelevement"] if rat else None)
        # L'INSEE de la commune où le prélèvement a réellement eu lieu — pour
        # que le bandeau d'emprunt y mène. Le nom seul ne suffit pas : il y a
        # des homonymes, et un lien mort est pire que pas de lien.
        insee_source = None
        if rat:
            r = con.execute(
                "SELECT code_insee FROM prelevements WHERE code_prelevement = ?",
                [rat["code_prelevement"]]).fetchone()
            insee_source = r[0] if r else None

        # UNE PAGE PAR PRÉLÈVEMENT — décision de Yannick, 16 août 2026.
        #
        # La fiche est maintenant écrite dans le fichier plutôt que fabriquée
        # au chargement ; un sélecteur qui change de bulletin sans recharger la
        # page ne peut donc plus fonctionner. Plutôt que de renvoyer la
        # composition dans le navigateur, chaque bulletin reçoit son adresse —
        # ce qui le rend CITABLE, et c'est cohérent avec un projet dont l'objet
        # est la traçabilité.
        #
        # Le nom du fichier est bâti sur le CODE DE PRÉLÈVEMENT, jamais sur la
        # date (§2.3) : une commune a souvent plusieurs prélèvements le même
        # jour sur des points d'eau différents, et deux pages datées à
        # l'identique s'écraseraient l'une l'autre, silencieusement.
        #
        # L'adresse du plus récent NE CHANGE PAS — `commune/82125.html` reste
        # ce que servent la carte, la liste des communes et les liens déjà
        # publiés. Ce sont les bulletins anciens qui gagnent une adresse.
        def fichier(cle):
            return f"{insee}.html" if cle == ORDER[0] else f"{insee}-{cle}.html"

        for cle in ORDER:
            d, a = C[cle], A[cle]
            tete = BF.tete_html(
                d["tete"], BF.prelevements_html(C, ORDER, cle, fichier))
            # L'ALERTE DE PANEL EST DANS L'EN-TÊTE, pas en bas de page.
            # « La dernière analyse complète de cette eau a 34 mois » n'est pas
            # une note : c'est ce qui conditionne la lecture de tout ce qui
            # suit. Elle était reléguée au bloc non porté, sans couleur.
            tete += BF.emprunt_html(d, insee_source) + BF.alerte_html(d)
            sections = (BF.bascules_html(d) + BF.depassements_html(d)
                        + BF.lectures_html(d, a) + BF.indicateurs_html(d, a)
                        + BF.nourrissons_html(d)
                        + BF.pfas_html(d) + BF.registres_html(d, slugs)
                        + BF.lq_html(d, slugs) + BF.barres_html(d, slugs))

            html = page(
                d["name"],
                # `main` est nu : la tête et chaque section portent leur zone.
                # Ce qui n'est pas encore porté reste enveloppé d'un bloc
                # unique pour ne pas s'étaler sur toute la largeur.
                f'<div class="zone zone-large">{tete}</div>\n{sections}\n'
                f'<section class="section"><div class="zone zone-large">'
                f'{corps}\n{situation}</div></section>',
                "communes.html",
                f"Bulletin d'analyse complet de l'eau du robinet à {d['name']} "
                f"({d['insee']}) prélevé le {d['date']}, noté contre les "
                f"grilles de 2016, d'aujourd'hui et la plus stricte "
                f"identifiée.",
                version, calcule_le=d["calcule_le"],
                sous_titre=f"{h(d['sub'])} — bulletin du {h(d['date'])}",
                # Le `h1` est dans le corps, avec le verdict à côté de lui :
                # c'est la composition de la maquette, l'identité à gauche et
                # ce que dit le bulletin à droite.
                titre_dans_corps=True, largeur="pleine",
                formule=False, prefixe="../", cle_bandeau="",
                fil=[("Accueil", "index.html"),
                     ("Les communes du corpus", "communes.html"),
                     (f"{_nom_dept(c['dept'])} ({c['dept']})",
                      f"departement/{c['dept']}.html"),
                     (d["name"], None if cle == ORDER[0] else fichier(ORDER[0])),
                     *([] if cle == ORDER[0] else [(f"Bulletin du {d['date']}",
                                                    None)])],
                # La page ne porte QUE son bulletin. Elle embarquait ceux de
                # toute la commune pour alimenter le sélecteur — 338 ko sur
                # Montech, dont l'essentiel pour 20 bulletins qu'on ne
                # regardait pas.
                scripts=("<script>\n"
                         f"const KPI_LABELS={j(BF.KPI_LABELS)};\n"
                         f"{BF.js_donnees({cle: d}, {cle: PARAMS[cle]})}\n"
                         f"const ORDER={j([cle])};\n</script>\n"
                         f'<script src="../assets/{empreinte("fiche.js")}">'
                         "</script>"))

            ecrire(os.path.join(public, "commune", fichier(cle)), html)
            n += 1
    return n


def main():
    p = argparse.ArgumentParser(description="Génère la vitrine publique statique")
    p.add_argument("--sortie", help="dossier de destination (défaut : site/public)")
    p.add_argument("--legal-incomplet", action="store_true",
                   help="écrire mentions-legales.html malgré ses marques "
                        "A_COMPLETER — pour relire en local, JAMAIS pour publier")
    p.add_argument("--depts", help="départements à publier, séparés par des virgules "
                                   "(ex. 28,81,69,09,31). Défaut : tous ceux qui sont "
                                   "figés — à n'utiliser que si aucun n'est partiel.")
    p.add_argument("--fiches-depts",
                   help="ne (re)construire QUE les fiches de ces départements, "
                        "en laissant les autres en place. Le reste du site — "
                        "carte, index, pages de département, accueil — est "
                        "bâti sur le corpus entier : c'est ce qui permet "
                        "d'ajouter un département sans refaire les 45 000 "
                        "fiches des précédents.")
    p.add_argument("--sans-fiches", action="store_true",
                   help="reconstruit TOUT sauf les fiches de commune : les huit "
                        "pages communes, la carte, les départements et les "
                        "pages de substance. Les fiches déjà construites sont "
                        "laissées en place. Quelques minutes au lieu de cinq "
                        "heures — c'est la boucle des corrections de forme.")
    p.add_argument("--communes", help="APERÇU : ne rendre que ces codes INSEE, "
                                      "séparés par des virgules. Exige --sortie — "
                                      "un aperçu ne s'écrit jamais dans site/public.")
    a = p.parse_args()
    depts = [d.strip() for d in a.depts.split(",") if d.strip()] if a.depts else None
    communes = ({c.strip() for c in a.communes.split(",") if c.strip()}
                if a.communes else None)
    if communes and not a.sortie:
        p.error("--communes exige --sortie : le site publié ne doit jamais "
                "recevoir une construction partielle, ses liens seraient morts.")
    construire(destination=a.sortie, depts=depts, communes=communes,
               sans_fiches=a.sans_fiches, legal_incomplet=a.legal_incomplet,
               depts_fiches={d.strip() for d in a.fiches_depts.split(",")
                             if d.strip()} if a.fiches_depts else None)


if __name__ == "__main__":
    main()

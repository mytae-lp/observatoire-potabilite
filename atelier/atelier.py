# -*- coding: utf-8 -*-
"""
L'atelier — le poste de pilotage local. **Il ne se publie jamais.**

    python3 atelier/atelier.py            # http://127.0.0.1:8760
    python3 atelier/atelier.py --port 9000

Pourquoi il est séparé de la vitrine
------------------------------------
L'atelier AGIT : il télécharge, il écrit en base, il fige, il publie. La
vitrine ne fait que montrer. Ces deux natures n'ont pas les mêmes besoins et
n'ont surtout pas à courir les mêmes risques.

Un formulaire public qui déclencherait une collecte serait deux fautes à la
fois : une charge abusive sur Hub'Eau, service public gratuit et sans clé
(CLAUDE.md §3.2), et une porte d'entrée sur la base. L'atelier n'écoute donc
que sur 127.0.0.1 : il n'est joignable que depuis cette machine.

Ce qu'il sait faire
-------------------
  · importer une liste de communes (fichier CSV ou liste collée) ;
  · lancer la collecte et la suivre en direct ;
  · afficher les cinq contrôles qualité, à relire après chaque collecte ;
  · éditer les rédactions — les textes de Yannick, jamais générés ;
  · publier : refiger, reconstruire la vitrine et la fiche autonome.

Il n'utilise que la bibliothèque standard : une dépendance de moins à
maintenir sur un outil dont toute la valeur est de durer.
"""
import argparse
import html
import io
import json
import os
import sys
import threading
import traceback
import urllib.parse
from contextlib import redirect_stdout, redirect_stderr
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, os.path.join(RACINE, "sortie"))
sys.path.insert(0, os.path.join(RACINE, "site"))

from common import DB_PATH, SEUIL_COMPLET, lire_liste_communes  # noqa: E402
import figer  # noqa: E402

GABARITS = os.path.join(RACINE, "site", "gabarits")
REDACTIONS = os.path.join(RACINE, "sortie", "redactions.json")

# Les cinq contrôles à relire après chaque collecte. Ils ne sont pas
# décoratifs : un paramètre mesuré mais non apparié existe en base sans peser
# sur aucun verdict, et une commune peut donc être déclarée « sans dépassement »
# alors qu'un dixième de son bulletin n'a jamais été comparé à quoi que ce soit.
CONTROLES = [
    ("v_parametres_non_apparies",
     "Mesures sans aucun seuil de comparaison",
     "Ni le référentiel, ni un alias, ni une règle de famille, ni la limite "
     "déclarée par la source ne leur donne de seuil. Elles existent en base et "
     "ne pèsent sur aucun verdict : c'est le premier endroit où regarder après "
     "une collecte, parce que les libellés varient d'un laboratoire à l'autre."),
    ("v_regle_famille_appliquee",
     "Rattachements automatiques par règle de famille",
     "À relire : une substance qui n'est pas un pesticide et qui porte par "
     "hasard la même limite déclarée y figurerait à tort."),
    ("v_ecarts_referentiel_source",
     "Notre seuil contre celui déclaré par la source",
     "Chaque ligne est soit une erreur de notre référentiel, soit un écart réel "
     "entre le texte et la pratique déclarée. En cas de désaccord, le "
     "référentiel daté du projet prime — mais l'écart se regarde."),
    ("v_unites_incomparables",
     "Unités non réconciliables — aucun verdict produit",
     "Le seuil et la mesure sont dans deux unités qu'on ne sait pas convertir. "
     "Aucun verdict n'est rendu : un verdict faux est pire qu'un verdict absent."),
    ("v_referentiel_jamais_mesure",
     "Lignes du référentiel jamais rencontrées",
     "Soit le paramètre n'est pas cherché sur ce corpus, soit son libellé ne "
     "correspond à rien de ce qui est mesuré — auquel cas il manque un alias."),
    ("v_seuils_sans_date",
     "Seuils dont on ignore la date de déplacement",
     "Ces lignes produisent un verdict potentiellement anachronique : on sait "
     "que la valeur a bougé, pas quand. Tant que la date manque, le verdict "
     "rendu à la date du prélèvement ne peut pas être garanti (§2.10)."),
]


# ---------------------------------------------------------------------------
# État d'une tâche longue (collecte, publication)
# ---------------------------------------------------------------------------
class Tache:
    """Une seule tâche à la fois. Deux collectes concurrentes se disputeraient
    l'écriture de la base et doubleraient la charge sur Hub'Eau."""

    def __init__(self):
        self.verrou = threading.Lock()
        self.lignes = []
        self.titre = None
        self.en_cours = False
        self.fini = False
        self.erreur = None

    def lancer(self, titre, fonction):
        if not self.verrou.acquire(blocking=False):
            return False
        self.lignes, self.titre = [], titre
        self.en_cours, self.fini, self.erreur = True, False, None

        def executer():
            flux = _FluxLignes(self.lignes)
            try:
                with redirect_stdout(flux), redirect_stderr(flux):
                    fonction()
            except SystemExit as e:
                self.erreur = f"interrompu (code {e.code})"
            except Exception:
                self.erreur = traceback.format_exc()
                self.lignes.append(self.erreur)
            finally:
                self.en_cours, self.fini = False, True
                self.verrou.release()

        threading.Thread(target=executer, daemon=True).start()
        return True

    def etat(self):
        return {"titre": self.titre, "en_cours": self.en_cours,
                "fini": self.fini, "erreur": self.erreur,
                "lignes": list(self.lignes)}


class _FluxLignes(io.TextIOBase):
    """Capture la sortie d'un script pour la montrer en direct dans la page."""

    def __init__(self, cible):
        self.cible = cible
        self.tampon = ""

    def write(self, s):
        self.tampon += s
        while "\n" in self.tampon:
            ligne, self.tampon = self.tampon.split("\n", 1)
            self.cible.append(ligne)
        return len(s)

    def flush(self):
        if self.tampon:
            self.cible.append(self.tampon)
            self.tampon = ""


TACHE = Tache()


# ---------------------------------------------------------------------------
# Lecture de l'état de la base
# ---------------------------------------------------------------------------
def etat_base():
    if not os.path.exists(DB_PATH):
        return {"absente": True}
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        e = {"absente": False, "version_fichiers": figer.version_referentiel()}
        e["prelevements"], e["mesures"] = con.execute(
            "SELECT (SELECT COUNT(*) FROM prelevements), (SELECT COUNT(*) FROM mesures)"
        ).fetchone()
        tables = {r[0] for r in con.execute(
            "SELECT table_name FROM information_schema.tables").fetchall()}
        if "analyses_figees" in tables:
            v = con.execute("""
                SELECT version_referentiel, MAX(calcule_le), COUNT(*)
                FROM analyses_figees GROUP BY 1 ORDER BY 2 DESC LIMIT 1
            """).fetchone()
            e["version_figee"], e["calcule_le"], e["bulletins"] = v or (None, None, 0)
            e["couverture"] = con.execute("""
                SELECT statut, COUNT(*) FROM couverture_communes GROUP BY 1 ORDER BY 1
            """).fetchall()
        else:
            e["version_figee"], e["calcule_le"], e["bulletins"] = None, None, 0
            e["couverture"] = []
        return e
    finally:
        con.close()


def controle(nom, limite=200):
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        if not con.execute("SELECT 1 FROM information_schema.tables WHERE table_name = ?",
                           [nom]).fetchone():
            return None, [], 0
        total = con.execute(f"SELECT COUNT(*) FROM {nom}").fetchone()[0]
        rows = con.execute(f"SELECT * FROM {nom} LIMIT {int(limite)}").fetchall()
        return [d[0] for d in con.description], rows, total
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Rendu
# ---------------------------------------------------------------------------
def h(x):
    return html.escape("" if x is None else str(x))


ONGLETS = [("/", "État"), ("/collecte", "Collecte"), ("/controles", "Contrôles"),
           ("/redactions", "Rédactions"), ("/publier", "Publier")]


def page(titre, corps, courant, scripts=""):
    nav = "".join(
        f'<li><a href="{u}"{" aria-current=\"page\"" if u == courant else ""}>{h(n)}</a></li>'
        for u, n in ONGLETS)
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Atelier — {h(titre)}</title>
<link rel="stylesheet" href="/assets/observatoire.css">
<style>
  .masthead{{background:#31404d}}
  .masthead .eyebrow{{color:#f0c987}}
  .nav{{background:#26323d}}
  .atelier-avert{{background:#f0c987;color:#4a3608;font-size:12.5px;font-weight:700;
    padding:7px 0;text-align:center;letter-spacing:.03em}}
  textarea{{width:100%;min-height:170px;font-family:var(--mono);font-size:13px;
    padding:11px;border:1px solid var(--line);border-radius:9px;resize:vertical}}
  input[type=text]{{width:100%;font-family:var(--mono);font-size:13px;padding:10px 12px;
    border:1px solid var(--line);border-radius:9px}}
  label{{display:block;font-size:12px;font-weight:700;text-transform:uppercase;
    letter-spacing:.08em;color:var(--eau);margin:14px 0 5px}}
  .journal{{background:#12263A;color:#DCE7EE;font-family:var(--mono);font-size:12px;
    padding:14px 16px;border-radius:10px;max-height:440px;overflow:auto;
    white-space:pre-wrap;margin-top:14px}}
  .journal .err{{color:#ffb3a7}}
  .bloc{{background:var(--card);border:1px solid var(--line);border-radius:12px;
    padding:18px 20px;margin-bottom:14px}}
  .bloc h4{{margin:0 0 8px;font-size:15px;color:var(--eau-deep);font-weight:800}}
  .bloc p{{margin:0 0 10px;font-size:13.5px;color:var(--ink-soft)}}
  .compte{{font-family:var(--mono);font-weight:700}}
</style></head><body>
<div class="atelier-avert">ATELIER LOCAL — 127.0.0.1 uniquement. Ce poste de pilotage
  ne fait pas partie du site public et ne doit jamais être déposé sur un hébergement.</div>
<div class="masthead"><div class="wrap">
  <div class="eyebrow">Observatoire de la potabilité réglementaire · atelier</div>
  <h1>{h(titre)}</h1>
</div></div>
<nav class="nav"><div class="wrap"><ul>{nav}</ul></div></nav>
<div class="wrap"><section style="margin-top:22px">{corps}</section>
<footer><div class="src">La collecte interroge Hub'Eau, service public gratuit et sans
clé. Pagination maximale, pause entre deux appels, reprise sur incident : le respect du
débit n'est pas optionnel. Un département représente plusieurs milliers d'appels.</div></footer>
</div>{scripts}</body></html>"""


def journal_html():
    return """
<div class="journal" id="journal">en attente…</div>
<script>
/* Le journal est relu tant que la tâche tourne. Un rafraîchissement de page
   n'interrompt rien : la tâche vit dans le serveur, pas dans l'onglet. */
function tick(){
  fetch("/tache").then(r => r.json()).then(t => {
    const j = document.getElementById("journal");
    j.textContent = t.lignes.length ? t.lignes.join("\\n") : "en attente…";
    if(t.erreur){ j.textContent += "\\n\\n" + t.erreur; j.classList.add("err"); }
    j.scrollTop = j.scrollHeight;
    document.querySelectorAll("button[type=submit]").forEach(b => b.disabled = t.en_cours);
    if(t.en_cours) setTimeout(tick, 700);
  }).catch(() => setTimeout(tick, 2000));
}
tick();
</script>"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_etat():
    e = etat_base()
    if e["absente"]:
        return page("État", f"""
          <div class="bloc"><h4>Base absente</h4>
          <p>Le fichier <code>{h(DB_PATH)}</code> n'existe pas encore.</p>
          <p>Construis-le d'abord : <code>python3 src/build_db.py</code></p></div>""", "/")

    couv = "".join(f"<div class='chiffre'><div class='n'>{n}</div>"
                   f"<div class='l'>{h(s.replace('_', ' '))}</div></div>"
                   for s, n in e["couverture"])
    desync = ""
    if e["version_figee"] and e["version_figee"] != e["version_fichiers"]:
        desync = f"""<div class="bandeau incomplet"><span class="ic">⚠</span><div>
          <b>Le référentiel a changé depuis le dernier calcul.</b> Les analyses figées
          portent la version <code>{h(e['version_figee'])}</code>, alors que les fichiers
          du référentiel donnent aujourd'hui <code>{h(e['version_fichiers'])}</code>.
          Les verdicts affichés ne sont plus ceux qu'on obtiendrait maintenant : il faut
          <a href="/publier">refiger</a>. Les deux versions coexisteront en base, et leur
          comparaison est précisément la trace du déplacement des seuils.</div></div>"""

    return page("État de la base", f"""
      <div class="chiffres">
        <div class="chiffre"><div class="n">{e['prelevements']}</div>
          <div class="l">prélèvements en base</div></div>
        <div class="chiffre"><div class="n">{e['mesures']}</div>
          <div class="l">mesures</div></div>
        <div class="chiffre"><div class="n">{e['bulletins']}</div>
          <div class="l">bulletins figés</div></div>
        {couv}
      </div>
      {desync}
      <div class="bloc" style="margin-top:16px"><h4>Traçabilité</h4>
        <p>Version du référentiel calculée sur le contenu des fichiers :
          <code>{h(e['version_fichiers'])}</code><br>
          Version portée par les analyses figées :
          <code>{h(e['version_figee'] or '—')}</code>, calculée le
          <code>{h(e['calcule_le'] or '—')}</code></p>
        <p>L'empreinte porte sur le <b>contenu</b> des fichiers du référentiel, pas sur
          un commit : une modification non commitée doit rester identifiable.</p>
      </div>
      <div class="bloc"><h4>Le circuit</h4>
        <p>1. <a href="/collecte">Collecter</a> des communes &nbsp;→&nbsp;
           2. relire les <a href="/controles">contrôles</a> &nbsp;→&nbsp;
           3. écrire les <a href="/redactions">rédactions</a> &nbsp;→&nbsp;
           4. <a href="/publier">publier</a>.</p>
        <p>Un prélèvement n'est retenu comme complet qu'au-delà de
          {SEUIL_COMPLET} paramètres. Une commune sans bulletin complet, ni pour elle ni
          pour son réseau, sort en « non documentée » : ce n'est ni conforme ni non
          conforme, et cela reste visible sur la carte.</p>
      </div>""", "/")


def page_collecte(message=""):
    return page("Collecte", f"""
      {message}
      <div class="bloc">
        <h4>Importer une liste de communes</h4>
        <p>Un code par ligne — code postal ou code INSEE, mêlés si besoin. Le texte
          après le point-virgule est un motif : il n'est pas utilisé par le programme,
          il sert à ce que la liste reste lisible dans six mois. Une ligne vide ou
          commençant par « # » est ignorée.</p>
        <form method="post" action="/collecte">
          <label for="fichier">Fichier CSV (chemin sur cette machine)</label>
          <input type="text" id="fichier" name="fichier"
                 placeholder="data/communes_a_collecter.csv">
          <label for="liste">…ou liste collée directement</label>
          <textarea id="liste" name="liste" placeholder="17415;Saintes
28068;Challet — non-conformité R417888
82125"></textarea>
          <label><input type="checkbox" name="tous" value="1" style="width:auto">
            &nbsp;tous les bulletins complets de chaque point d'eau, pas seulement le
            dernier (série historique)</label>
          <label><input type="checkbox" name="sans_repli" value="1" style="width:auto">
            &nbsp;ne pas rattacher au réseau voisin quand la commune n'a pas de bulletin
            propre</label>
          <p style="margin:14px 0 0"><button class="btn" type="submit">Lancer la collecte</button></p>
        </form>
      </div>
      <div class="bloc">
        <h4>Ce que la collecte fait</h4>
        <p>Pour chaque commune : résolution du code, énumération des points d'eau
          (une installation de production amont = un point, donc un bulletin), dernier
          bulletin complet de chacun, ingestion, puis calcul et figeage estampillés.
          L'ingestion est idempotente — relancer une collecte interrompue ne duplique
          rien.</p>
        <p>Un code postal peut couvrir plusieurs communes : elles sont toutes traitées.</p>
      </div>
      {journal_html()}""", "/collecte")


def page_controles():
    blocs = []
    for nom, titre, explication in CONTROLES:
        cols, rows, total = controle(nom)
        if cols is None:
            blocs.append(f"<div class='bloc'><h4>{h(titre)}</h4>"
                         f"<p>Vue <code>{h(nom)}</code> absente de la base.</p></div>")
            continue
        if not total:
            blocs.append(
                f"<div class='bloc'><h4>{h(titre)} — <span class='compte' "
                f"style='color:var(--vert)'>0</span></h4><p>{h(explication)}</p></div>")
            continue
        entetes = "".join(f"<th>{h(c)}</th>" for c in cols)
        corps = "".join("<tr>" + "".join(f"<td>{h(v)}</td>" for v in r) + "</tr>"
                        for r in rows)
        reste = (f"<p style='margin-top:10px'>{total - len(rows)} ligne(s) "
                 "supplémentaires non affichées.</p>" if total > len(rows) else "")
        blocs.append(f"""
          <div class="bloc"><h4>{h(titre)} — <span class="compte">{total}</span></h4>
            <p>{h(explication)}</p>
            <div class="tableau-communes" style="max-height:420px;overflow:auto">
              <table><thead><tr>{entetes}</tr></thead><tbody>{corps}</tbody></table>
            </div>{reste}</div>""")
    return page("Contrôles qualité", "".join(blocs), "/controles")


def page_redactions(message=""):
    red = {}
    if os.path.exists(REDACTIONS):
        red = json.load(open(REDACTIONS, encoding="utf-8"))

    connues = []
    if os.path.exists(DB_PATH):
        con = duckdb.connect(DB_PATH, read_only=True)
        try:
            if con.execute("SELECT 1 FROM information_schema.tables "
                           "WHERE table_name = 'couverture_communes'").fetchone():
                connues = con.execute(
                    "SELECT DISTINCT code_insee, commune FROM couverture_communes "
                    "WHERE statut <> 'non_documentee' ORDER BY commune").fetchall()
        finally:
            con.close()

    lig = "".join(
        f"<tr><td>{h(nom)}<span class='grille'>INSEE {h(insee)}</span></td>"
        f"<td>{'<span class=\"etat ok\">rédigée</span>' if red.get(insee, {}).get('analyse') else '<span class=\"etat ind\">factuelle seule</span>'}</td>"
        f"<td>{len(red.get(insee, {}).get('analyse', []))} section(s)</td></tr>"
        for insee, nom in connues)

    return page("Rédactions", f"""
      {message}
      <div class="bloc"><h4>Trois origines de prose, jamais confondues</h4>
        <p><b>auteur</b> — ta main, dans <code>sortie/redactions.json</code>, clé = code
          INSEE. Elle prime toujours, champ par champ.</p>
        <p><b>propose</b> — rédigé par le modèle, dans
          <code>sortie/redactions_proposees.json</code>. C'est là que vit ce que la base
          ne sait pas : le territoire, l'histoire d'une substance, la lecture d'une
          série. Marqué « à relire » sur la fiche tant qu'il n'est pas validé. Valider
          revient à recopier la section dans <code>redactions.json</code>.</p>
        <p><b>derive</b> — composé à la volée depuis <code>analyses_figees</code> et
          <code>verdicts_figes</code> par <code>sortie/rediger.py</code>. Aucune
          connaissance extérieure, aucun nombre qui ne vienne d'une requête. Ce texte
          n'est stocké nulle part : il se recalcule à chaque construction, donc il ne
          peut pas rester vrai pendant que le chiffre d'à côté change.</p>
        <p>Les chiffres ne s'écrivent jamais ici. Recopiés dans un texte, ils cesseraient
          d'être à jour sans que rien ne le signale — c'est exactement la demi-vérité que
          l'outil dénonce.</p>
      </div>
      <div class="bloc"><h4>Où en est la rédaction</h4>
        <div class="tableau-communes">
          <table><thead><tr><th>Commune</th><th>État</th><th>Analyse</th></tr></thead>
          <tbody>{lig or "<tr><td colspan=3>aucune commune en base</td></tr>"}</tbody></table>
        </div>
      </div>
      <div class="bloc"><h4>Éditer</h4>
        <p>Le fichier complet, tel quel. Il est relu comme du JSON avant d'être écrit :
          une erreur de syntaxe est refusée plutôt qu'enregistrée.</p>
        <form method="post" action="/redactions">
          <textarea name="contenu" style="min-height:420px">{h(json.dumps(red, ensure_ascii=False, indent=1))}</textarea>
          <p style="margin:14px 0 0"><button class="btn" type="submit">Enregistrer</button></p>
        </form>
      </div>""", "/redactions")


def page_publier(message=""):
    return page("Publier", f"""
      {message}
      <div class="bloc"><h4>Publier, c'est refiger puis reconstruire</h4>
        <p>Trois opérations, dans cet ordre :</p>
        <p>1. <b>Refiger</b> — recalculer tous les bulletins présents en base contre le
          référentiel actuel. La sortie porte l'empreinte du contenu du référentiel et la
          date du calcul. Si le référentiel a changé, une nouvelle version apparaît ; les
          deux coexistent, et leur comparaison est la trace du déplacement.</p>
        <p>2. <b>Reconstruire la vitrine</b> dans <code>site/public/</code> — pages,
          carte, index de recherche et exports.</p>
        <p>3. <b>Reconstruire la fiche autonome</b> dans <code>sortie/</code> — un
          fichier unique, consultable sans réseau, transmissible tel quel.</p>
        <form method="post" action="/publier">
          <p style="margin:14px 0 0"><button class="btn" type="submit">Refiger et publier</button></p>
        </form>
      </div>
      <div class="bloc"><h4>Ensuite</h4>
        <p>Le contenu de <code>site/public/</code> est un site statique complet : il se
          dépose tel quel sur n'importe quel hébergement de fichiers. Rien n'y tourne,
          rien n'y est à maintenir.</p>
        <p>L'atelier, lui, ne se publie pas.</p>
      </div>
      {journal_html()}""", "/publier")


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
def action_collecte(champs):
    codes = []
    fichier = (champs.get("fichier") or "").strip()
    if fichier:
        chemin = fichier if os.path.isabs(fichier) else os.path.join(RACINE, fichier)
        codes += [c for c, _ in lire_liste_communes(chemin)]

    colle = (champs.get("liste") or "").strip()
    if colle:
        import tempfile
        tmp = os.path.join(tempfile.mkdtemp(), "colle.csv")
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(colle if colle.lower().startswith("code") else "code;motif\n" + colle)
        codes += [c for c, _ in lire_liste_communes(tmp) if c not in codes]

    if not codes:
        raise ValueError("aucun code à collecter : donne un fichier ou colle une liste")

    tous = champs.get("tous") == "1"
    repli = champs.get("sans_repli") != "1"
    import observer

    def travail():
        print(f"{len(codes)} commune(s) à traiter : {', '.join(codes)}\n")
        observer.observer(codes, tous=tous, repli=repli)
        print("\ncollecte terminée. Relis les contrôles avant de publier.")

    return TACHE.lancer(f"collecte de {len(codes)} commune(s)", travail)


def action_publier():
    import build_fiche
    import build_site

    def travail():
        con = duckdb.connect(DB_PATH)
        try:
            version, n = figer.figer(con)
            print(f"figé : {n} bulletin(s), référentiel version {version}\n")
        finally:
            con.close()
        build_site.construire()
        print()
        build_fiche.construire()
        print("\npublication terminée.")

    return TACHE.lancer("publication", travail)


def action_redactions(champs):
    contenu = champs.get("contenu") or ""
    donnees = json.loads(contenu)          # refusé plutôt qu'enregistré si invalide
    if not isinstance(donnees, dict):
        raise ValueError("le fichier doit être un objet JSON, clé = code INSEE")
    with open(REDACTIONS, "w", encoding="utf-8") as fh:
        json.dump(donnees, fh, ensure_ascii=False, indent=1)
    return len(donnees)


# ---------------------------------------------------------------------------
# Serveur
# ---------------------------------------------------------------------------
def bandeau(texte, classe="reseau"):
    return f'<div class="bandeau {classe}"><span class="ic">·</span><div>{texte}</div></div>'


class Atelier(BaseHTTPRequestHandler):
    server_version = "Atelier/1.0"

    def log_message(self, *a):
        pass  # le journal utile est celui des tâches, pas celui des requêtes

    def _envoyer(self, corps, code=200, type_mime="text/html; charset=utf-8"):
        données = corps.encode("utf-8") if isinstance(corps, str) else corps
        try:
            self.send_response(code)
            self.send_header("Content-Type", type_mime)
            self.send_header("Content-Length", str(len(données)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(données)
        except (ConnectionError, BrokenPipeError):
            # Le navigateur a quitté la page avant la fin de la réponse. C'est
            # banal quand on suit une collecte, et ça n'a rien à voir avec la
            # tâche elle-même, qui vit dans son propre fil et continue.
            pass

    def do_GET(self):
        chemin = urllib.parse.urlparse(self.path).path
        try:
            if chemin == "/assets/observatoire.css":
                with open(os.path.join(GABARITS, "observatoire.css"), "rb") as fh:
                    return self._envoyer(fh.read(), type_mime="text/css; charset=utf-8")
            if chemin == "/tache":
                return self._envoyer(json.dumps(TACHE.etat(), ensure_ascii=False),
                                     type_mime="application/json; charset=utf-8")
            if chemin == "/":
                return self._envoyer(page_etat())
            if chemin == "/collecte":
                return self._envoyer(page_collecte())
            if chemin == "/controles":
                return self._envoyer(page_controles())
            if chemin == "/redactions":
                return self._envoyer(page_redactions())
            if chemin == "/publier":
                return self._envoyer(page_publier())
            self._envoyer(page("Page inconnue", "<div class='bloc'>Rien ici.</div>", ""), 404)
        except Exception:
            self._envoyer(page("Erreur", f"<div class='bloc'><h4>Erreur</h4>"
                               f"<pre class='journal'>{h(traceback.format_exc())}</pre></div>",
                               ""), 500)

    def do_POST(self):
        chemin = urllib.parse.urlparse(self.path).path
        taille = int(self.headers.get("Content-Length") or 0)
        brut = self.rfile.read(taille).decode("utf-8")
        champs = {k: v[0] for k, v in urllib.parse.parse_qs(brut, keep_blank_values=True).items()}
        try:
            if chemin == "/collecte":
                if action_collecte(champs):
                    return self._envoyer(page_collecte(
                        bandeau("Collecte lancée. Elle continue même si tu quittes cette "
                                "page : elle vit dans l'atelier, pas dans l'onglet.")))
                return self._envoyer(page_collecte(
                    bandeau("Une tâche est déjà en cours. Attends qu'elle finisse : deux "
                            "collectes simultanées se disputeraient l'écriture de la base "
                            "et doubleraient la charge sur Hub'Eau.", "incomplet")))
            if chemin == "/publier":
                if action_publier():
                    return self._envoyer(page_publier(bandeau("Publication lancée.")))
                return self._envoyer(page_publier(
                    bandeau("Une tâche est déjà en cours.", "incomplet")))
            if chemin == "/redactions":
                n = action_redactions(champs)
                return self._envoyer(page_redactions(
                    bandeau(f"Enregistré : {n} commune(s) rédigée(s). "
                            "Republie pour que les fiches en tiennent compte.")))
            self._envoyer(page("Page inconnue", "<div class='bloc'>Rien ici.</div>", ""), 404)
        except Exception as e:
            page_courante = {"/collecte": page_collecte, "/redactions": page_redactions,
                             "/publier": page_publier}.get(chemin, page_collecte)
            self._envoyer(page_courante(
                bandeau(f"<b>Refusé :</b> {h(e)}", "incomplet")), 400)


def main():
    p = argparse.ArgumentParser(description="Atelier local de l'Observatoire")
    p.add_argument("--port", type=int, default=8760)
    a = p.parse_args()

    # 127.0.0.1 et pas 0.0.0.0 : cet outil écrit en base et déclenche des appels
    # réseau. Il n'a rien à faire au-delà de cette machine.
    serveur = ThreadingHTTPServer(("127.0.0.1", a.port), Atelier)
    print(f"atelier : http://127.0.0.1:{a.port}")
    print("  écoute uniquement en local — ce poste de pilotage ne se publie pas.")
    print("  Ctrl+C pour arrêter.")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\narrêt.")


if __name__ == "__main__":
    main()

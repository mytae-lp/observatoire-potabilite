# -*- coding: utf-8 -*-
"""
Rédaction PROPOSÉE en lot — les deux bouts déterministes, en Claude Code.

    py -X utf8 sortie/rediger_lot.py --etat       # ce qui reste à rédiger
    py -X utf8 sortie/rediger_lot.py --dossiers   # fabrique les dossiers de faits
    py -X utf8 sortie/rediger_lot.py --verifier   # contrôle les réponses, sans écrire
    py -X utf8 sortie/rediger_lot.py --integrer   # contrôle puis écrit le JSON de prose

Ce fichier n'appelle aucune API et ne demande aucune clé. La rédaction se fait
**dans Claude Code**, par des agents de fond : c'est là que le travail est déjà
payé, et un agent par bulletin repart d'un contexte neuf — donc le coût ne croît
pas avec le nombre de bulletins déjà traités, ce qui était le vrai défaut de la
rédaction au fil d'une conversation.

Le partage des rôles
--------------------
Ce script tient ce qui doit être reproductible, et rien d'autre :

  1. **choisir** les bulletins qui n'ont pas encore de prose ;
  2. **fabriquer le dossier de faits** de chacun, entièrement par requête ;
  3. **contrôler** ce qui revient, avant que ça touche un fichier de prose ;
  4. **intégrer** dans `redactions_proposees.json`.

Entre 2 et 3, un agent Claude Code lit `sortie/CONSIGNE_REDACTION.md` et le
dossier, et écrit un JSON. C'est la seule étape qui demande un modèle, et c'est
la seule qui n'est pas ici.

Le contrôle de l'étape 3 est la raison d'être du fichier
--------------------------------------------------------
Un texte proposé par un modèle entre dans un projet dont toute la valeur est la
vérifiabilité. Il est donc contrôlé **avant** d'être écrit, et pas seulement au
moment de publier :

  · les garde-fous §2.1 et §2.11 sont ceux de `tests/test_sorties.py`, importés
    et non recopiés — deux copies d'une même règle divergent à la première
    retouche, et c'est le genre d'écart qui ne se voit pas ;
  · §2.4 : aucune affirmation d'absence ;
  · §2.2 : aucun qualificatif sanitaire ;
  · **tout nombre décimal absent du dossier bloque.** C'est le contrôle le plus
    utile : il attrape la valeur inventée, la conversion d'unité faite de tête et
    le seuil recopié de mémoire — les trois façons dont ce projet s'est déjà
    trompé, par la main humaine comme par la machine.

Rien n'est publié pour autant : une entrée intégrée apparaît dans l'onglet
Valider de l'atelier, marquée « proposition, à relire ».
"""
import argparse
import glob
import json
import os
import re
import sys

import duckdb

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, os.path.join(RACINE, "tests"))
sys.path.insert(0, ICI)

from common import DB_PATH          # noqa: E402
import rediger                      # noqa: E402
import build_fiche                  # noqa: E402
import test_sorties                 # noqa: E402  — les garde-fous, pas recopiés

PROPOSEES = os.path.join(ICI, "redactions_proposees.json")
CONSIGNE = os.path.join(ICI, "CONSIGNE_REDACTION.md")
DOSSIERS = os.path.join(RACINE, "data", "dossiers")
REPONSES = os.path.join(DOSSIERS, "reponses")

CHAMPS = ("sous_titre", "delta", "lecture_administrative", "analyse")

# §2.4 — une absence ne se constate pas, elle se mesure. Ces tournures disent
# « il n'y a rien » là où la donnée dit « l'instrument n'a rien vu ».
ABSENCES = ["absente de l'eau", "sont absents", "est absent", "aucune trace",
            "pas la moindre trace", "à zéro", "égal à zéro", "eau pure",
            "exempte de", "exempt de", "indemne de", "vierge de"]

# §2.2 — le texte décrit des écarts à des seuils datés, pas un état sanitaire.
SANITAIRES = ["dangereux", "dangereuse", "toxique", "nocif", "nocive",
              "inquiétant", "inquiétante", "alarmant", "alarmante", "malsain",
              "impropre", "à risque", "risque sanitaire", "polluée", "pollué",
              "contaminée", "contaminé", "eau saine", "bonne pour la santé"]


# ---------------------------------------------------------------------------
# Le dossier de faits
# ---------------------------------------------------------------------------
def _n(x, dec=6):
    return rediger.nb(x, dec) if x is not None else "—"


def _table(entetes, lignes):
    if not lignes:
        return "  (aucune)\n"
    out = ["  " + " | ".join(entetes)]
    out += ["  " + " | ".join(str(c) for c in l) for l in lignes]
    return "\n".join(out) + "\n"


def dossier(con, a, version):
    """
    Le brief factuel d'un bulletin.

    Règle de construction : **tout ce qui est ici vient d'une requête.** Le
    rédacteur n'a le droit de citer aucun chiffre absent de ce texte, et
    l'intégration le vérifie. Donc ce qui manque ici ne sera pas écrit — et ce
    qui est faux ici le sera. C'est la seule surface à vérifier.
    """
    lignes = rediger._lignes(con, a["code_prelevement"], version)
    d = ["# Bulletin\n"]
    # Le nombre de communes desservies fixe la PORTÉE du texte : un point d'eau
    # du Tarn en dessert jusqu'à 46, et le rédacteur ne peut pas le deviner.
    # Trois rédacteurs du lot ont buté dessus le 9 août 2026, l'un demandant
    # même s'il avait le droit d'écrire « Tarn » à partir du seul code « 81 ».
    n_com = con.execute("""
        SELECT COUNT(*) FROM couverture_communes
        WHERE code_prelevement = ? AND version_referentiel = ?
    """, [a["code_prelevement"], version]).fetchone()[0] or 1
    d.append(f"Commune : {a['commune']} ({a['code_insee']}), département {a['dept']} "
             "— le nom du département correspondant au code est une nomenclature "
             "publique, tu peux l'écrire")
    d.append(f"Portée de ce texte : ce bulletin est celui qu'affichent "
             f"{n_com} communes — écris pour toutes, pas pour la seule ci-dessus"
             if n_com > 1 else
             "Portée de ce texte : ce bulletin n'est affiché que par cette commune")
    d.append(f"Prélèvement : {a['code_prelevement']} du {rediger.date_fr(a['date_prelevement'])}")
    if a.get("nom_installation_amont"):
        d.append(f"Point d'eau (installation amont) : {a['nom_installation_amont']}")
    if a.get("nom_uge"):
        d.append(f"Gestionnaire déclaré par la source : {a['nom_uge']}")
    if a.get("noms_reseaux"):
        d.append(f"Réseaux desservis : {a['noms_reseaux']}")
    d.append(f"Conclusion du contrôle sanitaire : {a.get('conclusion_conformite') or '—'}")

    # La prose est indexée par POINT D'EAU : le rédacteur doit savoir qu'il
    # n'écrit pas pour une commune. Une allusion trop locale rendrait le texte
    # faux pour les sept autres.
    autres = con.execute("""
        SELECT commune FROM couverture_communes
        WHERE code_prelevement = ? AND version_referentiel = ? AND commune <> ?
        ORDER BY commune
    """, [a["code_prelevement"], version, a["commune"]]).fetchall()
    if autres:
        d.append(f"\nCe même point d'eau alimente aussi : "
                 f"{rediger.liste_fr([r[0] for r in autres], maxi=12)}. Le texte sera "
                 "affiché sur toutes ces communes — ne l'écris pas pour une seule.")

    d.append("\n# Effort de recherche\n")
    d.append(f"{a['nb_parametres']} paramètres recherchés (classe « {a['classe_effort']} »)")
    d.append(f"{a['nb_mesures_notees']} notés sur {a['nb_mesures_lues']} mesurés "
             f"= {_n(a['pct_couverture'], 1)} % de couverture")
    d.append(f"dont {a['nb_notees_referentiel']} par le référentiel daté du projet "
             f"et {a['nb_notees_declare']} par la seule limite déclarée par la source "
             "(celles-là ne peuvent produire ni bascule ni verdict 2016)")
    if a.get("nb_synthese_recherchees"):
        d.append(f"{a['nb_synthese_recherchees']} substances de synthèse recherchées")

    d.append("\n# Verdicts\n")
    d.append(f"Dépassements à la date du prélèvement : {a['nb_depasse_applicable']}")
    d.append(f"Bascules 2016→2026 : {a['nb_bascules']} "
             f"(dont datables au jour près : {a.get('nb_bascules_datees') or 0})")
    d.append(f"Contrefactuels — dépasserait la grille 2016 : {a['nb_depasse_2016']} ; "
             f"la grille 2026 : {a['nb_depasse_2026']} ; "
             f"le repère le plus strict identifié : {a['nb_depasse_strict']}")
    # Le recouvrement se DIT, il ne se laisse pas deviner.
    #
    # Défaut réel trouvé le 9 août 2026, signalé par deux rédacteurs du lot du
    # Tarn : le compteur ci-dessous porte TOUS les indéterminés, tandis que la
    # table « Indéterminés au repère le plus strict » écarte les paramètres
    # aveugles pour ne pas les répéter avec la table suivante. Or le chantier C4
    # a établi que les aveugles sont TOUS parmi les indéterminés. Quand le seul
    # indéterminé d'un bulletin est aussi aveugle, le dossier annonçait donc
    # « 1 » au-dessus d'une table vide — et un rédacteur consciencieux s'abstient
    # d'en parler, ce qui fait perdre le seul angle distinctif du bulletin.
    # Un compteur en désaccord avec son détail est exactement ce que l'atelier
    # faisait au chantier C8 : il ne ment pas, il induit en erreur.
    nb_ind = a["nb_indetermines"] or 0
    nb_av = a.get("nb_aveugles") or 0
    ind_aveugles = sum(1 for r in lignes if (r[10] or r[11]) and r[15]
                       and not r[7] and not r[8])
    ligne_ind = f"Indéterminés (LQ au-dessus du repère strict) : {nb_ind}"
    if ind_aveugles:
        ligne_ind += (f" — dont {ind_aveugles} qui sont AUSSI hors de portée du "
                      "laboratoire, donc listés plus bas dans « Paramètres hors "
                      "de portée », et absents de la table des indéterminés pour "
                      "ne pas être comptés deux fois")
    d.append(ligne_ind)
    d.append(f"Paramètres aveugles (LQ au-dessus du seuil applicable) : {nb_av}"
             + (f", soit {_n(a.get('aveugles_pour_mille'), 1)} ‰ des notés"
                if a.get("aveugles_pour_mille") else ""))
    if a.get("nb_synthese_quantifiees"):
        d.append(f"Substances de synthèse quantifiées ensemble : {a['nb_synthese_quantifiees']}"
                 + (f", charge cumulée {_n(a.get('charge_synthese_ug_l'), 3)} µg/L"
                    if a.get("charge_synthese_ug_l") else ""))
    if a.get("indice_danger") and a.get("indice_danger_n"):
        d.append(f"Indice de danger : {_n(a['indice_danger'], 2)} sur "
                 f"{a['indice_danger_n']} substances — à ne jamais nommer « risque » "
                 "ni présenter comme un verdict de potabilité, et jamais cité sans "
                 "ce nombre de substances")

    fmt = lambda r: [r[0], f"{_n(r[1])} {r[3] or ''}".strip(),  # noqa: E731
                     f"{_n(r[4])} ({r[6] or '—'})", _n(r[5]), _n(r[14])]
    entetes = ["paramètre", "valeur", "seuil applicable (grille)", "seuil 2016", "strict"]

    def bloc(titre, sel):
        return f"\n## {titre}\n" + _table(entetes, [fmt(r) for r in lignes if sel(r)][:15])

    d.append(bloc("Dépassements du seuil applicable", lambda r: r[7]))
    d.append(bloc("Bascules — dépassait 2016, ne dépasse plus",
                  lambda r: r[8] and not r[7]))
    d.append(bloc("Indéterminés au repère le plus strict",
                  lambda r: (r[10] or r[11]) and not r[7] and not r[8] and not r[15]))

    aveugles = [r for r in lignes if r[15]][:12]
    d.append("\n## Paramètres hors de portée du laboratoire\n"
             + _table(["paramètre", "LQ", "seuil applicable", "rapport LQ/seuil"],
                      [[r[0], f"{_n(r[2])} {r[3] or ''}".strip(), _n(r[4]),
                        (f"{_n(r[16], 1)}×" if r[16] else "—")] for r in aveugles]))

    # Même règle que rediger.py : une somme ne s'énumère pas à côté de ses
    # composants. Sans ce filtre, le dossier de faits listait deux lignes là où
    # le compteur en annonçait une, et quatre rédacteurs du lot du Tarn s'en
    # sont aperçus avant nous.
    quant = [r for r in lignes
             if r[13] and r[12] in rediger.FAMILLES_SYNTHESE
             and not r[7] and not r[17]][:15]
    d.append("\n## Substances de synthèse quantifiées, sans dépassement\n"
             + _table(["paramètre", "valeur", "famille", "seuil applicable"],
                      [[r[0], f"{_n(r[1])} {r[3] or ''}".strip(), r[12], _n(r[4])]
                       for r in quant]))

    # La série dans le temps : c'est elle qui a permis de voir, à Challet, que
    # l'effort avait baissé de 660 à 234 paramètres pendant que les dépassements
    # augmentaient. Aucun bulletin isolé ne peut le dire.
    serie = con.execute("""
        SELECT date_prelevement, nb_parametres, nb_mesures_notees,
               nb_depasse_applicable, nb_bascules, nom_installation_amont
        FROM analyses_figees
        WHERE code_insee = ? AND version_referentiel = ? AND code_prelevement <> ?
        ORDER BY date_prelevement DESC LIMIT 8
    """, [a["code_insee"], version, a["code_prelevement"]]).fetchall()
    d.append("\n## Autres bulletins de la même commune (corpus du projet)\n"
             + _table(["date", "cherchés", "notés", "dépassements", "bascules", "point d'eau"],
                      [[str(r[0]), r[1], r[2], r[3], r[4], r[5] or "—"] for r in serie]))

    der = rediger.rediger(con, a, version)
    d.append("\n# Texte DÉJÀ dérivé de la base — ne le répète pas\n")
    for s in der["analyse"]:
        d.append(f"### {s['t']}\n{s['x']}\n")
    d.append(f"### Lecture citoyenne\n{der['lecture_citoyenne']}\n")
    d.append(f"### Verdict\n{der['verdict']}\n")
    return "\n".join(d)


# ---------------------------------------------------------------------------
# Sélection — l'idempotence
# ---------------------------------------------------------------------------
def a_rediger(con, version, tous=False):
    """
    Les bulletins complets qui n'ont encore aucune prose écrite.

    Le journal de reprise n'est pas un fichier à part : ce sont les deux
    fichiers de prose eux-mêmes. Un point d'eau déjà servi par une clé
    `INSEE@date`, `INSEE` ou `PREL:` est sauté — de la main de Yannick comme
    d'un lot précédent. Relancer un lot interrompu ne coûte rien et n'écrase
    rien, exactement comme une collecte Hub'Eau.

    **Par défaut, seuls les bulletins qu'une fiche de commune AFFICHE.**
    Restriction ajoutée le 9 août 2026, quand le Tarn a fait passer le corpus de
    45 à 1 595 bulletins : 1 550 étaient sans prose, mais **143 seulement portent
    une fiche**. Les autres sont les bulletins antérieurs des mêmes points d'eau
    — ils nourrissent les chantiers C2 et C3, et personne ne les lit. En rédiger
    1 400 que rien n'affiche coûterait 1 400 agents pour zéro lecteur, et
    encombrerait la page de validation au point de la rendre inutilisable.

    Le lien est `couverture_communes.code_prelevement` : c'est LA table qui dit
    quel bulletin chaque commune montre (§8bis). Un même point d'eau y dessert
    souvent des dizaines de communes — Montdragon en dessert 46, Lavaur 43 —
    d'où la clé `PREL:` de la prose, qui écrit le texte une fois pour toutes.

    `tous=True` rend l'ancien comportement, pour le jour où l'on voudra une
    prose par bulletin historique.
    """
    auteur, propose = build_fiche.charger_prose()
    filtre = "" if tous else """
          AND code_prelevement IN (
              SELECT code_prelevement FROM couverture_communes
              WHERE version_referentiel = ? AND code_prelevement IS NOT NULL)"""
    params = [version] if tous else [version, version]
    rows = con.execute(f"""
        SELECT * FROM analyses_figees
        WHERE version_referentiel = ? AND est_complet {filtre}
        ORDER BY commune, date_prelevement DESC
    """, params).fetchall()
    cols = [d[0] for d in con.description]
    manquants, vus = [], set()
    for r in rows:
        a = dict(zip(cols, r))
        if a["code_prelevement"] in vus:
            continue
        vus.add(a["code_prelevement"])
        date_iso = str(a["date_prelevement"])[:10]
        for source in (auteur, propose):
            if build_fiche.pour_bulletin(source, a["code_insee"], date_iso,
                                         a["code_prelevement"]):
                break
        else:
            manquants.append(a)
    return manquants


def fabriquer(con, version, maxi, tous=False):
    cibles = a_rediger(con, version, tous=tous)
    if maxi:
        cibles = cibles[:maxi]
    if not cibles:
        print("  rien à rédiger : tous les bulletins portent déjà une prose.")
        return
    os.makedirs(REPONSES, exist_ok=True)
    for a in cibles:
        chemin = os.path.join(DOSSIERS, f"PREL-{a['code_prelevement']}.md")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(dossier(con, a, version))
    print(f"  {len(cibles)} dossier(s) écrit(s) dans data/dossiers/.\n")
    print("  À coller dans Claude Code :\n")
    print("  ┌" + "─" * 70)
    print("  │ Rédige les bulletins de data/dossiers/. Lis d'abord")
    print("  │ sortie/CONSIGNE_REDACTION.md — c'est la consigne complète, et elle")
    print("  │ est contrôlée à l'intégration. Un agent de fond par dossier, en")
    print("  │ Opus, par paquets de 5. Chaque agent lit UN dossier et écrit UN")
    print("  │ fichier data/dossiers/reponses/PREL-<code>.json, rien d'autre.")
    print("  └" + "─" * 70)
    print("\n  Puis : py -X utf8 sortie/rediger_lot.py --integrer")


# ---------------------------------------------------------------------------
# Le contrôle
# ---------------------------------------------------------------------------
def _texte_de(v):
    """
    Tout le texte d'une proposition, mis bout à bout.

    Chaque bout est **terminé par un point s'il ne l'est pas déjà**. Sans cela,
    le découpage en phrases du contrôle recolle la fin d'un champ au début du
    suivant — et un nom propre du `sous_titre` suffisait alors à faire passer
    pour « nommée » une comparaison anonyme du `delta`. Défaut trouvé en
    éprouvant le contrôle sur une réponse fautive fabriquée exprès.
    """
    bouts = [v.get(c, "") for c in CHAMPS if c != "analyse"]
    bouts += [s.get("t", "") + ". " + s.get("x", "")
              for s in v.get("analyse") or [] if isinstance(s, dict)]
    propres = []
    for b in bouts:
        if isinstance(b, str) and b.strip():
            b = b.strip()
            propres.append(b if b[-1] in ".!?" else b + ".")
    return "\n".join(propres)


def _nombres(texte):
    """Les nombres d'un texte, normalisés — « 0,047 » et « 0.047 » sont un seul."""
    out = set()
    for brut in re.findall(r"\d+(?:[.,]\d+)?", texte):
        n = brut.replace(",", ".")
        out.add(n.rstrip("0").rstrip(".") if "." in n else n)
    return out


def controler(v, texte_dossier):
    """
    (bloquants, signalements). Un bloquant refuse l'intégration.

    L'asymétrie est celle du §2.13, transposée du verdict au texte : un faux
    positif coûte plus cher au projet qu'un faux négatif. Mieux vaut refuser
    une phrase juste que laisser passer une prescription.
    """
    bloquants, signalements = [], []

    for champ in CHAMPS:
        if champ not in v or not v[champ]:
            bloquants.append(f"champ manquant ou vide : {champ}")
    a = v.get("analyse")
    if a is not None:
        if not isinstance(a, list) or not (1 <= len(a) <= 6):
            bloquants.append("`analyse` doit être une liste de 1 à 6 sections")
        else:
            for i, s in enumerate(a, 1):
                if not isinstance(s, dict) or not s.get("t") or not s.get("x"):
                    bloquants.append(f"section {i} : `t` et `x` sont obligatoires")
    for cle in v:
        if cle not in CHAMPS and not cle.startswith("_"):
            signalements.append(f"champ inattendu, ignoré à la publication : {cle}")

    texte = _texte_de(v)
    bas = texte.lower()

    # §2.2 et §2.11 — la même fonction que le contrôle de publication.
    for mot, phrase in test_sorties.prescrit(texte):
        bloquants.append(f"§2.2 prescription « {mot} » : {phrase[:110]}")
    for mot, phrase in test_sorties.comparaison_anonyme(texte):
        bloquants.append(f"§2.11 comparaison anonyme « {mot} » : {phrase[:110]}")

    for mot in ABSENCES:
        if mot in bas:
            bloquants.append(f"§2.4 affirmation d'absence « {mot} » — un non-quantifié "
                             "est sous la limite de quantification, pas absent")
    for mot in SANITAIRES:
        if re.search(rf"\b{re.escape(mot)}\b", bas):
            bloquants.append(f"§2.2 qualificatif sanitaire « {mot} »")
    if re.search(r"\brisque\b", bas) and re.search(r"indice|danger|cumul", bas):
        bloquants.append("§7.1 l'indice de danger ne se nomme jamais « risque »")
    if "plus strict au monde" in bas:
        bloquants.append("§2.14 « le plus strict au monde » — écrire « identifié »")

    # §2.7 transposé au texte : un nombre qui n'est pas dans le dossier n'a pas
    # de source. Les décimaux bloquent — ce sont les mesures et les seuils, donc
    # les valeurs qu'une erreur rend fausses. Les entiers (années, comptes)
    # signalent seulement : trop de faux positifs pour refuser dessus.
    du_dossier = _nombres(texte_dossier)
    for n in sorted(_nombres(texte) - du_dossier):
        if "." in n:
            bloquants.append(f"§2.7 nombre absent du dossier : {n.replace('.', ',')}")
        elif not (1900 <= int(n) <= 2100):
            signalements.append(f"nombre entier absent du dossier : {n}")

    return bloquants, signalements


def lire_reponses():
    for chemin in sorted(glob.glob(os.path.join(REPONSES, "PREL-*.json"))):
        code = os.path.basename(chemin)[5:-5]
        try:
            yield code, chemin, json.load(open(chemin, encoding="utf-8")), None
        except json.JSONDecodeError as e:
            yield code, chemin, None, f"JSON illisible : {e}"


def verifier(con, version, ecrire_prose):
    if not os.path.isdir(REPONSES):
        sys.exit("  ! aucune réponse. Lance --dossiers, puis fais rédiger.")

    rows = con.execute("SELECT * FROM analyses_figees WHERE version_referentiel = ?",
                       [version]).fetchall()
    cols = [d[0] for d in con.description]
    par_code = {r[cols.index("code_prelevement")]: dict(zip(cols, r)) for r in rows}

    bons, refuses, n_sign = {}, 0, 0
    for code, chemin, v, err in lire_reponses():
        a = par_code.get(code)
        titre = (f"{a['commune']} ({a['dept']}) — {a['date_prelevement']}"
                 if a else f"code inconnu : {code}")
        if err or a is None:
            motif = err or "ce prélèvement n'est pas dans la version publiée"
            print(f"  ✗ {titre}\n      {motif}")
            refuses += 1
            continue
        bloquants, signalements = controler(v, dossier(con, a, version))
        n_sign += len(signalements)
        if bloquants:
            refuses += 1
            print(f"  ✗ {titre}")
            for b in bloquants:
                print(f"      {b}")
            print(f"      → à refaire : {os.path.relpath(chemin, RACINE)}")
        else:
            print(f"  ✓ {titre}")
            v = {k: v[k] for k in CHAMPS}
            v["_commune"] = titre
            v["_lot"] = "proposé en Claude Code, non relu"
            bons[f"PREL:{code}"] = v
        for s in signalements:
            print(f"      · {s}")

    print(f"\n  {len(bons)} acceptée(s), {refuses} refusée(s), {n_sign} signalement(s).")
    if not ecrire_prose:
        print("  (--verifier : rien n'a été écrit)")
        return

    fichier = (json.load(open(PROPOSEES, encoding="utf-8"))
               if os.path.exists(PROPOSEES) else {})
    neuves = 0
    for cle, valeur in bons.items():
        # Une clé déjà présente a été relue ou commentée : on ne l'écrase pas.
        if cle in fichier:
            continue
        fichier[cle] = valeur
        neuves += 1
    with open(PROPOSEES, "w", encoding="utf-8") as f:
        json.dump(fichier, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for cle in bons:
        chemin = os.path.join(REPONSES, f"PREL-{cle[5:]}.json")
        if os.path.exists(chemin):
            os.remove(chemin)
        d = os.path.join(DOSSIERS, f"PREL-{cle[5:]}.md")
        if os.path.exists(d):
            os.remove(d)
    print(f"  {neuves} entrée(s) écrite(s) dans redactions_proposees.json.")
    print("  Rien n'est publié : relis-les dans l'onglet Valider de l'atelier.")


def etat(con, version, tous=False):
    manquants = a_rediger(con, version, tous=tous)
    total = con.execute("SELECT COUNT(*) FROM analyses_figees "
                        "WHERE version_referentiel = ? AND est_complet",
                        [version]).fetchone()[0]
    attente = len(glob.glob(os.path.join(REPONSES, "PREL-*.json")))
    print(f"  version publiée    : {version}")
    print(f"  bulletins complets : {total}")
    print(f"  sans aucune prose  : {len(manquants)}")
    print(f"  réponses à intégrer: {attente}")
    for a in manquants[:20]:
        print(f"    {a['commune']:28} {a['dept']:4} {a['date_prelevement']}  "
              f"{a['nb_parametres']:>4} param.  "
              f"{a['nb_depasse_applicable']} dép.  {a['nb_bascules']} basc.")
    if len(manquants) > 20:
        print(f"    … et {len(manquants) - 20} autres")


# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description="Rédaction proposée en lot — dossiers et contrôle, "
                    "la rédaction se fait en Claude Code.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--etat", action="store_true", help="ce qui reste à rédiger")
    g.add_argument("--dossiers", action="store_true", help="fabrique les dossiers de faits")
    g.add_argument("--verifier", action="store_true", help="contrôle les réponses, sans écrire")
    g.add_argument("--integrer", action="store_true", help="contrôle puis écrit la prose")
    p.add_argument("--maxi", type=int, help="borne le nombre de dossiers fabriqués")
    p.add_argument("--tous-bulletins", action="store_true",
                   help="inclure les bulletins qu'aucune fiche de commune n'affiche "
                        "(les antérieurs d'un même point d'eau — matériau de C2/C3, "
                        "1 452 sur 1 595 au 9 août 2026)")
    args = p.parse_args()

    con = duckdb.connect(DB_PATH, read_only=True)
    version, _ = build_fiche.version_a_publier(con)
    if not version:
        sys.exit("  ! aucune version figée. Lance src/figer.py d'abord.")

    if args.etat:
        etat(con, version, tous=args.tous_bulletins)
    elif args.dossiers:
        fabriquer(con, version, args.maxi, tous=args.tous_bulletins)
    else:
        verifier(con, version, ecrire_prose=args.integrer)
    con.close()


if __name__ == "__main__":
    main()

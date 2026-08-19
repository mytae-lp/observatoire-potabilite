# -*- coding: utf-8 -*-
"""
Les chiffres du dossier « conformité sur panel réduit » — lecture unique.

Le dossier de substance tire ses chiffres d'une requête à la base, à chaque
construction. **Celui-ci ne le peut pas, et il faut savoir pourquoi** : le
corpus ne contient que les bulletins complets (`SEUIL_COMPLET`), et l'objet de
cette étude est précisément ce que les contrôles de routine — jamais ingérés —
ont cessé de porter. Le suivi vient donc de Hub'Eau, pas de DuckDB.

D'où la décision de Yannick, le 17 août 2026 : **la synthèse est figée et
datée, et c'est lui qui la réactualise.** Un balayage rejoué à chaque
construction du site relancerait des centaines d'appels Hub'Eau pour des
chiffres qui bougeraient sous le texte qui les commente.

Ce module est donc le **lecteur unique** de cette synthèse. Il ne calcule rien
que le CSV ne porte pas, et la page comme l'accueil l'appellent tous les deux —
c'est ce qui empêche l'accueil d'annoncer 18 communes pendant que le dossier
en montre 37.

    py -X utf8 sortie/dossier_panel_reduit.py             # les faits, à l'œil
    py -X utf8 sortie/dossier_panel_reduit.py --verifier  # les contrôles

DEUX PIÈGES, ET ILS ONT ÉTÉ TROUVÉS EN ÉCRIVANT CE FICHIER
-----------------------------------------------------------
1. **« N mois » est relatif à la date de l'étude, jamais à aujourd'hui.**
   `etude_panel_reduit.py` écrit l'ancienneté en mois contre le jour où il
   tourne. Reconvertir ces mois en années avec la date du jour décalerait
   toute la chronologie d'un an de plus chaque année, en silence. La référence
   est lue dans le nom du fichier de synthèse, et nulle part ailleurs.

2. **Le nombre de départements balayés est une propriété de l'étude, pas du
   dépôt.** Au 12 août 2026 le balayage portait sur 11 départements publiés ;
   au 17 août `referentiel/departements_publies.csv` en compte 17. Lire ce
   fichier à la construction ferait dire au dossier qu'il a balayé 17
   départements — ce qui est faux, et faux dans le sens qui grossit le
   constat. Le périmètre est donc figé avec la synthèse, dans son `.meta.json`.

CE QUE CE MODULE NE REND PAS
----------------------------
Les chiffres que la synthèse ne porte pas restent dans l'argument versionné,
`ANALYSE_<date>.md` : les 39 candidates avant instruction, les 61 analyses
complètes dont 55 non conformes, et la série de nitrates de Nottonville. Ils
viennent du corpus figé et des dossiers commune par commune, pas d'ici.

Les libellés sont rendus **tels que la source les écrit** — « ESA
metolachlore », sans accent, est ce que Hub'Eau renvoie. Ce module ne
réunit pas non plus « OXA metazachlore » et « ESA metazachlore » en une
ligne : ce sont deux paramètres distincts, et les fondre ferait disparaître
un abandon du décompte.
"""

import argparse
import collections
import csv
import datetime
import glob
import json
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
ETUDE = os.path.join(RACINE, "data", "etudes", "conformite_sur_panel_reduit")

# « Total des pesticides analysés (119 mois) »
RE_ABANDON = re.compile(r"^(.*?)\s*\((\d+)\s*mois\)$")

# Le seuil d'abandon de l'étude, repris ici pour l'affichage seulement : le CSV
# porte déjà le tri fait, `nb_abandonnes_24m`.
MOIS_ABANDON = 24


class SyntheseIntrouvable(Exception):
    pass


def _synthese_la_plus_recente():
    """
    Le dernier `synthese_<date>.csv` du dossier d'étude, et sa date.

    Choisir par nom de fichier et non par date de modification : un `git
    checkout` réécrit les dates de modification de tout ce qu'il touche, et
    l'ordre s'inverserait sans que rien ne le dise.
    """
    chemins = sorted(glob.glob(os.path.join(ETUDE, "synthese_*.csv")))
    if not chemins:
        raise SyntheseIntrouvable(
            "aucun synthese_<date>.csv dans %s — l'étude n'a jamais tourné, "
            "ou le dossier a été déplacé." % ETUDE)
    chemin = chemins[-1]
    m = re.search(r"synthese_(\d{4}-\d{2}-\d{2})\.csv$", os.path.basename(chemin))
    if not m:
        raise SyntheseIntrouvable(
            "%s ne porte pas de date dans son nom. C'est cette date qui sert "
            "de référence aux « N mois » : sans elle, la chronologie est "
            "indatable." % chemin)
    return chemin, datetime.date.fromisoformat(m.group(1))


def _perimetre(chemin_csv, date_etude):
    """
    Le périmètre du balayage, figé avec la synthèse.

    Absent, on ne le devine pas : le dossier affichera « périmètre non
    consigné » plutôt qu'un nombre pris sur le dépôt du jour, qui serait faux
    dès la première collecte suivante.
    """
    meta = os.path.splitext(chemin_csv)[0] + ".meta.json"
    if not os.path.exists(meta):
        return {}
    with open(meta, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("date_etude") and d["date_etude"] != date_etude.isoformat():
        raise SyntheseIntrouvable(
            "%s dit porter sur le %s alors que la synthèse est datée du %s. "
            "Deux dates pour une même étude : ne rien publier avant de savoir "
            "laquelle est la bonne." % (meta, d["date_etude"], date_etude))
    return d


def _noms_departements():
    """
    Code -> nom, depuis `referentiel/departements_publies.csv`.

    Source unique, la même que la vitrine et les autres dossiers de faits. Un
    code sans nom est rendu tel quel plutôt que deviné : « (28) » vaut mieux
    qu'un nom approché.
    """
    chemin = os.path.join(RACINE, "referentiel", "departements_publies.csv")
    noms = {}
    try:
        with open(chemin, encoding="utf-8-sig") as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne or ligne.startswith("#") or ligne.startswith("code;"):
                    continue
                bouts = ligne.split(";")
                if len(bouts) >= 2 and bouts[0] and bouts[1]:
                    noms[bouts[0].strip()] = bouts[1].strip()
    except OSError:
        pass
    return noms


# Le contraste : deux paramètres d'une même commune, l'un toujours suivi,
# l'autre non. Les valeurs viennent du dossier commune par commune que
# `etude_panel_reduit.py` a écrit — donc d'une requête, comme tout le reste.
RE_LIGNE = re.compile(r"^\|\s*(.+?)\s*\|\s*([\d.,]+)\s*(\S*)\s*\|\s*([\d.,]+)\s*"
                      r"\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*\*\*(\d+) mois\*\*\s*\|$")


def contraste(insee, parametres):
    """
    Les lignes de `parametres` dans le dossier auto de la commune `insee`.

    Rend un dict {libellé: {valeur, unite, limite, mesures_depuis,
    derniere_mesure, mois}}. Un paramètre demandé et introuvable lève : le
    contraste tient sur DEUX lignes précises, et en afficher une seule
    retournerait le sens de la section.
    """
    trouves = {}
    motif = os.path.join(ETUDE, "auto_*-%s_*.md" % insee)
    chemins = sorted(glob.glob(motif))
    if not chemins:
        raise SyntheseIntrouvable(
            "aucun dossier auto pour la commune %s (%s)" % (insee, motif))
    with open(chemins[-1], encoding="utf-8") as f:
        for ligne in f:
            m = RE_LIGNE.match(ligne.strip())
            if not m or m.group(1) not in parametres:
                continue
            trouves[m.group(1)] = {
                "valeur": m.group(2).replace(".", ","), "unite": m.group(3),
                "limite": m.group(4).replace(".", ","),
                "mesures_depuis": int(m.group(5)),
                "derniere_mesure": m.group(6), "mois": int(m.group(7)),
            }
    manquants = [p for p in parametres if p not in trouves]
    if manquants:
        raise SyntheseIntrouvable(
            "%s : paramètre(s) introuvable(s) dans %s — %s"
            % (insee, os.path.basename(chemins[-1]), ", ".join(manquants)))
    return trouves


def _annee_de(mois, date_etude):
    """
    L'année de la dernière mesure d'un paramètre abandonné depuis `mois` mois.

    Même arithmétique que `etude_panel_reduit.mois_entre` — années et mois,
    jamais les jours : c'est ainsi que les mois ont été comptés, et compter
    autrement au retour rendrait les deux bouts incohérents aux bornes.
    """
    t = (date_etude.year * 12 + date_etude.month - 1) - mois
    return t // 12


def faits():
    """
    Tout ce que la synthèse figée porte, et rien d'autre.

    Rendu : un dict. Les nombres sont des `int`, les listes sont déjà triées
    dans l'ordre d'affichage du dossier.
    """
    chemin, date_etude = _synthese_la_plus_recente()
    meta = _perimetre(chemin, date_etude)

    with open(chemin, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    if not lignes:
        raise SyntheseIntrouvable("%s est vide." % chemin)

    # La géographie se compte sur les 37 INSTRUITES, pas sur les 18 retenues.
    # Sans le dénominateur par département, le tableau se lirait comme une
    # carte de France — alors qu'il dit d'abord où le corpus a cherché
    # (§2.11 : aucune comparaison de territoires sans l'effort de chaque terme).
    noms = _noms_departements()
    par_dept = collections.OrderedDict()
    for l in lignes:
        d = par_dept.setdefault(l["dept"], {"code": l["dept"],
                                            "nom": noms.get(l["dept"], ""),
                                            "instruites": 0, "avec_abandon": 0})
        d["instruites"] += 1
        if int(l["nb_abandonnes_24m"]) > 0:
            d["avec_abandon"] += 1

    communes, par_param, annees = [], collections.defaultdict(list), collections.Counter()
    for l in lignes:
        n_ab = int(l["nb_abandonnes_24m"])
        if n_ab <= 0:
            continue                       # instruite, mais rien d'abandonné

        abandons = []
        for bout in l["abandonnes"].split("|"):
            bout = bout.strip()
            if not bout:
                continue
            m = RE_ABANDON.match(bout)
            if not m:
                # Un libellé qui contiendrait « (… mois) » autrement casserait
                # le décompte en silence. On préfère l'arrêt à l'à-peu-près.
                raise SyntheseIntrouvable(
                    "abandon illisible dans %s, commune %s : %r"
                    % (os.path.basename(chemin), l["code_insee"], bout))
            nom, mois = m.group(1), int(m.group(2))
            abandons.append({"libelle": nom, "mois": mois,
                             "annee": _annee_de(mois, date_etude)})
            par_param[nom].append(mois)
            annees[_annee_de(mois, date_etude)] += 1

        if len(abandons) != n_ab:
            raise SyntheseIntrouvable(
                "commune %s : %d abandons annoncés, %d listés. La colonne et "
                "la liste ne disent pas la même chose."
                % (l["code_insee"], n_ab, len(abandons)))

        communes.append({
            "code_insee": l["code_insee"], "commune": l["commune"],
            "dept": l["dept"], "derniere_complete": l["derniere_complete"],
            "age_mois": int(l["age_mois"]),
            "nb_parametres_complete": int(l["nb_parametres_complete"]),
            "nb_controles_depuis": int(l["nb_controles_depuis"]),
            "dernier_controle": l["dernier_controle"],
            "nb_depassements": int(l["nb_depassements"]),
            "nb_abandonnes": n_ab,
            "nb_jamais_recherches": int(l["nb_jamais_recherches"]),
            "abandons": sorted(abandons, key=lambda a: -a["mois"]),
            "plus_ancien_mois": max(a["mois"] for a in abandons),
        })

    # L'ordre par défaut du tableau : l'ancienneté du plus ancien abandon.
    # Le tri par nombre de dépassements dirait d'abord l'effort de recherche
    # (§2.11) — il reste possible à la main, il n'est pas le défaut.
    communes.sort(key=lambda c: (-c["plus_ancien_mois"], c["commune"]))

    # Un paramètre est rendu avec le nombre de COMMUNES concernées, jamais un
    # nombre de mesures : le dénominateur est la commune (§2.8).
    parametres = sorted(
        ({"libelle": nom, "communes": len(v),
          "mois_min": min(v), "mois_max": max(v)} for nom, v in par_param.items()),
        key=lambda p: (-p["communes"], -p["mois_max"], p["libelle"]))

    # La chronologie. Toutes les années entre la première et la dernière sont
    # rendues, y compris celles à zéro : une année sautée ferait lire un cycle
    # là où il y a un trou.
    n_max = max(annees.values()) if annees else 0
    moyenne = (sum(annees.values()) / len(annees)) if annees else 0
    chronologie = [
        {"annee": a, "n": annees.get(a, 0),
         "part": round(annees.get(a, 0) / n_max * 100) if n_max else 0,
         # Un « pic » est une mise en évidence de lecture, pas un résultat :
         # au-dessus de la moyenne des années documentées. La légende du
         # dossier dit que la cause n'est pas établie — la barre ne conclut
         # pas à la place du texte.
         "pic": annees.get(a, 0) > moyenne}
        for a in range(min(annees), max(annees) + 1)] if annees else []

    return {
        "source": os.path.relpath(chemin, RACINE).replace("\\", "/"),
        "date_etude": date_etude,
        "mois_abandon": MOIS_ABANDON,
        # Le périmètre du BALAYAGE, figé — cf. le piège n° 2 en tête de fichier.
        "candidates": meta.get("candidates"),
        "instruites": meta.get("instruites", len(lignes)),
        # DEUX NOMS POUR LA MÊME CHOSE, et le plus ancien est le moins juste.
        #
        # Les synthèses jusqu'au 12 août 2026 écrivaient `departements_publies`,
        # pris dans `referentiel/departements_publies.csv` — c'est-à-dire les
        # départements COLLECTÉS. Or ce qu'il faut afficher est le nombre de
        # départements que le balayage a réellement LUS, c'est-à-dire les
        # départements FIGÉS du corpus. Les deux ont divergé de douze le
        # 19 août 2026 (42 déclarés, 30 figés), et l'écart allait dans le sens
        # qui grossit le constat — le piège n° 2 en tête de ce fichier, à la
        # source cette fois plutôt qu'ici.
        #
        # `etude_panel_reduit.py` écrit donc `departements_balayes` depuis le
        # 19 août. On lit le nouveau nom d'abord et l'ancien ensuite : une
        # synthèse archivée doit continuer de s'afficher telle qu'elle a été
        # produite, sans être réinterprétée.
        "departements_balayes": meta.get("departements_balayes",
                                         meta.get("departements_publies")),
        "date_consultation": meta.get("date_consultation", date_etude.isoformat()),
        "script": meta.get("script", "src/etude_panel_reduit.py"),
        # Les quatre nombres de tête.
        "n_communes": len(communes),
        "n_parametres": sum(c["nb_abandonnes"] for c in communes),
        "n_controles": sum(c["nb_controles_depuis"] for c in communes),
        "plus_ancien_mois": max((c["plus_ancien_mois"] for c in communes), default=0),
        # Les départements où le constat tombe — à ne pas confondre avec ceux
        # qui ont été balayés.
        "departements_touches": sorted({c["dept"] for c in communes}),
        # Par département, le plus fourni d'abord — c'est l'ordre qui rend
        # lisible le déséquilibre de collecte, et le déséquilibre est le point.
        "departements": sorted(par_dept.values(),
                               key=lambda d: (-d["instruites"], d["code"])),
        "communes": communes,
        "parametres": parametres,
        "chronologie": chronologie,
    }


def chiffre_accueil():
    """
    Ce que la carte d'accueil et la carte d'index annoncent — « 18 communes ».

    Cette fonction existe pour une seule raison : le nombre était écrit à la
    main dans `build_site.DOSSIERS`. Un chiffre d'accueil tapé est un chiffre
    faux à retardement — celui-ci suit la synthèse.
    """
    return "%d communes" % faits()["n_communes"]


def _verifier(f):
    """Les contrôles qu'on veut voir passer avant de publier quoi que ce soit."""
    ok = True

    def dire(bon, quoi):
        nonlocal ok
        ok = ok and bon
        print("   %s %s" % ("ok  " if bon else "ÉCHEC", quoi))

    n_listes = sum(len(c["abandons"]) for c in f["communes"])
    dire(n_listes == f["n_parametres"],
         "%d paramètres listés = %d annoncés" % (n_listes, f["n_parametres"]))
    n_chrono = sum(a["n"] for a in f["chronologie"])
    dire(n_chrono == f["n_parametres"],
         "chronologie : %d paramètres datés = %d abandonnés" % (n_chrono, f["n_parametres"]))
    n_par_param = sum(p["communes"] for p in f["parametres"])
    dire(n_par_param == f["n_parametres"],
         "tableau des paramètres : %d couples = %d abandons" % (n_par_param, f["n_parametres"]))
    dire(all(c["nb_abandonnes"] <= c["nb_depassements"] for c in f["communes"]),
         "aucune commune n'abandonne plus de paramètres qu'elle n'en dépassait")
    dire(all(a["annee"] <= f["date_etude"].year for c in f["communes"] for a in c["abandons"]),
         "aucune dernière mesure datée après l'étude")

    # Le périmètre est le seul chiffre que le CSV ne porte pas. Sans lui, le
    # dossier ne peut pas dire sur quoi il a balayé — un verdict sans son
    # dénominateur (§2.8).
    dire(f["departements_balayes"] is not None,
         "périmètre du balayage consigné (%s départements)"
         % (f["departements_balayes"] if f["departements_balayes"] else "AUCUN — "
            "écrire le .meta.json à côté de la synthèse"))
    return ok


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--verifier", action="store_true",
                   help="les contrôles de cohérence, sans rien écrire")
    a = p.parse_args()

    f = faits()
    print("synthèse : %s (étude du %s)" % (f["source"], f["date_etude"]))
    print("balayage : %s candidates, %s instruites, %s départements publiés"
          % (f["candidates"] or "?", f["instruites"], f["departements_balayes"] or "?"))
    print("\nles quatre nombres")
    print("   %3d communes sur %s instruites" % (f["n_communes"], f["instruites"]))
    print("   %3d paramètres en dépassement, plus mesurés depuis %d mois ou plus"
          % (f["n_parametres"], f["mois_abandon"]))
    print("   %3d contrôles de routine depuis" % f["n_controles"])
    print("   %3d mois pour le plus ancien abandon" % f["plus_ancien_mois"])
    print("   départements touchés : %s" % ", ".join(f["departements_touches"]))

    print("\nles %d communes (ordre d'affichage)" % f["n_communes"])
    for c in f["communes"]:
        print("   %-28s (%s)  %2d dép.  %2d aband.  %3d contrôles  %3d mois"
              % (c["commune"][:28], c["dept"], c["nb_depassements"],
                 c["nb_abandonnes"], c["nb_controles_depuis"], c["plus_ancien_mois"]))

    print("\nce qui cesse d'être mesuré")
    for x in f["parametres"]:
        plage = ("%d mois" % x["mois_min"] if x["mois_min"] == x["mois_max"]
                 else "%d à %d mois" % (x["mois_min"], x["mois_max"]))
        print("   %-34s %2d commune(s)   %s" % (x["libelle"], x["communes"], plage))

    print("\nquand les arrêts ont-ils lieu")
    for x in f["chronologie"]:
        print("   %d %s %-3d %s" % (x["annee"], "#" * round(x["part"] / 5),
                                    x["n"], "  ← pic" if x["pic"] else ""))

    if a.verifier:
        print("\ncontrôles")
        if not _verifier(f):
            raise SystemExit(1)


if __name__ == "__main__":
    main()

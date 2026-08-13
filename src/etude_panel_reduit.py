# -*- coding: utf-8 -*-
"""
Conformité sur panel réduit — balayage systématique.

    py -X utf8 src/etude_panel_reduit.py --candidats        # qui entre, sans réseau
    py -X utf8 src/etude_panel_reduit.py --limite 3         # instruire 3 communes
    py -X utf8 src/etude_panel_reduit.py --tous             # tout le corpus

CE QUE CE SCRIPT CHERCHE
------------------------
Une eau déclarée **conforme** sur un panel d'analyse qui **ne contient plus**
les paramètres qui l'avaient rendue **non conforme** à la dernière analyse
complète. La conformité affichée ne dit alors rien de l'eau : elle dit ce qu'on
a regardé.

Cas fondateur, instruit à la main le 12 août 2026 :
`data/etudes/conformite_sur_panel_reduit/thiville-28389_2026-08-12.md`.

CE QU'IL N'ÉCRIT JAMAIS
-----------------------
Ni que l'eau serait aujourd'hui non conforme — personne ne le sait, et c'est le
point —, ni une intention. Un contrôle réduit est le régime que la
réglementation prescrit entre deux analyses complètes ; sa composition vient
des marchés pluriannuels des ARS, pas d'un arbitrage au cas par cas. Le projet
interroge la norme, jamais les acteurs (CLAUDE.md §2.1), et l'absence de mesure
ne dit rien sur la présence (§2.4).

D'OÙ VIENNENT LES DONNÉES
-------------------------
Deux sources, et elles ne servent pas à la même chose.

  · les CANDIDATS viennent du corpus figé — la base si elle est libre, sinon
    l'export publié `site/public/donnees/bulletins.csv`, qui en est la
    photographie. Le script dit laquelle il a utilisée ;
  · le SUIVI vient de Hub'Eau, parce que le corpus ne contient QUE les
    bulletins complets : les analyses de routine n'y sont jamais entrées
    (`hubeau.selectionner_bulletins`, filtre `nb_lignes > SEUIL_COMPLET`).
    C'est précisément ce qui rend ce balayage nécessaire.

ÉTIQUETTE (§3.2)
----------------
Une commune = un à deux appels. Le cache disque évite de redemander ce qu'on a
déjà. Temporisation entre deux appels, `User-Agent` du projet, et `--limite`
par défaut : on ne lance pas un balayage de plusieurs centaines de communes
sans l'avoir mesuré sur trois.
"""
import argparse
import collections
import csv
import datetime
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

try:
    from common import DB_PATH, SEUIL_COMPLET, USER_AGENT
except Exception:                                    # exécution hors dépôt
    DB_PATH = os.path.join(RACINE, "data", "eau.duckdb")
    SEUIL_COMPLET = 200
    USER_AGENT = "Observatoire-potabilite"

API = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis"
EXPORT = os.path.join(RACINE, "site", "public", "donnees", "bulletins.csv")
SORTIE = os.path.join(RACINE, "data", "etudes", "conformite_sur_panel_reduit")
CACHE = os.path.join(RACINE, "data", "brut", "_panel_reduit")
PAUSE = 0.4


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def mois_entre(d1, d2):
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def non_conforme(txt):
    """
    L'administration écrit tantôt « non conforme », tantôt « non-conforme ».
    Chercher la première forme seule fait passer la seconde pour une
    conformité — le dossier Villemaury en marquait ainsi deux sur dix, et
    l'erreur allait dans le sens qui AFFAIBLIT le constat. Corrigé le
    12 août 2026 : le trait d'union est ramené à une espace avant la
    comparaison.
    """
    return "non conform" in norm(txt).replace("-", " ")


def lire_limite(txt):
    """
    « <=0,1 µg/L » -> 0.1. Rend None quand la limite n'est pas un plafond
    simple — un encadrement (« >=6,5 et <=9 »), un texte, un vide.

    On ne devine pas : une limite mal lue produirait un faux dépassement, et
    un faux positif coûte plus cher qu'un faux négatif (§2.13).
    """
    if not txt:
        return None
    t = str(txt).strip()
    if ">=" in t or "et" in norm(t):
        return None
    m = re.search(r"<=?\s*([0-9]+(?:[.,][0-9]+)?)", t)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return None


def appel(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def resultats(insee, depuis):
    """Tous les résultats d'une commune depuis une date. Caché sur disque."""
    os.makedirs(CACHE, exist_ok=True)
    chemin = os.path.join(CACHE, f"{insee}_{depuis}.json")
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)

    lignes, url, page = [], None, 1
    while True:
        # `size=5000`, et non 1000 : mesuré le 13 août 2026 sur 37 réponses
        # réelles, une commune rend 1 233 lignes en moyenne — donc UNE page à
        # 5 000, contre deux à quatre à 1 000. La pagination à 1 000 demandait
        # 76 % d'appels de trop à un service public gratuit, ce qui est notre
        # propre règle d'étiquette non respectée (CLAUDE.md §3.2 : pagination
        # maximale). La documentation Hub'Eau annonce 20 000 en maximum.
        u = url or (f"{API}?code_commune={insee}"
                    f"&date_min_prelevement={depuis}&size=5000&page={page}")
        d = appel(u)
        lignes += d.get("data") or []
        if not d.get("next"):
            break
        url, page = d["next"], page + 1
        time.sleep(PAUSE)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(lignes, f)
    time.sleep(PAUSE)
    return lignes


# ---------------------------------------------------------------------------
# 1. Les candidats
# ---------------------------------------------------------------------------
def candidats(mois_min, aujourd_hui):
    """
    La dernière analyse complète de chaque commune, quand elle est ancienne
    ET qu'elle portait au moins un dépassement.
    """
    lignes, source = _corpus()
    par_commune = {}
    for r in lignes:
        if r["est_complet"] not in ("1", "True", "true", 1, True):
            continue
        cle = r["code_insee"]
        d = r["date_prelevement"][:10]
        if cle not in par_commune or d > par_commune[cle]["date_prelevement"][:10]:
            par_commune[cle] = r

    # L'HISTORIQUE des analyses complètes, gardé à côté de la dernière.
    # Ajouté le 12 août 2026 sur demande de Yannick, et c'est ce qui donne au
    # dossier sa portée : savoir si la non-conformité était un accident ou un
    # état. Villemaury a dix analyses complètes en sept ans, toutes non
    # conformes — puis trente-neuf contrôles de routine, tous conformes.
    histo = collections.defaultdict(list)
    for r in lignes:
        if r["est_complet"] in ("1", "True", "true", 1, True):
            histo[r["code_insee"]].append(r)

    out = []
    for r in par_commune.values():
        d = datetime.date.fromisoformat(r["date_prelevement"][:10])
        age = mois_entre(d, aujourd_hui)
        if age < mois_min:
            continue
        try:
            dep = int(r.get("nb_depasse_applicable") or 0)
        except ValueError:
            dep = 0
        if dep <= 0:
            continue
        out.append({
            "code_insee": r["code_insee"], "commune": r["commune"],
            "dept": r["dept"], "date": d.isoformat(), "age_mois": age,
            "nb_parametres": r.get("nb_parametres"),
            "nb_depasse": dep,
            "conclusion": (r.get("conclusion_conformite") or "")[:400],
            "historique": sorted(
                ({"date": h["date_prelevement"][:10],
                  "nb_parametres": h.get("nb_parametres"),
                  "nb_depasse": h.get("nb_depasse_applicable"),
                  "non_conforme": non_conforme(
                      h.get("conclusion_conformite") or "")}
                 for h in histo[r["code_insee"]]),
                key=lambda x: x["date"]),
        })
    out.sort(key=lambda x: (-x["age_mois"], -x["nb_depasse"]))
    return out, source


def _corpus():
    """La base si elle est libre, sinon l'export publié. Dit laquelle."""
    try:
        import duckdb
        con = duckdb.connect(DB_PATH, read_only=True)
        cols = ["code_insee", "commune", "dept", "date_prelevement",
                "nb_parametres", "est_complet", "nb_depasse_applicable",
                "conclusion_conformite"]
        v = con.execute(
            "SELECT version_referentiel FROM figeage_moteur LIMIT 1").fetchone()[0]
        rows = con.execute(f"""
            SELECT {", ".join(cols)} FROM analyses_figees
            WHERE version_referentiel = ?
        """, [v]).fetchall()
        con.close()
        return ([dict(zip(cols, [str(x) if x is not None else "" for x in r]))
                 for r in rows], f"base (version {v})")
    except Exception as e:
        if not os.path.exists(EXPORT):
            raise SystemExit(
                "ni la base ni l'export publié ne sont lisibles.\n  %s" % e)
        with open(EXPORT, encoding="utf-8-sig") as f:
            return list(csv.DictReader(f, delimiter=";")), \
                   "export publié (base indisponible : %s)" % str(e)[:60]


# ---------------------------------------------------------------------------
# 2. L'instruction d'une commune
# ---------------------------------------------------------------------------
def instruire(c):
    """
    Les paramètres en dépassement à la dernière analyse complète ont-ils été
    recherchés depuis ?
    """
    lignes = resultats(c["code_insee"], c["date"])
    prels = collections.defaultdict(list)
    for l in lignes:
        prels[(l["date_prelevement"][:10], l["code_prelevement"])].append(l)
    if not prels:
        return None
    ordre = sorted(prels)
    ref, suivants = ordre[0], ordre[1:]

    # Les dépassements de la référence, lus sur la limite déclarée par la source.
    cibles = {}
    for l in prels[ref]:
        lim = lire_limite(l.get("limite_qualite_parametre"))
        v = l.get("resultat_numerique")
        if lim is None or v is None:
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if v > lim:
            cibles[l["code_parametre"]] = {
                "libelle": l["libelle_parametre"], "valeur": v, "limite": lim,
                "unite": l.get("libelle_unite") or "",
            }

    aujourd_hui = datetime.date.today()
    for code, d in cibles.items():
        d["revu"] = []
        for k in suivants:
            ici = [l for l in prels[k] if l["code_parametre"] == code]
            if ici:
                d["revu"].append((k[0], ici[0].get("resultat_numerique")))
        # L'INDICATEUR N'EST PAS BINAIRE, et l'avoir cru l'a rendu faux.
        # Corrigé le 12 août 2026 sur le cas de Nottonville : quatre pesticides
        # y avaient été recontrôlés UNE fois, en septembre 2018, puis plus
        # jamais — trente contrôles plus tard. Un « oui, il a été revu » les
        # comptait comme suivis. Ce qui se mesure est l'ANCIENNETÉ de la
        # dernière mesure, pas son existence.
        derniere = d["revu"][-1][0] if d["revu"] else c["date"]
        d["derniere_mesure"] = derniere
        d["mois_sans_mesure"] = mois_entre(
            datetime.date.fromisoformat(derniere), aujourd_hui)
        d["nb_mesures_depuis"] = len(d["revu"])

    # « Abandonné » : plus mesuré depuis au moins deux ans, alors que la
    # commune, elle, continue d'être contrôlée.
    abandonnes = {k: v for k, v in cibles.items() if v["mois_sans_mesure"] >= 24}
    return {
        "commune": c, "ref": ref, "nb_ref": len(prels[ref]),
        "suivants": [(k[0], len(prels[k])) for k in suivants],
        "cibles": cibles,
        "jamais": {k: v for k, v in cibles.items() if not v["revu"]},
        "abandonnes": abandonnes,
        "dernier_controle": suivants[-1][0] if suivants else None,
    }


# ---------------------------------------------------------------------------
# 3. Sorties
# ---------------------------------------------------------------------------
def rapport(res):
    c, cib, jam = res["commune"], res["cibles"], res["jamais"]
    L = ["# %s (%s) — conformité sur panel réduit" % (c["commune"], c["code_insee"]),
         "",
         "**Dernière analyse complète : %s, %s paramètres — il y a %d mois.**"
         % (c["date"], res["nb_ref"], c["age_mois"]),
         ""]
    if res["suivants"]:
        L += ["%d analyse(s) de contrôle depuis, la dernière le %s. "
              "L'eau est donc suivie — ce n'est pas un abandon de surveillance."
              % (len(res["suivants"]), res["dernier_controle"]), ""]
    else:
        L += ["**Aucune analyse depuis.**", ""]

    # L'HISTORIQUE — était-ce un accident, ou un état ?
    h = c.get("historique") or []
    if h:
        nc = sum(1 for x in h if x["non_conforme"])
        L += ["## Les analyses complètes du corpus, avant celle-ci", ""]
        if nc == len(h) and len(h) > 1:
            L += ["**Les %d analyses complètes de cette commune sont non "
                  "conformes.** Ce n'est pas un accident ponctuel : c'est un "
                  "état, sur %d ans." % (len(h),
                                         int(h[-1]["date"][:4]) - int(h[0]["date"][:4]) or 1),
                  ""]
        L += ["| date | paramètres | dépassements | conclusion |", "|---|---:|---:|---|"]
        for x in h:
            L.append("| %s | %s | %s | %s |"
                     % (x["date"], x["nb_parametres"], x["nb_depasse"],
                        "**non conforme**" if x["non_conforme"] else "conforme"))
        L.append("")

    L += ["## Les analyses depuis", "", "| date | paramètres |", "|---|---:|"]
    L += ["| %s | %d |" % s for s in res["suivants"]]
    L += ["", "## Les dépassements de la dernière analyse complète", "",
          "| paramètre | valeur | limite | fois mesuré depuis | dernière mesure | sans mesure depuis |",
          "|---|---:|---:|---:|---|---:|"]
    for d in sorted(cib.values(), key=lambda x: -x["mois_sans_mesure"]):
        L.append("| %s | %s %s | %s | %d | %s | **%d mois** |"
                 % (d["libelle"], d["valeur"], d["unite"], d["limite"],
                    d["nb_mesures_depuis"],
                    d["derniere_mesure"] if d["revu"] else "jamais revu",
                    d["mois_sans_mesure"]))
    ab = res["abandonnes"]
    L += ["",
          "**%d dépassement(s). %d n'ont plus été mesurés depuis au moins "
          "24 mois**, dont %d jamais recontrôlés du tout."
          % (len(cib), len(ab), len(jam)), "",
          "*Un paramètre recontrôlé une fois puis abandonné compte ici comme "
          "abandonné : ce qui se mesure est l'ancienneté de la dernière mesure, "
          "pas son existence.*", "",
          "> Ce qui précède ne dit pas que l'eau serait aujourd'hui non conforme :",
          "> personne ne le sait, et c'est le point. L'absence de mesure ne dit rien",
          "> sur la présence. Un contrôle réduit est le régime que la réglementation",
          "> prescrit entre deux analyses complètes.", "",
          "*Source : Hub'Eau, `qualite_eau_potable/resultats_dis`, commune %s, "
          "consultée le %s.*" % (c["code_insee"], datetime.date.today().isoformat())]
    return "\n".join(L)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--mois", type=int, default=24,
                   help="ancienneté minimale de la dernière analyse complète")
    p.add_argument("--candidats", action="store_true",
                   help="lister les communes retenues, sans aucun appel réseau")
    p.add_argument("--limite", type=int, default=3,
                   help="nombre de communes à instruire (défaut 3 — mesurer avant)")
    p.add_argument("--tous", action="store_true", help="toutes les candidates")
    p.add_argument("--insee", help="instruire ces communes-là, séparées par des "
                                   "virgules — passe outre --limite et --mois")
    p.add_argument("--sans-fiche", action="store_true",
                   help="ne pas écrire un fichier par commune")
    a = p.parse_args()

    aujourd_hui = datetime.date.today()
    # Une demande nominative passe outre les deux filtres : on instruit ce
    # qu'on veut regarder, pas seulement ce qui tombe dans le critère.
    cands, source = candidats(0 if a.insee else a.mois, aujourd_hui)
    if a.insee:
        vise = {c.strip() for c in a.insee.split(",")}
        cands = [c for c in cands if c["code_insee"] in vise]
        manquants = vise - {c["code_insee"] for c in cands}
        if manquants:
            print("!! sans dépassement à leur dernière analyse complète, ou "
                  "absentes du corpus : %s" % ", ".join(sorted(manquants)))
    print("corpus lu depuis : %s" % source)
    print("%d commune(s) dont la dernière analyse complète a plus de %d mois "
          "ET portait au moins un dépassement.\n" % (len(cands), a.mois))
    for c in cands[:40]:
        print("   %-28s %s  %s  %3d mois  %2d dépassement(s)  %s param."
              % (c["commune"][:28], c["code_insee"], c["date"],
                 c["age_mois"], c["nb_depasse"], c["nb_parametres"]))
    if len(cands) > 40:
        print("   … et %d autres" % (len(cands) - 40))
    if a.candidats:
        return

    lot = cands if a.tous else cands[:a.limite]
    print("\ninstruction de %d commune(s) — appels Hub'Eau, cache actif\n" % len(lot))
    os.makedirs(SORTIE, exist_ok=True)
    synthese = []
    for i, c in enumerate(lot, 1):
        print("  [%d/%d] %s (%s)…" % (i, len(lot), c["commune"], c["code_insee"]),
              flush=True)
        try:
            res = instruire(c)
        except Exception as e:
            print("      ÉCHEC : %s" % str(e)[:120])
            continue
        if not res:
            print("      aucun résultat rendu par l'API")
            continue
        n_cib = len(res["cibles"])
        n_jam, n_ab = len(res["jamais"]), len(res["abandonnes"])
        print("      %d dépassement(s), %d sans mesure depuis 24 mois ou plus "
              "(dont %d jamais recontrôlés), %d analyse(s) de contrôle"
              % (n_cib, n_ab, n_jam, len(res["suivants"])))
        synthese.append({
            "code_insee": c["code_insee"], "commune": c["commune"],
            "dept": c["dept"], "derniere_complete": c["date"],
            "age_mois": c["age_mois"], "nb_parametres_complete": res["nb_ref"],
            "nb_controles_depuis": len(res["suivants"]),
            "dernier_controle": res["dernier_controle"] or "",
            "nb_depassements": n_cib,
            "nb_abandonnes_24m": n_ab, "nb_jamais_recherches": n_jam,
            "abandonnes": " | ".join(
                "%s (%d mois)" % (v["libelle"], v["mois_sans_mesure"])
                for v in sorted(res["abandonnes"].values(),
                                key=lambda x: -x["mois_sans_mesure"])),
        })
        if not a.sans_fiche and n_ab:
            # PRÉFIXE « auto_ » — ce que ce script écrit lui appartient, et
            # rien d'autre. Le 12 août 2026, une relance a écrasé l'étude
            # rédigée à la main sur Thiville : même dossier, même nom de
            # fichier, 6 Ko de rédaction remplacés par un tableau généré.
            # Un script ne doit jamais pouvoir détruire ce qu'une main a écrit.
            nom = "auto_%s-%s_%s.md" % (
                norm(c["commune"]).replace(" ", "-").replace("'", ""),
                c["code_insee"], aujourd_hui.isoformat())
            with open(os.path.join(SORTIE, nom), "w", encoding="utf-8") as f:
                f.write(rapport(res))

    if synthese:
        f_csv = os.path.join(SORTIE, "synthese_%s.csv" % aujourd_hui.isoformat())
        with open(f_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(synthese[0]), delimiter=";")
            w.writeheader()
            w.writerows(synthese)
        print("\nsynthèse : %s" % f_csv)
        avec = [s for s in synthese if s["nb_jamais_recherches"]]
        print("%d commune(s) sur %d portent au moins un dépassement jamais "
              "recherché depuis." % (len(avec), len(synthese)))


if __name__ == "__main__":
    main()

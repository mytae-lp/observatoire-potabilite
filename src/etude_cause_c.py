# -*- coding: utf-8 -*-
"""
La cause C recomptée — un artefact ESTAMPILLÉ, régénérable, jamais recopié.

    py -X utf8 src/etude_cause_c.py              # → data/etudes/cause_C_compte_<version>_<date>.md
    py -X utf8 src/etude_cause_c.py --sortie -   # à l'écran

Pourquoi ce script existe
-------------------------
Le découpage de la cause C (`data/etudes/cause_C_familles_2026-08-10.md`) porte
une table de nombres **écrite à la main** le 10 août 2026, sur un corpus à deux
départements. Le Rhône est entré depuis, et chaque département qui entrera la
périmera de nouveau. Un nombre recopié dans un document ne se reprend pas : on
ne sait plus contre quel corpus ni contre quelle grille il a été calculé, et on
finit par raisonner dessus deux jours durant. C'est exactement l'accident du
« 295 bulletins complets, 155 cas, 52 % » du Rhône partiel — corrigé le 11 août
dans `fetch_departement.rapport()`, et la même leçon s'applique aux études.

**Deux estampilles, pas une.** `version_referentiel` dit contre quelle grille ;
le **corpus** dit sur quelles données. Aucune ne se déduit de l'autre : la même
grille appliquée à un corpus plus large ne donne pas les mêmes comptes, et le
même corpus sous une grille nouvelle non plus.

Ce que ce script NE fait pas : décider qui est « sans aucun seuil ». Cette
règle vit dans `v_parametres_non_apparies` (`src/build_db.py`) et nulle part
ailleurs — elle a déjà été corrigée une fois, le 10 août, quand elle oubliait
les références de qualité déclarées et surcomptait 157 libellés pour 143 réels.
Une seconde copie de cette règle divergerait à la première retouche. Le script
prend la liste que la vue lui donne, et ne fait que la **découper** par
département et par complétude.

Trois découpages, et ils ne disent pas la même chose
----------------------------------------------------
1. **tout le corpus** — le compte brut, comparable au document du 10 août ;
2. **bulletins complets seulement** (§2.3) — le seul dénominateur sur lequel le
   projet raisonne, et donc le seul citable dans une sortie ;
3. **par département** — parce qu'un compte agrégé mélange des panels qui ne
   sont pas les mêmes (§2.11, quatrième règle : un département se compare à
   lui-même). Le perchlorate le montre : 219 mesures, aucune dans le Rhône.
   Agréger le ferait passer pour rare une substance simplement pas cherchée là.
"""
import argparse
import datetime
import os
import sys

import duckdb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import figer  # noqa: E402
from common import DB_PATH, RACINE  # noqa: E402

SORTIE_DIR = os.path.join(RACINE, "data", "etudes")


def _corpus(con):
    """L'estampille de corpus : ce sur quoi les comptes portent."""
    depts = con.execute("""
        SELECT SUBSTR(code_insee, 1, 2) AS dept,
               COUNT(DISTINCT code_insee) AS communes,
               COUNT(*) AS bulletins
        FROM prelevements GROUP BY 1 ORDER BY bulletins DESC
    """).fetchall()
    tot = con.execute(
        "SELECT COUNT(*), (SELECT COUNT(*) FROM mesures) FROM prelevements"
    ).fetchone()
    return depts, tot


def _non_apparies(con):
    """La liste, telle que la vue la définit. On ne rejuge rien ici."""
    return con.execute("""
        SELECT libelle_parametre, libelle_norm, code_parametre_observe, code_cas,
               unite, nb_mesures, nb_communes, nb_quantifiees, max_quantifie
        FROM v_parametres_non_apparies
        ORDER BY nb_quantifiees DESC, nb_mesures DESC
    """).fetchall()


def _decoupage(con, libelles):
    """
    Pour chaque libellé retenu par la vue : le détail par département et par
    complétude. Le filtre d'appartenance est celui de la vue, repris tel quel
    depuis `v_mesures_ref` — pas réécrit, restreint aux libellés qu'elle nomme.
    """
    if not libelles:
        return {}
    con.execute("CREATE OR REPLACE TEMP TABLE _libelles(libelle_norm VARCHAR)")
    con.executemany("INSERT INTO _libelles VALUES (?)", [(l,) for l in libelles])
    rows = con.execute("""
        SELECT r.libelle_norm,
               SUBSTR(r.code_insee, 1, 2)              AS dept,
               p.est_complet                           AS complet,
               COUNT(*)                                AS mesures,
               COUNT(DISTINCT r.code_insee)            AS communes,
               COUNT(*) FILTER (WHERE r.est_quantifie) AS quantifiees
        FROM v_mesures_ref r
        JOIN _libelles USING (libelle_norm)
        JOIN v_prelevement_verdict p USING (code_prelevement)
        WHERE r.ref_key IS NULL AND r.limite_declaree IS NULL
          AND r.reference_max IS NULL AND r.reference_min IS NULL
        GROUP BY 1, 2, 3
    """).fetchall()
    d = {}
    for lib, dept, complet, mes, com, qt in rows:
        d.setdefault(lib, []).append((dept, bool(complet), mes, com, qt))
    return d


def _tableau(titre, lignes, note=None):
    out = [f"### {titre}", ""]
    if note:
        out += [note, ""]
    out += ["| substance | code | unité | mesures | communes | quantifiées |",
            "|---|---|---|---:|---:|---:|"]
    for lib, code, unite, mes, com, qt in lignes:
        out.append(f"| {lib} | {code or ''} | {unite or ''} | {mes} | {com} | {qt} |")
    out.append("")
    return out


def construire(db=DB_PATH):
    con = duckdb.connect(db, read_only=True)
    try:
        version = figer.version_referentiel()
        depts, (nb_prel, nb_mes) = _corpus(con)
        lignes = _non_apparies(con)
        par_lib = _decoupage(con, [r[1] for r in lignes])
    finally:
        con.close()

    jour = datetime.date.today().isoformat()
    doc = [
        f"# Cause C — comptes au {jour}",
        "",
        "**Artefact produit par `src/etude_cause_c.py`. Ne pas modifier à la "
        "main : il est régénéré, et toute retouche serait perdue sans trace.**",
        "",
        "Matériau d'étude, hors chaîne de publication. Il remplace la table de "
        "nombres du `cause_C_familles_2026-08-10.md`, qui était écrite à la main "
        "sur un corpus à deux départements et n'était donc pas reprenable.",
        "",
        "## Estampilles — les deux sont nécessaires",
        "",
        f"- **version de référentiel** : `{version}` — contre quelle grille ;",
        f"- **corpus** : {nb_prel} prélèvements, {nb_mes} mesures — sur quelles données ;",
        f"- **calculé le** : {jour}.",
        "",
        "Un compte repris d'ici se cite **avec les deux**. La même grille sur un "
        "corpus plus large ne donne pas les mêmes nombres, et le même corpus sous "
        "une grille nouvelle non plus.",
        "",
        "| département | communes | prélèvements |",
        "|---|---:|---:|",
    ]
    for dept, com, bul in depts:
        doc.append(f"| {dept} | {com} | {bul} |")
    doc += [
        "",
        f"**{len(lignes)} libellés sans aucun seuil de comparaison** — ni ligne de "
        "référentiel, ni limite déclarée, ni référence de qualité déclarée. La "
        "règle d'appartenance est celle de `v_parametres_non_apparies` "
        "(`src/build_db.py`) ; ce script ne la rejuge pas, il la découpe.",
        "",
        "---",
        "",
        "## Le noyau — quantifiées au moins une fois",
        "",
        "**La substance est là, dans l'eau, et rien ne la juge.** C'est la "
        "démonstration la plus forte du dossier, et la seule famille dont le "
        "périmètre grandit tout seul : une substance passe de « jamais trouvée » "
        "à « trouvée » quand un département arrive, jamais l'inverse. Tout "
        "nombre publié ici est donc une **borne inférieure**.",
        "",
    ]

    noyau = [r for r in lignes if r[7] > 0]
    reste = [r for r in lignes if r[7] == 0]

    doc += _tableau(
        f"Sur tout le corpus — {len(noyau)} libellés",
        [(r[0], r[2], r[4], r[5], r[6], r[7]) for r in noyau])

    # Bulletins complets seulement : le seul dénominateur sur lequel le projet
    # raisonne (§2.3). Un libellé qui disparaît d'ici n'a été vu que dans des
    # analyses de routine — c'est un fait, et il doit se voir.
    lignes_c = []
    for r in noyau:
        det = [d for d in par_lib.get(r[1], []) if d[1]]
        if not det:
            continue
        mes = sum(d[2] for d in det)
        com = sum(d[3] for d in det)   # somme par département : pas de doublon
        qt = sum(d[4] for d in det)
        if qt:
            lignes_c.append((r[0], r[2], r[4], mes, com, qt))
    lignes_c.sort(key=lambda x: (-x[5], -x[3]))
    doc += _tableau(
        f"Sur les bulletins complets seulement (§2.3) — {len(lignes_c)} libellés",
        lignes_c,
        "C'est ce tableau qui est citable dans une sortie : le projet ne "
        "raisonne que sur les bulletins complets.")

    doc += [
        "### Le détail par département (§2.11)",
        "",
        "Un compte agrégé mélange des panels différents. Une substance absente "
        "d'un département n'y est pas rare : elle n'y est **pas cherchée**, ce "
        "qui n'est pas la même information (§2.4).",
        "",
        "| substance | département | mesures | communes | quantifiées |",
        "|---|---|---:|---:|---:|",
    ]
    for r in noyau:
        for dept, complet, mes, com, qt in sorted(par_lib.get(r[1], [])):
            if complet:
                doc.append(f"| {r[0]} | {dept} | {mes} | {com} | {qt} |")
    doc += [
        "",
        "---",
        "",
        f"## Jamais quantifiées — {len(reste)} libellés",
        "",
        "**§2.4 : ce n'est pas une absence, c'est un « sous la limite de "
        "quantification ».** Aucune phrase d'absence ne se tire de ce tableau. "
        "Pour les substances mesurées en ng/L, la LQ doit être regardée avant "
        "toute affirmation (§8bis, obligation 11).",
        "",
    ]
    doc += _tableau("", [(r[0], r[2], r[4], r[5], r[6], r[7]) for r in reste])
    return "\n".join(doc) + "\n", version, jour


def main():
    p = argparse.ArgumentParser(description="Recompte estampillé de la cause C")
    p.add_argument("--sortie", help="chemin de sortie, ou « - » pour l'écran")
    a = p.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"base absente : {DB_PATH}\nlance d'abord : py -X utf8 src/build_db.py")
        sys.exit(1)
    try:
        texte, version, jour = construire()
    except duckdb.IOException as e:
        print("base verrouillée par un autre processus — l'étude ne peut pas "
              "être calculée maintenant.\n"
              "  (collecte en cours ? attendre qu'elle rende la main)")
        print(f"  {str(e).splitlines()[0]}")
        sys.exit(2)

    if a.sortie == "-":
        print(texte)
        return
    chemin = a.sortie or os.path.join(SORTIE_DIR, f"cause_C_compte_{version}_{jour}.md")
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(texte)
    print(f"écrit : {chemin}")
    print(f"  version de référentiel {version}, calculé le {jour}")


if __name__ == "__main__":
    main()

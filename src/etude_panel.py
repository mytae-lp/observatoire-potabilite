# -*- coding: utf-8 -*-
"""
Le journal des abandons — ce qu'on a cessé de chercher.

    py -X utf8 src/etude_panel.py

Le §2.11 pose que l'effort de recherche est un indicateur. Il l'exprime par un
nombre : 627 paramètres en 2019, 369 en 2024. Ce script en tire la LISTE — quels
paramètres ont disparu du programme d'analyse, où, et quand.

Demande de Yannick, 8 août 2026 :

    « quand en 2018 on cherche 650 paramètres et qu'en 2026 on en recherche plus
    que 300, je veux connaître lesquels on ne recherche plus. Ainsi sur plusieurs
    centaines de communes on pourra peut-être trouver une direction commune. »

C'est un MATÉRIAU D'ÉTUDE, pas une sortie publique. Il ne dit rien de la qualité
de l'eau : il décrit ce qu'on a choisi d'en savoir. Un paramètre retiré peut
l'avoir été parce que la molécule est interdite depuis vingt ans, parce que le
laboratoire a changé, ou parce que ce bulletin relevait d'un autre programme.
Le premier livrable est donc un dénombrement, sans interprétation — l'indicateur
le plus solide avant tout ce qui suit (cf. docs/METHODE_EFFET_COCKTAIL.md).

Cinq fichiers dans `data/etudes/`, non versionnés comme toute donnée dérivée :

    panel_evolution.csv         une ligne par paire de bulletins consécutifs
    journal_abandons.csv        une ligne par (commune, paramètre abandonné)
    parametres_abandonnes.csv   le cumul par paramètre
    parametre_presence.csv      la part des bulletins qui cherchent un paramètre,
                                année par année — le détecteur à l'échelle
    parametre_presence_dept.csv la même, par département — le contre-feu

Trois réserves de lecture, à ne pas perdre :

1. `meme_point_deau` distingue une évolution d'un écart. Deux bulletins d'une
   même commune ne portent pas forcément sur le même captage — à Boissezon il y
   en a trois. Comparer leurs panels reste légitime, c'est le programme
   d'analyse qu'on observe ; parler d'évolution d'une même eau ne l'est pas
   (§2.3). `identite_certaine` dit si la réponse est lue ou déduite : le
   `code_installation_amont` est vide sur un tiers des bulletins et se voit
   recodé d'une campagne à l'autre.

2. Le nombre de paramètres DISTINCTS peut différer du `nb_parametres` déclaré :
   4 couples du corpus portent la même substance deux ou trois fois sur le même
   bulletin (microcystines à Montech, essai marbre à Rostrenen). L'écart est de
   6 paramètres au maximum, et c'est le compte distinct qui fait foi ici.

3. Une chute de présence nationale n'est pas forcément un retrait. Le corpus
   change de composition d'une année sur l'autre — 7 bulletins sur 2
   départements en 2022, 13 sur 6 en 2026 — et un paramètre qui ne serait
   qu'une habitude locale chuterait sans avoir été retiré nulle part. Toute
   chute est donc affichée avec ses deux contrôles : la strate départementale
   (`v_parametre_presence_dept`) et les communes réellement suivies
   (`v_parametres_abandonnes`). Deux contrôles indépendants qui concordent,
   c'est un début ; un seul ne dit rien.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import duckdb  # noqa: E402
from common import DB_PATH  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "data", "etudes")

# La barre verticale sépare les éléments d'une liste À L'INTÉRIEUR d'une
# cellule : le point-virgule est le séparateur de colonnes, et l'y glisser
# décalerait silencieusement toute la ligne (CLAUDE.md §5).
EXPORTS = [
    ("panel_evolution.csv", """
        SELECT code_insee, commune, dept,
               date_precedente, date_courante,
               prelevement_precedent, prelevement_courant,
               installation_precedente, installation_courante,
               meme_point_deau, identite_certaine,
               panel_precedent, panel_courant, variation_panel,
               nb_abandonnes, nb_nouveaux,
               array_to_string(abandonnes, '|') AS cles_abandonnees,
               array_to_string(nouveaux,   '|') AS cles_nouvelles
        FROM v_panel_evolution
     """),
    ("journal_abandons.csv", """
        WITH detail AS (
            SELECT code_insee, commune, dept, date_precedente, date_courante,
                   meme_point_deau, identite_certaine,
                   UNNEST(abandonnes) AS cle_param
            FROM v_panel_evolution
        ),
        libelles AS (
            SELECT COALESCE(code_parametre, libelle_norm) AS cle_param,
                   ANY_VALUE(libelle_parametre)           AS libelle
            FROM mesures GROUP BY 1
        )
        SELECT d.code_insee, d.commune, d.dept,
               d.date_precedente, d.date_courante,
               d.meme_point_deau, d.identite_certaine,
               d.cle_param, COALESCE(l.libelle, d.cle_param) AS libelle_parametre
        FROM detail d LEFT JOIN libelles l ON l.cle_param = d.cle_param
        ORDER BY d.commune, d.date_courante, libelle_parametre
     """),
    ("parametres_abandonnes.csv", "SELECT * FROM v_parametres_abandonnes"),
    ("parametre_presence.csv", "SELECT * FROM v_parametre_presence"),
    ("parametre_presence_dept.csv", "SELECT * FROM v_parametre_presence_dept"),
]


def exporter(con, dossier):
    os.makedirs(dossier, exist_ok=True)
    ecrits = []
    for nom, requete in EXPORTS:
        chemin = os.path.join(dossier, nom)
        # Le dépôt vit dans un dossier nommé « …qualité de l'eau en France ».
        # L'apostrophe ferme la chaîne SQL et fait échouer le COPY : elle se
        # double. Un chemin n'est pas une donnée de confiance, même le nôtre.
        con.execute(f"COPY ({requete}) TO '{chemin.replace(chr(39), chr(39) * 2)}' "
                    "(HEADER, DELIMITER ';', QUOTE '\"')")
        n = con.execute(f"SELECT COUNT(*) FROM ({requete})").fetchone()[0]
        ecrits.append((nom, n))
    return ecrits


def resumer(con):
    """Ce qu'on voit tout de suite, et ce qu'il faut se garder d'en conclure."""
    paires, communes = con.execute("""
        SELECT COUNT(*), COUNT(DISTINCT code_insee) FROM v_panel_evolution
    """).fetchone()
    if not paires:
        print("\naucune commune ne porte deux bulletins complets : rien à comparer.")
        print("le journal des abandons prend son sens à partir de quelques")
        print("centaines de communes (cf. docs/CHANTIERS.md, chantier 6).")
        return

    print(f"\n=== {paires} paire(s) de bulletins consécutifs, "
          f"sur {communes} commune(s) ===\n")
    for r in con.execute("""
        SELECT commune, date_precedente, date_courante,
               panel_precedent, panel_courant, nb_abandonnes, nb_nouveaux,
               meme_point_deau, identite_certaine
        FROM v_panel_evolution ORDER BY nb_abandonnes DESC
    """).fetchall():
        point = ("même point d'eau" if r[7] else "point d'eau différent")
        if not r[8]:
            point = "présumé " + point.replace("même point d'eau", "le même") \
                                     .replace("point d'eau différent", "différent")
        print(f"  {r[0]:<24} {r[1]} → {r[2]}   {r[3]:>4} → {r[4]:<4} "
              f"−{r[5]:<4} +{r[6]:<4} {point}")

    print("\n=== les paramètres les plus souvent abandonnés ===\n")
    for r in con.execute("""
        SELECT libelle_parametre, nb_abandons, nb_communes
        FROM v_parametres_abandonnes LIMIT 10
    """).fetchall():
        print(f"  {r[0]:<44} {r[1]} fois, {r[2]} commune(s)")

    # Ce que le corpus permet déjà de voir : un paramètre cherché partout une
    # année et presque plus la suivante. Le dénominateur est affiché — sur trois
    # bulletins dans l'année, un pourcentage ne veut rien dire (§2.11).
    #
    # `v_parametre_presence` porte désormais une ligne à 0 % pour un paramètre
    # qui n'a pas été cherché du tout : sans elle, la jointure ci-dessous
    # manquait le cas le plus net — l'abandon complet — parce qu'il n'y avait
    # aucune ligne à joindre.
    chutes = con.execute("""
        SELECT a.cle_param, a.libelle_parametre,
               a.annee, a.pct_bulletins, a.nb_bulletins,
               b.annee, b.pct_bulletins, b.nb_bulletins
        FROM v_parametre_presence a
        JOIN v_parametre_presence b
          ON b.cle_param = a.cle_param AND b.annee > a.annee
        WHERE a.nb_bulletins >= 5 AND b.nb_bulletins >= 5
          AND a.pct_bulletins >= 75 AND b.pct_bulletins <= 25
        ORDER BY a.libelle_parametre, a.annee
    """).fetchall()
    if chutes:
        print("\n=== cherché partout, puis presque plus ===\n")
        vus = set()
        for cle, lib, a1, p1, n1, a2, p2, n2 in chutes:
            if lib in vus:
                continue
            vus.add(lib)
            print(f"  {lib}")
            print(f"      {p1:>5} % en {a1} ({n1} bull.)"
                  f"  →  {p2:>5} % en {a2} ({n2} bull.)")
            for ligne in controler_chute(con, cle, a2):
                print(f"      {ligne}")
        print("\n  Ce n'est pas une dégradation de l'eau : c'est un retrait du")
        print("  programme d'analyse. Sur ce qui n'est plus cherché, on ne sait rien.")


def controler_chute(con, cle_param, annee):
    """Les deux contrôles qui séparent un retrait d'un artefact de corpus.

    Une présence nationale qui chute peut n'être qu'un changement de
    composition : le corpus passe de 2 départements en 2022 à 6 en 2026, et une
    habitude locale s'y dilue sans avoir été retirée nulle part. D'où deux
    lectures indépendantes, et c'est leur concordance qui vaut, pas chacune
    prise seule.

    1. la strate — dans combien de départements documentés cette année-là le
       paramètre est-il à 0 % ? Un retrait national les touche tous ;
    2. les communes réellement suivies — le paramètre figure-t-il parmi les
       abandons constatés d'un bulletin au suivant sur une même commune ? C'est
       le contrôle le plus serré, puisqu'il ne change ni de commune ni de
       corpus.
    """
    lignes = []

    strates = con.execute("""
        SELECT dept, pct_bulletins, nb_bulletins
        FROM v_parametre_presence_dept
        WHERE cle_param = ? AND annee = ?
        ORDER BY dept
    """, [cle_param, annee]).fetchall()
    if strates:
        zero = [d for d, pct, _ in strates if pct == 0]
        lignes.append(
            f"corpus   : 0 % dans {len(zero)} des {len(strates)} département(s) "
            f"documenté(s) en {annee} qui l'ont cherché au moins une fois"
            + (f" — {', '.join(zero)}" if zero else ""))

    suivi = con.execute("""
        SELECT nb_abandons, nb_communes
        FROM v_parametres_abandonnes WHERE cle_param = ?
    """, [cle_param]).fetchone()
    if suivi:
        lignes.append(
            f"communes : abandonné sur {suivi[0]} paire(s) de bulletins "
            f"consécutifs, dans {suivi[1]} commune(s) suivie(s)")
    else:
        lignes.append(
            "communes : aucune commune suivie ne l'abandonne d'un bulletin "
            "au suivant — la chute peut n'être qu'un effet de corpus")

    return lignes


def main():
    ap = argparse.ArgumentParser(description="journal des abandons de paramètres")
    ap.add_argument("--db", default=DB_PATH)
    ap.add_argument("--sortie", default=SORTIE)
    args = ap.parse_args()

    con = duckdb.connect(args.db, read_only=True)
    try:
        resumer(con)
        print()
        for nom, n in exporter(con, args.sortie):
            print(f"  écrit  {nom:<28} {n} ligne(s)")
        print(f"\ndans {args.sortie}")
        print("matériau d'étude, non versionné : il décrit ce qu'on a cherché,")
        print("jamais la qualité de l'eau.")
    finally:
        con.close()


if __name__ == "__main__":
    main()

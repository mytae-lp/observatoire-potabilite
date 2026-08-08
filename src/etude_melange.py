# -*- coding: utf-8 -*-
"""
Le dénombrement des mélanges — ce qu'un réseau moyenne avant le robinet.

    py -X utf8 src/etude_melange.py

Chantier C7 (docs/CHANTIERS.md), premier pas. Hypothèse de Yannick, 8 août 2026 :

    « si pour une commune on mélange 3 captages alors la moyenne peut être
    bonne, même si un captage est hors caractéristique. Cette hypothèse veut
    également dire que "on injecte des molécules chimiques en moyennant" plutôt
    que de fermer ou traiter un captage ! Je précise, ceci est une hypothèse et
    non une affirmation, il faut investiguer. »

Ce script n'instruit pas l'hypothèse : il dit si elle a un terrain. Il compte,
sur la base actuelle et sans aucune collecte nouvelle, les mélanges que la
donnée rend déjà lisibles — c'est-à-dire les réseaux qu'une installation
n'alimente pas seule.

C'est un MATÉRIAU D'ÉTUDE, pas une sortie publique, au même titre que
`etude_panel.py`. Trois fichiers dans `data/etudes/`, non versionnés :

    melange_reseaux.csv    un réseau par ligne : sources connues, part non
                           attribuée, statut
    melange_bulletins.csv  un bulletin par ligne : les réseaux qu'il dessert et
                           à quelle part
    melange_sources.csv    pour les seuls réseaux mélangés, ce que chaque source
                           analysée apporte — avec son effort de recherche

Ce que le dénombrement ne peut pas voir, et qu'il ne faut pas lui faire dire
-----------------------------------------------------------------------------
1. Il voit le mélange ENTRE INSTALLATIONS, jamais entre captages. Une usine
   alimentée par trois forages dont un seul est dégradé apparaît comme une
   source unique à 100 % : la dilution y est faite en amont du seul point que la
   donnée expose. Le maillon captage → usine n'est pas publié par Hub'Eau.
2. Une part absente n'est pas 100 %. Le champ disparaît quand la source ne
   rattache le prélèvement à aucune installation amont ; `non_declare` est un
   troisième état, comme l'indéterminé du §2.4.
3. Diluer est légal, et c'est ce qui rend la question intéressante : elle est
   posée à la norme, qui note l'eau distribuée sans rien demander sur ce qu'on
   y a mêlé — jamais à l'exploitant qui l'applique (§2.1).

Voir docs/METHODE_DILUTION.md pour la lecture du champ et ses réserves.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import duckdb  # noqa: E402
from common import DB_PATH  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "data", "etudes")

# Ce que chaque source analysée apporte au réseau qu'elle partage. L'effort de
# recherche et la couverture y sont OBLIGATOIRES : comparer deux bulletins sans
# eux est un contresens (CLAUDE.md §2.11), et ici les deux termes comparés sont
# précisément deux bulletins.
SOURCES_SQL = """
    SELECT r.code_reseau,
           r.nom_reseau,
           r.statut_melange,
           r.part_non_attribuee,
           b.part_reseau_pct         AS part_de_cette_source,
           b.nom_installation_amont  AS installation,
           v.commune, v.dept, v.date_prelevement, v.code_prelevement,
           v.nb_parametres, v.classe_effort, v.pct_couverture,
           v.nb_mesures_notees,
           v.nb_depasse_applicable, v.depassements_pour_mille,
           v.nb_bascules, v.nb_indetermines,
           v.synthese_quantifiees_pour_mille,
           v.conclusion_conformite
    FROM v_melange_reseau r
    JOIN v_reseau_bulletin b       ON b.code_reseau = r.code_reseau
    JOIN v_prelevement_verdict v   ON v.code_prelevement = b.code_prelevement
    WHERE r.melange_lisible AND v.est_complet
    ORDER BY r.nom_reseau, b.part_reseau_pct DESC NULLS LAST
"""

EXPORTS = [
    ("melange_reseaux.csv", "SELECT * FROM v_melange_reseau"),
    ("melange_bulletins.csv", "SELECT * FROM v_melange_bulletin ORDER BY commune, date_prelevement"),
    ("melange_sources.csv", SOURCES_SQL),
]

LIBELLES_STATUT = {
    "melange_reconstitue": "mélange reconstitué — toutes les parts sont connues",
    "melange_partiel": "mélange partiel — une part vient d'ailleurs, non identifiée",
    "source_unique_declaree": "une seule installation déclarée, à 100 %",
    "non_declare": "aucune part déclarée — on ne sait pas s'il y a mélange",
    "incoherent": "somme des parts supérieure à 100 % — à vérifier à la main",
}


def exporter(con, dossier):
    os.makedirs(dossier, exist_ok=True)
    ecrits = []
    for nom, requete in EXPORTS:
        chemin = os.path.join(dossier, nom)
        # Le dépôt vit dans un dossier nommé « …qualité de l'eau en France ».
        # L'apostrophe fermerait la chaîne SQL du COPY : elle se double.
        con.execute(f"COPY ({requete}) TO '{chemin.replace(chr(39), chr(39) * 2)}' "
                    "(HEADER, DELIMITER ';', QUOTE '\"')")
        n = con.execute(f"SELECT COUNT(*) FROM ({requete})").fetchone()[0]
        ecrits.append((nom, n))
    return ecrits


def controler(con):
    """Les prélèvements que la décomposition n'a pas su lire. Doit rester vide."""
    illisibles = con.execute("SELECT COUNT(*) FROM v_reseaux_illisibles").fetchone()[0]
    if illisibles:
        print(f"  ! {illisibles} prélèvement(s) dont les listes de codes et de noms de")
        print("    réseaux n'ont pas la même longueur : l'appariement par position")
        print("    collerait un nom au mauvais code. Ils sont ÉCARTÉS du dénombrement.")
        for r in con.execute("""
            SELECT code_prelevement, nb_codes, nb_noms, noms_reseaux
            FROM v_reseaux_illisibles LIMIT 5
        """).fetchall():
            print(f"      {r[0]} : {r[1]} code(s), {r[2]} nom(s) — {r[3]}")
        print()
    return illisibles


def resumer(con):
    reseaux, melanges = con.execute("""
        SELECT COUNT(*), COUNT(*) FILTER (WHERE melange_lisible) FROM v_melange_reseau
    """).fetchone()
    if not reseaux:
        print("\naucun réseau en base : rien à dénombrer.")
        return

    bulletins, b_melanges, b_muets = con.execute("""
        SELECT COUNT(*), COUNT(*) FILTER (WHERE melange_lisible),
               COUNT(*) FILTER (WHERE nb_parts_declarees = 0)
        FROM v_melange_bulletin
    """).fetchone()

    print(f"\n=== {reseaux} réseau(x) desservis par {bulletins} bulletin(s) ===\n")
    for statut, n, communes in con.execute("""
        SELECT statut_melange, COUNT(*), SUM(nb_communes)
        FROM v_melange_reseau GROUP BY 1 ORDER BY 2 DESC
    """).fetchall():
        print(f"  {n:>3} réseau(x), {communes:>3} commune(s)   "
              f"{LIBELLES_STATUT.get(statut, statut)}")

    print(f"\n  {melanges} réseau(x) sur {reseaux} portent un mélange LISIBLE ;")
    print(f"  {b_muets} bulletin(s) sur {bulletins} ne déclarent aucune part — ")
    print("  pour ceux-là on ignore jusqu'à l'existence du mélange.")

    print("\n=== les mélanges lisibles, et ce qu'on ignore de chacun ===\n")
    for r in con.execute("""
        SELECT nom_reseau, code_reseau, statut_melange, part_non_attribuee,
               nb_communes, sources
        FROM v_melange_reseau WHERE melange_lisible
        ORDER BY part_non_attribuee DESC, nom_reseau
    """).fetchall():
        print(f"  {r[0]} ({r[1]}) — {r[4]} commune(s) du corpus")
        print(f"      {LIBELLES_STATUT.get(r[2], r[2])}")
        print(f"      sources connues : {r[5]}")
        if r[3]:
            print(f"      → {r[3]:g} % du débit vient d'une installation que le corpus "
                  "ne connaît pas")
        print()

    # Le terrain de l'hypothèse : les réseaux dont PLUSIEURS sources sont
    # analysées. C'est là, et seulement là, qu'on peut voir ce que chacune
    # apporte au mélange. Ailleurs, le mélange est su mais pas observable.
    terrain = con.execute("""
        SELECT nom_reseau, code_reseau, nb_sources_analysees, sources
        FROM v_melange_reseau
        WHERE melange_lisible AND nb_sources_analysees >= 2
        ORDER BY nom_reseau
    """).fetchall()
    print("=== là où l'hypothèse devient instruisible ===\n")
    if not terrain:
        print("  aucun réseau mélangé ne porte de bulletin complet sur plus d'une")
        print("  de ses sources : le mélange est lisible, ce qu'il mélange ne l'est pas.")
    for nom, code, n, sources in terrain:
        print(f"  {nom} ({code}) — {n} sources analysées : {sources}")
        for s in con.execute(f"SELECT * FROM ({SOURCES_SQL}) WHERE code_reseau = ?",
                             [code]).fetchall():
            part = f"{s[4]:g} %" if s[4] is not None else "part non déclarée"
            print(f"      {part:>18}  {s[5] or '(installation non renseignée)'}")
            print(f"      {'':>18}  {s[6]} {s[8]} — {s[10]} paramètres ({s[11]}), "
                  f"couverture {s[12]} %")
            print(f"      {'':>18}  {s[14]} dépassement(s) applicable(s), "
                  f"{s[15]} pour mille notés, {s[16]} bascule(s), "
                  f"{s[17]} indéterminé(s)")
        print()
    if terrain:
        print("  Ces chiffres se lisent AVEC leur effort de recherche : deux bulletins")
        print("  qui ne cherchent pas le même nombre de paramètres n'ont pas la même")
        print("  chance de trouver (§2.11). Et un écart entre deux sources n'est pas")
        print("  une preuve de dilution : c'est ce qui rend l'hypothèse instruisible,")
        print("  pas ce qui la démontre.")

    print("\n=== ce que ce dénombrement ne voit pas ===\n")
    print("  Le mélange à l'intérieur d'une installation. Une usine alimentée par")
    print("  trois captages dont un seul est dégradé compte ici pour une source")
    print("  unique à 100 % : la dilution y est déjà faite, en amont du seul point")
    print("  que la donnée expose. Le lien captage → usine n'est pas publié par")
    print("  Hub'Eau et ne pourra être établi que par inférence géographique —")
    print("  donc affiché comme une hypothèse, jamais comme un fait (§7bis).")


def main():
    ap = argparse.ArgumentParser(description="dénombrement des mélanges de réseaux")
    ap.add_argument("--db", default=DB_PATH)
    ap.add_argument("--sortie", default=SORTIE)
    args = ap.parse_args()

    con = duckdb.connect(args.db, read_only=True)
    try:
        controler(con)
        resumer(con)
        print()
        for nom, n in exporter(con, args.sortie):
            print(f"  écrit  {nom:<26} {n} ligne(s)")
        print(f"\ndans {args.sortie}")
        print("matériau d'étude, non versionné. Il décrit ce que la donnée laisse")
        print("voir du mélange, jamais la qualité de l'eau qui en sort.")
    finally:
        con.close()


if __name__ == "__main__":
    main()

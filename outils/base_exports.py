# -*- coding: utf-8 -*-
"""
Base locale des exports PUBLIÉS — lecture seule sur la production.

    py -X utf8 outils/base_exports.py --construire
    py -X utf8 outils/base_exports.py --etat

Pourquoi ce script existe
-------------------------
La campagne départementale tourne sur le VPS, et `data/eau.duckdb` est sa
sauvegarde : DuckDB n'a qu'un seul écrivain, et l'ouvrir pendant qu'un figeage
écrit serait exactement le piège du §8 de `docs/EXPLOITATION.md`. Or on a
besoin d'interroger le corpus en local pour préparer des dossiers.

La sortie de secours est celle que le projet publie déjà : les exports ODbL de
`site/public/donnees/`, rapatriés dans `exports-a-rapatrier/`. Ils portent
exactement la surface que le §8bis autorise à consommer — `analyses_figees`,
`verdicts_figes`, `couverture_communes` — c'est-à-dire des lignes FIGÉES, qui
disent contre quelle version de référentiel elles ont été calculées. Rien n'est
recalculé ici : ce script charge, il ne juge pas.

Ce que cette base N'EST PAS
---------------------------
  · **pas une seconde production.** Elle est dérivée d'une copie datée d'un
    export, elle n'a ni `mesures` ni `prelevements`, on ne fige rien dedans ;
  · **pas à jour.** Elle vaut à la date de `COPIE-PRISE-LE.txt`, et la campagne
    avance sans elle. Toute reprise commence par un nouveau rapatriement ;
  · **pas le corpus entier.** L'export est filtré aux départements publiés
    (`site/build_site.py::_filtre_dept`). Ce qui est moissonné mais pas encore
    figé n'y est pas — et ça se voit dans `--etat`.

Garde-fou dur : le script REFUSE d'écrire sur `data/eau.duckdb`.
"""
import argparse
import csv
import gzip
import os
import sys
import time

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.abspath(os.path.join(RACINE, "..", "..", "exports-a-rapatrier"))
BASE = os.path.join(RACINE, "data", "exports_publies.duckdb")
INTERDIT = os.path.join(RACINE, "data", "eau.duckdb")

# --------------------------------------------------------------------------
# Les schémas, écrits en clair.
#
# Le sniffeur de DuckDB conviendrait presque, mais « presque » ne suffit pas :
# une colonne vide dans un département et numérique dans un autre se lirait
# VARCHAR ici et DOUBLE là, et la comparaison de seuils échouerait en silence
# (§2.9 transposé au chargement). On déclare donc, et un en-tête qui ne
# correspond plus fait échouer le chargement au lieu de décaler les colonnes
# — c'est la leçon du `controler_forme` de `build_db.py` (§5).
#
# Les booléens sont écrits 0/1 par l'export (`build_site.py::_cellule`) : ils
# se lisent en TINYINT puis se convertissent, DuckDB ne prenant pas « 1 » pour
# un BOOLEAN.
# --------------------------------------------------------------------------

BULLETINS = [
    ("code_prelevement", "VARCHAR"), ("version_referentiel", "VARCHAR"),
    ("calcule_le", "DATE"), ("code_insee", "VARCHAR"), ("commune", "VARCHAR"),
    ("dept", "VARCHAR"), ("codes_postaux", "VARCHAR"), ("lon", "DOUBLE"),
    ("lat", "DOUBLE"), ("date_prelevement", "DATE"),
    ("code_installation_amont", "VARCHAR"), ("nom_installation_amont", "VARCHAR"),
    ("nom_uge", "VARCHAR"), ("noms_reseaux", "VARCHAR"),
    ("nb_parametres", "BIGINT"), ("classe_effort", "VARCHAR"),
    ("nb_synthese_recherchees", "BIGINT"), ("est_complet", "TINYINT"),
    ("nb_mesures_lues", "BIGINT"), ("nb_mesures_notees", "BIGINT"),
    ("pct_couverture", "DOUBLE"), ("nb_notees_referentiel", "BIGINT"),
    ("nb_notees_declare", "BIGINT"), ("nb_depasse_2016", "BIGINT"),
    ("nb_depasse_2026", "BIGINT"), ("nb_depasse_strict", "BIGINT"),
    ("nb_depasse_futur", "BIGINT"), ("nb_bascules", "BIGINT"),
    ("nb_indetermines", "BIGINT"), ("nb_aveugles", "BIGINT"),
    ("nb_depasse_limite", "BIGINT"), ("nb_au_dessus_vigilance", "BIGINT"),
    ("nb_hors_reference", "BIGINT"), ("nb_sous_reference", "BIGINT"),
    ("nb_ecarts_seuil", "BIGINT"), ("nb_depasse_applicable", "BIGINT"),
    ("nb_bascules_datees", "BIGINT"), ("depassements_pour_mille", "DOUBLE"),
    ("aveugles_pour_mille", "DOUBLE"), ("synthese_quantifiees_pour_mille", "DOUBLE"),
    ("nb_synthese_quantifiees", "BIGINT"), ("charge_synthese_ug_l", "DOUBLE"),
    ("somme_pesticides_declaree", "DOUBLE"), ("somme_pesticides_recalculee", "DOUBLE"),
    ("indice_danger", "DOUBLE"), ("indice_danger_n", "BIGINT"),
    ("conclusion_conformite", "VARCHAR"), ("source_url", "VARCHAR"),
]
BULLETINS_BOOL = {"est_complet"}

VERDICTS = [
    ("code_prelevement", "VARCHAR"), ("version_referentiel", "VARCHAR"),
    ("libelle_parametre", "VARCHAR"), ("code_parametre", "VARCHAR"),
    ("code_cas", "VARCHAR"), ("famille", "VARCHAR"),
    ("mode_appariement", "VARCHAR"), ("resultat_num", "DOUBLE"),
    ("lq", "DOUBLE"), ("est_quantifie", "TINYINT"), ("unite", "VARCHAR"),
    ("seuil_2016", "DOUBLE"), ("seuil_2026_effectif", "DOUBLE"),
    ("origine_seuil_2026", "VARCHAR"), ("seuil_strict", "DOUBLE"),
    ("seuil_futur", "DOUBLE"), ("seuil_applicable", "DOUBLE"),
    ("grille_applicable", "VARCHAR"), ("attribution", "VARCHAR"),
    ("depasse_2016", "TINYINT"), ("depasse_2026", "TINYINT"),
    ("depasse_applicable", "TINYINT"), ("depasse_strict", "TINYINT"),
    ("depasse_futur", "TINYINT"), ("bascule_2016_2026", "TINYINT"),
    ("bascule_datee", "TINYINT"), ("indetermine_strict", "TINYINT"),
    ("indetermine_condition", "TINYINT"), ("lq_aveugle", "TINYINT"),
    ("lq_rapport_seuil", "DOUBLE"), ("nature_seuil", "VARCHAR"),
    ("hors_reference", "TINYINT"), ("sens_hors_reference", "VARCHAR"),
    ("reference_min", "DOUBLE"), ("reference_max", "DOUBLE"),
    ("pe_reglementaire", "VARCHAR"), ("pe_scientifique", "VARCHAR"),
    ("est_agregat", "TINYINT"), ("fiabilite", "VARCHAR"),
]
VERDICTS_BOOL = {"est_quantifie", "depasse_2016", "depasse_2026",
                 "depasse_applicable", "depasse_strict", "depasse_futur",
                 "bascule_2016_2026", "bascule_datee", "indetermine_strict",
                 "indetermine_condition", "lq_aveugle", "hors_reference",
                 "est_agregat"}

COUVERTURE = [
    ("code_insee", "VARCHAR"), ("version_referentiel", "VARCHAR"),
    ("calcule_le", "DATE"), ("commune", "VARCHAR"), ("dept", "VARCHAR"),
    ("codes_postaux", "VARCHAR"), ("lon", "DOUBLE"), ("lat", "DOUBLE"),
    ("statut", "VARCHAR"), ("code_prelevement", "VARCHAR"),
    ("commune_prelevement", "VARCHAR"), ("date_prelevement", "DATE"),
    ("nb_parametres", "BIGINT"), ("pct_couverture", "DOUBLE"),
]

LQ_CORPUS = [
    ("version_referentiel", "VARCHAR"), ("calcule_le", "DATE"),
    ("cle_param", "VARCHAR"), ("libelle_parametre", "VARCHAR"),
    ("unite", "VARCHAR"), ("lq_min", "DOUBLE"), ("lq_max", "DOUBLE"),
    ("lq_mediane", "DOUBLE"), ("nb_mesures", "BIGINT"),
    ("nb_bulletins", "BIGINT"), ("nb_departements", "BIGINT"),
]

REFERENTIEL = [
    ("code_parametre", "VARCHAR"), ("code_cas", "VARCHAR"),
    ("libelle", "VARCHAR"), ("famille", "VARCHAR"), ("unite", "VARCHAR"),
    ("seuil_2016", "DOUBLE"), ("seuil_2026", "DOUBLE"),
    ("date_applicabilite_2026", "VARCHAR"), ("seuil_conditionnel", "DOUBLE"),
    ("condition_seuil", "VARCHAR"), ("statut_2026", "VARCHAR"),
    ("seuil_futur", "DOUBLE"), ("date_applicabilite_futur", "VARCHAR"),
    ("seuil_strict", "DOUBLE"), ("base_seuil_strict", "VARCHAR"),
    ("pe_reglementaire", "VARCHAR"), ("pe_scientifique", "VARCHAR"),
    # `est_agregat` est ecrit « oui »/« non » dans le referentiel source, la ou
    # l'export figé l'ecrit 0/1 : deux fichiers, deux conventions, aucune
    # conversion inventee ici.
    ("sources", "VARCHAR"), ("fiabilite", "VARCHAR"), ("est_agregat", "VARCHAR"),
    ("cancerogenicite_circ", "VARCHAR"),
]
REFERENTIEL_BOOL = frozenset()


def _controler_entete(chemin, attendu, ouvrir):
    """Un en-tête qui a bougé fait échouer le chargement — jamais un décalage
    silencieux de colonnes (§5)."""
    with ouvrir(chemin) as fh:
        lu = next(csv.reader(fh, delimiter=";"))
    lu = [c.lstrip("﻿") for c in lu]
    if lu != [c for c, _ in attendu]:
        manquantes = sorted(set(c for c, _ in attendu) - set(lu))
        nouvelles = sorted(set(lu) - set(c for c, _ in attendu))
        raise SystemExit(
            "ARRÊT — l'en-tête de %s ne correspond pas au schéma attendu.\n"
            "  absentes : %s\n  inconnues : %s\n"
            "L'export a changé de forme : mettre à jour outils/base_exports.py."
            % (os.path.basename(chemin), manquantes or "—", nouvelles or "—"))


def _lecture(chemin, colonnes):
    # L'apostrophe de « …de l'eau en France… » est dans le chemin du dossier de
    # travail : sans doublement elle ferme le littéral SQL.
    litteral = chemin.replace("\\", "/").replace("'", "''")
    spec = ", ".join("'%s': '%s'" % (c, t) for c, t in colonnes)
    return ("read_csv('%s', delim=';', header=true, columns={%s}, "
            "ignore_errors=false)" % (litteral, spec))


def _projection(colonnes, booleens, extra=""):
    bouts = [("CAST(%s AS BOOLEAN) AS %s" % (c, c) if c in booleens else c)
             for c, _ in colonnes]
    return ", ".join(bouts) + extra


def charger(con, nom, fichier, colonnes, booleens=frozenset()):
    chemin = os.path.join(EXPORTS, fichier)
    if not os.path.exists(chemin):
        raise SystemExit("ARRÊT — %s est absent." % chemin)
    _controler_entete(chemin, colonnes,
                      lambda p: open(p, encoding="utf-8-sig", newline=""))
    t = time.time()
    con.execute("CREATE OR REPLACE TABLE %s AS SELECT %s FROM %s"
                % (nom, _projection(colonnes, booleens), _lecture(chemin, colonnes)))
    n = con.execute("SELECT count(*) FROM %s" % nom).fetchone()[0]
    print(("  %-22s %10s lignes   %5.1f s" % (nom, "{:,}".format(n), time.time() - t))
          .replace(",", " "))
    return n


def charger_verdicts(con):
    """Le détail, découpé par département à l'export. Le nom du fichier PORTE
    le département — celui de la commune du prélèvement, pas de celle qui
    l'emprunte (`build_site.py::exporter`) : on le garde en colonne, sans quoi
    toute question départementale imposerait une jointure sur des dizaines de
    millions de lignes.
    """
    fichiers = sorted(f for f in os.listdir(EXPORTS)
                      if f.startswith("verdicts_") and f.endswith(".csv.gz"))
    if not fichiers:
        raise SystemExit("ARRÊT — aucun verdicts_*.csv.gz dans " + EXPORTS)
    _controler_entete(os.path.join(EXPORTS, fichiers[0]), VERDICTS,
                      lambda p: gzip.open(p, "rt", encoding="utf-8-sig", newline=""))
    con.execute("DROP TABLE IF EXISTS verdicts")
    total, t = 0, time.time()
    for i, f in enumerate(fichiers):
        dept = f[len("verdicts_"):-len(".csv.gz")]
        chemin = os.path.join(EXPORTS, f)
        sel = _projection(VERDICTS, VERDICTS_BOOL, ", '%s' AS dept" % dept)
        verbe = ("CREATE TABLE verdicts AS SELECT" if i == 0
                 else "INSERT INTO verdicts SELECT")
        con.execute("%s %s FROM %s" % (verbe, sel, _lecture(chemin, VERDICTS)))
        total = con.execute("SELECT count(*) FROM verdicts").fetchone()[0]
        print(("  verdicts %s : %12s lignes cumulées"
               % (dept, "{:,}".format(total))).replace(",", " "), end="\r")
    print(("  %-22s %10s lignes   %5.1f s"
           % ("verdicts", "{:,}".format(total), time.time() - t)).replace(",", " ")
          + " " * 20)
    return total


def charger_departements(con):
    """`departements_publies.csv` porte des lignes de commentaire `#` — la
    source de vérité de ce qui est collecté EN ENTIER, à ne pas confondre avec
    ce qui est figé (voir --etat)."""
    chemin = os.path.join(EXPORTS, "departements_publies.csv")
    lignes = []
    with open(chemin, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            code = (r.get("code") or "").strip()
            if code and not code.startswith("#"):
                lignes.append((code, r["nom"], r["collecte_terminee_le"],
                               int(r["communes"])))
    con.execute("CREATE OR REPLACE TABLE departements_publies (code VARCHAR, "
                "nom VARCHAR, collecte_terminee_le DATE, communes BIGINT)")
    con.executemany("INSERT INTO departements_publies VALUES (?, ?, ?, ?)", lignes)
    print("  %-22s %10d lignes" % ("departements_publies", len(lignes)))


def construire_bascules(con):
    """Le résumé des bascules par bulletin, matérialisé.

    Deux raisons de ne pas en faire une vue : 18,8 M de lignes se rescanneraient
    à chaque question posée, et surtout la distinction du §2.12 — limite de 2016
    lue dans un texte de l'époque, ou extrapolée de l'instruction de décembre
    2020 — doit être calculée UNE fois, au même endroit, sinon deux copies de la
    règle divergent à la première retouche.
    """
    con.execute("""
        CREATE OR REPLACE TABLE bascules_par_bulletin AS
        SELECT code_prelevement,
               count(*)                                          AS nb_bascules,
               count(*) FILTER (WHERE bascule_datee)             AS nb_bascules_datees,
               count(*) FILTER (WHERE famille <> 'metabolite')   AS nb_bascules_non_extrapolees,
               count(*) FILTER (WHERE bascule_datee AND famille <> 'metabolite')
                                                 AS nb_bascules_datees_non_extrapolees,
               string_agg(DISTINCT libelle_parametre, ', ')      AS substances_qui_basculent
        FROM verdicts WHERE bascule_2016_2026 GROUP BY 1""")
    n = con.execute("SELECT count(*) FROM bascules_par_bulletin").fetchone()[0]
    print(("  %-22s %10s lignes" % ("bascules_par_bulletin", "{:,}".format(n)))
          .replace(",", " "))


VUES = """
-- ------------------------------------------------------------------------
-- Les vues d'exploration. Elles n'ajoutent AUCUN calcul de verdict : tout ce
-- qu'elles portent vient des lignes figées. Elles regroupent, elles situent,
-- elles ne jugent pas.
-- ------------------------------------------------------------------------

-- Le dernier bulletin COMPLET de chaque commune (§2.3 : jamais de profil
-- synthétique, l'unité est le code_prelevement). Une commune sans bulletin
-- complet n'y figure pas — elle se lit dans `couverture_communes`.
CREATE OR REPLACE VIEW v_dernier_complet AS
SELECT * EXCLUDE (rang) FROM (
    SELECT b.*, row_number() OVER (
               PARTITION BY b.code_insee
               ORDER BY b.date_prelevement DESC, b.code_prelevement DESC) AS rang
    FROM bulletins b WHERE b.est_complet
) WHERE rang = 1
;
-- L'effort de recherche du département, terme de comparaison par défaut
-- (§2.11, quatrième règle : un département se compare à lui-même). À afficher
-- à côté de TOUT classement — un taux, jamais un compte.
CREATE OR REPLACE VIEW v_effort_dept AS
SELECT dept,
       count(*)                                    AS nb_communes_completes,
       median(nb_parametres)                       AS med_nb_parametres,
       median(pct_couverture)                      AS med_pct_couverture,
       median(depassements_pour_mille)             AS med_depassements_pm,
       median(aveugles_pour_mille)                 AS med_aveugles_pm,
       quantile_cont(aveugles_pour_mille, 0.9)     AS p90_aveugles_pm,
       median(nb_bascules)                         AS med_bascules
FROM v_dernier_complet GROUP BY dept
;
-- LA REQUÊTE QUI PORTE LA THÈSE (CLAUDE.md §6), servie telle quelle.
-- Conforme à la date, et qui ne l'aurait pas été il y a dix ans.
CREATE OR REPLACE VIEW v_these AS
SELECT code_insee, commune, dept, date_prelevement, nb_parametres,
       pct_couverture, nb_bascules, nb_bascules_datees, nb_indetermines,
       nb_aveugles, aveugles_pour_mille, conclusion_conformite, code_prelevement
FROM v_dernier_complet
WHERE nb_depasse_applicable = 0 AND nb_bascules > 0
;
-- Le détail des bascules, substance par substance. DEUX qualités distinctes,
-- qui ne se déduisent pas l'une de l'autre et qu'on ne doit pas confondre :
--
--   · `bascule_datee` (src/build_db.py, « BASCULE DATÉE ») dit que le
--     prélèvement est POSTÉRIEUR au jour où la limite a bougé — la même valeur,
--     la veille, n'était pas conforme. C'est la datation au jour près (§2.10) ;
--   · `seuil_2016_extrapole` dit d'où vient la limite de 2016 elle-même. Sur
--     les métabolites elle est extrapolée de l'instruction DGS/EA4/2020/177 de
--     décembre 2020, pas lue dans un texte de 2016 (§2.12) — et cela DOIT se
--     dire partout où la grille 2016 est invoquée sur un métabolite.
--
-- Une bascule peut donc être datée ET reposer sur un seuil 2016 extrapolé.
-- Les deux ensemble — datée et non extrapolée — donnent l'énoncé littéral,
-- celui de l'exemple d'Auneau-Bleury-Saint-Symphorien (28015) du CLAUDE.md.
CREATE OR REPLACE VIEW v_bascules_detail AS
SELECT b.code_insee, b.commune, b.dept, b.date_prelevement,
       v.libelle_parametre, v.famille, v.resultat_num, v.unite,
       v.seuil_2016, v.seuil_2026_effectif, v.origine_seuil_2026,
       v.bascule_datee,
       (v.famille = 'metabolite') AS seuil_2016_extrapole,
       v.est_quantifie, v.fiabilite, v.code_prelevement
FROM verdicts v JOIN bulletins b USING (code_prelevement)
WHERE v.bascule_2016_2026
;
-- Ce qui n'a PAS pu être vu : la LQ du laboratoire est au-dessus du seuil de
-- comparaison (§2.4, §8bis obligation 11). Ce n'est pas une négligence, c'est
-- une capacité d'instrument (§2.1).
CREATE OR REPLACE VIEW v_aveugles_detail AS
SELECT b.code_insee, b.commune, b.dept, b.date_prelevement,
       v.libelle_parametre, v.famille, v.lq, v.seuil_applicable,
       v.lq_rapport_seuil, v.unite, v.code_prelevement
FROM verdicts v JOIN bulletins b USING (code_prelevement)
WHERE v.lq_aveugle
;
-- LES CANDIDATS À UN DOSSIER. Aucune note d'ensemble, aucun score composite :
-- cinq axes lisibles séparément, chacun avec l'effort de son bulletin et la
-- médiane de son département à côté (§2.11). Le tri est le geste de l'humain.
CREATE OR REPLACE VIEW v_candidats_dossier AS
SELECT d.code_insee, d.commune, d.dept, d.date_prelevement,
       d.nb_parametres, d.classe_effort, d.pct_couverture,
       e.med_nb_parametres AS dept_med_nb_parametres,
       e.med_pct_couverture AS dept_med_pct_couverture,
       e.nb_communes_completes AS dept_nb_communes,
       -- axe 1 — la thèse. `axe_these_litterale` est le cas fort : conforme à
       -- la date, bascule datée, ET limite de 2016 réellement lue dans un texte
       -- de l'époque (§2.12). `axe_these_datee` est le cas large, qui reste
       -- vrai mais dont l'énoncé doit porter la mention d'extrapolation.
       (d.nb_depasse_applicable = 0 AND d.nb_bascules_datees > 0) AS axe_these_datee,
       (d.nb_depasse_applicable = 0
        AND coalesce(x.nb_bascules_datees_non_extrapolees, 0) > 0) AS axe_these_litterale,
       d.nb_bascules_datees, d.nb_bascules,
       coalesce(x.nb_bascules_datees_non_extrapolees, 0)
           AS nb_bascules_datees_non_extrapolees,
       x.substances_qui_basculent,
       -- axe 2 — le verdict administratif du jour, à traiter à part
       d.nb_depasse_applicable, d.depassements_pour_mille,
       e.med_depassements_pm AS dept_med_depassements_pm,
       -- axe 3 — ce que l'analyse ne pouvait pas voir
       d.nb_aveugles, d.aveugles_pour_mille,
       e.med_aveugles_pm AS dept_med_aveugles_pm,
       e.p90_aveugles_pm AS dept_p90_aveugles_pm,
       -- axe 4 — notre seuil contredit la limite déclarée par la source (§2.8)
       d.nb_ecarts_seuil,
       -- axe 5 — les indéterminés, troisième état jamais replié sur conforme
       d.nb_indetermines,
       -- effet cocktail : indicatif SEULEMENT, jamais nommé « risque », jamais
       -- publié sans indice_danger_n (§7.1)
       d.indice_danger, d.indice_danger_n,
       d.conclusion_conformite, d.code_prelevement, d.source_url
FROM v_dernier_complet d
JOIN v_effort_dept e USING (dept)
LEFT JOIN bascules_par_bulletin x USING (code_prelevement)
"""


def construire():
    if os.path.realpath(BASE) == os.path.realpath(INTERDIT):
        raise SystemExit("ARRÊT — cette base ne doit jamais être data/eau.duckdb.")
    if os.path.exists(BASE + ".wal"):
        raise SystemExit("ARRÊT — %s.wal existe : un autre processus l'écrit." % BASE)
    print("exports : %s" % EXPORTS)
    print("base    : %s\n" % BASE)
    con = duckdb.connect(BASE)
    con.execute("SET preserve_insertion_order = false")
    charger(con, "bulletins", "bulletins.csv", BULLETINS, BULLETINS_BOOL)
    charger(con, "couverture_communes", "couverture_communes.csv", COUVERTURE)
    charger(con, "lq_corpus", "lq_corpus.csv", LQ_CORPUS)
    charger(con, "referentiel_seuils", "referentiel_seuils.csv", REFERENTIEL,
            REFERENTIEL_BOOL)
    charger_departements(con)
    charger_verdicts(con)
    construire_bascules(con)

    # La traçabilité, obligation 9 du §8bis : d'où vient cette base, prise
    # quand, contre quelle version de référentiel.
    with open(os.path.join(EXPORTS, "COPIE-PRISE-LE.txt"), encoding="utf-8-sig") as fh:
        copie = fh.read().strip()
    con.execute(
        "CREATE OR REPLACE TABLE provenance AS SELECT ? AS source, "
        "? AS copie_prise_le, ? AS chargee_le, "
        "(SELECT string_agg(DISTINCT version_referentiel, '|') FROM bulletins) "
        "AS version_referentiel",
        [EXPORTS, copie, time.strftime("%Y-%m-%dT%H:%M:%S")])
    for ordre in VUES.split("\n;"):
        if ordre.strip():
            con.execute(ordre)
    print("\n  vues : v_dernier_complet, v_effort_dept, v_these, v_bascules_detail,"
          "\n         v_aveugles_detail, v_candidats_dossier")
    con.close()
    etat()


def candidats(chemin=None):
    """La table des candidats, sortie en CSV pour être triée à la main.

    Elle ne classe rien : elle pose cote à cote, pour chaque commune, son
    dernier bulletin complet, les cinq axes, et l'effort de recherche de son
    propre département (§2.11). Le tri est un geste éditorial, pas un calcul —
    un score composite ferait disparaitre ce qui distingue les axes.
    """
    chemin = chemin or os.path.join(RACINE, "data", "etudes",
                                    "candidats_dossiers_%s.csv"
                                    % time.strftime("%Y-%m-%d"))
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    con = duckdb.connect(BASE, read_only=True)
    con.execute("COPY (SELECT * FROM v_candidats_dossier "
                "ORDER BY dept, commune) TO '%s' (HEADER, DELIMITER ';')"
                % chemin.replace("\\", "/").replace("'", "''"))
    n = con.execute("SELECT count(*) FROM v_candidats_dossier").fetchone()[0]
    con.close()
    print("%d communes -> %s" % (n, chemin))


def etat():
    con = duckdb.connect(BASE, read_only=True)
    p = con.execute("SELECT * FROM provenance").fetchone()
    print("\nprovenance   copie du VPS prise le %s, chargée le %s" % (p[1], p[2]))
    print("référentiel  %s" % p[3])
    for t in ("bulletins", "verdicts", "couverture_communes", "lq_corpus",
              "referentiel_seuils"):
        n = con.execute("SELECT count(*) FROM %s" % t).fetchone()[0]
        print(("  %-22s %12s" % (t, "{:,}".format(n))).replace(",", " "))
    figes, publies = con.execute(
        "SELECT (SELECT count(DISTINCT dept) FROM bulletins), "
        "(SELECT count(*) FROM departements_publies)").fetchone()
    print("\ndépartements  %d dans l'export figé, %d déclarés collectés en entier"
          % (figes, publies))
    manquants = con.execute("""
        SELECT string_agg(code || ' ' || nom, ', ' ORDER BY code)
        FROM departements_publies
        WHERE code NOT IN (SELECT DISTINCT dept FROM bulletins)""").fetchone()[0]
    if manquants:
        print("  collectés mais ABSENTS de l'export — moissonné n'est pas figé,\n"
              "  et seul le figé est citable (§6, règle 2) :\n  %s" % manquants)
    sans = con.execute("""
        SELECT string_agg(DISTINCT dept, ', ') FROM bulletins
        WHERE dept NOT IN (SELECT DISTINCT dept FROM verdicts)""").fetchone()[0]
    if sans:
        print("  bulletins sans fichier de détail : %s" % sans)
    con.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--construire", action="store_true", help="(re)construire la base")
    ap.add_argument("--etat", action="store_true", help="ce que la base contient")
    ap.add_argument("--candidats", nargs="?", const=True,
                    help="sortir la table des candidats en CSV")
    ap.add_argument("--vues", action="store_true",
                    help="refaire les seules vues, sans recharger les CSV")
    ap.add_argument("--exports", help="dossier des exports rapatriés")
    ap.add_argument("--base", help="chemin de la base à écrire")
    a = ap.parse_args()
    if a.exports:
        EXPORTS = os.path.abspath(a.exports)
    if a.base:
        BASE = os.path.abspath(a.base)
    if a.construire:
        construire()
    elif a.vues:
        con = duckdb.connect(BASE)
        construire_bascules(con)
        for ordre in VUES.split("\n;"):
            if ordre.strip():
                con.execute(ordre)
        con.close()
        print("vues refaites.")
    elif a.candidats:
        candidats(None if a.candidats is True else a.candidats)
    elif a.etat:
        etat()
    else:
        ap.print_help()
        sys.exit(1)

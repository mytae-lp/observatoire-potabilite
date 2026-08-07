# -*- coding: utf-8 -*-
"""
Fige le résultat de l'analyse dans la base.

    python3 src/figer.py                 # (re)fige tous les bulletins présents
    python3 src/figer.py --statut        # état de la couverture par commune

Pourquoi figer, et pourquoi estampiller
---------------------------------------
La MESURE ne change jamais : c'est un fait, elle est déjà en base. Le VERDICT,
lui, dépend du référentiel — et le sujet même du projet est que les seuils
bougent. Figer un « conforme » sans dire contre quelle grille il a été calculé
reproduirait, à l'intérieur de l'outil, exactement le défaut que l'outil
dénonce.

Chaque ligne figée porte donc :
  - `version_referentiel` : empreinte du contenu des fichiers du référentiel
    (seuils + alias + règles). Une empreinte de CONTENU, pas un commit git :
    une modification non commitée doit être visible, et git ne la verrait pas.
  - `calcule_le` : la date du calcul.

Refiger après modification du référentiel produit une nouvelle version ; la
comparaison de deux versions est la trace du déplacement des seuils.

Les sommes
----------
Voir docs/METHODE_EFFET_COCKTAIL.md, qui définit les trois indicateurs et
leurs limites. Ce module les calcule ; il ne les commente pas.
"""
import argparse
import datetime
import hashlib
import os
import sys

import duckdb

from common import DB_PATH, REF_CSV, ALIAS_CSV, RACINE

REGLES_CSV = os.path.join(RACINE, "referentiel", "regles_famille.csv")

# Familles considérées comme substances de synthèse pour la charge cumulée.
FAMILLES_SYNTHESE = ("pesticide", "metabolite", "PFAS", "organique")

SCHEMA_FIGE = """
CREATE TABLE IF NOT EXISTS analyses_figees (
    code_prelevement        VARCHAR,
    version_referentiel     VARCHAR,
    calcule_le              DATE,
    code_insee              VARCHAR,
    commune                 VARCHAR,
    dept                    VARCHAR,
    codes_postaux           VARCHAR,
    lon                     DOUBLE,
    lat                     DOUBLE,
    date_prelevement        DATE,
    code_installation_amont VARCHAR,
    nom_installation_amont  VARCHAR,
    nom_uge                 VARCHAR,
    noms_reseaux            VARCHAR,
    nb_parametres           INTEGER,
    est_complet             BOOLEAN,
    nb_mesures_lues         INTEGER,
    nb_mesures_notees       INTEGER,
    pct_couverture          DOUBLE,
    nb_notees_referentiel   INTEGER,
    nb_notees_declare       INTEGER,
    nb_depasse_2016         INTEGER,
    nb_depasse_2026         INTEGER,
    nb_depasse_strict       INTEGER,
    nb_depasse_futur        INTEGER,
    nb_bascules             INTEGER,
    nb_indetermines         INTEGER,
    nb_ecarts_seuil         INTEGER,
    nb_synthese_quantifiees INTEGER,
    charge_synthese_ug_l    DOUBLE,
    somme_pesticides_declaree   DOUBLE,
    somme_pesticides_recalculee DOUBLE,
    indice_danger           DOUBLE,
    indice_danger_n         INTEGER,
    conclusion_conformite   VARCHAR,
    source_url              VARCHAR,
    PRIMARY KEY (code_prelevement, version_referentiel)
);

CREATE TABLE IF NOT EXISTS verdicts_figes (
    code_prelevement    VARCHAR,
    version_referentiel VARCHAR,
    libelle_parametre   VARCHAR,
    code_parametre      VARCHAR,
    code_cas            VARCHAR,
    famille             VARCHAR,
    mode_appariement    VARCHAR,
    resultat_num        DOUBLE,
    lq                  DOUBLE,
    est_quantifie       BOOLEAN,
    unite               VARCHAR,
    seuil_2016          DOUBLE,
    seuil_2026_effectif DOUBLE,
    origine_seuil_2026  VARCHAR,
    seuil_strict        DOUBLE,
    seuil_futur         DOUBLE,
    depasse_2016        BOOLEAN,
    depasse_2026        BOOLEAN,
    depasse_strict      BOOLEAN,
    depasse_futur       BOOLEAN,
    bascule_2016_2026   BOOLEAN,
    indetermine_strict  BOOLEAN,
    fiabilite           VARCHAR,
    PRIMARY KEY (code_prelevement, version_referentiel, libelle_parametre)
);

CREATE TABLE IF NOT EXISTS couverture_communes (
    code_insee          VARCHAR,
    version_referentiel VARCHAR,
    calcule_le          DATE,
    commune             VARCHAR,
    dept                VARCHAR,
    codes_postaux       VARCHAR,
    lon                 DOUBLE,
    lat                 DOUBLE,
    statut              VARCHAR,   -- analysee | rattachee_reseau | non_documentee
    code_prelevement    VARCHAR,
    commune_prelevement VARCHAR,
    date_prelevement    DATE,
    nb_parametres       INTEGER,
    pct_couverture      DOUBLE,
    PRIMARY KEY (code_insee, version_referentiel)
);
"""


def version_referentiel():
    """
    Empreinte du contenu du référentiel : 12 caractères hexadécimaux.

    Empreinte de CONTENU et non de commit : le référentiel peut être modifié
    sans être commité, et un verdict figé contre une version non commitée doit
    rester identifiable.
    """
    h = hashlib.sha256()
    for chemin in (REF_CSV, ALIAS_CSV, REGLES_CSV):
        h.update(os.path.basename(chemin).encode())
        if os.path.exists(chemin):
            with open(chemin, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()[:12]


def _sommes(con, code_prel):
    """Les indicateurs de cumul d'un bulletin (cf. docs/METHODE_EFFET_COCKTAIL.md)."""
    familles = ", ".join(f"'{f}'" for f in FAMILLES_SYNTHESE)

    # A et B — dénombrement et charge massique, hors lignes agrégées pour ne
    # pas compter une somme en même temps que ses composants. Charge ramenée
    # en µg/L via la table des unités.
    a_b = con.execute(f"""
        SELECT COUNT(*),
               SUM(v.resultat_num * COALESCE(u.facteur, 1.0))
        FROM v_mesures_verdict v
        LEFT JOIN unites_masse u ON u.unite_norm = lower(replace(replace(v.unite,'µ','u'),' ',''))
        WHERE v.code_prelevement = ?
          AND v.est_quantifie
          AND v.famille IN ({familles})
          AND NOT v.est_agregat
    """, [code_prel]).fetchone()

    # Somme des pesticides : celle que le laboratoire déclare…
    declaree = con.execute("""
        SELECT resultat_num FROM v_mesures_verdict
        WHERE code_prelevement = ? AND est_agregat
          AND libelle_parametre ILIKE '%pesticide%'
        LIMIT 1
    """, [code_prel]).fetchone()

    # …et celle qu'on recalcule. Zéro de substitution sur les non-quantifiés :
    # le résultat est un PLANCHER, jamais une estimation centrale.
    recalculee = con.execute("""
        SELECT SUM(v.resultat_num * COALESCE(u.facteur, 1.0))
        FROM v_mesures_verdict v
        LEFT JOIN unites_masse u ON u.unite_norm = lower(replace(replace(v.unite,'µ','u'),' ',''))
        WHERE v.code_prelevement = ? AND v.est_quantifie AND NOT v.est_agregat
          AND v.famille IN ('pesticide', 'metabolite')
    """, [code_prel]).fetchone()

    # C — indice de danger. Raisonnement, pas mesure.
    #
    # Restreint aux MÊMES familles que A et B. Sans cette restriction, l'indice
    # est dominé par des minéraux naturellement présents — sur Ramonville, le
    # potassium, les chlorures, les sulfates et le sodium pesaient plus que tous
    # les micropolluants réunis et portaient le total au-dessus de 1. Additionner
    # une fraction de la référence en sodium à une fraction de la limite d'un
    # pesticide n'a aucun sens : ce ne sont pas les mêmes objets.
    #
    # Conséquence assumée : une substance dont la famille est inconnue (notée
    # par la seule limite déclarée) n'entre pas dans l'indice. L'indice porte
    # donc sur ce qui est classé, et `indice_danger_n` dit sur combien de
    # substances il est calculé — sans ce nombre, il n'est pas interprétable.
    hi = con.execute(f"""
        SELECT SUM(resultat_num / seuil_2026_effectif), COUNT(*)
        FROM v_mesures_verdict
        WHERE code_prelevement = ? AND est_quantifie AND NOT est_agregat
          AND famille IN ({familles})
          AND seuil_2026_effectif IS NOT NULL AND seuil_2026_effectif > 0
    """, [code_prel]).fetchone()

    return {
        "nb_synthese_quantifiees": a_b[0] or 0,
        "charge_synthese_ug_l": a_b[1],
        "somme_pesticides_declaree": declaree[0] if declaree else None,
        "somme_pesticides_recalculee": recalculee[0] if recalculee else None,
        "indice_danger": hi[0] if hi else None,
        "indice_danger_n": (hi[1] or 0) if hi else 0,
    }


def figer(con, version=None, calcule_le=None):
    """(Re)calcule et fige tous les bulletins présents en base."""
    con.execute(SCHEMA_FIGE)
    version = version or version_referentiel()
    jour = calcule_le or datetime.date.today().isoformat()

    prels = [r[0] for r in con.execute(
        "SELECT code_prelevement FROM v_prelevement_verdict ORDER BY 1").fetchall()]

    con.execute("DELETE FROM analyses_figees WHERE version_referentiel = ?", [version])
    con.execute("DELETE FROM verdicts_figes  WHERE version_referentiel = ?", [version])

    for cp in prels:
        s = _sommes(con, cp)
        con.execute("""
            INSERT INTO analyses_figees
            SELECT p.code_prelevement, ?, ?::DATE,
                   p.code_insee, p.commune, p.dept, p.codes_postaux, p.lon, p.lat,
                   p.date_prelevement, p.code_installation_amont,
                   p.nom_installation_amont, p.nom_uge, p.noms_reseaux,
                   p.nb_parametres, p.est_complet,
                   p.nb_mesures_lues, p.nb_mesures_notees, p.pct_couverture,
                   p.nb_notees_referentiel, p.nb_notees_declare,
                   p.nb_depasse_2016, p.nb_depasse_2026, p.nb_depasse_strict,
                   p.nb_depasse_futur, p.nb_bascules, p.nb_indetermines,
                   p.nb_ecarts_seuil,
                   ?, ?, ?, ?, ?, ?,
                   p.conclusion_conformite, pr.source_url
            FROM v_prelevement_verdict p
            JOIN prelevements pr ON pr.code_prelevement = p.code_prelevement
            WHERE p.code_prelevement = ?
        """, [version, jour,
              s["nb_synthese_quantifiees"], s["charge_synthese_ug_l"],
              s["somme_pesticides_declaree"], s["somme_pesticides_recalculee"],
              s["indice_danger"], s["indice_danger_n"], cp])

        con.execute("""
            INSERT INTO verdicts_figes
            SELECT code_prelevement, ?, libelle_parametre, code_parametre, code_cas,
                   famille, mode_appariement, resultat_num, lq, est_quantifie, unite,
                   seuil_2016, seuil_2026_effectif, origine_seuil_2026,
                   seuil_strict, seuil_futur,
                   depasse_2016, depasse_2026, depasse_strict, depasse_futur,
                   bascule_2016_2026, indetermine_strict, fiabilite
            FROM v_mesures_verdict
            WHERE code_prelevement = ? AND notee
        """, [version, cp])

    return version, len(prels)


def figer_commune(con, commune, statut, version, calcule_le=None,
                  code_prelevement=None, commune_prelevement=None):
    """
    Inscrit le statut de couverture d'une commune.

    `statut` :
      - 'analysee'          : bulletin complet propre à la commune ;
      - 'rattachee_reseau'  : bulletin complet du même réseau, prélevé ailleurs ;
      - 'non_documentee'    : aucun bulletin complet. Ce n'est ni « conforme »
                              ni « non conforme » : c'est une absence de
                              donnée, et elle doit rester visible comme telle
                              (CLAUDE.md §2.4, transposé à la commune).
    """
    con.execute(SCHEMA_FIGE)
    jour = calcule_le or datetime.date.today().isoformat()

    # L'identité de la commune vient de la résolution INSEE, pas de la table
    # `communes` : une commune rattachée à un réseau voisin, ou non documentée,
    # n'a aucun prélèvement à elle et n'y figure donc pas. La chercher là
    # produirait une ligne anonyme sur la carte.
    code_insee = commune["code_insee"]
    infos = (commune.get("nom"), commune.get("dept") or code_insee[:2],
             commune.get("codes_postaux"), commune.get("lon"), commune.get("lat"))
    detail = (None, None, None)
    if code_prelevement:
        detail = con.execute("""
            SELECT date_prelevement, nb_parametres, pct_couverture
            FROM v_prelevement_verdict WHERE code_prelevement = ?
        """, [code_prelevement]).fetchone() or detail

    con.execute("DELETE FROM couverture_communes WHERE code_insee = ? AND version_referentiel = ?",
                [code_insee, version])
    con.execute("INSERT INTO couverture_communes VALUES (?,?,?::DATE,?,?,?,?,?,?,?,?,?::DATE,?,?)",
                [code_insee, version, jour, infos[0], infos[1], infos[2], infos[3], infos[4],
                 statut, code_prelevement, commune_prelevement,
                 str(detail[0]) if detail[0] else None, detail[1], detail[2]])


def statut(con):
    print("\n=== Couverture par commune ===")
    for r in con.execute("""
        SELECT statut, COUNT(*) FROM couverture_communes GROUP BY 1 ORDER BY 2 DESC
    """).fetchall():
        print(f"  {r[0]:<20} {r[1]}")
    print("\n=== Analyses figées ===")
    for r in con.execute("""
        SELECT version_referentiel, calcule_le, COUNT(*)
        FROM analyses_figees GROUP BY 1,2 ORDER BY 2 DESC
    """).fetchall():
        print(f"  {r[0]}  {r[1]}  {r[2]} bulletin(s)")


def main():
    p = argparse.ArgumentParser(description="Fige les analyses dans la base")
    p.add_argument("--statut", action="store_true", help="afficher l'état, sans recalculer")
    a = p.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"base absente : {DB_PATH}\nlance d'abord : python3 src/build_db.py")
        sys.exit(1)
    con = duckdb.connect(DB_PATH)
    try:
        if a.statut:
            con.execute(SCHEMA_FIGE)
            statut(con)
            return
        version, n = figer(con)
        print(f"figé : {n} bulletin(s) sous la version de référentiel {version}")
        statut(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Construction de la base : schéma en étoile + chargement du référentiel + vues de réétalonnage.

    python3 src/build_db.py            # crée / met à jour data/eau.duckdb
    python3 src/build_db.py --reset    # repart d'une base vide (perd les mesures collectées)

Le référentiel de seuils N'EST PAS dans ce fichier : il est lu depuis
referentiel/referentiel_seuils.csv, qui est la source de vérité versionnée
(cf. CLAUDE.md §4). Modifier un seuil = modifier le CSV + commit sourcé.
"""
import csv
import os
import sys

import duckdb

from common import (DB_PATH, REF_CSV, ALIAS_CSV, RACINE,
                    FACTEURS_MASSE_PAR_LITRE, norm, norm_unite, f, s)

REGLES_CSV = os.path.join(RACINE, "referentiel", "regles_famille.csv")

SCHEMA = """
CREATE TABLE IF NOT EXISTS communes (
    code_insee        VARCHAR PRIMARY KEY,
    nom               VARCHAR,
    code_departement  VARCHAR,
    codes_postaux     VARCHAR,
    lon               DOUBLE,
    lat               DOUBLE
);

CREATE TABLE IF NOT EXISTS prelevements (
    code_prelevement        VARCHAR PRIMARY KEY,
    code_insee              VARCHAR,
    code_installation_amont VARCHAR,
    nom_installation_amont  VARCHAR,
    nom_distributeur        VARCHAR,
    nom_uge                 VARCHAR,
    codes_reseaux           VARCHAR,
    noms_reseaux            VARCHAR,
    code_lieu_analyse       VARCHAR,
    date_prelevement        DATE,
    nb_parametres           INTEGER,
    est_complet             BOOLEAN,
    conclusion_conformite   VARCHAR,
    conf_limites_bact       VARCHAR,
    conf_limites_pc         VARCHAR,
    conf_references_pc      VARCHAR,
    source_url              VARCHAR
);

CREATE TABLE IF NOT EXISTS mesures (
    code_prelevement  VARCHAR,
    code_insee        VARCHAR,
    code_parametre    VARCHAR,
    code_cas          VARCHAR,
    libelle_parametre VARCHAR,
    libelle_norm      VARCHAR,
    resultat_num      DOUBLE,
    resultat_alpha    VARCHAR,
    lq                DOUBLE,
    est_quantifie     BOOLEAN,
    unite             VARCHAR,
    unite_norm        VARCHAR,
    limite_brute      VARCHAR,
    limite_declaree   DOUBLE,
    reference_brute   VARCHAR,
    reference_declaree DOUBLE,
    PRIMARY KEY (code_prelevement, libelle_parametre)
);

CREATE TABLE IF NOT EXISTS referentiel_seuils (
    libelle_norm             VARCHAR PRIMARY KEY,
    code_parametre           VARCHAR,
    code_cas                 VARCHAR,
    libelle                  VARCHAR,
    famille                  VARCHAR,
    unite                    VARCHAR,
    unite_norm               VARCHAR,
    seuil_2016               DOUBLE,
    seuil_2026               DOUBLE,
    date_applicabilite_2026  DATE,
    seuil_conditionnel       DOUBLE,
    condition_seuil          VARCHAR,
    statut_2026              VARCHAR,
    seuil_futur              DOUBLE,
    date_applicabilite_futur DATE,
    seuil_strict             DOUBLE,
    base_seuil_strict        VARCHAR,
    pe_reglementaire         VARCHAR,
    pe_scientifique          VARCHAR,
    sources                  VARCHAR,
    fiabilite                VARCHAR,
    est_agregat              BOOLEAN,
    cancerogenicite_circ     VARCHAR
);

CREATE TABLE IF NOT EXISTS alias_parametres (
    alias_norm   VARCHAR PRIMARY KEY,
    libelle_norm VARCHAR,
    commentaire  VARCHAR
);

CREATE TABLE IF NOT EXISTS unites_masse (
    unite_norm VARCHAR PRIMARY KEY,
    facteur    DOUBLE
);

CREATE TABLE IF NOT EXISTS regles_famille (
    nom_regle       VARCHAR PRIMARY KEY,
    limite_declaree DOUBLE,
    unite_norm      VARCHAR,
    libelle_norm    VARCHAR,
    justification   VARCHAR,
    sources         VARCHAR
);
"""

# ---------------------------------------------------------------------------
# Vues
# ---------------------------------------------------------------------------

# 1) Résolution du rapprochement mesure <-> référentiel.
#    Cascade : code_parametre Hub'Eau > numéro CAS > libellé normalisé >
#    alias > règle de famille.
#
#    Le numéro CAS est l'identifiant chimique international : il ne dépend ni
#    du laboratoire ni de l'orthographe. Il est renseigné sur 93 % des mesures
#    et c'est lui qui a permis de rattacher les 19 métabolites du tableau
#    ANSES à leur libellé Hub'Eau, dont « Terbuméton-désethyl » pour
#    « déséthyl-terbuméton » — qu'aucun rapprochement par libellé n'aurait
#    trouvé.
#
#    La règle de famille est ce qui rend le passage à l'échelle possible. Un
#    bulletin complet porte ~300 pesticides nommés (Boscalid, Quinmérac,
#    Imazamox…) qu'aucun référentiel saisi à la main ne couvrira jamais un par
#    un. Ils partagent tous la même limite réglementaire, et l'administration
#    la déclare avec chaque mesure. La règle rattache donc « toute mesure non
#    encore appariée dont la limite déclarée vaut 0,1 µg/L » à la ligne
#    « Pesticide - substance individuelle » du référentiel. La règle est
#    écrite dans un fichier versionné et son effet est auditable
#    (v_regle_famille_appliquee).
VUE_REF = """
CREATE OR REPLACE VIEW v_mesures_ref AS
SELECT
    m.*,
    COALESCE(r1.libelle_norm, rc.libelle_norm, r2.libelle_norm,
             r3.libelle_norm, r4.libelle_norm) AS ref_key,
    CASE
        WHEN r1.libelle_norm IS NOT NULL THEN 'code_parametre'
        WHEN rc.libelle_norm IS NOT NULL THEN 'code_cas'
        WHEN r2.libelle_norm IS NOT NULL THEN 'libelle'
        WHEN r3.libelle_norm IS NOT NULL THEN 'alias'
        WHEN r4.libelle_norm IS NOT NULL THEN 'regle_famille'
        ELSE NULL
    END AS mode_appariement,
    CASE WHEN COALESCE(r1.libelle_norm, rc.libelle_norm, r2.libelle_norm,
                       r3.libelle_norm) IS NULL
         THEN g.nom_regle END AS regle_appliquee
FROM mesures m
LEFT JOIN referentiel_seuils r1
       ON r1.code_parametre IS NOT NULL AND r1.code_parametre = m.code_parametre
LEFT JOIN referentiel_seuils rc
       ON rc.code_cas IS NOT NULL AND rc.code_cas = m.code_cas
LEFT JOIN referentiel_seuils r2
       ON r2.libelle_norm = m.libelle_norm
LEFT JOIN alias_parametres a
       ON a.alias_norm = m.libelle_norm
LEFT JOIN referentiel_seuils r3
       ON r3.libelle_norm = a.libelle_norm
LEFT JOIN regles_famille g
       ON COALESCE(r1.libelle_norm, rc.libelle_norm, r2.libelle_norm,
                   r3.libelle_norm) IS NULL
      AND g.limite_declaree = m.limite_declaree
      AND (g.unite_norm IS NULL OR g.unite_norm = m.unite_norm)
LEFT JOIN referentiel_seuils r4
       ON r4.libelle_norm = g.libelle_norm;
"""

# 2) Le cœur du projet : la même mesure notée contre trois grilles.
#
#    Deux sources de seuil, jamais confondues :
#      - le RÉFÉRENTIEL du projet : saisi à la main sur textes réglementaires,
#        daté, sourcé. Seul lui porte 2016, le seuil strict et les seuils
#        différés. Seul lui peut produire une bascule.
#      - la LIMITE DÉCLARÉE avec la mesure par l'administration : la grille
#        d'aujourd'hui, et rien d'autre. Elle sert de filet là où le
#        référentiel est muet, pour qu'un bulletin ne soit pas déclaré sans
#        dépassement après n'avoir été lu qu'au dixième.
#
#    Un dépassement exige est_quantifie = TRUE (CLAUDE.md §2.4).
VUE_VERDICT = """
CREATE OR REPLACE VIEW v_mesures_verdict AS
WITH base AS (
    SELECT
        v.*,
        r.libelle_norm AS r_key, r.famille, r.unite_norm AS unite_ref,
        r.seuil_2016, r.seuil_2026, r.seuil_strict, r.seuil_futur,
        r.base_seuil_strict, r.statut_2026, r.date_applicabilite_futur, r.est_agregat,
        r.date_applicabilite_2026, p.date_prelevement,
        r.seuil_conditionnel, r.condition_seuil, r.cancerogenicite_circ,
        r.pe_reglementaire, r.pe_scientifique, r.fiabilite,
        -- Facteur de conversion du seuil (exprimé dans l'unité du référentiel)
        -- vers l'unité dans laquelle la mesure est exprimée.
        --   NULL = les deux unités sont connues, différentes et non
        --   convertibles : AUCUN verdict n'est produit, plutôt qu'un verdict
        --   faux d'un facteur 1000.
        CASE
            WHEN r.unite_norm IS NULL OR v.unite_norm IS NULL THEN 1.0
            WHEN r.unite_norm = v.unite_norm                  THEN 1.0
            WHEN ur.facteur IS NOT NULL AND um.facteur IS NOT NULL
                 THEN ur.facteur / um.facteur
            ELSE NULL
        END AS k
    FROM v_mesures_ref v
    LEFT JOIN prelevements p ON p.code_prelevement = v.code_prelevement
    LEFT JOIN referentiel_seuils r ON r.libelle_norm = v.ref_key
    LEFT JOIN unites_masse ur ON ur.unite_norm = r.unite_norm
    LEFT JOIN unites_masse um ON um.unite_norm = v.unite_norm
)
SELECT
    v.code_insee,
    v.code_prelevement,
    v.libelle_parametre,
    v.code_parametre,
    v.code_cas,
    v.mode_appariement,
    v.regle_appliquee,
    v.famille,
    v.resultat_num,
    v.lq,
    v.est_quantifie,
    v.unite,

    -- Tous les seuils sont RAMENÉS À L'UNITÉ DE LA MESURE (facteur k), donc
    -- directement comparables au résultat et affichables tels quels.
    v.seuil_2016   * v.k AS seuil_2016,
    v.seuil_2026   * v.k AS seuil_2026,
    v.seuil_strict * v.k AS seuil_strict,
    v.seuil_futur  * v.k AS seuil_futur,
    v.limite_declaree,
    COALESCE(v.seuil_2026 * v.k, v.limite_declaree) AS seuil_2026_effectif,
    CASE
        WHEN v.seuil_2026 * v.k IS NOT NULL THEN 'referentiel'
        WHEN v.limite_declaree  IS NOT NULL THEN 'declare'
        ELSE 'absent'
    END AS origine_seuil_2026,
    (v.k IS NULL) AS unite_incomparable,
    v.date_applicabilite_2026,
    v.seuil_conditionnel * v.k AS seuil_conditionnel,
    v.condition_seuil,
    v.cancerogenicite_circ,

    -- LE SEUIL QUI S'APPLIQUAIT LE JOUR DU PRÉLÈVEMENT.
    -- Un reclassement n'est pas rétroactif : la note d'information de la
    -- délégation départementale de Charente-Maritime du 10/06/2024 est
    -- formelle — « il n'y a pas de rétroactivité possible ; l'expression des
    -- non-conformités mises en évidence avant le 29/04/2024 est maintenue ».
    -- Une mesure de R471811 à 0,5 µg/L prélevée en 2023 EST une non-conformité ;
    -- la même valeur prélevée en 2025 est conforme. Comparer les deux au seul
    -- seuil d'aujourd'hui produit un verdict anachronique — l'erreur symétrique
    -- de celle du plomb, où un seuil futur était appliqué trop tôt.
    CASE
        WHEN v.date_applicabilite_2026 IS NOT NULL
             AND v.date_prelevement IS NOT NULL
             AND v.date_prelevement < v.date_applicabilite_2026
        THEN v.seuil_2016 * v.k
        ELSE COALESCE(v.seuil_2026 * v.k, v.limite_declaree)
    END AS seuil_applicable,
    CASE
        WHEN v.date_applicabilite_2026 IS NOT NULL
             AND v.date_prelevement IS NOT NULL
             AND v.date_prelevement < v.date_applicabilite_2026 THEN '2016'
        WHEN v.seuil_2026 * v.k IS NOT NULL THEN '2026'
        WHEN v.limite_declaree IS NOT NULL   THEN 'declare'
        ELSE 'aucune'
    END AS grille_applicable,
    v.base_seuil_strict,
    v.statut_2026,
    COALESCE(v.est_agregat, FALSE) AS est_agregat,
    v.date_applicabilite_futur,
    v.pe_reglementaire,
    v.pe_scientifique,
    v.fiabilite,

    -- Une mesure est « notée » si elle a un seuil de comparaison actuel.
    -- C'est le dénominateur honnête de toute affirmation de conformité.
    (COALESCE(v.seuil_2026 * v.k, v.limite_declaree) IS NOT NULL) AS notee,

    -- 2016 et strict ne viennent QUE du référentiel : on n'invente pas de
    -- passé réglementaire à partir de la grille d'aujourd'hui.
    (v.est_quantifie AND v.seuil_2016   * v.k IS NOT NULL AND v.resultat_num > v.seuil_2016   * v.k) AS depasse_2016,
    (v.est_quantifie AND v.seuil_strict * v.k IS NOT NULL AND v.resultat_num > v.seuil_strict * v.k) AS depasse_strict,
    (v.est_quantifie AND v.seuil_futur  * v.k IS NOT NULL AND v.resultat_num > v.seuil_futur  * v.k) AS depasse_futur,
    (v.est_quantifie AND COALESCE(v.seuil_2026 * v.k, v.limite_declaree) IS NOT NULL
       AND v.resultat_num > COALESCE(v.seuil_2026 * v.k, v.limite_declaree))                         AS depasse_2026,

    -- LE VERDICT TEL QU'IL DEVAIT ÊTRE RENDU CE JOUR-LÀ.
    -- C'est celui-ci qui est comparable à la conclusion de l'ARS.
    --
    -- Un seuil peut dépendre du PROCÉDÉ ou de la RESSOURCE, pas seulement de
    -- la date : chlorates et chlorites passent à 0,70 mg/L quand la
    -- désinfection en génère, le sélénium à 30 µg/L et le bore à 2,4 mg/L par
    -- exception géologique. Rien dans les données ne dit si la condition est
    -- remplie. On ne prononce donc un dépassement que si la mesure franchit
    -- AUSSI la valeur la plus permissive ; entre les deux, c'est un
    -- indéterminé, pas une non-conformité. Un faux positif coûte plus cher au
    -- projet qu'un faux négatif (CLAUDE.md §2.13).
    (v.est_quantifie AND v.resultat_num > COALESCE(v.seuil_conditionnel * v.k, CASE
        WHEN v.date_applicabilite_2026 IS NOT NULL
             AND v.date_prelevement IS NOT NULL
             AND v.date_prelevement < v.date_applicabilite_2026
        THEN v.seuil_2016 * v.k
        ELSE COALESCE(v.seuil_2026 * v.k, v.limite_declaree)
     END)) AS depasse_applicable,

    -- Au-dessus du seuil de base, sous le seuil conditionnel : le verdict
    -- dépend d'une information que la base n'a pas.
    (v.est_quantifie AND v.seuil_conditionnel IS NOT NULL
       AND v.resultat_num >  CASE
             WHEN v.date_applicabilite_2026 IS NOT NULL
                  AND v.date_prelevement IS NOT NULL
                  AND v.date_prelevement < v.date_applicabilite_2026
             THEN v.seuil_2016 * v.k
             ELSE COALESCE(v.seuil_2026 * v.k, v.limite_declaree) END
       AND v.resultat_num <= v.seuil_conditionnel * v.k) AS indetermine_condition,

    -- LA BASCULE : dépassait la limite de 2016, ne dépasse pas celle de 2026.
    -- Ce n'est pas l'eau qui a changé, c'est la limite. Référentiel seul.
    (v.est_quantifie
       AND v.seuil_2016 * v.k IS NOT NULL AND v.seuil_2026 * v.k IS NOT NULL
       AND v.resultat_num >  v.seuil_2016 * v.k
       AND v.resultat_num <= v.seuil_2026 * v.k) AS bascule_2016_2026,

    -- BASCULE DATÉE : la bascule, mais avec le jour où la limite a bougé.
    -- Ce prélèvement est postérieur au déplacement : cette eau est conforme
    -- parce qu'elle a été prélevée APRÈS. La même valeur, la veille, ne
    -- l'était pas. C'est la thèse du projet, datable au jour près.
    (v.est_quantifie
       AND v.date_applicabilite_2026 IS NOT NULL
       AND v.date_prelevement IS NOT NULL
       AND v.date_prelevement >= v.date_applicabilite_2026
       AND v.seuil_2016 * v.k IS NOT NULL AND v.seuil_2026 * v.k IS NOT NULL
       AND v.resultat_num >  v.seuil_2016 * v.k
       AND v.resultat_num <= v.seuil_2026 * v.k) AS bascule_datee,

    -- Troisième état de verdict : ni conforme ni dépassement, indéterminé.
    (NOT v.est_quantifie AND v.lq IS NOT NULL
       AND v.seuil_strict * v.k IS NOT NULL AND v.lq > v.seuil_strict * v.k) AS indetermine_strict,

    -- Contrôle croisé : notre seuil 2026 contredit-il celui que
    -- l'administration déclare avec la mesure ? Comparaison faite après
    -- conversion, sinon une simple différence d'unité passerait pour un
    -- désaccord réglementaire.
    (v.seuil_2026 * v.k IS NOT NULL AND v.limite_declaree IS NOT NULL
       AND abs(v.seuil_2026 * v.k - v.limite_declaree) > 1e-9) AS ecart_referentiel_declare
FROM base v;
"""

# 3) Agrégat par prélèvement. est_complet reste porté ici : toute requête de
#    thèse doit filtrer dessus. Le taux de couverture est porté ici aussi :
#    une conformité annoncée sans son dénominateur est une demi-vérité.
VUE_PRELEVEMENT = """
CREATE OR REPLACE VIEW v_prelevement_verdict AS
SELECT
    p.code_prelevement,
    p.code_insee,
    c.nom               AS commune,
    c.code_departement  AS dept,
    c.codes_postaux,
    c.lon,
    c.lat,
    p.date_prelevement,
    p.code_installation_amont,
    p.nom_installation_amont,
    p.nom_uge,
    p.noms_reseaux,
    p.nom_distributeur,
    p.nb_parametres,
    p.est_complet,
    p.conclusion_conformite,
    COUNT(v.libelle_parametre)                                    AS nb_mesures_lues,
    COUNT(*) FILTER (WHERE v.notee)                               AS nb_mesures_notees,
    ROUND(100.0 * COUNT(*) FILTER (WHERE v.notee)
          / NULLIF(COUNT(v.libelle_parametre), 0), 1)             AS pct_couverture,
    COUNT(*) FILTER (WHERE v.origine_seuil_2026 = 'referentiel')  AS nb_notees_referentiel,
    COUNT(*) FILTER (WHERE v.origine_seuil_2026 = 'declare')      AS nb_notees_declare,
    COUNT(*) FILTER (WHERE v.origine_seuil_2026 = 'absent')       AS nb_sans_seuil,
    COUNT(*) FILTER (WHERE v.depasse_2016)                        AS nb_depasse_2016,
    COUNT(*) FILTER (WHERE v.depasse_2026)                        AS nb_depasse_2026,
    COUNT(*) FILTER (WHERE v.depasse_applicable)                  AS nb_depasse_applicable,
    COUNT(*) FILTER (WHERE v.indetermine_condition)               AS nb_indetermines_condition,
    COUNT(*) FILTER (WHERE v.depasse_strict)                      AS nb_depasse_strict,
    COUNT(*) FILTER (WHERE v.depasse_futur)                       AS nb_depasse_futur,
    COUNT(*) FILTER (WHERE v.bascule_2016_2026)                   AS nb_bascules,
    COUNT(*) FILTER (WHERE v.bascule_datee)                       AS nb_bascules_datees,
    COUNT(*) FILTER (WHERE v.indetermine_strict)                  AS nb_indetermines,
    COUNT(*) FILTER (WHERE v.ecart_referentiel_declare)           AS nb_ecarts_seuil,
    COUNT(*) FILTER (WHERE v.est_quantifie
                     AND v.famille IN ('metabolite', 'PFAS', 'pesticide')) AS nb_polluants_synthese,

    -- EFFORT DE RECHERCHE. Ce n'est pas un indicateur de qualité de l'eau,
    -- c'est un indicateur de ce qu'on a bien voulu chercher. Une commune qui
    -- recherche 700 paramètres a mécaniquement plus de chances d'en voir un
    -- dépasser qu'une commune qui en recherche 200 : comparer leurs nombres
    -- bruts de dépassements est un contresens (CLAUDE.md §2.11).
    COUNT(*) FILTER (WHERE v.famille IN ('pesticide','metabolite','PFAS','organique'))
                                                                  AS nb_synthese_recherchees,
    CASE WHEN p.nb_parametres < 200 THEN 'restreinte'
         WHEN p.nb_parametres < 300 THEN 'standard'
         WHEN p.nb_parametres < 450 THEN 'approfondie'
         ELSE 'exhaustive' END                                    AS classe_effort,
    -- Les TAUX sont comparables d'un bulletin à l'autre ; les comptes ne le
    -- sont pas. Toute comparaison entre communes passe par eux.
    ROUND(1000.0 * COUNT(*) FILTER (WHERE v.depasse_applicable)
          / NULLIF(COUNT(*) FILTER (WHERE v.notee), 0), 2)         AS depassements_pour_mille,
    ROUND(1000.0 * COUNT(*) FILTER (WHERE v.est_quantifie
              AND v.famille IN ('pesticide','metabolite','PFAS','organique'))
          / NULLIF(COUNT(*) FILTER (WHERE
              v.famille IN ('pesticide','metabolite','PFAS','organique')), 0), 2)
                                                                  AS synthese_quantifiees_pour_mille
FROM prelevements p
JOIN communes c ON c.code_insee = p.code_insee
LEFT JOIN v_mesures_verdict v ON v.code_prelevement = p.code_prelevement
GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16;
"""

# 4) Diagnostic de couverture — à consulter après CHAQUE collecte.
#    Un paramètre sans aucun seuil de comparaison est une mesure invisible :
#    elle existe en base et ne pèse sur aucun verdict.
VUE_NON_APPARIES = """
CREATE OR REPLACE VIEW v_parametres_non_apparies AS
SELECT
    libelle_parametre,
    libelle_norm,
    ANY_VALUE(code_parametre)          AS code_parametre_observe,
    ANY_VALUE(code_cas)                AS code_cas,
    ANY_VALUE(unite)                   AS unite,
    ANY_VALUE(limite_brute)            AS limite_declaree_brute,
    COUNT(*)                           AS nb_mesures,
    COUNT(DISTINCT code_insee)         AS nb_communes,
    COUNT(*) FILTER (WHERE est_quantifie) AS nb_quantifiees,
    MAX(resultat_num) FILTER (WHERE est_quantifie) AS max_quantifie
FROM v_mesures_ref
WHERE ref_key IS NULL AND limite_declaree IS NULL
GROUP BY 1, 2
ORDER BY nb_quantifiees DESC, nb_mesures DESC;
"""

# 5) Couverture du référentiel : quelles lignes ne sont jamais mesurées ?
VUE_COUVERTURE_REF = """
CREATE OR REPLACE VIEW v_referentiel_jamais_mesure AS
SELECT r.libelle, r.famille, r.fiabilite, r.sources
FROM referentiel_seuils r
LEFT JOIN (SELECT DISTINCT ref_key FROM v_mesures_ref WHERE ref_key IS NOT NULL) u
       ON u.ref_key = r.libelle_norm
WHERE u.ref_key IS NULL
ORDER BY r.famille, r.libelle;
"""

# 6) Audit de la règle de famille : QUOI, exactement, a été rattaché
#    automatiquement ? Cette liste doit être relue : une substance qui n'est
#    pas un pesticide et qui porte la même limite y apparaîtrait à tort.
VUE_REGLE_FAMILLE = """
CREATE OR REPLACE VIEW v_regle_famille_appliquee AS
SELECT
    regle_appliquee                    AS regle,
    libelle_parametre,
    ANY_VALUE(code_parametre)          AS code_parametre,
    ANY_VALUE(unite)                   AS unite,
    ANY_VALUE(limite_declaree)         AS limite_declaree,
    COUNT(*)                           AS nb_mesures,
    COUNT(*) FILTER (WHERE est_quantifie) AS nb_quantifiees
FROM v_mesures_ref
WHERE mode_appariement = 'regle_famille'
GROUP BY 1, 2
ORDER BY nb_quantifiees DESC, libelle_parametre;
"""

# 7) Contrôle croisé du référentiel contre la source.
#    Chaque ligne est soit une erreur de notre référentiel, soit un écart
#    réel entre le texte et la pratique déclarée : dans les deux cas, à
#    regarder. C'est le contrôle qualité que le projet n'avait pas.
VUE_ECARTS = """
CREATE OR REPLACE VIEW v_ecarts_referentiel_source AS
SELECT
    libelle_parametre,
    ANY_VALUE(seuil_2026)      AS seuil_2026_referentiel,
    ANY_VALUE(limite_declaree) AS limite_declaree_source,
    ANY_VALUE(unite)           AS unite,
    ANY_VALUE(fiabilite)       AS fiabilite,
    COUNT(*)                   AS nb_mesures,
    COUNT(DISTINCT code_insee) AS nb_communes
FROM v_mesures_verdict
WHERE ecart_referentiel_declare
GROUP BY 1
ORDER BY nb_mesures DESC;
"""

# L'effort de recherche, lisible d'un coup d'œil.
#
# À lire dans ce sens : une eau « correcte » sur 200 paramètres est une
# information plus faible qu'une eau « moyenne » sur 700. La première n'a pas
# été beaucoup interrogée. Trier par parametres_recherches décroissant met en
# tête les communes les plus transparentes, pas les plus polluées.
# Les mesures dont le verdict dépend d'une condition que la base ne connaît
# pas : procédé de désinfection, nature géologique de la ressource. Elles ne
# sont PAS des dépassements — elles sont à vérifier à la main avant toute
# publication.
VUE_CONDITIONS = """
CREATE OR REPLACE VIEW v_verdicts_sous_condition AS
SELECT
    code_insee, code_prelevement, libelle_parametre,
    resultat_num, unite, seuil_2026 AS seuil_de_base,
    seuil_conditionnel, condition_seuil
FROM v_mesures_verdict
WHERE indetermine_condition
ORDER BY libelle_parametre;
"""

VUE_EFFORT = """
CREATE OR REPLACE VIEW v_effort_recherche AS
SELECT
    commune, dept, date_prelevement, nom_installation_amont,
    nb_parametres AS parametres_recherches,
    classe_effort,
    nb_synthese_recherchees,
    nb_mesures_notees,
    nb_depasse_applicable,
    depassements_pour_mille,
    synthese_quantifiees_pour_mille
FROM v_prelevement_verdict
WHERE est_complet
ORDER BY parametres_recherches DESC;
"""

VUE_SEUILS_SANS_DATE = """
CREATE OR REPLACE VIEW v_seuils_sans_date AS
SELECT libelle, famille, seuil_2016, seuil_2026, statut_2026, sources, fiabilite
FROM referentiel_seuils
WHERE seuil_2016 IS NOT NULL AND seuil_2026 IS NOT NULL
  AND seuil_2016 <> seuil_2026
  AND date_applicabilite_2026 IS NULL
ORDER BY famille, libelle;
"""

VUE_UNITES = """
CREATE OR REPLACE VIEW v_unites_incomparables AS
SELECT libelle_parametre,
       ANY_VALUE(unite)     AS unite_mesure,
       COUNT(*)             AS nb_mesures,
       COUNT(DISTINCT code_insee) AS nb_communes
FROM v_mesures_verdict
WHERE unite_incomparable
GROUP BY 1
ORDER BY nb_mesures DESC;
"""

VUES = [VUE_REF, VUE_VERDICT, VUE_PRELEVEMENT, VUE_NON_APPARIES,
        VUE_COUVERTURE_REF, VUE_REGLE_FAMILLE, VUE_ECARTS, VUE_UNITES,
        VUE_SEUILS_SANS_DATE, VUE_EFFORT, VUE_CONDITIONS]


def controler_forme(chemin):
    """
    Refuse un CSV dont une ligne n'a pas le bon nombre de colonnes.

    Un point-virgule oublié à l'intérieur d'une cellule décale toute la ligne
    SANS erreur visible : `fiabilite` se retrouve dans `sources`, un seuil
    dans un libellé. C'est arrivé deux fois dans ce projet — la première sur
    14 lignes, la seconde le 7 août 2026 sur quatre. Les deux fois, rien ne
    l'a signalé. Ce contrôle existe pour qu'il n'y ait pas de troisième fois
    (cf. CLAUDE.md §5).
    """
    with open(chemin, encoding="utf-8") as fh:
        lignes = [l.rstrip("\n") for l in fh if not l.lstrip().startswith("#") and l.strip()]
    attendu = len(lignes[0].split(";"))
    mauvaises = [(n, l) for n, l in enumerate(lignes[1:], 2)
                 if len(l.split(";")) != attendu]
    if mauvaises:
        print(f"  ! {os.path.basename(chemin)} : {len(mauvaises)} ligne(s) au mauvais "
              f"nombre de colonnes ({attendu} attendues) — point-virgule dans une cellule ?")
        for n, l in mauvaises[:5]:
            print(f"      ligne {n} : {len(l.split(';'))} colonnes — {l[:70]}")
        raise ValueError(f"{chemin} : {len(mauvaises)} ligne(s) mal formée(s)")
    return len(lignes) - 1


def charger_referentiel(con, chemin=REF_CSV):
    """Charge referentiel_seuils.csv. Remplace intégralement la table."""
    controler_forme(chemin)
    con.execute("DELETE FROM referentiel_seuils")
    n, doublons = 0, []
    vus = set()
    with open(chemin, encoding="utf-8") as fh:
        for ligne in csv.DictReader(_sans_commentaires(fh), delimiter=";"):
            libelle = s(ligne.get("libelle"))
            if not libelle:
                continue
            cle = norm(libelle)
            if cle in vus:
                doublons.append(libelle)
                continue
            vus.add(cle)
            con.execute(
                "INSERT INTO referentiel_seuils VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [
                    cle,
                    s(ligne.get("code_parametre")),
                    s(ligne.get("code_cas")),
                    libelle,
                    s(ligne.get("famille")),
                    s(ligne.get("unite")),
                    norm_unite(ligne.get("unite")),
                    f(ligne.get("seuil_2016")),
                    f(ligne.get("seuil_2026")),
                    s(ligne.get("date_applicabilite_2026")),
                    f(ligne.get("seuil_conditionnel")),
                    s(ligne.get("condition_seuil")),
                    s(ligne.get("statut_2026")),
                    f(ligne.get("seuil_futur")),
                    s(ligne.get("date_applicabilite_futur")),
                    f(ligne.get("seuil_strict")),
                    s(ligne.get("base_seuil_strict")),
                    s(ligne.get("pe_reglementaire")),
                    s(ligne.get("pe_scientifique")),
                    s(ligne.get("sources")),
                    s(ligne.get("fiabilite")),
                    (s(ligne.get("est_agregat")) or "non").lower() == "oui",
                    s(ligne.get("cancerogenicite_circ")),
                ],
            )
            n += 1
    if doublons:
        print(f"  ! {len(doublons)} libellé(s) en doublon ignoré(s) : {', '.join(doublons)}")
    return n


def charger_alias(con, chemin=ALIAS_CSV):
    """Charge alias_parametres.csv. Un alias dont la cible est absente du
    référentiel est refusé : un alias qui ne mène nulle part est un piège."""
    con.execute("DELETE FROM alias_parametres")
    cibles = {r[0] for r in con.execute("SELECT libelle_norm FROM referentiel_seuils").fetchall()}
    n, orphelins = 0, []
    with open(chemin, encoding="utf-8") as fh:
        for ligne in csv.DictReader(_sans_commentaires(fh), delimiter=";"):
            alias = norm(ligne.get("alias"))
            cible = norm(ligne.get("libelle_cible"))
            if not alias or not cible:
                continue
            if cible not in cibles:
                orphelins.append(f"{alias} -> {cible}")
                continue
            if alias in cibles:
                # l'alias est déjà un libellé du référentiel : inutile et ambigu
                continue
            con.execute(
                "INSERT OR REPLACE INTO alias_parametres VALUES (?,?,?)",
                [alias, cible, s(ligne.get("commentaire"))],
            )
            n += 1
    if orphelins:
        print(f"  ! {len(orphelins)} alias sans cible au référentiel, ignoré(s) :")
        for o in orphelins:
            print(f"      {o}")
    return n


def charger_regles(con, chemin=REGLES_CSV):
    """Charge regles_famille.csv : rattachement automatique par limite déclarée."""
    con.execute("DELETE FROM regles_famille")
    if not os.path.exists(chemin):
        return 0
    cibles = {r[0] for r in con.execute("SELECT libelle_norm FROM referentiel_seuils").fetchall()}
    n, refusees, signatures = 0, [], set()
    with open(chemin, encoding="utf-8") as fh:
        for ligne in csv.DictReader(_sans_commentaires(fh), delimiter=";"):
            nom = s(ligne.get("nom_regle"))
            cible = norm(ligne.get("libelle_cible"))
            limite = f(ligne.get("limite_declaree"))
            unite = s(ligne.get("unite"))
            if not nom or not cible or limite is None:
                continue
            if cible not in cibles:
                refusees.append(f"{nom} -> {cible} (cible absente du référentiel)")
                continue
            signature = (limite, norm_unite(unite))
            if signature in signatures:
                refusees.append(f"{nom} (signature {signature} déjà prise : "
                                "deux règles ne peuvent pas capter la même mesure)")
                continue
            signatures.add(signature)
            con.execute(
                "INSERT INTO regles_famille VALUES (?,?,?,?,?,?)",
                [nom, limite, norm_unite(unite), cible,
                 s(ligne.get("justification")), s(ligne.get("sources"))],
            )
            n += 1
    if refusees:
        print(f"  ! {len(refusees)} règle(s) de famille refusée(s) :")
        for r in refusees:
            print(f"      {r}")
    return n


def charger_unites(con):
    """Facteurs de conversion des unités de masse par litre (physique, pas
    réglementation) : ils ne sont donc pas dans un CSV versionné."""
    con.execute("DELETE FROM unites_masse")
    for u, k in FACTEURS_MASSE_PAR_LITRE.items():
        con.execute("INSERT INTO unites_masse VALUES (?,?)", [u, k])
    return len(FACTEURS_MASSE_PAR_LITRE)


def _sans_commentaires(fh):
    """Laisse passer le CSV en ignorant les lignes de commentaire « # »."""
    for ligne in fh:
        if not ligne.lstrip().startswith("#"):
            yield ligne


def build(db=DB_PATH, reset=False):
    os.makedirs(os.path.dirname(db), exist_ok=True)
    if reset and os.path.exists(db):
        os.remove(db)
        print(f"base supprimée : {db}")

    con = duckdb.connect(db)
    con.execute(SCHEMA)
    print("schéma en place")

    nref = charger_referentiel(con)
    print(f"référentiel   : {nref} paramètres chargés depuis referentiel_seuils.csv")
    nalias = charger_alias(con)
    print(f"alias         : {nalias} variantes d'écriture chargées")
    nunites = charger_unites(con)
    print(f"unités        : {nunites} facteurs de conversion masse/litre")
    nregles = charger_regles(con)
    print(f"règles famille: {nregles} règle(s) de rattachement par limite déclarée")

    for v in VUES:
        con.execute(v)
    print(f"vues          : {len(VUES)} créées")

    # Contrôles de cohérence du référentiel -------------------------------
    incoherences = con.execute("""
        SELECT libelle, seuil_2026, seuil_futur, date_applicabilite_futur
        FROM referentiel_seuils
        WHERE (seuil_futur IS NOT NULL AND date_applicabilite_futur IS NULL)
           OR (seuil_futur IS NULL AND date_applicabilite_futur IS NOT NULL)
    """).fetchall()
    if incoherences:
        print("  ! seuil futur sans date d'applicabilité (ou l'inverse) — cf. CLAUDE.md §2.5 :")
        for r in incoherences:
            print(f"      {r[0]}")

    sans_date = con.execute("SELECT libelle FROM v_seuils_sans_date").fetchall()
    if sans_date:
        print(f"  ! {len(sans_date)} seuil(s) déplacé(s) sans date d'applicabilité — "
              "le verdict y est anachronique (cf. CLAUDE.md §2.10) :")
        for r in sans_date:
            print(f"      {r[0]}")

    a_verifier = con.execute(
        "SELECT COUNT(*) FROM referentiel_seuils WHERE fiabilite <> 'verifie'"
    ).fetchone()[0]
    if a_verifier:
        print(f"  i {a_verifier} ligne(s) du référentiel en fiabilite <> 'verifie' :")
        print("    à signaler comme telles dans toute sortie publique (CLAUDE.md §2.7)")

    nmes = con.execute("SELECT COUNT(*) FROM mesures").fetchone()[0]
    npre = con.execute("SELECT COUNT(*) FROM prelevements").fetchone()[0]
    print(f"contenu       : {npre} prélèvement(s), {nmes} mesure(s)")

    if nmes:
        cov = con.execute("""
            SELECT COUNT(*), COUNT(*) FILTER (WHERE notee),
                   COUNT(*) FILTER (WHERE origine_seuil_2026 = 'referentiel'),
                   COUNT(*) FILTER (WHERE origine_seuil_2026 = 'declare')
            FROM v_mesures_verdict
        """).fetchone()
        pct = 100.0 * cov[1] / cov[0] if cov[0] else 0
        print(f"couverture    : {cov[1]}/{cov[0]} mesures notées ({pct:.1f} %) "
              f"— référentiel {cov[2]}, limite déclarée {cov[3]}")
        non_app = con.execute("SELECT COUNT(*) FROM v_parametres_non_apparies").fetchone()[0]
        print(f"  → {non_app} libellé(s) sans aucun seuil de comparaison")
        print("    (SELECT * FROM v_parametres_non_apparies LIMIT 40)")
        ecarts = con.execute("SELECT COUNT(*) FROM v_ecarts_referentiel_source").fetchone()[0]
        if ecarts:
            print(f"  ! {ecarts} paramètre(s) où notre seuil_2026 contredit la limite déclarée")
            print("    (SELECT * FROM v_ecarts_referentiel_source)")

    con.close()
    print(f"\nbase prête : {db}")
    print("prochaine étape : python3 src/fetch_departement.py --dept <NN>")


if __name__ == "__main__":
    build(reset="--reset" in sys.argv)

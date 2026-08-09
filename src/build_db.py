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
    --
    -- `seuil_strict * k > 0` n'est pas une précaution de calcul, c'est une
    -- règle de méthode — la même que celle du §8bis obligation 11, dont ce
    -- champ est le voisin immédiat. **Un seuil de zéro ne se perce pas par le
    -- bas.** La bactériologie exige l'absence, et la « LQ » d'un dénombrement
    -- vaut 1 puisqu'on ne compte pas une demi-bactérie : sans cette condition,
    -- toute mesure bactériologique non quantifiée serait déclarée indéterminée
    -- alors qu'elle est parfaitement lisible.
    --
    -- Aucune mesure du corpus n'était concernée le 8 août 2026, et par
    -- accident : les libellés de la source — « Escherichia coli /100ml - MF »,
    -- « Entérocoques /100ml-MS » — ne rejoignent aucune ligne du référentiel,
    -- qui porte « Escherichia coli » tout court. Leur seuil vient donc de la
    -- seule limite déclarée, et `seuil_strict` reste NULL. Le jour où un alias
    -- est ajouté — c'est précisément à cela que sert alias_parametres.csv —
    -- 69 mesures basculaient en « indéterminé » sans que rien n'ait changé
    -- dans l'eau. Une règle qui ne tient que par une lacune du catalogue n'est
    -- pas une règle.
    --
    -- Rien à corriger en revanche sur `depasse_strict` : trois entérocoques
    -- pour 100 mL franchissent bel et bien une exigence d'absence. C'est la
    -- LQ, et elle seule, qui ne peut pas passer sous zéro.
    (NOT v.est_quantifie AND v.lq IS NOT NULL
       AND v.seuil_strict * v.k IS NOT NULL AND v.seuil_strict * v.k > 0
       AND v.lq > v.seuil_strict * v.k) AS indetermine_strict,

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

# ---------------------------------------------------------------------------
# LE PANEL : ce qu'on a cherché, et ce qu'on a cessé de chercher
# ---------------------------------------------------------------------------
#
# Le §2.11 dit que l'effort de recherche est un indicateur. Il l'exprime par un
# NOMBRE — 627 paramètres en 2019, 369 en 2024. Mais l'information est aussi
# dans la LISTE : quels paramètres a-t-on cessé de chercher ? Personne ne
# l'annonce, et sur des centaines de communes un retrait commun trahirait une
# décision nationale, un changement de laboratoire ou une date d'arrêté.
#
# Cinq vues, du local à l'agrégé :
#   v_panel_bulletin          le panel de chaque bulletin complet
#   v_panel_evolution         la comparaison de deux bulletins consécutifs
#   v_parametres_abandonnes   ce qui disparaît, et chez combien de communes
#   v_parametre_presence      la part des bulletins qui cherchent un paramètre,
#                             année par année — le détecteur à l'échelle
#   v_parametre_presence_dept la même, par département — le contre-feu, qui dit
#                             si une chute est un retrait ou un corpus qui a
#                             changé de composition
#
# Clé d'identité du paramètre : `code_parametre` quand la source le donne
# (15 613 mesures sur 15 617 au 8 août 2026), sinon le libellé normalisé. Les
# deux sont nécessaires : le code seul perdrait quatre mesures, le libellé seul
# éclaterait un paramètre renommé d'une campagne à l'autre.
VUE_PANEL = """
CREATE OR REPLACE VIEW v_panel_bulletin AS
SELECT
    p.code_prelevement,
    p.code_insee,
    c.nom               AS commune,
    c.code_departement  AS dept,
    p.date_prelevement,
    p.nom_installation_amont,
    -- Le nom de réseau porte sa part de mélange : « JOUY (100 %) » en 2025,
    -- « JOUY » en 2026. C'est le même réseau ; sans ce nettoyage, toute
    -- comparaison d'une année sur l'autre les croirait différents.
    regexp_replace(COALESCE(p.noms_reseaux, ''),
                   '\\s*\\(\\d+([.,]\\d+)?\\s*%\\)', '', 'g') AS reseau_norm,
    COUNT(DISTINCT COALESCE(m.code_parametre, m.libelle_norm))        AS nb_panel,
    list_sort(list(DISTINCT COALESCE(m.code_parametre, m.libelle_norm))) AS panel
FROM prelevements p
JOIN communes c ON c.code_insee = p.code_insee
JOIN mesures   m ON m.code_prelevement = p.code_prelevement
WHERE p.est_complet
GROUP BY 1, 2, 3, 4, 5, 6, 7;
"""

# La comparaison de deux bulletins complets CONSÉCUTIFS d'une même commune.
#
# Réserve de méthode, vérifiée sur le corpus le 8 août 2026 et à ne pas perdre
# de vue : sur les huit communes portant plus d'un bulletin complet, AUCUNE
# paire ne partage un `code_installation_amont`. Deux situations très
# différentes se cachent derrière ce zéro — le même point d'eau recodé
# (Laparrouquial : 081000936 puis 081004209, même station) ou non renseigné
# (Challet, Jouy, Souel, Bailleau : code vide sur le bulletin récent), et des
# points d'eau réellement distincts (Boissezon : trois captages).
#
# D'où deux colonnes et non une. `meme_point_deau` répond, `identite_certaine`
# dit si la réponse est lue ou déduite. Comparer les panels de deux captages
# différents reste légitime — c'est bien le programme d'analyse qu'on observe —
# mais on ne peut alors pas parler d'évolution d'une même eau (§2.3).
VUE_PANEL_EVOLUTION = """
CREATE OR REPLACE VIEW v_panel_evolution AS
WITH suite AS (
    SELECT
        v.*,
        LAG(code_prelevement)       OVER w AS prec_code,
        LAG(date_prelevement)       OVER w AS prec_date,
        LAG(panel)                  OVER w AS prec_panel,
        LAG(nb_panel)               OVER w AS prec_nb,
        LAG(nom_installation_amont) OVER w AS prec_installation,
        LAG(reseau_norm)            OVER w AS prec_reseau
    FROM v_panel_bulletin v
    WINDOW w AS (PARTITION BY code_insee ORDER BY date_prelevement)
)
SELECT
    code_insee, commune, dept,
    prec_date          AS date_precedente,
    date_prelevement   AS date_courante,
    prec_code          AS prelevement_precedent,
    code_prelevement   AS prelevement_courant,
    prec_installation  AS installation_precedente,
    nom_installation_amont AS installation_courante,
    (prec_installation IS NOT NULL AND nom_installation_amont IS NOT NULL)
                       AS identite_certaine,
    CASE WHEN prec_installation IS NOT NULL AND nom_installation_amont IS NOT NULL
         THEN nom_installation_amont = prec_installation
         ELSE reseau_norm = prec_reseau
    END                AS meme_point_deau,
    prec_nb            AS panel_precedent,
    nb_panel           AS panel_courant,
    nb_panel - prec_nb AS variation_panel,
    len(list_filter(prec_panel, x -> NOT list_contains(panel, x)))      AS nb_abandonnes,
    len(list_filter(panel, x -> NOT list_contains(prec_panel, x)))      AS nb_nouveaux,
    list_filter(prec_panel, x -> NOT list_contains(panel, x))           AS abandonnes,
    list_filter(panel, x -> NOT list_contains(prec_panel, x))           AS nouveaux
FROM suite
WHERE prec_code IS NOT NULL
ORDER BY commune, date_courante;
"""

# Ce qui a cessé d'être cherché, paramètre par paramètre.
#
# À l'échelle du corpus actuel (45 bulletins), c'est une curiosité. À celle de
# plusieurs centaines de communes, c'est le matériau : un paramètre abandonné
# partout à la même période ne relève plus du choix local.
VUE_PARAMETRES_ABANDONNES = """
CREATE OR REPLACE VIEW v_parametres_abandonnes AS
WITH detail AS (
    SELECT code_insee, commune, dept, date_courante, meme_point_deau,
           UNNEST(abandonnes) AS cle_param
    FROM v_panel_evolution
),
libelles AS (
    SELECT COALESCE(code_parametre, libelle_norm) AS cle_param,
           ANY_VALUE(libelle_parametre)           AS libelle
    FROM mesures GROUP BY 1
)
SELECT
    COALESCE(l.libelle, d.cle_param) AS libelle_parametre,
    d.cle_param,
    COUNT(*)                         AS nb_abandons,
    COUNT(DISTINCT d.code_insee)     AS nb_communes,
    COUNT(*) FILTER (WHERE d.meme_point_deau) AS nb_abandons_meme_point,
    MIN(d.date_courante)             AS premier_constat,
    MAX(d.date_courante)             AS dernier_constat
FROM detail d
LEFT JOIN libelles l ON l.cle_param = d.cle_param
GROUP BY 1, 2
ORDER BY nb_abandons DESC, libelle_parametre;
"""

# La part des bulletins complets qui cherchent un paramètre, année par année.
#
# C'est la vue qui n'a pas besoin d'apparier quoi que ce soit : elle ne compare
# pas deux bulletins, elle regarde une population. Un paramètre dont la
# présence passe de 90 % à 5 % en deux ans a été retiré des programmes, et
# aucune commune n'a eu à le décider.
#
# Elle ne dit RIEN de la qualité de l'eau, et tout de ce qu'on a choisi d'en
# savoir. Le dénominateur est affiché : sur trois bulletins dans l'année, un
# pourcentage ne veut rien dire.
#
# LE ZÉRO DOIT EXISTER. Corrigé le 9 août 2026. La vue ne produisait de ligne
# que pour les couples (année, paramètre) effectivement cherchés : un paramètre
# tombé à 0 % n'avait plus de ligne du tout. Le détecteur était donc aveugle au
# seul cas qui l'intéresse vraiment — l'abandon complet — et tout consommateur
# devait le retrouver par une anti-jointure qu'il n'avait aucune raison
# d'écrire. C'est le §2.4 transposé du laboratoire au programme d'analyse :
# l'absence de trace n'est pas l'absence de fait, et elle doit s'écrire.
#
# D'où la grille pleine : chaque paramètre connu du corpus × chaque année
# documentée, à 0 % quand il n'a pas été cherché. Le libellé est désormais pris
# une fois pour toutes sur l'ensemble du corpus, et non année par année : un
# paramètre absent d'une année n'y a pas de libellé à lire.
VUE_PARAMETRE_PRESENCE = """
CREATE OR REPLACE VIEW v_parametre_presence AS
WITH bulletins AS (
    SELECT YEAR(date_prelevement) AS annee, COUNT(*) AS nb_bulletins
    FROM prelevements WHERE est_complet GROUP BY 1
),
params AS (
    SELECT COALESCE(m.code_parametre, m.libelle_norm) AS cle_param,
           ANY_VALUE(m.libelle_parametre)             AS libelle
    FROM prelevements p
    JOIN mesures m ON m.code_prelevement = p.code_prelevement
    WHERE p.est_complet
    GROUP BY 1
),
cherches AS (
    SELECT YEAR(p.date_prelevement)                     AS annee,
           COALESCE(m.code_parametre, m.libelle_norm)   AS cle_param,
           COUNT(DISTINCT p.code_prelevement)           AS nb_recherche
    FROM prelevements p
    JOIN mesures m ON m.code_prelevement = p.code_prelevement
    WHERE p.est_complet
    GROUP BY 1, 2
)
SELECT b.annee, x.cle_param, x.libelle AS libelle_parametre,
       COALESCE(c.nb_recherche, 0) AS nb_recherche,
       b.nb_bulletins,
       ROUND(100.0 * COALESCE(c.nb_recherche, 0) / b.nb_bulletins, 1)
                                   AS pct_bulletins
FROM bulletins b
CROSS JOIN params x
LEFT JOIN cherches c ON c.annee = b.annee AND c.cle_param = x.cle_param
ORDER BY x.libelle, b.annee;
"""

# La même chose, stratifiée par département — le contre-feu de la vue
# précédente.
#
# Ajoutée le 9 août 2026. Une présence nationale qui chute peut avoir deux
# causes, et elles n'ont rien à voir : le programme d'analyse a changé, ou bien
# c'est le CORPUS qui a changé de composition. Le corpus actuel le montre en
# clair — 7 bulletins sur 2 départements en 2022, 13 sur 6 en 2026. Un
# paramètre qui serait une habitude du seul Tarn passerait mécaniquement de
# 100 % à 20 % en n'ayant jamais été retiré nulle part.
#
# C'est le §2.11 poussé d'un cran : l'effort de recherche se déclare, et le
# dénominateur d'un taux agrégé doit dire de QUI il est le dénominateur.
#
# Le corpus ne porte pas le laboratoire — `code_lieu_analyse` vaut « L » sur les
# 45 bulletins. Le département est donc la strate la plus fine dont on dispose
# pour approcher les trois hypothèses du chantier (une logique nationale, un
# laboratoire, une date d'arrêté), et il faut le lire comme un proxy, pas comme
# une explication.
#
# L'univers est borné au département : un paramètre jamais cherché dans le 17
# n'y produit pas de ligne à 0 %. Sans cette borne, la grille pleine noierait
# le signal sous des zéros qui ne veulent rien dire — et elle exploserait au
# passage à l'échelle (chantier C6).
VUE_PARAMETRE_PRESENCE_DEPT = """
CREATE OR REPLACE VIEW v_parametre_presence_dept AS
WITH bulletins AS (
    SELECT YEAR(p.date_prelevement) AS annee,
           c.code_departement       AS dept,
           COUNT(*)                 AS nb_bulletins
    FROM prelevements p
    JOIN communes c ON c.code_insee = p.code_insee
    WHERE p.est_complet
    GROUP BY 1, 2
),
cherches AS (
    SELECT YEAR(p.date_prelevement)                     AS annee,
           c.code_departement                           AS dept,
           COALESCE(m.code_parametre, m.libelle_norm)   AS cle_param,
           COUNT(DISTINCT p.code_prelevement)           AS nb_recherche
    FROM prelevements p
    JOIN communes c ON c.code_insee = p.code_insee
    JOIN mesures  m ON m.code_prelevement = p.code_prelevement
    WHERE p.est_complet
    GROUP BY 1, 2, 3
),
params_dept AS (
    SELECT DISTINCT dept, cle_param FROM cherches
),
libelles AS (
    SELECT COALESCE(m.code_parametre, m.libelle_norm) AS cle_param,
           ANY_VALUE(m.libelle_parametre)             AS libelle
    FROM prelevements p
    JOIN mesures m ON m.code_prelevement = p.code_prelevement
    WHERE p.est_complet
    GROUP BY 1
)
SELECT b.annee, b.dept, x.cle_param, l.libelle AS libelle_parametre,
       COALESCE(c.nb_recherche, 0) AS nb_recherche,
       b.nb_bulletins,
       ROUND(100.0 * COALESCE(c.nb_recherche, 0) / b.nb_bulletins, 1)
                                   AS pct_bulletins
FROM bulletins b
JOIN params_dept x ON x.dept = b.dept
LEFT JOIN cherches c
       ON c.annee = b.annee AND c.dept = b.dept AND c.cle_param = x.cle_param
LEFT JOIN libelles l ON l.cle_param = x.cle_param
ORDER BY l.libelle, b.dept, b.annee;
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

# ---------------------------------------------------------------------------
# LE MÉLANGE : ce qu'un réseau moyenne avant d'arriver au robinet
# ---------------------------------------------------------------------------
#
# Chantier C7 (docs/CHANTIERS.md), premier pas : DÉNOMBRER les mélanges déjà
# lisibles, sans aucune collecte nouvelle. L'hypothèse à instruire est celle de
# Yannick — « si pour une commune on mélange 3 captages alors la moyenne peut
# être bonne, même si un captage est hors caractéristique » — c'est-à-dire la
# dilution tenant lieu de dépollution (CLAUDE.md §7bis).
#
# CE QUE DIT LE CHAMP, ET COMMENT ON LE SAIT
# ------------------------------------------
# Hub'Eau attache à chaque prélèvement une liste `reseaux`, dont chaque entrée
# porte `code`, `nom` et parfois `debit` — une chaîne du genre « 80 % ».
# `hubeau.bulletin_meta` l'aplatit en `codes_reseaux` / `noms_reseaux`, séparés
# par des barres verticales, la part restant collée au nom : « LOUBERS (80 %) ».
#
# La documentation de l'API ne décrit pas ce `debit`. Sa signification est donc
# DÉDUITE du corpus, et deux réseaux la démontrent en se refermant sur 100 % :
#
#   LOUBERS (081000643)          LOUBERS BATESTE 80 %  +  BOUYSSOUNADE 20 %
#   VALLEE DU CEROU (081004092)  BOURNAZEL RÉSERVOIR 50 %  +  MOULIN GALAT 50 %
#
# Deux installations distinctes, deux bulletins distincts, une somme exacte :
# `debit` est la PART DU DÉBIT DU RÉSEAU APPORTÉE PAR L'INSTALLATION AMONT DE CE
# PRÉLÈVEMENT. La lecture concurrente — « part de l'eau de la commune » — est
# réfutée par Loubers, où la même commune et le même réseau portent 80 % sur un
# bulletin et 20 % sur l'autre ; et par le Moulin Galat, qui alimente quatre
# réseaux à quatre parts différentes. C'est une déduction vérifiée deux fois,
# pas une lecture de texte : elle est marquée comme telle dans
# docs/METHODE_DILUTION.md et doit le rester tant que la source ne l'écrit pas.
#
# TROIS PIÈGES, INSCRITS DANS LE CODE
# -----------------------------------
# 1. UNE PART ABSENTE N'EST PAS 100 %. Le `debit` disparaît quand la source ne
#    rattache le prélèvement à aucune installation amont — « CHALLET » en 2026
#    contre « CHALLET (100 %) » en 2022, sans que rien n'ait changé au réseau.
#    C'est le §2.4 transposé au mélange : l'absence d'information n'est pas une
#    information d'absence. `part_reseau_pct` reste donc NULL, et
#    `part_non_attribuee` est NULL — jamais 100 — quand rien n'est déclaré.
# 2. UN RÉSEAU PEUT FIGURER DEUX FOIS DANS LE MÊME BULLETIN, sous deux libellés
#    et le même code : « BERCHERES ST GERMAIN|SECTEUR BERCHERES ST GERMAIN »,
#    codes `028000707|028000707`. Ce n'est pas un mélange, c'est un doublon de
#    libellé : le regroupement se fait sur le CODE, et `nb_libelles` le signale.
# 3. DEUX SOURCES NE FONT PAS UN MÉLANGE SI L'UNE DÉCLARE 100 %. Laparrouquial
#    porte deux clés d'installation, `081000936 STATION LA MAFRESIE` puis
#    `081004209 STATION DE LA MAFRESIE` : c'est la même station recodée (cf.
#    chantier C3). Un mélange n'est reconstitué que si PLUSIEURS sources
#    déclarent chacune moins de 100 %.
#
# CE QUE CES VUES NE DISENT PAS, ET NE DIRONT JAMAIS SEULES
# ---------------------------------------------------------
# Elles voient le mélange ENTRE INSTALLATIONS, jamais entre captages. Une usine
# alimentée par trois forages dont un seul est dégradé apparaît ici comme une
# source unique à 100 % : la dilution y est déjà faite, en amont du seul point
# que la donnée expose. Le maillon captage → usine n'est pas publié par Hub'Eau
# et ne pourra être établi que par inférence géographique — donc affiché comme
# une hypothèse, jamais comme un fait (§7bis).
# Et diluer est légal : ce qui est interrogé ici est la norme, qui note l'eau
# distribuée et ne demande rien sur ce qu'on y a mêlé, jamais l'exploitant qui
# l'applique (§2.1).

# a) La décomposition : une ligne par (bulletin × réseau desservi).
VUE_RESEAU_BULLETIN = """
CREATE OR REPLACE VIEW v_reseau_bulletin AS
WITH eclate AS (
    SELECT p.code_prelevement, p.code_insee, p.date_prelevement, p.est_complet,
           p.code_installation_amont, p.nom_installation_amont,
           UNNEST(str_split(p.codes_reseaux, '|')) AS code_brut,
           UNNEST(str_split(p.noms_reseaux,  '|')) AS nom_brut
    FROM prelevements p
    WHERE p.codes_reseaux IS NOT NULL AND p.noms_reseaux IS NOT NULL
      -- Les deux listes sont appariées par POSITION. Si elles n'ont pas la
      -- même longueur, l'appariement colle un nom au mauvais code : on
      -- n'apparie pas, et `v_reseaux_illisibles` dit lesquels sont écartés.
      AND len(str_split(p.codes_reseaux, '|')) = len(str_split(p.noms_reseaux, '|'))
),
lu AS (
    SELECT e.*,
           trim(regexp_replace(nom_brut, '\\s*\\(\\d+([.,]\\d+)?\\s*%\\)', '', 'g')) AS nom_reseau,
           TRY_CAST(replace(regexp_extract(nom_brut, '\\((\\d+([.,]\\d+)?)\\s*%\\)', 1),
                            ',', '.') AS DOUBLE) AS part
    FROM eclate e
)
SELECT code_prelevement, code_insee, date_prelevement, est_complet,
       code_installation_amont, nom_installation_amont,
       trim(code_brut)  AS code_reseau,
       MIN(nom_reseau)  AS nom_reseau,
       MAX(part)        AS part_reseau_pct,
       COUNT(*)         AS nb_libelles
FROM lu
GROUP BY 1, 2, 3, 4, 5, 6, 7;
"""

# Contrôle : les prélèvements que la décomposition a dû écarter. Un contrôle
# qui se tait est un défaut ; celui-ci doit rester vide.
VUE_RESEAUX_ILLISIBLES = """
CREATE OR REPLACE VIEW v_reseaux_illisibles AS
SELECT code_prelevement, code_insee, date_prelevement,
       codes_reseaux, noms_reseaux,
       len(str_split(codes_reseaux, '|')) AS nb_codes,
       len(str_split(noms_reseaux,  '|')) AS nb_noms
FROM prelevements
WHERE codes_reseaux IS NULL OR noms_reseaux IS NULL
   OR len(str_split(codes_reseaux, '|')) <> len(str_split(noms_reseaux, '|'))
ORDER BY code_prelevement;
"""

# b) Par bulletin : l'eau que décrit ce bulletin est-elle un mélange lisible ?
#    `nb_reseaux_melanges` compte les réseaux que l'installation de ce
#    prélèvement n'alimente PAS seule — ceux dont l'eau vient donc, pour partie,
#    d'ailleurs. Le Moulin Galat alimente quatre réseaux, trois à 100 % et un à
#    50 % : le bulletin est en partie un mélange, et un booléen seul le dirait
#    mal.
VUE_MELANGE_BULLETIN = """
CREATE OR REPLACE VIEW v_melange_bulletin AS
SELECT
    b.code_prelevement,
    b.code_insee,
    c.nom                   AS commune,
    c.code_departement      AS dept,
    b.date_prelevement,
    b.est_complet,
    b.code_installation_amont,
    b.nom_installation_amont,
    COUNT(*)                                                  AS nb_reseaux_desservis,
    COUNT(*) FILTER (WHERE b.part_reseau_pct IS NOT NULL)     AS nb_parts_declarees,
    COUNT(*) FILTER (WHERE b.part_reseau_pct < 100)           AS nb_reseaux_melanges,
    MIN(b.part_reseau_pct)                                    AS part_min_pct,
    MAX(b.part_reseau_pct)                                    AS part_max_pct,
    COALESCE(MIN(b.part_reseau_pct) < 100, FALSE)             AS melange_lisible,
    string_agg(b.nom_reseau
               || COALESCE(' ' || CAST(b.part_reseau_pct AS VARCHAR) || ' %', ' (part non déclarée)'),
               ' | ' ORDER BY b.part_reseau_pct NULLS LAST)   AS reseaux
FROM v_reseau_bulletin b
JOIN communes c ON c.code_insee = b.code_insee
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8;
"""

# c) Par réseau : que sait-on de ce qui entre dans ce robinet-là ?
#
#    `part_non_attribuee` est le chiffre du chantier : ce que le réseau reçoit
#    d'une installation que le corpus ne connaît pas. 75 % pour CHARTRES S1 veut
#    dire que trois quarts de l'eau distribuée viennent d'ailleurs, et qu'aucun
#    bulletin ne nous dit d'où. Il vaut NULL — pas 100 — quand aucune part n'est
#    déclarée : on ne sait alors même pas s'il y a mélange.
VUE_MELANGE_RESEAU = """
CREATE OR REPLACE VIEW v_melange_reseau AS
WITH par_source AS (
    -- Une ligne par (réseau, installation). Un même couple peut porter
    -- plusieurs bulletins : on retient la part la plus récemment DÉCLARÉE, un
    -- bulletin muet ne devant pas effacer une part connue.
    SELECT b.code_reseau,
           MIN(b.nom_reseau) AS nom_reseau,
           COALESCE(b.code_installation_amont, b.nom_installation_amont) AS cle_installation,
           MIN(b.nom_installation_amont) AS nom_installation,
           max_by(b.part_reseau_pct, b.date_prelevement)
                 FILTER (WHERE b.part_reseau_pct IS NOT NULL) AS part_pct,
           MAX(b.date_prelevement)               AS derniere_date,
           COUNT(*)                              AS nb_bulletins,
           COUNT(*) FILTER (WHERE b.est_complet) AS nb_complets
    FROM v_reseau_bulletin b
    GROUP BY b.code_reseau, COALESCE(b.code_installation_amont, b.nom_installation_amont)
),
communes_par_reseau AS (
    -- Les communes qui PORTENT UN BULLETIN sur ce réseau. Ce n'est pas le
    -- nombre de communes desservies : une commune rattachée au réseau sans
    -- bulletin propre (`couverture_communes.rattachee_reseau`) n'y figure pas.
    -- Le rattachement est écrit au figeage, cette vue lit la base brute.
    SELECT code_reseau, COUNT(DISTINCT code_insee) AS nb_communes
    FROM v_reseau_bulletin GROUP BY 1
),
agrege AS (
    SELECT
        s.code_reseau,
        MIN(s.nom_reseau)                                          AS nom_reseau,
        COUNT(*) FILTER (WHERE s.cle_installation IS NOT NULL)     AS nb_sources_identifiees,
        COUNT(*) FILTER (WHERE s.part_pct IS NOT NULL)             AS nb_parts_declarees,
        COUNT(*) FILTER (WHERE s.part_pct < 100)                   AS nb_sources_partielles,
        ROUND(SUM(s.part_pct), 1)                                  AS somme_parts_connues,
        MIN(s.part_pct)                                            AS part_min_pct,
        MAX(s.part_pct)                                            AS part_max_pct,
        SUM(s.nb_bulletins)                                        AS nb_bulletins,
        SUM(s.nb_complets)                                         AS nb_bulletins_complets,
        COUNT(*) FILTER (WHERE s.nb_complets > 0
                           AND s.cle_installation IS NOT NULL)     AS nb_sources_analysees,
        MAX(s.derniere_date)                                       AS derniere_date,
        string_agg(COALESCE(s.nom_installation, '(installation non renseignée)')
                   || COALESCE(' ' || CAST(s.part_pct AS VARCHAR) || ' %',
                               ' (part non déclarée)'),
                   ' | ' ORDER BY s.part_pct DESC NULLS LAST)      AS sources
    FROM par_source s
    GROUP BY s.code_reseau
)
SELECT
    a.code_reseau, a.nom_reseau, k.nb_communes,
    a.nb_sources_identifiees, a.nb_parts_declarees, a.nb_sources_partielles,
    a.nb_sources_analysees,
    a.somme_parts_connues, a.part_min_pct, a.part_max_pct,
    -- Ce qui entre dans ce réseau sans qu'aucun bulletin ne dise d'où.
    CASE WHEN a.nb_parts_declarees = 0 THEN NULL
         ELSE ROUND(100 - a.somme_parts_connues, 1) END       AS part_non_attribuee,
    CASE
        WHEN a.nb_parts_declarees = 0                THEN 'non_declare'
        WHEN a.somme_parts_connues > 100.5           THEN 'incoherent'
        WHEN a.part_max_pct >= 100                   THEN 'source_unique_declaree'
        WHEN a.nb_sources_partielles >= 2
             AND a.somme_parts_connues >= 99.5       THEN 'melange_reconstitue'
        ELSE 'melange_partiel'
    END                                                       AS statut_melange,
    -- « lisible », pas « inexistant » : un réseau dont aucune part n'est
    -- déclarée peut parfaitement être un mélange, on ne le voit simplement
    -- pas. C'est `statut_melange = 'non_declare'` qui porte cette nuance.
    COALESCE(a.part_min_pct < 100, FALSE)                     AS melange_lisible,
    a.nb_bulletins, a.nb_bulletins_complets, a.derniere_date, a.sources
FROM agrege a
JOIN communes_par_reseau k ON k.code_reseau = a.code_reseau
ORDER BY melange_lisible DESC, part_non_attribuee DESC NULLS LAST, a.nom_reseau;
"""

# LE PANEL CONSTANT — ce qui rend une série temporelle lisible.
#
# Ajouté le 9 août 2026, après la collecte du Tarn. Le §2.11 pose depuis le
# même jour qu'« aucune série temporelle à panel variable » ne doit être
# produite : comparer 2019 et 2026 sans se restreindre aux paramètres cherchés
# les deux années fait passer une baisse des RECHERCHES pour une baisse des
# DÉTECTIONS. La règle était écrite, rien ne l'outillait.
#
# Définition : un paramètre est constant sur un département s'il a été cherché
# sur au moins 75 % des bulletins complets de CHAQUE année documentée. Pas de
# couple d'années de référence à choisir — donc rien à arbitrer, et la série se
# recalcule seule quand le corpus grandit.
#
# `nb_annees_documentees` est le garde-fou et il s'affiche : sur un département
# d'une seule année, « constant » ne veut rien dire (§2.11 — un taux sans son
# dénominateur n'est pas un indicateur).
VUE_PANEL_CONSTANT = """
CREATE OR REPLACE VIEW v_panel_constant AS
WITH annees AS (
    SELECT dept, COUNT(DISTINCT annee) AS nb_annees
    FROM v_parametre_presence_dept GROUP BY 1
)
SELECT p.dept,
       p.cle_param,
       ANY_VALUE(p.libelle_parametre) AS libelle_parametre,
       ANY_VALUE(a.nb_annees)         AS nb_annees_documentees
FROM v_parametre_presence_dept p
JOIN annees a ON a.dept = p.dept
GROUP BY 1, 2
HAVING COUNT(*) FILTER (WHERE p.pct_bulletins >= 75) = ANY_VALUE(a.nb_annees);
"""

# La série qu'on a le droit de lire : le taux de quantification à panel
# constant, année par année et département par département.
#
# C'est le pendant temporel de `depassements_pour_mille` (§2.11) : un TAUX, et
# sur un périmètre de mesure qui ne bouge pas. Il ne dit pas la qualité de
# l'eau — il dit ce que le même effort de recherche trouve d'une année à
# l'autre.
VUE_SERIE_PANEL_CONSTANT = """
CREATE OR REPLACE VIEW v_serie_panel_constant AS
SELECT c.code_departement                      AS dept,
       YEAR(p.date_prelevement)                AS annee,
       ANY_VALUE(k.nb_annees_documentees)      AS nb_annees_documentees,
       COUNT(DISTINCT k.cle_param)             AS nb_panel_constant,
       COUNT(DISTINCT p.code_prelevement)      AS nb_bulletins,
       COUNT(DISTINCT p.code_insee)            AS nb_communes,
       COUNT(*)                                AS nb_mesures,
       COUNT(*) FILTER (WHERE m.est_quantifie) AS nb_quantifiees,
       ROUND(1000.0 * COUNT(*) FILTER (WHERE m.est_quantifie) / COUNT(*), 2)
                                               AS quantifiees_pour_mille,
       COUNT(DISTINCT p.code_insee) FILTER (WHERE m.est_quantifie)
                                               AS nb_communes_touchees
FROM prelevements p
JOIN communes c ON c.code_insee = p.code_insee
JOIN mesures  m ON m.code_prelevement = p.code_prelevement
JOIN v_panel_constant k
     ON k.dept = c.code_departement
    AND k.cle_param = COALESCE(m.code_parametre, m.libelle_norm)
WHERE p.est_complet
GROUP BY 1, 2
ORDER BY 1, 2;
"""

VUES = [VUE_REF, VUE_VERDICT, VUE_PRELEVEMENT, VUE_NON_APPARIES,
        VUE_COUVERTURE_REF, VUE_REGLE_FAMILLE, VUE_ECARTS, VUE_UNITES,
        VUE_SEUILS_SANS_DATE, VUE_EFFORT, VUE_CONDITIONS,
        VUE_PANEL, VUE_PANEL_EVOLUTION, VUE_PARAMETRES_ABANDONNES,
        VUE_PARAMETRE_PRESENCE, VUE_PARAMETRE_PRESENCE_DEPT,
        VUE_RESEAU_BULLETIN, VUE_RESEAUX_ILLISIBLES,
        VUE_MELANGE_BULLETIN, VUE_MELANGE_RESEAU,
        # après VUE_PARAMETRE_PRESENCE_DEPT, dont elles dépendent
        VUE_PANEL_CONSTANT, VUE_SERIE_PANEL_CONSTANT]


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

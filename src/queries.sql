-- =========================================================================
-- Observatoire de la potabilité réglementaire — requêtes de référence
--
--   duckdb data/eau.duckdb
--   .read src/queries.sql
--
-- Toutes les requêtes d'analyse filtrent sur est_complet. Sans ce filtre,
-- les analyses de routine noient les analyses complètes et la réponse est
-- toujours « tout va bien » (CLAUDE.md §2.3).
-- =========================================================================


-- -------------------------------------------------------------------------
-- 0. CONTRÔLE — à lancer après chaque collecte, avant toute analyse
-- -------------------------------------------------------------------------

-- 0.a Que contient la base ?
SELECT
    COUNT(DISTINCT code_insee)                         AS communes,
    COUNT(*)                                           AS prelevements,
    COUNT(*) FILTER (WHERE est_complet)                AS dont_complets,
    MIN(date_prelevement)                              AS plus_ancien,
    MAX(date_prelevement)                              AS plus_recent
FROM prelevements;

-- 0.a bis Le dénominateur : sur combien de paramètres porte réellement chaque
--     verdict ? Une conformité annoncée sans ce chiffre est une demi-vérité.
SELECT commune, date_prelevement, nom_installation_amont,
       nb_mesures_lues, nb_mesures_notees, pct_couverture,
       nb_notees_referentiel, nb_notees_declare, nb_sans_seuil
FROM v_prelevement_verdict
WHERE est_complet
ORDER BY pct_couverture;

-- 0.b Paramètres mesurés qu'aucune règle n'a rattachés au référentiel.
--     Chacun est une mesure INVISIBLE pour l'analyse : elle existe en base
--     et ne pèse sur aucun verdict. Les lignes en tête (quantifiées, sur
--     beaucoup de communes) sont à ajouter au référentiel ou aux alias.
SELECT * FROM v_parametres_non_apparies LIMIT 40;

-- 0.c Lignes du référentiel jamais rencontrées dans les mesures :
--     soit le paramètre n'est pas recherché par le contrôle sanitaire,
--     soit son libellé diffère et il manque un alias.
SELECT * FROM v_referentiel_jamais_mesure;

-- 0.c bis Contrôles de qualité introduits avec la couche de couverture.
SELECT * FROM v_regle_famille_appliquee LIMIT 40;   -- à relire : rattachements automatiques
SELECT * FROM v_ecarts_referentiel_source;          -- notre seuil 2026 contre celui déclaré
SELECT * FROM v_unites_incomparables;               -- aucun verdict produit, faute d'unité comparable

-- 0.d Taux d'appariement par mode : plus la part 'code_parametre' est
--     élevée, plus la base est robuste au passage à l'échelle.
SELECT
    COALESCE(mode_appariement, 'NON APPARIE') AS mode,
    COUNT(*)                                  AS nb_mesures,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM v_mesures_ref
GROUP BY 1 ORDER BY nb_mesures DESC;


-- -------------------------------------------------------------------------
-- 1. LA REQUÊTE DE LA THÈSE
--    Des bulletins complets, déclarés conformes aujourd'hui, qui ne
--    l'auraient pas été selon la grille de 2016. Chaque ligne est un cas.
-- -------------------------------------------------------------------------
SELECT commune, dept, date_prelevement, nb_parametres, nb_bascules,
       conclusion_conformite
FROM v_prelevement_verdict
WHERE est_complet
  AND nb_depasse_2026 = 0
  AND nb_bascules > 0
ORDER BY nb_bascules DESC, date_prelevement DESC;


-- 1.b Le détail : quelle substance, à quelle valeur, contre quels seuils.
--     C'est cette table qui se lit dans une fiche citoyenne.
SELECT v.code_insee, p.commune, p.date_prelevement,
       v.libelle_parametre, v.famille,
       v.resultat_num, v.unite,
       v.seuil_2016, v.seuil_2026, v.seuil_strict,
       v.statut_2026, v.fiabilite
FROM v_mesures_verdict v
JOIN v_prelevement_verdict p USING (code_prelevement)
WHERE p.est_complet AND v.bascule_2016_2026
ORDER BY p.date_prelevement DESC, v.resultat_num DESC;


-- -------------------------------------------------------------------------
-- 2. OÙ LA NORME A BOUGÉ — le classement des paramètres responsables
--    À l'échelle d'un département, cette requête dit quels déplacements de
--    seuil produisent effectivement l'effet, et lesquels sont théoriques.
-- -------------------------------------------------------------------------
SELECT libelle_parametre, famille,
       seuil_2016, seuil_2026, statut_2026,
       COUNT(*)                                    AS nb_bascules,
       COUNT(DISTINCT code_insee)                  AS nb_communes,
       ROUND(MIN(resultat_num), 4)                 AS mini,
       ROUND(MAX(resultat_num), 4)                 AS maxi
FROM v_mesures_verdict v
WHERE bascule_2016_2026
GROUP BY 1,2,3,4,5
ORDER BY nb_bascules DESC;


-- -------------------------------------------------------------------------
-- 3. L'AXE INTERNATIONAL — conforme en France, pas ailleurs
-- -------------------------------------------------------------------------
SELECT p.commune, p.dept, p.date_prelevement,
       v.libelle_parametre, v.famille,
       v.resultat_num, v.unite,
       v.seuil_2026        AS limite_fr,
       v.seuil_strict      AS seuil_le_plus_strict,
       v.base_seuil_strict AS pays_ou_reference,
       v.fiabilite
FROM v_mesures_verdict v
JOIN v_prelevement_verdict p USING (code_prelevement)
WHERE p.est_complet
  AND v.depasse_strict
  AND NOT COALESCE(v.depasse_2026, FALSE)
ORDER BY v.famille, v.resultat_num DESC;


-- -------------------------------------------------------------------------
-- 4. CE QU'ON NE SAIT PAS — les indéterminés
--    La limite de quantification du laboratoire est au-dessus du seuil de
--    comparaison : on ne peut pas dire que l'eau respecte ce seuil, on peut
--    seulement dire qu'on ne sait pas. Ne jamais présenter ces lignes
--    comme des conformités (CLAUDE.md §2.4).
-- -------------------------------------------------------------------------
SELECT libelle_parametre, famille,
       COUNT(*)                    AS nb_mesures_indeterminees,
       COUNT(DISTINCT code_insee)  AS nb_communes,
       MIN(lq)                     AS meilleure_lq,
       ANY_VALUE(seuil_strict)     AS seuil_strict,
       ANY_VALUE(unite)            AS unite
FROM v_mesures_verdict
WHERE indetermine_strict
GROUP BY 1,2
ORDER BY nb_mesures_indeterminees DESC;


-- -------------------------------------------------------------------------
-- 5. LES SEUILS DIFFÉRÉS — ce qui dépassera sans que rien ne change
--    Plomb 5 µg/L et chrome total 25 µg/L s'appliquent au 1er janvier 2036.
--    Ces mesures sont conformes aujourd'hui et ne le seront plus alors.
-- -------------------------------------------------------------------------
SELECT p.commune, p.dept, p.date_prelevement,
       v.libelle_parametre, v.resultat_num, v.unite,
       v.seuil_2026 AS limite_actuelle,
       v.seuil_futur, v.date_applicabilite_futur
FROM v_mesures_verdict v
JOIN v_prelevement_verdict p USING (code_prelevement)
WHERE p.est_complet
  AND v.depasse_futur
  AND NOT COALESCE(v.depasse_2026, FALSE)
ORDER BY v.libelle_parametre, v.resultat_num DESC;


-- -------------------------------------------------------------------------
-- 6. CHARGE EN MICROPOLLUANTS DE SYNTHÈSE
--    Nombre de substances de synthèse effectivement QUANTIFIÉES dans un
--    bulletin complet — l'inverse du raisonnement réglementaire, qui note
--    substance par substance. Ce n'est pas encore un indice de danger
--    (cf. CLAUDE.md §7) : c'est un dénombrement, et il doit être présenté
--    comme tel.
-- -------------------------------------------------------------------------
SELECT p.commune, p.dept, p.date_prelevement, p.nb_parametres,
       COUNT(*)                                             AS nb_substances_quantifiees,
       COUNT(*) FILTER (WHERE v.famille = 'PFAS')           AS dont_pfas,
       COUNT(*) FILTER (WHERE v.famille = 'metabolite')     AS dont_metabolites,
       COUNT(*) FILTER (WHERE v.famille = 'pesticide')      AS dont_pesticides,
       p.conclusion_conformite
FROM v_mesures_verdict v
JOIN v_prelevement_verdict p USING (code_prelevement)
WHERE p.est_complet
  AND v.est_quantifie
  AND v.famille IN ('PFAS', 'metabolite', 'pesticide', 'organique')
GROUP BY 1,2,3,4,9
ORDER BY nb_substances_quantifiees DESC;


-- -------------------------------------------------------------------------
-- 7. SYNTHÈSE DÉPARTEMENTALE — la ligne à publier
-- -------------------------------------------------------------------------
SELECT dept,
       COUNT(*)                                                  AS bulletins_complets,
       COUNT(*) FILTER (WHERE nb_depasse_2026 = 0)               AS conformes_2026,
       COUNT(*) FILTER (WHERE nb_depasse_2016 > 0)               AS auraient_ete_non_conformes_2016,
       COUNT(*) FILTER (WHERE nb_depasse_2026 = 0
                        AND nb_bascules > 0)                     AS conformes_grace_au_deplacement,
       ROUND(100.0 * COUNT(*) FILTER (WHERE nb_depasse_2026 = 0
                        AND nb_bascules > 0) / COUNT(*), 1)      AS pct,
       COUNT(*) FILTER (WHERE nb_depasse_strict > 0)             AS non_conformes_seuil_strict
FROM v_prelevement_verdict
WHERE est_complet
GROUP BY dept
ORDER BY dept;


-- -------------------------------------------------------------------------
-- 8. LA SORTIE FIGÉE
--    Ce que la base a arrêté, et contre quelle grille. Tout chiffre publié
--    doit venir d'ici, pas d'une vue recalculée à la volée : une vue suit le
--    référentiel du jour, une ligne figée dit contre quoi elle a été calculée.
-- -------------------------------------------------------------------------
SELECT commune, date_prelevement, nom_installation_amont,
       nb_mesures_notees || '/' || nb_parametres AS notes_sur_mesures,
       pct_couverture, nb_depasse_2026, nb_bascules, nb_indetermines,
       nb_synthese_quantifiees, ROUND(charge_synthese_ug_l, 4) AS charge_ug_l,
       ROUND(indice_danger, 2) AS indice_danger, indice_danger_n,
       version_referentiel, calcule_le
FROM analyses_figees
ORDER BY calcule_le DESC, commune;


-- 8.b CE QUE COLORIE LA CARTE. « non_documentee » n'est ni conforme ni non
--     conforme : c'est une absence de donnée, et elle doit rester visible.
SELECT statut, COUNT(*) AS nb_communes
FROM couverture_communes
GROUP BY 1 ORDER BY 2 DESC;

SELECT commune, dept, lon, lat, statut, commune_prelevement,
       date_prelevement, pct_couverture
FROM couverture_communes
ORDER BY statut, commune;


-- 8.c LE DÉPLACEMENT DES SEUILS, VU PAR L'OUTIL LUI-MÊME.
--     Deux versions du référentiel figées sur le même prélèvement : la
--     différence est exactement ce que le projet cherche à rendre visible.
SELECT a.code_prelevement, a.commune,
       a.version_referentiel, a.calcule_le,
       a.nb_depasse_2026, a.nb_bascules, a.nb_mesures_notees
FROM analyses_figees a
WHERE a.code_prelevement IN (
    SELECT code_prelevement FROM analyses_figees
    GROUP BY code_prelevement HAVING COUNT(DISTINCT version_referentiel) > 1)
ORDER BY a.code_prelevement, a.calcule_le;

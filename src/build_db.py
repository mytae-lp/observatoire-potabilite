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

from common import DB_PATH, REF_CSV, ALIAS_CSV, norm, f, s

SCHEMA = """
CREATE TABLE IF NOT EXISTS communes (
    code_insee        VARCHAR PRIMARY KEY,
    nom               VARCHAR,
    code_departement  VARCHAR
);

CREATE TABLE IF NOT EXISTS prelevements (
    code_prelevement      VARCHAR PRIMARY KEY,
    code_insee            VARCHAR,
    nom_installation      VARCHAR,
    nom_distributeur      VARCHAR,
    date_prelevement      DATE,
    nb_parametres         INTEGER,
    est_complet           BOOLEAN,
    conclusion_conformite VARCHAR,
    conf_limites_bact     VARCHAR,
    conf_limites_pc       VARCHAR,
    conf_references_pc    VARCHAR,
    source_url            VARCHAR
);

CREATE TABLE IF NOT EXISTS mesures (
    code_prelevement  VARCHAR,
    code_insee        VARCHAR,
    code_parametre    VARCHAR,
    libelle_parametre VARCHAR,
    libelle_norm      VARCHAR,
    resultat_num      DOUBLE,
    resultat_alpha    VARCHAR,
    lq                DOUBLE,
    est_quantifie     BOOLEAN,
    unite             VARCHAR,
    limite_qualite    VARCHAR,
    PRIMARY KEY (code_prelevement, libelle_parametre)
);

CREATE TABLE IF NOT EXISTS referentiel_seuils (
    libelle_norm             VARCHAR PRIMARY KEY,
    code_parametre           VARCHAR,
    libelle                  VARCHAR,
    famille                  VARCHAR,
    unite                    VARCHAR,
    seuil_2016               DOUBLE,
    seuil_2026               DOUBLE,
    statut_2026              VARCHAR,
    seuil_futur              DOUBLE,
    date_applicabilite_futur DATE,
    seuil_strict             DOUBLE,
    base_seuil_strict        VARCHAR,
    pe_reglementaire         VARCHAR,
    pe_scientifique          VARCHAR,
    sources                  VARCHAR,
    fiabilite                VARCHAR
);

CREATE TABLE IF NOT EXISTS alias_parametres (
    alias_norm   VARCHAR PRIMARY KEY,
    libelle_norm VARCHAR,
    commentaire  VARCHAR
);
"""

# ---------------------------------------------------------------------------
# Vues
# ---------------------------------------------------------------------------

# 1) Résolution du rapprochement mesure <-> référentiel.
#    Priorité : code_parametre Hub'Eau (stable) > libellé normalisé > alias.
#    C'est cette cascade qui permet le passage à l'échelle : au-delà de
#    quelques communes, les variantes d'écriture rendent le seul libellé
#    insuffisant.
VUE_REF = """
CREATE OR REPLACE VIEW v_mesures_ref AS
SELECT
    m.*,
    COALESCE(r1.libelle_norm, r2.libelle_norm, r3.libelle_norm) AS ref_key,
    CASE
        WHEN r1.libelle_norm IS NOT NULL THEN 'code_parametre'
        WHEN r2.libelle_norm IS NOT NULL THEN 'libelle'
        WHEN r3.libelle_norm IS NOT NULL THEN 'alias'
        ELSE NULL
    END AS mode_appariement
FROM mesures m
LEFT JOIN referentiel_seuils r1
       ON r1.code_parametre IS NOT NULL AND r1.code_parametre = m.code_parametre
LEFT JOIN referentiel_seuils r2
       ON r2.libelle_norm = m.libelle_norm
LEFT JOIN alias_parametres a
       ON a.alias_norm = m.libelle_norm
LEFT JOIN referentiel_seuils r3
       ON r3.libelle_norm = a.libelle_norm;
"""

# 2) Le cœur du projet : la même mesure notée contre trois grilles.
#    Un dépassement exige est_quantifie = TRUE (cf. CLAUDE.md §2.4).
#    indetermine_strict : la LQ du laboratoire est au-dessus du seuil strict,
#    on ne peut donc RIEN conclure — ce n'est pas une conformité.
VUE_VERDICT = """
CREATE OR REPLACE VIEW v_mesures_verdict AS
SELECT
    v.code_insee,
    v.code_prelevement,
    v.libelle_parametre,
    v.code_parametre,
    v.mode_appariement,
    r.famille,
    v.resultat_num,
    v.lq,
    v.est_quantifie,
    v.unite,
    r.seuil_2016,
    r.seuil_2026,
    r.seuil_strict,
    r.base_seuil_strict,
    r.statut_2026,
    r.seuil_futur,
    r.date_applicabilite_futur,
    r.pe_reglementaire,
    r.pe_scientifique,
    r.fiabilite,

    (v.est_quantifie AND r.seuil_2016   IS NOT NULL AND v.resultat_num > r.seuil_2016)   AS depasse_2016,
    (v.est_quantifie AND r.seuil_2026   IS NOT NULL AND v.resultat_num > r.seuil_2026)   AS depasse_2026,
    (v.est_quantifie AND r.seuil_strict IS NOT NULL AND v.resultat_num > r.seuil_strict) AS depasse_strict,
    (v.est_quantifie AND r.seuil_futur  IS NOT NULL AND v.resultat_num > r.seuil_futur)  AS depasse_futur,

    -- LA BASCULE : dépassait la limite de 2016, ne dépasse pas celle de 2026.
    -- Ce n'est pas l'eau qui a changé, c'est la limite.
    (v.est_quantifie
       AND r.seuil_2016 IS NOT NULL AND r.seuil_2026 IS NOT NULL
       AND v.resultat_num >  r.seuil_2016
       AND v.resultat_num <= r.seuil_2026) AS bascule_2016_2026,

    -- Troisième état de verdict : ni conforme ni dépassement, indéterminé.
    (NOT v.est_quantifie AND v.lq IS NOT NULL
       AND r.seuil_strict IS NOT NULL AND v.lq > r.seuil_strict) AS indetermine_strict
FROM v_mesures_ref v
JOIN referentiel_seuils r ON r.libelle_norm = v.ref_key;
"""

# 3) Agrégat par prélèvement. est_complet reste porté ici : toute requête de
#    thèse doit filtrer dessus.
VUE_PRELEVEMENT = """
CREATE OR REPLACE VIEW v_prelevement_verdict AS
SELECT
    p.code_prelevement,
    p.code_insee,
    c.nom               AS commune,
    c.code_departement  AS dept,
    p.date_prelevement,
    p.nom_installation,
    p.nom_distributeur,
    p.nb_parametres,
    p.est_complet,
    p.conclusion_conformite,
    COUNT(v.libelle_parametre)                                    AS nb_mesures_notees,
    COUNT(*) FILTER (WHERE v.depasse_2016)                        AS nb_depasse_2016,
    COUNT(*) FILTER (WHERE v.depasse_2026)                        AS nb_depasse_2026,
    COUNT(*) FILTER (WHERE v.depasse_strict)                      AS nb_depasse_strict,
    COUNT(*) FILTER (WHERE v.depasse_futur)                       AS nb_depasse_futur,
    COUNT(*) FILTER (WHERE v.bascule_2016_2026)                   AS nb_bascules,
    COUNT(*) FILTER (WHERE v.indetermine_strict)                  AS nb_indetermines,
    COUNT(*) FILTER (WHERE v.est_quantifie
                     AND v.famille IN ('metabolite', 'PFAS', 'pesticide')) AS nb_polluants_synthese
FROM prelevements p
JOIN communes c ON c.code_insee = p.code_insee
LEFT JOIN v_mesures_verdict v ON v.code_prelevement = p.code_prelevement
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10;
"""

# 4) Diagnostic de couverture — à consulter après CHAQUE collecte.
#    Un paramètre non apparié est une mesure invisible pour l'analyse : elle
#    existe dans la base et ne pèse sur aucun verdict. À l'échelle d'un
#    département, c'est le premier endroit où regarder.
VUE_NON_APPARIES = """
CREATE OR REPLACE VIEW v_parametres_non_apparies AS
SELECT
    libelle_parametre,
    libelle_norm,
    ANY_VALUE(code_parametre)          AS code_parametre_observe,
    ANY_VALUE(unite)                   AS unite,
    COUNT(*)                           AS nb_mesures,
    COUNT(DISTINCT code_insee)         AS nb_communes,
    COUNT(*) FILTER (WHERE est_quantifie) AS nb_quantifiees,
    MAX(resultat_num) FILTER (WHERE est_quantifie) AS max_quantifie
FROM v_mesures_ref
WHERE ref_key IS NULL
GROUP BY 1, 2
ORDER BY nb_quantifiees DESC, nb_mesures DESC;
"""

# 5) Couverture du référentiel : quelles lignes du référentiel ne sont
#    jamais mesurées ? (l'inverse du diagnostic précédent)
VUE_COUVERTURE_REF = """
CREATE OR REPLACE VIEW v_referentiel_jamais_mesure AS
SELECT r.libelle, r.famille, r.fiabilite, r.sources
FROM referentiel_seuils r
LEFT JOIN (SELECT DISTINCT ref_key FROM v_mesures_ref WHERE ref_key IS NOT NULL) u
       ON u.ref_key = r.libelle_norm
WHERE u.ref_key IS NULL
ORDER BY r.famille, r.libelle;
"""

VUES = [VUE_REF, VUE_VERDICT, VUE_PRELEVEMENT, VUE_NON_APPARIES, VUE_COUVERTURE_REF]


def charger_referentiel(con, chemin=REF_CSV):
    """Charge referentiel_seuils.csv. Remplace intégralement la table."""
    con.execute("DELETE FROM referentiel_seuils")
    n, doublons = 0, []
    vus = set()
    with open(chemin, encoding="utf-8") as fh:
        for ligne in csv.DictReader(fh, delimiter=";"):
            libelle = s(ligne.get("libelle"))
            if not libelle:
                continue
            cle = norm(libelle)
            if cle in vus:
                doublons.append(libelle)
                continue
            vus.add(cle)
            con.execute(
                "INSERT INTO referentiel_seuils VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [
                    cle,
                    s(ligne.get("code_parametre")),
                    libelle,
                    s(ligne.get("famille")),
                    s(ligne.get("unite")),
                    f(ligne.get("seuil_2016")),
                    f(ligne.get("seuil_2026")),
                    s(ligne.get("statut_2026")),
                    f(ligne.get("seuil_futur")),
                    s(ligne.get("date_applicabilite_futur")),
                    f(ligne.get("seuil_strict")),
                    s(ligne.get("base_seuil_strict")),
                    s(ligne.get("pe_reglementaire")),
                    s(ligne.get("pe_scientifique")),
                    s(ligne.get("sources")),
                    s(ligne.get("fiabilite")),
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
        for ligne in csv.DictReader(fh, delimiter=";"):
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
        non_app = con.execute(
            "SELECT COUNT(*) FROM v_parametres_non_apparies"
        ).fetchone()[0]
        print(f"  → {non_app} libellé(s) mesuré(s) non apparié(s) au référentiel")
        print("    (SELECT * FROM v_parametres_non_apparies LIMIT 40)")

    con.close()
    print(f"\nbase prête : {db}")
    print("prochaine étape : python3 src/fetch_departement.py --dept <NN>")


if __name__ == "__main__":
    build(reset="--reset" in sys.argv)

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

Le plafond analytique
---------------------
Chantier C4, devenu la **onzième obligation d'affichage du §8bis** le 8 août
2026. Une mesure « non quantifiée » ne dit pas la même chose selon la
finesse du laboratoire : si sa limite de quantification est AU-DESSUS du seuil
auquel on compare, l'analyse ne voit rien là où la conformité se joue. On ne
peut alors pas dire que l'eau respecte la limite, seulement qu'on ne sait pas
(CLAUDE.md §2.4, vu par le bout de l'instrument).

Trois objets le portent, du plus sûr au plus synthétique :
  - `verdicts_figes.lq_aveugle` / `lq_rapport_seuil` — au paramètre ;
  - `analyses_figees.nb_aveugles` / `aveugles_pour_mille` — au bulletin, et
    c'est le TAUX qui est comparable d'un bulletin à l'autre, jamais le compte
    (§2.11) ;
  - la table `lq_corpus` — l'étendue des LQ observées pour chaque paramètre,
    qui permet de situer celle d'un bulletin. Elle est estampillée comme le
    reste parce qu'elle bouge avec le corpus : c'est le plus fin IDENTIFIÉ,
    jamais le plus fin qui existe (§2.14).

Une LQ élevée n'est pas une négligence : c'est une capacité d'instrument. On
examine ce que le dispositif permet de savoir, on n'accuse pas le laboratoire —
pas plus qu'on n'accuse l'exploitant (§2.1).
"""
import argparse
import datetime
import hashlib
import os
import sys
import time

import duckdb

from common import DB_PATH, REF_CSV, ALIAS_CSV, RACINE

REGLES_CSV = os.path.join(RACINE, "referentiel", "regles_famille.csv")

# Familles considérées comme substances de synthèse pour la charge cumulée.
FAMILLES_SYNTHESE = ("pesticide", "metabolite", "PFAS", "organique")

SCHEMA_FIGE = """
-- Sous quelle empreinte de CODE chaque version de référentiel a été figée.
-- C'est ce qui rend le figeage incrémental sûr : voir `version_moteur()`.
-- Une seule ligne par version — la dernière empreinte utilisée.
CREATE TABLE IF NOT EXISTS figeage_moteur (
    version_referentiel VARCHAR PRIMARY KEY,
    empreinte_moteur    VARCHAR,
    calcule_le          DATE
);

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
    classe_effort           VARCHAR,
    nb_synthese_recherchees INTEGER,
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
    -- Le plafond analytique du bulletin : combien de paramètres cherchés sont
    -- hors de portée du laboratoire, c'est-à-dire non quantifiés avec une LQ
    -- au-dessus du seuil auquel on les compare. Compté à part de
    -- `nb_indetermines`, qui ne porte que sur le repère le plus strict : « on
    -- ne sait pas si le repère danois est tenu » et « on ne sait pas si la
    -- limite française est tenue » ne sont pas la même information.
    nb_aveugles             INTEGER,
    -- LA NATURE DE CE QUI EST FRANCHI. `nb_depasse_applicable` ne bouge pas :
    -- ces compteurs le DÉCOMPOSENT. Un taux qui mélange une limite sanitaire,
    -- une référence organoleptique et une valeur indicative ne se compare pas
    -- d'une commune à l'autre ; ceux-là, si.
    nb_depasse_limite       INTEGER,
    nb_au_dessus_vigilance  INTEGER,
    -- Hors de la référence déclarée, dans les DEUX sens. Le sens compte : une
    -- eau trop peu minéralisée n'est pas une eau chargée, c'est une eau
    -- agressive — elle attaque le réseau entre le point de prélèvement et le
    -- robinet, et ce qu'elle en emporte n'est dans aucun bulletin.
    nb_hors_reference       INTEGER,
    nb_sous_reference       INTEGER,
    nb_ecarts_seuil         INTEGER,
    nb_depasse_applicable   INTEGER,
    nb_bascules_datees      INTEGER,
    depassements_pour_mille DOUBLE,
    -- Seul comparable d'un bulletin à l'autre. Un bulletin qui cherche
    -- 700 paramètres en aura mécaniquement plus qu'un qui en cherche 200 :
    -- le compte brut ne se compare pas, le taux si (§2.11).
    aveugles_pour_mille     DOUBLE,
    synthese_quantifiees_pour_mille DOUBLE,
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
    -- Le seuil en vigueur LE JOUR DU PRÉLÈVEMENT, et le verdict rendu contre
    -- lui. Sans ces deux colonnes, une sortie qui ne lit que les tables figées
    -- ne peut afficher que `depasse_2026` — c'est-à-dire juger une mesure de
    -- 2023 à l'aune de la grille de 2026, exactement ce que CLAUDE.md §2.10
    -- interdit. Le compteur `nb_depasse_applicable` de `analyses_figees` était
    -- alors en désaccord avec son propre détail.
    seuil_applicable    DOUBLE,
    grille_applicable   VARCHAR,
    -- L'ATTRIBUTION que portait cette mesure LE JOUR DU CALCUL.
    -- Elle est figée, pas déduite à l'affichage : sinon deux écrans peuvent
    -- dire deux choses du même bulletin selon le référentiel du moment, ce que
    -- le figeage existe précisément pour empêcher (CLAUDE.md §8bis).
    -- Cinq valeurs, définies dans docs/METHODE_ATTRIBUTION.md §0 :
    --   juge · juge_avec_son_groupe · juge_sur_valeur_declaree ·
    --   norme_non_exprimee · rien_ne_se_prononce_{etabli,non_instruit}
    attribution         VARCHAR,
    depasse_2016        BOOLEAN,
    depasse_2026        BOOLEAN,
    depasse_applicable  BOOLEAN,
    depasse_strict      BOOLEAN,
    depasse_futur       BOOLEAN,
    bascule_2016_2026   BOOLEAN,
    bascule_datee       BOOLEAN,
    indetermine_strict  BOOLEAN,
    indetermine_condition BOOLEAN,
    -- LE PLAFOND ANALYTIQUE, au paramètre (chantier C4).
    -- `lq_aveugle` : la mesure n'est pas quantifiée ET la limite de
    -- quantification du laboratoire est au-dessus du seuil auquel on compare.
    -- Sous cette valeur, l'analyse ne voit rien : on ne peut pas dire que le
    -- seuil est respecté, seulement qu'on ne sait pas.
    -- `lq_rapport_seuil` : de combien. « LQ 0,5 µg/L, soit 5 × la limite de
    -- 0,1 » se lit ; « 0,5 » ne se lit pas.
    lq_aveugle          BOOLEAN,
    lq_rapport_seuil    DOUBLE,
    -- limite | reference | vigilance — l'administration sépare elle-même ces
    -- trois axes dans ses conclusions, et les confondre à l'affichage
    -- transforme un écart organoleptique en non-conformité sanitaire (§2.1).
    nature_seuil        VARCHAR,
    hors_reference      BOOLEAN,
    sens_hors_reference VARCHAR,
    reference_min       DOUBLE,
    reference_max       DOUBLE,
    -- Statut de perturbateur endocrinien, dans les DEUX registres et jamais
    -- fusionnés (CLAUDE.md §2.6). Figés ici parce qu'ils viennent de la ligne
    -- de référentiel réellement appariée : une substance rattachée par règle de
    -- famille n'a pas de ligne propre, et un rapprochement par libellé au
    -- moment de l'affichage la manquerait — donc la déclarerait non-PE, ce qui
    -- est un faux négatif. Trois états, comme partout ici : avéré, suspecté,
    -- et « non documenté », qui n'est pas « non ».
    pe_reglementaire    VARCHAR,
    pe_scientifique     VARCHAR,
    -- Ligne agrégée (« Total des pesticides analysés », « Somme de 20 PFAS »,
    -- « Nitrates/50 + Nitrites/3 ») : une somme, pas une substance. Sans ce
    -- drapeau, toute lecture qui énumère des substances compte la somme en
    -- même temps que ses composants.
    est_agregat         BOOLEAN,
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

CREATE TABLE IF NOT EXISTS lq_corpus (
    version_referentiel VARCHAR,
    calcule_le          DATE,
    cle_param           VARCHAR,
    libelle_parametre   VARCHAR,
    unite               VARCHAR,
    lq_min              DOUBLE,
    lq_max              DOUBLE,
    lq_mediane          DOUBLE,
    nb_mesures          INTEGER,
    nb_bulletins        INTEGER,
    nb_departements     INTEGER,
    PRIMARY KEY (version_referentiel, cle_param)
);
"""


# Colonnes attendues par table figée. Sert au contrôle de dérive ci-dessous :
# une table créée par une version antérieure du code ne doit jamais survivre en
# silence à un changement de schéma.
def _colonnes_declarees(schema):
    tables = {}
    for bloc in schema.split("CREATE TABLE IF NOT EXISTS ")[1:]:
        nom, corps = bloc.split("(", 1)
        colonnes = []
        for ligne in corps.rsplit(");", 1)[0].split("\n"):
            ligne = ligne.strip()
            if ligne and not ligne.startswith(("--", "PRIMARY KEY")):
                colonnes.append(ligne.split()[0])
        tables[nom.strip()] = colonnes
    return tables


COLONNES_ATTENDUES = _colonnes_declarees(SCHEMA_FIGE)


def assurer_schema(con, verbeux=True):
    """
    Crée les tables figées, et **détruit celles dont le schéma a dérivé**.

    `CREATE TABLE IF NOT EXISTS` ne dit rien quand la table existe déjà avec
    d'autres colonnes : un dépôt construit par une version antérieure du code
    garderait son ancienne table, l'INSERT échouerait — ou pire, réussirait en
    laissant de côté une colonne devenue nécessaire.

    Une table figée détruite ici n'est pas une perte de fait : les mesures sont
    intactes en base, et `figer()` recalcule tout. Ce qui se perd est le verdict
    calculé contre une version ANTÉRIEURE du référentiel, et cela se dit.

    **`analyses_figees` et `verdicts_figes` sont UN SEUL figeage en deux
    tables** — le bulletin et son détail paramètre par paramètre. Reconstruire
    l'une sans vider l'autre laisse un figeage à moitié présent, et depuis que
    `figer()` est incrémental ce demi-figeage est **invisible** : le bulletin
    figure toujours dans `analyses_figees`, donc il est réputé figé, donc son
    détail n'est jamais réécrit. Le compteur du bulletin annoncerait des
    dépassements dont le détail serait vide.

    Défaut réel, attrapé par `tests/test_figer.py` en écrivant le figeage
    incrémental le 11 août 2026 : le contrôle « et refigée sans perte » est
    passé au rouge dès le premier essai. Sans lui, la régression serait entrée
    sans bruit — c'est exactement ce que ce test existe pour empêcher.
    """
    con.execute(SCHEMA_FIGE)
    reconstruites = []
    for table, attendues in COLONNES_ATTENDUES.items():
        presentes = [r[0] for r in con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = ? ORDER BY ordinal_position", [table]).fetchall()]
        if presentes == attendues:
            continue
        manquantes = [c for c in attendues if c not in presentes]
        if verbeux:
            print(f"  ! {table} : schéma obsolète, table reconstruite"
                  + (f" (colonnes ajoutées : {', '.join(manquantes)})" if manquantes else ""))
            print("    les verdicts figés contre une version antérieure du référentiel", flush=True)
            print("    sont perdus ; les mesures, elles, sont intactes. Refige.", flush=True)
        con.execute(f"DROP TABLE IF EXISTS {table}")
        reconstruites.append(table)
    con.execute(SCHEMA_FIGE)

    if set(reconstruites) & {"analyses_figees", "verdicts_figes"}:
        # L'une des deux moitiés est repartie de zéro : l'autre ne décrit plus
        # rien de complet. On les remet toutes les deux à vide, et on efface
        # l'empreinte de moteur pour que le prochain `figer()` reparte du
        # corpus entier au lieu de croire qu'il n'a rien à faire.
        if verbeux and len(reconstruites) == 1:
            print("    l'autre moitié du figeage est vidée avec elle : un bulletin "
                  "et son détail ne se séparent pas", flush=True)
        con.execute("DELETE FROM analyses_figees")
        con.execute("DELETE FROM verdicts_figes")
        con.execute("DELETE FROM figeage_moteur")


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


# Les fichiers dont le contenu décide de ce que vaut une ligne figée :
# le calcul lui-même, les vues qu'il interroge, et les fonctions de lecture
# d'une mesure. Une modification de l'un des trois change potentiellement
# TOUS les verdicts déjà figés.
FICHIERS_MOTEUR = ("figer.py", "build_db.py", "common.py")


def version_moteur():
    """
    Empreinte du **code** qui calcule un figeage : 12 caractères hexadécimaux.

    Pourquoi elle existe — le piège du figeage incrémental
    ------------------------------------------------------
    `version_referentiel` répond à « contre quelle grille ce verdict a-t-il été
    rendu ». Elle ne répond pas à « par quel calcul ». Tant que `figer()`
    refigeait tout le corpus à chaque appel, la question ne se posait pas : une
    correction du moteur se propageait d'elle-même au figeage suivant.

    Dès que le figeage devient incrémental, elle se pose et elle est
    dangereuse : on corrige un défaut de calcul, le référentiel n'a pas bougé
    donc `version_referentiel` non plus, et les 4 700 lignes déjà figées
    **gardent silencieusement l'ancien verdict** pendant que les nouvelles
    portent le bon. Deux calculs sous une même version, et rien ne le dit —
    c'est exactement le défaut qui a fait citer deux jours durant un chiffre du
    Rhône introuvable en base.

    D'où cette seconde empreinte, comparée à chaque figeage : si elle a changé,
    le figeage redevient complet d'office et l'annonce. Elle est délibérément
    grossière — elle porte sur les octets des fichiers, commentaires compris —
    parce que l'erreur à ne pas commettre est de sauter un refigeage
    nécessaire. Un refigeage inutile coûte du temps ; un refigeage manquant
    produit un chiffre faux, et le §2.13 tranche cette asymétrie-là depuis
    toujours.
    """
    h = hashlib.sha256()
    for nom in FICHIERS_MOTEUR:
        chemin = os.path.join(RACINE, "src", nom)
        h.update(nom.encode())
        if os.path.exists(chemin):
            with open(chemin, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()[:12]


class MoteurChange(RuntimeError):
    """
    Le code de calcul a changé depuis le dernier figeage de cette version.

    Levée par `figer()` **avant d'avoir écrit ou effacé quoi que ce soit**.
    L'appelant a deux issues, et aucune n'est automatique : refiger tout le
    corpus avec le code actuel (`complet=True`), ou ne pas figer et le dire.
    """


def _compte_figes(con, version):
    return con.execute("SELECT COUNT(*) FROM analyses_figees "
                       "WHERE version_referentiel = ?", [version]).fetchone()[0]


def _moteur_enregistre(con, version):
    """L'empreinte de moteur sous laquelle cette version a été figée, ou None."""
    r = con.execute("SELECT empreinte_moteur FROM figeage_moteur "
                    "WHERE version_referentiel = ?", [version]).fetchone()
    return r[0] if r else None


def _enregistrer_moteur(con, version, moteur, jour):
    con.execute("DELETE FROM figeage_moteur WHERE version_referentiel = ?", [version])
    con.execute("INSERT INTO figeage_moteur VALUES (?,?,?::DATE)",
                [version, moteur, jour])


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


# Le seuil auquel la LQ est comparée : celui qui s'appliquait le jour du
# prélèvement, sauf s'il existe un seuil conditionnel — auquel c'est le plus
# permissif des deux qui fait foi, exactement comme pour `depasse_applicable`
# (§2.13 : rien dans les données ne dit si la condition est remplie, et un faux
# positif coûte plus cher au projet qu'un faux négatif).
#
# `> 0` n'est pas une précaution de calcul, c'est une règle de méthode. La
# limite de qualité de la bactériologie est ZÉRO — zéro entérocoque pour
# 100 mL — et la « LQ » d'un dénombrement vaut 1, puisqu'on ne compte pas
# une demi-bactérie. Aucune LQ ne peut passer sous zéro : sans cette
# condition, les 69 mesures bactériologiques du corpus seraient déclarées
# « aveugles » alors qu'elles sont parfaitement lisibles, et elles
# noieraient les 46 cas réels.
SEUIL_LQ = "COALESCE(seuil_conditionnel, seuil_applicable)"

EST_AVEUGLE = f"""
    COALESCE(NOT est_quantifie AND lq IS NOT NULL
             AND {SEUIL_LQ} IS NOT NULL AND {SEUIL_LQ} > 0
             AND lq > {SEUIL_LQ}, FALSE)
"""


def _plafond_analytique(con, code_prel):
    """
    Ce que le laboratoire ne pouvait pas voir sur ce bulletin (chantier C4).

    Le compte ET le taux. Le compte seul n'est pas comparable d'un bulletin à
    l'autre — un bulletin qui cherche 700 paramètres a mécaniquement plus
    d'occasions d'être aveugle qu'un qui en cherche 200 (§2.11). Le
    dénominateur est le nombre de mesures NOTÉES, le même que
    `depassements_pour_mille`, pour que les deux taux se lisent ensemble.
    """
    n, notees = con.execute(f"""
        SELECT COUNT(*) FILTER (WHERE {EST_AVEUGLE}),
               COUNT(*) FILTER (WHERE notee)
        FROM v_mesures_verdict WHERE code_prelevement = ?
    """, [code_prel]).fetchone()
    return {
        "nb_aveugles": n or 0,
        "aveugles_pour_mille": (round(1000.0 * n / notees, 2) if notees else None),
    }


def figer_lq_corpus(con, version, calcule_le=None):
    """
    L'étendue des limites de quantification observées dans le corpus, paramètre
    par paramètre. C'est la base du barème de finesse analytique.

    Pourquoi une table figée et non une vue : la référence BOUGE avec le
    corpus. « Le plus fin » sur 45 bulletins n'est pas « le plus fin » sur
    4 000, et une fiche publiée doit pouvoir dire contre quelle base elle a
    situé son laboratoire — d'où `nb_bulletins` et `nb_departements`, qui
    s'affichent avec le barème et ne sont pas décoratifs. C'est le §2.14
    transposé à l'instrument : le plus fin IDENTIFIÉ, jamais le plus fin qui
    existe.

    Clé d'identité du paramètre : `code_parametre` quand la source le donne,
    sinon le libellé normalisé — la même convention que les vues de panel. Le
    code seul perdrait les mesures qui n'en portent pas, le libellé seul
    éclaterait un paramètre renommé d'une campagne à l'autre.

    Une LQ élevée n'est pas une négligence : c'est une capacité d'instrument
    (§2.1). Cette table décrit des instruments, elle ne classe pas des
    laboratoires — elle ne porte d'ailleurs aucun nom de laboratoire.
    """
    jour = calcule_le or datetime.date.today().isoformat()
    con.execute("DELETE FROM lq_corpus WHERE version_referentiel = ?", [version])
    con.execute("""
        INSERT INTO lq_corpus
        SELECT ?, ?::DATE,
               COALESCE(m.code_parametre, m.libelle_norm)  AS cle_param,
               ANY_VALUE(m.libelle_parametre),
               ANY_VALUE(m.unite),
               MIN(m.lq), MAX(m.lq), MEDIAN(m.lq),
               COUNT(*),
               COUNT(DISTINCT m.code_prelevement),
               COUNT(DISTINCT c.code_departement)
        FROM mesures m
        JOIN prelevements p ON p.code_prelevement = m.code_prelevement
        JOIN communes     c ON c.code_insee = p.code_insee
        WHERE m.lq IS NOT NULL
        GROUP BY cle_param
    """, [version, jour])
    return con.execute("SELECT COUNT(*) FROM lq_corpus WHERE version_referentiel = ?",
                       [version]).fetchone()[0]


def figer(con, version=None, calcule_le=None, verbeux=True, complet=False):
    """
    Fige les bulletins qui ne le sont pas encore sous cette version.

    **Cette fonction imprime sa progression**, et ce n'est pas du confort. Le
    11 août 2026, le figeage du Rhône a tourné dix-sept minutes sans une ligne :
    indiscernable d'un processus gelé, exactement le défaut qui venait d'être
    corrigé dans `hubeau._pages` le matin même. Une boucle longue et muette n'est
    pas diagnosticable — et elle finit par coûter une soirée à quelqu'un.

    Incrémental depuis le 11 août 2026, et pourquoi
    -----------------------------------------------
    Cette fonction refigeait TOUT le corpus à chaque appel. Mesuré ce jour-là :
    **32,4 minutes pour 4 745 bulletins**, soit 0,41 s l'unité — pour une
    ingestion de 65 bulletins, et le verrou de la base tenu pendant tout ce
    temps. Le coût croissait avec le corpus et non avec le lot : à 35 000
    communes, chaque ingestion aurait coûté des heures d'indisponibilité. Le
    découpage moisson/ingestion aurait levé un verrou de trois heures pour en
    installer un autre.

    Ce qui est sauté est **exactement** ce qui n'a pas à être recalculé : un
    bulletin déjà présent dans `analyses_figees` sous CETTE version. Trois
    situations, et les trois restent justes :

      · **un bulletin nouvellement ingéré** n'y est pas -> il est figé ;
      · **le référentiel a changé** -> `version_referentiel` change, donc plus
        personne n'y est sous la nouvelle version -> tout est refigé. C'est la
        règle du projet et elle est intacte : une version s'applique au corpus
        entier, jamais à une partie ;
      · **un bulletin réingéré** (ses mesures ont été remplacées) voit ses
        lignes figées supprimées par l'ingestion elle-même — cf.
        `ingest.ingest_bulletin`. Sans cela il garderait un verdict qui ne
        décrit plus ses données, ce qui est le pire cas possible ici.

    Reste le quatrième cas, et c'est lui qui demandait un mécanisme : **le
    calcul lui-même change** sans que le référentiel bouge. `version_moteur()`
    l'attrape — si l'empreinte du code diffère de celle enregistrée pour cette
    version, cette fonction **lève `MoteurChange` et ne fige rien**. Elle
    n'efface rien non plus : refiger tout le corpus est un geste qui se
    demande (`complet=True`), jamais un effet de bord d'une ingestion.

    `complet=True` refige tout le corpus, en remplaçant bulletin par bulletin.
    """
    assurer_schema(con)
    version = version or version_referentiel()
    jour = calcule_le or datetime.date.today().isoformat()

    moteur = version_moteur()
    enregistre = _moteur_enregistre(con, version)
    if enregistre and enregistre != moteur and not complet:
        # ON NE FIGE RIEN, et on ne détruit rien.
        #
        # La première version de ce contrôle forçait `complet = True`, donc
        # effaçait tout le figeage de la version avant de le recalculer.
        # Défaut réel, le 11 août 2026 : une autre session avait ajouté une
        # fonction éditoriale à `common.py` — sans le moindre effet sur un
        # verdict —, l'empreinte a changé, et une simple ingestion a effacé
        # 7 279 lignes figées puis est morte au bulletin 3 780. Le corpus s'est
        # retrouvé dans un état pire qu'avant, comme effet de bord d'une
        # commande qui ne demandait rien de tel.
        #
        # Deux leçons, et elles tiennent toutes les deux :
        #   · une empreinte d'octets ne distingue pas un changement de calcul
        #     d'un ajout sans conséquence, et elle ne le peut pas ;
        #   · **détruire une sortie figée ne doit jamais être un effet de bord.**
        #     C'est un geste que l'on demande, jamais un geste que l'on subit.
        #
        # Refuser de figer laisse le corpus COHÉRENT et incomplet : les
        # nouveaux bulletins restent absents d'`analyses_figees`, donc non
        # citables (§8bis), ce qui est exactement leur statut réel. C'est
        # l'inverse de mélanger deux calculs sous une seule version, qui serait
        # invisible.
        raise MoteurChange(
            f"le code de calcul a changé depuis le dernier figeage de "
            f"{version} : empreinte {enregistre} -> {moteur}.\n"
            f"    Rien n'a été figé, et RIEN N'A ÉTÉ EFFACÉ — les "
            f"{_compte_figes(con, version)} bulletin(s) déjà figés sont "
            f"intacts.\n"
            f"    Figer les nouveaux avec le code actuel les mettrait sous la "
            f"même version que les anciens,\n"
            f"    calculés autrement : deux calculs sous une seule version, et "
            f"rien pour le dire.\n"
            f"    Fichiers surveillés : {', '.join(FICHIERS_MOTEUR)}.\n"
            f"    Pour refiger tout le corpus avec le code actuel (long, et "
            f"c'est le bon geste si le calcul\n"
            f"    a réellement changé) :  --refiger")

    prels = [r[0] for r in con.execute(
        "SELECT code_prelevement FROM v_prelevement_verdict ORDER BY 1").fetchall()]
    corpus = len(prels)

    if complet:
        # On n'efface PAS tout d'avance. Chaque bulletin est remplacé au moment
        # où il est recalculé, dans la boucle. La différence n'est pas
        # cosmétique : effacer d'abord, c'est garantir qu'une interruption
        # laisse le corpus amputé de tout ce qui n'a pas encore été refait —
        # ce qui est arrivé le 11 août 2026, 7 279 lignes effacées pour 3 780
        # recalculées avant que le processus ne meure.
        #
        # En remplaçant au fil, une interruption laisse un corpus MIXTE : une
        # partie recalculée, une partie ancienne. C'est moins bon qu'un corpus
        # cohérent, mais bien meilleur qu'un corpus amputé — et surtout, c'est
        # DÉTECTABLE : `figeage_moteur` n'est mis à jour qu'à la toute fin, donc
        # une reprise revoit l'écart d'empreinte et refuse de figer tant que le
        # refigeage n'a pas été mené à son terme.
        a_figer = prels
    else:
        deja = {r[0] for r in con.execute(
            "SELECT code_prelevement FROM analyses_figees "
            "WHERE version_referentiel = ?", [version]).fetchall()}
        a_figer = [cp for cp in prels if cp not in deja]

    total = len(a_figer)
    # Un jalon tous les 5 %, borné : assez pour voir que ça avance, assez rare
    # pour ne pas noyer le journal d'un gros lot.
    pas = max(50, total // 20)
    t0 = time.time()
    if verbeux:
        if total:
            deja_n = corpus - total
            print(f"figeage   : {total} bulletin(s) à figer sous {version}"
                  + (f" ({deja_n} déjà figés, inchangés)" if deja_n else "")
                  + (" — refigeage complet" if complet else ""))
        else:
            print(f"figeage   : rien à figer, les {corpus} bulletin(s) du corpus "
                  f"sont déjà figés sous {version}", flush=True)

    for i, cp in enumerate(a_figer, 1):
        if verbeux and total and (i % pas == 0 or i == total):
            ecoule = time.time() - t0
            reste = ecoule / i * (total - i)
            # `flush=True` : sans lui, la progression d'un figeage redirigé vers
            # un fichier reste dans le tampon de stdout et **disparaît si le
            # processus meurt**. C'est arrivé le 11 août 2026 — un figeage tué
            # en cours de route n'a laissé aucune trace de son avancement, et
            # l'incident a dû être reconstitué en interrogeant la base. Une
            # fonction dont la docstring dit « elle imprime sa progression, ce
            # n'est pas du confort » doit s'assurer que cette progression
            # survit à sa propre mort.
            print(f"  {i}/{total} bulletins figés — {ecoule/60:.1f} min écoulées, "
                  f"~{reste/60:.1f} min restantes", flush=True)

        # Remplacement AU FIL, et non un effacement global en amont : une
        # interruption laisse alors un corpus mixte et détectable, jamais un
        # corpus amputé (cf. le bloc `if complet:` plus haut).
        con.execute("DELETE FROM analyses_figees WHERE version_referentiel = ? "
                    "AND code_prelevement = ?", [version, cp])
        con.execute("DELETE FROM verdicts_figes WHERE version_referentiel = ? "
                    "AND code_prelevement = ?", [version, cp])
        s = _sommes(con, cp)
        lq = _plafond_analytique(con, cp)
        con.execute("""
            INSERT INTO analyses_figees
            SELECT p.code_prelevement, ?, ?::DATE,
                   p.code_insee, p.commune, p.dept, p.codes_postaux, p.lon, p.lat,
                   p.date_prelevement, p.code_installation_amont,
                   p.nom_installation_amont, p.nom_uge, p.noms_reseaux,
                   p.nb_parametres, p.classe_effort, p.nb_synthese_recherchees,
                   p.est_complet,
                   p.nb_mesures_lues, p.nb_mesures_notees, p.pct_couverture,
                   p.nb_notees_referentiel, p.nb_notees_declare,
                   p.nb_depasse_2016, p.nb_depasse_2026, p.nb_depasse_strict,
                   p.nb_depasse_futur, p.nb_bascules, p.nb_indetermines,
                   ?,
                   p.nb_depasse_limite, p.nb_au_dessus_vigilance,
                   p.nb_hors_reference, p.nb_sous_reference,
                   p.nb_ecarts_seuil,
                   p.nb_depasse_applicable, p.nb_bascules_datees,
                   p.depassements_pour_mille,
                   ?,
                   p.synthese_quantifiees_pour_mille,
                   ?, ?, ?, ?, ?, ?,
                   p.conclusion_conformite, pr.source_url
            FROM v_prelevement_verdict p
            JOIN prelevements pr ON pr.code_prelevement = p.code_prelevement
            WHERE p.code_prelevement = ?
        """, [version, jour,
              lq["nb_aveugles"], lq["aveugles_pour_mille"],
              s["nb_synthese_quantifiees"], s["charge_synthese_ug_l"],
              s["somme_pesticides_declaree"], s["somme_pesticides_recalculee"],
              s["indice_danger"], s["indice_danger_n"], cp])

        con.execute(f"""
            INSERT INTO verdicts_figes
            SELECT code_prelevement, ?, libelle_parametre, code_parametre, code_cas,
                   famille, mode_appariement, resultat_num, lq, est_quantifie, unite,
                   seuil_2016, seuil_2026_effectif, origine_seuil_2026,
                   seuil_strict, seuil_futur,
                   seuil_applicable, grille_applicable, attribution,
                   depasse_2016, depasse_2026, depasse_applicable,
                   depasse_strict, depasse_futur,
                   bascule_2016_2026, bascule_datee,
                   indetermine_strict, indetermine_condition,
                   {EST_AVEUGLE},
                   CASE WHEN {EST_AVEUGLE} THEN lq / {SEUIL_LQ} END,
                   nature_seuil, hors_reference, sens_hors_reference,
                   reference_min, reference_max,
                   pe_reglementaire, pe_scientifique, est_agregat, fiabilite
            FROM v_mesures_verdict
            -- « notee » = la mesure a un seuil dans la grille D'AUJOURD'HUI.
            -- C'est le bon dénominateur de la couverture, et ce n'est pas le
            -- bon filtre de figeage : une mesure qui n'a QU'UN repère strict —
            -- la somme de 4 PFAS, dont le seuil danois de 2 ng/L est le plus
            -- protecteur au monde — n'est pas notée, et disparaissait donc du
            -- détail figé. Or c'est précisément là que naît l'indéterminé le
            -- plus fréquent : la LQ courante des laboratoires est de 4 ng/L.
            -- Le compteur du bulletin annonçait deux indéterminés et le détail
            -- n'en montrait qu'un (CLAUDE.md §2.4).
            --
            -- ÉLARGI LE 12 AOÛT 2026 : plus aucun filtre. Le détail figé est
            -- désormais la photographie ENTIÈRE du bulletin.
            --
            -- Le filtre précédent — `notee OR seuil_strict IS NOT NULL OR
            -- hors_reference` — ne gardait que les mesures ayant un seuil de
            -- comparaison. C'était cohérent tant que la sortie ne montrait que
            -- des verdicts. Ça ne l'est plus depuis la décision du 11 août :
            -- toute substance mesurée reçoit une attribution, y compris
            -- « rien ne se prononce » (docs/METHODE_ATTRIBUTION.md).
            --
            -- Mesuré avant le changement : le moteur calculait l'attribution
            -- « rien ne se prononce, non instruit » sur 413 050 mesures, et le
            -- détail figé n'en conservait que 364 — soit 0,1 %. Autrement dit
            -- la population qu'on venait de décider de rendre visible était
            -- précisément celle que le figeage écartait. Volume ajouté : environ
            -- 450 000 lignes sur 4,2 millions, soit +11 %.
            --
            -- CONSÉQUENCE À CONNAÎTRE : tout compte tiré de cette table change
            -- de sens — il portait sur « les mesures notées », il porte
            -- désormais sur « les mesures ». Les dossiers de faits en tirent
            -- des chiffres : les régénérer après ce changement, sans quoi la
            -- prose et la table parlent de périmètres différents.
            WHERE code_prelevement = ?
        """, [version, cp])

    # Ces deux-là se refont TOUJOURS, même quand aucun bulletin n'a été figé :
    # elles ne décrivent pas un bulletin mais le CORPUS, et le corpus vient de
    # changer. Le barème de finesse analytique en particulier — « le plus fin
    # identifié sur N bulletins, M départements » (§2.14) — se déplace à chaque
    # arrivée, et une fiche qui l'afficherait périmé situerait son laboratoire
    # contre une base qui n'existe plus.
    figer_couverture_implicite(con, version, jour)
    figer_lq_corpus(con, version, jour)
    _enregistrer_moteur(con, version, moteur, jour)
    return version, len(a_figer)


def figer_couverture_implicite(con, version, calcule_le=None):
    """
    Toute commune qui a un bulletin figé EST une commune analysée, qu'on l'ait
    demandée ou non. Cette fonction inscrit celles qui manquaient.

    Défaut réel, trouvé le 8 août 2026. `observer.py` n'inscrit la couverture
    que des communes qu'on lui a **demandées**. Or quand une commune n'a pas de
    bulletin propre, le moteur prend celui de son réseau — prélevé chez une
    voisine, et ingéré sous le nom de cette voisine, ce qui est juste (§2.3 :
    le rattachement vit dans `couverture_communes`, pas dans le fait). Mais la
    voisine, jamais demandée, n'obtenait aucune ligne de couverture : son
    bulletin alimentait la fiche d'à côté, et elle-même restait invisible sur
    la carte.

    C'est le symétrique exact de la règle « non documentée ». Le projet tient à
    ce qu'une ABSENCE de donnée reste visible ; il ne peut pas tolérer qu'une
    PRÉSENCE de donnée ne le soit pas. Et les bulletins concernés sont les plus
    informatifs du secteur — ce sont ceux qui alimentent plusieurs communes.

    N'écrase jamais une ligne existante : une commune déjà inscrite comme
    `rattachee_reseau` par `observer.py` garde son statut, qui est plus précis.
    """
    jour = calcule_le or datetime.date.today().isoformat()
    manquantes = con.execute("""
        SELECT a.code_insee, a.commune, a.dept, a.codes_postaux, a.lon, a.lat,
               a.code_prelevement, a.date_prelevement, a.nb_parametres, a.pct_couverture
        FROM analyses_figees a
        LEFT JOIN couverture_communes cc
               ON cc.code_insee = a.code_insee
              AND cc.version_referentiel = a.version_referentiel
        WHERE a.version_referentiel = ? AND cc.code_insee IS NULL
          -- le bulletin le plus récent de la commune fait foi pour la carte
          AND a.date_prelevement = (SELECT MAX(b.date_prelevement) FROM analyses_figees b
                                    WHERE b.version_referentiel = a.version_referentiel
                                      AND b.code_insee = a.code_insee)
        QUALIFY ROW_NUMBER() OVER (PARTITION BY a.code_insee ORDER BY a.code_prelevement) = 1
    """, [version]).fetchall()

    for insee, nom, dept, cp, lon, lat, prel, date, nbp, pct in manquantes:
        con.execute("INSERT INTO couverture_communes VALUES (?,?,?::DATE,?,?,?,?,?,?,?,?,?::DATE,?,?)",
                    [insee, version, jour, nom, dept, cp, lon, lat,
                     "analysee", prel, None, str(date) if date else None, nbp, pct])

    # Contradiction : une commune déclarée sans donnée qui en a une. Elle vient
    # d'une collecte antérieure où le repli avait échoué ; la corriger en
    # silence effacerait la trace, donc on la dit.
    contredites = con.execute("""
        SELECT cc.code_insee, cc.commune FROM couverture_communes cc
        JOIN analyses_figees a ON a.code_insee = cc.code_insee
                              AND a.version_referentiel = cc.version_referentiel
        WHERE cc.version_referentiel = ? AND cc.statut = 'non_documentee'
    """, [version]).fetchall()
    for insee, nom in contredites:
        print(f"  ! {nom or insee} était « non documentée » et a désormais un bulletin "
              "figé — statut corrigé en « analysée »", flush=True)
        con.execute("""
            UPDATE couverture_communes SET statut = 'analysee',
                   code_prelevement = (SELECT a.code_prelevement FROM analyses_figees a
                                       WHERE a.code_insee = couverture_communes.code_insee
                                         AND a.version_referentiel = couverture_communes.version_referentiel
                                       ORDER BY a.date_prelevement DESC LIMIT 1)
            WHERE code_insee = ? AND version_referentiel = ?
        """, [insee, version])

    # Report des statuts qui ne dépendent PAS de la grille.
    #
    # « rattachée au réseau » et « non documentée » décrivent ce que les DONNÉES
    # permettent de savoir, pas ce que le référentiel dit : changer un seuil ne
    # fait pas apparaître un bulletin là où il n'y en a pas. Or ces statuts ne
    # sont écrits que par observer.py, pour les communes explicitement
    # demandées. Refiger sous une nouvelle version les perdait toutes — dix
    # communes rattachées ont ainsi disparu du site d'une publication à l'autre,
    # sans que rien ne le signale.
    reportes = con.execute("""
        WITH precedente AS (
            SELECT * FROM couverture_communes
            WHERE version_referentiel <> ?
              AND statut IN ('rattachee_reseau', 'non_documentee')
            QUALIFY ROW_NUMBER() OVER (PARTITION BY code_insee
                                       ORDER BY calcule_le DESC) = 1
        )
        SELECT p.code_insee, p.commune, p.dept, p.codes_postaux, p.lon, p.lat,
               p.statut, p.code_prelevement, p.commune_prelevement
        FROM precedente p
        LEFT JOIN couverture_communes c
               ON c.code_insee = p.code_insee AND c.version_referentiel = ?
        WHERE c.code_insee IS NULL
    """, [version, version]).fetchall()

    for insee, nom, dept, cp, lon, lat, statut, prel, commune_prel in reportes:
        detail = (None, None, None)
        if prel:
            detail = con.execute("""
                SELECT date_prelevement, nb_parametres, pct_couverture
                FROM analyses_figees
                WHERE code_prelevement = ? AND version_referentiel = ?
            """, [prel, version]).fetchone() or detail
        con.execute("INSERT INTO couverture_communes VALUES (?,?,?::DATE,?,?,?,?,?,?,?,?,?::DATE,?,?)",
                    [insee, version, jour, nom, dept, cp, lon, lat, statut, prel,
                     commune_prel, str(detail[0]) if detail[0] else None,
                     detail[1], detail[2]])

    if manquantes:
        print(f"  i {len(manquantes)} commune(s) inscrite(s) d'office : elles ont un "
              "bulletin figé sans avoir été demandées", flush=True)
        print("    (leur analyse sert de repli à une commune voisine — sans cela elles "
              "seraient absentes de la carte)", flush=True)
    if reportes:
        print(f"  i {len(reportes)} statut(s) de couverture reporté(s) depuis la version "
              "précédente", flush=True)
        print("    (rattachement au réseau et absence de donnée ne dépendent pas de la "
              "grille)", flush=True)
    return len(manquantes)


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
    assurer_schema(con, verbeux=False)
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
    print("\n=== Couverture par commune ===", flush=True)
    for r in con.execute("""
        SELECT statut, COUNT(*) FROM couverture_communes GROUP BY 1 ORDER BY 2 DESC
    """).fetchall():
        print(f"  {r[0]:<20} {r[1]}", flush=True)
    print("\n=== Analyses figées ===", flush=True)
    for r in con.execute("""
        SELECT version_referentiel, calcule_le, COUNT(*)
        FROM analyses_figees GROUP BY 1,2 ORDER BY 2 DESC
    """).fetchall():
        print(f"  {r[0]}  {r[1]}  {r[2]} bulletin(s)", flush=True)

    # Le plafond analytique, en clair. Ce n'est pas un défaut du bulletin :
    # c'est la part de l'analyse qui ne peut pas conclure, et elle conditionne
    # toute comparaison entre communes au même titre que l'effort de recherche.
    aveugles = con.execute("""
        SELECT COUNT(*) FILTER (WHERE nb_aveugles > 0), SUM(nb_aveugles),
               MAX(aveugles_pour_mille)
        FROM analyses_figees
        WHERE version_referentiel = (SELECT version_referentiel FROM analyses_figees
                                     GROUP BY 1 ORDER BY MAX(calcule_le) DESC LIMIT 1)
    """).fetchone()
    if aveugles and aveugles[1]:
        print("\n=== Plafond analytique (chantier C4) ===", flush=True)
        print(f"  {aveugles[1]} mesure(s) hors de portée du laboratoire sur "
              f"{aveugles[0]} bulletin(s) — jusqu'à {aveugles[2]} pour mille", flush=True)
        print("    LQ au-dessus du seuil de comparaison : ni conforme, ni dépassement.", flush=True)
        for r in con.execute("""
            SELECT libelle_parametre, COUNT(*), MIN(lq), MAX(lq), ANY_VALUE(unite)
            FROM verdicts_figes WHERE lq_aveugle GROUP BY 1 ORDER BY 2 DESC LIMIT 8
        """).fetchall():
            print(f"      {r[0][:44]:<44} {r[1]:>3} mesure(s)  LQ {r[2]}–{r[3]} {r[4] or ''}", flush=True)


def main():
    p = argparse.ArgumentParser(description="Fige les analyses dans la base")
    p.add_argument("--statut", action="store_true", help="afficher l'état, sans recalculer")
    a = p.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"base absente : {DB_PATH}\nlance d'abord : python3 src/build_db.py", flush=True)
        sys.exit(1)
    con = duckdb.connect(DB_PATH)
    try:
        if a.statut:
            assurer_schema(con)
            statut(con)
            return
        version, n = figer(con)
        print(f"figé : {n} bulletin(s) sous la version de référentiel {version}", flush=True)
        statut(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()

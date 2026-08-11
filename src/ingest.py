# -*- coding: utf-8 -*-
"""
Ingestion d'UN bulletin : un prélèvement, une date, un point d'eau,
l'intégralité de ses paramètres.

Idempotent : réingérer un prélèvement déjà présent le REMPLACE (DELETE puis
INSERT sur code_prelevement). On peut donc relancer une collecte interrompue
sans précaution et sans doublon.

Ce module ne fait aucune requête réseau : il reçoit les lignes déjà obtenues.
"""
from common import (norm, norm_unite, parse_val, parse_limite,
                    bornes_reference, SEUIL_COMPLET)


class BulletinHeterogene(ValueError):
    """Plusieurs prélèvements dans le même lot de lignes.

    C'est le défaut que cette version corrige : regrouper par date fusionnait
    l'analyse complète d'un point avec l'analyse de routine d'un autre point
    prélevé le même jour. Le nombre de paramètres s'en trouvait gonflé et les
    valeurs des paramètres communs (pH, chlore, nitrates) étaient prises au
    hasard sur l'un ou l'autre point. Une analyse porte sur UN prélèvement
    (CLAUDE.md §2.3).
    """


def _valeur(row):
    """
    Ligne Hub'Eau -> (resultat_num, lq, unite, est_quantifie).

    Hub'Eau expose deux champs :
      - resultat_numerique      : valeur numérique, souvent 0 pour un résultat
                                  non quantifié ;
      - resultat_alphanumerique : chaîne, qui porte le « < » quand la valeur est
                                  sous la limite de quantification.

    On lit d'abord l'alphanumérique : c'est le seul endroit où l'information
    « non quantifié » est présente. Un resultat_numerique à 0 sans « < » est
    traité comme NON quantifié de LQ inconnue — jamais comme une absence
    (CLAUDE.md §2.4 : zéro n'est pas zéro).
    """
    unite = row.get("libelle_unite") or row.get("code_unite")

    alpha = row.get("resultat_alphanumerique")
    if alpha not in (None, ""):
        num, lq, unite_parsee, quantifie = parse_val(alpha)
        if quantifie and num == 0.0:
            # « 0 » sans « < » : non quantifié, LQ non communiquée.
            # Cas particulier de la microbiologie, où 0 signifie « aucune
            # colonie dénombrée » : le verdict est inchangé (le seuil est 0,
            # et 0 ne le dépasse pas), mais on ne l'écrit pas « quantifié ».
            return (None, None, unite or unite_parsee, False)
        if quantifie or lq is not None:
            return (num, lq, unite or unite_parsee, quantifie)
        # résultat purement qualitatif (« absence », « à l'équilibre »…)
        if num is None and lq is None:
            return (None, None, unite or unite_parsee, False)

    brut = row.get("resultat_numerique")
    if brut in (None, ""):
        return (None, None, unite, False)
    try:
        num = float(str(brut).replace(",", "."))
    except (TypeError, ValueError):
        return (None, None, unite, False)

    if num == 0.0:
        # 0 signifie « inférieur au seuil de quantification », LQ non communiquée
        return (None, None, unite, False)
    return (num, None, unite, True)


def verifier_homogeneite(rows):
    """Un lot de lignes doit porter un seul code_prelevement."""
    codes = {str(r.get("code_prelevement")) for r in rows if r.get("code_prelevement")}
    if len(codes) > 1:
        raise BulletinHeterogene(
            f"{len(codes)} prélèvements dans le même lot ({', '.join(sorted(codes)[:4])}…) : "
            "un bulletin doit être ingéré prélèvement par prélèvement"
        )
    return codes.pop() if codes else None


def par_libelle(rows):
    """
    Lignes d'un bulletin -> {libellé: ligne retenue}, dédupliqué.

    La PK de `mesures` est (code_prelevement, libelle_parametre) : deux lignes
    de même libellé sont le même paramètre, et la première gagne.
    """
    retenues = {}
    for r in rows:
        lib = r.get("libelle_parametre")
        if not lib:
            continue
        retenues.setdefault(lib, r)
    return retenues


def identifier(meta, rows):
    """
    (code_prelevement, nb_parametres_distincts, est_complet) — **sans base**.

    Extrait de `ingest_bulletin` pour que la moisson puisse dire ce qu'elle
    rapatrie sans ouvrir DuckDB (`src/moisson.py`). C'est la définition unique
    de « combien de paramètres porte ce bulletin » et donc de `est_complet` :
    la recopier ailleurs ferait diverger le seuil du §2.3 entre la trace de
    collecte et ce qui entre réellement en base.
    """
    code_prel = verifier_homogeneite(rows) or meta.get("code_prelevement")
    if not code_prel:
        raise ValueError("aucun code_prelevement : bulletin non identifiable")
    nb = len(par_libelle(rows))
    return code_prel, nb, nb > SEUIL_COMPLET


# Les tables figées dépendent des mesures. Réingérer sans les invalider
# laisserait un verdict qui ne décrit plus ses données.
_TABLES_FIGEES = ("analyses_figees", "verdicts_figes")


def _invalider_figeage(con, code_prel):
    """
    Efface les lignes figées du prélèvement qu'on s'apprête à remplacer.

    Tant que `figer.figer()` refigeait tout le corpus à chaque appel, cette
    invalidation était inutile : le figeage suivant réécrivait la ligne de
    toute façon. **Depuis que le figeage est incrémental, elle est ce qui rend
    l'incrémentalité correcte** — sans elle, un bulletin réingéré (correction
    d'un bug d'ingestion, `--tout`, cache refait) serait vu comme « déjà figé »
    et garderait indéfiniment le verdict calculé sur les anciennes mesures.

    Toutes versions confondues, et non la seule version courante : une ligne
    figée sous une version antérieure décrit elle aussi des mesures qui
    viennent de disparaître. Un verdict daté reste vrai contre sa grille ; il
    ne reste pas vrai contre des données qu'on a remplacées.

    Silencieux si les tables n'existent pas encore : l'ingestion doit pouvoir
    tourner sur une base qui n'a jamais été figée.
    """
    presentes = {r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_name IN ('analyses_figees', 'verdicts_figes')").fetchall()}
    for table in _TABLES_FIGEES:
        if table in presentes:
            con.execute(f"DELETE FROM {table} WHERE code_prelevement = ?", [code_prel])


def ingest_bulletin(con, meta, rows):
    """
    Insère commune + prélèvement + mesures. Retourne (code_prelevement, nb, est_complet).

    nb = nombre de paramètres DISTINCTS du bulletin : c'est lui qui décide si le
    prélèvement est complet, donc s'il entre dans les analyses (CLAUDE.md §2.3).
    """
    insee = meta["code_insee"]
    code_prel, nb, est_complet = identifier(meta, rows)

    con.execute(
        "INSERT OR REPLACE INTO communes VALUES (?,?,?,?,?,?)",
        [insee, meta.get("nom"), meta.get("code_departement"),
         meta.get("codes_postaux"), meta.get("lon"), meta.get("lat")],
    )

    retenues = par_libelle(rows)

    _invalider_figeage(con, code_prel)
    con.execute("DELETE FROM mesures WHERE code_prelevement = ?", [code_prel])
    con.execute("DELETE FROM prelevements WHERE code_prelevement = ?", [code_prel])

    con.execute(
        "INSERT INTO prelevements VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            code_prel,
            insee,
            meta.get("code_installation_amont"),
            meta.get("nom_installation_amont"),
            meta.get("nom_distributeur"),
            meta.get("nom_uge"),
            meta.get("codes_reseaux"),
            meta.get("noms_reseaux"),
            meta.get("code_lieu_analyse"),
            (meta.get("date_prelevement") or None),
            nb,
            est_complet,
            meta.get("conclusion_conformite"),
            meta.get("conf_limites_bact"),
            meta.get("conf_limites_pc"),
            meta.get("conf_references_pc"),
            meta.get("source_url"),
        ],
    )

    lignes = []
    for lib, r in retenues.items():
        num, lq, unite, quantifie = _valeur(r)
        code_param = r.get("code_parametre")
        brut_limite = r.get("limite_qualite_parametre")
        brut_reference = r.get("reference_qualite_parametre")
        # La limite déclarée avec la mesure est la grille d'AUJOURD'HUI. Elle
        # ne remplace pas le référentiel daté : elle le complète là où il est
        # muet, et permet de le contrôler là où il parle (cf. build_db.py).
        limite_num, _ = parse_limite(brut_limite)
        reference_num, _ = parse_limite(brut_reference)
        # Les DEUX bornes de la référence. `reference_num` ci-dessus ne retient
        # que la borne haute et vaut None dès que la source encadre des deux
        # côtés (« >=6,5 et <=9 ») : toutes les références bilatérales étaient
        # invisibles, et avec elles les eaux agressives — celles qui attaquent
        # les canalisations entre le point de prélèvement et le robinet.
        # `bornes_reference` est le seul endroit qui décide de la forme.
        reference_min, reference_max = bornes_reference(brut_reference)
        lignes.append([
            code_prel,
            insee,
            str(code_param) if code_param not in (None, "") else None,
            (r.get("code_parametre_cas") or None),
            lib,
            norm(lib),
            num,
            (r.get("resultat_alphanumerique") or None),
            lq,
            quantifie,
            unite,
            norm_unite(unite),
            (brut_limite or None),
            limite_num,
            (brut_reference or None),
            reference_num,
            reference_min,
            reference_max,
        ])
    if lignes:
        con.executemany(
            "INSERT INTO mesures VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lignes
        )

    return code_prel, nb, est_complet

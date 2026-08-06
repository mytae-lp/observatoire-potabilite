# -*- coding: utf-8 -*-
"""
Ingestion d'un bulletin (un prélèvement, une date, l'intégralité de ses paramètres).

Idempotent : réingérer un prélèvement déjà présent le REMPLACE (DELETE puis
INSERT sur code_prelevement). On peut donc relancer une collecte interrompue
sans précaution et sans doublon.

Ce module ne fait aucune requête réseau : il reçoit les lignes déjà obtenues.
"""
from common import norm, parse_val, SEUIL_COMPLET


def _valeur(row):
    """
    Lignes Hub'Eau -> (resultat_num, lq, unite, est_quantifie).

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


def code_prelevement(meta, rows):
    """Identifiant du prélèvement : celui d'Hub'Eau si présent, sinon reconstruit."""
    for r in rows:
        cp = r.get("code_prelevement")
        if cp:
            return str(cp)
    insee = meta.get("code_insee", "")
    date = (meta.get("date_prelevement") or "ND")[:10]
    inst = norm(meta.get("nom_installation", ""))[:20]
    return f"{insee}_{date}_{inst}"


def ingest_bulletin(con, meta, rows):
    """
    Insère commune + prélèvement + mesures. Retourne (code_prelevement, nb, est_complet).

    nb = nombre de paramètres DISTINCTS du bulletin : c'est lui qui décide si le
    prélèvement est complet, donc s'il entre dans les analyses (CLAUDE.md §2.3).
    """
    insee = meta["code_insee"]
    code_prel = code_prelevement(meta, rows)

    con.execute(
        "INSERT OR REPLACE INTO communes VALUES (?,?,?)",
        [insee, meta.get("nom"), meta.get("code_departement")],
    )

    # Déduplication par libellé : la PK de mesures est (code_prelevement, libelle_parametre)
    par_libelle = {}
    for r in rows:
        lib = r.get("libelle_parametre")
        if not lib:
            continue
        par_libelle.setdefault(lib, r)

    nb = len(par_libelle)
    est_complet = nb > SEUIL_COMPLET

    con.execute("DELETE FROM mesures WHERE code_prelevement = ?", [code_prel])
    con.execute("DELETE FROM prelevements WHERE code_prelevement = ?", [code_prel])

    con.execute(
        "INSERT INTO prelevements VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            code_prel,
            insee,
            meta.get("nom_installation"),
            meta.get("nom_distributeur"),
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
    for lib, r in par_libelle.items():
        num, lq, unite, quantifie = _valeur(r)
        code_param = r.get("code_parametre")
        lignes.append([
            code_prel,
            insee,
            str(code_param) if code_param not in (None, "") else None,
            lib,
            norm(lib),
            num,
            (r.get("resultat_alphanumerique") or None),
            lq,
            quantifie,
            unite,
            (r.get("limite_qualite_parametre") or r.get("reference_qualite_parametre") or None),
        ])
    if lignes:
        con.executemany(
            "INSERT INTO mesures VALUES (?,?,?,?,?,?,?,?,?,?,?)", lignes
        )

    return code_prel, nb, est_complet

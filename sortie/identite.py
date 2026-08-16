# -*- coding: utf-8 -*-
"""
Ce qu'une molécule EST — la seule chose qu'aucune requête ne rend.

Le répertoire des substances est entièrement dérivé : combien de bulletins
cherchent une molécule, combien la quantifient, à quoi on la compare et depuis
quelle date. Rien là-dedans ne dit ce que la molécule est. Un lecteur qui
tombe sur « CGA 369873 » n'apprend rien d'un tableau, si exact soit-il.

Cette identité vit dans une table versionnée, `referentiel/identite_substances.csv`,
jamais dans de la prose — même dispositif que `referentiel/indicateurs.csv` et
que la table de rétention des procédés annoncée au §2.2 : une ligne, ses
`sources`, sa `fiabilite`. Le §2.7 s'y applique entier, et c'est le point qui
compte : **une identité non sourcée ne s'affiche pas.** Le répertoire préfère
ne rien dire à dire quelque chose de plausible — c'est la même asymétrie qu'au
§2.13, un faux positif coûte plus cher qu'un silence.

**Ce module est lu par la couche de sortie, jamais par `build_db.py`.**
L'empreinte du moteur ne prend que `figer.py`, `build_db.py` et `common.py` ;
y charger cette table ferait dépendre huit heures de refigeage d'une phrase qui
ne déplace aucun verdict.
"""

import csv
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "src"))

import common as C  # noqa: E402

TABLE = os.path.join(RACINE, "referentiel", "identite_substances.csv")

CHAMPS = ("quoi", "usage", "molecule_mere", "statut_autorisation")


def charger():
    """
    {clé: ligne} — deux clés par molécule, le code SANDRE et le libellé normalisé.

    L'ordre d'appariement reprend celui du moteur (`v_mesures_ref`) : par code
    d'abord, par libellé normalisé ensuite. Une ligne qui ne porte ni l'un ni
    l'autre est ignorée, et une ligne sans `sources` aussi — sans quoi la règle
    du §2.7 ne serait qu'une intention.
    """
    par_code, par_libelle = {}, {}
    if not os.path.exists(TABLE):
        return par_code, par_libelle
    with open(TABLE, encoding="utf-8") as fh:
        lignes = [l for l in fh if not l.lstrip().startswith("#") and l.strip()]
    for ligne in csv.DictReader(lignes, delimiter=";"):
        if not (ligne.get("sources") or "").strip():
            continue
        if not any((ligne.get(c) or "").strip() for c in CHAMPS):
            continue
        code = (ligne.get("code_parametre") or "").strip()
        libelle = (ligne.get("libelle_norm") or "").strip()
        if code:
            par_code[code] = ligne
        if libelle:
            par_libelle[C.norm(libelle)] = ligne
    return par_code, par_libelle


def pour(tables, code_parametre, libelle_parametre):
    """
    La ligne d'identité d'un paramètre, ou None.

    **Le libellé est interrogé AVANT le code, et l'ordre n'est pas indifférent.**
    Un code SANDRE porte souvent plusieurs libellés — 2094 pour « Dalapon 85 »
    et « Dalapon spd », 1370 pour l'aluminium total et dissous, 2013 pour les
    deux anthraquinones. En cherchant par code d'abord, on rendait la ligne du
    VOISIN : la page de l'un affichait l'identité de l'autre.

    Constaté le 15 août 2026, et c'est la troisième fois de la journée que la
    même hypothèse fausse — « un code, un libellé » — se retrouve tapie à un
    endroit différent. Elle est sans conséquence tant que les deux libellés
    partagent le même texte, et elle devient un faux affichage à la minute où
    ils divergent : les deux anthraquinones, écrites séparément le jour même,
    étaient déjà dans ce cas.

    Le libellé identifie, le code confirme.
    """
    par_code, par_libelle = tables
    ligne = par_libelle.get(C.norm(libelle_parametre or ""))
    if ligne is not None:
        return ligne
    if code_parametre and str(code_parametre) in par_code:
        return par_code[str(code_parametre)]
    return None


def bloc(ligne, h):
    """
    Le paragraphe « ce que c'est », ou une chaîne vide.

    Vide veut dire « pas encore sourcé », et le répertoire l'écrit en toutes
    lettres à côté : un blanc silencieux se lirait comme « rien à en dire ».
    """
    if not ligne:
        return ""
    o = []
    if (ligne.get("quoi") or "").strip():
        o.append(f'<p>{h(ligne["quoi"].strip())}</p>')
    details = []
    for cle, etiquette in (("usage", "Usage"),
                           ("molecule_mere", "Molécule mère"),
                           ("statut_autorisation", "Statut d'autorisation")):
        if (ligne.get(cle) or "").strip():
            details.append(f'<li><b>{etiquette} :</b> {h(ligne[cle].strip())}</li>')
    if details:
        o.append("<ul>" + "".join(details) + "</ul>")
    fiabilite = (ligne.get("fiabilite") or "").strip()
    o.append(f'<p class="bnote">Sources : {h(ligne.get("sources") or "—")}. '
             f'Fiabilité : <b>{h(fiabilite or "—")}</b>.'
             + (' <b>Valeur en « à vérifier » : elle est signalée comme telle '
                'et ne s\'arrondit jamais en « vérifié ».</b>'
                if fiabilite != "verifie" else "") + '</p>')
    return "".join(o)

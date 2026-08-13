# -*- coding: utf-8 -*-
"""
L'alerte « analyse complète ancienne » — le texte, fabriqué ici.

POURQUOI CE MODULE EXISTE, ET POURQUOI LE TEXTE EST EN PYTHON
-------------------------------------------------------------
Les deux bandeaux existants de la fiche ont leur texte écrit en dur dans
`site/gabarits/fiche.js`. Conséquence : **aucun contrôle de
`tests/test_sorties.py` ne les relit**, parce que la moisson des sorties ne
lit que le JSON. Écrire une troisième prose au même endroit, sur plusieurs
milliers de fiches, ce serait publier du texte que rien ne vérifie. Le texte
est donc composé ici, il descend dans le JSON de la fiche, et il devient
contrôlable comme le reste.

CE QUE L'ALERTE DIT, ET CE QU'ELLE NE DIT PAS
---------------------------------------------
Elle dit l'âge de ce qu'on sait. **Elle n'accuse personne** (§2.1) : ni l'ARS,
ni l'exploitant, ni la commune. La liste des substances recherchées est arrêtée
à l'échelle régionale pour la durée d'un marché d'analyses — elle ne se décide
ni commune par commune ni prélèvement par prélèvement.

**Les deux compléments sont obligatoires**, et l'alerte ne s'affiche pas sans
au moins le premier :

1. le **nombre de contrôles** intervenus depuis. Sans lui, l'alerte se lit
   comme un abandon de surveillance — ce qui serait faux et injuste : sur les
   413 communes mesurées le 13 août 2026, **aucune n'était à zéro contrôle**,
   la médiane était de 15 et le maximum de 188 ;
2. le **nom des substances** qui dépassaient à la dernière analyse complète et
   qu'on ne mesure plus depuis au moins deux ans.

**« Ne figure plus dans les analyses enregistrées » n'est pas « a disparu de
l'eau »** (§2.4). Une substance non mesurée n'est ni confirmée ni écartée :
c'est un indéterminé, et le texte le dit en toutes lettres.

DEUX ÂGES QUI NE SE CONFONDENT PAS
-----------------------------------
L'âge du **bulletin** et l'âge de la **dernière mesure d'une substance** sont
deux nombres différents — 119 et 71 mois à Réclainville. Les mélanger produit
un chiffre faux ; ils s'affichent donc à deux endroits distincts.

SEUIL : 24 MOIS
---------------
Décision de Yannick du 13 août 2026, sur le corpus mesuré : à 24 mois l'alerte
touche une commune documentée sur dix ; à 12 mois, une sur quatre — à ce
niveau ce n'est plus une alerte, c'est le décor. Ce seuil est une **décision du
projet**, pas une règle réglementaire, et le texte ne le présente jamais
autrement.
"""
import csv
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUIVI_CSV = os.path.join(RACINE, "data", "suivi_panel",
                         "alerte_panel_reduit.csv")
SEUIL_MOIS = 24

_CACHE = None


def _mois_fr(iso):
    MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre")
    try:
        a, m, j = iso[:10].split("-")
        return f"{int(j)} {MOIS[int(m) - 1]} {a}"
    except Exception:
        return iso or ""


def _charger():
    """Le relevé, une ligne par commune. Rend {} si le fichier est absent.

    Ne jamais faire échouer une lecture ici : ce relevé est un enrichissement
    de la fiche, pas une dépendance technique. Une fiche sans lui reste juste,
    elle est seulement moins complète.
    """
    global _CACHE
    if _CACHE is None:
        _CACHE = {}
        if os.path.exists(SUIVI_CSV):
            with open(SUIVI_CSV, encoding="utf-8-sig") as fh:
                for r in csv.DictReader(fh, delimiter=";"):
                    _CACHE[r["code_insee"]] = r
    return _CACHE


def _entier(v, defaut=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return defaut


def _lister(noms):
    """« a, b et c » — jamais « a, b, c », qui se lit comme une liste tronquée."""
    noms = [n for n in noms if n]
    if not noms:
        return ""
    if len(noms) == 1:
        return noms[0]
    return ", ".join(noms[:-1]) + " et " + noms[-1]


def alerte(code_insee):
    """
    Le bandeau d'une commune, ou None s'il n'y a pas lieu d'en afficher un.

    Rend un dict : `titre`, `paragraphes` (liste), `mois`, et `substances`
    (la liste nue, pour un contrôle automatique qui n'aurait pas à relire la
    prose).
    """
    r = _charger().get(str(code_insee))
    if not r:
        return None

    mois = _entier(r.get("mois_ecoules"))
    if mois < SEUIL_MOIS:
        return None

    controles = _entier(r.get("nb_controles_depuis"))
    # RÈGLE DURE : sans le nombre de contrôles, pas d'alerte. L'ancienneté
    # seule se lit comme un abandon de surveillance, et ce serait faux.
    if controles <= 0:
        return None

    rattachee = r.get("statut") == "rattachee_reseau"
    ou = r.get("commune_prelevement") or ""
    date = _mois_fr(r.get("date_derniere_complete"))
    nb_par = _entier(r.get("nb_parametres"))
    taille = _entier(r.get("mediane_taille_controle"))
    dernier = _mois_fr(r.get("dernier_controle"))

    if rattachee:
        titre = (f"La dernière analyse complète du réseau qui alimente cette "
                 f"commune a {mois} mois.")
        premier = (f"Elle a été faite le {date}"
                   + (f" à {ou}" if ou else "")
                   + (f" et portait {nb_par} paramètres." if nb_par else ".")
                   + " Cette commune n'a pas d'analyse complète à elle :"
                   " c'est celle de son réseau que cette fiche présente.")
    else:
        titre = f"La dernière analyse complète de cette eau a {mois} mois."
        premier = (f"Elle a été faite le {date}"
                   + (f" et portait {nb_par} paramètres." if nb_par else ".")
                   + " C'est celle que cette fiche présente.")

    second = (f"Depuis, {controles} analyse{'s' if controles > 1 else ''} de "
              f"contrôle {'ont' if controles > 1 else 'a'} été "
              f"{'faites' if controles > 1 else 'faite'} sur l'eau distribuée "
              f"ici, la dernière le {dernier}.")
    if taille:
        second += (f" Une analyse de contrôle porte moins de paramètres qu'une "
                   f"analyse complète — ici {taille} en médiane. **L'eau "
                   f"continue donc d'être suivie ; ce qui change, c'est "
                   f"l'étendue de ce qui est recherché.**")

    paragraphes = [premier, second]

    # Le troisième paragraphe n'existe que s'il y a matière. Une commune sans
    # substance abandonnée reçoit l'alerte d'ancienneté, et rien de plus :
    # inventer un manque serait un faux positif.
    substances = []
    detail = (r.get("detail_abandons") or "").strip()
    if detail:
        for bloc in detail.split(" | "):
            nom = bloc.split(" (dernière mesure")[0].strip()
            if nom:
                substances.append(nom)
    if substances:
        n = len(substances)
        paragraphes.append(
            f"{n} paramètre{'s' if n > 1 else ''} qui "
            f"{'dépassaient leur' if n > 1 else 'dépassait sa'} limite le {date} "
            f"ne {'figurent' if n > 1 else 'figure'} plus dans les analyses "
            f"enregistrées depuis : {_lister(substances)}. **Ce qui n'est pas "
            f"mesuré ne peut être ni confirmé ni écarté : la valeur de "
            f"{'ces paramètres' if n > 1 else 'ce paramètre'} aujourd'hui "
            f"n'est pas connue.**")
        # Une somme n'est pas une substance, et son extinction est d'une autre
        # nature : c'est une limite opposable qui cesse d'être calculable.
        if any("total des pesticides" in s.lower() for s in substances):
            paragraphes.append(
                "Le total des pesticides analysés n'est pas une substance : "
                "c'est la somme de ceux qui ont été recherchés et quantifiés. "
                "Quand les substances qui la composent ne sont plus "
                "recherchées, la somme ne se calcule plus.")

    paragraphes.append(
        "La liste des substances recherchées lors d'un contrôle est arrêtée à "
        "l'échelle de la région, pour la durée d'un marché d'analyses. Elle ne "
        "se décide ni commune par commune, ni prélèvement par prélèvement.")

    return {
        "titre": titre,
        "paragraphes": paragraphes,
        "mois": mois,
        "controles": controles,
        "substances": substances,
        "rattachee": rattachee,
        "seuil_mois": SEUIL_MOIS,
    }

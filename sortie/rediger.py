# -*- coding: utf-8 -*-
"""
Rédaction DÉRIVÉE de la base — la part de la prose qui ne s'invente pas.

    python3 sortie/rediger.py 28379          # voir ce qui serait écrit
    python3 sortie/rediger.py --toutes

Ce module ne stocke rien. Il compose des phrases au moment de la construction
de la fiche, à partir de `analyses_figees` et `verdicts_figes` uniquement.
Conséquence voulue : **le texte ne peut pas devenir faux sans que le chiffre
change en même temps.** Si le référentiel bouge et qu'on refige, la phrase
bouge avec lui. Un texte figé à côté de chiffres qui évoluent, c'est
exactement la demi-vérité que le projet dénonce.

Trois origines de prose, jamais confondues (cf. `docs/ARCHITECTURE.md` §5,
d'où le §8quater de CLAUDE.md a été déplacé le 8 août 2026) :

    auteur   la main de Yannick, dans sortie/redactions.json
    propose  rédigé par le modèle, contexte extérieur inclus, dans
             sortie/redactions_proposees.json — à relire, marqué comme tel
    derive   ce fichier : aucune connaissance extérieure, aucun adjectif
             d'appréciation, aucun nombre qui ne vienne d'une requête

Ce que ce module s'interdit
---------------------------
  · toute recommandation d'équipement, de filtration ou de produit (§2.2) ;
  · toute mise en cause d'un acteur — on interroge la norme (§2.1) ;
  · tout qualificatif sanitaire : « dangereux », « sain », « à risque »,
    « inquiétant ». Il décrit des écarts à des seuils datés, rien de plus ;
  · toute affirmation d'absence. Un non-quantifié est « sous la limite de
    quantification », jamais « absent » (§2.4).
"""
import argparse
import os
import sys

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

from common import DB_PATH  # noqa: E402

FAMILLES_SYNTHESE = ("pesticide", "metabolite", "PFAS", "organique")


def nb(x, dec=6):
    """Nombre à la française, sans zéros inutiles."""
    if x is None:
        return ""
    s = f"{x:.{dec}f}".rstrip("0").rstrip(".")
    return (s or "0").replace(".", ",")


def pluriel(n, singulier, plur=None):
    return f"{n} {singulier if abs(n) <= 1 else (plur or singulier + 's')}"


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def date_fr(d):
    """Une date de prélèvement est lue par un habitant, pas par une machine."""
    try:
        a, m, j = str(d)[:10].split("-")
        return f"{int(j)}{'er' if j == '01' else ''} {MOIS[int(m) - 1]} {a}"
    except (ValueError, IndexError, AttributeError):
        return str(d)


def liste_fr(elements, maxi=None):
    """« a, b et c ». Tronque en disant qu'elle tronque, jamais en silence."""
    elements = list(elements)
    reste = 0
    if maxi and len(elements) > maxi:
        reste = len(elements) - maxi
        elements = elements[:maxi]
    if not elements:
        return ""
    if len(elements) == 1:
        texte = elements[0]
    else:
        texte = ", ".join(elements[:-1]) + " et " + elements[-1]
    return texte + (f", et {reste} autre(s)" if reste else "")


# ---------------------------------------------------------------------------
def _lignes(con, code_prel, version):
    return con.execute("""
        SELECT libelle_parametre, resultat_num, lq, unite, seuil_applicable,
               seuil_2016, grille_applicable, depasse_applicable,
               bascule_2016_2026, bascule_datee, indetermine_strict,
               indetermine_condition, famille, est_quantifie, seuil_strict,
               lq_aveugle, lq_rapport_seuil
        FROM verdicts_figes
        WHERE code_prelevement = ? AND version_referentiel = ?
        ORDER BY resultat_num DESC NULLS LAST
    """, [code_prel, version]).fetchall()


def _mesure(r):
    """« Chlorothalonil R471811 à 1,607 µg/L »."""
    u = f" {r[3]}" if r[3] else ""
    return f"{r[0]} à {nb(r[1])}{u}"


def sections(con, a, version, lignes=None):
    """
    `a` est une ligne de `analyses_figees` en dictionnaire.
    Renvoie [{t, x, o}] — titre, texte, origine.
    """
    lignes = _lignes(con, a["code_prelevement"], version) if lignes is None else lignes
    dep = [r for r in lignes if r[7]]
    bas = [r for r in lignes if r[8] and not r[7]]
    quant = [r for r in lignes if r[13] and r[12] in FAMILLES_SYNTHESE and not r[7]]
    aveugles = [r for r in lignes if r[15]]
    # Un aveugle est presque toujours AUSSI un indéterminé au sens du repère le
    # plus strict — 46 sur 46 dans le corpus au 8 août 2026. Les laisser dans
    # les deux sections ferait dire deux fois la même chose, et le lecteur
    # croirait à deux problèmes là où il n'y en a qu'un. La section 4 garde
    # donc ce que la section 4bis ne dit pas.
    ind = [r for r in lignes
           if (r[10] or r[11]) and not r[7] and not r[8] and not r[15]]

    out = []

    # --- 1. l'inventaire ---------------------------------------------------
    morceaux = []
    if dep:
        morceaux.append(
            f"{pluriel(len(dep), 'paramètre')} dépasse"
            + ("nt" if len(dep) > 1 else "")
            + " le seuil qui s'appliquait le jour du prélèvement : "
            + liste_fr([f"{_mesure(r)} pour un seuil de {nb(r[4])} {r[3] or ''}".strip()
                        for r in dep], 6))
    if quant:
        morceaux.append(
            f"{pluriel(len(quant), 'substance de synthèse', 'substances de synthèse')} "
            "est quantifiée sous son seuil" if len(quant) <= 1 else
            f"{len(quant)} substances de synthèse sont quantifiées sous leur seuil")
        morceaux[-1] += " — " + liste_fr([_mesure(r) for r in quant], 8)
    if not dep and not quant:
        morceaux.append(
            "aucune substance de synthèse n'est quantifiée et aucun paramètre ne "
            "dépasse son seuil. Cela ne veut pas dire qu'il n'y en a pas : cela veut "
            "dire qu'aucune n'a été mesurée au-dessus de la limite de quantification "
            "du laboratoire")
    out.append({"t": "Ce que le bulletin contient",
                "x": ". ".join(m[0].upper() + m[1:] for m in morceaux) + ".",
                "o": "derive"})

    # --- 2. le réétalonnage ------------------------------------------------
    if bas:
        detail = liste_fr(
            [f"{_mesure(r)}, sous la limite actuelle de {nb(r[4])} {r[3] or ''}".strip()
             + f" mais au-dessus de celle de {nb(r[5])} en vigueur en 2016"
             for r in bas], 5)
        datees = sum(1 for r in bas if r[9])
        out.append({
            "t": "Le réétalonnage — ce qui a changé sans que l'eau change",
            "x": (f"{pluriel(len(bas), 'mesure')} de ce bulletin "
                  + ("bascule" if len(bas) == 1 else "basculent")
                  + " d'une grille à l'autre : " + detail + ". "
                  + (("Cette bascule est datable au jour près : "
                      if len(bas) == 1 else
                      f"{datees} de ces bascules sont datables au jour près : ")
                     + "le prélèvement est postérieur au déplacement de la limite, et "
                       "la même valeur, la veille, aurait été non conforme. "
                     if datees else "")
                  + "Ce n'est pas l'eau qui a changé entre les deux lectures."),
            "o": "derive"})

    # --- 3. l'effort de recherche -----------------------------------------
    anterieurs = con.execute("""
        SELECT date_prelevement, nb_parametres FROM analyses_figees
        WHERE version_referentiel = ? AND code_insee = ?
          AND date_prelevement < ? ORDER BY date_prelevement DESC LIMIT 1
    """, [version, a["code_insee"], a["date_prelevement"]]).fetchone()
    texte = (f"{a['nb_parametres']} paramètres ont été recherchés sur ce prélèvement "
             f"(analyse dite {a['classe_effort']}), dont "
             f"{a['nb_synthese_recherchees']} substances de synthèse. "
             f"{a['nb_mesures_notees']} ont pu être comparés à un seuil, soit "
             f"{nb(a['pct_couverture'])} % ; les "
             f"{a['nb_mesures_lues'] - a['nb_mesures_notees']} autres n'ont aucun seuil "
             "de comparaison, ni au référentiel ni dans la limite déclarée par la "
             "source, et ne pèsent donc sur aucun verdict.")
    if anterieurs and anterieurs[1] and anterieurs[1] != a["nb_parametres"]:
        ecart = a["nb_parametres"] - anterieurs[1]
        texte += (f" Le prélèvement précédent de cette commune, le {date_fr(anterieurs[0])}, "
                  f"portait sur {anterieurs[1]} paramètres : l'effort de recherche a "
                  f"{'augmenté' if ecart > 0 else 'baissé'} de {abs(ecart)}. "
                  "Le nombre de paramètres cherchés ne mesure pas la qualité de l'eau, "
                  "il mesure ce qu'on a bien voulu chercher — deux bulletins d'efforts "
                  "différents ne se comparent pas directement.")
    out.append({"t": "L'effort de recherche", "x": texte, "o": "derive"})

    # --- 4. ce qu'on ne sait pas ------------------------------------------
    if ind:
        out.append({
            "t": "Ce que ce bulletin ne permet pas de dire",
            "x": (f"{pluriel(len(ind), 'paramètre reste indéterminé', 'paramètres restent indéterminés')} : "
                  + liste_fr([f"{r[0]} (limite de quantification {nb(r[2])} {r[3] or ''}".strip()
                              + f", seuil de comparaison "
                                f"{nb(r[4] if r[4] is not None else r[14])} "
                                f"{r[3] or ''})".replace(" )", ")")
                              for r in ind], 6)
                  + ". La limite de quantification du laboratoire se situe au-dessus du "
                    "seuil auquel on voudrait comparer : on ne peut pas affirmer que le "
                    "seuil est respecté, seulement qu'on ne sait pas. Un indéterminé "
                    "n'est pas un résultat conforme."),
            "o": "derive"})

    # --- 4bis. le plafond analytique (chantier C4) -------------------------
    # Le §2.4 vu par le bout de l'instrument. La section 4 dit qu'on ne sait
    # pas ; celle-ci dit POURQUOI on ne sait pas, et de combien on en est loin.
    # Elle ne met personne en cause : une limite de quantification est une
    # capacité d'appareil, pas une décision (§2.1).
    if aveugles:
        un = len(aveugles) == 1
        detail = liste_fr(
            [f"{r[0]} (LQ {nb(r[2])} {r[3] or ''}".strip()
             + f" pour un seuil de {nb(r[4])}"
             + (f", soit {nb(round(r[16], 1) if r[16] < 10 else round(r[16]))} fois plus haut)"
                if r[16] else ")")
             for r in aveugles], 6)
        texte = (f"{pluriel(len(aveugles), 'paramètre a été cherché', 'paramètres ont été cherchés')} "
                 "avec une limite de quantification supérieure au seuil auquel on "
                 + ("le" if un else "les") + f" compare : {detail}. "
                 + ("Sous cette valeur" if un else "Sous ces valeurs")
                 + ", l'analyse ne voit rien — elle ne permet ni de constater un "
                   "dépassement, ni d'affirmer que le seuil est respecté.")
        if a.get("aveugles_pour_mille"):
            texte += (f" Cela représente {nb(a['aveugles_pour_mille'])} pour mille des "
                      f"{a['nb_mesures_notees']} paramètres notés de ce bulletin. "
                      "C'est un taux, et c'est à ce titre qu'il se compare à celui d'une "
                      "autre commune : le compte brut, lui, dépend du nombre de "
                      "paramètres cherchés.")

        # Le barème — niveau 3 du chantier. Il ne vaut qu'à PARAMÈTRE CONSTANT,
        # et il porte toujours sa base : « le plus fin » sur 45 bulletins n'est
        # pas « le plus fin » sur 4 000 (§2.14 transposé à l'instrument).
        etendues = []
        for r in aveugles:
            c = con.execute("""
                SELECT c.lq_min, c.lq_max, c.nb_bulletins, c.nb_departements
                FROM lq_corpus c
                JOIN mesures m ON c.cle_param = COALESCE(m.code_parametre, m.libelle_norm)
                WHERE c.version_referentiel = ? AND m.code_prelevement = ?
                  AND m.libelle_parametre = ?
            """, [version, a["code_prelevement"], r[0]]).fetchone()
            if c and c[0] and c[1] and c[1] > c[0]:
                etendues.append(
                    f"{r[0]}, de {nb(c[0])} à {nb(c[1])} {r[3] or ''}".strip()
                    + f" sur {pluriel(c[2], 'bulletin')} et "
                      f"{pluriel(c[3], 'département')}"
                    + (f" — celle-ci en est {nb(round(r[2] / c[0], 1))} fois moins fine "
                       "que la plus basse relevée" if c[0] else ""))
        if etendues:
            # Point-virgule et non « et » : chaque élément porte déjà des
            # virgules, et une énumération à la française y deviendrait
            # illisible.
            texte += (" Le corpus a déjà relevé, pour les mêmes substances : "
                      + " ; ".join(etendues[:4])
                      + (f" ; et {len(etendues) - 4} autre(s)" if len(etendues) > 4 else "")
                      + ". Ces étendues sont celles des analyses réunies à ce jour, et "
                        "elles se déplaceront à mesure que le corpus grandira.")
        texte += (" Une limite de quantification élevée est une capacité d'instrument, "
                  "pas une négligence : ce qui est en cause ici est ce que le "
                  "dispositif permet de savoir.")
        out.append({"t": "Ce que le laboratoire ne pouvait pas voir",
                    "x": texte, "o": "derive"})

    # --- 5. le cumul -------------------------------------------------------
    if a["nb_synthese_quantifiees"]:
        texte = (f"{pluriel(a['nb_synthese_quantifiees'], 'substance de synthèse est quantifiée', 'substances de synthèse sont quantifiées')} "
                 "simultanément dans ce prélèvement")
        if a["charge_synthese_ug_l"]:
            texte += (f", pour une charge cumulée d'au moins "
                      f"{nb(round(a['charge_synthese_ug_l'], 4))} µg/L. Ce total est un "
                      "plancher : les substances non quantifiées y comptent pour zéro, "
                      "ce qu'elles ne sont pas")
        texte += (". La réglementation note chaque substance séparément ; elle n'évalue "
                  "pas leur action combinée.")
        if a["indice_danger"] is not None:
            texte += (f" L'indice de danger calculé par la méthode simplifiée du projet "
                      f"vaut {nb(round(a['indice_danger'], 2))} sur "
                      f"{pluriel(a['indice_danger_n'], 'substance')}. "
                      "C'est un raisonnement destiné à classer des bulletins entre eux, "
                      "pas une mesure de risque sanitaire, et il ne constitue pas un "
                      "verdict de potabilité.")
        out.append({"t": "Le cumul", "x": texte, "o": "derive"})

    return out


def _phrase_aveugles(a, lq):
    """
    La phrase du plafond analytique, dans un résumé où figure déjà le nombre
    d'indéterminés.

    Les deux ensembles se RECOUVRENT : un paramètre dont la LQ dépasse la
    limite réglementaire dépasse a fortiori le repère plus strict, quand il en
    existe un. Dans le corpus au 8 août 2026, les 46 aveugles sont tous parmi
    les 55 indéterminés. Les additionner annoncerait 101 problèmes là où il y
    en a 55, ce qui serait exactement le genre d'arithmétique dont le projet
    fait le reproche au reste du monde.

    `lq['dedans']` est donc COMPTÉ, pas supposé : rien n'interdit qu'un
    paramètre sans repère strict soit aveugle sans être indéterminé.
    """
    if not lq or not lq.get("nb"):
        return ""
    n, dedans = lq["nb"], lq.get("dedans", 0)
    if a.get("nb_indetermines") and dedans == n:
        tete = (" Pour " + ("l'un d'eux" if n == 1 else f"{n} d'entre eux")
                + ", ce n'est pas seulement le repère le plus strict qui est hors "
                  "de portée")
    elif a.get("nb_indetermines") and dedans:
        tete = (f" Pour {n} paramètre(s), dont {dedans} déjà comptés ci-dessus, "
                "ce n'est pas seulement le repère le plus strict qui est hors de "
                "portée")
    else:
        tete = (f" Pour {pluriel(n, 'paramètre')}, le repère hors de portée n'est "
                "pas le plus strict")
    return (tete + " : la limite de quantification du laboratoire se situe au-dessus "
            "de la limite réglementaire elle-même, et l'analyse ne conclut donc pas.")


def lecture_citoyenne(a, lq=None):
    if a["nb_depasse_applicable"]:
        base = (f"{pluriel(a['nb_depasse_applicable'], 'paramètre dépassait', 'paramètres dépassaient')} "
                "le seuil applicable le jour du prélèvement.")
    elif a["nb_bascules"]:
        base = ("Aucun dépassement à la date du prélèvement, mais "
                f"{pluriel(a['nb_bascules'], 'mesure aurait dépassé', 'mesures auraient dépassé')} "
                "la limite en vigueur en 2016.")
    else:
        base = "Aucun dépassement à la date du prélèvement, aucune bascule réglementaire."
    return (base + f" Lecture faite sur {a['nb_mesures_notees']} paramètres notés "
            f"parmi les {a['nb_mesures_lues']} mesurés, soit "
            f"{nb(a['pct_couverture'])} % du bulletin."
            + (f" {pluriel(a['nb_indetermines'], 'paramètre reste indéterminé', 'paramètres restent indéterminés')}."
               if a["nb_indetermines"] else "")
            # Une absence de dépassement annoncée sans dire quelle part de
            # l'analyse ne pouvait pas conclure est une demi-vérité — le §2.8
            # transposé du seuil à l'instrument (chantier C4).
            + _phrase_aveugles(a, lq))


def verdict(a, lq=None):
    if a["nb_depasse_applicable"]:
        t = (f"Bulletin portant {pluriel(a['nb_depasse_applicable'], 'dépassement')} "
             "du seuil applicable à la date du prélèvement.")
    elif a["nb_bascules"]:
        t = (f"Bulletin sans aucun dépassement aujourd'hui, et portant "
             f"{pluriel(a['nb_bascules'], 'bascule')} : conforme à la grille en vigueur, "
             "il ne l'aurait pas été à celle de 2016.")
    else:
        t = ("Bulletin sans dépassement à la date du prélèvement et sans bascule "
             "réglementaire.")
    return (t + f" Sur {a['nb_parametres']} paramètres recherchés, "
            f"{a['nb_mesures_notees']} ont pu être notés."
            + (f" {pluriel(a['nb_indetermines'], 'reste indéterminé', 'restent indéterminés')}, "
               "faute d'une limite de quantification assez basse."
               if a["nb_indetermines"] else "")
            + _phrase_aveugles(a, lq)
            + (f" Soit {nb(a.get('aveugles_pour_mille'))} pour mille des paramètres "
               "notés — le taux, et non le compte, est ce qui se compare d'un "
               "bulletin à l'autre."
               if (lq or {}).get("nb") and a.get("aveugles_pour_mille") else ""))


def rediger(con, a, version):
    """
    Toutes les parties dérivables, en une fois.

    Le détail du bulletin est lu UNE fois et partagé : les trois parties
    doivent parler du même objet, et le recouvrement entre indéterminés et
    paramètres aveugles se compte sur les lignes, il ne se déduit pas des
    compteurs (cf. `_phrase_aveugles`).
    """
    lignes = _lignes(con, a["code_prelevement"], version)
    aveugles = [r for r in lignes if r[15]]
    lq = {"nb": len(aveugles),
          "dedans": sum(1 for r in aveugles if r[10] or r[11])}
    return {"analyse": sections(con, a, version, lignes),
            "lecture_citoyenne": lecture_citoyenne(a, lq),
            "verdict": verdict(a, lq),
            "origine": "derive"}


# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Rédaction dérivée de la base")
    p.add_argument("insees", nargs="*")
    p.add_argument("--toutes", action="store_true")
    args = p.parse_args()

    con = duckdb.connect(DB_PATH, read_only=True)
    version = con.execute("SELECT version_referentiel FROM analyses_figees "
                          "GROUP BY 1 ORDER BY MAX(calcule_le) DESC LIMIT 1").fetchone()[0]
    where, params = "WHERE version_referentiel = ?", [version]
    if args.insees:
        where += f" AND code_insee IN ({','.join('?' * len(args.insees))})"
        params += args.insees
    elif not args.toutes:
        p.error("donne au moins un code INSEE, ou --toutes")

    rows = con.execute(f"SELECT * FROM analyses_figees {where} "
                       "ORDER BY commune, date_prelevement DESC", params).fetchall()
    cols = [d[0] for d in con.description]
    for r in rows:
        a = dict(zip(cols, r))
        print("=" * 72)
        print(f"{a['commune']} ({a['dept']}) — {a['date_prelevement']}")
        print("=" * 72)
        d = rediger(con, a, version)
        for s in d["analyse"]:
            print(f"\n### {s['t']}\n{s['x']}")
        print(f"\n### Lecture citoyenne\n{d['lecture_citoyenne']}")
        print(f"\n### Verdict\n{d['verdict']}\n")
    con.close()


if __name__ == "__main__":
    main()

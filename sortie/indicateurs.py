# -*- coding: utf-8 -*-
"""
Les indicateurs de la fiche : ce qu'il y a dans l'eau, et ce que ça vaut.

    python3 sortie/indicateurs.py 28379

Trois groupes, et l'ordre compte
--------------------------------
    polluants  ce qu'on a trouvé — pesticides, PFAS, nitrates, sous-produits
               de chloration, cumul
    eau        quelle eau c'est — pH, minéralisation, dureté, matière
               organique. Ce n'est pas de la pollution : c'est le caractère de
               la ressource, et une eau agressive est un vrai sujet.
    lecture    ce que vaut cette lecture — effort de recherche, couverture,
               indéterminés. Obligations 1 et 2 du §8bis : jamais un
               « conforme » sans son dénominateur.

Aucun seuil n'est écrit ici
---------------------------
Les valeurs de comparaison viennent de `verdicts_figes` — donc du référentiel
daté — ou de la limite que la source déclare avec la mesure. Ce module ne fait
que rapprocher une mesure de ses seuils et en tirer un état.

Les états d'affichage, et les trois verdicts
--------------------------------------------
    conforme      quantifié, sous le seuil applicable à la date
    proche        quantifié, entre 85 % et 100 % du seuil. **Conforme aussi**
    depassement   quantifié, au-dessus
    bascule       sous le seuil d'aujourd'hui, au-dessus de celui de 2016
    indetermine   la limite de quantification est au-dessus du seuil auquel on
                  voudrait comparer — on ne sait pas, et ça ne se peint pas en
                  vert (CLAUDE.md §2.4)
    absent        le paramètre n'a pas été recherché. Ce n'est pas un résultat.

Ce sont des états d'AFFICHAGE. Le projet a **trois verdicts** — conforme,
dépassement, indéterminé — et il n'en aura pas un quatrième. `proche` (décision
D9) ne figure ni dans `analyses_figees`, ni dans une conclusion, ni dans une
métadonnée : il change la couleur d'une barre, parce qu'entre l'incertitude de
mesure et la finesse du laboratoire, le dernier pour cent avant une limite ne
veut plus rien dire.

Le plafond analytique
---------------------
Chantier C4. Un « non quantifié » ne porte pas la même information selon la
finesse du laboratoire. Quand la LQ dépasse le seuil auquel on compare, la
tuile porte sa mention — `lq_aveugle` et `lq_mention` — et `plafond_analytique()`
en donne la lecture d'ensemble : le taux au bulletin, et le barème qui situe
cette LQ parmi celles du corpus, à paramètre constant.
"""
import argparse
import csv
import math
import os
import sys

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

from common import DB_PATH, norm, parse_limite, parse_plage  # noqa: E402

DEFINITIONS = os.path.join(RACINE, "referentiel", "indicateurs.csv")

GROUPES = [
    ("polluants", "Ce qu'on a trouvé dans cette eau",
     "Chaque valeur est comparée au seuil qui s'appliquait <b>le jour du "
     "prélèvement</b>, et non à celui d'aujourd'hui."),
    ("eau", "Quelle eau c'est",
     "Ces paramètres ne décrivent pas une pollution : ils décrivent le "
     "caractère de la ressource. Ils sortent de leur plage sans que rien ne "
     "soit « dépassé » au sens sanitaire."),
    ("lecture", "Ce que vaut cette lecture",
     "Sans ces trois nombres, aucun des précédents ne peut être comparé à ceux "
     "d'une autre commune."),
]


def _nb(x, dec=6):
    if x is None:
        return ""
    s = f"{x:.{dec}f}".rstrip("0").rstrip(".")
    return (s or "0").replace(".", ",")


def definitions():
    """Le fichier versionné, tel quel. Les lignes de commentaire sautent."""
    with open(DEFINITIONS, encoding="utf-8-sig") as fh:
        lignes = [l for l in fh if l.strip() and not l.lstrip().startswith("#")]
    out = []
    for d in csv.DictReader(lignes, delimiter=";"):
        d["ordre"] = int(d["ordre"])
        d["candidats"] = [norm(x) for x in (d["reference"] or "").split("|") if x.strip()]
        out.append(d)
    return sorted(out, key=lambda d: (d["groupe"], d["ordre"]))


# ---------------------------------------------------------------------------
def _mesures(con, code_prel, version):
    """Toutes les mesures du bulletin, avec leurs seuils figés et les limites
    que la source déclare — indexées par libellé normalisé."""
    rows = con.execute("""
        SELECT m.libelle_parametre, m.resultat_num, m.lq, m.est_quantifie, m.unite,
               m.limite_brute, m.reference_brute,
               f.seuil_applicable, f.seuil_2016, f.seuil_strict,
               f.depasse_applicable, f.bascule_2016_2026,
               f.indetermine_strict, f.indetermine_condition, f.fiabilite,
               f.lq_aveugle, f.lq_rapport_seuil
        FROM mesures m
        LEFT JOIN verdicts_figes f
               ON f.code_prelevement = m.code_prelevement
              AND f.libelle_parametre = m.libelle_parametre
              AND f.version_referentiel = ?
        WHERE m.code_prelevement = ?
    """, [version, code_prel]).fetchall()
    return {norm(r[0]): r for r in rows}


# La zone d'approche — décision D9 de `docs/CHARTE_GRAPHIQUE.md`, prise par
# Yannick le 14 août 2026.
#
# Une eau à 99 % d'une limite est conforme, et le restera. Mais entre
# l'incertitude de mesure et la limite de quantification du laboratoire, ce
# dernier pour cent ne veut plus rien dire : la barre change donc de couleur
# **avant** la limite, pas au moment où elle est franchie.
#
# **`proche` est un état d'AFFICHAGE, pas un verdict.** Il ne doit apparaître
# nulle part dans `analyses_figees`, ni dans un texte de conclusion, ni dans une
# métadonnée. Le projet a trois états de verdict — conforme, dépassement,
# indéterminé — et il n'en aura pas un quatrième. Ce qui se joue ici est la
# couleur d'une barre, rien d'autre.
SEUIL_APPROCHE = 0.85


def _etat(quantifie, valeur, lq, seuil, seuil_2016, seuil_strict,
          plage, depasse, bascule, indetermine):
    """L'état d'un indicateur, du plus fort au plus rassurant."""
    if depasse:
        return "depassement"
    if plage and plage[0] is not None and valeur is not None:
        if valeur < plage[0] or valeur > plage[1]:
            return "hors_plage"
    if bascule:
        return "bascule"
    if indetermine:
        return "indetermine"
    if not quantifie:
        # Non quantifié : conforme SEULEMENT si la LQ est sous le seuil. Sinon
        # on ne sait pas, et c'est le piège le plus facile du projet.
        #
        # `cible > 0` : un seuil de zéro — la bactériologie, où l'absence est
        # exigée — ne peut pas être « percé par le bas ». La LQ d'un
        # dénombrement vaut 1, puisqu'on ne compte pas une demi-bactérie ;
        # sans cette garde, toute la bactériologie serait déclarée indéterminée
        # (chantier C4).
        cible = seuil if seuil is not None else seuil_strict
        if cible is not None and cible > 0 and lq is not None and lq > cible:
            return "indetermine"
        return "sous_lq"
    # Quantifié, sous la limite : conforme — mais la zone d'approche se dit.
    # `seuil > 0` pour la même raison qu'au-dessus : sur une exigence d'absence,
    # il n'y a pas de « 85 % du seuil » à approcher.
    if (seuil is not None and seuil > 0 and valeur is not None
            and valeur / seuil >= SEUIL_APPROCHE):
        return "proche"
    return "conforme"


def _texte_valeur(quantifie, valeur, lq, unite):
    """
    Trois écritures pour trois faits, et jamais un tiret.

    Le tiret confondait deux situations opposées : « recherché, rien trouvé »
    et « on ne sait pas ce que le laboratoire a fait ». Demande de Yannick du
    12 août 2026, sur un cas réel — une fiche où peu de substances ressortaient
    donnait l'impression qu'on n'avait pas cherché, alors que chercher et ne
    rien trouver est une bonne nouvelle qui mérite d'être lue comme telle.

    Ce qui n'est PAS écrit ici, et ne le sera jamais : « 0 ». Un laboratoire qui
    ne trouve rien ne mesure pas zéro, il mesure « en dessous de mon seuil ».
    Écrire 0 dirait « il n'y en a pas » là où la donnée dit « il n'y en a pas
    au-dessus de 0,01 µg/L » (CLAUDE.md §2.4).
    """
    u = f" {unite}" if unite else ""
    if quantifie and valeur is not None:
        return f"{_nb(valeur)}{u}"
    if lq is not None:
        return f"< {_nb(lq)}{u}"
    # Cherché, non quantifié, et le laboratoire n'a pas communiqué son seuil.
    # Un troisième cas réel, qui se dit au lieu de se taire.
    return "recherché, seuil de détection non communiqué"


def _mention_lq(lq, seuil, rapport, unite):
    """
    La mention du chantier C4, telle que Yannick l'a demandée : la LQ, le seuil,
    et le rapport entre les deux. « 0,5 » ne se lit pas ; « 5 × la limite de
    0,1 » se lit.

    Elle ne met en cause personne. Une LQ élevée est une capacité d'instrument,
    pas une négligence : on examine ce que le dispositif permet de savoir, on
    n'accuse pas le laboratoire (CLAUDE.md §2.1).
    """
    u = f" {unite}" if unite else ""
    facteur = ""
    if rapport:
        arrondi = round(rapport, 1) if rapport < 10 else round(rapport)
        facteur = f", soit {_nb(arrondi, 1)} × la limite de {_nb(seuil)}{u}"
    return (f"LQ {_nb(lq)}{u}{facteur}. Sous cette valeur, l'analyse ne voit "
            "rien : on ne peut pas dire que le seuil est respecté, seulement "
            "qu'on ne sait pas.")


def calculer(con, a, version):
    """
    `a` : une ligne de `analyses_figees` en dictionnaire.
    Renvoie {groupe: [indicateur, ...]}.
    """
    mesures = _mesures(con, a["code_prelevement"], version)
    resultat = {g: [] for g, _, _ in GROUPES}

    for d in definitions():
        ind = {"cle": d["cle"], "libelle": d["libelle"], "lecture": d["lecture"],
               "unite": d["unite"] or None}

        # ---- indicateur tiré de l'agrégat du bulletin --------------------
        if d["source"] == "analyse":
            v = a.get(d["reference"])
            ind.update(valeur=v, quantifie=v is not None,
                       texte=("—" if v is None else
                              f"{_nb(round(v, 2) if isinstance(v, float) else v)}"
                              + (f" {d['unite']}" if d["unite"] else "")),
                       etat="neutre", seuil=None, plage=None, part=None)
            resultat[d["groupe"]].append(ind)
            continue

        # ---- indicateur tiré d'une mesure --------------------------------
        m = next((mesures[c] for c in d["candidats"] if c in mesures), None)
        if m is None:
            # Non recherché. Une absence de recherche n'est pas un résultat, et
            # la taire donnerait à croire que le paramètre est bon.
            ind.update(valeur=None, quantifie=False, texte="non recherché",
                       etat="absent", seuil=None, plage=None, part=None,
                       detail="ce paramètre ne figure pas dans ce bulletin")
            resultat[d["groupe"]].append(ind)
            continue

        (lib, valeur, lq, quantifie, unite, limite_brute, reference_brute,
         seuil, s2016, sstrict, depasse, bascule, ind_s, ind_c, fiab,
         lq_aveugle, lq_rapport) = m

        # La plage vient de la référence déclarée par la source : c'est le seul
        # endroit où un encadrement bas ET haut existe (pH, conductivité).
        plage = parse_plage(reference_brute)
        plage = (plage[0], plage[1]) if plage[0] is not None else None
        if seuil is None:
            seuil = parse_limite(limite_brute)[0] or parse_limite(reference_brute)[0]

        etat = _etat(quantifie, valeur, lq, seuil, s2016, sstrict, plage,
                     depasse, bascule, ind_s or ind_c)

        detail = []
        if seuil is not None:
            detail.append(f"limite {_nb(seuil)} {unite or ind['unite'] or ''}".strip())
        if plage:
            detail.append(f"référence {_nb(plage[0])} à {_nb(plage[1])} "
                          f"{unite or ind['unite'] or ''}".strip())
        if sstrict is not None and (seuil is None or sstrict < seuil):
            detail.append(f"repère le plus strict {_nb(sstrict)}")
        if s2016 is not None and seuil is not None and s2016 != seuil:
            detail.append(f"en 2016 : {_nb(s2016)}")

        # La barre : où se situe la mesure par rapport à son seuil. C'est ce
        # qui rend un nombre lisible d'un coup d'œil — 0,493 ne dit rien,
        # « 99 % de la limite » dit tout.
        part = None
        if quantifie and valeur is not None:
            if plage:
                etendue = plage[1] - plage[0]
                part = (valeur - plage[0]) / etendue if etendue else None
            elif seuil:
                part = valeur / seuil

        ind.update(valeur=valeur, lq=lq, quantifie=bool(quantifie),
                   unite=unite or ind["unite"],
                   texte=_texte_valeur(quantifie, valeur, lq, unite or ind["unite"]),
                   seuil=seuil, seuil_2016=s2016, seuil_strict=sstrict,
                   plage=list(plage) if plage else None,
                   etat=etat, part=part, detail=" · ".join(detail),
                   a_verifier=bool(fiab and fiab != "verifie"),
                   # Le plafond analytique de CETTE tuile : sous la LQ, elle ne
                   # dit rien. Une tuile verte au-dessus d'une analyse aveugle
                   # serait le pire mensonge de la fiche (chantier C4).
                   lq_aveugle=bool(lq_aveugle),
                   lq_mention=(_mention_lq(lq, seuil, lq_rapport,
                                           unite or ind["unite"])
                               if lq_aveugle else None))
        resultat[d["groupe"]].append(ind)

    return resultat


PFAS_CHAINES = os.path.join(RACINE, "referentiel", "pfas_chaines.csv")


def _chaines():
    """Le fichier versionné des longueurs de chaîne, indexé par CAS ET par
    libellé normalisé — les laboratoires n'écrivent pas tous le CAS."""
    if not os.path.exists(PFAS_CHAINES):
        return {}, {}
    with open(PFAS_CHAINES, encoding="utf-8-sig") as fh:
        lignes = [l for l in fh if l.strip() and not l.lstrip().startswith("#")]
    par_cas, par_libelle = {}, {}
    for d in csv.DictReader(lignes, delimiter=";"):
        d["carbones"] = int(d["carbones"])
        if d["code_cas"]:
            par_cas[d["code_cas"].strip()] = d
        par_libelle[norm(d["libelle_norm"])] = d
    return par_cas, par_libelle


def pfas_par_chaine(con, a, version):
    """
    Les PFAS individuels du bulletin, répartis par longueur de chaîne.

    Ce que cette répartition met en évidence — et c'est tout son objet ici —
    c'est que la « somme de 4 » mise en avant par la réglementation européenne
    (PFOA, PFNA, PFHxS, PFOS) ne contient QUE des chaînes longues, c'est-à-dire
    celles dont l'usage est en cours d'interdiction. Les chaînes courtes qui
    les remplacent sont mesurées et n'entrent dans aucun total opposable autre
    que la somme de 20. La norme regarde ce qui disparaît.

    Ce bloc ne dit rien d'un traitement, d'un procédé ou d'un équipement, et
    ne doit jamais servir à en suggérer un (CLAUDE.md §2.2).
    """
    par_cas, par_libelle = _chaines()
    if not par_cas:
        return None

    rows = con.execute("""
        SELECT libelle_parametre, code_cas, resultat_num, lq, est_quantifie, unite,
               code_parametre
        FROM mesures WHERE code_prelevement = ?
    """, [a["code_prelevement"]]).fetchall()

    groupes = {"longue": [], "courte": []}
    vus = set()
    agregats = []
    for lib, cas, val, lq, quant, unite, code in rows:
        # Les paramètres de SOMME sont relevés à part : ce sont eux qui
        # produisaient une valeur affichée sans aucune substance derrière.
        n = norm(lib)
        if "perfluor" in n and ("somme" in n or "total" in n):
            agregats.append({
                "libelle": lib, "code": code, "quantifie": bool(quant),
                "texte": _texte_valeur(quant, val, lq, unite),
            })
            continue
        d = par_cas.get((cas or "").strip()) or par_libelle.get(norm(lib))
        if not d:
            continue
        vus.add(d["sigle"])
        groupes[d["chaine"]].append({
            "sigle": d["sigle"], "libelle": lib, "carbones": d["carbones"],
            "type": d["type"], "quantifie": bool(quant),
            "valeur": val, "lq": lq, "unite": unite,
            "texte": _texte_valeur(quant, val, lq, unite),
        })

    # CE BLOC NE DISPARAÎT PLUS JAMAIS. Demande de Yannick du 12 août 2026 :
    # un bloc absent se lit comme une absence de problème, alors qu'il signale
    # au contraire qu'on n'a rien cherché — le signal le plus fort de la page.
    # Les PFAS sont l'exemple type : leur recherche est une obligation récente,
    # donc beaucoup de bulletins anciens n'en portent aucun.
    # Auparavant : `return None`, et la page n'affichait rien du tout.
    non_cherchees = sorted(
        {d["sigle"] for d in par_cas.values()} - vus,
        key=lambda s: (len(s), s))
    rien_de_cherche = not groupes["longue"] and not groupes["courte"]

    def resume(cle):
        g = sorted(groupes[cle], key=lambda x: (not x["quantifie"], -(x["valeur"] or 0)))
        quantifies = [x for x in g if x["quantifie"]]
        return {
            "substances": g,
            "cherchees": len(g),
            "quantifiees": len(quantifies),
            # Plancher, comme toute somme du projet : les non-quantifiés y
            # comptent pour zéro, ce qu'ils ne sont pas (§2.4).
            "somme": round(sum(x["valeur"] for x in quantifies), 6) if quantifies else None,
        }

    return {
        "longue": resume("longue"), "courte": resume("courte"),
        "somme4_ne_voit_que_longues": True,
        # Aucun PFAS individuel dans ce bulletin : le bloc s'affiche quand même
        # et le dit. « Non cherché » est une information, pas un vide.
        "rien_de_cherche": rien_de_cherche,
        "cherchees_total": len(vus),
        "attendues_total": len({d["sigle"] for d in par_cas.values()}),
        "non_cherchees": non_cherchees,
        # Les paramètres de SOMME trouvés dans le bulletin. Quand il y en a un
        # ET qu'aucune substance individuelle n'a été cherchée, la fiche
        # affichait un total sans rien derrière : le laboratoire a rendu
        # l'addition sans les termes. Le cas se dit maintenant explicitement.
        "agregats": agregats,
        "agregat_sans_detail": bool(agregats) and rien_de_cherche,
    }


def reperes_nourrissons(con, a, version):
    """
    Les paramètres pour lesquels il existe un repère propre aux nourrissons.

    **Ce ne sont pas des limites au robinet.** Ils viennent de la
    réglementation des eaux embouteillées autorisées à porter la mention
    « convient à l'alimentation des nourrissons » (arrêté du 14 mars 2007).
    Comparer une eau de robinet à ces valeurs est une information utile — un
    nourrisson boit son biberon avec l'eau qu'on a sous la main — mais ce n'est
    pas un test de conformité, et la fiche doit le dire à chaque fois.

    Le référentiel porte déjà ces valeurs en `seuil_strict`, avec leur origine
    dans `base_seuil_strict` : rien n'est inventé ici, on ne fait que les
    distinguer des autres repères stricts.
    """
    rows = con.execute("""
        SELECT v.libelle_parametre, v.resultat_num, v.lq, v.est_quantifie, v.unite,
               v.seuil_strict, v.seuil_applicable, r.base_seuil_strict
        FROM verdicts_figes v
        JOIN referentiel_seuils r ON r.libelle = v.libelle_parametre
                                  OR lower(strip_accents(r.libelle))
                                     = lower(strip_accents(v.libelle_parametre))
        WHERE v.code_prelevement = ? AND v.version_referentiel = ?
          AND v.seuil_strict IS NOT NULL
          AND lower(strip_accents(COALESCE(r.base_seuil_strict, ''))) LIKE '%nourrisson%'
        ORDER BY v.resultat_num / NULLIF(v.seuil_strict, 0) DESC NULLS LAST
    """, [a["code_prelevement"], version]).fetchall()

    out = []
    for lib, val, lq, quant, unite, strict, applicable, base in rows:
        part = (val / strict) if (quant and val is not None and strict) else None
        out.append({
            "libelle": lib, "texte": _texte_valeur(quant, val, lq, unite),
            "unite": unite,
            # Formatés ici : un « 0.05 » à la point-décimale au milieu d'une
            # fiche en français se lit comme une coquille.
            "repere": _nb(strict), "limite": _nb(applicable) if applicable is not None else None,
            "part": part, "origine": base,
            "au_dessus": bool(quant and val is not None and strict and val > strict),
            # Le cas qui compte : sous la limite du robinet, au-dessus du
            # repère nourrissons. L'eau est conforme et ne convient pourtant
            # pas à l'usage que beaucoup en font.
            "conforme_mais_au_dessus": bool(
                quant and val is not None and strict and applicable
                and val <= applicable and val > strict),
        })
    return out


def hors_references(con, a, version):
    """
    Les paramètres SANS limite de qualité qui sortent de leur référence déclarée.

    Décision de Yannick, 9 août 2026 : « on note les références de qualité ; si
    pas de limite, alors on donne une information sur cette valeur ».

    Le périmètre est donc exactement celui-là — `seuil_2026_effectif IS NULL` :
    aucune limite au référentiel, aucune limite déclarée avec la mesure. Là où
    une limite existe, c'est elle qui parle et le dépassement s'affiche
    normalement ; le bloc ne redit pas ce que la fiche dit déjà ailleurs.

    Ce que ce bloc n'est pas
    ------------------------
    **Ce ne sont pas des non-conformités**, et la fiche doit le dire à chaque
    fois. L'administration sépare elle-même ses conclusions en trois axes
    (`conf_limites_bact`, `conf_limites_pc`, `conf_references_pc`) : une
    référence de qualité est organoleptique, structurelle ou de bon
    fonctionnement. La franchir n'engage pas la potabilité. Peindre l'une pour
    l'autre serait le faux positif que le §2.13 dit coûter le plus cher au
    projet.

    Les deux sens ne disent pas la même chose
    -----------------------------------------
    Le modèle ne connaissait que le dépassement par le haut. Or sur le corpus à
    deux départements, **539 mesures sortent de leur plage par le BAS contre 202
    par le haut**. Une eau peu minéralisée ou acide n'est pas une eau chargée :
    c'est une eau **agressive**, qui attaque les canalisations qu'elle traverse
    et emporte ce qu'elle en dissout. Le prélèvement étant fait à un point du
    réseau, ce qu'elle arrache entre ce point et le robinet n'est dans aucun
    bulletin — c'est le seul indice, dans les données, d'une contamination que
    les données ne contiennent pas.

    C'est un fait de physico-chimie, pas un conseil : le §2.2 interdit d'en
    tirer une orientation vers un produit ou un équipement, et le §2.1 de le
    reprocher à quiconque.
    """
    rows = con.execute("""
        SELECT libelle_parametre, resultat_num, lq, est_quantifie, unite,
               reference_min, reference_max, sens_hors_reference
        FROM verdicts_figes
        WHERE code_prelevement = ? AND version_referentiel = ?
          AND hors_reference
          AND seuil_2026_effectif IS NULL
        ORDER BY sens_hors_reference, libelle_parametre
    """, [a["code_prelevement"], version]).fetchall()

    out = []
    for lib, val, lq, quant, unite, mini, maxi, sens in rows:
        # La borne franchie, et elle seule : afficher « entre 6,5 et 9 » quand
        # c'est la borne basse qui est en cause noie l'information utile.
        borne = mini if sens == "en_dessous" else maxi
        out.append({
            "libelle": lib,
            "texte": _texte_valeur(quant, val, lq, unite),
            "unite": unite or "",
            "sens": sens,
            "borne": _nb(borne) if borne is not None else None,
            "plage": (_nb(mini) + " à " + _nb(maxi)
                      if mini is not None and maxi is not None else None),
        })
    return {
        "liste": out,
        "nb_au_dessus": sum(1 for x in out if x["sens"] == "au_dessus"),
        "nb_en_dessous": sum(1 for x in out if x["sens"] == "en_dessous"),
    } if out else None


def statut_hormonal(reg, sci):
    """
    Le registre d'une substance quantifiée : ('avere'|'suspecte'|'non_documente',
    mention) — ou (None, None) quand le statut est instruit et négatif.

    **Une seule copie de cette règle dans tout le dépôt.** Elle sert à la fiche
    de commune (`perturbateurs`) et au tableau de département
    (`compter_hormonal`). Deux copies d'une règle divergent à la première
    retouche, et celle-ci décide de ce qui est montré au lecteur comme
    « avéré » : la divergence y serait un faux positif ou un faux négatif selon
    la page consultée, pour la même eau.
    """
    r, s = (reg or "").strip().lower(), (sci or "").strip().lower()
    if r.startswith("pe avere"):
        return "avere", reg
    if s.startswith("pe avere") or s.startswith("suspecte"):
        return "suspecte", sci
    if s.startswith("a_documenter") or not s:
        return "non_documente", None
    if s == "non":
        return None, None                  # statut instruit, et négatif
    # Mention circonstanciée — atrazine, atrazine déséthyl. Elle nuance plus
    # qu'elle n'affirme : elle est citée telle quelle.
    return "suspecte", sci


def compter_hormonal(con, version, codes=None):
    """
    Par bulletin, le compte de substances quantifiées dans chacun des trois
    registres : {code_prelevement: {'avere': n, 'suspecte': n,
    'non_documente': n}}.

    Une seule requête pour tout le corpus — la page de département en affiche
    plusieurs centaines de lignes, et une requête par commune sur une table de
    plusieurs millions de lignes serait payée à chaque construction du site.

    Les trois comptes ne sont **jamais additionnés ici** (§2.6, §2.15) : ce sont
    trois registres distincts, et le total « perturbateurs endocriniens
    trouvés » n'existe pas comme fait. La somme sert de clé de tri, pas
    d'énoncé — cette décision-là appartient à l'affichage, pas au calcul.
    """
    sql = """
        SELECT code_prelevement, pe_reglementaire, pe_scientifique
        FROM verdicts_figes
        WHERE version_referentiel = ? AND est_quantifie
          -- Mêmes exclusions que `perturbateurs`, pour les mêmes raisons : une
          -- somme n'est pas une substance, et une ligne appariée à aucune
          -- entrée du référentiel n'a aucun statut à afficher, pas même
          -- « non documenté ».
          AND NOT COALESCE(est_agregat, FALSE)
          AND famille IS NOT NULL
    """
    p = [version]
    if codes:
        sql += f" AND code_prelevement IN ({','.join('?' * len(codes))})"
        p += list(codes)

    out = {}
    for cp, reg, sci in con.execute(sql, p).fetchall():
        cle, _ = statut_hormonal(reg, sci)
        if cle is None:
            continue
        d = out.setdefault(cp, {"avere": 0, "suspecte": 0, "non_documente": 0})
        d[cle] += 1
    return out


# Familles qui n'ont pas leur place dans un registre de perturbateurs
# endocriniens — décision de Yannick du 17 août 2026, après relecture de la
# publication.
#
# LE CRITÈRE, en une phrase : le registre liste les substances dont la présence
# est une question posée à la ressource ou aux sous-produits du traitement. Pas
# la composition minérale de l'eau, pas une activité radiologique, pas un
# dénombrement bactérien.
#
# CE N'EST PAS UNE RÉGRESSION DU PORTAGE mais un effet de bord du chantier C11.
# La base du 13 août donnait 14 entrées sur Montech, toutes légitimes ; la
# version enrichie en donne 24, avec le calcium, les hydrogénocarbonates, le
# titre hydrotimétrique, le pH d'équilibre et l'activité bêta du potassium 40.
# Plus de paramètres appariés au référentiel, donc plus d'entrées — et
# personne n'avait décidé que celles-là devaient y figurer. Un titre
# hydrotimétrique n'est pas une molécule, et une activité en becquerels ne peut
# pas avoir de statut hormonal.
#
# Le précédent existe et il est daté : le §7.1 a écarté exactement ces
# paramètres de l'indice de danger, parce qu'il « était dominé par le
# potassium, les chlorures, les sulfates et le sodium ».
#
# `desinfection` — le chlore libre et le chlore total — est écarté À TITRE
# PROVISOIRE, et la nuance compte : Yannick veut instruire les suspicions
# portant sur cette substance avant de trancher. Ce n'est donc pas « le chlore
# n'a pas sa place ici », c'est « on ne l'affiche pas tant que la question
# n'est pas instruite ». À rouvrir. Rien à voir avec `sous-produit
# desinfection` — les acides haloacétiques — qui sont de vrais sous-produits
# et restent.
FAMILLES_HORS_REGISTRE = {
    "mineral",          # calcium, hydrogénocarbonates, titres, pH d'équilibre
    "radiologique",     # activités alpha et bêta : pas des substances
    "microbiologique",  # dénombrements bactériens
    "desinfection",     # chlore libre et total — PROVISOIRE, cf. ci-dessus
}


def perturbateurs(con, a, version):
    """
    Les perturbateurs endocriniens quantifiés, dans TROIS registres distincts.

    CLAUDE.md §2.6 : le statut réglementaire et le statut scientifique ne se
    fusionnent jamais. Un perturbateur reconnu par la littérature n'est pas
    nécessairement reconnu par le droit, et **dans l'eau destinée à la
    consommation humaine le seul PE avéré au sens réglementaire européen est le
    bisphénol A**. Écrire qu'un pesticide « est un perturbateur endocrinien »
    sans préciser le registre est une faute vérifiable.

    Le troisième registre est le plus important, et il n'existe nulle part
    ailleurs : `a_documenter`. Quarante-cinq lignes du référentiel n'ont pas de
    statut renseigné. Ce n'est pas « non » — c'est « la question n'a pas été
    instruite ici ». Les ranger avec les non-PE serait un faux négatif, les
    ranger avec les suspects un faux positif. On les montre à part, comme on
    montre les indéterminés.
    """
    rows = con.execute("""
        SELECT libelle_parametre, resultat_num, lq, est_quantifie, unite,
               seuil_applicable, famille, pe_reglementaire, pe_scientifique
        FROM verdicts_figes
        WHERE code_prelevement = ? AND version_referentiel = ? AND est_quantifie
          -- Une somme n'est pas une substance : la lister ici la ferait
          -- compter en même temps que ses composants.
          AND NOT COALESCE(est_agregat, FALSE)
          -- Et une ligne qui n'est appariée à AUCUNE entrée du référentiel n'a
          -- pas de statut à afficher, même « non documenté » : on ne sait rien
          -- d'elle, pas même sa famille chimique. Les compter à part, plutôt
          -- que les ranger dans un registre auquel elles n'appartiennent pas.
          AND famille IS NOT NULL
        ORDER BY resultat_num DESC NULLS LAST
    """, [a["code_prelevement"], version]).fetchall()

    hors_referentiel = con.execute("""
        SELECT COUNT(*) FROM verdicts_figes
        WHERE code_prelevement = ? AND version_referentiel = ? AND est_quantifie
          AND NOT COALESCE(est_agregat, FALSE) AND famille IS NULL
    """, [a["code_prelevement"], version]).fetchone()[0]

    groupes = {"avere": [], "suspecte": [], "non_documente": [],
               "hors_referentiel": hors_referentiel}
    for lib, val, lq, quant, unite, seuil, famille, reg, sci in rows:
        cle, mention = statut_hormonal(reg, sci)
        if cle is None:
            continue
        # Le filtre ne porte QUE sur le registre « non documenté ». Une
        # substance réellement avérée ou suspectée resterait affichée quelle
        # que soit sa famille : on n'écarte pas un fait établi au motif d'un
        # rangement.
        if cle == "non_documente" and famille in FAMILLES_HORS_REGISTRE:
            continue
        groupes[cle].append({
            "libelle": lib, "texte": _texte_valeur(quant, val, lq, unite),
            "famille": famille, "seuil": _nb(seuil) if seuil is not None else None,
            "unite": unite,
            "mention": (mention[:240] if mention else None),
        })
    if not any(groupes[k] for k in ("avere", "suspecte", "non_documente")):
        return None
    return groupes


def plafond_analytique(con, a, version):
    """
    Ce que le laboratoire de CE bulletin ne pouvait pas voir — chantier C4,
    devenu la onzième obligation d'affichage du §8bis le 8 août 2026.

    Demande de Yannick, à propos de Pont-de-Larn : « le seuil du laboratoire ne
    permet pas du tout de quantifier ce qui est en dessous de cette limite […]
    si je compare avec une autre commune dont les limites du laboratoire sont
    beaucoup plus faibles, la comparaison des deux est biaisée. »

    Trois niveaux, du plus sûr au plus synthétique, et ils ne se remplacent pas.

    1. **La mention, au paramètre.** Vraie sans aucune convention : la LQ est
       au-dessus du seuil, donc l'analyse ne conclut pas.
    2. **Le taux, au bulletin.** `aveugles_pour_mille` — le seul chiffre
       comparable d'un bulletin à l'autre (§2.11), au même titre que
       `depassements_pour_mille`. Les comptes bruts ne se comparent pas : un
       bulletin qui cherche 700 paramètres a mécaniquement plus d'occasions
       d'être aveugle qu'un qui en cherche 200.
    3. **Le barème, et sa base.** Situer une LQ entre la plus fine et la plus
       grossière n'a de sens qu'À PARAMÈTRE CONSTANT : un laboratoire peut
       descendre à 4 ng/L sur les PFAS et rester à 0,5 µg/L sur l'hydrazide
       maléique. Une jauge unique par commune moyennerait deux instruments
       différents et produirait un score qui ne correspond à rien de mesurable
       — le profil synthétique que le §2.3 interdit, transposé à l'instrument.

    Trois réserves, qui sont le prix du niveau 3 :
      · **la référence bouge avec le corpus.** Le barème affiche donc sur
        combien de bulletins et de départements il est calculé, et il est figé
        avec sa version. C'est le §2.14 : le plus fin IDENTIFIÉ, jamais le plus
        fin qui existe ;
      · **un barème par paramètre ne tient pas sur une fiche** — 350 lignes. Il
        ne s'affiche que là où il mord, c'est-à-dire sur les paramètres du
        niveau 1 ;
      · **une LQ élevée n'est pas une négligence.** C'est une capacité
        d'instrument. On examine ce que le dispositif permet de savoir, on
        n'accuse pas le laboratoire — pas plus que l'exploitant (§2.1).

    L'échelle du barème est LOGARITHMIQUE : les LQ s'étalent sur des facteurs,
    pas sur des écarts. Entre 0,05 et 2,5 µg/L, une graduation linéaire
    collerait 0,5 contre la borne basse et laisserait croire à une finesse
    quasi optimale, alors qu'elle en est dix fois éloignée.
    """
    lignes = con.execute("""
        SELECT v.libelle_parametre, v.lq, v.seuil_applicable, v.unite,
               v.lq_rapport_seuil,
               c.lq_min, c.lq_max, c.lq_mediane, c.nb_bulletins, c.nb_departements
        FROM verdicts_figes v
        JOIN mesures m ON m.code_prelevement = v.code_prelevement
                      AND m.libelle_parametre = v.libelle_parametre
        LEFT JOIN lq_corpus c
               ON c.version_referentiel = v.version_referentiel
              AND c.cle_param = COALESCE(m.code_parametre, m.libelle_norm)
        WHERE v.code_prelevement = ? AND v.version_referentiel = ? AND v.lq_aveugle
        ORDER BY v.lq_rapport_seuil DESC NULLS LAST
    """, [a["code_prelevement"], version]).fetchall()
    if not lignes:
        return None

    out = []
    for (lib, lq, seuil, unite, rapport,
         cmin, cmax, cmed, nb_bull, nb_dept) in lignes:
        bareme = None
        if cmin is not None and cmax is not None and cmax > cmin > 0 and lq:
            etendue = math.log10(cmax) - math.log10(cmin)
            bareme = {
                "min": _nb(cmin), "max": _nb(cmax),
                "mediane": _nb(cmed) if cmed is not None else None,
                "ici": _nb(lq),
                "position": (math.log10(lq) - math.log10(cmin)) / etendue,
                # La base, jamais tue : « le plus fin » sur 29 bulletins n'est
                # pas « le plus fin » sur 4 000.
                "nb_bulletins": nb_bull, "nb_departements": nb_dept,
                "facteur_au_plus_fin": round(lq / cmin, 1) if cmin else None,
            }
        elif cmin is not None:
            # Une seule LQ observée dans tout le corpus : il n'y a pas de
            # barème, et le dire vaut mieux qu'afficher une jauge plate qui
            # laisserait croire à une position.
            bareme = {"min": _nb(cmin), "max": _nb(cmax), "ici": _nb(lq),
                      "position": None, "mediane": None,
                      "nb_bulletins": nb_bull, "nb_departements": nb_dept,
                      "facteur_au_plus_fin": None}
        out.append({
            "libelle": lib,
            "lq": _nb(lq), "seuil": _nb(seuil), "unite": unite or "",
            "rapport": (round(rapport, 1) if rapport and rapport < 10
                        else (round(rapport) if rapport else None)),
            "mention": _mention_lq(lq, seuil, rapport, unite),
            "bareme": bareme,
        })

    return {
        "lignes": out,
        "nb": a.get("nb_aveugles") or len(out),
        "pour_mille": a.get("aveugles_pour_mille"),
        "notees": a.get("nb_mesures_notees"),
    }


def decomposition_danger(con, a, version, maxi=None):
    """
    De quoi l'indice de danger est fait.

    Le nombre seul — « 6,99 » — ne se lit pas. Ce qui se lit, c'est : le
    chlorothalonil R471811 occupe 1,85 fois sa propre limite, l'atrazine
    déséthyl 1,10 fois la sienne, et ainsi de suite. L'indice est la somme de
    ces fractions (cf. docs/METHODE_EFFET_COCKTAIL.md, indicateur C).

    **Toutes les contributions, depuis le 16 août 2026.** Le plafond valait 6,
    et il était muet : l'indice affichait un total dont on ne voyait pas les
    termes, alors qu'il n'a de sens que décomposé. Mesuré au moment de le
    retirer : sur 28 557 bulletins portant une décomposition, **1 214 étaient
    tronqués**, jusqu'à 30 contributions. C'est le §2.8 — aucun chiffre sans ce
    qui le compose — appliqué à une somme dont le total était publié et les
    termes cachés.

    Le repli au-delà de six est affaire de gabarit, pas de requête : la liste
    part entière, et `fiche.js` la plie dans un `<details>` dont le résumé
    **annonce le compte exact**. Tronquer ici aurait rendu ce compte impossible
    à écrire.
    """
    rows = con.execute(f"""
        SELECT libelle_parametre, resultat_num, unite, seuil_applicable,
               resultat_num / NULLIF(seuil_applicable, 0) AS part
        FROM verdicts_figes
        WHERE code_prelevement = ? AND version_referentiel = ?
          AND est_quantifie AND NOT COALESCE(est_agregat, FALSE)
          AND famille IN ('pesticide','metabolite','PFAS','organique')
          AND seuil_applicable IS NOT NULL
        ORDER BY part DESC NULLS LAST
        {"LIMIT " + str(int(maxi)) if maxi else ""}
    """, [a["code_prelevement"], version]).fetchall()

    return [{"p": r[0], "v": _nb(r[1]), "u": r[2] or "", "s": _nb(r[3]),
             "part": round(r[4], 3) if r[4] is not None else None}
            for r in rows]


def bascules_en_tete(con, a, version, maxi=None):
    """
    Les mesures qui portent la thèse, pour le bandeau de tête : au-dessus de la
    limite de 2016, sous celle d'aujourd'hui. C'est le sujet du projet, il n'a
    pas à être cherché au milieu d'un tableau de 300 lignes.

    **Toutes les bascules, depuis le 10 août 2026.** Le plafond valait 3, et il
    était muet : le bandeau annonçait « 6 mesures ont changé de statut » et en
    montrait trois, sans que rien ne signale les autres. Un compteur et une
    liste qui se contredisent sur le même écran est précisément ce que le §2.8
    interdit — un chiffre sans ce qui le compose. Sur le corpus au 10 août 2026,
    4 bulletins étaient tronqués et le maximum tenait en 6 cartes.
    """
    return con.execute(f"""
        SELECT libelle_parametre, resultat_num, unite, seuil_2016,
               seuil_applicable, bascule_datee
        FROM verdicts_figes
        WHERE code_prelevement = ? AND version_referentiel = ? AND bascule_2016_2026
        ORDER BY resultat_num / NULLIF(seuil_2016, 0) DESC
        {"LIMIT " + str(int(maxi)) if maxi else ""}
    """, [a["code_prelevement"], version]).fetchall()


def depassements_en_tete(con, a, version, maxi=None):
    """
    `seuil_2016` est renvoyé aussi : une mesure qui dépasse aujourd'hui a
    souvent dépassé bien plus largement l'ancienne limite, et la jauge le
    montre mieux qu'une phrase.

    **`nature_seuil` est renvoyée depuis le 9 août 2026**, et elle change ce que
    la ligne veut dire. Trois natures que l'administration sépare elle-même dans
    ses conclusions, et que le bandeau confondait :

      limite     limite de qualité, fondée sur la santé — une non-conformité ;
      reference  référence de qualité — organoleptique, structurelle ou de bon
                 fonctionnement. Pas une non-conformité sanitaire ;
      vigilance  valeur indicative sans portée opposable, typiquement un
                 métabolite reclassé « non pertinent ».

    Sur le Tarn entier, 79 des 172 mesures en dépassement portaient sur une
    valeur de vigilance et 8 sur une référence : les annoncer toutes comme des
    dépassements produisait un faux positif sur la moitié du compte. Cinq
    bulletins de Paulinet affichaient un dépassement d'ESA métolachlore là où
    l'ARS conclut à la conformité pleine.

    Le tri met les limites d'abord : à écart égal, une limite sanitaire compte
    plus qu'une valeur indicative.

    **Tous les dépassements, depuis le 10 août 2026.** Le plafond valait 3, et
    il était muet : un bulletin annonçant « 7 paramètres dépassaient la limite »
    en affichait trois, sans un mot sur les quatre autres. Le lecteur ne pouvait
    ni les voir ni savoir qu'ils existaient — et le tri par nature aggravait la
    chose, puisque les cartes retenues étaient les plus graves : ce qui
    disparaissait était systématiquement le bas de la liste.

    Défaut signalé par Yannick le 10 août 2026 sur une fiche réelle. Mesuré au
    même moment sur le corpus : **54 bulletins tronqués sur 592** en comportant
    au moins un, pour un maximum de **10 dépassements** — donc aucun besoin de
    pagination, seulement de cesser de couper.
    """
    return con.execute(f"""
        SELECT libelle_parametre, resultat_num, unite, seuil_applicable,
               grille_applicable, seuil_2016, nature_seuil
        FROM verdicts_figes
        WHERE code_prelevement = ? AND version_referentiel = ? AND depasse_applicable
        ORDER BY CASE nature_seuil WHEN 'limite' THEN 0 WHEN 'reference' THEN 1
                                   WHEN 'vigilance' THEN 2 ELSE 3 END,
                 resultat_num / NULLIF(seuil_applicable, 0) DESC
        {"LIMIT " + str(int(maxi)) if maxi else ""}
    """, [a["code_prelevement"], version]).fetchall()


def natures_du_bulletin(con, a, version):
    """
    Le compte des dépassements, décomposé par nature du seuil franchi.

    `nb_depasse_applicable` ne bouge pas — il reste le compteur canonique, et
    aucune sortie ne le recalcule. Ces trois nombres le DÉCOMPOSENT, pour que le
    bandeau puisse dire « 12 dépassements, dont 2 d'une limite sanitaire »
    plutôt que « 12 dépassements » tout court.

    Les compteurs sont lus dans `analyses_figees`, qui les porte déjà
    (`nb_depasse_limite`, `nb_au_dessus_vigilance`) : on ne recompte pas à
    l'affichage ce qui a été figé (§8bis — ne jamais recalculer un verdict à la
    volée dans l'interface).
    """
    total = a["nb_depasse_applicable"] or 0
    limite = a["nb_depasse_limite"] or 0
    vigilance = a["nb_au_dessus_vigilance"] or 0
    # Le reste est nécessairement de nature « référence » ou sans statut : on le
    # déduit plutôt que de le recompter, pour que la somme se referme toujours.
    return {
        "total": total,
        "limite": limite,
        "vigilance": vigilance,
        "reference": max(0, total - limite - vigilance),
    }


# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Indicateurs d'un bulletin")
    p.add_argument("insees", nargs="+")
    args = p.parse_args()

    con = duckdb.connect(DB_PATH, read_only=True)
    version = con.execute("SELECT version_referentiel FROM analyses_figees "
                          "GROUP BY 1 ORDER BY MAX(calcule_le) DESC LIMIT 1").fetchone()[0]
    marques = ",".join("?" * len(args.insees))
    rows = con.execute(f"""SELECT * FROM analyses_figees
                           WHERE version_referentiel = ? AND code_insee IN ({marques})
                           ORDER BY commune, date_prelevement DESC""",
                       [version, *args.insees]).fetchall()
    cols = [d[0] for d in con.description]
    for r in rows:
        a = dict(zip(cols, r))
        print("=" * 78)
        print(f"{a['commune']} — {a['date_prelevement']}")
        print("=" * 78)
        groupes = calculer(con, a, version)
        for cle, titre, _ in GROUPES:
            print(f"\n--- {titre} ---")
            for i in groupes[cle]:
                print(f"  {i['libelle'][:38]:<38} {i['texte'][:20]:<20} "
                      f"{i['etat']:<12} {i.get('detail', '')}")
        for lib, val, u, s16, sapp, datee in bascules_en_tete(con, a, version):
            print(f"\n  BASCULE  {lib} {_nb(val)} {u} — 2016 : {_nb(s16)}, "
                  f"aujourd'hui : {_nb(sapp)}" + ("  (datée)" if datee else ""))

        plafond = plafond_analytique(con, a, version)
        if plafond:
            print(f"\n--- Ce que le laboratoire ne pouvait pas voir "
                  f"({plafond['nb']} paramètre(s), {_nb(plafond['pour_mille'])} "
                  f"pour mille notés) ---")
            for l in plafond["lignes"]:
                print(f"  {l['libelle'][:38]:<38} LQ {l['lq']} {l['unite']} "
                      f"pour un seuil de {l['seuil']} — {_nb(l['rapport'], 1)} ×")
                b = l["bareme"]
                if b and b["position"] is not None:
                    print(f"      corpus : {b['min']} à {b['max']} "
                          f"({b['nb_bulletins']} bulletins, "
                          f"{b['nb_departements']} dép.) — "
                          f"{_nb(b['facteur_au_plus_fin'], 1)} × le plus fin relevé")
    con.close()


if __name__ == "__main__":
    main()

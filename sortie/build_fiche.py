# -*- coding: utf-8 -*-
"""
Générateur de la fiche citoyenne, dérivé de la base.

    python3 sortie/build_fiche.py                  # toutes les communes figées
    python3 sortie/build_fiche.py 28068 17415      # une sélection
    python3 sortie/build_fiche.py --sortie ma_fiche.html

Ce que ce fichier produit et ce qu'il ne produit pas
----------------------------------------------------
La fiche mêle deux natures de contenu, et elles ne se mélangent jamais ici :

  - le FACTUEL — mesures, seuils, verdicts, couverture, effort de recherche.
    Entièrement dérivé de `analyses_figees`, `verdicts_figes` et `mesures`.
    Reproductible, traçable, et estampillé de la version de référentiel qui a
    servi au calcul.

  - la PROSE — sous-titre territorial, lecture citoyenne, sections d'analyse,
    verdict rédigé. Elle est de la main de Yannick et vit dans
    `sortie/redactions.json`, clé = code INSEE. **Ce script n'en écrit
    jamais.** Une commune sans rédaction produit une fiche factuelle complète,
    qui l'indique explicitement plutôt que de combler le vide.

Avant, tout était écrit en dur dans ce fichier, y compris les chiffres : la
fiche était la seule partie du dépôt qui n'était pas traçable. Elle l'est.

Garde-fous applicables (CLAUDE.md §2) :
  - aucune recommandation de filtration, d'équipement ou de produit ;
  - interroger la norme, pas les acteurs qui l'appliquent ;
  - un « non quantifié » n'est pas une absence : affiché « < LQ », jamais 0 ;
  - une valeur en fiabilite 'a_verifier' est signalée comme telle ;
  - aucune comparaison entre communes sans l'effort de recherche (§2.11).
"""
import argparse
import html as _html
import json
import os
import re
import sys

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICI = os.path.join(RACINE, "sortie")
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, ICI)

from common import DB_PATH  # noqa: E402
import indicateurs as IND  # noqa: E402
import rediger  # noqa: E402
import suivi_panel as SP  # noqa: E402

def version_a_publier(con):
    """
    La version de référentiel à publier : celle que les fichiers du référentiel
    produisent AUJOURD'HUI, si elle est figée.

    Défaut réel, trouvé le 8 août 2026 : la sortie prenait « la version dont la
    date de calcul est la plus récente ». Deux versions figées le même jour ne
    sont pas départagées par une date, et le site a publié l'ancienne grille
    sans que rien ne le signale — l'outil se mettait à faire ce qu'il dénonce,
    afficher un verdict sans dire contre quoi il a été calculé.

    On interroge donc l'empreinte du contenu du référentiel, qui est sans
    ambiguïté. Si elle n'est pas encore figée, on le dit très fort plutôt que
    de publier une grille périmée en silence.
    """
    import figer

    attendue = figer.version_referentiel()
    presentes = {r[0]: r[1] for r in con.execute(
        "SELECT version_referentiel, MAX(calcule_le) FROM analyses_figees "
        "GROUP BY 1 ORDER BY 2 DESC").fetchall()}
    if not presentes:
        return None, None
    if attendue in presentes:
        return attendue, str(presentes[attendue])
    repli = next(iter(presentes))
    print(f"  ! le référentiel actuel ({attendue}) n'est PAS figé.")
    print(f"    publication de la version {repli}, qui ne correspond plus aux")
    print("    fichiers du référentiel. Lance src/figer.py avant de publier.")
    return repli, str(presentes[repli])


REDACTIONS = os.path.join(ICI, "redactions.json")
PROPOSEES = os.path.join(ICI, "redactions_proposees.json")
GABARITS = os.path.join(RACINE, "site", "gabarits")

# Champs de prose, et l'ordre de préséance de leurs origines.
CHAMPS_PROSE = ("sous_titre", "delta", "lecture_administrative",
                "lecture_citoyenne", "analyse", "verdict")
PRESEANCE = ("auteur", "propose", "derive")

LIBELLE_ORIGINE = {
    "auteur": None,          # la main de Yannick : rien à signaler
    "propose": "proposition de rédaction, à relire",
    "derive": "dérivé de la base",
}


def charger_prose():
    """
    Les deux fichiers de prose écrite. Le troisième niveau — la prose dérivée —
    n'est pas un fichier : il est calculé au moment de la construction, pour
    qu'un texte ne puisse pas rester vrai pendant que le chiffre d'à côté
    change.
    """
    lire = lambda p: json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}  # noqa: E731
    return lire(REDACTIONS), lire(PROPOSEES)


def pour_bulletin(prose, insee, date_iso, code_prelevement=None):
    """
    La prose qui accompagne un bulletin, de la clé la plus précise à la plus
    générale.

        "28068@2026-03-10"        cette commune, ce prélèvement
        "28068"                   cette commune, tous ses prélèvements
        "PREL:08100134523"        CE POINT D'EAU, ce prélèvement — partagé par
                                  toutes les communes qu'il alimente

    La clé `PREL:` est la réponse à un fait de terrain : un même prélèvement
    alimente jusqu'à huit communes. Écrire huit fois le même texte serait
    absurde, et les huit versions divergeraient à la première correction. Un
    texte par point d'eau, et les communes desservies en héritent.

    Elle est indexée sur le `code_prelevement` et non sur
    `code_installation_amont`, qui est vide sur un tiers des bulletins — et
    parce qu'un texte citant « 1,662 µg/L » décrit un prélèvement daté, pas une
    installation en général.

    Défaut réel corrigé au passage : la prose n'était indexée que par commune.
    Challet a deux bulletins complets, 2022 et 2026 ; l'analyse écrite pour
    celui de 2026 s'affichait aussi sous les chiffres de 2022, où la valeur
    citée n'existe pas.
    """
    if not prose:
        return None
    for cle in (f"{insee}@{date_iso}", insee,
                f"PREL:{code_prelevement}" if code_prelevement else None):
        if cle and cle in prose:
            return prose[cle]
    return None


def fusionner(auteur, propose, derive):
    """
    Assemble la prose d'une commune, champ par champ, et dit d'où vient chacun.

    Préséance : ce que Yannick a écrit prime toujours ; à défaut une
    proposition du modèle ; à défaut le texte dérivé de la base. Le mélange se
    fait au CHAMP et non à la commune : on peut avoir un verdict de sa main et
    un inventaire dérivé, et les deux doivent rester distinguables.

    Renvoie (prose, origines) — `origines` associe chaque champ à son origine,
    pour que la fiche puisse l'afficher. Une prose dont on ne sait pas d'où
    elle vient n'a pas sa place dans un outil dont toute la valeur est la
    traçabilité (CLAUDE.md §2.7, transposé du chiffre au texte).
    """
    prose, origines = {}, {}
    sources = {"auteur": auteur or {}, "propose": propose or {}, "derive": derive or {}}

    for champ in CHAMPS_PROSE:
        if champ == "analyse":
            continue
        for origine in PRESEANCE:
            valeur = sources[origine].get(champ)
            if valeur:                       # ni None, ni "", ni []
                prose[champ], origines[champ] = valeur, origine
                break

    # `analyse` ne s'écrase pas, elle s'assemble — sauf quand Yannick l'a
    # écrite : sa fiche est complète et se suffit, y ajouter des paragraphes
    # dérivés reviendrait à dupliquer ce qu'il a déjà dit à sa manière.
    # Sinon, les faits d'abord (dérivés de la base), le contexte ensuite
    # (proposé) : on ne cadre pas le lecteur avant de lui donner les chiffres.
    if auteur and auteur.get("analyse"):
        prose["analyse"] = [dict(s, o="auteur") for s in auteur["analyse"]]
        origines["analyse"] = "auteur"
    else:
        sections = ([dict(s, o="derive") for s in (sources["derive"].get("analyse") or [])]
                    + [dict(s, o="propose") for s in (sources["propose"].get("analyse") or [])])
        if sections:
            prose["analyse"] = sections
            origines["analyse"] = ("propose" if any(s["o"] == "propose" for s in sections)
                                   else "derive")
    return prose, origines

KPI_LABELS = [
    "Effort de recherche",
    "Couverture de l'analyse",
    "Dépassements à la date",
    "Bascules réglementaires",
    "Substances de synthèse quantifiées",
    "Indice de danger (méthode simplifiée)",
]


# ---------------------------------------------------------------------------
# Mise en forme
# ---------------------------------------------------------------------------
def fmt_val(resultat, lq, quantifie, unite):
    """Valeur affichée. « < LQ » quand la valeur n'est pas quantifiée : un
    non-quantifié n'est pas un zéro (CLAUDE.md §2.4)."""
    u = f" {unite}" if unite else ""
    if quantifie and resultat is not None:
        return f"{_nb(resultat)}{u}"
    if lq is not None:
        return f"<{_nb(lq)}{u}"
    return "non quantifié"


def fmt_seuil(seuil, unite):
    return f"≤ {_nb(seuil)} {unite}".strip() if seuil is not None else None


def _nb(x):
    """Nombre à la française, sans zéros inutiles."""
    if x is None:
        return ""
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return (s or "0").replace(".", ",")


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def _date_fr(d):
    """2026-03-10 -> « 10 mars 2026 ». La date d'un prélèvement est lue par un
    habitant, pas par une machine."""
    if d is None:
        return "—"
    try:
        a, m, j = str(d)[:10].split("-")
        return f"{int(j)}{'er' if j == '01' else ''} {MOIS[int(m) - 1]} {a}"
    except (ValueError, IndexError):
        return str(d)


# Codes de conformité SISE-Eaux tels que fournis par la source. Les traduire
# ici, une fois : un « C » brut affiché sur une fiche citoyenne n'est pas une
# information, et le laisser interpréter par le gabarit invite à deviner.
CONFORMITE = {
    "C": ("Conforme", "vert"),
    "N": ("Non conforme", "rouge"),
    "D": ("Dérogation", "ambre"),
    "S": ("Sans objet", "gris"),
}


def _conformite(code):
    if not code:
        return ("Non renseigné", "gris")
    return CONFORMITE.get(str(code).strip().upper()[:1],
                          (str(code), "gris"))


def _extrait(texte, n=90):
    """Coupe sur un mot, pas au milieu d'un mot. La conclusion de l'ARS est
    citée : la tronquer en « présence d'ESA M » la déforme."""
    t = " ".join((texte or "").split())
    if len(t) <= n:
        return t or "—"
    return t[:n].rsplit(" ", 1)[0] + "…"


def _resume_depassements(n):
    """
    Le résumé citoyen, en une ligne, qui nomme CE QUI a été franchi.

    Le compte seul est trompeur : sur cinq bulletins de Paulinet, « 5
    dépassements » désignait cinq mesures d'ESA métolachlore au-dessus d'une
    valeur de vigilance — un métabolite reclassé « non pertinent » — là où
    l'ARS conclut à la conformité pleine. Le lecteur lisait une alerte
    sanitaire là où l'administration ne voit rien à signaler.
    """
    if not n["total"]:
        return "Aucun dépassement à la date"
    bouts = []
    if n["limite"]:
        bouts.append(f"{n['limite']} {_accord(n['limite'], 'limite')} de qualité")
    if n["reference"]:
        bouts.append(f"{n['reference']} {_accord(n['reference'], 'référence')} "
                     "de qualité")
    if n["vigilance"]:
        bouts.append(f"{n['vigilance']} {_accord(n['vigilance'], 'valeur')} "
                     "de vigilance")
    if not n["limite"]:
        # Le cas qui demandait la correction : rien de sanitaire n'est franchi.
        return "Aucune limite de qualité dépassée — " + ", ".join(bouts)
    return " · ".join(bouts) + ", à la date du prélèvement"


def niveau(nb_depassements, nb_bascules, nb_indetermines, nb_depasse_limite=None):
    """
    Feu de la fiche. Un indéterminé n'est pas un conforme : il colore.

    **Le rouge est réservé à la limite de qualité**, depuis le 9 août 2026.
    `nb_depassements` mélange trois natures que l'administration sépare
    elle-même : une limite sanitaire, une référence de qualité, une valeur de
    vigilance sans portée opposable. Peindre en rouge un bulletin dont le seul
    écart porte sur un métabolite reclassé « non pertinent » dit à l'habitant
    l'inverse de ce que conclut l'ARS — cinq bulletins de Paulinet étaient dans
    ce cas. Ces écarts-là colorent en ambre : ils sont réels, ils se lisent,
    ils ne sont pas une non-conformité sanitaire.

    `nb_depasse_limite=None` conserve l'ancien comportement, pour un appelant
    qui n'aurait pas la décomposition sous la main.
    """
    if nb_depassements:
        if nb_depasse_limite is None or nb_depasse_limite:
            return "rouge"
        return "ambre"
    if nb_bascules or nb_indetermines:
        return "ambre"
    return "vert"


# ---------------------------------------------------------------------------
# La tête de fiche — rendue en Python, et non plus dans le navigateur
# ---------------------------------------------------------------------------
# Écrit le 16 août 2026, passe 1 du portage de la forme v2.
#
# POURQUOI CE BLOC EST ICI. La fiche était bâtie dans le navigateur par
# `fiche.js` : le fichier publié ne portait qu'une coquille vide. Les deux
# contrôles de forme le disaient chacun à sa manière, et personne ne les
# écoutait — `tests/comparer_charte.py` mesurait 21 % du vocabulaire de la
# maquette (il retire les `<script>` avant de compter, donc il ne voit que ce
# qui est réellement dans le fichier), et `outils/mesure_sans_js.py` relevait
# 2 817 caractères lisibles là où il en attend 6 000. Une page dont le contenu
# n'apparaît qu'une fois un moteur exécuté n'est pas le « dossier de fichiers
# statiques » que `site/build_site.py` revendique.
#
# LE TEXTE DU VERDICT EST COMPOSÉ ICI, pas dans le gabarit ni en JavaScript,
# et c'est la même raison que pour l'alerte de panel : ce qui est écrit en
# Python est relisible par `tests/test_sorties.py` — prescription, comparaison
# anonyme, affirmation d'absence. Ce qui est écrit en JavaScript ne l'est pas.
#
# Les formulations viennent des quatre maquettes, une par état, et non d'une
# rédaction nouvelle : Saintes donne le conforme, Montech la bascule, Thiville
# le dépassement, Tramayes l'indéterminé.

MOIS_COURT = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.",
              "août", "sept.", "oct.", "nov.", "déc."]


def h(s):
    """Échappement HTML. Un nom de réseau porte des apostrophes et des « & »,
    et il vient de la source, pas de nous."""
    return _html.escape("" if s is None else str(s), quote=True)


def _date_courte(d):
    """« 2026-01-14 » -> « 14 janv. 2026 ». Employé quand la série défile : à
    vingt-et-un prélèvements, la date pleine ne tient pas sur une ligne."""
    try:
        an, m, j = str(d)[:10].split("-")
        return f"{int(j)} {MOIS_COURT[int(m) - 1]} {an}"
    except (ValueError, IndexError):
        return str(d)


def _accord(n, singulier, pluriel=None):
    """L'accord se fait ici plutôt que par un « (s) » collé au mot : la fiche
    est lue par un habitant."""
    return singulier if abs(n) <= 1 else (pluriel or singulier + "s")


def _lecture_faite(a):
    """Le dénominateur, dans la phrase même du verdict (§2.8 et §8bis n° 1).

    Jamais un « conforme » sans ce qui a été noté et sur combien. C'est la
    seule partie de la phrase qui ne change pas d'un état à l'autre."""
    notes, lues = a["nb_mesures_notees"] or 0, a["nb_mesures_lues"] or 0
    pct = a["pct_couverture"]
    return (f" Lecture faite sur <b>{notes} paramètres notés parmi les "
            f"{lues} mesurés</b>"
            + (f", soit {_nb(pct)} % du bulletin." if pct is not None else "."))


def verdict_tete(a, natures):
    """Ce que dit ce bulletin — le bloc de droite de l'en-tête.

    Quatre états, quatre modificateurs, et l'ordre dans lequel ils sont testés
    est une règle de méthode, pas une commodité :

    1. **le rouge est réservé à la limite de qualité** (§2.1 et la leçon de
       Paulinet) — `nb_depasse_applicable` mélange trois natures que
       l'administration sépare elle-même ;
    2. un franchissement qui ne porte sur aucune limite sanitaire ne se peint
       donc pas en rouge. La charte n'a que quatre modificateurs et aucun
       « attention » : ce cas prend le gris de l'indéterminé, avec un titre qui
       dit explicitement qu'aucune limite de qualité n'est dépassée. **À
       confirmer par Yannick** — l'autre issue serait d'ajouter
       `.verdict-bloc--attention` à la charte, ce qui est une décision de
       forme et se prend dans `docs/CHARTE_GRAPHIQUE.md` d'abord ;
    3. la bascule ensuite : c'est la thèse du projet, et elle ne s'annonce que
       si rien n'est dépassé à la date ;
    4. l'indéterminé enfin — il colore, il n'est jamais un conforme (§2.4).
    """
    basc = a["nb_bascules"] or 0
    indet = a["nb_indetermines"] or 0
    lim, vig, ref = natures["limite"], natures["vigilance"], natures["reference"]

    if lim:
        autres = []
        if vig:
            autres.append(f"{vig} {_accord(vig, 'mesure')} au-dessus d'une "
                          f"{_accord(vig, 'valeur')} de vigilance")
        if ref:
            autres.append(f"{ref} {_accord(ref, 'mesure')} au-dessus d'une "
                          f"{_accord(ref, 'référence')} de qualité")
        suite = ""
        if autres:
            suite = (f" S'y {_accord(vig + ref, 'ajoute', 'ajoutent')} "
                     f"<b>{' et '.join(autres)}</b>, qui n'"
                     f"{_accord(vig + ref, 'est', 'sont')} pas une "
                     f"non-conformité sanitaire.")
        return {
            "mod": "depassement",
            "titre": (f"{lim} {_accord(lim, 'dépassement')} de limite de "
                      f"qualité, à la date du prélèvement"),
            "texte": ("Le verdict est rendu contre <b>la grille en vigueur le "
                      "jour du prélèvement</b> : un reclassement n'est pas "
                      "rétroactif." + suite + _lecture_faite(a)),
        }

    if vig or ref:
        quoi = []
        if vig:
            quoi.append(f"{vig} {_accord(vig, 'valeur')} de vigilance")
        if ref:
            quoi.append(f"{ref} {_accord(ref, 'référence')} de qualité")
        return {
            "mod": "indetermine",
            "titre": "Aucune limite de qualité dépassée",
            "texte": (f"Ce bulletin franchit <b>{' et '.join(quoi)}</b>. Ni "
                      "l'une ni l'autre n'est une limite sanitaire opposable : "
                      "l'écart est réel, il se lit, il n'est pas une "
                      "non-conformité." + _lecture_faite(a)),
        }

    if basc:
        return {
            "mod": "bascule",
            "titre": "Conforme aujourd'hui. Ne l'aurait pas été il y a dix ans.",
            "texte": (f"<b>{basc} {_accord(basc, 'mesure')} "
                      f"{_accord(basc, 'a', 'ont')} changé de statut sans que "
                      "l'eau change.</b> Ce n'est pas la ressource qui s'est "
                      "améliorée : c'est la limite qui a bougé. Aucun "
                      "dépassement à la date du prélèvement."
                      + _lecture_faite(a)),
        }

    if indet:
        return {
            "mod": "indetermine",
            "titre": (f"Aucun dépassement, et {indet} "
                      f"{_accord(indet, 'paramètre')} "
                      f"{_accord(indet, 'indéterminé')}"),
            "texte": ("Aucune bascule réglementaire non plus. Mais pour "
                      f"{indet} {_accord(indet, 'paramètre')}, <b>la limite de "
                      "quantification du laboratoire se situe au-dessus du "
                      "seuil de comparaison</b> : on ne peut pas affirmer que "
                      "le seuil est respecté. <b>Un indéterminé n'est pas un "
                      "conforme.</b>" + _lecture_faite(a)),
        }

    # Annoncer « aucun dépassement » alors qu'une part de l'analyse ne pouvait
    # pas conclure serait exactement la demi-vérité que le projet dénonce
    # (§8bis n° 11, chantier C4). Ce cas n'est dans aucune des quatre
    # maquettes ; il vient du bandeau qu'écrivait `fiche.js` et il ne se perd
    # pas au passage en Python.
    aveugles = a["nb_aveugles"] or 0
    if aveugles:
        return {
            "mod": "indetermine",
            "titre": (f"Aucun dépassement — et {aveugles} "
                      f"{_accord(aveugles, 'paramètre')} que l'analyse ne "
                      f"pouvait pas trancher"),
            "texte": ("Pour ceux-là, la limite de quantification du "
                      "laboratoire se situe au-dessus de <b>la limite "
                      "réglementaire elle-même</b> : sous cette valeur "
                      "l'analyse ne voit rien, là précisément où la conformité "
                      "se joue. <b>Ce n'est ni un conforme, ni un "
                      "dépassement.</b>" + _lecture_faite(a)),
        }

    return {
        "mod": "conforme",
        "titre": "Aucun dépassement, aucune bascule",
        "texte": ("Sur ce qui a été cherché. Une eau n'est jamais déclarée pure "
                  "ici : elle est déclarée conforme <b>aux paramètres "
                  "recherchés ce jour-là</b>." + _lecture_faite(a)),
    }


def tete_donnees(a, natures, nom_dept=None, emprunt=None):
    """L'en-tête d'un bulletin, sous forme de données — un dictionnaire par
    prélèvement, que le rendu Python pose et que `fiche.js` repose à
    l'identique quand le lecteur change de prélèvement.

    Il n'y a donc qu'un seul compositeur, et il est ici : le navigateur ne
    fabrique aucune phrase, il déplace celles qui ont été écrites.
    """
    # La source sépare les réseaux par une barre sans espaces : « THIVILLE
    # (100 %)|ABA THIVILLE (100 %) » se lit mal et se coupe mal en fin de
    # ligne. On ne touche pas aux noms, seulement à ce qui les sépare.
    reseau = (a["noms_reseaux"] or "").replace("|", " | ")
    uge = a["nom_uge"] or ""
    chapo = nom_dept or a["dept"]
    if reseau:
        chapo += f" · réseau {reseau}"
    elif uge:
        chapo += f" · unité de distribution {uge}"

    # « — » n'est pas une valeur : une ligne sans contenu ne s'affiche pas.
    # Saintes le montre, sa maquette n'a pas de ligne « Gestionnaire ».
    identite = []
    if uge:
        identite.append(["Gestionnaire", h(uge)])
    if a["nom_distributeur"]:
        identite.append(["Distributeur", h(a["nom_distributeur"])])
    if a["nom_installation_amont"]:
        identite.append(["Ressource", h(a["nom_installation_amont"])])
    d_iso = str(a["date_prelevement"])[:10]
    # §8bis n° 5 : quand l'analyse est empruntée au réseau, dire où elle a été
    # prélevée. Ce n'est pas une note de bas de page, c'est dans l'identité.
    identite.append(["Prélèvement",
                     f'<time datetime="{h(d_iso)}">{h(_date_fr(d_iso))}</time>'
                     + (f" · prélevé à {h(emprunt)}" if emprunt else "")])
    # « panel intermédiaire » dans une ligne intitulée « Panel » se répète :
    # la maquette écrit « 398 paramètres · intermédiaire · complet ».
    effort = (a["classe_effort"] or "").removeprefix("panel ")
    identite.append(["Panel",
                     f"{a['nb_parametres']} paramètres · {h(effort)}"
                     + (" · <b>complet</b>" if a["est_complet"]
                        else " · <b>INCOMPLET</b>")])

    return {
        "surtitre": (f"Commune · INSEE {h(a['code_insee'])} · prélèvement du "
                     f"{h(_date_fr(d_iso))}"),
        "titre": h(a["commune"]),
        "chapo": h(chapo),
        "identite": identite,
        "verdict": verdict_tete(a, natures),
    }


def prelevements_html(commune_par_cle, ordre, courant, fichier=None):
    """La série des prélèvements complets, et la phrase qui interdit de la
    moyenner.

    Groupée par POINT D'EAU et non alignée par date : une commune en a souvent
    plusieurs et ils ne donnent pas la même eau (§8bis n° 5, le cas des Arcs).
    C'est la logique que `fiche.js` portait ; elle remonte ici, où elle est
    rendue une fois pour toutes dans le fichier.

    `--serie` dès cinq prélèvements : la ligne cesse alors de passer à la ligne
    et défile. Les maquettes bornent le seuil sans le fixer — Thiville en a
    trois et ne défile pas, Tramayes en a six et défile.
    """
    if len(ordre) < 2:
        return ""
    # La fiche autonome peut réunir plusieurs communes ; la vitrine, jamais.
    # Quand elle en réunit plusieurs, le nom revient sur chaque groupe, sans
    # quoi deux communes alignent des dates indiscernables.
    multi = len({commune_par_cle[k]["name"] for k in ordre}) > 1
    groupes = []
    for k in ordre:
        d = commune_par_cle[k]
        lib = d.get("pt") or "Point d'eau non déclaré"
        if multi:
            lib = f"{d['name']} · {lib}"
        for g in groupes:
            if g["lib"] == lib:
                g["cles"].append(k)
                break
        else:
            groupes.append({"lib": lib, "cles": [k]})

    serie = len(ordre) >= 5
    bouts = []
    for g in groupes:
        # Un seul point d'eau : on annonce le compte, comme la maquette.
        # Plusieurs : chaque groupe porte le nom de son point d'eau, sans quoi
        # les dates s'alignent comme si la commune n'avait qu'une eau.
        if len(groupes) == 1:
            bouts.append(f'<span class="lib">{len(ordre)} prélèvements '
                         f'complets</span>')
        else:
            bouts.append(f'<span class="lib">{h(g["lib"])}</span>')
        for k in g["cles"]:
            d = commune_par_cle[k]
            libelle = _date_courte(d["date_iso"]) if serie else d["date"]
            ici = ' aria-current="page"' if k == courant else ""
            # Sur la vitrine, `fichier` donne l'adresse de chaque bulletin :
            # le lien navigue, il ne commute pas. Sans lui — la fiche autonome,
            # qui réunit tout dans un seul fichier transmissible —, on retombe
            # sur la commutation par `data-k`.
            cible = (f'href="{h(fichier(k))}"' if fichier
                     else f'href="#bulletin" data-k="{h(k)}"')
            bouts.append(f"<a {cible}{ici}>{h(libelle)}</a>")

    return (f'<div class="prelevements{" prelevements--serie" if serie else ""}">'
            + "".join(bouts) + "</div>\n"
            '<p class="note">Chacun est <b>un point dans le temps, sur un point '
            "d'eau donné</b> : ils se lisent l'un après l'autre, jamais "
            "moyennés — une moyenne de bulletins n'a ni date ni grille, et ne "
            "peut donc être notée contre aucune.</p>")


def tete_html(tete, prelevements=""):
    """L'en-tête complet : l'identité à gauche, le verdict à droite.

    Les identifiants posés ici sont ceux que `fiche.js` repose quand on change
    de prélèvement. Ils ne servent à rien d'autre — pas de style, pas de
    sélecteur de feuille.
    """
    lignes = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>"
                     for k, v in tete["identite"])
    v = tete["verdict"]
    return f"""{prelevements}
  <div class="fiche-tete">
    <div>
      <p class="surtitre" id="f-surtitre">{tete['surtitre']}</p>
      <h1 id="f-titre">{tete['titre']}</h1>
      <p class="chapo" id="f-chapo">{tete['chapo']}</p>
      <dl class="identite" id="f-identite">{lignes}</dl>
    </div>
    <div class="verdict-bloc verdict-bloc--{v['mod']}" id="f-verdict">
      <p class="surtitre">Ce que dit ce bulletin</p>
      <h2 id="f-verdict-titre">{v['titre']}</h2>
      <p id="f-verdict-texte">{v['texte']}</p>
    </div>
  </div>"""


# ---------------------------------------------------------------------------
# La thèse et la double lecture — passe 2 du portage
# ---------------------------------------------------------------------------
# Ces trois sections existaient déjà, écrites en JavaScript : `jauge()` et
# `renderHero()` de `fiche.js` produisaient DÉJÀ le vocabulaire v2 — `.piste`,
# `.piste-rail`, `.piste-zone--bascule`. Elles n'étaient simplement nulle part
# dans le fichier. Ce qui suit est une transcription, pas une invention : la
# règle d'échelle, les trois zones et l'ordre des cas sont ceux du JavaScript,
# et les formulations sont celles des quatre maquettes.

CHIFFRES = ["zéro", "une", "deux", "trois", "quatre", "cinq", "six", "sept",
            "huit", "neuf", "dix"]


def _en_lettres(n, feminin=True):
    """« Huit mesures », pas « 8 mesures » : un titre se lit, il ne se compte
    pas. Au-delà de dix, le chiffre reprend la main.

    Le genre est un paramètre parce qu'un seul mot le porte — « une mesure »
    mais « un paramètre » —, et qu'un titre publié qui écrit « Une paramètre »
    décrédibilise tout ce qu'il y a en dessous."""
    if n == 1 and not feminin:
        return "un"
    return CHIFFRES[n] if 0 <= n <= 10 else str(n)


def _f(x):
    """« 0,14 » -> 0.14. Les valeurs circulent déjà formatées à la française."""
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return None


def piste_html(valeur, s16, s_applicable, unite):
    """La piste : une règle, trois zones, et les repères posés dessus.

    ÉCHELLE. La limite d'aujourd'hui se pose à 90 % de la largeur, et c'est
    elle qui fixe tout le reste. Ce n'est pas un choix graphique : il faut
    qu'une mesure qui DÉPASSE cette limite ait encore de la place pour se
    montrer à droite, sinon elle se plaque contre le bord et l'ampleur du
    dépassement disparaît au moment où elle compte le plus.

    TROIS ZONES, et elles portent la thèse à elles seules : sous la limite de
    2016, conforme aux deux grilles ; entre les deux, la bascule — tout ce qui
    tombe là était non conforme hier et ne l'est plus ; au-delà de la limite
    d'aujourd'hui. **Quand les deux limites sont égales il n'y a pas de zone de
    bascule** : rien ne s'est déplacé, et en dessiner une inventerait un écart.
    """
    v, b = _f(valeur), _f(s_applicable)
    a16 = _f(s16)
    if v is None or b is None or b <= 0:
        return ""
    u = f" {unite}" if unite else ""
    maxi = b / 0.9
    pc = lambda x: max(0.0, min(98.0, (x / maxi) * 100.0))  # noqa: E731
    pb = pc(b)
    pa = pc(a16) if a16 is not None else None
    bascule = pa is not None and pa < pb

    zones = []
    def zone(cls, gauche, largeur):
        if largeur > 0:
            zones.append(f'<div class="piste-zone piste-zone--{cls}" '
                         f'style="left:{gauche:.4g}%;width:{largeur:.4g}%"></div>')
    zone("deux", 0, pa if bascule else pb)
    if bascule:
        zone("bascule", pa, pb - pa)
    zone("hors", pb, 100 - pb)

    reperes = []
    if bascule:
        reperes.append(f'<div class="piste-lim" style="left:{pa:.4g}%">'
                       f'<em>{h(s16)} — limite 2016</em></div>')
    # « limite d'aujourd'hui » et non « limite 2026 » comme l'écrit la
    # maquette : ce repère est le seuil APPLICABLE à la date du prélèvement
    # (§2.10), et sur un bulletin de 2018 ce n'est pas celui de 2026.
    reperes.append(f'<div class="piste-lim" style="left:{pb:.4g}%"><em>'
                   f'{h(s_applicable)} — limite '
                   f'{"d\'aujourd\'hui" if bascule else "de qualité"}</em></div>')
    reperes.append(f'<div class="piste-mes" style="left:{pc(v):.4g}%">'
                   f'<em>{h(valeur)}{h(u)}</em></div>')

    alt = (f"Mesure {valeur}{u} : "
           + (f"au-dessus de la limite de {s16} de 2016, "
              if a16 is not None and a16 < b and v > a16 else "")
           + ("au-dessus de" if v > b else "sous")
           + f" la limite de {s_applicable} d'aujourd'hui")
    return (f'<div class="piste" role="img" aria-label="{h(alt)}">'
            '<div class="piste-rail"></div>'
            + "".join(zones) + "".join(reperes) + "</div>")


LEGENDE_PISTE = (
    '<div class="piste-lg">'
    '<span><i style="background:var(--vert)"></i> conforme aux deux grilles</span>'
    '<span><i style="background:var(--bascule)"></i> a changé de statut</span>'
    '<span><i style="background:var(--rouge)"></i> dépasse les deux</span>'
    "</div>")


def _section(surtitre, titre, chapo, contenu):
    """Une section de la fiche : son surtitre, son titre, son chapô, sa
    matière. `main` est nu et chaque section porte sa zone — c'est ce qui
    permet à la bande alternée de la charte d'aller d'un bord à l'autre."""
    return (f'<section class="section"><div class="zone zone-large">'
            f'<p class="surtitre">{surtitre}</p><h2>{titre}</h2>'
            + (f'<p class="chapo">{chapo}</p>' if chapo else "")
            + contenu + "</div></section>")


def bascules_html(d):
    """Les mesures qui ont changé de statut sans que l'eau change.

    C'est la thèse du projet, montrée plutôt qu'écrite : sur chaque piste la
    limite de 2016, celle qui s'applique, et la mesure entre les deux.
    """
    cas = (d.get("hero") or {}).get("bascules") or []
    if not cas:
        return ""
    cartes = []
    for c in cas:
        # La DATE du déplacement n'est pas dans ce que rend
        # `bascules_en_tete()` — seulement le fait qu'il soit daté. On dit donc
        # qu'il l'est, sans écrire une date qu'on n'a pas lue (§2.5, §2.7).
        date = ('<span class="basc-date">Déplacement daté : la même valeur, la '
                "veille, n'était pas conforme.</span>" if c.get("datee") else "")
        ds = c.get("ds") or {}
        lien = (f'<p><a href="{h(ds["u"])}">Ce que cette substance démontre à '
                f"l'échelle du corpus →</a></p>" if ds.get("u") else "")
        cartes.append(
            '<div class="basc">'
            f'<div class="basc-tete"><span class="basc-nom">{h(c["p"])}</span>'
            f'<span class="basc-val">{h(c["v"])} {h(c["u"])}</span></div>'
            + piste_html(c["v"], c["s16"], c["s"], c["u"]) + LEGENDE_PISTE
            + f'<p><b>Au-dessus de la limite de {h(c["s16"])} {h(c["u"])} en '
            f'vigueur en 2016, sous celle de {h(c["s"])} {h(c["u"])} appliquée '
            "aujourd'hui.</b></p>" + date + lien + "</div>")

    n = len(cas)
    titre = (f"{_en_lettres(n).capitalize()} mesure{'s' if n > 1 else ''}, deux "
             "verdicts opposés, une seule eau")
    return _section(
        "Le réétalonnage", titre,
        "Sur chaque piste : la limite en vigueur en 2016, celle qui s'applique "
        "aujourd'hui, et la mesure entre les deux.",
        f'<div class="bascules">{"".join(cartes)}</div>')


NATURE_SEUIL = {"limite": ("", "limite de qualité"),
                "reference": ("dep--vigilance", "référence de qualité"),
                "vigilance": ("dep--vigilance", "valeur de vigilance")}


def depassements_html(d):
    """Ce qui dépasse — une jauge par mesure, et la nature de ce qui est
    franchi écrite dessus.

    Sans cette étiquette, la carte d'un métabolite reclassé « non pertinent »
    est indiscernable de celle d'un plomb au-dessus de sa limite : c'est
    l'erreur des cinq bulletins de Paulinet, et elle disait au lecteur
    l'inverse de ce que conclut l'ARS.
    """
    cas = (d.get("hero") or {}).get("depassements") or []
    if not cas:
        return ""
    cartes = []
    for c in cas:
        mod, nom_nature = NATURE_SEUIL.get(c.get("nat"), ("", ""))
        v, s = _f(c["v"]), _f(c["s"])
        maxi = max(v or 0, s or 0) or 1
        fois = ""
        if v and s:
            fois = f"<b>× {_nb(round(v / s, 2))}</b>"
        etat = (f' <span class="etat etat--attention">{nom_nature}</span>'
                if mod else "")
        ds = c.get("ds") or {}
        lien = (f' <a href="{h(ds["u"])}">Ce que cette substance démontre à '
                f"l'échelle du corpus →</a>" if ds.get("u") else "")
        cartes.append(
            f'<div class="dep{" " + mod if mod else ""}">'
            f'<div class="dep-tete"><span class="dep-nom">{h(c["p"])}{etat}'
            f'</span><span class="dep-val">{h(c["v"])} {h(c["u"])}</span></div>'
            f'<div class="jauge"><i style="width:{(v or 0) / maxi * 100:.4g}%">'
            f'</i><b style="left:{(s or 0) / maxi * 100:.4g}%"></b></div>'
            f'<div class="jauge-lg"><span>seuil applicable : '
            f'<b>{h(c["s"])} {h(c["u"])}</b></span><span>{fois}</span></div>'
            f'<p><b>La règle en vigueur le jour du prélèvement</b> est celle '
            f'contre laquelle la mesure est notée — un reclassement n\'est pas '
            f'rétroactif.{lien}</p></div>')

    n = len(cas)
    titre = (f"{_en_lettres(n).capitalize()} mesure{'s' if n > 1 else ''} "
             f"au-dessus de {'leur' if n > 1 else 'son'} seuil")
    return _section(
        "Ce qui dépasse", titre,
        "Le trait sur chaque jauge marque le seuil applicable le jour du "
        "prélèvement. La barre le franchit d'autant plus qu'elle en est loin.",
        f'<div class="depassements">{"".join(cartes)}</div>')


def lectures_html(d, a):
    """Le même prélèvement, noté deux fois : ce que l'administration en dit, et
    ce que disent les grilles datées. Deux colonnes de même poids — c'est la
    comparaison qui est l'objet du projet, pas la substitution.
    """
    axes = (d.get("official") or {}).get("axes") or []
    # L'état de la colonne officielle se lit sur les trois axes rendus par
    # l'ARS, pas sur le seul axe « limites » : un bulletin conforme aux limites
    # et non conforme aux références n'est ni vert ni rouge.
    manques = [n for n, val, lvl in axes if lvl not in ("vert", None)]
    if not axes:
        etat_off, mod_off = "Conclusion non renseignée", "indetermine"
    elif not manques:
        etat_off, mod_off = "Conforme", "conforme"
    else:
        etat_off = "Conforme aux limites · non " + " et ".join(
            f"conforme aux {n.lower()}" for n in manques)
        mod_off = "attention"
        if any("limite" in n.lower() for n in manques):
            etat_off = "Non " + " et ".join(f"conforme aux {n.lower()}"
                                            for n in manques)
            mod_off = "depassement"
    detail_axes = " ".join(f"{h(n)} : {h(val)}." for n, val, lvl in axes)
    concl = (d.get("official") or {}).get("concl") or "—"

    notes, lues = a["nb_mesures_notees"] or 0, a["nb_mesures_lues"] or 0
    sans = a["nb_sans_seuil"] or 0
    basc, indet = a["nb_bascules"] or 0, a["nb_indetermines"] or 0
    total_dep = a["nb_depasse_applicable"] or 0

    etat_cit = (d.get("cit") or {}).get("v") or ""
    if basc:
        etat_cit += f" · {basc} {_accord(basc, 'bascule')}"
        titre_cit = (f"Mais {basc} {_accord(basc, 'mesure')} "
                     f"{_accord(basc, 'aurait', 'auraient')} dépassé la limite "
                     "en vigueur en 2016")
    elif total_dep:
        titre_cit = (f"{total_dep} {_accord(total_dep, 'paramètre')} au-dessus "
                     "du seuil applicable ce jour-là")
    else:
        titre_cit = "Aucun dépassement à la date, aucune bascule"
    if indet:
        etat_cit += f" · {indet} {_accord(indet, 'indéterminé')}"
    mod_cit = {"rouge": "depassement", "ambre": "attention",
               "vert": "conforme"}.get((d.get("cit") or {}).get("level"),
                                       "indetermine")

    detail_cit = (f"Chaque mesure est comparée au seuil en vigueur <b>le "
                  f"{h(_date_fr(a['date_prelevement']))}</b>, puis à celui de "
                  "2016 et au repère le plus protecteur identifié."
                  + _lecture_faite(a)
                  + (f" Les {sans} autres n'ont aucun seuil de comparaison, ni "
                     "au référentiel ni dans la limite déclarée par la source."
                     if sans else ""))

    return _section(
        "La double lecture", "Le même prélèvement, noté deux fois", None,
        '<div class="lectures">'
        '<div class="lecture">'
        '<p class="surtitre">Lecture officielle — telle qu\'elle a été rendue</p>'
        f'<span class="etat etat--{mod_off}">{h(etat_off)}</span>'
        f'<h3>{h(_extrait(concl, 90))}</h3>'
        f'<p>« {h(concl)} » <i>— conclusion sanitaire telle que rendue par '
        f'l\'ARS.</i> {detail_axes}</p>'
        "</div>"
        '<div class="lecture">'
        '<p class="surtitre">Lecture datée — grilles 2016, 2026, et la plus '
        'stricte identifiée</p>'
        f'<span class="etat etat--{mod_cit}">{h(etat_cit)}</span>'
        f"<h3>{h(titre_cit)}</h3><p>{detail_cit}</p>"
        "</div></div>")


# ---------------------------------------------------------------------------
# Les indicateurs — passe 3 du portage
# ---------------------------------------------------------------------------
# Six tuiles fixes, et « non recherché » est un état plein, avec sa couleur et
# son explication. Jamais un blanc : une case vide se lit comme une absence de
# substance alors qu'elle est une absence de recherche (§2.11).

# L'état calculé par `indicateurs._etat()` -> le modificateur de la charte.
# La table est explicite plutôt que déduite : `hors_plage` et `proche` n'ont
# pas de modificateur à eux, et les rabattre silencieusement sur « conforme »
# effacerait précisément ce qu'ils signalent.
IND_MOD = {
    "depassement": "depassement",
    "hors_plage": "attention",
    "proche": "attention",
    "bascule": "bascule",
    "indetermine": "indetermine",
    "sous_lq": "conforme",
    "conforme": "conforme",
    "absent": "vide",
    "neutre": "",
}
JG_MOD = {
    "depassement": "depasse", "hors_plage": "proche", "proche": "proche",
    "bascule": "proche", "indetermine": "indet", "sous_lq": "souslq",
    "conforme": "ok",
}
# Le surtitre nomme le rayon, le titre dit ce qu'on y a trouvé : les deux ne
# se répètent pas. Les titres et les chapôs, eux, viennent de
# `indicateurs.GROUPES` — ils sont écrits une fois, là où ils sont relus.
SURTITRE_GROUPE = {"polluants": "Ce qu'il y a dans cette eau",
                   "eau": "Le caractère de la ressource",
                   "lecture": "Ce que vaut cette lecture"}


def _jauge_ind(i):
    """La barre d'une tuile : où se situe la mesure par rapport à son seuil.

    C'est ce qui rend un nombre lisible d'un coup d'œil — « 0,493 » ne dit
    rien, « 99 % de la limite » dit tout. Pas de barre quand il n'y a pas de
    seuil : dessiner une jauge sans terme de comparaison inventerait le terme.
    """
    if i["etat"] in ("absent", "neutre") or i.get("seuil") is None:
        return ""
    unite = i.get("unite") or ""
    if i["etat"] == "sous_lq":
        # Sous la limite de quantification, la barre ne mesure rien : elle
        # marque seulement que l'analyse a regardé et n'a rien vu au-dessus de
        # ce que son instrument distingue. Un dixième de piste, et c'est dit.
        pct, droite = 10, "sous la LQ"
    else:
        part = i.get("part")
        if part is None:
            return ""
        pct = max(0, min(100, round(part * 100)))
        droite = f"{pct} % de la limite"
    return (f'<div class="jauges"><div class="jg jg--{JG_MOD.get(i["etat"], "neutre")}"'
            f' style="--pct:{pct}%"><div class="jg-lg">'
            f'<span>limite réglementaire <b>{h(_nb(i["seuil"]))} {h(unite)}</b>'
            f'</span><b>{h(droite)}</b></div>'
            '<div class="jg-piste"><em></em></div></div></div>')


def _tuile(i, a):
    """Une tuile d'indicateur : le libellé, la valeur, l'état, la barre, la
    lecture. Et le dénominateur quand la valeur est un compte — un nombre de
    substances quantifiées ne veut rien dire sans ce qui a été cherché (§2.8).
    """
    unite = i.get("unite") or ""
    texte = i.get("texte") or "—"
    # L'unité passe en `small` : la valeur doit rester lisible d'un coup, et
    # « 12,4 mg/L » écrit d'un seul poids se lit moins vite que « 12,4 » suivi
    # de son unité.
    if unite and texte.endswith(" " + unite):
        valeur = (f'{h(texte[:-len(unite) - 1])} <small>{h(unite)}</small>')
    else:
        valeur = h(texte)

    etats = []
    if i["etat"] == "absent":
        etats.append('<span class="etat etat--gris">non recherché</span>')
    elif i["etat"] == "sous_lq":
        etats.append('<span class="etat etat--conforme">sous la limite de '
                     "quantification</span>")
    elif i["etat"] == "indetermine":
        etats.append('<span class="etat etat--indetermine">indéterminé</span>')
    elif i["etat"] == "depassement":
        etats.append('<span class="etat etat--depassement">au-dessus du '
                     "seuil applicable</span>")
    elif i["etat"] == "bascule":
        etats.append('<span class="etat etat--bascule">bascule</span>')
    # §2.7 et §8bis n° 8 : une valeur en `a_verifier` est signalée comme telle,
    # partout, et ne s'arrondit jamais en « vérifié ».
    if i.get("a_verifier"):
        etats.append('<span class="etat etat--averifier">seuil à vérifier</span>')

    denom = ""
    if i.get("cle") == "pesticides_nb" and a.get("nb_parametres"):
        denom = (f'<span class="denominateur">sur {a["nb_parametres"]} '
                 "paramètres recherchés</span>")

    detail = (f'<p class="note">{h(i["detail"])}</p>'
              if i.get("detail") else "")
    # §8bis n° 11 : quand la LQ dépasse le seuil, la tuile le dit et le
    # chiffre. Une tuile verte au-dessus d'une analyse aveugle serait le pire
    # mensonge de la fiche.
    lq = (f'<p class="note">{h(i["lq_mention"])}</p>'
          if i.get("lq_mention") else "")
    mod = IND_MOD.get(i["etat"], "")
    return (f'<div class="ind{" ind--" + mod if mod else ""}">'
            f'<h4>{h(i["libelle"])}</h4>'
            f'<span class="val">{valeur}</span>'
            + "".join(etats) + denom + _jauge_ind(i) + detail + lq
            + (f'<p>{h(i["lecture"])}</p>' if i.get("lecture") else "")
            + "</div>")


def indicateurs_html(d, a):
    """Les trois rayons d'indicateurs, dans l'ordre du fichier versionné."""
    ind = d.get("ind") or {}
    out = []
    for cle, titre, chapo in (d.get("groupes") or []):
        tuiles = ind.get(cle) or []
        if not tuiles:
            continue
        out.append(_section(
            SURTITRE_GROUPE.get(cle, "Les indicateurs"), h(titre), chapo,
            '<div class="indicateurs">'
            + "".join(_tuile(i, a) for i in tuiles) + "</div>"))
    return "".join(out)


# ---------------------------------------------------------------------------
# Les trois registres, la LQ, les PFAS et le cumul — passe 4 du portage
# ---------------------------------------------------------------------------

REGISTRES = [
    ("avere", "avere", "Avérés au sens réglementaire",
     "Reconnus comme perturbateurs endocriniens par le droit européen."),
    ("suspecte", "suspect", "Suspectés par la littérature",
     "Des travaux publiés le rapportent, sans reconnaissance réglementaire."),
    ("non_documente", "nondoc", "Statut non documenté",
     "Quantifiés dans cette eau, sans statut établi dans l'un ou l'autre "
     "registre. Ce n'est pas un blanc-seing : c'est une absence d'instruction."),
]


def registres_html(d):
    """Trois registres, jamais fusionnés (§2.15).

    `pe_reglementaire`, `pe_scientifique`, `cancerogenicite_circ` disent trois
    choses différentes, et aucun ne se déduit des autres. Les afficher côte à
    côte sans les fondre est la forme même de la règle : dire « c'est un
    perturbateur endocrinien » sans préciser le registre est une faute.
    """
    pe = d.get("pe") or {}
    if not any(pe.get(cle) for cle, _, _, _ in REGISTRES):
        return ""
    blocs = []
    for cle, mod, titre, sous in REGISTRES:
        subs = pe.get(cle) or []
        if subs:
            items = "".join(
                f'<li><b>{h(s["libelle"])}</b> <span>{h(s.get("texte") or "")}'
                f"</span></li>" for s in subs)
        else:
            items = ('<li class="vide">Aucune substance quantifiée dans ce '
                     "registre</li>")
        blocs.append(
            f'<div class="registre registre--{mod}">'
            f'<div class="registre-tete"><span class="registre-n">{len(subs)}'
            f"</span><h4>{titre}</h4></div><p>{sous}</p>"
            f'<ul class="substances">{items}</ul></div>')
    return _section(
        "Les trois registres",
        "Trois listes qui ne disent pas la même chose et ne se remplacent pas",
        "Un statut réglementaire, une suspicion de la littérature et une "
        "absence d'instruction sont trois faits distincts. Les fondre en un "
        "seul chiffre serait la seule manière de se tromper à coup sûr.",
        f'<div class="registres">{"".join(blocs)}</div>')


def lq_html(d):
    """Quand la limite de quantification passe au-dessus du seuil (§8bis n° 11).

    Sous cette valeur, l'analyse ne voit rien — là précisément où la
    conformité se joue. Et une LQ élevée est une **capacité d'instrument**,
    jamais une négligence (§2.1) : l'échelle situe celle-ci parmi celles du
    corpus, et affiche la base sur laquelle elle est située, car elle se
    déplace.
    """
    plafond = d.get("plafond") or {}
    lignes = plafond.get("lignes") or []
    if not lignes:
        return ""
    blocs = []
    for l in lignes:
        b = l.get("bareme") or {}
        echelle = ""
        if b.get("min") and b.get("ici"):
            pos = max(0, min(100, round((b.get("position") or 0) * 100)))
            echelle = (
                '<div class="echelle" aria-hidden="true">'
                '<div class="echelle-piste"></div>'
                '<div class="echelle-pt echelle-pt--debut" style="left:0">'
                f'<span>{h(b["min"])} {h(l.get("unite") or "")} — la plus fine '
                "relevée</span></div>"
                f'<div class="echelle-pt echelle-pt--ici'
                f'{" echelle-pt--fin" if pos >= 100 else ""}" '
                f'style="left:{pos}%"><span>ici : {h(b["ici"])} '
                f'{h(l.get("unite") or "")}</span></div></div>')
        # La base est affichée avec le classement, sans quoi « la plus fine
        # relevée » ne veut rien dire : elle se déplace avec le corpus.
        base = ""
        if b.get("nb_bulletins"):
            base = (f'<p class="note">Comparaison faite sur '
                    f'{b["nb_bulletins"]} bulletins, '
                    f'{b.get("nb_departements", "?")} départements — la plus '
                    "fine <b>identifiée</b>, pas la plus fine possible.</p>")
        blocs.append(
            '<div class="lq"><div class="lq-tete">'
            f'<b>{h(l["libelle"])}</b>'
            f'<span class="lq-mult">× {h(_nb(l.get("rapport")))}</span></div>'
            f'<p>{h(l.get("mention") or "")}</p>{echelle}{base}</div>')

    n = len(lignes)
    return _section(
        "Ce que le laboratoire ne pouvait pas voir",
        (f"{_en_lettres(n, feminin=False).capitalize()} "
         f"paramètre{'s' if n > 1 else ''} "
         f"cherché{'s' if n > 1 else ''} avec un instrument qui ne peut pas "
         "conclure"),
        "La limite de quantification du laboratoire se situe au-dessus du "
        "seuil de comparaison. Ce n'est ni un conforme, ni un dépassement.",
        "".join(blocs))


def pfas_html(d):
    """Chaînes longues et chaînes courtes — la mesure existe, la norme ne la
    regarde pas.

    La somme réglementaire de 4 ne vise que les chaînes longues ; les courtes
    sont mesurées et restent hors de son assiette. **Une somme ne se compare
    jamais sans son périmètre** (§2.13, §2.14) : c'est ce que ce bloc montre.
    """
    pfas = d.get("pfas") or {}
    if pfas.get("rien_de_cherche") or not pfas.get("cherchees_total"):
        return ""
    blocs = []
    for cle, mod, titre, sous in (
            ("longue", "vise", "Chaînes longues",
             "celles que vise la somme de 4"),
            ("courte", "hors", "Chaînes courtes",
             "mesurées, hors de l'assiette de la somme de 4")):
        f = pfas.get(cle) or {}
        subs = f.get("substances") or []
        if not subs:
            continue
        items = "".join(
            f'<li class="pf{" pf--quant" if s.get("quantifie") else ""}">'
            f'<b>{h(s.get("sigle") or s.get("libelle"))}</b>'
            f'<span>C{s.get("carbones")} · {h(s.get("type") or "")}</span></li>'
            for s in subs)
        blocs.append(
            f'<div class="pfas-fam pfas-fam--{mod}"><h4>{titre}</h4>'
            f'<p>{sous} · <b>{f.get("quantifiees", 0)} quantifiée(s) sur '
            f'{f.get("cherchees", 0)} recherchées</b></p>'
            f'<ul class="pf-liste">{items}</ul></div>')
    if not blocs:
        return ""
    return _section(
        "Le périmètre de la somme",
        "La mesure existe. La norme ne la regarde pas.",
        "La somme réglementaire de 4 ne porte que sur les chaînes longues. "
        "Les courtes sont cherchées, parfois trouvées, et ne comptent dans "
        "aucun total opposable — <b>même valeur, assiette différente</b>.",
        f'<div class="pfas-familles">{"".join(blocs)}</div>')


def barres_html(d):
    """Ce qui pèse dans l'indice de danger, mesure par mesure.

    Trois contraintes non négociables du §7.1, et elles sont dans le code
    plutôt que dans une consigne : l'indice **n'est jamais nommé « risque »**,
    il n'est **jamais publié sans le nombre de substances qui le composent**,
    et il ne vaut pas verdict de potabilité. Au-delà de six lignes, le reste se
    replie — il ne se coupe pas : un compteur et une liste qui se contredisent
    sur le même écran est ce que le §2.8 interdit.
    """
    danger = d.get("danger") or {}
    parts = danger.get("parts") or []
    if not parts or danger.get("total") is None:
        return ""

    def ligne(p):
        part = p.get("part")
        largeur = max(0.0, min(100.0, (part or 0) * 100 / 3))
        return (f'<li><div><div class="nom">{h(p["p"])}</div>'
                f'<div class="det">{h(p["v"])} {h(p.get("u") or "")} pour une '
                f'limite de {h(p.get("s") or "—")}</div>'
                f'<div class="jauge"><i style="width:{largeur:.4g}%"></i>'
                f'<b style="left:33.3%"></b></div></div>'
                f'<div class="mult{" inf" if (part or 0) < 1 else " sup"}">'
                f'× {h(_nb(round(part, 3)) if part is not None else "—")}'
                "</div></li>")

    tete = parts[:6]
    reste = parts[6:]
    liste = f'<ul class="barres">{"".join(ligne(p) for p in tete)}</ul>'
    if reste:
        liste += (f'<details class="plus"><summary>Afficher les {len(reste)} '
                  "autres substances qui composent l'indice</summary>"
                  f'<ul class="barres">{"".join(ligne(p) for p in reste)}</ul>'
                  "</details>")
    total = _nb(round(danger["total"], 2))
    n = danger.get("n") or len(parts)
    return _section(
        "Le cumul",
        f"{total} — et voici les {_en_lettres(min(len(tete), 6))} mesures qui "
        "y pèsent le plus",
        f"Indice de danger calculé sur <b>{n} substances de synthèse</b>. "
        "Ce n'est pas une estimation de risque sanitaire et il ne vaut pas "
        "verdict de potabilité : il sert à classer des bulletins entre eux.",
        liste)


# ---------------------------------------------------------------------------
# L'alerte de panel et les repères « nourrissons » — 17 août 2026
# ---------------------------------------------------------------------------
# Deux blocs remis d'aplomb après une remarque de Yannick sur la publication.
#
# LES REPÈRES NOURRISSONS AVAIENT PUREMENT DISPARU. `reperes_nourrissons()`
# calculait toujours la donnée ; le portage ne l'a jamais rendue. Du contenu
# qui existait avant est parti en ligne en moins — c'est le défaut le plus
# grave qu'un portage puisse produire, et le contrôle de charte ne pouvait pas
# le voir : il mesure ce qui est présent, jamais ce qui manque.
#
# L'ALERTE DE PANEL ÉTAIT RELÉGUÉE EN BAS DE PAGE, encore fabriquée par
# `fiche.js` dans le bloc non porté, sans couleur ni compteur. Or « la dernière
# analyse complète de cette eau a 34 mois » est une information de premier
# plan : elle conditionne la lecture de tout ce qui suit. Sa place est juste
# après l'en-tête.


def _gras(texte):
    """Les paragraphes de `suivi_panel` portent leur emphase en `**…**` — la
    convention d'écriture du dépôt. On la rend, on ne la réécrit pas."""
    bouts = h(texte).split("**")
    return "".join(b if i % 2 == 0 else f"<b>{b}</b>"
                   for i, b in enumerate(bouts))


def alerte_html(d):
    """« Depuis ce prélèvement » — l'âge de la dernière analyse complète.

    Le compteur est extrait du titre calculé par `suivi_panel`, jamais
    recalculé ici : deux endroits qui comptent les mois finiraient par ne plus
    dire le même nombre.
    """
    a = d.get("alerte_panel")
    if not a or not a.get("titre"):
        return ""
    paras = a.get("paragraphes") or []
    # Le dernier paragraphe porte le mécanisme administratif — la liste
    # régionale arrêtée pour la durée d'un marché. Il se distingue des autres :
    # c'est lui qui interdit d'y lire une intention (§2.1).
    corps = "".join(f"<p>{_gras(p)}</p>" for p in paras[:-1])
    if paras:
        corps += f'<p class="note note--attention">{_gras(paras[-1])}</p>'

    m = re.search(r"(\d+)\s*mois", a["titre"])
    titre = (f'<span class="compteur">{m.group(1)}</span> mois — c\'est l\'âge '
             "de la dernière analyse complète de cette eau" if m
             else h(a["titre"]))
    return ('<div class="alerte"><p class="surtitre">Depuis ce prélèvement</p>'
            f"<h3>{titre}</h3>"
            f'<div class="alerte-grille"><div>{corps}</div></div></div>')


def nourrissons_html(d):
    """Les repères « nourrissons » — et ce qu'ils ne sont pas.

    Ce sont les valeurs que doit respecter une eau EMBOUTEILLÉE pour porter la
    mention « convient à l'alimentation des nourrissons ». Une eau du robinet
    parfaitement conforme peut se situer au-dessus : **ce n'est pas une
    non-conformité**, et la fiche doit le dire dans la même phrase que le
    chiffre, sans quoi elle fabrique une alerte là où il n'y en a pas (§2.2).

    Deux barres par paramètre, et c'est tout l'intérêt du bloc : la limite au
    robinet, puis le repère nourrissons, sur la même tuile. Une seule des deux
    laisserait croire qu'il n'y a qu'un terme de comparaison.
    """
    lignes = d.get("nourrissons") or []
    if not lignes:
        return ""
    tuiles = []
    for n in lignes:
        unite = n.get("unite") or ""
        repere, limite = _f(n.get("repere")), _f(n.get("limite"))
        part = n.get("part")
        valeur = (part * repere) if (part is not None and repere) else None

        barres = ""
        if valeur is not None and limite:
            pc = max(0, min(100, round(valeur / limite * 100)))
            barres += (f'<div class="jg jg--ok" style="--pct:{pc}%">'
                       f'<div class="jg-lg"><span>limite au robinet '
                       f'<b>{h(n["limite"])} {h(unite)}</b></span>'
                       f"<b>{pc} %</b></div>"
                       '<div class="jg-piste"><em></em></div></div>')
        if part is not None and repere:
            pc = max(0, min(100, round(part * 100)))
            droite = (f"× {_nb(round(part, 2))}" if n.get("au_dessus")
                      else f"{pc} %")
            mod = "jg--depasse" if n.get("au_dessus") else "jg--ok"
            barres += (f'<div class="jg jg--repere {mod}" style="--pct:{pc}%">'
                       f'<div class="jg-lg"><span>repère nourrissons '
                       f'<b>{h(n["repere"])} {h(unite)}</b></span>'
                       f"<b>{h(droite)}</b></div>"
                       '<div class="jg-piste"><em></em></div></div>')

        # La phrase dit les deux choses à la fois, et jamais l'une sans
        # l'autre : au-dessus du repère, et conforme au robinet.
        lecture = ("Conforme au robinet, <b>au-dessus du repère "
                   "nourrissons</b> — ce qui n'est pas une non-conformité."
                   if n.get("au_dessus")
                   else "Sous le repère nourrissons comme sous la limite au "
                        "robinet.")
        tuiles.append(
            f'<div class="ind ind--{"attention" if n.get("au_dessus") else "conforme"}">'
            f'<h4>{h(n["libelle"])}</h4>'
            f'<span class="val">{h(n.get("texte") or "—")}</span>'
            f'<div class="jauges">{barres}</div><p>{lecture}</p></div>')

    return _section(
        "Repères « nourrissons »",
        "Ces valeurs ne sont pas des limites au robinet",
        "Ce sont les repères que doit respecter une eau <b>embouteillée</b> "
        "pour porter la mention « convient à l'alimentation des nourrissons » "
        "(arrêté du 14 mars 2007). Une eau parfaitement conforme peut se "
        "situer au-dessus : cela ne la rend pas non conforme, cela dit "
        "seulement qu'elle ne serait pas vendue sous cette mention.",
        f'<div class="indicateurs">{"".join(tuiles)}</div>')


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
def analyses(con, version, insees=None, historique=False):
    """
    Par défaut, le DERNIER bulletin de chaque point d'eau — c'est l'objet de
    la fiche : « la dernière analyse la plus complète ». `historique=True`
    reprend toute la série, utile pour lire une évolution mais illisible sur
    une fiche destinée à un habitant.
    """
    where = "WHERE a.version_referentiel = ?"
    args = [version]
    if insees:
        where += f" AND a.code_insee IN ({','.join('?' * len(insees))})"
        args += list(insees)
    if not historique:
        where += """ AND a.date_prelevement = (
            SELECT MAX(b.date_prelevement) FROM analyses_figees b
            WHERE b.version_referentiel = a.version_referentiel
              AND b.code_insee = a.code_insee
              AND COALESCE(b.code_installation_amont,'') 
                  = COALESCE(a.code_installation_amont,''))"""
    return con.execute(f"""
        SELECT a.*, p.conf_limites_bact, p.conf_limites_pc, p.conf_references_pc,
               p.nom_distributeur,
               a.nb_mesures_lues - a.nb_mesures_notees AS nb_sans_seuil
        FROM analyses_figees a
        JOIN prelevements p ON p.code_prelevement = a.code_prelevement
        {where}
        ORDER BY a.commune, a.date_prelevement DESC
    """, args).fetchall(), [d[0] for d in con.description]


def parametres(con, code_prel, version):
    """
    Le bulletin entier, ligne à ligne.

    Les mesures viennent de `mesures` — ce sont des faits, ils ne bougent
    pas. Le seuil affiché vient de `verdicts_figes`, donc de la grille
    estampillée. Un paramètre mesuré sans seuil de comparaison apparaît
    quand même, sans seuil : le taire reviendrait à masquer ce qu'on ne
    sait pas noter.

    Le seuil et le verdict retenus sont ceux **applicables le jour du
    prélèvement**, pas ceux d'aujourd'hui (CLAUDE.md §2.10). Afficher
    `depasse_2026` ici mettrait le détail en désaccord avec le compteur
    `nb_depasse_applicable` de la même fiche, et donnerait « conforme » à une
    ligne que l'ARS avait déclarée non conforme à l'époque.
    """
    return con.execute("""
        SELECT m.libelle_parametre, m.resultat_num, m.lq, m.est_quantifie, m.unite,
               f.seuil_applicable, f.depasse_applicable, f.fiabilite,
               f.grille_applicable, f.seuil_2016, f.seuil_2026_effectif,
               f.bascule_2016_2026, f.bascule_datee,
               f.indetermine_strict, f.indetermine_condition,
               f.lq_aveugle, f.lq_rapport_seuil
        FROM mesures m
        LEFT JOIN verdicts_figes f
               ON f.code_prelevement = m.code_prelevement
              AND f.libelle_parametre = m.libelle_parametre
              AND f.version_referentiel = ?
        WHERE m.code_prelevement = ?
        ORDER BY m.est_quantifie DESC, m.libelle_parametre
    """, [version, code_prel]).fetchall()


def rattachements(con, version, insees=None):
    """
    Les communes qui n'ont pas de bulletin propre mais boivent l'eau d'un
    réseau analysé ailleurs.

    Sans cette table, la fiche affiche le nom de la commune où le
    prélèvement a eu lieu, et l'habitant qui a demandé SA commune reçoit une
    fiche au nom d'une autre. C'est la moitié citoyenne de la règle de repli
    (CLAUDE.md §2.3) : elle doit aller jusqu'à la sortie.
    """
    where = "WHERE version_referentiel = ? AND statut = 'rattachee_reseau'"
    args = [version]
    if insees:
        where += f" AND code_insee IN ({','.join('?' * len(insees))})"
        args += list(insees)
    return {r[0]: {"code_insee": r[0], "commune": r[1], "dept": r[2],
                   "codes_postaux": r[3], "lon": r[4], "lat": r[5],
                   "commune_prelevement": r[6], "code_prelevement": r[7]}
            for r in con.execute(f"""
                SELECT code_insee, commune, dept, codes_postaux, lon, lat,
                       commune_prelevement, code_prelevement
                FROM couverture_communes {where}
            """, args).fetchall()}


def non_documentees(con, version, insees=None):
    where = "WHERE version_referentiel = ? AND statut = 'non_documentee'"
    args = [version]
    if insees:
        where += f" AND code_insee IN ({','.join('?' * len(insees))})"
        args += list(insees)
    return con.execute(f"SELECT commune, code_insee FROM couverture_communes {where}",
                       args).fetchall()


def bloc_commune(con, ligne, cols, redaction, version, rattachement=None,
                 proposee=None, accroches=None, nom_dept=None):
    """Une ligne de `analyses_figees` -> le dictionnaire attendu par le gabarit.

    **Décision de Yannick du 10 août 2026 : la fiche communale ne porte plus
    aucune prose écrite.** Elle ne montre que ce qui se dérive de la base, plus
    les accroches vers les dossiers de substance. `redaction` et `proposee`
    sont donc ignorés — les paramètres restent pour ne pas casser l'atelier et
    les appelants, mais rien n'en sort.

    Le motif est d'échelle, et il vaut d'être gardé : à deux départements,
    88 propositions attendaient une relecture et un département de plus en
    ajoutait environ 350. Une prose par commune ne se relit pas à cette
    cadence — elle se valide en lot, c'est-à-dire qu'elle ne se relit plus.
    Le raisonnement a changé d'étage : il est écrit UNE fois par substance,
    relu une fois, et chaque fiche concernée y renvoie par une accroche
    fabriquée à partir de ses propres chiffres (cf. `sortie/dossier_page.py`).

    Conséquence directe sur ce qui suit : plus de fusion, plus de préséance,
    plus d'origines à afficher — tout ce qui est écrit ici vient d'une requête,
    et c'est vrai de la première ligne à la dernière.
    """
    a = dict(zip(cols, ligne))

    # Rattachement : c'est la commune ÉTUDIÉE qui donne son nom à la fiche,
    # et le lieu réel du prélèvement est dit, jamais tu.
    emprunt = None
    if rattachement:
        emprunt = rattachement["commune_prelevement"]
        a = dict(a, commune=rattachement["commune"],
                 code_insee=rattachement["code_insee"],
                 dept=rattachement["dept"] or a["dept"],
                 codes_postaux=rattachement["codes_postaux"],
                 lon=rattachement["lon"], lat=rattachement["lat"])

    # Uniquement le dérivé. `fusionner` reste dans ce module pour l'atelier,
    # qui sert encore à relire d'anciennes propositions.
    r, origines = rediger.rediger(con, a, version), {}

    niv = niveau(a["nb_depasse_applicable"], a["nb_bascules"], a["nb_indetermines"],
                 a["nb_depasse_limite"])
    natures = IND.natures_du_bulletin(con, a, version)
    panel = (f"{a['nb_parametres']} paramètres · {a['classe_effort']}"
             + (" · complet" if a["est_complet"] else " · INCOMPLET"))

    kpi = [
        {"val": f"{a['nb_parametres']} paramètres",
         "note": f"{a['classe_effort']} · dont {a['nb_synthese_recherchees']} de synthèse",
         "level": "vert" if a["est_complet"] else "ambre"},
        {"val": f"{a['nb_mesures_notees']} notés sur {a['nb_mesures_lues']}",
         "note": f"{_nb(a['pct_couverture'])} % · {a['nb_sans_seuil']} sans seuil de comparaison",
         "level": "vert" if (a["pct_couverture"] or 0) >= 80 else "ambre"},
        {"val": str(a["nb_depasse_applicable"]),
         "note": f"{_nb(a['depassements_pour_mille'])} pour mille paramètres notés",
         "level": "rouge" if a["nb_depasse_applicable"] else "vert"},
        {"val": str(a["nb_bascules"]),
         "note": (f"dont {a['nb_bascules_datees']} datée(s)" if a["nb_bascules"]
                  else "aucune limite déplacée en jeu"),
         "level": "ambre" if a["nb_bascules"] else "vert"},
        {"val": str(a["nb_synthese_quantifiees"]),
         "note": (f"charge cumulée ≥ {_nb(round(a['charge_synthese_ug_l'], 4))} µg/L"
                  if a["charge_synthese_ug_l"] else "aucune quantifiée"),
         "level": "ambre" if (a["nb_synthese_quantifiees"] or 0) > 3 else "vert"},
        {"val": (_nb(round(a["indice_danger"], 2)) if a["indice_danger"] is not None else "—"),
         "note": f"sur {a['indice_danger_n']} substances · raisonnement, pas mesure",
         "level": "rouge" if (a["indice_danger"] or 0) > 1 else "vert"},
    ]

    axes = [[nom, *_conformite(code)] for nom, code in (
        ("Bactériologie", a["conf_limites_bact"]),
        ("Limites de qualité (santé)", a["conf_limites_pc"]),
        ("Références de qualité", a["conf_references_pc"]))]

    manque = ("Aucune lecture n'est disponible pour ce champ. Les chiffres de cette "
              "fiche restent entièrement consultables et vérifiables.")

    # L'origine de chaque section d'analyse. Elle suit celle du champ dont la
    # section provient, sauf si la section porte la sienne — un texte de
    # Yannick peut voisiner avec un paragraphe dérivé sans qu'on les confonde.
    origine_analyse = origines.get("analyse", "derive")
    analyse = [dict(s, o=s.get("o", origine_analyse)) for s in (r.get("analyse") or [])]

    return {
        "name": a["commune"],
        "insee": a["code_insee"],
        # L'en-tête, composé en Python pour CE prélèvement. Il est rendu tel
        # quel dans le fichier pour le prélèvement affiché, et `fiche.js` va
        # rechercher celui-ci quand le lecteur change de date : une seule
        # plume, deux endroits où elle se pose.
        "tete": tete_donnees(a, natures, nom_dept, emprunt),
        # Le point d'eau qui a produit CE bulletin. Il ne suffit pas qu'il
        # descende dans les métadonnées : c'est lui qui étiquette le sélecteur
        # de bulletins, sans quoi une commune alimentée par plusieurs captages
        # aligne des dizaines de boutons indiscernables et se lit comme si elle
        # n'avait qu'une eau (§8bis n° 5). Les Arcs (83004), 15 août 2026 :
        # Sainte Cécile tourne autour de 300 mg/L de sulfates, Les Cambres
        # autour de 150 — deux eaux, et un seul libellé pour les 33 bulletins.
        "pt": a["nom_installation_amont"] or "",
        # Le sous-titre nomme le RÉSEAU, pas le gestionnaire. Corrigé le 13 août
        # 2026, sur décision de Yannick : il écrivait « eau du réseau
        # <nom_uge> », or `nom_uge` est l'exploitant. Un habitant de Baziège
        # lisait « eau du réseau SICOVAL AEP » alors qu'il est sur SICOVAL
        # MONTAGNE NOIRE, et rien sur la fiche ne le lui apprenait. La phrase
        # était sur 2 829 fiches. Le gestionnaire n'est pas perdu — il descend
        # dans les métadonnées, à sa place et sous son vrai nom.
        "sub": ((f"{a['dept']} · réseau {a['noms_reseaux'] or a['nom_uge'] or ''}, "
                 f"analyse prélevée à {emprunt}") if emprunt
                else (r.get("sous_titre")
                      or f"{a['dept']} · {a['noms_reseaux'] or a['nom_uge'] or ''}")),
        "dot": niv,
        "kpi": kpi,
        "meta": [
            ["Réseau de distribution", a["noms_reseaux"] or "—"],
            ["Gestionnaire", a["nom_uge"] or "—"],
            ["Distributeur", a["nom_distributeur"] or "—"],
            ["Ressource", a["nom_installation_amont"] or "—"],
            ["Prélèvement", _date_fr(a["date_prelevement"])
             + (f" · prélevé à {emprunt}" if emprunt else "")],
            ["Panel", panel],
        ],
        "hubeau": f"?code_commune={a['code_insee']}&size=5000",
        # Traçabilité (§8bis obligation 9) : l'appel Hub'Eau réellement passé
        # pour obtenir CE bulletin, pas une requête reconstituée.
        "src": a["source_url"] or "",
        "date": _date_fr(a["date_prelevement"]),
        "date_iso": str(a["date_prelevement"]),
        "date_courte": "/".join(reversed(str(a["date_prelevement"])[:10].split("-"))),
        "dept": a["dept"],
        "complet": bool(a["est_complet"]),
        "nb_indetermines": a["nb_indetermines"],
        "official": {"concl": a["conclusion_conformite"] or "—", "axes": axes},
        # Le niveau de la lecture administrative suit la conclusion RENDUE par
        # l'ARS, pas la nôtre : c'est le point de comparaison, il ne doit pas
        # être coloré par notre propre verdict.
        # La lecture administrative n'a jamais été dérivable : elle disait, en
        # prose, ce que la conclusion de l'ARS énonce déjà juste au-dessus.
        # Sans prose écrite, ce champ reste vide et le gabarit le masque —
        # plutôt qu'afficher « aucune lecture disponible » sur 678 fiches, ce
        # qui laisserait croire à un contenu manquant alors qu'il n'y en a pas.
        "admin": {"level": _conformite(a["conf_limites_pc"])[1],
                  "v": _extrait(a["conclusion_conformite"]),
                  "d": r.get("lecture_administrative") or "",
                  "o": None},
        "delta": r.get("delta") or "",
        # Le résumé citoyen dit ce qui a été franchi, pas seulement combien de
        # fois. « 12 dépassements » quand aucun ne porte sur une limite de
        # qualité contredit la conclusion de l'ARS sur le même bulletin.
        "cit": {"level": niv,
                "v": _resume_depassements(natures),
                "d": r.get("lecture_citoyenne") or manque,
                "o": None},
        # Les indicateurs, groupés : ce qu'on a trouvé / quelle eau c'est /
        # ce que vaut cette lecture. L'ordre et le contenu viennent du fichier
        # versionné referentiel/indicateurs.csv, pas de ce code.
        "natures": natures,
        "ind": IND.calculer(con, a, version),
        "groupes": [[c, t, s] for c, t, s in IND.GROUPES],
        # Les trois lectures qui ne tiennent pas dans une tuile.
        "pfas": IND.pfas_par_chaine(con, a, version),
        "nourrissons": IND.reperes_nourrissons(con, a, version),
        # Les paramètres SANS limite de qualité qui sortent de leur référence
        # déclarée — dans les deux sens. Ce ne sont pas des non-conformités, et
        # le bloc le dit ; le sens « en dessous » est celui de l'eau agressive.
        "references": IND.hors_references(con, a, version),
        "pe": IND.perturbateurs(con, a, version),
        # L'alerte « analyse complète ancienne » — texte composé en Python et
        # non dans le navigateur, pour qu'il soit relisible par le contrôle des
        # sorties. Absente quand la dernière analyse complète a moins de deux
        # ans, ou quand on ne sait pas combien de contrôles ont eu lieu depuis :
        # l'ancienneté seule se lirait comme un abandon de surveillance.
        "alerte_panel": SP.alerte(a["code_insee"]),
        # Ce que le laboratoire ne pouvait pas voir : la mention au paramètre,
        # le taux au bulletin, et le barème qui situe cette LQ dans le corpus
        # (chantier C4). Absent quand le bulletin n'a aucun paramètre aveugle.
        "plafond": IND.plafond_analytique(con, a, version),
        "danger": {"total": a["indice_danger"], "n": a["indice_danger_n"],
                   "parts": IND.decomposition_danger(con, a, version)},
        # Le bandeau de tête : les mesures qui portent la thèse.
        "hero": {
            "niveau": niv,
            "bascules": [{"p": b[0], "v": _nb(b[1]), "u": b[2] or "",
                          "s16": _nb(b[3]), "s": _nb(b[4]), "datee": bool(b[5]),
                          "ds": (accroches or {}).get(b[0])}
                         for b in IND.bascules_en_tete(con, a, version)],
            # Le dépassement porte lui aussi sa jauge : voir de combien une
            # mesure franchit son seuil, et où se situait celui de 2016, est
            # aussi parlant que pour une bascule — souvent davantage.
            "depassements": [{"p": d[0], "v": _nb(d[1]), "u": d[2] or "",
                              "s": _nb(d[3]), "g": d[4],
                              "s16": _nb(d[5]) if d[5] is not None else None,
                              # La nature de ce qui est franchi : une limite
                              # sanitaire et une valeur indicative ne se
                              # peignent pas de la même couleur.
                              "nat": d[6],
                              # L'accroche vers le dossier de la substance,
                              # quand il en existe un : deux phrases fabriquées
                              # à partir des chiffres de CE bulletin, et un
                              # lien. Le raisonnement, lui, n'est écrit qu'une
                              # fois — il ne se recopie pas dans chaque fiche.
                              "ds": (accroches or {}).get(d[0])}
                             for d in IND.depassements_en_tete(con, a, version)],
            "natures": IND.natures_du_bulletin(con, a, version),
            "nb_bascules": a["nb_bascules"],
            "nb_depassements": a["nb_depasse_applicable"],
            "nb_indetermines": a["nb_indetermines"],
            # Un bandeau qui annonce « aucun dépassement » alors qu'une part de
            # l'analyse ne pouvait pas conclure est la demi-vérité que le
            # projet dénonce. Le bandeau le dit donc lui-même (chantier C4).
            "nb_aveugles": a["nb_aveugles"],
            "aveugles_pour_mille": a["aveugles_pour_mille"],
        },
        "analyse": analyse,
        "verdict": {"level": niv, "t": r.get("verdict") or manque,
                    "o": origines.get("verdict")},
        # Ce que le lecteur doit pouvoir savoir : d'où vient chaque phrase.
        # Plus d'origines à afficher : tout vient d'une requête. Les clés
        # restent, vides, pour que le gabarit n'ait pas à tester leur existence.
        "origines": {},
        "libelles_origine": {},
        "redige": origines.get("analyse") == "auteur",
        "rattachee": bool(emprunt),
        "commune_prelevement": emprunt,
        "version_referentiel": a["version_referentiel"],
        "calcule_le": str(a["calcule_le"]),
    }


def bloc_parametres(con, code_prel, version):
    """
    Trois états par ligne, jamais deux (CLAUDE.md §2.4 et §8bis obligation 3) :

      x  dépassement   — quantifié, au-dessus du seuil applicable à la date ;
      i  indéterminé   — soit la LQ du laboratoire est au-dessus du seuil
                         strict, soit le seuil dépend d'une condition
                         (ressource, procédé) que la base ne connaît pas ;
      a  aveugle       — la LQ du laboratoire est au-dessus de la limite
                         RÉGLEMENTAIRE elle-même : sous cette valeur l'analyse
                         ne voit rien, là précisément où la conformité se joue
                         (§8bis obligation 11). C'est le cas le plus fort du
                         troisième état, et il porte sa mention chiffrée ;
      d  quantifié     — la substance a été détectée et mesurée.

    Un « indéterminé » n'est pas un « conforme ». Il porte sa propre couleur.
    """
    lignes = []
    for (lib, num, lq, quant, unite, seuil, depasse, fiab, grille,
         s2016, s2026, bascule, bascule_d, ind_strict, ind_cond,
         lq_aveugle, lq_rapport) in parametres(con, code_prel, version):
        lignes.append({
            "p": lib,
            "v": fmt_val(num, lq, quant, unite),
            "s": fmt_seuil(seuil, unite),
            "d": bool(quant),
            "x": bool(depasse),
            "i": bool(ind_strict or ind_cond or lq_aveugle),
            # LE PLAFOND ANALYTIQUE (chantier C4). Distinct de « i » : ici la LQ
            # dépasse la limite RÉGLEMENTAIRE, pas seulement le repère le plus
            # strict. La ligne porte donc sa mention chiffrée, et elle est le
            # seul « non quantifié » qu'il serait faux de lire comme rassurant.
            "a4": bool(lq_aveugle),
            "lqr": (round(lq_rapport, 1) if lq_rapport and lq_rapport < 10
                    else (round(lq_rapport) if lq_rapport else None)),
            "b": bool(bascule),
            "g": grille,
            # Signalée telle quelle : une valeur non confirmée sur source
            # primaire ne doit pas circuler avec l'apparence du vérifié (§2.7).
            "a": bool(fiab and fiab != "verifie"),
            # Ce que la ligne serait devenue sous l'autre grille : c'est la
            # bascule rendue lisible au niveau du paramètre.
            "s16": fmt_seuil(s2016, unite) if bascule else None,
        })
    return {"count": len(lignes), "params": lignes}


# ---------------------------------------------------------------------------
# Encodage des données de la page.
#
# Mesuré le 10 août 2026 sur les 678 fiches communes, sur la forme précédente
# — un objet complet par paramètre et par instantané, tout écrit en clair.
#
#   PARAMS, le détail paramètre par paramètre :
#     34,3 % du poids   les noms de champs JSON ("p":, "v":, "lqr"…), soit
#                       douze chaînes courtes répétées 1,4 million de fois ;
#     10,5 %            les noms de paramètres, 706 valeurs uniques pour
#                       25 905 occurrences sur une SEULE fiche ;
#      9,1 %            les seuils, même phénomène.
#
#   C, le bloc des indicateurs et de la prose (59,3 Mo cumulés) :
#     70,9 %            les scalaires, 38 228 valeurs distinctes pour
#                       1,72 million d'occurrences — les explications longues
#                       sont réécrites à l'identique à chaque instantané ;
#     28,1 %            les noms de champs, 1,73 million d'occurrences pour
#                       708 combinaisons de clés distinctes seulement.
#
# D'où trois transformations, sans perte et sans changement d'affichage :
#
#   DICTIONNAIRE  tout scalaire (chaîne, nombre, booléen) est remplacé par son
#                 rang dans une table déposée une fois par page, PARTAGÉE entre
#                 C et PARAMS — un seuil comme « ≤ 0,1 µg/L » vit dans les deux.
#                 L'indice 0 est réservé à `null` : un état à part, jamais une
#                 chaîne vide (§2.4, trois états et pas deux).
#   COLONNES      pour PARAMS, qui est une table régulière : une liste par champ
#                 au lieu d'un objet par ligne.
#   FORMES        pour C, qui ne l'est pas : chaque objet devient un tableau
#                 précédé du rang de sa combinaison de clés. Les noms de champs
#                 sont écrits une fois pour la page, plus une fois par forme.
#
# Le dictionnaire reste PAR PAGE et non global au site : une fiche continue à
# se lire seule, hors ligne, sans dépendre d'un fichier tiers. C'est ce qui la
# rend citable telle quelle.
#
# Les décodeurs vivent dans site/gabarits/fiche.js et rendent des objets
# identiques à ceux d'avant : rien d'autre dans le rendu n'a eu à changer.
# ---------------------------------------------------------------------------

# Rares, donc stockés en liste des rangs où le drapeau est vrai plutôt qu'en
# un booléen par ligne : « d » est vrai 6,7 % du temps, les autres moins.
DRAPEAUX = ("d", "x", "i", "a4", "b", "a")

# Denses (presque toujours renseignés) : une colonne pleine d'indices.
CHAINES_DENSES = ("p", "v", "s", "g")


class Dictionnaire:
    """Table des scalaires de la page. Un seul exemplaire, partagé.

    La clé de déduplication porte le TYPE en plus de la valeur : en Python
    `True == 1` et `hash(True) == hash(1)`, si bien qu'un dictionnaire naïf
    rendrait `true` là où `1` était attendu. Le bogue serait silencieux et
    n'apparaîtrait qu'à l'affichage.
    """

    def __init__(self):
        self.valeurs = []
        self._rangs = {}

    def idx(self, v):
        """Rang 1-based dans la table. 0 est réservé à `null`."""
        if v is None:
            return 0
        cle = (type(v), v)
        rang = self._rangs.get(cle)
        if rang is None:
            self.valeurs.append(v)
            rang = self._rangs[cle] = len(self.valeurs)
        return rang


def encoder_params(params_par_cle, dico):
    """{clé: bloc_parametres()} → colonnes. Alimente `dico` au passage."""
    cols = {}
    for cle, bloc in params_par_cle.items():
        lignes = bloc["params"]
        c = {"n": bloc["count"]}
        for champ in CHAINES_DENSES:
            c[champ] = [dico.idx(l[champ]) for l in lignes]
        for champ in DRAPEAUX:
            c[champ] = [k for k, l in enumerate(lignes) if l[champ]]
        # Creux : renseignés seulement sur bascule, ou quand la LQ est au-dessus
        # de la limite. Une paire [rang, valeur] par ligne concernée.
        c["s16"] = [[k, dico.idx(l["s16"])] for k, l in enumerate(lignes)
                    if l["s16"] is not None]
        c["lqr"] = [[k, dico.idx(l["lqr"])] for k, l in enumerate(lignes)
                    if l["lqr"] is not None]
        cols[cle] = c
    return cols


def encoder_arbre(v, dico, formes, rangs_formes):
    """Encodage générique d'une structure hétérogène (le bloc C).

    Trois cas, distinguables sans ambiguïté au décodage :

      scalaire  → un entier POSITIF OU NUL, rang dans le dictionnaire ;
      liste     → un tableau dont le premier élément n'est jamais un entier
                  négatif (ses éléments sont eux-mêmes des encodages) ;
      objet     → un tableau dont le premier élément EST un entier négatif,
                  `-(1 + rang de la forme)`, suivi des valeurs dans l'ordre
                  des clés de cette forme.

    Le signe suffit donc à trancher, et les deux cas limites tiennent : une
    liste vide reste `[]`, un objet sans champ devient `[-n]`.
    """
    if isinstance(v, dict):
        forme = tuple(v)
        rang = rangs_formes.get(forme)
        if rang is None:
            formes.append(list(forme))
            rang = rangs_formes[forme] = len(formes)
        return [-rang] + [encoder_arbre(x, dico, formes, rangs_formes)
                          for x in v.values()]
    if isinstance(v, list):
        return [encoder_arbre(x, dico, formes, rangs_formes) for x in v]
    return dico.idx(v)


def decoder_arbre(v, dico, formes):
    """Inverse exact d'`encoder_arbre`. Rend la structure d'origine.

    Existe pour que ce qui RELIT une page publiée — `tests/test_sorties.py` en
    premier — n'ait pas à connaître le format d'encodage. Une seconde
    implémentation du décodage divergerait à la première retouche, et le
    contrôle qui s'appuierait dessus deviendrait muet sans le dire. C'est
    exactement ce qui est arrivé le 13 août 2026 : l'encodage a supprimé
    `const C={…}` des pages, le motif du test ne correspondait plus, et les
    contrôles de prescription (§2.2) et de comparaison anonyme (§2.11) ont
    passé au vert sur zéro texte pendant une journée.
    """
    if isinstance(v, list):
        if v and isinstance(v[0], int) and v[0] < 0:
            noms = formes[-v[0] - 1]
            return {n: decoder_arbre(v[i + 1], dico, formes)
                    for i, n in enumerate(noms)}
        return [decoder_arbre(x, dico, formes) for x in v]
    return None if v == 0 else dico[v - 1]


def lire_commune_dans_page(html):
    """Le bloc C d'une page publiée, quel que soit son format.

    Rend `None` — et non un dictionnaire vide — si la page ne porte aucun bloc
    reconnaissable : l'appelant doit pouvoir distinguer « pas de prose » de
    « format non reconnu ».
    """
    m = re.search(r"const CENC=(.*?);\nconst PCOLS", html, re.S)
    if m:
        dico = json.loads(re.search(r"const DICT=(\[.*?\]);\n", html, re.S).group(1))
        formes = json.loads(re.search(r"const CFORM=(\[.*?\]);\n", html, re.S).group(1))
        return decoder_arbre(json.loads(m.group(1)), dico, formes)
    # Format antérieur au 13 août 2026, conservé pour relire une page ancienne.
    m = re.search(r"const C=(\{.*?\});\nconst PARAMS", html, re.S)
    return json.loads(m.group(1)) if m else None


def js_donnees(commune_par_cle, params_par_cle):
    """Le fragment JavaScript à déposer dans la page.

    Un seul producteur pour les deux sorties — la fiche autonome et la vitrine
    — afin qu'elles ne puissent pas diverger sur le format.
    """
    dico = Dictionnaire()
    formes, rangs_formes = [], {}
    # C d'abord : ses chaînes sont les plus longues, donc les mieux amorties.
    cenc = encoder_arbre(commune_par_cle, dico, formes, rangs_formes)
    pcols = encoder_params(params_par_cle, dico)
    compact = lambda x: json.dumps(x, ensure_ascii=False,  # noqa: E731
                                   separators=(",", ":"))
    return (f"const DICT={compact(dico.valeurs)};\n"
            f"const CFORM={compact(formes)};\n"
            f"const CENC={compact(cenc)};\n"
            f"const PCOLS={compact(pcols)};")


# ---------------------------------------------------------------------------
def construire(insees=None, destination=None, historique=False, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : python3 src/build_db.py "
              "puis python3 src/observer.py <code postal>")
        sys.exit(1)

    con = duckdb.connect(db, read_only=True)
    try:
        version, _ = version_a_publier(con)
        if not version:
            print("aucune analyse figée en base — lance d'abord src/observer.py")
            sys.exit(1)

        lignes, cols = analyses(con, version, insees, historique)
        if not lignes:
            print(f"aucune analyse figée pour cette sélection (version {version})")
            sys.exit(1)

        rattachees = rattachements(con, version, insees)
        empruntes = {r["code_prelevement"] for r in rattachees.values()}

        # `A` garde la ligne brute de chaque bulletin : les sections rendues en
        # Python la lisent (dénominateurs, décomptes), et elle n'est pas dans
        # le dictionnaire d'affichage.
        C, PARAMS, ORDER, A = {}, {}, [], {}
        for ligne in lignes:
            a = dict(zip(cols, ligne))
            # Un bulletin emprunté par une commune voisine n'apparaît pas
            # deux fois : il porte le nom de la commune qui l'a demandé.
            if a["code_prelevement"] in empruntes and a["code_insee"] not in (insees or []):
                continue
            # La clé est le code de prélèvement, jamais la date (§2.3) : une
            # commune a souvent plusieurs prélèvements le même jour sur des
            # points d'eau différents. Aux Arcs, le 1er mars 2024, Les Cambres
            # et Sainte Cécile sont tous deux prélevés — la clé datée écrasait
            # l'un des deux et le faisait disparaître de la fiche.
            cle = a["code_prelevement"]
            d_iso = str(a["date_prelevement"])
            C[cle] = bloc_commune(con, ligne, cols, None, version)
            A[cle] = a
            PARAMS[cle] = bloc_parametres(con, a["code_prelevement"], version)
            ORDER.append(cle)

        for insee, rat in rattachees.items():
            ligne = con.execute(f"""
                SELECT a.*, p.conf_limites_bact, p.conf_limites_pc,
                       p.conf_references_pc, p.nom_distributeur,
                       a.nb_mesures_lues - a.nb_mesures_notees AS nb_sans_seuil
                FROM analyses_figees a
                JOIN prelevements p ON p.code_prelevement = a.code_prelevement
                WHERE a.version_referentiel = ? AND a.code_prelevement = ?
            """, [version, rat["code_prelevement"]]).fetchone()
            if not ligne:
                continue
            cle = f"{insee}-rattachee"
            C[cle] = bloc_commune(con, ligne, cols, None, version,
                                  rattachement=rat)
            A[cle] = dict(zip(cols, ligne))
            PARAMS[cle] = bloc_parametres(con, rat["code_prelevement"], version)
            ORDER.append(cle)

        sans_bulletin = non_documentees(con, version, insees)
    finally:
        con.close()

    # Style, corps et rendu viennent de site/gabarits/ : la fiche autonome et la
    # vitrine partagent la même source et ne peuvent donc pas diverger. Ils sont
    # inlinés ici pour que le fichier produit reste transmissible d'un bloc et
    # consultable sans réseau.
    lire = lambda *p: open(os.path.join(GABARITS, *p), encoding="utf-8").read()  # noqa: E731
    gabarit = open(os.path.join(ICI, "_template.html"), encoding="utf-8").read()
    j = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
    html = (gabarit
            # La feuille v2, et les polices avec elle. La fiche autonome
            # partage `fiche.js` avec la vitrine : elles produisent donc le
            # MÊME balisage, et il leur faut la même feuille. Tant que celle-ci
            # inlinait la v1, tout composant v2 y arrivait sans style — le
            # `.piste` des bascules s'y affichait en trois blocs empilés sans
            # rail ni couleur, alors qu'il était juste sur la vitrine. Le défaut
            # ne se voyait pas en relisant le code : il fallait ouvrir le
            # fichier produit.
            #
            # Les polices sont inlinées en second, avant la feuille, parce
            # qu'un `@font-face` doit précéder ce qui l'emploie. Leurs `url()`
            # restent relatives : dans un fichier transmis seul, la police
            # retombe sur la pile système, et c'est le comportement voulu —
            # `font-display: swap` le prévoit, et embarquer 121 ko de base64
            # dans chaque fiche coûterait plus que ça ne rapporte.
            .replace("/*__CSS__*/",
                     lire("polices.css") + "\n" + lire("observatoire-v2.css"))
            # L'en-tête est rendu ici, pas dans le navigateur — la fiche
            # autonome est justement l'artefact qu'on transmet d'un bloc et
            # qu'on ouvre sans rien d'autre. Le nom du département n'y est pas
            # résolu (`geo_departements()` appartient à la vitrine) : le chapô
            # y porte donc le code, et c'est le seul écart assumé entre les
            # deux artefacts.
            .replace("<!--__TETE__-->",
                     (tete_html(C[ORDER[0]]["tete"],
                                prelevements_html(C, ORDER, ORDER[0]))
                      + alerte_html(C[ORDER[0]])
                      + bascules_html(C[ORDER[0]])
                      + depassements_html(C[ORDER[0]])
                      + lectures_html(C[ORDER[0]], A[ORDER[0]])
                      + indicateurs_html(C[ORDER[0]], A[ORDER[0]])
                      + nourrissons_html(C[ORDER[0]])
                      + pfas_html(C[ORDER[0]]) + registres_html(C[ORDER[0]])
                      + lq_html(C[ORDER[0]]) + barres_html(C[ORDER[0]]))
                     if ORDER else "")
            .replace("<!--__CORPS__-->", lire("corps_fiche.html"))
            .replace("/*__FICHE_JS__*/", lire("fiche.js"))
            .replace("/*__KPI_LABELS__*/", "const KPI_LABELS=" + j(KPI_LABELS) + ";")
            # C et PARAMS partagent un dictionnaire : ils sortent ensemble.
            .replace("/*__C__*/", "")
            .replace("/*__PARAMS__*/", js_donnees(C, PARAMS))
            .replace("/*__ORDER__*/", "const ORDER=" + j(ORDER) + ";"))

    destination = destination or os.path.join(ICI, "Resultat_Analyse_Standardise.html")
    open(destination, "w", encoding="utf-8").write(html)

    print(f"fiche générée : {destination} ({round(len(html)/1024)} Ko)")
    print(f"  {len(C)} bulletin(s), référentiel version {version}")
    for cle, c in C.items():
        print(f"    {c['name']:<24} {PARAMS[cle]['count']:>4} paramètres"
              + (f"   (réseau, prélevé à {c['commune_prelevement']})"
                 if c["rattachee"] else ""))
    if sans_bulletin:
        print(f"  i {len(sans_bulletin)} commune(s) NON DOCUMENTÉE(S), absentes de la fiche :")
        for nom, insee in sans_bulletin:
            print(f"      {nom or insee} — aucun bulletin complet, ni pour la commune "
                  "ni pour son réseau")
        print("    ce n'est ni conforme ni non conforme : c'est une absence de donnée,")
        print("    et elle reste visible dans couverture_communes (ce que colorie la carte).")
    return destination


def main():
    p = argparse.ArgumentParser(description="Fiche citoyenne dérivée de la base")
    p.add_argument("insees", nargs="*", help="codes INSEE à inclure (défaut : tous)")
    p.add_argument("--sortie", help="chemin du fichier HTML produit")
    p.add_argument("--historique", action="store_true",
                   help="inclure tous les bulletins, pas seulement le dernier de chaque point")
    a = p.parse_args()
    construire(insees=a.insees or None, destination=a.sortie,
               historique=a.historique)


if __name__ == "__main__":
    main()

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
import json
import os
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
        bouts.append(f"{n['limite']} limite(s) de qualité")
    if n["reference"]:
        bouts.append(f"{n['reference']} référence(s) de qualité")
    if n["vigilance"]:
        bouts.append(f"{n['vigilance']} valeur(s) de vigilance")
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
                 proposee=None, accroches=None):
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

        C, PARAMS, ORDER = {}, {}, []
        for ligne in lignes:
            a = dict(zip(cols, ligne))
            # Un bulletin emprunté par une commune voisine n'apparaît pas
            # deux fois : il porte le nom de la commune qui l'a demandé.
            if a["code_prelevement"] in empruntes and a["code_insee"] not in (insees or []):
                continue
            cle = f"{a['code_insee']}-{a['date_prelevement']}"
            d_iso = str(a["date_prelevement"])
            C[cle] = bloc_commune(con, ligne, cols, None, version)
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
            .replace("/*__CSS__*/", lire("observatoire.css"))
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

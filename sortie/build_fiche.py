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


def pour_bulletin(prose, insee, date_iso):
    """
    La prose d'un bulletin précis.

    Deux clés possibles, la plus précise l'emporte :
        "28068"              vaut pour tous les bulletins de la commune
        "28068@2026-03-10"   ne vaut que pour ce prélèvement

    Défaut réel, trouvé le 8 août 2026 : la prose n'était indexée que par
    commune. Challet a deux bulletins complets, 2022 et 2026 ; l'analyse écrite
    pour celui de 2026 — « chlorothalonil R471811 à 1,662 µg/L » — s'affichait
    aussi sous les chiffres de 2022, où cette valeur n'existe pas. Un texte qui
    décrit un autre prélèvement que celui qu'il accompagne est exactement le
    genre de dérive que le projet combat ailleurs.
    """
    if not prose:
        return None
    return prose.get(f"{insee}@{date_iso}") or prose.get(insee)


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


def niveau(nb_depassements, nb_bascules, nb_indetermines):
    """Feu de la fiche. Un indéterminé n'est pas un conforme : il colore."""
    if nb_depassements:
        return "rouge"
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
               f.indetermine_strict, f.indetermine_condition
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
                 proposee=None):
    """Une ligne de `analyses_figees` -> le dictionnaire attendu par le gabarit.

    `redaction` est la prose de Yannick, `proposee` celle du modèle ; la part
    dérivable est calculée ici même depuis la base. Les trois sont fusionnées
    champ par champ, et l'origine de chacun est transmise au gabarit.
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

    r, origines = fusionner(redaction, proposee, rediger.rediger(con, a, version))

    niv = niveau(a["nb_depasse_applicable"], a["nb_bascules"], a["nb_indetermines"])
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
        "sub": ((f"{a['dept']} · eau du réseau {a['nom_uge'] or ''}, "
                 f"analyse prélevée à {emprunt}") if emprunt
                else (r.get("sous_titre")
                      or f"{a['dept']} · {a['nom_uge'] or a['noms_reseaux'] or ''}")),
        "dot": niv,
        "kpi": kpi,
        "meta": [
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
        "admin": {"level": _conformite(a["conf_limites_pc"])[1],
                  "v": _extrait(a["conclusion_conformite"]),
                  "d": r.get("lecture_administrative") or manque,
                  "o": origines.get("lecture_administrative")},
        "delta": r.get("delta") or "",
        "cit": {"level": niv,
                "v": (f"{a['nb_depasse_applicable']} dépassement(s) à la date du prélèvement"
                      if a["nb_depasse_applicable"] else "Aucun dépassement à la date"),
                "d": r.get("lecture_citoyenne") or manque,
                "o": origines.get("lecture_citoyenne")},
        # Les indicateurs, groupés : ce qu'on a trouvé / quelle eau c'est /
        # ce que vaut cette lecture. L'ordre et le contenu viennent du fichier
        # versionné referentiel/indicateurs.csv, pas de ce code.
        "ind": IND.calculer(con, a, version),
        "groupes": [[c, t, s] for c, t, s in IND.GROUPES],
        # Les trois lectures qui ne tiennent pas dans une tuile.
        "pfas": IND.pfas_par_chaine(con, a, version),
        "nourrissons": IND.reperes_nourrissons(con, a, version),
        "pe": IND.perturbateurs(con, a, version),
        "danger": {"total": a["indice_danger"], "n": a["indice_danger_n"],
                   "parts": IND.decomposition_danger(con, a, version)},
        # Le bandeau de tête : les mesures qui portent la thèse.
        "hero": {
            "niveau": niv,
            "bascules": [{"p": b[0], "v": _nb(b[1]), "u": b[2] or "",
                          "s16": _nb(b[3]), "s": _nb(b[4]), "datee": bool(b[5])}
                         for b in IND.bascules_en_tete(con, a, version)],
            # Le dépassement porte lui aussi sa jauge : voir de combien une
            # mesure franchit son seuil, et où se situait celui de 2016, est
            # aussi parlant que pour une bascule — souvent davantage.
            "depassements": [{"p": d[0], "v": _nb(d[1]), "u": d[2] or "",
                              "s": _nb(d[3]), "g": d[4],
                              "s16": _nb(d[5]) if d[5] is not None else None}
                             for d in IND.depassements_en_tete(con, a, version)],
            "nb_bascules": a["nb_bascules"],
            "nb_depassements": a["nb_depasse_applicable"],
            "nb_indetermines": a["nb_indetermines"],
        },
        "analyse": analyse,
        "verdict": {"level": niv, "t": r.get("verdict") or manque,
                    "o": origines.get("verdict")},
        # Ce que le lecteur doit pouvoir savoir : d'où vient chaque phrase.
        "origines": origines,
        "libelles_origine": LIBELLE_ORIGINE,
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
      d  quantifié     — la substance a été détectée et mesurée.

    Un « indéterminé » n'est pas un « conforme ». Il porte sa propre couleur.
    """
    lignes = []
    for (lib, num, lq, quant, unite, seuil, depasse, fiab, grille,
         s2016, s2026, bascule, bascule_d, ind_strict, ind_cond) in parametres(
            con, code_prel, version):
        lignes.append({
            "p": lib,
            "v": fmt_val(num, lq, quant, unite),
            "s": fmt_seuil(seuil, unite),
            "d": bool(quant),
            "x": bool(depasse),
            "i": bool(ind_strict or ind_cond),
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
def construire(insees=None, destination=None, historique=False, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : python3 src/build_db.py "
              "puis python3 src/observer.py <code postal>")
        sys.exit(1)

    redactions, proposees = charger_prose()

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
            C[cle] = bloc_commune(
                con, ligne, cols,
                pour_bulletin(redactions, a["code_insee"], d_iso), version,
                proposee=pour_bulletin(proposees, a["code_insee"], d_iso))
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
            C[cle] = bloc_commune(con, ligne, cols, redactions.get(insee),
                                  version, rattachement=rat,
                                  proposee=proposees.get(insee))
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
            .replace("/*__C__*/", "const C=" + j(C) + ";")
            .replace("/*__PARAMS__*/", "const PARAMS=" + j(PARAMS) + ";")
            .replace("/*__ORDER__*/", "const ORDER=" + j(ORDER) + ";"))

    destination = destination or os.path.join(ICI, "Resultat_Analyse_Standardise.html")
    open(destination, "w", encoding="utf-8").write(html)

    print(f"fiche générée : {destination} ({round(len(html)/1024)} Ko)")
    print(f"  {len(C)} bulletin(s), référentiel version {version}")
    for cle, c in C.items():
        natures = sorted(set(c["origines"].values()))
        print(f"    {c['name']:<24} {PARAMS[cle]['count']:>4} paramètres"
              f"   prose : {'+'.join(natures) or 'aucune'}"
              + (f"   (réseau, prélevé à {c['commune_prelevement']})"
                 if c["rattachee"] else ""))
    a_relire = [c["name"] for c in C.values()
                if "propose" in c["origines"].values()]
    if sans_bulletin:
        print(f"  i {len(sans_bulletin)} commune(s) NON DOCUMENTÉE(S), absentes de la fiche :")
        for nom, insee in sans_bulletin:
            print(f"      {nom or insee} — aucun bulletin complet, ni pour la commune "
                  "ni pour son réseau")
        print("    ce n'est ni conforme ni non conforme : c'est une absence de donnée,")
        print("    et elle reste visible dans couverture_communes (ce que colorie la carte).")
    if a_relire:
        print(f"  i {len(a_relire)} commune(s) portent une prose PROPOSÉE, à relire : "
              f"{', '.join(a_relire)}")
        print("    la fiche la signale comme telle. Valider revient à la recopier")
        print("    dans sortie/redactions.json, où elle devient de ta main.")
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

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

from common import DB_PATH  # noqa: E402

REDACTIONS = os.path.join(ICI, "redactions.json")

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
    """
    return con.execute("""
        SELECT m.libelle_parametre, m.resultat_num, m.lq, m.est_quantifie, m.unite,
               f.seuil_2026_effectif, f.depasse_2026, f.fiabilite
        FROM mesures m
        LEFT JOIN verdicts_figes f
               ON f.code_prelevement = m.code_prelevement
              AND f.libelle_parametre = m.libelle_parametre
              AND f.version_referentiel = ?
        WHERE m.code_prelevement = ?
        ORDER BY m.est_quantifie DESC, m.libelle_parametre
    """, [version, code_prel]).fetchall()


def bloc_commune(con, ligne, cols, redaction, version):
    """Une ligne de `analyses_figees` -> le dictionnaire attendu par le gabarit."""
    a = dict(zip(cols, ligne))
    r = redaction or {}

    niv = niveau(a["nb_depasse_applicable"], a["nb_bascules"], a["nb_indetermines"])
    panel = (f"{a['nb_parametres']} paramètres · {a['classe_effort']}"
             + (" · complet" if a["est_complet"] else " · INCOMPLET"))

    kpi = [
        {"val": f"{a['nb_parametres']} paramètres",
         "note": f"{a['classe_effort']} · dont {a['nb_synthese_recherchees']} de synthèse",
         "level": "vert" if a["est_complet"] else "ambre"},
        {"val": f"{a['nb_mesures_notees']} notés",
         "note": f"{a['pct_couverture']} % · {a['nb_sans_seuil']} sans seuil de comparaison",
         "level": "vert" if (a["pct_couverture"] or 0) >= 80 else "ambre"},
        {"val": str(a["nb_depasse_applicable"]),
         "note": f"{a['depassements_pour_mille']} pour mille paramètres notés",
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

    axes = [["Bactériologie", a["conf_limites_bact"] or "—"],
            ["Limites (santé)", a["conf_limites_pc"] or "—"],
            ["Références", a["conf_references_pc"] or "—"]]

    manque = "Analyse éditoriale non rédigée pour cette commune. " \
             "Les chiffres ci-dessus sont dérivés de la base et vérifiables ; " \
             "leur mise en perspective reste à écrire."

    return {
        "name": a["commune"],
        "insee": a["code_insee"],
        "sub": r.get("sous_titre") or f"{a['dept']} · {a['nom_uge'] or a['noms_reseaux'] or ''}",
        "dot": niv,
        "kpi": kpi,
        "meta": [
            ["Distributeur", a["nom_distributeur"] or "—"],
            ["Ressource", a["nom_installation_amont"] or "—"],
            ["Prélèvement", str(a["date_prelevement"])],
            ["Panel", panel],
        ],
        "hubeau": f"?code_commune={a['code_insee']}&size=5000",
        "official": {"concl": a["conclusion_conformite"] or "—", "axes": axes},
        "admin": {"level": "ambre",
                  "v": (a["conclusion_conformite"] or "—")[:70],
                  "d": r.get("lecture_administrative") or manque},
        "delta": r.get("delta") or "",
        "cit": {"level": niv,
                "v": (f"{a['nb_depasse_applicable']} dépassement(s) à la date du prélèvement"
                      if a["nb_depasse_applicable"] else "Aucun dépassement à la date"),
                "d": r.get("lecture_citoyenne") or manque},
        "analyse": r.get("analyse") or [],
        "verdict": {"level": niv, "t": r.get("verdict") or manque},
        "redige": bool(r.get("analyse")),
        "version_referentiel": a["version_referentiel"],
        "calcule_le": str(a["calcule_le"]),
    }


def bloc_parametres(con, code_prel, version):
    lignes = []
    for lib, num, lq, quant, unite, seuil, depasse, fiab in parametres(con, code_prel, version):
        lignes.append({
            "p": lib + (" ⚠" if fiab and fiab != "verifie" else ""),
            "v": fmt_val(num, lq, quant, unite),
            "s": fmt_seuil(seuil, unite),
            "d": bool(quant),
            "x": bool(depasse),
        })
    return {"count": len(lignes), "params": lignes}


# ---------------------------------------------------------------------------
def construire(insees=None, destination=None, historique=False, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : python3 src/build_db.py "
              "puis python3 src/observer.py <code postal>")
        sys.exit(1)

    redactions = {}
    if os.path.exists(REDACTIONS):
        redactions = json.load(open(REDACTIONS, encoding="utf-8"))

    con = duckdb.connect(db, read_only=True)
    try:
        version = con.execute("""
            SELECT version_referentiel FROM analyses_figees
            GROUP BY 1 ORDER BY MAX(calcule_le) DESC LIMIT 1
        """).fetchone()
        if not version:
            print("aucune analyse figée en base — lance d'abord src/observer.py")
            sys.exit(1)
        version = version[0]

        lignes, cols = analyses(con, version, insees, historique)
        if not lignes:
            print(f"aucune analyse figée pour cette sélection (version {version})")
            sys.exit(1)

        C, PARAMS, ORDER = {}, {}, []
        for ligne in lignes:
            a = dict(zip(cols, ligne))
            cle = f"{a['code_insee']}-{a['date_prelevement']}"
            C[cle] = bloc_commune(con, ligne, cols,
                                  redactions.get(a["code_insee"]), version)
            PARAMS[cle] = bloc_parametres(con, a["code_prelevement"], version)
            ORDER.append(cle)
    finally:
        con.close()

    gabarit = open(os.path.join(ICI, "_template.html"), encoding="utf-8").read()
    j = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
    html = (gabarit
            .replace("/*__KPI_LABELS__*/", "const KPI_LABELS=" + j(KPI_LABELS) + ";")
            .replace("/*__C__*/", "const C=" + j(C) + ";")
            .replace("/*__PARAMS__*/", "const PARAMS=" + j(PARAMS) + ";")
            .replace("/*__ORDER__*/", "const ORDER=" + j(ORDER) + ";"))

    destination = destination or os.path.join(ICI, "Resultat_Analyse_Standardise.html")
    open(destination, "w", encoding="utf-8").write(html)

    non_rediges = [c["name"] for c in C.values() if not c["redige"]]
    print(f"fiche générée : {destination} ({round(len(html)/1024)} Ko)")
    print(f"  {len(C)} bulletin(s), référentiel version {version}")
    for cle, c in C.items():
        print(f"    {c['name']:<24} {PARAMS[cle]['count']:>4} paramètres"
              f"   {'rédigée' if c['redige'] else 'FACTUELLE SEULE'}")
    if non_rediges:
        print(f"  i {len(non_rediges)} commune(s) sans rédaction : "
              f"{', '.join(non_rediges)}")
        print("    la fiche l'indique ; elle n'invente pas de commentaire.")
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

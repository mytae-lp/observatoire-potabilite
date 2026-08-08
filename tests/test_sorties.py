# -*- coding: utf-8 -*-
"""
Contrôle des SORTIES publiées, sans réseau.

    python3 tests/test_sorties.py

Les deux autres suites vérifient le moteur ; celle-ci vérifie ce qui sort. Un
verdict juste en base et faux à l'écran reste un verdict faux, et c'est ce
qu'un lecteur voit.

Ce qu'elle contrôle
-------------------
  1. la version publiée est celle que le référentiel produit aujourd'hui ;
  2. chaque compteur de bulletin est d'accord avec son propre détail ;
  3. toute commune couverte a sa page, et tout bulletin figé une commune ;
  4. aucun marqueur de gabarit n'est resté en place ;
  5. la vitrine n'appelle aucune ressource distante ;
  6. **aucune prose générée ne prescrit quoi que ce soit** (CLAUDE.md §2.2) ;
  7. un indéterminé n'est jamais aussi un dépassement.

L'asymétrie du contrôle 6
-------------------------
La prose `derive` et `propose` est produite par la machine : si elle prescrit,
c'est un **échec**, et il doit bloquer. La prose `auteur` est de la main de
Yannick : si elle prescrit, c'est **signalé et non bloquant** — c'est son
texte, et la décision lui revient. Un outil qui censure son auteur ne serait
pas un garde-fou, ce serait une panne.

Suppose que `site/public/` et la fiche autonome ont été construits.
"""
import json
import os
import re
import sys

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, os.path.join(RACINE, "sortie"))

import figer  # noqa: E402
from common import DB_PATH  # noqa: E402

PUBLIC = os.path.join(RACINE, "site", "public")
FICHE = os.path.join(RACINE, "sortie", "Resultat_Analyse_Standardise.html")

# Termes que le projet s'interdit de prononcer autrement que pour dire qu'il ne
# les prononce pas (CLAUDE.md §2.2). La liste est volontairement large : mieux
# vaut un signalement à écarter qu'une prescription qui passe.
PRESCRIPTIONS = ["osmoseur", "charbon actif", "filtration", "filtrer", "filtrez",
                 "purificateur", "adoucisseur", "carafe filtrante",
                 "eau en bouteille", "eau embouteillée", "achetez", "installez",
                 "nous recommandons", "il est conseillé", "privilégiez"]

# Une négation dans les parages retourne le sens : « aucune recommandation de
# filtration n'y figure » est le contraire d'une prescription.
NEGATIONS = ["aucun", "aucune", "jamais", "ne doit", "n'y figure", "sans",
             "interdit", "s'interdit", "ne dit rien", "ne sert à aucune"]

ECHECS, ALERTES = [], []


def ok(cond, msg, bloquant=True):
    print(("  ok   " if cond else ("  ~    " if not bloquant else "  ECHEC ")) + msg)
    if not cond:
        (ECHECS if bloquant else ALERTES).append(msg)


def prescrit(texte):
    """Renvoie les termes prescriptifs employés sans négation alentour."""
    t = texte.lower()
    trouves = []
    for mot in PRESCRIPTIONS:
        for m in re.finditer(re.escape(mot), t):
            contexte = t[max(0, m.start() - 120):m.end() + 60]
            if not any(n in contexte for n in NEGATIONS):
                trouves.append((mot, texte[max(0, m.start() - 80):m.end() + 60].strip()))
    return trouves


def prose_des_pages():
    """(commune, champ, origine, texte) pour toute la prose des pages."""
    dossier = os.path.join(PUBLIC, "commune")
    if not os.path.isdir(dossier):
        return
    for f in sorted(os.listdir(dossier)):
        contenu = open(os.path.join(dossier, f), encoding="utf-8").read()
        m = re.search(r"const C=(\{.*?\});\nconst PARAMS", contenu, re.S)
        if not m:
            continue
        for cle, d in json.loads(m.group(1)).items():
            org = d.get("origines", {})
            for champ in ("sous_titre", "delta", "verdict"):
                v = d.get(champ)
                v = v.get("t") if isinstance(v, dict) else v
                if v:
                    yield d["name"], champ, org.get(champ, "?"), v
            for bloc in ("admin", "cit"):
                if d.get(bloc, {}).get("d"):
                    yield d["name"], bloc, d[bloc].get("o", "?"), d[bloc]["d"]
            for s in d.get("analyse", []):
                yield d["name"], s.get("t", "analyse"), s.get("o", "?"), s.get("x", "")


def main():
    if not os.path.exists(os.path.join(PUBLIC, "index.html")):
        print("vitrine absente — lance d'abord : python3 site/build_site.py")
        sys.exit(1)
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        print("\n1. la version publiée est celle du référentiel actuel")
        attendue = figer.version_referentiel()
        figees = [r[0] for r in con.execute(
            "SELECT DISTINCT version_referentiel FROM analyses_figees").fetchall()]
        ok(attendue in figees, f"le référentiel actuel ({attendue}) est figé")
        for nom, chemin in (("vitrine", os.path.join(PUBLIC, "index.html")),
                            ("fiche autonome", FICHE)):
            if os.path.exists(chemin):
                ok(attendue in open(chemin, encoding="utf-8").read(),
                   f"la {nom} porte cette version")

        print("\n2. chaque compteur est d'accord avec son détail")
        for col, cond in (("nb_depasse_applicable", "depasse_applicable"),
                          ("nb_bascules", "bascule_2016_2026"),
                          ("nb_indetermines", "indetermine_strict")):
            n = con.execute(f"""
                SELECT COUNT(*) FROM analyses_figees a
                WHERE a.version_referentiel = ?
                  AND a.{col} <> (SELECT COUNT(*) FROM verdicts_figes v
                                  WHERE v.code_prelevement = a.code_prelevement
                                    AND v.version_referentiel = a.version_referentiel
                                    AND v.{cond})
            """, [attendue]).fetchone()[0]
            ok(n == 0, f"{col} = son détail partout ({n} écart(s))")

        print("\n3. couverture et pages")
        couvertes = con.execute("""
            SELECT code_insee, statut FROM couverture_communes WHERE version_referentiel = ?
        """, [attendue]).fetchall()
        sans_page = [c for c, s in couvertes if s != "non_documentee"
                     and not os.path.exists(os.path.join(PUBLIC, "commune", f"{c}.html"))]
        ok(not sans_page, f"{len(couvertes)} commune(s) couverte(s), "
                          f"{len(sans_page)} sans page")
        orphelins = con.execute("""
            SELECT COUNT(*) FROM analyses_figees a
            LEFT JOIN couverture_communes c
                   ON c.code_insee = a.code_insee
                  AND c.version_referentiel = a.version_referentiel
            WHERE a.version_referentiel = ? AND c.code_insee IS NULL
        """, [attendue]).fetchone()[0]
        ok(orphelins == 0,
           f"aucun bulletin figé invisible sur la carte ({orphelins})")

        print("\n4. gabarits substitués")
        if os.path.exists(FICHE):
            fiche = open(FICHE, encoding="utf-8").read()
            restes = [m for m in ("/*__CSS__*/", "/*__C__*/", "/*__ORDER__*/",
                                  "<!--__CORPS__-->", "/*__FICHE_JS__*/",
                                  "/*__KPI_LABELS__*/", "/*__PARAMS__*/")
                      if m in fiche]
            ok(not restes, f"aucun marqueur résiduel dans la fiche ({restes})")

        print("\n5. aucune ressource distante")
        pages = [os.path.join(r, f) for r, _, fs in os.walk(PUBLIC)
                 for f in fs if f.endswith(".html")]
        distants = [(os.path.basename(p), u) for p in pages
                    for u in re.findall(r'(?:src|href)="(https?://[^"]+)"',
                                        open(p, encoding="utf-8").read())]
        ok(not distants,
           f"{len(pages)} page(s), {len(distants)} ressource(s) distante(s) {distants[:3]}")

        print("\n6. §2.2 — aucune prescription")
        machine, auteur = [], []
        for commune, champ, origine, texte in prose_des_pages():
            for mot, extrait in prescrit(texte):
                (auteur if origine == "auteur" else machine).append(
                    (commune, champ, origine, mot, extrait))
        ok(not machine,
           f"la prose générée ne prescrit rien ({len(machine)} cas)")
        for c, champ, o, mot, extrait in machine:
            print(f"        {c} · {champ} [{o}] : « …{extrait}… »")
        ok(not auteur,
           f"la prose d'auteur ne prescrit rien ({len(auteur)} cas) — "
           "signalement, la décision revient à l'auteur", bloquant=False)
        for c, champ, o, mot, extrait in auteur:
            print(f"        {c} · {champ} : « …{extrait}… »")

        print("\n7. un indéterminé n'est jamais un dépassement")
        faux = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes
            WHERE version_referentiel = ? AND indetermine_strict AND depasse_applicable
        """, [attendue]).fetchone()[0]
        ok(faux == 0, f"aucun paramètre dans les deux états ({faux})")
    finally:
        con.close()

    print("\n" + "=" * 66)
    if ECHECS:
        print(f"{len(ECHECS)} ÉCHEC(S) :")
        for e in ECHECS:
            print("   -", e)
        sys.exit(1)
    print("sorties conformes : version juste, compteurs d'accord avec leur détail,")
    print("aucune ressource distante, aucune prescription générée")
    if ALERTES:
        print(f"\n{len(ALERTES)} point(s) signalé(s), non bloquants — à relire.")


if __name__ == "__main__":
    main()

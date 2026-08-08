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
  7. un indéterminé n'est jamais aussi un dépassement, et un paramètre déclaré
     hors de portée du laboratoire l'est réellement (chantier C4) ;
  8. **aucune comparaison de territoire ne reste anonyme** (§2.11, chantier C5).

Ce que le contrôle 8 sait faire, et ce qu'il ne sait pas
-------------------------------------------------------
Il repère les désignations qui ne nomment rien — « ailleurs », « le
voisinage », « les grands réseaux », « plusieurs communes » — et vérifie
qu'un nom propre ou le mot « corpus » figure dans la **même phrase**. Il
constate donc qu'une zone est nommée ; il ne peut pas constater que c'est la
bonne, ni que le corpus détient ses bulletins, ni que l'effort de recherche
des deux termes est affiché. Cette relecture-là reste humaine — le contrôle
sert à ce qu'on ne l'oublie pas.

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

# Désignations de territoire qui ne nomment rien (CLAUDE.md §2.11, chantier C5).
# « Mieux que le voisinage » est invérifiable : le lecteur ne peut ni retrouver
# la zone, ni lire son effort de recherche, ni contredire la phrase. Et c'est
# d'autant plus tentant que ça ne demande aucune donnée.
COMPARAISONS_VAGUES = ["ailleurs", "voisinage", "alentours", "aux environs",
                       "les grands réseaux", "les gros réseaux",
                       "d'autres communes", "plusieurs communes",
                       "certaines communes", "les autres communes",
                       "la plupart des communes", "la plupart des réseaux",
                       "la plupart des bulletins", "beaucoup de communes",
                       "d'autres agglomérations", "d'autres territoires",
                       "d'autres secteurs", "d'autres départements",
                       "la moyenne nationale", "au niveau national",
                       "le reste de la France"]

# Emplois de ces mots qui ne sont pas des comparaisons de territoire.
# « prélevée ailleurs » est l'obligation d'affichage n° 5 du §8bis — dire où
# l'analyse a eu lieu quand elle est empruntée au réseau.
IDIOMES = ["par ailleurs", "prélevé ailleurs", "prélevée ailleurs",
           "prélevés ailleurs", "prélevées ailleurs", "analysé ailleurs",
           "analysée ailleurs"]

# Ce qui, dans la même phrase, dit à quelle zone on compare : un nom propre,
# ou le corpus lui-même — un ensemble dont on détient par définition les
# bulletins. Les mots ci-dessous commencent une phrase sans nommer personne.
ANCRES_MOTS = ["corpus", "série"]
FAUX_NOMS_PROPRES = {
    "Le", "La", "Les", "Un", "Une", "Des", "Du", "De", "Ce", "Cette", "Ces",
    "Il", "Elle", "On", "Ils", "Elles", "Sur", "Dans", "Et", "Ou", "Mais",
    "Or", "Donc", "Car", "Ni", "Aucun", "Aucune", "Sans", "Avec", "Pour",
    "Par", "Au", "Aux", "En", "Son", "Sa", "Ses", "Leur", "Leurs", "Deux",
    "Trois", "Quatre", "Cinq", "Six", "Sept", "Huit", "Neuf", "Dix", "Cent",
    "Quand", "Ici", "Rien", "Tout", "Toute", "Toutes", "Tous", "Cela", "Ça",
    "Comparer", "Lire", "Dire", "Écrire", "Trouver", "Chaque", "Plus",
    "Moins", "Autant", "Depuis", "Après", "Avant", "Pendant", "Puis", "Ainsi",
}

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


def _sans_balises(texte):
    return re.sub(r"<[^>]+>", " ", texte).replace("&lt;", "<").replace("&gt;", ">")


def _phrases(texte):
    """Découpe grossière en phrases. Le séparateur décimal est la virgule dans
    cette prose (« 1,662 ») : couper sur « . » suivi d'une espace ne casse
    aucun nombre.

    On ne coupe **pas** sur « : » ni sur « ; ». La zone comparée est très
    souvent nommée avant le deux-points — « Le contraste avec les autres
    communes du corpus est net : ailleurs les perfluorés… » — et couper là
    produirait un signalement sur une phrase qui nomme pourtant sa zone."""
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", _sans_balises(texte))
            if p.strip()]


def _nomme_une_zone(phrase):
    """La phrase désigne-t-elle quelque chose de nommé ?"""
    if any(m in phrase.lower() for m in ANCRES_MOTS):
        return True
    mots = re.findall(r"[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ][\wÀ-ÿ'’-]+", phrase)
    return any(m not in FAUX_NOMS_PROPRES for m in mots[1:] if len(m) > 1)


def comparaison_anonyme(texte):
    """Renvoie les comparaisons de territoire qui ne nomment aucune zone."""
    trouves = []
    for phrase in _phrases(texte):
        bas = phrase.lower()
        for mot in COMPARAISONS_VAGUES:
            for m in re.finditer(re.escape(mot), bas):
                fenetre = bas[max(0, m.start() - 12):m.end() + 12]
                if any(i in fenetre for i in IDIOMES):
                    continue
                if not _nomme_une_zone(phrase):
                    trouves.append((mot, phrase))
                break
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
                          ("nb_indetermines", "indetermine_strict"),
                          # Chantier C4 : le plafond analytique compte à part de
                          # l'indéterminé ordinaire, et son compteur doit lui
                          # aussi être d'accord avec son propre détail.
                          ("nb_aveugles", "lq_aveugle")):
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

        # Chantier C4. Un paramètre aveugle n'est ni quantifié — sinon la
        # question de la LQ ne se pose plus — ni comparé à un seuil de zéro :
        # la limite de qualité de la bactériologie est nulle et la LQ d'un
        # dénombrement vaut 1, ce qui déclarerait aveugle une analyse
        # parfaitement lisible.
        incoherents = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes
            WHERE version_referentiel = ? AND lq_aveugle
              AND (est_quantifie OR depasse_applicable
                   OR seuil_applicable IS NULL OR seuil_applicable <= 0
                   OR lq IS NULL OR lq <= seuil_applicable)
        """, [attendue]).fetchone()[0]
        ok(incoherents == 0,
           f"un paramètre aveugle est non quantifié, sous un seuil non nul, "
           f"et sa LQ dépasse ce seuil ({incoherents} contre-exemple(s))")
        bacterio = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes
            WHERE version_referentiel = ? AND seuil_applicable = 0 AND lq_aveugle
        """, [attendue]).fetchone()[0]
        ok(bacterio == 0,
           f"aucune mesure à seuil nul déclarée aveugle ({bacterio}) — "
           "aucune LQ ne passe sous zéro")

        print("\n8. §2.11 — aucune comparaison de territoire anonyme")
        machine, auteur = [], []
        for commune, champ, origine, texte in prose_des_pages():
            for mot, phrase in comparaison_anonyme(texte):
                (auteur if origine == "auteur" else machine).append(
                    (commune, champ, origine, mot, phrase))
        ok(not machine,
           f"la prose générée ne compare qu'à des zones nommées ({len(machine)} cas)")
        for c, champ, o, mot, phrase in machine:
            print(f"        {c} · {champ} [{o}] : « {phrase} »")
        ok(not auteur,
           f"la prose d'auteur ne compare qu'à des zones nommées ({len(auteur)} cas) — "
           "signalement, la décision revient à l'auteur", bloquant=False)
        for c, champ, o, mot, phrase in auteur:
            print(f"        {c} · {champ} : « {phrase} »")
    finally:
        con.close()

    print("\n" + "=" * 66)
    if ECHECS:
        print(f"{len(ECHECS)} ÉCHEC(S) :")
        for e in ECHECS:
            print("   -", e)
        sys.exit(1)
    print("sorties conformes : version juste, compteurs d'accord avec leur détail,")
    print("aucune ressource distante, aucune prescription générée,")
    print("aucune comparaison de territoire anonyme")
    if ALERTES:
        print(f"\n{len(ALERTES)} point(s) signalé(s), non bloquants — à relire.")


if __name__ == "__main__":
    main()

"""Une substance, une commune, dix ans — une courbe PAR POINT D'EAU.

Matériau d'étude, hors chaîne de publication : écrit dans `data/etudes/`, lu
par personne d'autre que nous. Il sert à décider si l'axe « évolution » mérite
un chantier dans la vitrine.

Ce que cette figure teste, et qui n'est pas acquis
--------------------------------------------------
Le §2.3 interdit le **profil synthétique** — composer une eau à partir de la
dernière valeur connue de chaque paramètre, prise dans des bulletins
différents. Une série d'UN SEUL paramètre dans le temps n'est pas cet objet :
une substance, une unité, plusieurs dates, rien ne s'y compose. Le §2.11
troisième règle (panel constant) ne mord pas non plus tant qu'on n'agrège pas
entre paramètres — elle interdit de comparer deux années sur des listes de
recherche différentes, pas de suivre une substance cherchée les deux années.
La série reste donc à instruire au cas par cas : **si le paramètre n'est pas
cherché sur toute la période, la courbe ment par ses trous**, et le script le
dit au lieu de le masquer.

Trois règles tenues ici
-----------------------
1. **Une courbe par point d'eau, jamais une courbe par commune.** Une commune
   est souvent alimentée par plusieurs captages qui ne donnent pas la même
   eau. Aux Arcs, Sainte Cécile est autour de 300 mg/L de sulfates et Les
   Cambres autour de 150 : une courbe unique alterne entre les deux et fait
   passer un mélange pour une variation. C'est le §7.2 (dilution) appliqué à
   l'affichage.
2. **Zéro n'est pas zéro (§2.4).** Seules les mesures quantifiées font un
   point. Les non quantifiées sont dénombrées sous la figure avec leur LQ,
   jamais tracées à zéro — un « 0 µg/L » posé sur un axe est une valeur
   affirmée, et elle n'a pas été mesurée.
3. **Aucun pourcentage d'évolution.** Un « + X % » entre le premier et le
   dernier point d'une série qui alterne deux captages, ou qui compte des
   points sous LQ, ne mesure rien. Tant qu'aucun estimateur n'est arrêté, la
   figure montre les points et se tait.

Emploi :
    py -X utf8 src/etude_serie.py --insee 83004 --parametre sulfate
"""
import argparse
import os
import sys

import duckdb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DB_PATH  # noqa: E402

SORTIE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "data", "etudes")

# Trois teintes de la famille de marque (charte : --eau-deep, --eau, #4FC3CC).
# Elles identifient un POINT D'EAU et ne portent aucun verdict : la palette de
# verdict — vert conforme, rouge dépassement, violet bascule, gris indéterminé
# — n'est volontairement pas employée ici, pour qu'aucune couleur de série ne
# se lise comme un jugement.
TEINTES = ["#08344C", "#0B6A73", "#4FC3CC", "#5A6E80", "#8E5A0B"]
AMBRE = "#8E5A0B"
ENCRE = "#12242F"
ENCRE_PALE = "#5A6E80"
TRAIT = "#D6DEE4"

L, R, HAUT, BAS = 78, 250, 96, 74      # marges du cadre
LARG, HAUTEUR = 1120, 560


def _echap(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def resoudre(con, insee, motif):
    """Un fragment de libellé → UN paramètre, ou rien.

    Écrit après l'erreur : `--parametre sulfate` attrapait « Sulfates » ET
    « Endosulfan sulfate », un pesticide. Les deux séries se retrouvaient dans
    la même figure, et seule la différence d'unité — mg/L contre µg/L — les a
    séparées. Par chance, pas par méthode : deux paramètres dans la même unité
    auraient été tracés ensemble sous un seul titre. C'est le §2.7 transposé du
    seuil à la série — *la substance d'à côté n'est pas la substance*.

    Le script refuse donc de choisir à notre place : si le fragment désigne
    plusieurs paramètres, il les liste et s'arrête.
    """
    trouves = con.execute("""
        SELECT m.libelle_norm, min(m.libelle_parametre), count(*)
        FROM mesures m
        JOIN prelevements p USING(code_prelevement)
        JOIN analyses_figees a USING(code_prelevement)
        WHERE p.code_insee = ?
          AND lower(m.libelle_norm) LIKE '%' || lower(?) || '%'
        GROUP BY 1 ORDER BY 3 DESC
    """, [insee, motif]).fetchall()
    if not trouves:
        return None
    exact = [t for t in trouves if t[0] == motif.lower().strip()]
    if len(trouves) > 1 and not exact:
        print(f"« {motif} » désigne {len(trouves)} paramètres sur cette "
              f"commune. Précise lequel :")
        for norm, lib, n in trouves:
            print(f"    --parametre \"{norm}\"   ({lib}, {n} mesures)")
        sys.exit(1)
    return (exact or trouves)[0][0]


def lire(con, insee, libelle_norm):
    """Les mesures d'un paramètre sur une commune, bulletins complets figés.

    On reste sur les bulletins figés : c'est la seule matière citable (§8bis),
    et c'est aussi ce qui garantit que chaque point a une date et une grille.
    """
    lignes = con.execute("""
        SELECT p.date_prelevement          AS d,
               p.nom_installation_amont    AS pt,
               m.resultat_num              AS v,
               m.lq                        AS lq,
               m.unite                     AS u,
               m.est_quantifie             AS q,
               m.libelle_parametre         AS lib
        FROM mesures m
        JOIN prelevements p USING(code_prelevement)
        JOIN analyses_figees a USING(code_prelevement)
        WHERE p.code_insee = ?
          AND m.libelle_norm = ?
        ORDER BY p.date_prelevement
    """, [insee, libelle_norm]).fetchall()
    if not lignes:
        return None
    # Une seule unité par figure (§2.9) : celle qui porte les mesures
    # quantifiées. Les lignes dans une autre unité sont écartées et comptées.
    unites = {}
    for _, _, _, _, u, q, _ in lignes:
        if q:
            unites[u] = unites.get(u, 0) + 1
    if not unites:
        return {"vide": True, "lignes": lignes}
    unite = max(unites, key=unites.get)
    return {"vide": False, "unite": unite, "lignes": lignes}


def seuil(con, libelle_norm):
    """Le repère du référentiel pour CE paramètre — jamais celui d'un voisin.

    L'appariement passe par la table d'alias du dépôt, comme `v_mesures_ref` :
    on ne réinvente pas ici une seconde façon de rapprocher un libellé d'une
    ligne de référentiel, deux copies d'une règle divergent à la première
    retouche.
    """
    r = con.execute("""
        SELECT libelle, unite, seuil_2016, seuil_2026, statut_2026,
               sources, fiabilite
        FROM referentiel_seuils
        WHERE libelle_norm = ?
           OR libelle_norm = (SELECT libelle_norm FROM alias_parametres
                              WHERE alias_norm = ?)
        LIMIT 1
    """, [libelle_norm, libelle_norm]).fetchone()
    return dict(zip(["libelle", "unite", "s2016", "s2026", "statut",
                     "sources", "fiabilite"], r)) if r else None


def construire(insee, motif, db=DB_PATH):
    con = duckdb.connect(db, read_only=True)
    try:
        commune = con.execute(
            "SELECT nom, code_departement FROM communes WHERE code_insee = ?",
            [insee]).fetchone()
        if not commune:
            print(f"commune {insee} absente de la base")
            sys.exit(1)
        libelle_norm = resoudre(con, insee, motif)
        if libelle_norm is None:
            print(f"aucune mesure « {motif} » sur {commune[0]}")
            sys.exit(1)
        d = lire(con, insee, libelle_norm)
        if d is None:
            print(f"aucune mesure « {motif} » sur {commune[0]}")
            sys.exit(1)
        if d["vide"]:
            print(f"« {motif} » n'est jamais quantifié sur {commune[0]} : "
                  f"{len(d['lignes'])} mesure(s), toutes sous la limite de "
                  f"quantification. Il n'y a pas de courbe à tracer, et c'est "
                  f"l'information (§2.4).")
            sys.exit(0)
        ref = seuil(con, libelle_norm)
        version = con.execute(
            "SELECT max(version_referentiel) FROM analyses_figees").fetchone()[0]
    finally:
        con.close()

    unite = d["unite"]
    series, hors, sous_lq = {}, 0, []
    libelles = set()
    for date, pt, val, lq, u, q, lib in d["lignes"]:
        if u != unite:
            hors += 1
            continue
        libelles.add(lib)
        if not q or val is None:
            sous_lq.append((date, lq))
            continue
        series.setdefault(pt or "Point d'eau non déclaré", []).append((date, val))

    if not series:
        print("aucun point quantifié dans l'unité retenue")
        sys.exit(0)

    svg = dessiner(series, sous_lq, hors, unite, ref, commune, insee,
                   sorted(libelles), version)
    os.makedirs(SORTIE, exist_ok=True)
    # Le nom du fichier porte le paramètre RÉSOLU, pas le fragment tapé : deux
    # fragments différents pour la même substance doivent écrire le même
    # fichier, et deux substances différentes ne doivent jamais l'écraser.
    slug = "".join(ch if ch.isalnum() else "-" for ch in libelle_norm).strip("-")
    chemin = os.path.join(SORTIE, f"serie-{insee}-{slug}.svg")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"{commune[0]} ({insee}) · {', '.join(sorted(libelles))} · {unite}")
    for pt in sorted(series, key=lambda k: -len(series[k])):
        pts = sorted(series[pt])
        print(f"  {pt:<28} {len(pts):>3} point{'s' if len(pts) > 1 else ' '} · "
              f"{pts[0][0]} {pts[0][1]:g} → {pts[-1][0]} {pts[-1][1]:g}")
    if sous_lq:
        print(f"  {len(sous_lq)} mesure(s) non quantifiée(s), non tracée(s)")
    if hors:
        print(f"  {hors} mesure(s) dans une autre unité, écartée(s) (§2.9)")
    print(f"→ {chemin}")
    return chemin


def dessiner(series, sous_lq, hors, unite, ref, commune, insee, libelles,
             version):
    tous = [v for pts in series.values() for _, v in pts]
    dates = [d for pts in series.values() for d, _ in pts]
    d0, d1 = min(dates), max(dates)
    etendue = max((d1 - d0).days, 1)

    # La référence entre dans l'échelle : une courbe qui la franchit doit se
    # voir la franchir, et une courbe qui reste loin en dessous doit se voir
    # rester loin en dessous.
    val_ref = None
    if ref and ref["unite"] == unite and ref["s2026"] is not None:
        val_ref = float(ref["s2026"])
    hautvals = tous + ([val_ref] if val_ref else [])
    ymax = max(hautvals) * 1.14
    x = lambda dt: L + (dt - d0).days / etendue * (LARG - L - R)   # noqa: E731
    y = lambda v: HAUTEUR - BAS - (v / ymax) * (HAUTEUR - BAS - HAUT)  # noqa: E731

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARG}" '
         f'height="{HAUTEUR}" viewBox="0 0 {LARG} {HAUTEUR}" '
         f'font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif">',
         f'<rect width="{LARG}" height="{HAUTEUR}" fill="#FFFFFF"/>']

    titre = f"{commune[0]} ({insee}) · {' / '.join(libelles)}"
    o.append(f'<text x="{L}" y="40" font-size="21" font-weight="700" '
             f'fill="{ENCRE}">{_echap(titre)}</text>')
    o.append(f'<text x="{L}" y="64" font-size="13" fill="{ENCRE_PALE}">'
             f'Une courbe par point d\'eau — la commune en compte '
             f'{len(series)}. Bulletins complets figés, '
             f'{d0.year}–{d1.year}. Valeurs en {_echap(unite)}.</text>')

    # Graduations horizontales
    pas = 10 ** (len(str(int(ymax))) - 1)
    if ymax / pas < 3:
        pas /= 2
    v = 0
    while v <= ymax:
        yy = y(v)
        o.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{LARG - R}" y2="{yy:.1f}" '
                 f'stroke="{TRAIT}" stroke-width="1"/>')
        o.append(f'<text x="{L - 10}" y="{yy + 4:.1f}" font-size="11" '
                 f'text-anchor="end" fill="{ENCRE_PALE}">{v:g}</text>')
        v += pas

    # Années
    for an in range(d0.year, d1.year + 1):
        import datetime
        dt = datetime.date(an, 1, 1)
        if not (d0 <= dt <= d1):
            continue
        xx = x(dt)
        o.append(f'<line x1="{xx:.1f}" y1="{HAUT}" x2="{xx:.1f}" '
                 f'y2="{HAUTEUR - BAS}" stroke="{TRAIT}" stroke-width="1" '
                 f'stroke-dasharray="2 4"/>')
        o.append(f'<text x="{xx:.1f}" y="{HAUTEUR - BAS + 18}" font-size="11" '
                 f'text-anchor="middle" fill="{ENCRE_PALE}">{an}</text>')

    # La référence de qualité, nommée pour ce qu'elle est (§2.8) : un repère de
    # bon fonctionnement, pas une limite sanitaire opposable.
    if val_ref:
        yy = y(val_ref)
        mot = "limite de qualité" if ref["statut"] == "limite" else \
              "référence de qualité"
        o.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{LARG - R}" y2="{yy:.1f}" '
                 f'stroke="{AMBRE}" stroke-width="1.5" stroke-dasharray="7 5"/>')
        o.append(f'<text x="{LARG - R + 10}" y="{yy + 4:.1f}" font-size="11.5" '
                 f'font-weight="600" fill="{AMBRE}">'
                 f'{ref["s2026"]:g} {_echap(unite)}</text>')
        o.append(f'<text x="{LARG - R + 10}" y="{yy + 20:.1f}" font-size="10.5" '
                 f'fill="{AMBRE}">{mot}</text>')

    # Les séries, la plus fournie d'abord — elle passe dessous.
    ordre = sorted(series, key=lambda k: -len(series[k]))
    etiquettes = []
    for i, pt in enumerate(ordre):
        col = TEINTES[i % len(TEINTES)]
        pts = sorted(series[pt])
        if len(pts) > 1:
            trace = " ".join(f"{x(dd):.1f},{y(vv):.1f}" for dd, vv in pts)
            o.append(f'<polyline points="{trace}" fill="none" stroke="{col}" '
                     f'stroke-width="2.2" stroke-linejoin="round"/>')
        for dd, vv in pts:
            o.append(f'<circle cx="{x(dd):.1f}" cy="{y(vv):.1f}" r="3.6" '
                     f'fill="#FFFFFF" stroke="{col}" stroke-width="2.2"/>')
        dd, vv = pts[-1]
        etiquettes.append({"pt": pt, "col": col, "n": len(pts),
                           "x": x(dd), "y0": y(vv), "y": y(vv), "v": vv})

    # La légende s'ancre au dernier point de chaque courbe — pas de bloc à
    # décoder ailleurs. Deux courbes qui finissent à la même hauteur
    # superposeraient leurs libellés : on écarte verticalement, en gardant
    # l'ordre des courbes, et un filet relie l'étiquette déplacée à son point.
    etiquettes.sort(key=lambda e: e["y0"])
    for i in range(1, len(etiquettes)):
        mini = etiquettes[i - 1]["y"] + 34
        if etiquettes[i]["y"] < mini:
            etiquettes[i]["y"] = mini
    for e in etiquettes:
        xt = min(e["x"] + 9, LARG - 8)
        if abs(e["y"] - e["y0"]) > 3:
            o.append(f'<line x1="{e["x"] + 4:.1f}" y1="{e["y0"]:.1f}" '
                     f'x2="{xt:.1f}" y2="{e["y"] - 12:.1f}" stroke="{e["col"]}" '
                     f'stroke-width="1" opacity=".45"/>')
        o.append(f'<text x="{xt:.1f}" y="{e["y"] - 9:.1f}" font-size="12" '
                 f'font-weight="700" fill="{e["col"]}">{_echap(e["pt"])}</text>')
        o.append(f'<text x="{xt:.1f}" y="{e["y"] + 6:.1f}" font-size="11" '
                 f'fill="{e["col"]}">{e["v"]:g} {_echap(unite)} · {e["n"]} '
                 f'point{"s" if e["n"] > 1 else ""}</text>')

    # Pied : ce que la figure ne montre pas, et contre quoi elle a été faite.
    pied = []
    if sous_lq:
        lqs = sorted({str(l) for _, l in sous_lq if l is not None})
        pied.append(f"{len(sous_lq)} mesure(s) non quantifiée(s), non tracée(s)"
                    + (f" — LQ {', '.join(lqs)} {unite}" if lqs else "")
                    + " : sous la limite de quantification, « 0 » n'est pas une "
                      "valeur mesurée")
    if hors:
        pied.append(f"{hors} mesure(s) dans une autre unité, écartée(s)")
    # Ce que le référentiel dit, ou ne dit pas. L'absence de trait horizontal
    # ne doit jamais se lire « il n'y a rien à dépasser » : elle peut vouloir
    # dire que nous n'avons pas de valeur, ce qui n'est pas la même chose
    # (§2.4, trois états).
    if ref and val_ref:
        mot = ("limite de qualité, opposable" if ref["statut"] == "limite"
               else "référence de qualité — un repère de bon fonctionnement, "
                    "pas une limite sanitaire opposable")
        bouge = ("inchangée depuis 2016"
                 if ref["s2016"] == ref["s2026"]
                 else f"2016 : {ref['s2016']:g} {ref['unite']}")
        pied.append(f"Trait ambré : {ref['libelle']} {ref['s2026']:g} "
                    f"{ref['unite']}, {mot} ({bouge}) — "
                    f"source {ref['sources']}, {ref['fiabilite']}")
    elif ref:
        pied.append(f"Repère {ref['libelle']} {ref['s2026']:g} {ref['unite']} "
                    f"— non tracé : les mesures sont en {unite}, et deux "
                    f"unités différentes ne se comparent pas (§2.9)")
    else:
        pied.append("Aucun repère au référentiel pour ce paramètre : "
                    "l'absence de trait horizontal ne dit pas que la valeur "
                    "est sans limite, elle dit que nous n'en avons pas.")
    pied.append("Aucun pourcentage d'évolution n'est calculé : entre deux "
                "points d'eau différents, il ne mesurerait rien.")
    pied.append(f"Référentiel {version} · Hub'Eau / SISE-Eaux · "
                f"Observatoire de la potabilité réglementaire")
    for i, ligne in enumerate(pied):
        o.append(f'<text x="{L}" y="{HAUTEUR - BAS + 38 + i * 14}" '
                 f'font-size="10.5" fill="{ENCRE_PALE}">{_echap(ligne)}</text>')

    o.append("</svg>")
    return "\n".join(o)


def main():
    p = argparse.ArgumentParser(
        description="Une substance, une commune, une courbe par point d'eau")
    p.add_argument("--insee", required=True, help="code INSEE de la commune")
    p.add_argument("--parametre", required=True,
                   help="fragment du libellé (ex. sulfate, nitrate, plomb)")
    p.add_argument("--db", default=DB_PATH)
    a = p.parse_args()
    construire(a.insee, a.parametre, a.db)


if __name__ == "__main__":
    main()

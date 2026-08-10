# -*- coding: utf-8 -*-
"""
Le dossier de faits du PANEL — ce que le corpus dit de sa propre construction.

Le dossier de substance répond « qu'est-ce que cette substance démontre ? ».
Celui-ci répond à la question d'avant, et elle commande tout le reste :
**qu'est-ce qui fait qu'on cherche une substance, ou qu'on ne la cherche pas ?**

Il existe parce qu'une phrase du projet — « on ne trouve que ce qu'on cherche »
— est vraie dans les deux sens, et que le second est presque toujours oublié :

  · une baisse du nombre de paramètres n'est pas une perte d'information si ce
    qui sort n'était jamais trouvé. Sur le Tarn, les 280 paramètres sortis
    avant 2020 totalisent 2 quantifications sur 124 690 mesures ;
  · mais une substance jamais cherchée quelque part y est un angle mort
    permanent — et si le critère d'entrée au programme est « on a des chances
    d'en trouver », alors ne pas chercher se perpétue tout seul.

Même contrat que `dossier_substance.py` : **tout ce qui est ici vient d'une
requête**, le rédacteur ne peut citer aucun chiffre absent de ce texte, et
`--verifier` le contrôle.

Usage :

    py -X utf8 sortie/dossier_panel.py
    py -X utf8 sortie/dossier_panel.py --verifier
"""

import argparse
import os
import sys

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

import figer  # noqa: E402

DB_PATH = os.path.join(RACINE, "data", "eau.duckdb")
DOSSIERS = os.path.join(RACINE, "data", "dossiers")
FICHIER = "PANEL.md"

# Un département n'entre dans ce dossier que s'il est collecté en ENTIER :
# comparer un département complet à trois bulletins isolés ne mesurerait que
# la collecte (§2.11).
MIN_BULLETINS = 500


def fr(x, n=2):
    if x is None:
        return "—"
    if isinstance(x, int):
        return str(x)
    # `rstrip("0")` sur « 650.000 » rend « 65 » : sans décimale, il mange
    # le nombre. Trouvé le 10 août 2026 sur la médiane du panel.
    s = f"{x:.{n}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return (s or "0").replace(".", ",")


def dossier(con, version):
    d = []
    a = d.append

    depts = [r[0] for r in con.execute("""
        SELECT dept FROM analyses_figees WHERE version_referentiel = ? AND est_complet
        GROUP BY 1 HAVING COUNT(*) >= ? ORDER BY COUNT(*) DESC
    """, [version, MIN_BULLETINS]).fetchall()]
    liste = ", ".join(depts)

    a("# Dossier de faits — le panel d'analyse\n")
    a("**Sujet : ce que le corpus dit de la liste des substances recherchées.** "
      "Pas de la qualité de l'eau — de ce qu'on décide d'en regarder.")
    a("")
    a(f"Départements collectés en entier et retenus ici : **{liste}**. Un "
      "département qui ne compte que quelques bulletins n'y figure pas : "
      "l'écart mesurerait la collecte, pas le programme d'analyse (§2.11).")
    a("")
    # Le dénominateur de chaque département : sans lui, « jamais cherché dans
    # le Tarn » n'a pas d'échelle. La prose l'a réclamé, le contrôle l'a
    # bloquée, et c'est ainsi que le dossier s'étend.
    a("Ce que chacun pèse — **c'est le dénominateur de tout ce qui suit** :")
    for r in con.execute("""
        SELECT dept, COUNT(*), COUNT(DISTINCT code_insee),
               MIN(date_prelevement), MAX(date_prelevement)
        FROM analyses_figees
        WHERE version_referentiel = ? AND est_complet AND dept IN (SELECT UNNEST(?))
        GROUP BY 1 ORDER BY 2 DESC
    """, [version, depts]).fetchall():
        a(f"- **{r[0]}** : {r[1]} bulletins complets, {r[2]} communes, "
          f"du {r[3].strftime('%d/%m/%Y')} au {r[4].strftime('%d/%m/%Y')}")
    a("")
    a("**Trois interdits, à garder sous les yeux :**")
    a("- **aucune cause.** Le corpus donne des dates et des dénombrements. "
      "Pourquoi une substance entre ou sort d'un programme, il ne le dit pas. "
      "Et un texte ne cause jamais ce qui le précède ;")
    a("- **jamais « on cherche moins » ni « on cherche mieux ».** Les deux sont "
      "des jugements. Ce qui se dit, c'est ce qui est sorti, ce qui est entré, "
      "et ce que chacun valait en quantifications ;")
    a("- **une substance non cherchée est un indéterminé** (§2.4), jamais une "
      "absence. Ni pour un habitant, ni pour un département.")

    # ------------------------------------------------------------ la rupture
    a("\n## 1. Le nombre de paramètres, par année et par département\n")
    a("| département | année | bulletins | paramètres (médiane) | mini | maxi |")
    a("|---|---|---|---|---|---|")
    for r in con.execute("""
        SELECT dept, year(date_prelevement), COUNT(*), MEDIAN(nb_parametres),
               MIN(nb_parametres), MAX(nb_parametres)
        FROM analyses_figees
        WHERE version_referentiel = ? AND est_complet AND dept IN (SELECT UNNEST(?))
        GROUP BY 1, 2 ORDER BY 1, 2
    """, [version, depts]).fetchall():
        a(f"| {r[0]} | {r[1]} | {r[2]} | {fr(r[3], 0)} | {r[4]} | {r[5]} |")

    # ------------------------------------------------- ce qui sort, ce qui entre
    a("\n## 2. Ce qui sort, ce qui entre — et ce que chacun valait\n")
    a("Un paramètre « sorti » n'a plus été mesuré après 2019 ; un paramètre "
      "« entré » ne l'a jamais été avant 2020. Le taux est en quantifications "
      "pour mille mesures : **c'est lui qui dit ce que le programme gagne ou "
      "perd, pas le compte de paramètres.**")
    a("")
    a("| département | mouvement | paramètres | mesures | quantifiées | taux ‰ |")
    a("|---|---|---|---|---|---|")
    for dept in depts:
        r = con.execute("""
        WITH p AS (
          SELECT v.libelle_parametre lib,
                 MIN(year(a.date_prelevement)) an_min, MAX(year(a.date_prelevement)) an_max,
                 COUNT(*) n, COUNT(*) FILTER (WHERE v.est_quantifie) q
          FROM verdicts_figes v JOIN analyses_figees a USING (code_prelevement, version_referentiel)
          WHERE v.version_referentiel = ? AND a.dept = ? AND a.est_complet
          GROUP BY 1)
        SELECT COUNT(*) FILTER (WHERE an_max <= 2019), SUM(n) FILTER (WHERE an_max <= 2019),
               SUM(q) FILTER (WHERE an_max <= 2019),
               COUNT(*) FILTER (WHERE an_min >= 2020), SUM(n) FILTER (WHERE an_min >= 2020),
               SUM(q) FILTER (WHERE an_min >= 2020)
        FROM p
        """, [version, dept]).fetchone()
        for etiquette, (np_, nm, nq) in (("sortis avant 2020", r[0:3]),
                                         ("entrés depuis 2020", r[3:6])):
            taux = 1000.0 * (nq or 0) / nm if nm else 0
            a(f"| {dept} | {etiquette} | {np_ or 0} | {nm or 0} | {nq or 0} "
              f"| {fr(taux)} |")

    a("\n### Les entrants les plus souvent trouvés\n")
    a("| substance | première mesure | mesures | quantifiées | part | communes |")
    a("|---|---|---|---|---|---|")
    for r in con.execute("""
    WITH p AS (
      SELECT v.libelle_parametre lib, MIN(a.date_prelevement) d1, COUNT(*) n,
             COUNT(*) FILTER (WHERE v.est_quantifie) q,
             COUNT(DISTINCT a.code_insee) FILTER (WHERE v.est_quantifie) com
      FROM verdicts_figes v JOIN analyses_figees a USING (code_prelevement, version_referentiel)
      WHERE v.version_referentiel = ? GROUP BY 1)
    SELECT lib, d1, n, q, ROUND(100.0 * q / n, 1), com FROM p
    WHERE d1 >= DATE '2020-01-01' AND q >= 20 ORDER BY q DESC LIMIT 10
    """, [version]).fetchall():
        a(f"| {r[0]} | {r[1].strftime('%d/%m/%Y')} | {r[2]} | {r[3]} "
          f"| {fr(r[4], 1)} % | {r[5]} |")

    # ------------------------------------------------------- le panel constant
    a("\n## 3. À panel constant — ce que le corpus ne voit pas bouger\n")
    a("La seule série honnête dans le temps se restreint aux paramètres "
      "cherchés **chaque** année documentée. Comparer deux années sans cette "
      "restriction fait passer une baisse des recherches pour une baisse des "
      "détections (§2.11).")
    a("")
    a("| département | années | paramètres constants | année | quantifiées ‰ |")
    a("|---|---|---|---|---|")
    for r in con.execute("""
        SELECT dept, nb_annees_documentees, nb_panel_constant, annee, quantifiees_pour_mille
        FROM v_serie_panel_constant WHERE dept IN (SELECT UNNEST(?)) ORDER BY dept, annee
    """, [depts]).fetchall():
        a(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {fr(r[4])} |")

    # ------------------------------------------------------------ la disparité
    a("\n## 4. Ce qu'un département cherche et que l'autre ne cherche pas\n")
    if len(depts) >= 2:
        d1, d2 = depts[0], depts[1]
        r = con.execute("""
        WITH p AS (
          SELECT v.libelle_parametre lib, a.dept, COUNT(*) n,
                 COUNT(*) FILTER (WHERE v.est_quantifie) q
          FROM verdicts_figes v JOIN analyses_figees a USING (code_prelevement, version_referentiel)
          WHERE v.version_referentiel = ? AND a.dept IN (?, ?) GROUP BY 1, 2),
        c AS (SELECT lib,
                MAX(n) FILTER (WHERE dept = ?) na, MAX(q) FILTER (WHERE dept = ?) qa,
                MAX(n) FILTER (WHERE dept = ?) nb, MAX(q) FILTER (WHERE dept = ?) qb
              FROM p GROUP BY 1)
        SELECT COUNT(*) FILTER (WHERE na IS NOT NULL AND nb IS NULL),
               COUNT(*) FILTER (WHERE nb IS NOT NULL AND na IS NULL),
               COUNT(*) FILTER (WHERE na IS NOT NULL AND nb IS NOT NULL),
               COUNT(*) FILTER (WHERE nb IS NULL AND qa > 0),
               COUNT(*) FILTER (WHERE na IS NULL AND qb > 0)
        FROM c
        """, [version, d1, d2, d1, d1, d2, d2]).fetchone()
        a(f"- cherchés dans les deux départements : **{r[2]}**")
        a(f"- cherchés dans le {d1} seulement : **{r[0]}**, dont **{r[3]}** y "
          f"sont quantifiés")
        a(f"- cherchés dans le {d2} seulement : **{r[1]}**, dont **{r[4]}** y "
          f"sont quantifiés")
        a("")
        a("**Une substance quantifiée d'un côté et jamais cherchée de l'autre "
          "est un angle mort de programme.** Ce n'est pas un dépassement caché : "
          "c'est une question qui n'est pas posée. Le §2.4 s'applique — "
          "indéterminé, jamais absence.")
        a("")
        a("| substance | quantifications | situation | valeur la plus haute |")
        a("|---|---|---|---|")
        for x in con.execute("""
        WITH p AS (
          SELECT v.libelle_parametre lib, a.dept, COUNT(*) n,
                 COUNT(*) FILTER (WHERE v.est_quantifie) q,
                 MAX(v.resultat_num) FILTER (WHERE v.est_quantifie) maxi
          FROM verdicts_figes v JOIN analyses_figees a USING (code_prelevement, version_referentiel)
          WHERE v.version_referentiel = ? AND a.dept IN (?, ?) GROUP BY 1, 2),
        c AS (SELECT lib,
                MAX(n) FILTER (WHERE dept = ?) na, MAX(q) FILTER (WHERE dept = ?) qa,
                MAX(maxi) FILTER (WHERE dept = ?) ma,
                MAX(n) FILTER (WHERE dept = ?) nb, MAX(q) FILTER (WHERE dept = ?) qb,
                MAX(maxi) FILTER (WHERE dept = ?) mb
              FROM p GROUP BY 1)
        SELECT lib, COALESCE(qa, qb),
               CASE WHEN nb IS NULL THEN ? ELSE ? END, COALESCE(ma, mb)
        FROM c WHERE (nb IS NULL AND qa > 0) OR (na IS NULL AND qb > 0)
        ORDER BY 2 DESC LIMIT 10
        """, [version, d1, d2, d1, d1, d1, d2, d2, d2,
              f"cherché dans le {d1}, pas dans le {d2}",
              f"cherché dans le {d2}, pas dans le {d1}"]).fetchall():
            a(f"| {x[0]} | {x[1]} | {x[2]} | {fr(x[3], 3)} |")
        a("")
        a("**Réserve, et elle est bloquante pour cette section** : cette liste "
          "mélange de vraies absences de programme et de simples variantes de "
          "libellé — un même paramètre écrit autrement d'un département à "
          "l'autre y apparaît à tort. **Chaque ligne doit être vérifiée à la "
          "main avant d'être écrite**, en comparant les codes SANDRE.")

    # ------------------------------------------------- ce que dit le texte
    #
    # Le corpus ne dit pas POURQUOI une substance entre ou sort. Sans ce bloc,
    # le rédacteur n'a rien pour répondre à la question du lecteur — et il
    # l'inventera. Il est donc donné ici, explicitement marqué comme ne venant
    # pas de la base, avec sa réserve de datation.
    a("\n## 4bis. Ce que dit le texte, et qui ne vient pas de la base\n")
    a("**À citer comme un texte, jamais comme une observation du corpus.**")
    a("")
    a("L'instruction n° DGS/EA4/2020/177 du 18 décembre 2020 [REG-05] substitue "
      "au balayage de toutes les molécules analysables une **liste régionale "
      "arrêtée par l'ARS**, ciblée « en fonction de la probabilité de les "
      "retrouver » : usages locaux, ventes, **détections antérieures**, "
      "hiérarchisation SIRIS. Elle porte aussi la règle du métabolite pertinent "
      "par défaut.")
    a("")
    a("**Trois précautions, toutes obligatoires :**")
    a("- **cette instruction est du 18 décembre 2020.** La rupture du Tarn est "
      "datée de janvier 2020, onze mois plus tôt. Elle décrit un mécanisme "
      "cohérent, elle n'est pas la cause établie de ce que montre le §1. "
      "Écrire « compatible avec », jamais « causée par » ;")
    a("- **le critère « probabilité de les retrouver » contient une boucle**, et "
      "c'est un fait de lecture du texte, pas une accusation : si la détection "
      "antérieure est un critère d'entrée, une substance jamais cherchée "
      "quelque part n'y produit aucune détection, donc aucun motif d'y entrer. "
      "Le §4 en donne la trace mesurable ;")
    a("- **qui arbitre, sur quel seuil de probabilité et avec quel budget "
      "d'analyse, le corpus ne le dit pas et le texte lu ici non plus.** Ce "
      "silence se dit.")

    # ------------------------------------------------------------ traçabilité
    a("\n## 5. Traçabilité\n")
    a(f"Version de référentiel : {version}")
    n = con.execute("SELECT COUNT(*) FROM analyses_figees WHERE version_referentiel = ?",
                    [version]).fetchone()[0]
    a(f"Corpus : {n} bulletins complets figés")
    a("Vues utilisées : `analyses_figees`, `verdicts_figes`, `v_serie_panel_constant`.")

    return "\n".join(d) + "\n"


def main():
    p = argparse.ArgumentParser(description="Le dossier de faits du panel d'analyse")
    p.add_argument("--verifier", action="store_true",
                   help="contrôle la prose du panel contre ce dossier")
    p.add_argument("--sortie", help="chemin du fichier produit")
    a = p.parse_args()

    if a.verifier:
        sys.path.insert(0, os.path.join(RACINE, "sortie"))
        import dossier_substance as DS
        b, s, n = DS.verifier([os.path.join(RACINE, "sortie",
                                            "redactions_panel_proposees.json")],
                              dossier_pour=lambda _cle, _v: os.path.join(DOSSIERS, FICHIER))
        print(f"{n} prose(s) contrôlée(s)")
        for x in s:
            print(f"  ~ {x}")
        for x in b:
            print(f"  ! {x}")
        sys.exit(1 if b else 0)

    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        version = figer.version_referentiel()
        texte = dossier(con, version)
    finally:
        con.close()
    os.makedirs(DOSSIERS, exist_ok=True)
    chemin = a.sortie or os.path.join(DOSSIERS, FICHIER)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(texte)
    print(f"dossier écrit : {chemin}")
    print(f"  {len(texte.splitlines())} lignes, version de référentiel {version}")


if __name__ == "__main__":
    main()

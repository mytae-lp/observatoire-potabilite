# -*- coding: utf-8 -*-
"""
Le dossier de faits d'UNE SUBSTANCE, sur tout le corpus.

L'étage au-dessus de la fiche communale. La fiche répond « qu'y a-t-il dans
mon eau ? » ; ce dossier répond « qu'est-ce que cette substance démontre ? ».
Il se rédige UNE fois, se relit UNE fois, et s'accroche ensuite à toutes les
communes où la substance apparaît — c'est ce qui rend la relecture humaine
tenable quand le corpus passe à des centaines de communes.

Même contrat que `sortie/rediger_lot.py`, et pour la même raison :

    tout ce qui est ici vient d'une requête. Le rédacteur ne peut citer aucun
    chiffre absent de ce texte, et le contrôle d'intégration le vérifie
    (`_nombres`). Donc ce qui manque ici ne sera pas écrit — et ce qui est
    faux ici le sera. C'est la seule surface à vérifier.

Trois garde-fous sont imprimés DANS le dossier, parce qu'un rédacteur qui ne
les a pas sous les yeux les enfreint :

  · §2.11 — une substance n'est cherchée que dans les bulletins qui la
    portent. Le dénombrement se donne toujours avec son dénominateur, et la
    date d'entrée au panel est rappelée département par département ;
  · §2.4  — avant cette date, le corpus ne dit RIEN. Ni absence, ni
    apparition : un indéterminé ;
  · §2.1  — le sujet est la norme, jamais l'ARS, le distributeur ou l'exploitant.

Usage :

    py -X utf8 sortie/dossier_substance.py --code 6862
    py -X utf8 sortie/dossier_substance.py --libelle "Chlorothalonil R471811"
    py -X utf8 sortie/dossier_substance.py --liste        # ce qui est éligible
"""

import argparse
import os
import re
import sys
import unicodedata

import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

import figer  # noqa: E402

DB_PATH = os.path.join(RACINE, "data", "eau.duckdb")
DOSSIERS = os.path.join(RACINE, "data", "dossiers")

# Une substance ne mérite un dossier que si elle a de quoi en porter un.
# Seuil bas : c'est un matériau de travail, pas une publication.
MIN_QUANTIFIEES = 20


def slug(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def fr(x, n=3):
    """Un nombre à la française, sans zéros inutiles — 0,9 et non 0.900."""
    if x is None:
        return "—"
    if isinstance(x, int):
        return str(x)
    s = f"{x:.{n}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",") or "0"


def date_fr(d):
    return d.strftime("%d/%m/%Y") if d else "—"


def eligibles(con, version):
    return con.execute("""
        SELECT libelle_parametre, ANY_VALUE(code_parametre) code,
               COUNT(*) n, COUNT(*) FILTER (WHERE est_quantifie) q,
               COUNT(*) FILTER (WHERE bascule_2016_2026) bascules
        FROM verdicts_figes WHERE version_referentiel = ?
        GROUP BY 1 HAVING q >= ? ORDER BY bascules DESC, q DESC
    """, [version, MIN_QUANTIFIEES]).fetchall()


def dossier(con, libelle, version):
    """Le brief factuel d'une substance. Chaque ligne est une requête."""
    d = []
    a = d.append

    ref = con.execute("""
        SELECT libelle, famille, unite, seuil_2016, seuil_2026,
               date_applicabilite_2026, seuil_conditionnel, condition_seuil,
               statut_2026, seuil_strict, base_seuil_strict, sources, fiabilite,
               pe_reglementaire, pe_scientifique, cancerogenicite_circ
        FROM referentiel_seuils r
        WHERE EXISTS (SELECT 1 FROM verdicts_figes v
                      WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
                        AND (v.code_parametre = r.code_parametre
                             OR lower(v.libelle_parametre) = lower(r.libelle)))
    """, [version, libelle]).fetchone()

    ident = con.execute("""
        SELECT ANY_VALUE(code_parametre), ANY_VALUE(code_cas), ANY_VALUE(famille),
               ANY_VALUE(unite), ANY_VALUE(mode_appariement), ANY_VALUE(nature_seuil)
        FROM verdicts_figes WHERE version_referentiel = ? AND libelle_parametre = ?
    """, [version, libelle]).fetchone()

    a("# Dossier de substance\n")
    a(f"Libellé de la source : {libelle}")
    a(f"Code SANDRE : {ident[0] or '—'} · numéro CAS : {ident[1] or '—'} "
      f"· famille : {ident[2] or '—'} · unité : {ident[3] or '—'}")
    a(f"Appariement au référentiel : par {ident[4] or '—'} "
      f"· nature du seuil : {ident[5] or '—'}")
    a("")
    a("**Tu ne sais de cette substance que ce qui suit.** Rien sur sa chimie, "
      "son usage agricole, sa toxicologie ou son histoire réglementaire hors "
      "de ce dossier : ce qui n'y est pas ne s'écrit pas.")

    # ------------------------------------------------------------------ seuil
    a("\n## 1. Le seuil, et sa date\n")
    if ref:
        (rlib, rfam, runite, s16, s26, dapp, scond, cond, statut, sstrict,
         bstrict, sources, fiab, pe_reg, pe_sci, circ) = ref
        a(f"Ligne du référentiel : « {rlib} » ({rfam}, {runite})")
        a(f"Grille 2016 : {fr(s16)} {runite}")
        a(f"Grille 2026 : {fr(s26)} {runite}"
          + (f" — **applicable à partir du {date_fr(dapp)}**" if dapp else
             " — aucune date d'applicabilité au référentiel"))
        if scond:
            a(f"Seuil conditionnel : {fr(scond)} {runite} — condition : {cond}")
        a(f"Nature : {statut or '—'}")
        a(f"Repère le plus strict identifié : {fr(sstrict)} {runite} — {bstrict or '—'}")
        a(f"Sources : {sources or '—'} · fiabilité : {fiab or '—'}")
        if fiab and fiab != "verifie":
            a("**Cette valeur est en `a_verifier` : le texte doit le dire (§2.7).**")
        for etiquette, valeur in (("perturbateur endocrinien réglementaire", pe_reg),
                                  ("perturbateur endocrinien — littérature", pe_sci),
                                  ("cancérogénicité CIRC", circ)):
            if valeur and valeur.lower() not in ("non", ""):
                a(f"Statut « {etiquette} » : {valeur}")
        if s16 is not None and s26 is not None and s26 > s16:
            a(f"\n**Le seuil s'est déplacé de {fr(s16)} à {fr(s26)} {runite}"
              + (f", au {date_fr(dapp)}" if dapp else "") + ".** "
              "C'est le déplacement que ce dossier a pour objet de rendre visible. "
              "Il ne se raconte jamais comme une amélioration de l'eau (§2.1).")
    else:
        a("**Aucune ligne de référentiel appariée.** Aucun verdict daté n'est "
          "possible sur cette substance : ne rien affirmer d'un seuil.")

    # -------------------------------------------------------------- présence
    p = con.execute("""
        SELECT COUNT(*) , COUNT(*) FILTER (WHERE v.est_quantifie),
               COUNT(DISTINCT a.code_insee),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.est_quantifie),
               MIN(a.date_prelevement), MAX(a.date_prelevement),
               MAX(v.resultat_num) FILTER (WHERE v.est_quantifie),
               MEDIAN(v.resultat_num) FILTER (WHERE v.est_quantifie),
               MIN(v.lq), MAX(v.lq)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
    """, [version, libelle]).fetchone()
    tot_bull = con.execute(
        "SELECT COUNT(*) FROM analyses_figees WHERE version_referentiel = ?",
        [version]).fetchone()[0]

    a("\n## 2. Ce que le corpus en contient\n")
    a(f"Mesures : {p[0]} — sur {tot_bull} bulletins complets du corpus. "
      "**Le dénominateur se donne toujours (§2.11) : une substance n'est "
      "présente que dans les bulletins qui la cherchent.**")
    a(f"Quantifiées : {p[1]}"
      + (f", soit {fr(100.0 * p[1] / p[0], 1)} % des mesures" if p[0] else ""))
    a(f"Communes où elle est cherchée : {p[2]} · où elle est quantifiée : {p[3]}")
    a(f"Première mesure du corpus : {date_fr(p[4])} · dernière : {date_fr(p[5])}")
    a(f"Valeur quantifiée la plus haute : {fr(p[6])} · médiane des quantifiées : {fr(p[7])}")
    a(f"Limites de quantification rencontrées : de {fr(p[8])} à {fr(p[9])}")

    # ------------------------------------------------------- entrée au panel
    a("\n## 3. Quand elle entre au programme d'analyse — par département\n")
    a("**Avant cette date, le corpus ne dit RIEN de cette substance : ni "
      "absence, ni apparition. C'est un indéterminé (§2.4).** Ne jamais écrire "
      "qu'elle « apparaît » ou qu'elle « était absente ».")
    a("")
    a("| département | 1re mesure | dernière | mesures | quantifiées | communes touchées | bulletins du dept |")
    a("|---|---|---|---|---|---|---|")
    for r in con.execute("""
        SELECT a.dept, MIN(a.date_prelevement), MAX(a.date_prelevement), COUNT(*),
               COUNT(*) FILTER (WHERE v.est_quantifie),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.est_quantifie),
               (SELECT COUNT(*) FROM analyses_figees b
                 WHERE b.version_referentiel = a.version_referentiel AND b.dept = a.dept)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
        GROUP BY a.dept, a.version_referentiel ORDER BY 4 DESC
    """, [version, libelle]).fetchall():
        a(f"| {r[0]} | {date_fr(r[1])} | {date_fr(r[2])} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |")

    # Deux départements ne quantifient pas au même rythme, et la première
    # explication à écarter n'est PAS l'eau : c'est l'instrument. Une LQ dix
    # fois plus fine trouve dix fois plus souvent. Sans cette colonne, un
    # rédacteur attribue au territoire ce qui appartient au laboratoire.
    a("\n### Avant de comparer deux départements — regarde la LQ\n")
    a("**Un taux de quantification ne se compare que si les limites de "
      "quantification se comparent.** Une LQ plus fine trouve plus souvent, à "
      "eau identique. Ce n'est pas une négligence, c'est une capacité "
      "d'instrument (§2.1).")
    a("")
    a("| département | LQ min | LQ médiane | LQ max | quantifiées / mesures | taux |")
    a("|---|---|---|---|---|---|")
    for r in con.execute("""
        SELECT a.dept, MIN(v.lq), MEDIAN(v.lq), MAX(v.lq),
               COUNT(*) FILTER (WHERE v.est_quantifie), COUNT(*)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
        GROUP BY 1 HAVING COUNT(*) >= 10 ORDER BY 6 DESC
    """, [version, libelle]).fetchall():
        taux = f"{fr(100.0 * r[4] / r[5], 1)} %" if r[5] else "—"
        a(f"| {r[0]} | {fr(r[1])} | {fr(r[2])} | {fr(r[3])} | {r[4]} / {r[5]} | {taux} |")

    # ------------------------------------------------------- le réétalonnage
    a("\n## 4. Le réétalonnage, en nombre de bulletins\n")
    b = con.execute("""
        SELECT COUNT(*) FILTER (WHERE v.bascule_2016_2026),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.bascule_2016_2026),
               COUNT(*) FILTER (WHERE v.depasse_applicable),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.depasse_applicable),
               COUNT(*) FILTER (WHERE v.depasse_2016),
               COUNT(*) FILTER (WHERE v.depasse_2026),
               COUNT(*) FILTER (WHERE v.depasse_strict)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
    """, [version, libelle]).fetchone()
    a(f"Bascules (au-dessus de la grille 2016, sous celle de 2026) : {b[0]}, "
      f"dans {b[1]} communes")
    a(f"Dépassements **à la date du prélèvement** — le seul comparable à la "
      f"conclusion de l'ARS (§2.10) : {b[2]}, dans {b[3]} communes")
    a(f"Contrefactuels : {b[4]} mesures dépassent la grille 2016, {b[5]} celle "
      f"de 2026, {b[6]} le repère le plus strict identifié")

    # Le poids RELATIF, sans lequel « 221 bascules » ne veut rien dire. Il
    # manquait au premier tirage : la prose a voulu écrire « 44 % des bascules
    # du département » et le contrôle des nombres l'a bloquée. C'est ainsi que
    # le dossier s'étend — par ce que le contrôle refuse, jamais par à-peu-près.
    a("\nPart des bascules de chaque département portée par cette substance :\n")
    a("| département | bascules de la substance | bascules du département | part |")
    a("|---|---|---|---|")
    for r in con.execute("""
        SELECT a.dept,
               COUNT(*) FILTER (WHERE v.bascule_2016_2026 AND v.libelle_parametre = ?),
               COUNT(*) FILTER (WHERE v.bascule_2016_2026)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND a.est_complet
        GROUP BY 1 HAVING COUNT(*) FILTER (WHERE v.bascule_2016_2026 AND v.libelle_parametre = ?) > 0
        ORDER BY 2 DESC
    """, [libelle, version, libelle]).fetchall():
        part = f"{fr(100.0 * r[1] / r[2], 1)} %" if r[2] else "—"
        a(f"| {r[0]} | {r[1]} | {r[2]} | {part} |")

    a("\nPar année de prélèvement :\n")
    a("| année | mesures | quantifiées | bascules | dépassements à la date |")
    a("|---|---|---|---|---|")
    for r in con.execute("""
        SELECT year(a.date_prelevement), COUNT(*),
               COUNT(*) FILTER (WHERE v.est_quantifie),
               COUNT(*) FILTER (WHERE v.bascule_2016_2026),
               COUNT(*) FILTER (WHERE v.depasse_applicable)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
        GROUP BY 1 ORDER BY 1
    """, [version, libelle]).fetchall():
        a(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")

    # ------------------------------------------------------- le cas limite
    if ref and ref[5]:
        dapp = ref[5]
        a("\n## 5. Les cas les plus proches de la date de bascule\n")

        # Une substance peut entrer au programme d'analyse APRÈS son
        # reclassement : il n'existe alors aucune mesure sous l'ancienne règle,
        # et le tableau des « cas de part et d'autre » n'a plus d'objet. Le
        # dire vaut mieux que d'aligner des écarts de mille jours — c'est le
        # CGA 369873 qui l'a montré, entré au corpus 1 032 jours après sa date.
        avant = con.execute("""
            SELECT COUNT(*) FROM verdicts_figes v JOIN analyses_figees a
              USING (code_prelevement, version_referentiel)
            WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
              AND a.date_prelevement < ?::DATE
        """, [version, libelle, dapp]).fetchone()[0]

        if not avant:
            a(f"**Le corpus ne contient aucune mesure de cette substance "
              f"antérieure au {date_fr(dapp)}.** Elle est entrée au programme "
              "d'analyse après son propre reclassement : aucun prélèvement "
              "n'a donc jamais été noté contre l'ancienne valeur, et il n'y a "
              "pas de « cas de part et d'autre » à montrer.")
            a("")
            a("**C'est une nuance de fond, pas une lacune du dossier.** Les "
              "bascules comptées plus haut sont ici entièrement "
              "**contrefactuelles** : elles disent ce qu'aurait valu ce "
              "résultat sous une règle qui n'était déjà plus en vigueur quand "
              "on a commencé à le mesurer. L'écrire autrement — laisser croire "
              "qu'un habitant a bu une eau requalifiée du jour au lendemain — "
              "serait faux.")
        else:
            a(f"La valeur applicable a changé le {date_fr(dapp)}. Un même "
              "résultat, mesuré de part et d'autre de cette date, ne reçoit "
              "pas le même verdict — **c'est la démonstration la plus directe "
              "de la thèse, et elle se raconte sans accuser personne (§2.1).**")
            a(f"\nMesures antérieures à cette date dans le corpus : {avant}.")
            a("")
            a("| commune | dept | date | écart à la date | valeur | seuil appliqué | grille | verdict |")
            a("|---|---|---|---|---|---|---|---|")
            for r in con.execute("""
                SELECT a.commune, a.dept, a.date_prelevement,
                       date_diff('day', ?::DATE, a.date_prelevement) ecart,
                       v.resultat_num, v.seuil_applicable, v.grille_applicable,
                       v.depasse_applicable
                FROM verdicts_figes v JOIN analyses_figees a
                  USING (code_prelevement, version_referentiel)
                WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
                  AND v.est_quantifie AND v.resultat_num > ?
                ORDER BY abs(date_diff('day', ?::DATE, a.date_prelevement)) LIMIT 8
            """, [dapp, version, libelle, ref[3] or 0, dapp]).fetchall():
                signe = f"+{r[3]} j" if r[3] >= 0 else f"{r[3]} j"
                a(f"| {r[0]} | {r[1]} | {date_fr(r[2])} | {signe} | {fr(r[4])} | "
                  f"{fr(r[5])} | {r[6]} | {'dépassement' if r[7] else 'conforme'} |")

    # ------------------------------------------- ce qu'en dit l'administration
    a("\n## 6. Ce que la conclusion sanitaire en dit, quand elle la nomme\n")
    a("Extraits **littéraux** des conclusions de l'ARS où la substance est "
      "nommée. Ils se citent tels quels, jamais reformulés en intention. "
      "**On interroge la norme, pas celui qui l'applique (§2.1).**")
    a("")
    motif = "%" + libelle.split()[-1] + "%"
    for r in con.execute("""
        SELECT a.conclusion_conformite, COUNT(*) n,
               COUNT(DISTINCT a.code_insee), MIN(a.date_prelevement), MAX(a.date_prelevement)
        FROM analyses_figees a
        WHERE a.version_referentiel = ? AND a.conclusion_conformite ILIKE ?
        GROUP BY 1 ORDER BY n DESC LIMIT 6
    """, [version, motif]).fetchall():
        texte = " ".join((r[0] or "").split())
        a(f"- **{r[1]} bulletin(s)**, {r[2]} commune(s), du {date_fr(r[3])} au "
          f"{date_fr(r[4])} :\n  > {texte}")

    # ----------------------------------------------- verdict contre conclusion
    a("\n### Là où notre verdict daté et la conclusion ne disent pas la même chose\n")
    dv = con.execute("""
        SELECT COUNT(*) FROM analyses_figees a
        WHERE a.version_referentiel = ? AND a.conclusion_conformite ILIKE 'Eau d%conforme%'
          AND a.conclusion_conformite NOT ILIKE '%non conforme%'
          AND a.conclusion_conformite NOT ILIKE '%non-conforme%'
          AND EXISTS (SELECT 1 FROM verdicts_figes v
                      WHERE v.code_prelevement = a.code_prelevement
                        AND v.version_referentiel = a.version_referentiel
                        AND v.libelle_parametre = ? AND v.depasse_applicable)
    """, [version, libelle]).fetchone()[0]
    a(f"{dv} bulletin(s) où la conclusion officielle ne prononce aucune "
      "non-conformité alors que notre verdict à la date compte un dépassement "
      "sur cette substance. **Ces cas se disent comme un écart de lecture, "
      "jamais comme une faute : ils demandent une relecture humaine avant "
      "publication (§2.13).**")

    # ------------------------------------------------------------ l'aveugle
    a("\n## 7. Ce que l'analyse ne pouvait pas voir\n")
    av = con.execute("""
        SELECT COUNT(*) FILTER (WHERE v.lq_aveugle),
               MAX(v.lq_rapport_seuil), COUNT(*) FILTER (WHERE v.indetermine_strict)
        FROM verdicts_figes v
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
    """, [version, libelle]).fetchone()
    a(f"Mesures aveugles — la limite de quantification du laboratoire est "
      f"au-dessus du seuil de comparaison : {av[0]}"
      + (f", jusqu'à {fr(av[1], 1)} fois le seuil" if av[1] else ""))
    a(f"Indéterminés au repère le plus strict : {av[2]}")
    a("Sous une LQ, l'analyse ne voit rien : « 0 » ne veut pas dire « absent » "
      "(§2.4). Et une LQ élevée est une capacité d'instrument, jamais une "
      "négligence (§2.1).")

    # ---------------------------------------------------------- traçabilité
    a("\n## 8. Traçabilité\n")
    a(f"Version de référentiel : {version}")
    a(f"Corpus : {tot_bull} bulletins complets figés")
    src = con.execute("""
        SELECT ANY_VALUE(a.source_url) FROM analyses_figees a
        JOIN verdicts_figes v USING (code_prelevement, version_referentiel)
        WHERE a.version_referentiel = ? AND v.libelle_parametre = ? AND v.est_quantifie
    """, [version, libelle]).fetchone()
    if src and src[0]:
        a(f"Exemple d'appel Hub'Eau d'origine : {src[0]}")

    return "\n".join(d) + "\n"


def _sans_separateur(texte):
    """« 2 877 » et « 2877 » sont un seul nombre.

    L'espace des milliers est une convention typographique française ; sans
    cette normalisation, le contrôle lit « 2 » et « 877 » et refuse une phrase
    parfaitement exacte. Appliquée des DEUX côtés — dossier et prose — elle ne
    peut pas laisser passer un nombre inventé.
    """
    return re.sub(r"(?<=\d)[   ](?=\d)", "", texte)


def verifier(chemins=None):
    """
    Contrôle mécanique des proses de substance, avant qu'elles ne s'affichent.

    Le principe du §2.7 transposé du chiffre au texte : **tout nombre décimal
    absent du dossier de faits bloque**. Les règles de vocabulaire sont celles
    de `tests/test_sorties.py` et de `rediger_lot`, importées et non recopiées —
    deux copies d'une règle divergent à la première retouche.

    Rend (bloquants, signalements). Aucun fichier n'est écrit.
    """
    import json
    sys.path.insert(0, os.path.join(RACINE, "tests"))
    import rediger_lot as RL

    prop = os.path.join(RACINE, "sortie", "redactions_substances_proposees.json")
    valid = os.path.join(RACINE, "sortie", "redactions_substances.json")
    bloquants, signalements = [], []
    n = 0

    for chemin in (chemins or [valid, prop]):
        if not os.path.exists(chemin):
            continue
        with open(chemin, encoding="utf-8") as fh:
            entrees = json.load(fh)
        for cle, v in entrees.items():
            n += 1
            libelle = v.get("libelle_parametre") or cle
            dossier_md = os.path.join(DOSSIERS, f"SUBSTANCE-{slug(libelle)}.md")
            if not os.path.exists(dossier_md):
                bloquants.append(f"{cle} : dossier de faits absent — {dossier_md}")
                continue
            with open(dossier_md, encoding="utf-8") as fh:
                faits = _sans_separateur(fh.read())

            morceaux = [v.get("titre", ""), v.get("chapeau", "")]
            morceaux += [s.get("t", "") + " " + s.get("x", "")
                         for s in v.get("sections", [])]
            morceaux += list(v.get("limites", []))
            texte = _sans_separateur("\n".join(morceaux))

            # 1. les nombres — le contrôle qui attrape la valeur inventée
            connus = RL._nombres(faits)
            for x in sorted(RL._nombres(texte) - connus):
                bloquants.append(f"{cle} : le nombre « {x} » n'est pas dans le "
                                 "dossier de faits")

            # 2. le vocabulaire — mêmes listes que la prose de bulletin
            bas = texte.lower()
            for mot in RL.ABSENCES:
                if mot in bas:
                    bloquants.append(f"{cle} : affirmation d'absence — « {mot} » (§2.4)")
            for mot in RL.SANITAIRES:
                if mot in bas:
                    bloquants.append(f"{cle} : qualificatif sanitaire — « {mot} » (§2.2)")

            # 3. la forme
            if not (4 <= len(v.get("sections", [])) <= 6):
                bloquants.append(f"{cle} : `sections` doit compter 4 à 6 entrées")
            if not (3 <= len(v.get("limites", [])) <= 6):
                bloquants.append(f"{cle} : `limites` doit compter 3 à 6 entrées")
            for champ in ("titre", "chapeau", "libelle_parametre"):
                if not v.get(champ):
                    bloquants.append(f"{cle} : champ manquant — {champ}")
            for m in v.get("manques", []):
                signalements.append(f"{cle} : manque signalé par le rédacteur — {m}")

    return bloquants, signalements, n


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--libelle", help="libellé exact tel qu'il figure dans la source")
    p.add_argument("--code", help="code SANDRE")
    p.add_argument("--liste", action="store_true",
                   help="les substances qui ont de quoi porter un dossier")
    p.add_argument("--verifier", action="store_true",
                   help="contrôle les proses écrites, sans rien produire")
    p.add_argument("--sortie", help="chemin du fichier produit")
    a = p.parse_args()

    if a.verifier:
        bloquants, signalements, n = verifier()
        print(f"{n} prose(s) de substance contrôlée(s)")
        for s in signalements:
            print(f"  ~ {s}")
        for b in bloquants:
            print(f"  ! {b}")
        if bloquants:
            print(f"\n{len(bloquants)} bloquant(s) — rien ne doit s'afficher en l'état.")
            sys.exit(1)
        print("\naucun bloquant : chaque nombre écrit vient du dossier de faits.")
        return

    if not os.path.exists(DB_PATH):
        print("base absente — lance d'abord src/build_db.py")
        sys.exit(1)
    con = duckdb.connect(DB_PATH, read_only=True)
    version = figer.version_referentiel()

    try:
        if a.liste:
            print(f"substances à au moins {MIN_QUANTIFIEES} quantifications "
                  f"(version {version}) :\n")
            print(f"{'libellé':<46} {'code':>6} {'mesures':>8} {'quantif':>8} {'bascules':>9}")
            for r in eligibles(con, version):
                print(f"{r[0][:46]:<46} {r[1] or '':>6} {r[2]:>8} {r[3]:>8} {r[4]:>9}")
            return

        libelle = a.libelle
        if a.code and not libelle:
            r = con.execute("""
                SELECT libelle_parametre, COUNT(*) n FROM verdicts_figes
                WHERE version_referentiel = ? AND code_parametre = ?
                GROUP BY 1 ORDER BY n DESC
            """, [version, a.code]).fetchall()
            if not r:
                print(f"aucune mesure figée sous le code {a.code}")
                sys.exit(1)
            if len(r) > 1:
                print(f"le code {a.code} porte {len(r)} libellés — "
                      "choisis avec --libelle :")
                for x in r:
                    print(f"    {x[0]}  ({x[1]} mesures)")
                sys.exit(1)
            libelle = r[0][0]
        if not libelle:
            p.error("donne --libelle, --code ou --liste")

        n = con.execute("""SELECT COUNT(*) FROM verdicts_figes
                           WHERE version_referentiel = ? AND libelle_parametre = ?""",
                        [version, libelle]).fetchone()[0]
        if not n:
            print(f"aucune mesure figée pour « {libelle} » sous la version {version}")
            sys.exit(1)

        texte = dossier(con, libelle, version)
        os.makedirs(DOSSIERS, exist_ok=True)
        chemin = a.sortie or os.path.join(DOSSIERS, f"SUBSTANCE-{slug(libelle)}.md")
        with open(chemin, "w", encoding="utf-8") as fh:
            fh.write(texte)
        print(f"dossier écrit : {chemin}")
        print(f"  {len(texte.splitlines())} lignes, version de référentiel {version}")
        print("  à relire AVANT toute rédaction : ce qui manque ici ne sera pas")
        print("  écrit, et ce qui est faux ici le sera.")
    finally:
        con.close()


if __name__ == "__main__":
    main()

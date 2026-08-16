# -*- coding: utf-8 -*-
"""
La page publique d'une substance — et l'accroche courte qui y renvoie.

L'étage au-dessus de la fiche communale. La fiche répond « qu'y a-t-il dans mon
eau ? » ; cette page répond « qu'est-ce que cette substance démontre ? ».

**Le partage, décidé le 10 août 2026 : ce qui est partagé ne se recopie pas, il
se lie.** Le raisonnement — long, sourcé, relu une fois par l'auteur — vit ici,
en un seul exemplaire. Chaque fiche communale concernée ne porte qu'une
accroche de deux phrases, fabriquée mécaniquement à partir des chiffres de SON
bulletin, plus un lien. Recopier les cinq sections dans 155 fiches produirait
155 pages qui disent la même chose : le lecteur qui en ouvre deux cesse de
croire la troisième, et la relecture humaine redevient un travail de lot.

Trois sources se superposent, dans l'ordre de préséance de `build_fiche` :

    auteur  →  sortie/redactions_substances.json
    proposé →  sortie/redactions_substances_proposees.json
    dérivé  →  les tableaux calculés ici, qui s'affichent de toute façon

Les tableaux ne sont jamais écrits par un modèle : ils sortent d'une requête à
chaque construction, et se recalculent si le référentiel bouge.
"""

import json
import os
import re
import sys
import unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "src"))

import common as C  # noqa: E402

VALIDEES = os.path.join(ICI, "redactions_substances.json")
PROPOSEES = os.path.join(ICI, "redactions_substances_proposees.json")

LIBELLE_ORIGINE = {
    "auteur": "rédaction de l'auteur",
    "propose": "proposition de rédaction, à relire",
    "derive": "dérivé de la base",
}

# Le vocabulaire des trois natures — défini UNE fois, employé par la page de
# substance et par son index (`site/build_site.py` le lit ici). Deux copies
# d'un vocabulaire divergent à la première retouche, et celui-ci décide de ce
# que le lecteur croit lire : une valeur opposable, ou une valeur indicative.
NATURE_EN_CLAIR = {
    "limite": "limite de qualité",
    "reference": "référence de qualité",
    "vigilance": "valeur de vigilance",
    "referentiel_sans_statut": "au référentiel, sans statut",
}

# Ce que chaque nature autorise à conclure. Le §2.13 cinquième cas : un
# reclassement de pertinence ne relâche pas une limite, il fait SORTIR la
# substance du périmètre opposable — le sien, et celui du total des pesticides
# qu'elle cessait le même jour d'alimenter.
PORTEE_NATURE = {
    "limite": "Une limite de qualité est <b>opposable</b> : la dépasser rend "
              "l'eau non conforme. Le déplacement de cette valeur déplace donc "
              "un verdict de conformité, au sens plein.",
    "reference": "Une référence de qualité <b>ne fonde aucune non-conformité</b>. "
                 "La dépasser ne rend pas l'eau non conforme ; l'administration "
                 "le mentionne séparément.",
    "vigilance": "Une valeur de vigilance est <b>indicative</b> : elle ne fonde "
                 "aucune non-conformité. Une substance qui y passe <b>sort du "
                 "périmètre opposable</b> — pour elle-même, et pour le total "
                 "des pesticides qu'elle cessait ce jour-là d'alimenter. Ce "
                 "n'est donc pas une limite qui se relâche, c'est une substance "
                 "qui cesse d'être comptée.",
    "referentiel_sans_statut": "Le référentiel porte une valeur pour cette "
                               "substance sans en déclarer la nature : on ne "
                               "peut pas dire ici si elle est opposable.",
}

# §2.12 — sur un métabolite, la valeur « d'avant » n'est pas lue dans un texte
# de l'époque : elle vient de l'instruction de décembre 2020. Partout où la
# grille de 2016 est invoquée sur un métabolite, cela se dit.
NOTE_METABOLITE = (
    "<b>La valeur « d'avant » est ici une extrapolation, et elle se dit.</b> "
    "Les 0,1 µg/L portés comme valeur applicable avant le reclassement viennent "
    "de l'instruction DGS/EA4/2020/177 de <b>décembre 2020</b>. Les appliquer à "
    "un prélèvement plus ancien est un raisonnement défendable, pas la lecture "
    "d'un texte de l'époque.")


def slug(s):
    """
    L'identifiant d'URL d'un paramètre.

    **Défini ici et nulle part ailleurs.** `sortie/dossier_substance.py` le
    reprend : deux fonctions de slug qui divergeraient enverraient le
    répertoire vers des adresses que les pages ne portent pas, et les quatre
    dossiers déjà publiés changeraient d'adresse sans que rien ne le signale.
    """
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _lire(chemin):
    if not os.path.exists(chemin):
        return {}
    with open(chemin, encoding="utf-8") as fh:
        return json.load(fh)


def charger():
    return _lire(VALIDEES), _lire(PROPOSEES)


def publiables():
    """[(slug, libelle_parametre, origine)] — l'auteur l'emporte sur le modèle."""
    valid, prop = charger()
    out = []
    for slug in sorted(set(valid) | set(prop)):
        d = valid.get(slug) or prop[slug]
        out.append((slug, d.get("libelle_parametre") or slug,
                    "auteur" if slug in valid else "propose"))
    return out


# ---------------------------------------------------------------------------
# Le répertoire — TOUTES les molécules cherchées, en une seule passe
# ---------------------------------------------------------------------------
def repertoire(con, version):
    """
    Une entrée par paramètre cherché dans le corpus figé, triée par libellé.

    **Une seule requête groupée, et c'est une contrainte de conception, pas une
    optimisation.** Les fonctions `seuil`, `chiffres`, `par_departement` et
    `cas_limites` ci-dessous coûtent chacune un balayage : à quatre dossiers
    elles se paient, à 1 243 molécules elles balaieraient quatorze millions de
    lignes plus de sept mille fois. Mesuré le 15 août 2026 : la passe groupée
    rend les 1 243 molécules en **0,9 s**. Les requêtes par molécule restent
    donc réservées aux quelques-unes qui portent un dossier rédigé.

    Tout est lu dans `verdicts_figes`, jamais recalculé : ce que le moteur a
    conclu au moment du figeage fait foi (§8bis). Le référentiel n'est
    interrogé que pour ce qu'une ligne figée ne porte pas — la date
    d'applicabilité et le statut — et l'appariement y reprend celui de `seuil()`
    : par code, à défaut par libellé.
    """
    lignes = con.execute("""
        SELECT v.libelle_parametre,
               ANY_VALUE(v.code_parametre), ANY_VALUE(v.code_cas),
               ANY_VALUE(v.famille), ANY_VALUE(v.nature_seuil),
               ANY_VALUE(v.unite), ANY_VALUE(v.attribution),
               ANY_VALUE(v.seuil_2016), ANY_VALUE(v.seuil_2026_effectif),
               ANY_VALUE(v.origine_seuil_2026), ANY_VALUE(v.fiabilite),
               ANY_VALUE(v.pe_reglementaire), ANY_VALUE(v.pe_scientifique),
               COUNT(*), COUNT(*) FILTER (WHERE v.est_quantifie),
               COUNT(DISTINCT a.code_insee),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.est_quantifie),
               COUNT(*) FILTER (WHERE v.depasse_applicable),
               COUNT(*) FILTER (WHERE v.bascule_2016_2026),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.bascule_2016_2026),
               MEDIAN(v.lq), COUNT(*) FILTER (WHERE v.lq_aveugle),
               MIN(a.date_prelevement), MAX(a.date_prelevement),
               COUNT(DISTINCT a.dept)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ?
        GROUP BY 1 ORDER BY 1
    """, [version]).fetchall()

    # Le référentiel entier tient en mémoire — 457 lignes. L'appariement se
    # fait ici plutôt qu'en SQL parce qu'une jointure sur « code OU libellé »
    # multiplie les lignes du groupe et fausserait tous les comptes.
    #
    # **Le repli se fait par `common.norm`, pas par `lower()`.** Écrit d'abord
    # avec `lower()`, il perdait le sélénium : le corpus dit « Sélénium », le
    # référentiel « Selenium », et le code 1385 a été retiré du référentiel en
    # août 2026 parce qu'il porte deux objets réglementaires (§11.2). Ni le
    # code ni le libellé minuscule ne rapprochaient donc les deux — la ligne
    # sortait sans date d'applicabilité, alors que le §2.5 la rend obligatoire.
    # `norm` est la fonction que le moteur lui-même emploie ; s'en écarter,
    # c'est apparier autrement que ce qu'on affiche.
    par_code, par_libelle, par_alias = {}, {}, {}
    for r in con.execute("""
            SELECT code_parametre, libelle, date_applicabilite_2026,
                   statut_2026, sources, fiabilite, seuil_futur,
                   date_applicabilite_futur, cancerogenicite_circ
            FROM referentiel_seuils""").fetchall():
        if r[0]:
            par_code[str(r[0])] = r
        if r[1]:
            par_libelle[C.norm(r[1])] = r
    # Et les alias, troisième et dernier recours — même ordre que `v_mesures_ref`.
    for a, cible in con.execute(
            "SELECT alias_norm, libelle_norm FROM alias_parametres").fetchall():
        if cible in par_libelle:
            par_alias[a] = par_libelle[cible]

    # Les molécules jugées par une RÈGLE DE FAMILLE, et non par une ligne qui
    # leur soit propre. La distinction est celle du §2.8 — « trois sources de
    # seuil qui ne se confondent pas » — et la colonne figée ne la porte pas :
    # `origine_seuil_2026` vaut « referentiel » dans les deux cas, parce que
    # `v_mesures_ref` a déjà fondu la règle de famille dans `seuil_2026`. Sur
    # 1 243 molécules du corpus, **735 sont notées par la règle des pesticides
    # à 0,1 µg/L**, pas par une valeur lue pour elles : la majorité. Une page
    # qui laisserait croire à une ligne sourcée par molécule mentirait sur le
    # travail réellement fait.
    familles = {}
    try:
        for r in con.execute("""SELECT libelle_parametre, ANY_VALUE(regle)
                                FROM v_regle_famille_appliquee
                                GROUP BY 1""").fetchall():
            familles[r[0]] = r[1]
    except Exception:
        pass                      # vue absente d'une base ancienne : on n'invente pas

    corpus = con.execute(
        "SELECT COUNT(*) FROM analyses_figees WHERE version_referentiel = ?",
        [version]).fetchone()[0]

    # Deux molécules peuvent donner le même identifiant d'URL — « Chlorite » et
    # « chlorite ! » en donneraient un seul. On le constate ici plutôt que de
    # publier deux pages dont la seconde écrase la première : le code SANDRE
    # départage, et à défaut un rang. Silencieux serait le pire des deux.
    vus, out = {}, []
    for r in lignes:
        ref = par_code.get(str(r[1])) if r[1] else None
        if ref is None:
            ref = par_libelle.get(C.norm(r[0])) or par_alias.get(C.norm(r[0]))
        s = slug(r[0])
        if s in vus:
            s = f"{s}-{r[1]}" if r[1] else f"{s}-{len(vus)}"
        vus[s] = r[0]
        # Les quatre origines honnêtes, là où la colonne figée n'en connaît que
        # trois. `regle` prime sur `ligne` : une molécule couverte par la règle
        # de famille ET par une ligne propre est jugée par la ligne, mais la
        # vue ne l'y range justement pas.
        if r[9] == "referentiel":
            origine = "regle" if r[0] in familles else "ligne"
        else:
            origine = r[9]
        out.append(dict(
            slug=s, libelle=r[0], code=r[1], cas=r[2], famille=r[3],
            nature=r[4], unite=r[5], attribution=r[6],
            seuil_2016=r[7], seuil_2026=r[8], origine_seuil=origine,
            regle_famille=familles.get(r[0]),
            fiabilite=r[10], pe_reglementaire=r[11], pe_scientifique=r[12],
            mesures=r[13], quantifiees=r[14], communes=r[15],
            communes_quantifiee=r[16], depassements=r[17], bascules=r[18],
            communes_bascule=r[19], lq_mediane=r[20], aveugles=r[21],
            premiere=r[22], derniere=r[23], departements=r[24],
            version=version,
            date_applicabilite=ref[2] if ref else None,
            statut=ref[3] if ref else None,
            sources=ref[4] if ref else None,
            circ=ref[8] if ref else None,
            corpus=corpus))
    return out


# ---------------------------------------------------------------------------
# Les faits — une requête chacun, jamais une valeur écrite à la main
# ---------------------------------------------------------------------------
def seuil(con, libelle, version):
    """La ligne de référentiel qui note cette substance, ou None."""
    return con.execute("""
        SELECT r.libelle, r.unite, r.seuil_2016, r.seuil_2026,
               r.date_applicabilite_2026, r.statut_2026, r.sources, r.fiabilite
        FROM referentiel_seuils r
        WHERE EXISTS (SELECT 1 FROM verdicts_figes v
                      WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
                        AND (v.code_parametre = r.code_parametre
                             OR lower(v.libelle_parametre) = lower(r.libelle)))
        LIMIT 1
    """, [version, libelle]).fetchone()


def chiffres(con, libelle, version):
    """
    Les comptes de la substance — et la NATURE de la valeur qui la note.

    `nature_seuil` est lue dans `verdicts_figes`, où elle est calculée une fois
    par `build_db.py` et figée avec le reste. On ne la redérive pas ici du
    `statut_2026` : deux copies d'une règle divergent à la première retouche, et
    celle-ci décide de ce que le lecteur croit lire — une limite de qualité
    opposable, une référence, ou une simple valeur indicative (§11.3).
    """
    r = con.execute("""
        SELECT COUNT(*), COUNT(*) FILTER (WHERE v.est_quantifie),
               COUNT(DISTINCT a.code_insee),
               COUNT(*) FILTER (WHERE v.bascule_2016_2026),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.bascule_2016_2026),
               COUNT(*) FILTER (WHERE v.depasse_applicable),
               ANY_VALUE(v.nature_seuil), ANY_VALUE(v.famille)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
    """, [version, libelle]).fetchone()
    total = con.execute(
        "SELECT COUNT(*) FROM analyses_figees WHERE version_referentiel = ?",
        [version]).fetchone()[0]
    return dict(mesures=r[0], quantifiees=r[1], communes=r[2], bascules=r[3],
                communes_bascule=r[4], depassements=r[5],
                nature=r[6], famille=r[7], corpus=total)


def par_departement(con, libelle, version):
    return con.execute("""
        SELECT a.dept, MIN(a.date_prelevement), COUNT(*),
               COUNT(*) FILTER (WHERE v.est_quantifie),
               MEDIAN(v.lq),
               COUNT(*) FILTER (WHERE v.bascule_2016_2026)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
        GROUP BY 1 HAVING COUNT(*) >= 10 ORDER BY 3 DESC
    """, [version, libelle]).fetchall()


def mesures_avant(con, libelle, version, date_app):
    """Combien de mesures ont été notées sous l'ANCIENNE valeur.

    Zéro veut dire que la substance est entrée au programme d'analyse après son
    propre reclassement : les bascules sont alors entièrement contrefactuelles,
    et il n'y a aucun « cas de part et d'autre » à montrer. Le CGA 369873 est
    dans ce cas — entré au corpus plus de mille jours après sa date.
    """
    if not date_app:
        return None
    return con.execute("""
        SELECT COUNT(*) FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
          AND a.date_prelevement < ?::DATE
    """, [version, libelle, date_app]).fetchone()[0]


def cas_limites(con, libelle, version, date_app, plancher, n=6):
    """Les mesures les plus proches de la date de bascule, de part et d'autre."""
    if not date_app or not mesures_avant(con, libelle, version, date_app):
        return []
    return con.execute("""
        SELECT a.commune, a.code_insee, a.dept, a.date_prelevement,
               date_diff('day', ?::DATE, a.date_prelevement),
               v.resultat_num, v.seuil_applicable, v.depasse_applicable
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
          AND v.est_quantifie AND v.resultat_num > ?
        ORDER BY abs(date_diff('day', ?::DATE, a.date_prelevement)) LIMIT ?
    """, [date_app, version, libelle, plancher or 0, date_app, n]).fetchall()


ORIGINE_SEUIL = {
    "ligne": ("une ligne du référentiel qui lui est propre",
              "Le terme de comparaison vient d'une ligne du référentiel établie "
              "pour lui seul, avec ses sources et sa date."),
    "regle": ("une règle de famille",
              "Aucune valeur n'a été lue <b>pour ce paramètre en propre</b> : il "
              "est noté par la règle qui s'applique à toute sa famille. C'est ce "
              "que fait aussi l'administration, mais cela ne vaut pas une "
              "valeur sourcée molécule par molécule, et le §2.8 impose de ne "
              "pas confondre les deux."),
    "declare": ("la limite déclarée par la source",
                "La valeur vient du fichier de la source, pas du référentiel du "
                "projet. Une limite seulement déclarée <b>ne fabrique jamais de "
                "passé réglementaire</b> : elle ne produit ni verdict 2016 ni "
                "bascule, parce qu'on ne reconstruit pas la grille d'hier à "
                "partir de celle d'aujourd'hui."),
    "absent": ("aucun",
               "<b>Rien n'est prononcé sur ce paramètre.</b> Le corpus le "
               "mesure, mais aucun terme de comparaison n'a été établi : il "
               "ne pèse sur aucun verdict de conformité, ni dans un sens ni "
               "dans l'autre."),
}


def brief(f, identites, h, prefixe="", a_un_dossier=False):
    """
    La page d'un paramètre qui n'a pas de dossier rédigé — tout est dérivé.

    Trois obligations d'affichage la structurent, et aucune n'est décorative :

      · §2.11 — le dénombrement ne se donne jamais sans son dénominateur. Une
        substance n'est présente que dans les bulletins qui la cherchent ;
      · §2.4  — jamais « absente ». Une molécule cherchée mille fois et jamais
        quantifiée est une molécule **jamais vue au-dessus de la limite de
        quantification du laboratoire**, ce qui n'est pas la même chose ;
      · §2.8  — d'où vient le terme de comparaison, et s'il n'y en a pas, le
        dire. Sur 1 243 paramètres, 390 n'en ont aucun et 731 sont notés par
        une règle de famille : le taire ferait passer le répertoire pour un
        travail de sourçage molécule par molécule qu'il n'est pas.
    """
    import build_fiche as BF
    import identite as ID

    o = []
    a = o.append
    nature = NATURE_EN_CLAIR.get(f["nature"], "aucun terme de comparaison")
    etiquette, explication = ORIGINE_SEUIL.get(
        f["origine_seuil"], ("—", ""))

    # --- ce que c'est, sourcé ou pas du tout ------------------------------
    ligne_identite = ID.pour(identites, f["code"], f["libelle"])
    a('<section style="margin-top:0"><div class="prose">')
    if ligne_identite:
        a(ID.bloc(ligne_identite, h))
    else:
        a('<p class="bnote"><b>Ce que ce paramètre est n\'a pas encore été '
          'sourcé.</b> Tout ce qui suit est dérivé du corpus et du référentiel ; '
          'dire à quoi il sert ou d\'où il vient demande la lecture d\'une '
          'source, et le projet n\'écrit pas ce qu\'il n\'a pas lu.</p>')
    a('</div></section>')

    # --- identité administrative ------------------------------------------
    a('<section><h3 class="sec">Identité</h3><table><tbody>')
    a(f'<tr><th>Libellé de la source</th><td>{h(f["libelle"])}</td></tr>')
    a(f'<tr><th>Code SANDRE</th><td>{h(f["code"] or "—")}</td></tr>')
    a(f'<tr><th>Numéro CAS</th><td>{h(f["cas"] or "—")}</td></tr>')
    a(f'<tr><th>Famille</th><td>{h(f["famille"] or "non renseignée")}</td></tr>')
    a(f'<tr><th>Unité de mesure</th><td>{h(f["unite"] or "—")}</td></tr>')
    a('</tbody></table></section>')

    # --- à quoi on la compare ---------------------------------------------
    a('<section><h3 class="sec">À quoi on la compare</h3>')
    if f["seuil_2026"] is None:
        a(f'<p class="bnote">{explication}</p>')
        if f["attribution"]:
            a(f'<p class="bnote">Attribution : <b>{h(f["attribution"])}</b>.</p>')
    else:
        a('<div class="chiffres">')
        bouge = (f["seuil_2016"] is not None
                 and f["seuil_2016"] != f["seuil_2026"])
        if bouge:
            a(f'<div class="chiffre"><div class="n">{h(BF._nb(f["seuil_2016"]))}</div>'
              f'<div class="l">{h(nature)} applicable avant<br>{h(f["unite"] or "")}</div></div>')
        a(f'<div class="chiffre{" bascule" if bouge else ""}">'
          f'<div class="n">{h(BF._nb(f["seuil_2026"]))}</div>'
          f'<div class="l">{h(nature)} aujourd\'hui<br>'
          + (f'depuis le {h(BF._date_fr(f["date_applicabilite"]))}'
             if f["date_applicabilite"] else h(f["unite"] or "")) + '</div></div>')
        if f["bascules"]:
            a(f'<div class="chiffre"><div class="n">{f["bascules"]}</div>'
              f'<div class="l">analyses basculées<br>'
              f'dans {f["communes_bascule"]} communes</div></div>')
        a('</div>')
        a(f'<p class="bnote">Nature : <b>{h(nature)}</b>. '
          + PORTEE_NATURE.get(f["nature"], "") + '</p>')
        a(f'<p class="bnote">D\'où vient ce terme de comparaison : '
          f'<b>{h(etiquette)}</b>. {explication}</p>')
        if bouge and (f["famille"] or "") == "metabolite":
            a(f'<p class="bnote">{NOTE_METABOLITE}</p>')
        if f["statut"]:
            fiab = f["fiabilite"] or ""
            a(f'<p class="bnote">Statut au référentiel : <b>{h(f["statut"])}</b>. '
              f'Sources : {h(f["sources"] or "—")}. Fiabilité : <b>{h(fiab or "—")}</b>.'
              + (' <b>Valeur en « à vérifier » : elle est signalée comme telle '
                 'et ne s\'arrondit jamais en « vérifié ».</b>'
                 if fiab != "verifie" else "") + '</p>')
        elif f["regle_famille"]:
            a(f'<p class="bnote">Règle appliquée : <b>{h(f["regle_famille"])}</b>.</p>')
    a('</section>')

    # --- ce que le corpus en dit ------------------------------------------
    a('<section><h3 class="sec">Ce que le corpus en dit</h3>')
    a(f'<p class="bnote">Cherché dans <b>{f["mesures"]} bulletins</b> sur les '
      f'{f["corpus"]} que compte le corpus, répartis sur {f["departements"]} '
      f'départements et {f["communes"]} communes. Une substance n\'est présente '
      f'que dans les bulletins qui la cherchent : ce dénominateur ne se sépare '
      f'jamais du reste.</p>')
    a('<div class="chiffres">')
    a(f'<div class="chiffre"><div class="n">{f["quantifiees"]}</div>'
      f'<div class="l">analyses où elle est quantifiée<br>'
      f'dans {f["communes_quantifiee"]} communes</div></div>')
    if f["lq_mediane"] is not None:
        a(f'<div class="chiffre"><div class="n">{h(BF._nb(f["lq_mediane"]))}</div>'
          f'<div class="l">limite de quantification médiane<br>{h(f["unite"] or "")}</div></div>')
    if f["seuil_2026"] is not None:
        a(f'<div class="chiffre"><div class="n">{f["depassements"]}</div>'
          f'<div class="l">dépassements<br>à la date du prélèvement</div></div>')
    a('</div>')

    # §2.4 — le point sur lequel une page de substance se trompe le plus vite.
    if not f["quantifiees"]:
        a('<p class="bnote"><b>Elle n\'a jamais été quantifiée dans le corpus, '
          'et cela ne veut pas dire qu\'elle est absente.</b> Cela veut dire '
          'qu\'aucune analyse ne l\'a vue au-dessus de la limite de '
          'quantification du laboratoire. En dessous, l\'analyse ne distingue '
          'pas une eau qui n\'en contient pas d\'une eau qui en porte moins '
          'que ce que l\'instrument sait lire.</p>')
    if f["aveugles"]:
        a(f'<p class="bnote"><b>{f["aveugles"]} analyses sont aveugles</b> : la '
          'limite de quantification du laboratoire y est au-dessus de la valeur '
          'à laquelle on compare. Sous cette limite, l\'analyse ne peut rien '
          'conclure — là précisément où la conformité se joue. C\'est une '
          'capacité d\'instrument, jamais une négligence.</p>')
    if f["premiere"]:
        a(f'<p class="bnote">Première mesure du corpus le '
          f'{h(BF._date_fr(f["premiere"]))}, dernière le '
          f'{h(BF._date_fr(f["derniere"]))}. <b>Avant cette première date, le '
          'corpus ne dit rien</b> : ni absence, ni apparition.</p>')
    a('</section>')

    # --- les trois registres, jamais fusionnés (§2.15) ---------------------
    registres = [(e, v) for e, v in (
        ("Perturbateur endocrinien au sens réglementaire (UE)", f["pe_reglementaire"]),
        ("Perturbateur endocrinien au sens de la littérature", f["pe_scientifique"]),
        ("Cancérogénicité — classement CIRC", f["circ"])) if v]
    if registres:
        a('<section><h3 class="sec">Trois registres, qui ne se déduisent pas '
          'l\'un de l\'autre</h3><table><tbody>')
        for etiq, val in registres:
            a(f'<tr><th>{etiq}</th><td>{h(val)}</td></tr>')
        a('</tbody></table><p class="bnote">Un statut réglementaire, un état de '
          'la littérature et un classement du CIRC sont trois faits distincts. '
          'Aucun ne s\'infère d\'un autre, et l\'absence de l\'un ne dit rien '
          'des deux autres.</p></section>')

    if a_un_dossier:
        a('<section><p class="bnote">Cette substance porte en outre un '
          '<b>dossier rédigé</b>, qui expose ce que son reclassement démontre.</p>'
          '</section>')

    a('<section><p class="bnote">Tous les chiffres de cette page sont dérivés '
      'de la base, version de référentiel ' + h(f.get("version", "")) + '. '
      'On interroge ici la norme et son déplacement, jamais ceux qui '
      'l\'appliquent.</p></section>')
    return "\n".join(o)


# ---------------------------------------------------------------------------
# L'accroche posée dans la fiche communale
# ---------------------------------------------------------------------------
def accroches(con, version):
    """
    {libelle_parametre: {u, d, a, b}} pour les substances qui ont une page.

    `u` l'adresse de la page, `d` la date d'applicabilité en toutes lettres,
    `a` la valeur d'avant, `b` celle d'après. La fiche n'a besoin de rien
    d'autre : le reste de la phrase se compose côté rendu, avec la valeur du
    bulletin, qu'elle est seule à connaître.
    """
    import build_fiche as BF
    out = {}
    for slug, libelle, _origine in publiables():
        s = seuil(con, libelle, version)
        if not s or not s[4] or s[2] is None or s[3] is None:
            continue          # sans date d'applicabilité, il n'y a rien à raconter
        out[libelle] = {"u": f"substance/{slug}.html",
                        "d": BF._date_fr(s[4]),
                        "a": BF._nb(s[2]), "b": BF._nb(s[3]), "un": s[1] or ""}
    return out


# ---------------------------------------------------------------------------
# Le corps de la page
# ---------------------------------------------------------------------------
def corps(con, slug, version, h, prefixe=""):
    """`h` est l'échappement HTML de l'appelant — on ne le redéfinit pas ici."""
    import build_fiche as BF

    valid, prop = charger()
    d = valid.get(slug) or prop.get(slug)
    origine = "auteur" if slug in valid else "propose"
    libelle = d.get("libelle_parametre") or slug

    s = seuil(con, libelle, version)
    c = chiffres(con, libelle, version)
    depts = par_departement(con, libelle, version)
    cas = cas_limites(con, libelle, version, s[4] if s else None,
                      s[2] if s else None)

    o = []
    a = o.append

    if origine == "propose":
        a('<section style="margin-top:0"><div class="gardefou">'
          '<b>Proposition de rédaction, à relire.</b> Ce texte est une '
          'proposition composée à partir du dossier de faits de la substance ; '
          'il n\'a pas encore été validé par l\'auteur. Les tableaux et les '
          'chiffres, eux, sont dans tous les cas dérivés de la base et '
          'vérifiables.</div></section>')

    # --- ce que c'est, sourcé ----------------------------------------------
    #
    # Le dossier long l'a porté aussi à partir du 15 août 2026. Il l'ignorait
    # tant que la table d'identité n'existait pas ; une fois qu'elle existe,
    # laisser le brief la porter et pas le dossier ferait de la page la plus
    # travaillée la moins complète des deux.
    # L'appariement se fait ici par LIBELLÉ seul : `seuil()` ne rend pas le
    # code SANDRE. C'est suffisant — la table d'identité porte les deux clés —
    # mais une identité déclarée par code seul, sans libellé, ne serait pas
    # retrouvée sur cette page. Le brief, lui, dispose des deux.
    import identite as ID
    ligne_identite = ID.pour(ID.charger(), None, libelle)
    if ligne_identite:
        a('<section style="margin-top:0"><div class="prose">'
          + ID.bloc(ligne_identite, h) + '</div></section>')

    # --- le chapeau et les sections, prose ---------------------------------
    a('<section style="margin-top:0"><div class="prose">')
    if d.get("chapeau"):
        a(f'<p class="st">{h(d["chapeau"])}</p>')
    for sec in d.get("sections", []):
        a(f'<h4>{h(sec.get("t", ""))}</h4><p>{h(sec.get("x", ""))}</p>')
    a('</div></section>')

    # --- le seuil et sa date, dérivé --------------------------------------
    if s:
        nature = NATURE_EN_CLAIR.get(c["nature"], "nature non déclarée")
        a('<section><h3 class="sec">La valeur, sa nature et sa date</h3>')
        # La nature vient AVANT les deux chiffres. Elle était reléguée en note
        # de bas de bloc jusqu'au 15 août 2026 : trois grands nombres « 0,1 →
        # 0,9, applicable depuis le 29 avril 2024 » se lisent comme une limite
        # de qualité qu'on relâche, alors que les quatre substances publiées
        # sont des métabolites reclassés en valeur de vigilance. Le lecteur
        # doit savoir ce qu'il regarde avant de le regarder.
        a(f'<p class="bnote" style="margin-top:0">Ce que cette substance porte '
          f'est une <b>{h(nature)}</b>. ' + PORTEE_NATURE.get(c["nature"], "")
          + '</p>')
        a('<div class="chiffres">')
        a(f'<div class="chiffre"><div class="n">{h(BF._nb(s[2]))}</div>'
          f'<div class="l">{h(nature)} applicable avant<br>{h(s[1] or "")}</div></div>')
        a(f'<div class="chiffre bascule"><div class="n">{h(BF._nb(s[3]))}</div>'
          f'<div class="l">{h(nature)} applicable depuis<br>le {h(BF._date_fr(s[4]))}</div></div>'
          if s[4] else
          f'<div class="chiffre"><div class="n">{h(BF._nb(s[3]))}</div>'
          f'<div class="l">{h(nature)} applicable aujourd\'hui<br>sans date au référentiel</div></div>')
        a(f'<div class="chiffre"><div class="n">{c["bascules"]}</div>'
          f'<div class="l">analyses basculées<br>dans {c["communes_bascule"]} communes</div></div>')
        a('</div>')
        if (c["famille"] or "") == "metabolite":
            a(f'<p class="bnote">{NOTE_METABOLITE}</p>')
        a(f'<p class="bnote">Statut au référentiel : <b>{h(s[5] or "—")}</b>. '
          f'Sources : {h(s[6] or "—")}. Fiabilité : <b>{h(s[7] or "—")}</b>.'
          + (' <b>Valeur en « à vérifier » : elle est signalée comme telle '
             'et ne s\'arrondit jamais en « vérifié ».</b>'
             if (s[7] or "") != "verifie" else "") + '</p>')
        a('</section>')

    # --- ce que le corpus en contient -------------------------------------
    a('<section><h3 class="sec">Ce que le corpus en contient</h3>')
    a(f'<p class="bnote">Une substance n\'est présente que dans les bulletins '
      f'qui la cherchent : <b>{c["mesures"]} analyses sur les {c["corpus"]}</b> '
      f'que compte le corpus, dans {c["communes"]} communes. '
      f'{c["quantifiees"]} mesures sont quantifiées. Le dénombrement ne se lit '
      f'jamais sans ce dénominateur.</p>')
    if depts:
        a('<table><thead><tr><th>Département</th><th>Entrée au programme</th>'
          '<th class="num">Analyses</th><th class="num">Quantifiées</th>'
          '<th class="num">LQ médiane</th><th class="num">Basculées</th></tr></thead><tbody>')
        for r in depts:
            a(f'<tr><td>{h(r[0])}</td><td>{h(BF._date_fr(r[1]))}</td>'
              f'<td class="num">{r[2]}</td><td class="num">{r[3]}</td>'
              f'<td class="num">{h(BF._nb(r[4]))}</td><td class="num">{r[5]}</td></tr>')
        a('</tbody></table>')
        a('<p class="bnote"><b>Un taux de quantification ne se compare que si '
          'les limites de quantification se comparent</b> — une LQ plus fine '
          'trouve plus souvent, à eau identique. C\'est une capacité '
          'd\'instrument, jamais une négligence. Et avant la date d\'entrée au '
          'programme, le corpus ne dit rien : ni absence, ni apparition.</p>')
    a('</section>')

    # --- les cas de part et d'autre ---------------------------------------
    if cas:
        a('<section><h3 class="sec">De part et d\'autre de la date</h3>')
        a('<table><thead><tr><th>Commune</th><th>Prélèvement</th>'
          '<th class="num">Écart à la date</th><th class="num">Mesure</th>'
          '<th class="num">Valeur applicable</th><th>Verdict ce jour-là</th>'
          '</tr></thead><tbody>')
        for r in cas:
            ecart = f"+{r[4]} j" if r[4] >= 0 else f"{r[4]} j"
            lien = (f'<a href="{prefixe}commune/{h(r[1])}.html">{h(r[0])}</a>')
            a(f'<tr><td>{lien}</td><td>{h(BF._date_fr(r[3]))}</td>'
              f'<td class="num">{h(ecart)}</td>'
              f'<td class="num">{h(BF._nb(r[5]))}</td>'
              f'<td class="num">{h(BF._nb(r[6]))}</td>'
              f'<td>{"dépassement" if r[7] else "conforme"}</td></tr>')
        a('</tbody></table>')
        a('<p class="bnote">Le tableau porte les mesures les plus proches de la '
          'date, dans les deux sens — <b>y compris celles que le déplacement du '
          'seuil n\'absout pas</b>. Une page qui n\'alignerait que les cas '
          'favorables se lirait comme un plaidoyer.</p>')
        a('</section>')
    elif s and s[4] and not mesures_avant(con, libelle, version, s[4]):
        # Entrée au programme APRÈS le reclassement : il n'y a rien à montrer,
        # et c'est précisément ce qu'il faut écrire.
        a('<section><h3 class="sec">De part et d\'autre de la date</h3>'
          f'<p class="bnote"><b>Le corpus ne contient aucune mesure de cette '
          f'substance antérieure au {h(BF._date_fr(s[4]))}.</b> Elle est entrée '
          'au programme d\'analyse après son propre reclassement : aucun '
          'prélèvement n\'a jamais été noté contre l\'ancienne valeur. Les '
          'analyses dites « basculées » sont donc ici <b>entièrement '
          'contrefactuelles</b> — elles disent ce qu\'aurait valu ce résultat '
          'sous une règle qui n\'était déjà plus en vigueur quand on a commencé '
          'à le mesurer. Personne n\'a bu une eau requalifiée du jour au '
          'lendemain, et l\'écrire autrement serait faux.</p></section>')

    # --- ce que la page ne dit pas ----------------------------------------
    if d.get("limites"):
        a('<section><h3 class="sec">Ce que cette page ne dit pas</h3>'
          '<div class="prose"><ul>')
        for x in d["limites"]:
            a(f'<li>{h(x)}</li>')
        a('</ul></div></section>')

    # --- traçabilité -------------------------------------------------------
    a(f'<section><p class="bnote">Origine de la prose : '
      f'<b>{h(LIBELLE_ORIGINE[origine])}</b>. Les tableaux et les chiffres sont '
      f'dérivés de la base, version de référentiel {h(version)}. '
      f'On interroge ici la norme et son déplacement, jamais ceux qui '
      f'l\'appliquent.</p></section>')

    return "\n".join(o), libelle, origine

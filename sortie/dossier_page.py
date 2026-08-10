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

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

VALIDEES = os.path.join(ICI, "redactions_substances.json")
PROPOSEES = os.path.join(ICI, "redactions_substances_proposees.json")

LIBELLE_ORIGINE = {
    "auteur": "rédaction de l'auteur",
    "propose": "proposition de rédaction, à relire",
    "derive": "dérivé de la base",
}


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
    r = con.execute("""
        SELECT COUNT(*), COUNT(*) FILTER (WHERE v.est_quantifie),
               COUNT(DISTINCT a.code_insee),
               COUNT(*) FILTER (WHERE v.bascule_2016_2026),
               COUNT(DISTINCT a.code_insee) FILTER (WHERE v.bascule_2016_2026),
               COUNT(*) FILTER (WHERE v.depasse_applicable)
        FROM verdicts_figes v JOIN analyses_figees a
          USING (code_prelevement, version_referentiel)
        WHERE v.version_referentiel = ? AND v.libelle_parametre = ?
    """, [version, libelle]).fetchone()
    total = con.execute(
        "SELECT COUNT(*) FROM analyses_figees WHERE version_referentiel = ?",
        [version]).fetchone()[0]
    return dict(mesures=r[0], quantifiees=r[1], communes=r[2], bascules=r[3],
                communes_bascule=r[4], depassements=r[5], corpus=total)


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

    # --- le chapeau et les sections, prose ---------------------------------
    a('<section style="margin-top:0"><div class="prose">')
    if d.get("chapeau"):
        a(f'<p class="st">{h(d["chapeau"])}</p>')
    for sec in d.get("sections", []):
        a(f'<h4>{h(sec.get("t", ""))}</h4><p>{h(sec.get("x", ""))}</p>')
    a('</div></section>')

    # --- le seuil et sa date, dérivé --------------------------------------
    if s:
        a('<section><h3 class="sec">Le seuil, et sa date</h3><div class="chiffres">')
        a(f'<div class="chiffre"><div class="n">{h(BF._nb(s[2]))}</div>'
          f'<div class="l">valeur applicable avant<br>{h(s[1] or "")}</div></div>')
        a(f'<div class="chiffre bascule"><div class="n">{h(BF._nb(s[3]))}</div>'
          f'<div class="l">valeur applicable depuis<br>le {h(BF._date_fr(s[4]))}</div></div>'
          if s[4] else
          f'<div class="chiffre"><div class="n">{h(BF._nb(s[3]))}</div>'
          f'<div class="l">valeur applicable aujourd\'hui<br>sans date au référentiel</div></div>')
        a(f'<div class="chiffre"><div class="n">{c["bascules"]}</div>'
          f'<div class="l">analyses basculées<br>dans {c["communes_bascule"]} communes</div></div>')
        a('</div>')
        a(f'<p class="bnote">Nature du seuil : <b>{h(s[5] or "—")}</b>. '
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

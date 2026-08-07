# -*- coding: utf-8 -*-
"""
Point d'entrée du projet : « je veux travailler sur la commune 31520 ».

    python3 src/observer.py 31520
    python3 src/observer.py 31520 17415 31446      # codes postaux ou INSEE mêlés
    python3 src/observer.py 31520 --sans-repli     # pas de rattachement au réseau

Enchaînement complet :

    code postal -> code(s) INSEE          (un code postal peut couvrir
                                           plusieurs communes)
      -> points d'eau de la commune       (une installation amont = un point ;
                                           trois captages, trois analyses)
        -> dernier bulletin complet de chacun
          -> ingestion
            -> comparaison au référentiel, sommes
              -> sortie figée en base, estampillée

Règle de couverture (décidée le 7 août 2026)
--------------------------------------------
1. bulletin complet propre à la commune                  -> `analysee`
2. sinon, bulletin complet du même réseau prélevé dans
   une commune voisine, la commune de prélèvement étant
   affichée                                              -> `rattachee_reseau`
3. sinon                                                 -> `non_documentee`

« non documentée » n'est ni conforme ni non conforme : c'est une absence de
donnée, et elle doit rester visible comme telle. La faire disparaître de la
carte reviendrait à présenter un indéterminé comme un conforme (CLAUDE.md §2.4).
"""
import argparse
import os
import sys

import duckdb

import figer
import hubeau
import ingest
from common import DB_PATH, SEUIL_COMPLET


def resoudre(code):
    """Code postal ou code INSEE -> [{code_insee, nom, lon, lat, ...}]."""
    code = str(code).strip()
    if len(code) == 5 and code.isdigit():
        communes = hubeau.communes_par_code_postal(code)
        if communes:
            return communes
    return [hubeau.commune_par_insee(code)]


def _ingerer(con, insee, commune, rows, dept):
    meta = hubeau.bulletin_meta(insee, commune.get("nom"), dept, rows)
    meta.update({"codes_postaux": commune.get("codes_postaux"),
                 "lon": commune.get("lon"), "lat": commune.get("lat")})
    return meta, ingest.ingest_bulletin(con, meta, rows)


def traiter(con, commune, depuis=None, tous=False, repli=True):
    """Collecte, ingère et renvoie (statut, [code_prelevement], commune_prelevement)."""
    insee = commune["code_insee"]
    dept = insee[:2]
    nom = commune.get("nom") or insee

    bulletins = hubeau.derniers_bulletins_complets(insee, depuis=depuis, tous=tous)
    if bulletins:
        codes = []
        for _cp, rows in bulletins.items():
            meta, (code_prel, nb, complet) = _ingerer(con, insee, commune, rows, dept)
            codes.append(code_prel)
            print(f"  {meta['date_prelevement']}  "
                  f"{meta.get('nom_installation_amont') or 'installation non renseignée'}"
                  f"  — {nb} paramètres")
        return "analysee", codes, None

    if not repli:
        return "non_documentee", [], None

    # Repli : la même eau, prélevée ailleurs sur le même réseau.
    #
    # Le prélèvement est ingéré sous la commune où il a RÉELLEMENT eu lieu.
    # L'attacher à la commune étudiée serait faux, et ferait se disputer la
    # même clé par deux communes dès que la voisine serait analysée à son
    # tour. Le rattachement vit dans couverture_communes, pas dans le fait.
    reseaux = hubeau.reseaux_de_la_commune(insee, depuis=depuis)
    for code_reseau, nom_reseau in reseaux.items():
        trouve = hubeau.bulletin_du_reseau(code_reseau, depuis=depuis)
        if not trouve:
            continue
        rows, insee_prel, _nom_prel = trouve
        commune_prel = hubeau.commune_par_insee(insee_prel)
        meta, (code_prel, nb, _complet) = _ingerer(
            con, insee_prel, commune_prel, rows, insee_prel[:2])
        libelle = commune_prel.get("nom") or insee_prel
        print(f"  {meta['date_prelevement']}  réseau {nom_reseau or code_reseau}"
              f"  — {nb} paramètres, prélevé à {libelle}")
        return "rattachee_reseau", [code_prel], libelle

    print(f"  aucun bulletin complet (> {SEUIL_COMPLET} paramètres), "
          f"ni pour la commune ni pour son réseau")
    return "non_documentee", [], None


def observer(codes, depuis=None, tous=False, repli=True, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : python3 src/build_db.py")
        sys.exit(1)

    con = duckdb.connect(db)
    try:
        con.execute(figer.SCHEMA_FIGE)
        version = figer.version_referentiel()
        print(f"référentiel : version {version}\n")

        traitees = []
        for code in codes:
            for commune in resoudre(code):
                insee = commune["code_insee"]
                commune.setdefault("dept", insee[:2])
                etiquette = f"{insee} {commune.get('nom') or ''}".strip()
                if str(code) != insee:
                    etiquette = f"{code} -> {etiquette}"
                print(f"[{etiquette}]")
                statut, prels, commune_prel = traiter(
                    con, commune, depuis=depuis, tous=tous, repli=repli)
                traitees.append((commune, statut, prels, commune_prel))

        version, n = figer.figer(con, version=version)
        for commune, statut, prels, commune_prel in traitees:
            figer.figer_commune(con, commune, statut, version,
                                code_prelevement=prels[0] if prels else None,
                                commune_prelevement=commune_prel)

        print(f"\nfigé : {n} bulletin(s) en base, version de référentiel {version}")
        _restituer(con, version, [t[0]['code_insee'] for t in traitees])
    finally:
        con.close()


def _restituer(con, version, insees):
    """Ce que la base contient maintenant pour ces communes."""
    marques = ",".join("?" * len(insees))
    print("\n=== Analyses figées ===")
    rows = con.execute(f"""
        SELECT commune, date_prelevement, nom_installation_amont,
               nb_parametres, nb_mesures_notees, pct_couverture,
               nb_depasse_2026, nb_bascules, nb_indetermines,
               nb_synthese_quantifiees, ROUND(charge_synthese_ug_l, 4),
               ROUND(indice_danger, 2)
        FROM analyses_figees
        WHERE version_referentiel = ? AND code_insee IN ({marques})
        ORDER BY commune, date_prelevement DESC
    """, [version] + insees).fetchall()
    for r in rows:
        print(f"\n  {r[0]} — {r[1]} — {r[2] or 'installation non renseignée'}")
        print(f"    {r[4]} paramètres notés sur {r[3]} mesurés ({r[5]} % de couverture)")
        print(f"    dépassements 2026 : {r[6]}   bascules : {r[7]}   indéterminés : {r[8]}")
        print(f"    substances de synthèse quantifiées : {r[9]}"
              + (f"   charge cumulée ≥ {r[10]} µg/L" if r[10] is not None else ""))
        if r[11] is not None:
            print(f"    indice de danger (méthode simplifiée) : {r[11]}"
                  " — raisonnement, pas mesure (docs/METHODE_EFFET_COCKTAIL.md)")

    non_doc = con.execute(f"""
        SELECT commune, code_insee FROM couverture_communes
        WHERE version_referentiel = ? AND statut = 'non_documentee'
          AND code_insee IN ({marques})
    """, [version] + insees).fetchall()
    for c in non_doc:
        print(f"\n  {c[0] or c[1]} — NON DOCUMENTÉE : aucun bulletin complet.")
        print("    Ce n'est ni « conforme » ni « non conforme » : on ne sait pas.")

    rattachees = con.execute(f"""
        SELECT cc.commune, cc.commune_prelevement, a.date_prelevement,
               a.nb_mesures_notees, a.nb_parametres, a.pct_couverture,
               a.nb_depasse_2026, a.nb_bascules
        FROM couverture_communes cc
        LEFT JOIN analyses_figees a
               ON a.code_prelevement = cc.code_prelevement
              AND a.version_referentiel = cc.version_referentiel
        WHERE cc.version_referentiel = ? AND cc.statut = 'rattachee_reseau'
          AND cc.code_insee IN ({marques})
    """, [version] + insees).fetchall()
    for c in rattachees:
        print(f"\n  {c[0] or ''} — RATTACHÉE AU RÉSEAU")
        print("    aucun bulletin complet propre ; analyse du même réseau,")
        print(f"    prélevée à {c[1]} le {c[2]}")
        print(f"    {c[3]} paramètres notés sur {c[4]} mesurés ({c[5]} % de couverture)")
        print(f"    dépassements 2026 : {c[6]}   bascules : {c[7]}")
        print("    la commune de prélèvement doit figurer dans toute sortie publique")


def main():
    p = argparse.ArgumentParser(
        description="Analyser une commune par son code postal ou son code INSEE")
    p.add_argument("codes", nargs="+", help="codes postaux ou codes INSEE")
    p.add_argument("--depuis", help="année minimale de prélèvement (ex. 2020)")
    p.add_argument("--tous", action="store_true",
                   help="tous les bulletins complets de chaque point d'eau")
    p.add_argument("--sans-repli", action="store_true",
                   help="ne pas rattacher au réseau si la commune n'a pas de bulletin")
    a = p.parse_args()
    observer(a.codes, depuis=a.depuis, tous=a.tous, repli=not a.sans_repli)


if __name__ == "__main__":
    main()

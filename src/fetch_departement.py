# -*- coding: utf-8 -*-
"""
Collecte automatique à l'échelle d'un département.

    py -X utf8 src/fetch_departement.py --dept 81 --limite 10   # essai, mesuré
    py -X utf8 src/fetch_departement.py --dept 81 --tous        # le département
    py -X utf8 src/fetch_departement.py --dept 81 --figer       # fige sans rien collecter
    py -X utf8 src/fetch_departement.py --dept 81 --rapport     # relit le journal

Ce script fait des requêtes HTTP : il doit tourner dans un environnement avec
accès réseau depuis le shell (la machine de Yannick, Claude Code) — pas dans un
bac à sable. Voir CLAUDE.md §3.1.

Ce qu'il fait :
  1. énumère les communes du département — **un seul appel**, centroïdes
     compris, parce que `couverture_communes` porte les coordonnées et que
     c'est elle que colorie la carte ;
  2. pour chaque commune, applique la règle de couverture de `collecte.py` :
     bulletin propre, sinon bulletin du réseau prélevé ailleurs, sinon
     « non documentée » ;
  3. écrit chaque bulletin brut au cache (`brut.py`) avant de l'ingérer ;
  4. journalise, de façon reprenable après coupure ;
  5. **fige** — sans quoi rien n'est publiable et la carte reste vide.

Ce que ce fichier ne fait plus
------------------------------
Il portait sa propre version de la collecte, sans repli réseau, sans couverture
et sans figeage : lancé sur un département, il aurait rempli `prelevements` et
`mesures` sans produire une seule page ni une seule commune sur la carte. La
règle vit désormais dans `collecte.py`, partagée avec `observer.py`.

L'accès réseau est entièrement dans `src/hubeau.py`.
"""
import argparse
import collections
import json
import os
import sys
import time

import duckdb

import brut
import collecte
import figer
import hubeau
from common import DB_PATH, JOURNAL_DIR, SEUIL_COMPLET


# ---------------------------------------------------------------------------
# Journal de reprise
#
# Il porte de quoi REFIGER sans réseau : statut, prélèvements retenus, commune
# de prélèvement, et l'identité complète de la commune (nom, coordonnées). Une
# collecte interrompue se termine donc par `--figer`, sans redemander une seule
# ligne à Hub'Eau.
# ---------------------------------------------------------------------------
def chemin_journal(dept):
    os.makedirs(JOURNAL_DIR, exist_ok=True)
    return os.path.join(JOURNAL_DIR, f"dept_{dept}.jsonl")


def lire_journal(dept):
    """{code_insee: dernière entrée} — permet de reprendre où on s'est arrêté."""
    chemin = chemin_journal(dept)
    vu = {}
    if not os.path.exists(chemin):
        return vu
    with open(chemin, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                e = json.loads(ligne)
            except json.JSONDecodeError:
                continue
            if e.get("code_insee"):
                vu[e["code_insee"]] = e
    return vu


def ecrire_journal(dept, entree):
    with open(chemin_journal(dept), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entree, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# L'énumération des communes, mise au cache elle aussi
#
# Elle coûte un appel, mais elle porte les centroïdes — donc la position de
# chaque commune sur la carte, y compris celles qui n'auront jamais de bulletin.
# La garder rend la réingestion depuis le cache entièrement hors ligne : sans
# elle, une commune réingérée après une perte de base n'aurait plus de lon/lat
# et disparaîtrait de la carte sans que rien ne le signale.
# ---------------------------------------------------------------------------
def chemin_communes(dept):
    return os.path.join(brut.BRUT_DIR, str(dept), "_communes.json")


def ecrire_communes_cache(dept, communes):
    os.makedirs(os.path.dirname(chemin_communes(dept)), exist_ok=True)
    with open(chemin_communes(dept), "w", encoding="utf-8") as fh:
        json.dump(communes, fh, ensure_ascii=False, indent=1, sort_keys=True)


def lire_communes_cache(dept):
    """
    L'énumération mise au cache, ou {} si elle est absente ou illisible.

    `utf-8-sig` et non `utf-8` : un fichier réécrit à la main sous Windows
    porte souvent un BOM, et `json.load` refuse de le lire. Un cache illisible
    ne doit pas faire tomber l'appelant — il doit se lire comme une absence,
    parce que le script de reprise automatique interroge cette fonction pour
    savoir s'il reste du travail, et qu'une exception à ce moment-là ferait
    échouer la reprise sans que personne ne le voie.
    """
    chem = chemin_communes(dept)
    if not os.path.exists(chem):
        return {}
    try:
        with open(chem, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(f"  cache d'énumération illisible ({type(e).__name__}) : {chem}")
        return {}


# ---------------------------------------------------------------------------
# Réingestion depuis le cache — sans réseau
# ---------------------------------------------------------------------------
def reingerer_departement(dept, db=DB_PATH):
    """
    Rejoue tout le cache brut dans la base, **sans un seul appel réseau**.

    C'est la raison d'être du cache, et le filet de sécurité de la collecte à
    l'échelle. Trois cas où l'on en a besoin :

      · la base a été perdue, corrompue, ou reconstruite par `build_db.py` ;
      · un bug d'ingestion a été corrigé et il faut relire la matière première ;
      · une coupure a laissé le journal en avance sur la base — le journal dit
        « commune traitée » alors que l'écriture DuckDB de la dernière n'a pas
        abouti. Ici on ne fait pas confiance au journal : on relit les fichiers.

    L'ingestion est idempotente (DELETE puis INSERT sur `code_prelevement`),
    donc relancer cette commande ne duplique rien.
    """
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : py -X utf8 src/build_db.py")
        sys.exit(1)

    entrees = brut.lister(dept)
    if not entrees:
        print(f"cache brut vide pour le département {dept} — rien à réingérer")
        return 0

    communes = lire_communes_cache(dept)
    print(f"réingestion : {len(entrees)} bulletin(s) du cache, sans réseau")
    con = duckdb.connect(db)
    n = 0
    try:
        for _d, cp, _chem in entrees:
            rows = brut.lire(dept, cp)
            if not rows:
                print(f"  {cp} — illisible, ignoré")
                continue
            r0 = rows[0]
            insee = str(r0.get("code_commune") or "")
            # L'identité vient du cache d'énumération quand elle y est : elle
            # porte les coordonnées. Sinon on retombe sur ce que la ligne dit
            # d'elle-même, quitte à n'avoir pas de position.
            commune = dict(communes.get(insee) or
                           {"code_insee": insee, "nom": r0.get("nom_commune")})
            commune.setdefault("code_insee", insee)
            collecte._ingerer(con, insee, commune, rows, insee[:2] or dept)
            n += 1
            if n % 100 == 0:
                print(f"  {n}/{len(entrees)}")
    finally:
        con.close()
    print(f"réingéré : {n} bulletin(s)")
    return n


# ---------------------------------------------------------------------------
# Figeage — séparé de la collecte, et rejouable depuis le journal
# ---------------------------------------------------------------------------
def figer_departement(dept, db=DB_PATH, verbeux=True):
    """
    Fige les bulletins et inscrit la couverture des communes du journal.

    Séparé de la collecte pour deux raisons. D'abord la reprise : une coupure
    au milieu d'un département ne doit pas coûter le figeage de ce qui a été
    obtenu. Ensuite le coût : `figer.figer()` recalcule TOUT le corpus, et
    l'appeler à chaque commune serait quadratique.
    """
    vu = lire_journal(dept)
    if not vu:
        print(f"aucun journal pour le département {dept} — rien à figer")
        return None, 0

    con = duckdb.connect(db)
    try:
        figer.assurer_schema(con)
        version = figer.version_referentiel()
        version, n = figer.figer(con, version=version)
        for e in vu.values():
            if e.get("etat") == "erreur":
                continue
            commune = {"code_insee": e["code_insee"], "nom": e.get("nom"),
                       "dept": dept, "codes_postaux": e.get("codes_postaux"),
                       "lon": e.get("lon"), "lat": e.get("lat")}
            prels = e.get("prelevements") or []
            figer.figer_commune(con, commune, e.get("statut", "non_documentee"),
                                version,
                                code_prelevement=prels[0] if prels else None,
                                commune_prelevement=e.get("commune_prelevement"))
        # `figer()` l'a déjà appelée, mais AVANT la boucle ci-dessus. On repasse
        # pour attraper les communes qui n'ont de bulletin que par le repli —
        # celui-ci est ingéré sous la commune où il a réellement eu lieu, qui
        # n'est pas forcément au journal. La fonction n'écrase jamais une ligne
        # existante : les statuts inscrits ci-dessus, plus précis, sont gardés.
        figer.figer_couverture_implicite(con, version)
        if verbeux:
            print(f"\nfigé : {n} bulletin(s), version de référentiel {version}")
        return version, n
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Rapport de couverture
#
# Il lit `analyses_figees`, JAMAIS `v_prelevement_verdict`
# -------------------------------------------------------
# Défaut réel, trouvé le 11 août 2026 en recomptant le Rhône. Ce rapport
# interrogeait `v_prelevement_verdict`, une vue qui suit le référentiel **du
# jour**. Les chiffres qu'il imprimait n'avaient donc pas de version, et ceux
# recopiés au journal de reprise sont devenus irreproductibles : le « 295
# bulletins complets, 155 cas, 52 % » du Rhône partiel n'existe dans AUCUNE
# version figée — sous `435b9a089f1d` le département porte 17 bulletins
# complets et 0 cas. Deux jours de raisonnement ont porté sur ce chiffre-là.
#
# C'est le §8bis pris en défaut chez nous — « ne jamais recalculer un verdict à
# la volée : une vue suit le référentiel du jour, une ligne figée dit contre
# quelle grille elle a été calculée » — et l'obligation 9, « chaque écran porte
# sa traçabilité ». Un rapport de collecte est un écran comme un autre.
#
# Le rapport annonce donc **la version qu'il lit**, et signale quand le
# référentiel a bougé depuis le dernier figeage : sans cet avertissement, on
# relève de bonne foi des chiffres périmés.
# ---------------------------------------------------------------------------
def _figeage_courant(con, dept):
    """
    (version, calcule_le, n) du figeage le plus récent de ce département, ou None.

    On prend le figeage le plus récent **du département**, pas la version
    courante du référentiel : le rapport doit dire ce qui EST figé, pas ce qui
    devrait l'être. L'écart entre les deux est précisément ce qu'il signale.
    """
    existe = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_name = 'analyses_figees'").fetchone()[0]
    if not existe:
        return None
    return con.execute("""
        SELECT version_referentiel, MAX(calcule_le) AS le, COUNT(*) AS n
        FROM analyses_figees WHERE dept = ?
        GROUP BY version_referentiel
        ORDER BY le DESC, n DESC LIMIT 1
    """, [dept]).fetchone()


def rapport(dept, db=DB_PATH):
    vu = lire_journal(dept)
    if vu:
        etats = collections.Counter(e.get("statut") or e.get("etat")
                                    for e in vu.values())
        total = len(vu)
        print(f"\n=== Couverture département {dept} ===")
        print(f"communes traitées        : {total}")
        for etat, n in etats.most_common():
            print(f"  {etat:<22} {n:>5}  ({100*n/total:.1f} %)")

        bulletins = sum(len(e.get("prelevements") or []) for e in vu.values())
        print(f"bulletins retenus        : {bulletins}")

    etat_cache = brut.etat(dept)
    print(f"cache brut               : {etat_cache['bulletins']} bulletin(s), "
          f"{etat_cache['mo']} Mo")

    if not os.path.exists(db):
        return
    con = duckdb.connect(db, read_only=True)
    try:
        fige = _figeage_courant(con, dept)
        if not fige:
            print(f"\nen base — aucune analyse figée pour le département {dept}.")
            print("          Rien n'est publiable et aucun chiffre n'est citable "
                  "tant que le figeage n'a pas eu lieu :")
            print(f"          py -X utf8 src/fetch_departement.py --dept {dept} --figer")
            return
        version, calcule_le, _n = fige

        r = con.execute("""
            SELECT COUNT(*) FILTER (WHERE est_complet),
                   COUNT(*) FILTER (WHERE est_complet AND nb_depasse_2026 = 0
                                    AND nb_bascules > 0),
                   SUM(nb_bascules) FILTER (WHERE est_complet),
                   ROUND(AVG(pct_couverture) FILTER (WHERE est_complet), 1)
            FROM analyses_figees
            WHERE dept = ? AND version_referentiel = ?
        """, [dept, version]).fetchone()

        print(f"\nfigé    — version de référentiel {version}, "
              f"calculé le {calcule_le}")
        print(f"          bulletins complets : {r[0] or 0}")
        print(f"          couverture moyenne des mesures : {r[3] or 0} %")
        print(f"          conformes 2026 AVEC bascule : {r[1] or 0}   <-- les cas")
        print(f"          bascules cumulées : {r[2] or 0}")
        print(f"          tout chiffre repris d'ici se cite AVEC {version}")

        courante = figer.version_referentiel()
        if courante != version:
            print(f"\n  ! le référentiel a changé depuis ce figeage "
                  f"({version} -> {courante})")
            print("    les chiffres ci-dessus sont ceux de l'ANCIENNE grille. "
                  "Pour les mettre à jour :")
            print(f"    py -X utf8 src/build_db.py && "
                  f"py -X utf8 src/fetch_departement.py --dept {dept} --figer")

        # Diagnostic de couverture, et non verdict : celui-ci se lit bien sur une
        # vue vivante, puisqu'il décrit l'état du référentiel du jour et non le
        # sort d'un bulletin. Il est étiqueté pour qu'on ne s'y trompe pas.
        na = con.execute("SELECT COUNT(*) FROM v_parametres_non_apparies").fetchone()[0]
        print(f"\nvue vivante (référentiel du jour, non figé) —")
        print(f"          libellés sans aucun seuil de comparaison : {na}")
        print("          (SELECT * FROM v_parametres_non_apparies LIMIT 40)")
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------
def run(dept, limite=None, depuis=None, tous=False, repli=True, cache=True,
        reprendre=True, figeage=True, db=DB_PATH):
    if not os.path.exists(db):
        print(f"base absente : {db}\nlance d'abord : py -X utf8 src/build_db.py")
        sys.exit(1)

    communes = hubeau.communes_departement(dept)
    ecrire_communes_cache(dept, communes)
    print(f"communes  : {len(communes)} dans le département {dept} "
          f"(geo.api.gouv.fr, centroïdes compris — un appel, mis au cache)")

    vu = lire_journal(dept) if reprendre else {}
    if vu:
        print(f"journal   : {len(vu)} commune(s) déjà traitée(s), reprise")

    # Une commune EN ERREUR n'est pas une commune faite.
    #
    # Défaut réel, trouvé le 8 août 2026 en dépouillant la première collecte
    # départementale : neuf communes du Tarn — dont Castres et Cordes-sur-Ciel —
    # ont échoué sur des coupures réseau de Hub'Eau, sept d'affilée. Le journal
    # portait bien leur échec, mais la reprise les considérait comme traitées et
    # ne les redemandait jamais. Elles seraient restées « non documentées » à
    # tort, ce qui est précisément le pire cas du §2.4 transposé à la commune :
    # une absence de donnée qui n'est pas une absence de fait, présentée comme
    # un état stable. Un échec réseau est transitoire ; il se retente.
    a_faire = [c for i, c in sorted(communes.items())
               if (vu.get(i) or {}).get("etat") in (None, "erreur")]
    a_retenter = sum(1 for c in a_faire if c["code_insee"] in vu)
    if a_retenter:
        print(f"reprise   : {a_retenter} commune(s) en erreur à retenter")
    if limite:
        a_faire = a_faire[:limite]
    print(f"à traiter : {len(a_faire)} commune(s)")
    print(f"règle     : {'TOUS les bulletins complets' if tous else 'le dernier bulletin'} "
          f"de chaque point d'eau"
          + (f", depuis {depuis}" if depuis else ", sans borne de date")
          + f" (> {SEUIL_COMPLET} paramètres)\n")

    collecte.reinitialiser_stats()
    con = duckdb.connect(db)
    t0 = time.time()
    stats = collections.Counter()
    interrompu = False
    consecutives = 0
    try:
        for idx, commune in enumerate(a_faire, 1):
            insee = commune["code_insee"]
            commune.setdefault("dept", dept)
            print(f"[{idx}/{len(a_faire)}] {insee} {commune.get('nom') or ''}".strip())
            try:
                statut, prels, commune_prel = collecte.traiter_commune(
                    con, commune, depuis=depuis, tous=tous, repli=repli, cache=cache)
            except Exception as e:
                print(f"  ERREUR : {type(e).__name__}: {e}")
                ecrire_journal(dept, {"code_insee": insee, "nom": commune.get("nom"),
                                      "etat": "erreur", "message": str(e)})
                stats["erreur"] += 1
                # Les échecs arrivent en rafale : sept communes consécutives du
                # Tarn sont tombées sur la même coupure. Insister au même rythme
                # ne sert à rien et n'est pas courtois envers un service public
                # gratuit (§3.2) — on laisse le temps à l'hôte de revenir.
                consecutives += 1
                if consecutives >= 3:
                    attente = min(60, 5 * consecutives)
                    print(f"  {consecutives} échecs d'affilée — pause de {attente}s")
                    time.sleep(attente)
                continue
            consecutives = 0

            ecrire_journal(dept, {
                "code_insee": insee, "nom": commune.get("nom"),
                "codes_postaux": commune.get("codes_postaux"),
                "lon": commune.get("lon"), "lat": commune.get("lat"),
                "etat": "traitee", "statut": statut,
                "prelevements": prels, "commune_prelevement": commune_prel,
            })
            stats[statut] += 1
            time.sleep(hubeau.PAUSE_COMMUNE)
    except KeyboardInterrupt:
        interrompu = True
        print("\ninterruption — le journal permet de reprendre par la même commande")
    finally:
        con.close()

    duree = time.time() - t0
    print(f"\nterminé en {duree/60:.1f} min — "
          + ", ".join(f"{k}: {v}" for k, v in stats.most_common()))
    traitees = sum(stats.values()) or 1
    print(f"  {duree/traitees:.1f} s par commune")
    print(f"  bulletins rapatriés du réseau : {collecte.STATS['bulletins_du_reseau']}")
    print(f"  bulletins relus au cache      : {collecte.STATS['bulletins_du_cache']}"
          "   <-- autant d'appels épargnés à Hub'Eau")

    if figeage and not interrompu:
        figer_departement(dept, db)
    elif interrompu:
        print("\nrien n'a été figé — pour figer ce qui est déjà collecté :")
        print(f"  py -X utf8 src/fetch_departement.py --dept {dept} --figer")
    rapport(dept, db)


def main():
    p = argparse.ArgumentParser(description="Collecte Hub'Eau à l'échelle d'un département")
    p.add_argument("--dept", required=True, help="code département (ex. 81, 2A, 971)")
    p.add_argument("--limite", type=int, help="ne traiter que les N premières communes (essai)")
    p.add_argument("--depuis", help="année minimale de prélèvement (ex. 2020)")
    p.add_argument("--tous", action="store_true",
                   help="tous les bulletins complets de chaque point d'eau, pas seulement le dernier")
    p.add_argument("--sans-repli", action="store_true",
                   help="ne pas rattacher au réseau si la commune n'a pas de bulletin")
    p.add_argument("--sans-cache", action="store_true",
                   help="ignorer le cache brut et tout redemander au réseau")
    p.add_argument("--reprendre-a-zero", action="store_true",
                   help="ignorer le journal et retraiter toutes les communes")
    p.add_argument("--figer", action="store_true",
                   help="figer depuis le journal, sans rien collecter")
    p.add_argument("--reingerer", action="store_true",
                   help="rejouer tout le cache brut dans la base, sans réseau, puis figer")
    p.add_argument("--rapport", action="store_true",
                   help="afficher la couverture sans rien collecter")
    p.add_argument("--termine", action="store_true",
                   help="code de sortie 0 si le département est entièrement traité, 1 sinon "
                        "(sert au script de reprise automatique)")
    a = p.parse_args()

    if a.termine:
        communes = lire_communes_cache(a.dept)
        vu = lire_journal(a.dept)
        if not communes:
            print(f"département {a.dept} : pas de cache d'énumération, état inconnu")
            sys.exit(1)
        # Même règle que la reprise : une commune en erreur reste à faire.
        # Sans cela, `--termine` annoncerait « terminé » sur un département
        # amputé de ses échecs réseau.
        reste = [i for i in communes
                 if (vu.get(i) or {}).get("etat") in (None, "erreur")]
        en_erreur = sum(1 for i in communes if (vu.get(i) or {}).get("etat") == "erreur")
        faites = len(communes) - len(reste)
        print(f"département {a.dept} : {faites}/{len(communes)} communes traitées, "
              f"{len(reste)} restante(s)"
              + (f" dont {en_erreur} en erreur, à retenter" if en_erreur else ""))
        sys.exit(1 if reste else 0)
    if a.rapport:
        rapport(a.dept)
        return
    if a.reingerer:
        reingerer_departement(a.dept)
        figer_departement(a.dept)
        rapport(a.dept)
        return
    if a.figer:
        figer_departement(a.dept)
        rapport(a.dept)
        return
    run(a.dept, limite=a.limite, depuis=a.depuis, tous=a.tous,
        repli=not a.sans_repli, cache=not a.sans_cache,
        reprendre=not a.reprendre_a_zero)


if __name__ == "__main__":
    main()

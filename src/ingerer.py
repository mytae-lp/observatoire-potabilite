# -*- coding: utf-8 -*-
"""
Verser le tampon dans la base — **sans réseau**, et en quelques minutes.

    py -X utf8 src/ingerer.py --depts 69,71,01     # ingère puis fige
    py -X utf8 src/ingerer.py --tous               # tout ce que le cache porte
    py -X utf8 src/ingerer.py --etat               # ce qui attend, sans rien écrire
    py -X utf8 src/ingerer.py --depts 69 --tout    # réingère même ce qui est en base
    py -X utf8 src/ingerer.py --depts 69 --sans-figer

C'est la seconde moitié de `src/moisson.py`, et la seule qui prend le verrou
DuckDB. Elle le prend le plus tard possible, le rend le plus tôt possible, et
dit combien de temps elle l'a tenu.

Pourquoi ce fichier existe
--------------------------
Une collecte départementale durait deux à trois heures **verrou tenu** :
`fetch_departement.run()` ouvrait la base avant la première commune et la
fermait après la dernière. Aucun autre processus ne pouvait alors ouvrir
`data/eau.duckdb`, pas même en lecture seule. Or l'écriture ne représente
qu'une petite part de cette durée : le reste est de l'attente réseau, et elle
n'a aucune raison d'être faite le verrou à la main.

La matière première est déjà sur disque — `data/brut/<dept>/*.jsonl.gz`, écrit
par la moisson — et l'identité des communes aussi (`_communes.json`,
centroïdes compris). Il ne reste qu'à relire et insérer.

Ce qui est déjà fait se lit dans la base, pas dans un fichier d'état
--------------------------------------------------------------------
Par défaut, un prélèvement déjà présent dans `prelevements` n'est pas
réingéré : l'idempotence se lit dans la sortie elle-même, sans journal
parallèle qui pourrait mentir. Deux cas demandent `--tout`, et il faut les
connaître :

  · **un bug d'ingestion a été corrigé** — la base porte des lignes calculées
    par l'ancien code, et rien ne les distingue ; il faut tout relire ;
  · **le cache a été refait** (`--sans-cache` à la moisson) — le fichier a
    changé, le `code_prelevement` non.

`--tout` est sans danger : l'ingestion est idempotente (DELETE puis INSERT sur
`code_prelevement`), elle coûte seulement du temps.

Le figeage est incrémental, et c'est ce qui borne la durée du verrou
--------------------------------------------------------------------
Mesuré le 11 août 2026 : verser 65 bulletins coûtait 1,3 min, et le figeage
qui suivait 32,4 min — parce qu'il refigeait les 4 745 bulletins du corpus.
Le verrou de trois heures aurait simplement été remplacé par un verrou qui
croît avec le corpus. `figer.figer()` ne refige donc plus que ce qui n'est pas
déjà figé sous la version courante ; le détail de ce qui rend cela sûr, et du
seul cas qui échappe à la règle, est dans sa docstring et dans
`figer.version_moteur()`.

Il reste appelé **une seule fois** à la fin pour tout le lot — jamais une fois
par département, encore moins par commune : il balaie le corpus pour savoir ce
qui manque, et ce balayage n'a pas à être refait N fois.

`--refiger` force le refigeage complet. Il est long, et il n'est pas censé
servir souvent : le changement de référentiel comme le changement de code de
calcul le déclenchent d'eux-mêmes.
"""
import argparse
import collections
import os
import sys
import time

import duckdb

import brut
import collecte
import figer
import journal
from common import DB_PATH
from console import dire_brut

# Toutes les N insertions, on referme la transaction. Une seule transaction
# géante rendrait une interruption totalement stérile ; une transaction par
# bulletin coûterait un fsync par bulletin. Entre les deux, un lot perdu au
# pire — et il se relance sans précaution, l'ingestion étant idempotente.
LOT = 200

# Attente maximale quand la base est déjà prise par un autre processus.
# On préfère patienter que rendre la main : l'ingestion est le geste que
# l'utilisateur a demandé, et l'autre processus (une fiche, un figeage) dure
# rarement plus de quelques minutes.
ATTENTE_VERROU = 600
PAUSE_VERROU = 10


def ouvrir(db=DB_PATH, lecture_seule=False, attendre=ATTENTE_VERROU):
    """
    Ouvre la base, en patientant si elle est prise.

    DuckDB n'a qu'un seul écrivain : tant qu'un autre processus la tient, tout
    `connect()` échoue. Plutôt que d'abandonner, on redemande — et on **dit**
    qu'on attend, avec le message d'origine, qui nomme le processus fautif.
    Sans cette trace, une ingestion qui patiente est indiscernable d'une
    ingestion gelée, et c'est précisément le diagnostic qui a coûté trois
    soirées sur le Rhône.
    """
    limite = time.time() + attendre
    annonce = False
    while True:
        try:
            return duckdb.connect(db, read_only=lecture_seule)
        except Exception as e:
            if time.time() >= limite:
                raise
            if not annonce:
                dire_brut(f"\nla base est prise par un autre processus — attente "
                          f"(jusqu'à {attendre//60} min)")
                dire_brut(f"  {type(e).__name__}: {e}")
                annonce = True
            time.sleep(PAUSE_VERROU)


def deja_en_base(con):
    """Les `code_prelevement` déjà présents — l'idempotence lue dans la sortie."""
    existe = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_name = 'prelevements'").fetchone()[0]
    if not existe:
        return set()
    return {r[0] for r in con.execute(
        "SELECT code_prelevement FROM prelevements").fetchall()}


def a_ingerer(dept, connus, tout=False):
    """
    [(code_prelevement, chemin)] du cache brut de ce département qui reste à verser.

    Le cache fait foi sur la matière première, pas le journal : une coupure
    peut laisser le journal en avance sur les fichiers, ou l'inverse. On relit
    ce qui est réellement sur disque.
    """
    entrees = brut.lister(dept)
    if tout:
        return [(cp, chem) for _d, cp, chem in entrees]
    return [(cp, chem) for _d, cp, chem in entrees if cp not in connus]


def ingerer_departement(con, dept, connus, tout=False, verbeux=True):
    """Verse le cache brut d'un département dans la base ouverte. Retourne (n, ignores)."""
    restants = a_ingerer(dept, connus, tout=tout)
    if not restants:
        dire_brut(f"  {dept} : rien de nouveau au cache brut")
        return 0, 0

    communes = journal.lire_communes_cache(dept)
    if not communes:
        dire_brut(f"  {dept} : pas de cache d'énumération — les coordonnées "
                  f"manqueront, et les communes sans bulletin ne seront pas "
                  f"placées sur la carte")

    dire_brut(f"  {dept} : {len(restants)} bulletin(s) à verser")
    n, ignores = 0, 0
    con.execute("BEGIN")
    try:
        for cp, _chem in restants:
            rows = brut.lire(dept, cp)
            if not rows:
                dire_brut(f"    {cp} — illisible, ignoré")
                ignores += 1
                continue
            r0 = rows[0]
            insee = str(r0.get("code_commune") or "")
            # L'identité vient du cache d'énumération quand elle y est : elle
            # porte les coordonnées. Sinon on retombe sur ce que la ligne dit
            # d'elle-même, quitte à n'avoir pas de position.
            commune = dict(communes.get(insee) or
                           {"code_insee": insee, "nom": r0.get("nom_commune")})
            commune.setdefault("code_insee", insee)
            try:
                collecte._ingerer(con, insee, commune, rows, insee[:2] or dept)
            except Exception as e:
                dire_brut(f"    {cp} — {type(e).__name__}: {e}")
                ignores += 1
                continue
            n += 1
            connus.add(cp)
            if n % LOT == 0:
                con.execute("COMMIT")
                con.execute("BEGIN")
                if verbeux:
                    dire_brut(f"    {n}/{len(restants)}")
        con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise
    return n, ignores


def figer_departements(con, depts, complet=False):
    """
    Fige une fois pour tous les départements, puis inscrit leur couverture.

    **Une seule fois pour tout le lot** : `figer.figer()` balaie le corpus, et
    l'appeler par département referait N fois le même parcours. La couverture,
    elle, est propre à chaque département et se relit dans son journal.
    """
    figer.assurer_schema(con)
    version = figer.version_referentiel()
    try:
        version, n = figer.figer(con, version=version, complet=complet)
    except figer.MoteurChange as e:
        # Rien n'a été figé, rien n'a été effacé. L'ingestion, elle, a bien eu
        # lieu : les bulletins sont en base, simplement pas encore figés — donc
        # pas citables (§8bis), ce qui est leur statut réel et non un mensonge.
        dire_brut(f"\n  ! FIGEAGE REFUSÉ — {e}")
        dire_brut("\n  les bulletins sont INGÉRÉS mais NON FIGÉS : rien n'est "
                  "publiable d'eux tant que")
        dire_brut("  le refigeage n'a pas eu lieu. `src/ingerer.py --etat` et le "
                  "rapport de département")
        dire_brut("  montrent l'écart.")
        return None, 0
    # Le nombre figé N'EST PAS le corpus : depuis que le figeage est
    # incrémental, « figé : 65 » veut dire « 65 nouveaux », pas « 65 en tout ».
    # Annoncer le premier sans le second, c'est publier un compte sans son
    # dénominateur — le §2.8 appliqué à notre propre trace d'exécution.
    corpus = con.execute("SELECT COUNT(*) FROM analyses_figees "
                         "WHERE version_referentiel = ?", [version]).fetchone()[0]
    dire_brut(f"\nfigé : {n} nouveau(x) bulletin(s) — {corpus} au total sous {version}")

    for dept in depts:
        vu = journal.lire_journal(dept)
        if not vu:
            dire_brut(f"  {dept} : aucun journal — aucune couverture inscrite")
            continue
        inscrites = 0
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
            inscrites += 1
        dire_brut(f"  {dept} : couverture de {inscrites} commune(s)")

    # `figer()` l'a déjà appelée, mais AVANT la boucle ci-dessus. On repasse
    # pour attraper les communes qui n'ont de bulletin que par le repli — celui-ci
    # est ingéré sous la commune où il a réellement eu lieu, qui n'est pas
    # forcément au journal. La fonction n'écrase jamais une ligne existante :
    # les statuts inscrits ci-dessus, plus précis, sont gardés.
    figer.figer_couverture_implicite(con, version)
    return version, n


def ingerer(depts, db=DB_PATH, tout=False, figeage=True, refiger=False):
    if not os.path.exists(db):
        dire_brut(f"base absente : {db}\nlance d'abord : py -X utf8 src/build_db.py")
        sys.exit(1)

    dire_brut(f"\n=== Ingestion de {len(depts)} département(s) : {', '.join(depts)} ===")
    dire_brut("aucun appel réseau — la matière première est le cache brut")

    t0 = time.time()
    con = ouvrir(db)
    pris = time.time()
    total = collections.Counter()
    try:
        connus = set() if tout else deja_en_base(con)
        if connus:
            dire_brut(f"déjà en base : {len(connus)} prélèvement(s), qui ne seront "
                      f"pas réingérés (--tout pour forcer)\n")
        for dept in depts:
            n, ignores = ingerer_departement(con, dept, connus, tout=tout)
            total["ingeres"] += n
            total["ignores"] += ignores
        if figeage:
            figer_departements(con, depts, complet=refiger)
    finally:
        con.close()

    tenu = time.time() - pris
    dire_brut(f"\ningéré : {total['ingeres']} bulletin(s)"
              + (f", {total['ignores']} ignoré(s)" if total["ignores"] else ""))
    dire_brut(f"verrou de la base tenu {tenu/60:.1f} min "
              f"(attente comprise : {(time.time()-t0)/60:.1f} min)")
    dire_brut("la base est rendue — elle est de nouveau disponible")
    return total["ingeres"]


def etat(depts=None, db=DB_PATH):
    """Ce qui attend au tampon, et ce qui est déjà en base. N'écrit rien."""
    depts = depts or journal.departements_du_cache()
    if not depts:
        dire_brut("aucun département au cache brut")
        return
    connus = set()
    if os.path.exists(db):
        try:
            con = ouvrir(db, lecture_seule=True, attendre=0)
        except Exception as e:
            dire_brut(f"base illisible pour l'instant ({type(e).__name__}) — "
                      f"les colonnes « en base » et « à verser » sont inconnues")
            dire_brut(f"  {e}\n")
            con = None
        if con is not None:
            try:
                connus = deja_en_base(con)
            finally:
                con.close()

    dire_brut(f"\n{'dept':<6}{'au cache':>10}{'en base':>10}{'à verser':>11}{'poids':>12}")
    attente = 0
    en_attente = []
    for dept in depts:
        entrees = brut.lister(dept)
        codes = {cp for _d, cp, _c in entrees}
        verse = len(codes & connus)
        reste = len(codes) - verse
        attente += reste
        if reste:
            en_attente.append(dept)
        c = brut.etat(dept)
        dire_brut(f"{dept:<6}{len(codes):>10}{verse:>10}{reste:>11}{c['mo']:>9} Mo")
    dire_brut(f"\n{attente} bulletin(s) attendent au tampon.")
    if en_attente:
        # Les départements déjà versés ne sont pas proposés : les relire
        # coûterait le verrou de la base pour ne rien changer.
        dire_brut(f"  py -X utf8 src/ingerer.py --depts {','.join(en_attente)}")


def main():
    p = argparse.ArgumentParser(
        description="Verse le cache brut dans la base, sans réseau, puis fige")
    p.add_argument("--depts", help="départements, séparés par des virgules (ex. 69,71)")
    p.add_argument("--tous", action="store_true",
                   help="tous les départements présents au cache brut")
    p.add_argument("--tout", action="store_true",
                   help="réingérer même les prélèvements déjà en base "
                        "(après correction d'un bug d'ingestion)")
    p.add_argument("--sans-figer", action="store_true",
                   help="ingérer sans figer — rien ne sera publiable tant que "
                        "le figeage n'a pas eu lieu")
    p.add_argument("--refiger", action="store_true",
                   help="refiger TOUT le corpus au lieu des seuls nouveaux "
                        "bulletins (long — voir figer.version_moteur)")
    p.add_argument("--etat", action="store_true",
                   help="ce qui attend au tampon, sans rien écrire")
    a = p.parse_args()

    depts = None
    if a.depts:
        depts = journal.lire_depts(a.depts)
    elif a.tous:
        depts = journal.departements_du_cache()

    if a.etat:
        etat(depts)
        return
    if not depts:
        p.error("--depts, --tous ou --etat est requis")

    ingerer(depts, tout=a.tout, figeage=not a.sans_figer, refiger=a.refiger)


if __name__ == "__main__":
    main()

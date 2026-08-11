# -*- coding: utf-8 -*-
"""
La moisson : rapatrier plusieurs départements en parallèle, **sans ouvrir la base**.

    py -X utf8 src/moisson.py --depts 69,71,01 --tous
    py -X utf8 src/moisson.py --depts 69,71,01 --tous --ouvriers 6
    py -X utf8 src/moisson.py --etat                    # où en est chaque département
    py -X utf8 src/moisson.py --depts 71 --limite 5     # essai mesuré, avant le lot

Puis, quand on veut bien rendre la base indisponible quelques minutes :

    py -X utf8 src/ingerer.py --depts 69,71,01

Le problème que ce fichier résout
---------------------------------
`fetch_departement.run()` tenait une connexion DuckDB en lecture-écriture
ouverte **de bout en bout d'une collecte départementale**, soit deux à trois
heures. Pendant ce temps, aucun autre processus ne pouvait ouvrir
`data/eau.duckdb`, **pas même en lecture seule** : ni `rediger_lot.py`, ni
`build_fiche.py`, ni les tests, ni une requête d'analyse. Le verrou DuckDB
était devenu la contrainte d'ordonnancement du projet (`docs/REPRISE.md`, en
tête), et il l'était sans nécessité : sur ces trois heures, l'écriture en base
occupe quelques minutes. Le reste est de l'attente réseau.

Or la séparation existait déjà, à moitié. `brut.py` garde depuis le 8 août
2026 la réponse de Hub'Eau telle quelle, et sa raison d'être était justement
de séparer **collecter** (une fois, en ligne) de **ingérer** (autant de fois
qu'on veut, hors ligne). Il manquait un chemin qui n'ingère pas du tout.

C'est ce fichier. Le cache brut devient le tampon, et il l'était déjà :

    réseau  ->  data/brut/<dept>/*.jsonl.gz   ->  data/eau.duckdb
              (moisson, des heures,            (ingestion, quelques
               parallèle, base libre)           minutes, base prise)

Trois conséquences, et la troisième est la plus importante
----------------------------------------------------------
1. **La base reste ouverte au travail** pendant toute la moisson. Rédiger,
   figer, bâtir des fiches, interroger : rien n'attend.
2. **Plusieurs départements avancent en même temps.** Mesuré sur les collectes
   réelles : 16,7 s par commune (Rhône partiel), 21,4 s (Eure-et-Loir),
   35,2 s (Tarn). L'essentiel est de l'attente de réponse, pas du calcul :
   c'est exactement le profil qui se parallélise.
3. **L'étiquette du §3.2 est tenue GLOBALEMENT, pas par fil.** Quatre fils qui
   respectent chacun `time.sleep(0.3)` quadruplent la charge vue par Hub'Eau,
   et rien ne le dirait. `hubeau.REGULATEUR` borne le débit du processus
   entier — appels en vol et appels par seconde — et met **tous** les fils en
   retenue dès qu'un seul reçoit un 429. Le parallélisme sans ce régulateur
   serait une charge abusive, pas une amélioration.

Ordre de traitement : les départements sont pris **dans l'ordre demandé**, et
les ouvriers passent au suivant dès qu'un département est épuisé. On ne mélange
pas : un département terminé tôt peut être ingéré et publié pendant que les
autres continuent, ce qu'un traitement en rond interdirait.

Reprise : le journal est celui de toujours (`data/journal/dept_NN.jsonl`). Une
moisson interrompue se relance par la même commande, et une commune en erreur
est retentée — jamais tenue pour faite (`journal.reste_a_faire`).

Ce fichier n'importe pas `duckdb`, et cela doit le rester.
"""
import argparse
import collections
import queue
import sys
import threading
import time

import brut
import collecte
import hubeau
import journal
from console import dire, dire_brut, etiqueter

# Réglage par défaut du régulateur. Quatre ouvriers, quatre appels en vol au
# plus, trois appels ouverts par seconde au plus.
#
# Ces valeurs sont les NÔTRES : Hub'Eau ne publie pas de quota, et le §2.7
# interdit d'écrire un seuil qu'on n'a pas lu — y compris quand il s'agit d'un
# seuil de politesse. Elles sont choisies pour rester du même ordre que ce que
# le projet demandait déjà, en tenant compte du fait qu'un appel coûte
# plusieurs secondes de réponse : à 16-35 s par commune, quatre fils ouvrent de
# l'ordre d'un appel par seconde, loin du plafond. Le plafond n'est là que pour
# le jour où les réponses deviennent rapides.
#
# Les augmenter est un choix qui engage le projet vis-à-vis d'un service public
# gratuit. Ne pas le faire sans mesurer, et ne jamais le faire pour rattraper
# un retard.
OUVRIERS = 4
PAR_SECONDE = 3.0

# Combien de temps on attend, après un Ctrl-C, que les communes en cours
# finissent proprement. Large parce qu'une pagination profonde dure : le
# réseau CENTRE de la Métropole de Lyon demande une demi-heure à lui seul.
ATTENTE_ARRET = 300


class Compte:
    """Avancement partagé, pour la ligne de progression."""

    def __init__(self, total):
        self.total = total
        self.faites = 0
        self.stats = collections.Counter()
        self.debut = time.time()
        self._verrou = threading.Lock()

    def noter(self, dept, statut):
        with self._verrou:
            self.faites += 1
            self.stats[statut] += 1
            self.stats[f"dept_{dept}"] += 1
            return self.faites

    def ligne(self):
        with self._verrou:
            ecoule = time.time() - self.debut
            faites = self.faites
        if not faites:
            return f"0/{self.total}"
        par_commune = ecoule / faites
        reste = (self.total - faites) * par_commune
        return (f"{faites}/{self.total} communes — "
                f"{par_commune:.1f} s/commune (parallèle), "
                f"reste ~{reste/3600:.1f} h")


def _taches(depts, limite=None, reprendre=True):
    """
    [(dept, commune), ...] dans l'ordre des départements demandés.

    L'énumération de chaque département coûte un appel et porte les centroïdes
    (cf. `journal.ecrire_communes_cache`). Elle est faite ici, avant les fils :
    on veut savoir combien de travail il y a AVANT de lancer quoi que ce soit,
    et une énumération qui échoue doit se voir tout de suite.
    """
    taches = []
    for dept in depts:
        communes = hubeau.communes_departement(dept)
        journal.ecrire_communes_cache(dept, communes)
        vu = journal.lire_journal(dept) if reprendre else {}
        a_faire = journal.reste_a_faire(communes, vu)
        a_retenter = sum(1 for c in a_faire if c["code_insee"] in vu)
        if limite:
            a_faire = a_faire[:limite]
        dire_brut(f"  {dept} : {len(communes)} communes, "
                  f"{len(vu)} déjà au journal, {len(a_faire)} à traiter"
                  + (f" dont {a_retenter} en erreur à retenter" if a_retenter else ""))
        for commune in a_faire:
            commune.setdefault("dept", dept)
            taches.append((dept, commune))
    return taches


def _ouvrier(travail, compte, arret, options):
    """
    Un fil : prend des communes, les moissonne, journalise. **Aucune base.**

    Le `con=None` passé à `collecte.traiter_commune` est tout le mécanisme :
    la règle de couverture, le repli sur le réseau et l'écriture au cache brut
    sont exactement ceux de la collecte d'avant, et c'est le même code qui les
    porte. Seule l'insertion en base est différée.
    """
    while not arret.is_set():
        try:
            dept, commune = travail.get_nowait()
        except queue.Empty:
            return
        insee = commune["code_insee"]
        # L'étiquette suit le fil jusqu'au fond de `hubeau._pages` : sans elle,
        # « page 12 — 60 000 lignes lues » ne dit pas de quel département il
        # s'agit, et une trace non attribuée redevient indistinguable d'un gel.
        etiqueter(f"[{dept}] ")
        try:
            dire(f"{insee} {commune.get('nom') or ''}".strip())
            try:
                statut, prels, commune_prel = collecte.traiter_commune(
                    None, commune,
                    depuis=options["depuis"], tous=options["tous"],
                    repli=options["repli"], cache=options["cache"])
            except Exception as e:
                dire(f"  ERREUR : {type(e).__name__}: {e}")
                journal.ecrire_journal(dept, {
                    "code_insee": insee, "nom": commune.get("nom"),
                    "etat": "erreur", "message": str(e)})
                compte.noter(dept, "erreur")
                # Les échecs arrivent en rafale, et sous plusieurs fils la
                # rafale est partagée : c'est le régulateur qui met tout le
                # monde en retenue sur 429. Ici on ne fait que ne pas
                # enchaîner immédiatement sur la commune suivante.
                time.sleep(5)
                continue

            journal.ecrire_journal(dept, {
                "code_insee": insee, "nom": commune.get("nom"),
                "codes_postaux": commune.get("codes_postaux"),
                "lon": commune.get("lon"), "lat": commune.get("lat"),
                "etat": "traitee", "statut": statut,
                "prelevements": prels, "commune_prelevement": commune_prel,
            })
            n = compte.noter(dept, statut)
            if n % 25 == 0:
                dire_brut(f"    ... {compte.ligne()}")
            time.sleep(hubeau.PAUSE_COMMUNE)
        finally:
            etiqueter(None)
            travail.task_done()


def moissonner(depts, ouvriers=OUVRIERS, par_seconde=PAR_SECONDE,
               limite=None, depuis=None, tous=False, repli=True, cache=True,
               reprendre=True):
    """Moissonne les départements demandés. Ne touche jamais `data/eau.duckdb`."""
    hubeau.REGULATEUR.regler(par_seconde=par_seconde, simultanes=ouvriers)
    etat = hubeau.REGULATEUR.etat()

    dire_brut(f"\n=== Moisson de {len(depts)} département(s) : {', '.join(depts)} ===")
    dire_brut(f"étiquette : {etat['simultanes']} appel(s) en vol au plus, "
              f"{etat['par_seconde']} appel(s) ouverts par seconde au plus, "
              f"retenue commune sur 429 (§3.2)")
    dire_brut(f"règle     : {'TOUS les bulletins complets' if tous else 'le dernier bulletin'}"
              f" de chaque point d'eau"
              + (f", depuis {depuis}" if depuis else ", sans borne de date"))
    dire_brut("la base   : jamais ouverte par ce processus — "
              "elle reste disponible pour tout le reste\n")

    taches = _taches(depts, limite=limite, reprendre=reprendre)
    if not taches:
        dire_brut("\nrien à moissonner — tous les départements demandés sont traités")
        return 0

    collecte.reinitialiser_stats()
    travail = queue.Queue()
    for t in taches:
        travail.put(t)
    compte = Compte(len(taches))
    arret = threading.Event()
    options = {"depuis": depuis, "tous": tous, "repli": repli, "cache": cache}

    dire_brut(f"\n{len(taches)} commune(s) à moissonner, {ouvriers} ouvrier(s)\n")
    fils = [threading.Thread(target=_ouvrier, args=(travail, compte, arret, options),
                             name=f"moisson-{i+1}", daemon=True)
            for i in range(ouvriers)]
    for f in fils:
        f.start()
    interrompu = False
    try:
        while any(f.is_alive() for f in fils):
            for f in fils:
                f.join(timeout=0.5)
    except KeyboardInterrupt:
        # Un Ctrl-C ne tue pas une commune en cours : elle finit, elle est
        # journalisée, et la reprise repartira APRÈS elle. L'interrompre en
        # plein vol la laisserait absente du journal alors que ses bulletins
        # seraient déjà au cache — reprise correcte quand même (le cache est
        # relu sans réseau), mais une commune redemandée pour rien.
        #
        # L'attente est BORNÉE et elle s'annonce : un fil peut être au milieu
        # d'une pagination profonde — le réseau CENTRE de Lyon, c'est une
        # demi-heure. Sans ce compte à rebours, un Ctrl-C sans effet visible
        # se lit comme un gel, et c'est le défaut qu'on passe son temps à
        # corriger dans ce dépôt.
        interrompu = True
        arret.set()
        dire_brut("\ninterruption demandée — les communes en cours finissent "
                  "(jusqu'à quelques minutes), puis les fils s'arrêtent.")
        dire_brut("  ce qui est déjà au cache brut est acquis, la reprise "
                  "repartira de là. Ctrl-C à nouveau pour couper net.")
        try:
            fin = time.time() + ATTENTE_ARRET
            for f in fils:
                f.join(timeout=max(1.0, fin - time.time()))
            encore = [f.name for f in fils if f.is_alive()]
            if encore:
                dire_brut(f"  {len(encore)} fil(s) encore en vol après "
                          f"{ATTENTE_ARRET//60} min — on rend la main sans les "
                          f"attendre ; ce sont des fils démons, ils meurent "
                          f"avec le processus")
        except KeyboardInterrupt:
            dire_brut("  coupure immédiate demandée — le cache brut et le "
                      "journal restent cohérents")

    duree = time.time() - compte.debut
    dire_brut(f"\nmoisson {'interrompue' if interrompu else 'terminée'} "
              f"en {duree/60:.1f} min")
    dire_brut("  " + ", ".join(f"{k}: {v}" for k, v in compte.stats.most_common()
                               if not k.startswith("dept_")))
    if compte.faites:
        dire_brut(f"  {duree/compte.faites:.1f} s par commune, "
                  f"{ouvriers} en parallèle")
    dire_brut(f"  bulletins rapatriés du réseau : "
              f"{collecte.STATS['bulletins_du_reseau']}")
    dire_brut(f"  bulletins relus au cache      : "
              f"{collecte.STATS['bulletins_du_cache']}"
              "   <-- autant d'appels épargnés à Hub'Eau")

    # Ce qu'on a réellement demandé au service public — le chiffre du §3.2,
    # que le projet ne mesurait pas. Et la réponse à « faut-il plus
    # d'ouvriers ? », qui ne se décide pas au jugé.
    b = hubeau.REGULATEUR.bilan()
    if b["appels"]:
        dire_brut(f"\ncharge demandée à Hub'Eau : {b['appels']} appels, "
                  f"{b['debit_reel']} par seconde en moyenne "
                  f"(plafond que le projet s'est fixé : {b['plafond']})")
        part = b["part_freinee"]
        dire_brut(f"  part du temps des fils passée à attendre NOTRE plafond : "
                  f"{part*100:.0f} %")
        if part >= 0.35:
            dire_brut("  -> c'est le plafond qui donne le rythme, pas Hub'Eau. "
                      "Ajouter des ouvriers")
            dire_brut("     n'accélérerait rien : ils attendraient. Le levier "
                      "est --par-seconde,")
            dire_brut("     et c'est une décision qui engage le projet (§3.2), "
                      "pas un réglage.")
        elif part <= 0.10:
            dire_brut("  -> c'est Hub'Eau qui donne le rythme. Des ouvriers "
                      "supplémentaires serviraient,")
            dire_brut("     sans demander plus d'appels par seconde qu'aujourd'hui.")

    dire_brut("\nrien n'est en base : le tampon est le cache brut. Pour l'y verser,")
    dire_brut(f"  py -X utf8 src/ingerer.py --depts {','.join(depts)}")
    return compte.faites


def etat(depts=None):
    """Où en est chaque département — sans réseau et sans base."""
    depts = depts or journal.departements_du_cache()
    if not depts:
        dire_brut("aucun département moissonné à ce jour")
        return
    dire_brut(f"\n{'dept':<6}{'communes':>10}{'traitées':>10}{'erreurs':>9}"
              f"{'restantes':>11}{'cache brut':>14}")
    for dept in depts:
        communes = journal.lire_communes_cache(dept)
        vu = journal.lire_journal(dept)
        c = brut.etat(dept)
        if not communes:
            dire_brut(f"{dept:<6}{'?':>10}{len(vu):>10}"
                      f"{'':>9}{'?':>11}"
                      f"{c['bulletins']:>8} / {c['mo']} Mo")
            continue
        erreurs = sum(1 for i in communes if (vu.get(i) or {}).get("etat") == "erreur")
        reste = len(journal.reste_a_faire(communes, vu))
        dire_brut(f"{dept:<6}{len(communes):>10}{len(communes)-reste:>10}"
                  f"{erreurs:>9}{reste:>11}"
                  f"{c['bulletins']:>8} / {c['mo']} Mo")
    dire_brut("\n« traitées » se lit dans le journal de moisson, PAS dans la base.")
    dire_brut("Ce qui est ingéré : py -X utf8 src/ingerer.py --etat")


def main():
    p = argparse.ArgumentParser(
        description="Moisson Hub'Eau parallèle — remplit le cache brut, "
                    "n'ouvre jamais la base")
    p.add_argument("--depts", help="départements, séparés par des virgules (ex. 69,71,01)")
    p.add_argument("--ouvriers", type=int, default=OUVRIERS,
                   help=f"communes traitées en parallèle (défaut {OUVRIERS})")
    p.add_argument("--par-seconde", type=float, default=PAR_SECONDE,
                   help=f"plafond d'appels ouverts par seconde, TOUS fils confondus "
                        f"(défaut {PAR_SECONDE})")
    p.add_argument("--limite", type=int,
                   help="ne traiter que les N premières communes de chaque département")
    p.add_argument("--depuis", help="année minimale de prélèvement (ex. 2020)")
    p.add_argument("--tous", action="store_true",
                   help="tous les bulletins complets de chaque point d'eau, "
                        "pas seulement le dernier")
    p.add_argument("--sans-repli", action="store_true",
                   help="ne pas rattacher au réseau si la commune n'a pas de bulletin")
    p.add_argument("--sans-cache", action="store_true",
                   help="ignorer le cache brut et tout redemander au réseau")
    p.add_argument("--reprendre-a-zero", action="store_true",
                   help="ignorer le journal et retraiter toutes les communes")
    p.add_argument("--etat", action="store_true",
                   help="avancement de chaque département, sans réseau ni base")
    p.add_argument("--termine", action="store_true",
                   help="code de sortie 0 si TOUS les départements demandés sont "
                        "moissonnés, 1 sinon (sert à la reprise automatique)")
    a = p.parse_args()

    if a.termine:
        if not a.depts:
            p.error("--termine demande --depts")
        reste_total, inconnus = 0, []
        for dept in journal.lire_depts(a.depts):
            communes = journal.lire_communes_cache(dept)
            if not communes:
                # Pas d'énumération : on ne sait pas ce qu'il reste. Répondre
                # « terminé » ici ferait retirer le lanceur automatique sur un
                # département jamais commencé.
                inconnus.append(dept)
                continue
            r = len(journal.reste_a_faire(communes, journal.lire_journal(dept)))
            reste_total += r
            dire_brut(f"{dept} : {len(communes)-r}/{len(communes)} communes moissonnées")
        for dept in inconnus:
            dire_brut(f"{dept} : pas de cache d'énumération, état inconnu")
        sys.exit(1 if (reste_total or inconnus) else 0)
    if a.etat:
        etat(journal.lire_depts(a.depts) if a.depts else None)
        return
    if not a.depts:
        p.error("--depts est requis (ou --etat)")
    if a.ouvriers < 1:
        p.error("--ouvriers doit valoir au moins 1")

    moissonner(journal.lire_depts(a.depts), ouvriers=a.ouvriers, par_seconde=a.par_seconde,
               limite=a.limite, depuis=a.depuis, tous=a.tous,
               repli=not a.sans_repli, cache=not a.sans_cache,
               reprendre=not a.reprendre_a_zero)


if __name__ == "__main__":
    main()

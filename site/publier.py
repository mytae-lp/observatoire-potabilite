#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publication de la vitrine publique vers l'hébergement (FTPS explicite).

Ce script ne fabrique rien. Il envoie `site/public/` tel quel, tel que
`build_site.py` vient de le produire. La vitrine reste un produit dérivé, non
versionné : la publication ne passe donc pas par git, et ne peut pas en
dépendre.

TROIS PROPRIÉTÉS TENUES, dans l'ordre d'importance :

1. ON NE SUPPRIME QUE CE QU'ON A SOI-MÊME ENVOYÉ. Le script tient un manifeste
   — `.manifeste-observatoire.json`, déposé à la racine distante — qui liste les
   fichiers qu'il a publiés et leur empreinte. Un fichier distant absent de ce
   manifeste n'est jamais touché, jamais listé pour suppression, jamais écrasé
   à l'aveugle. C'est ce qui rend l'outil utilisable sur un hébergement qui
   porte déjà autre chose.

2. IDEMPOTENCE SANS JOURNAL LOCAL. Ce qui est déjà en ligne se lit dans le
   manifeste distant, pas dans un fichier d'état sur la machine. Relancer une
   publication interrompue ne coûte que le reliquat ; publier depuis une autre
   machine fonctionne sans rien recopier. Même principe que la reprise de
   collecte : l'état vit dans le résultat, pas à côté.

3. ORDRE D'ENVOI SÛR. Les données, feuilles de style et scripts partent AVANT
   les pages HTML qui les appellent. Un visiteur tombant au milieu d'une
   publication voit au pire une page ancienne, jamais une page neuve dont les
   ressources manquent. Le manifeste part en dernier : tant qu'il n'est pas à
   jour, la publication est considérée comme inachevée.

IDENTIFIANTS — jamais dans le dépôt, jamais en argument de ligne de commande
(ils resteraient dans l'historique du shell).

Trois variables d'environnement, qui ne sont PAS des secrets et peuvent donc
être posées durablement :

    OBS_FTP_HOTE          nom d'hôte ou adresse IP du serveur FTP
    OBS_FTP_UTILISATEUR   l'utilisateur FTP créé dans hPanel
    OBS_FTP_RACINE        le dossier distant du sous-domaine,
                          à découvrir avec `--explorer`
    OBS_FTP_PORT          facultatif, 21 par défaut

Le mot de passe, lui, ne se range nulle part : le script le DEMANDE à chaque
publication, en saisie masquée. Il ne touche donc ni le disque, ni le registre,
ni l'historique du shell, et il n'existe que le temps du transfert. La variable
OBS_FTP_MOTDEPASSE reste lue si elle est présente — utile pour un lancement
automatisé — mais ce n'est pas le mode recommandé.

Conseil de portée : créer dans hPanel un compte FTP dédié, dont la racine est
le dossier du sous-domaine. Si l'identifiant fuite, il n'ouvre que la vitrine,
pas le reste de l'hébergement.

USAGE

    python site/publier.py --explorer     # découvrir l'arborescence distante
    python site/publier.py --simulation   # ce qui serait envoyé, sans rien écrire
    python site/publier.py                # publier
"""

import argparse
import concurrent.futures
import ftplib
import getpass
import hashlib
import json
import os
import ssl
import sys
import threading
import time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(RACINE, "site", "public")

MANIFESTE = ".manifeste-observatoire.json"

# Ce qui ne doit jamais partir en ligne, quoi qu'il arrive.
EXCLUS = {".DS_Store", "Thumbs.db", "__pycache__", ".git"}


# --------------------------------------------------------------------------
# Connexion
# --------------------------------------------------------------------------

class FTPS(ftplib.FTP_TLS):
    """FTPS explicite avec réutilisation de la session TLS.

    Plusieurs serveurs FTP courants (Pure-FTPd, ProFTPD, vsftpd configurés en
    `require_ssl_reuse`) refusent un canal de données dont la session TLS
    diffère de celle du canal de commande. `ftplib` ne fait pas cette
    réutilisation ; sans ce correctif, la connexion s'établit mais le premier
    transfert échoue.
    """

    def ntransfercmd(self, cmd, rest=None):
        conn, taille = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn, server_hostname=self.host, session=self.sock.session)
        return conn, taille


def config():
    """Rassemble les identifiants. Ne les affiche jamais, n'en écrit aucun."""
    manquantes = []
    valeurs = {}
    for cle in ("OBS_FTP_HOTE", "OBS_FTP_UTILISATEUR"):
        v = os.environ.get(cle, "").strip()
        if not v:
            manquantes.append(cle)
        valeurs[cle] = v
    if manquantes:
        sys.exit(
            "Réglages absents de l'environnement : " + ", ".join(manquantes)
            + "\nLes poser, puis relancer. Voir l'en-tête du script."
        )
    valeurs["OBS_FTP_RACINE"] = os.environ.get("OBS_FTP_RACINE", "").strip()
    port = os.environ.get("OBS_FTP_PORT", "").strip()
    valeurs["OBS_FTP_PORT"] = int(port) if port.isdigit() else 21

    # Le mot de passe est demandé plutôt que rangé. getpass n'écrit rien et
    # n'affiche rien ; il échoue franchement si l'entrée n'est pas un terminal,
    # ce qui est le comportement voulu — mieux vaut une erreur qu'un secret
    # tapé en clair dans un journal d'exécution.
    mdp = os.environ.get("OBS_FTP_MOTDEPASSE", "").strip()
    if not mdp:
        try:
            mdp = getpass.getpass(
                f"Mot de passe FTP de {valeurs['OBS_FTP_UTILISATEUR']} : ")
        except (EOFError, OSError):
            sys.exit("Pas de terminal pour la saisie du mot de passe. "
                     "Pour un lancement non interactif, poser "
                     "OBS_FTP_MOTDEPASSE dans l'environnement.")
    if not mdp:
        sys.exit("Mot de passe vide — rien n'a été tenté.")
    valeurs["OBS_FTP_MOTDEPASSE"] = mdp
    return valeurs


def connexion(cfg, verifier=True, silencieux=False):
    """Ouvre la session FTPS.

    `verifier=False` conserve le CHIFFREMENT mais renonce à vérifier l'identité
    du serveur. Ce n'est pas un détail : le trafic reste illisible pour un tiers
    passif, mais plus rien ne prouve qu'on parle bien à l'hébergeur. On ne le
    fait donc jamais par défaut — seulement sur demande explicite, et le script
    le dit à chaque fois.
    """
    if verifier:
        ctx = ssl.create_default_context()
    else:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if not silencieux:
            print("  ! identité du serveur NON vérifiée (--certificat-non-verifie)")

    ftp = FTPS(context=ctx, timeout=60)
    ftp.encoding = "utf-8"
    try:
        ftp.connect(cfg["OBS_FTP_HOTE"], cfg["OBS_FTP_PORT"])
        ftp.login(cfg["OBS_FTP_UTILISATEUR"], cfg["OBS_FTP_MOTDEPASSE"])
    except ssl.SSLCertVerificationError as e:
        sys.exit(
            f"\nLe certificat du serveur n'a pas pu être validé :\n  {e}\n\n"
            "C'est le cas attendu quand on se connecte à une ADRESSE IP : un\n"
            "certificat est émis pour un nom d'hôte, jamais pour une IP.\n\n"
            "Deux façons d'en sortir, dans cet ordre :\n"
            "  1. utiliser le NOM D'HÔTE du serveur plutôt que son IP —\n"
            "     à demander au support Hostinger, ou visible dans hPanel ;\n"
            "  2. à défaut, relancer avec --certificat-non-verifie : le\n"
            "     transfert reste chiffré, mais l'identité du serveur n'est\n"
            "     plus contrôlée. Acceptable ici — le site publié est public\n"
            "     et ne contient aucune donnée personnelle — mais c'est une\n"
            "     décision, pas un défaut.")
    ftp.prot_p()          # chiffre aussi le canal de données
    ftp.set_pasv(True)
    return ftp


# --------------------------------------------------------------------------
# Découverte de l'arborescence distante
# --------------------------------------------------------------------------

class Session:
    """La connexion FTPS, et de quoi la ROUVRIR.

    Écrit le 17 août 2026, après deux heures perdues. 45 617 fichiers ne
    tiennent pas sur une seule session : l'hébergeur a coupé au 32e
    département, et le script a continué à essayer d'écrire dans un tuyau
    fermé — trois tentatives et six secondes de temporisation par fichier,
    pendant deux heures, sans envoyer un octet ni afficher une ligne.

    Le record précédent était 4 974 fichiers : la connexion tenait, et le
    défaut ne pouvait pas se voir. Une page par prélèvement l'a révélé.
    """

    def __init__(self, cfg, verifier=True):
        self.cfg, self.verifier = cfg, verifier
        self.ftp = connexion(cfg, verifier)
        self.reouvertures = 0

    def rouvrir(self):
        """Referme ce qui peut l'être, et rouvre. Une connexion coupée ne se
        répare pas en réessayant d'écrire dedans."""
        try:
            self.ftp.close()
        except Exception:
            pass
        self.ftp = connexion(self.cfg, self.verifier, silencieux=True)
        self.reouvertures += 1
        return self.ftp


def explorer(ftp, depart="/", profondeur=3, _niveau=0):
    """Affiche l'arborescence distante, pour identifier le dossier du
    sous-domaine avec certitude plutôt que de le deviner."""
    marge = "  " * _niveau
    try:
        entrees = sorted(ftp.mlsd(depart), key=lambda e: e[0])
    except (ftplib.error_perm, ftplib.error_proto):
        try:
            entrees = [(os.path.basename(n), {"type": "?"})
                       for n in sorted(ftp.nlst(depart))]
        except ftplib.error_perm as e:
            print(f"{marge}  (illisible : {e})")
            return
    for nom, faits in entrees:
        if nom in (".", ".."):
            continue
        type_ = faits.get("type", "?")
        if type_ == "dir":
            print(f"{marge}{nom}/")
            if _niveau + 1 < profondeur:
                explorer(ftp, depart.rstrip("/") + "/" + nom,
                         profondeur, _niveau + 1)
        elif type_ == "file":
            taille = faits.get("size", "?")
            print(f"{marge}{nom}  ({taille} o)")
        else:
            print(f"{marge}{nom}")


# --------------------------------------------------------------------------
# Empreintes
# --------------------------------------------------------------------------

def empreinte(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(131072), b""):
            h.update(bloc)
    return h.hexdigest()


def empreintes_locales(racine, sauf=()):
    """{chemin relatif en / : empreinte} pour tout site/public.

    `sauf` accepte des motifs (fnmatch) évalués sur le chemin relatif : ce qui
    y correspond n'est ni envoyé, ni retiré, ni inscrit au manifeste — le
    fichier reste simplement hors du périmètre de l'outil.
    """
    import fnmatch
    out = {}
    for dossier, sous, fichiers in os.walk(racine):
        sous[:] = [d for d in sous if d not in EXCLUS]
        for f in fichiers:
            if f in EXCLUS:
                continue
            absolu = os.path.join(dossier, f)
            rel = os.path.relpath(absolu, racine).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, m) for m in sauf):
                continue
            out[rel] = empreinte(absolu)
    return out


def alerter_poids(racine, chemins, seuil_mo=25):
    """Signale les fichiers lourds avant l'envoi.

    Un transfert FTP d'un fichier de plusieurs centaines de Mo tient rarement
    le coup, et ce qui est lourd à envoyer est lourd à télécharger pour le
    visiteur. Le script n'interdit rien : il montre, la décision reste éditoriale.
    """
    lourds = []
    for r in chemins:
        o = os.path.getsize(os.path.join(racine, r.replace("/", os.sep)))
        if o >= seuil_mo * 1024 * 1024:
            lourds.append((o, r))
    if lourds:
        print(f"  ! fichiers de plus de {seuil_mo} Mo :")
        for o, r in sorted(lourds, reverse=True):
            print(f"      {o / 1048576:8.1f} Mo  {r}")
        print("    Les écarter au besoin :  --sauf 'donnees/verdicts.csv'\n")


def lire_manifeste(ftp, racine_distante):
    """Le manifeste précédent, ou {} à la première publication."""
    tampon = bytearray()
    try:
        ftp.retrbinary(f"RETR {racine_distante}/{MANIFESTE}", tampon.extend)
    except ftplib.error_perm:
        return {}
    try:
        return json.loads(tampon.decode("utf-8")).get("fichiers", {})
    except (ValueError, UnicodeDecodeError):
        print("  ! manifeste distant illisible — publication complète")
        return {}


def ecrire_manifeste(ftp, racine_distante, fichiers):
    import io
    contenu = json.dumps(
        {"outil": "site/publier.py", "fichiers": fichiers},
        ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8")
    ftp.storbinary(f"STOR {racine_distante}/{MANIFESTE}", io.BytesIO(contenu))


# --------------------------------------------------------------------------
# Transferts
# --------------------------------------------------------------------------

def assurer_dossier(ftp, chemin, connus):
    """Crée les dossiers distants manquants, de proche en proche."""
    if not chemin or chemin in connus:
        return
    parent = chemin.rsplit("/", 1)[0]
    if parent and parent != chemin:
        assurer_dossier(ftp, parent, connus)
    try:
        ftp.mkd(chemin)
    except ftplib.error_perm:
        pass          # existe déjà — le seul cas attendu
    connus.add(chemin)


def envoyer(session, local, distant, connus, essais=4):
    """Envoie un fichier, en rouvrant la session si elle a lâché.

    L'ordre compte : on temporise, PUIS on rouvre, PUIS on réessaie. Réessayer
    sur la même connexion morte est ce qui a coûté deux heures le 17 août.
    """
    for tentative in range(1, essais + 1):
        try:
            assurer_dossier(session.ftp, distant.rsplit("/", 1)[0], connus)
            with open(local, "rb") as f:
                session.ftp.storbinary(f"STOR {distant}", f, blocksize=131072)
            return True
        except (ftplib.error_temp, ftplib.error_proto, OSError, EOFError) as e:
            if tentative == essais:
                print(f"  ! échec définitif : {distant} ({e})", flush=True)
                return False
            time.sleep(2 * tentative)
            try:
                session.rouvrir()
                # Les dossiers déjà créés le restent côté serveur, mais le
                # cache local de ce qui a été vérifié appartenait à la session
                # perdue : on le laisse, il ne coûte qu'un MKD refusé.
                print(f"    reconnexion #{session.reouvertures} "
                      f"(après « {e} »)", flush=True)
            except Exception as e2:
                print(f"  ! reconnexion impossible : {e2}", flush=True)
    return False


# --------------------------------------------------------------------------
# Publication
# --------------------------------------------------------------------------

def adopter(ftp, racine_distante, sauf=()):
    """Déclare l'état distant conforme à l'état local, sans rien transférer.

    Sert après un premier envoi fait autrement — FileZilla, par exemple, qui
    est plus confortable pour les 363 Mo initiaux. Sans ce relais, le script
    ne trouverait aucun manifeste et renverrait tout.

    Le manifeste devient alors une AFFIRMATION, pas une observation : si le
    distant ne correspond pas réellement, les écarts seront tenus pour déjà
    publiés et sautés. En cas de doute, `--forcer` republie tout et remet les
    deux en accord.
    """
    locales = empreintes_locales(PUBLIC, sauf)
    if not locales:
        sys.exit(f"{PUBLIC} est vide — rien à adopter.")
    ecrire_manifeste(ftp, racine_distante, locales)
    print(f"\n  {len(locales)} fichiers déclarés déjà en ligne sous "
          f"{racine_distante}.")
    print("  Les prochaines publications n'enverront que ce qui change.")
    print("  Si le distant ne correspondait pas : relancer avec --forcer.")


def publier(session, racine_distante, simulation=False, forcer=False,
            sauf=(), jalon=500, fils=6):
    if not os.path.isdir(PUBLIC):
        sys.exit(f"{PUBLIC} n'existe pas. Construire la vitrine d'abord :\n"
                 f"    python site/build_site.py")

    locales = empreintes_locales(PUBLIC, sauf)
    if not locales:
        sys.exit(f"{PUBLIC} est vide — rien à publier.")

    # LA CONNEXION EST ROUVERTE ICI, ET C'EST UN CORRECTIF, PAS UNE PRÉCAUTION.
    #
    # `empreintes_locales` vient de hacher tout `site/public` — 54 000 fichiers
    # et 6,5 Go au 19 août 2026 — pendant que la session FTPS ouverte plus haut
    # restait inactive. L'hébergeur ferme une session oisive, et la lecture du
    # manifeste tombait alors sur un tuyau mort : `EOFError` levée dans
    # `voidcmd('TYPE I')`, avant même le premier octet transféré.
    #
    # Le défaut a mangé les trois publications de la Bretagne dans la nuit du
    # 18 au 19 août — neuf tentatives, toutes au même endroit — et il est
    # apparu avec la taille : plus le site grossit, plus le hachage dure, et
    # plus la session a le temps de mourir. D'où son air d'intermittence.
    #
    # Rouvrir coûte une seconde et vaut mieux qu'un keepalive : on ne sait pas
    # combien de temps le hachage durera au prochain département.
    session.rouvrir()

    publiees = {} if forcer else lire_manifeste(session.ftp, racine_distante)

    import fnmatch
    a_envoyer = [r for r, h in locales.items() if publiees.get(r) != h]
    # On ne propose à la suppression QUE ce que ce script a publié auparavant,
    # et jamais ce qui est explicitement écarté par --sauf : un fichier hors
    # périmètre reste hors périmètre, dans les deux sens. (Propriété 1)
    a_supprimer = [r for r in publiees
                   if r not in locales
                   and not any(fnmatch.fnmatch(r, m) for m in sauf)]

    # Les ressources d'abord, les pages ensuite. (Propriété 3)
    a_envoyer.sort(key=lambda r: (r.endswith(".html"), r))

    octets = sum(os.path.getsize(os.path.join(PUBLIC, r.replace("/", os.sep)))
                 for r in a_envoyer)
    inchanges = len(locales) - len(a_envoyer)
    print(f"\n  {len(locales)} fichiers retenus · {inchanges} inchangés · "
          f"{len(a_envoyer)} à envoyer ({octets / 1048576:.1f} Mo) · "
          f"{len(a_supprimer)} à retirer")
    print(f"  destination : {racine_distante}\n")
    alerter_poids(PUBLIC, a_envoyer)

    if simulation:
        for r in a_envoyer[:40]:
            print(f"    → {r}")
        if len(a_envoyer) > 40:
            print(f"    … et {len(a_envoyer) - 40} autres")
        for r in a_supprimer:
            print(f"    ✗ {r}")
        print("\n  Simulation : rien n'a été écrit.")
        return

    if not a_envoyer and not a_supprimer:
        print("  Le site en ligne est déjà à jour.")
        return

    connus = set()
    etat = dict(publiees)
    envoyes = 0
    verrou = threading.Lock()

    def un_fichier(r):
        """Le travail d'un ouvrier : un fichier, sur SA propre session."""
        nonlocal envoyes
        s = threading.current_thread().session
        if not envoyer(s, os.path.join(PUBLIC, r.replace("/", os.sep)),
                       f"{racine_distante}/{r}", connus):
            return
        with verrou:
            etat[r] = locales[r]
            envoyes += 1
            n = envoyes
        if n % 100 == 0 or n == len(a_envoyer):
            print(f"    {n}/{len(a_envoyer)} envoyés", flush=True)
        # LE MANIFESTE SE POSE EN COURS DE ROUTE, et pas seulement à la fin.
        # Il n'était écrit que dans le `finally` : une session tuée par un
        # signal, ou une connexion morte au moment de l'écrire, et les heures
        # d'envoi déjà faites étaient perdues — c'est ce qui s'est passé le
        # 17 août. Un jalon tous les 500 fichiers borne la perte à 500.
        if jalon and n % jalon == 0:
            with verrou:
                instantane = dict(etat)
            try:
                ecrire_manifeste(s.ftp, racine_distante, instantane)
                print(f"    · jalon posé à {n}", flush=True)
            except Exception as e:
                print(f"    ! jalon non posé ({e})", flush=True)

    def ouvrier_pret():
        """Chaque fil ouvre SA session : un objet ftplib n'est pas partageable
        entre fils, et c'est justement le point — N connexions, N latences qui
        se recouvrent.

        L'hébergement borne le nombre de sessions simultanées, et il ne le
        publie pas. On réessaie donc plutôt que d'abandonner : un fil qui
        n'obtient pas sa connexion tuerait tout le lot qui lui est confié.
        """
        for essai in range(1, 5):
            try:
                threading.current_thread().session = Session(session.cfg,
                                                             session.verifier)
                return
            except Exception as e:
                if essai == 4:
                    raise
                print(f"    connexion d'ouvrier refusée ({e}), "
                      f"nouvelle tentative", flush=True)
                time.sleep(3 * essai)

    try:
        # DEUX PHASES, et la barrière entre elles n'est pas une commodité :
        # « les ressources d'abord, les pages ensuite » (Propriété 3). Une page
        # mise en ligne avant la feuille qu'elle appelle s'affiche nue le temps
        # que l'autre arrive. En parallèle, l'ordre d'une liste ne garantit
        # plus rien — seule une barrière le garantit.
        for phase, lot in (("ressources", [r for r in a_envoyer
                                           if not r.endswith(".html")]),
                           ("pages", [r for r in a_envoyer
                                      if r.endswith(".html")])):
            if not lot:
                continue
            n_fils = min(fils, len(lot))
            print(f"\n  {phase} : {len(lot)} fichier(s) sur {n_fils} "
                  f"connexion(s)", flush=True)
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=n_fils, initializer=ouvrier_pret) as pool:
                list(pool.map(un_fichier, lot))

        for r in a_supprimer:
            try:
                session.ftp.delete(f"{racine_distante}/{r}")
                etat.pop(r, None)
                print(f"    ✗ retiré : {r}", flush=True)
            except ftplib.error_perm as e:
                print(f"  ! suppression refusée : {r} ({e})", flush=True)
    finally:
        # Même après interruption, le manifeste reflète ce qui est réellement
        # en ligne : la reprise ne réenvoie que le reliquat. (Propriété 2)
        #
        # Et il se sauve même si la connexion est morte — c'est précisément le
        # moment où on en a le plus besoin. Le 17 août, elle l'était, et deux
        # heures d'envoi sont parties avec elle.
        try:
            ecrire_manifeste(session.ftp, racine_distante, etat)
        except Exception:
            try:
                ecrire_manifeste(session.rouvrir(), racine_distante, etat)
            except Exception as e:
                print(f"  ! manifeste NON écrit ({e}) — la reprise "
                      f"réenverra tout", flush=True)

    print(f"\n  Publié : {envoyes} fichier(s), {len(a_supprimer)} retiré(s).")


def main():
    p = argparse.ArgumentParser(
        description="Publie site/public/ vers l'hébergement, en FTPS.")
    p.add_argument("--explorer", action="store_true",
                   help="affiche l'arborescence distante et quitte")
    p.add_argument("--simulation", action="store_true",
                   help="montre ce qui serait envoyé, sans rien écrire")
    p.add_argument("--forcer", action="store_true",
                   help="ignore le manifeste et republie tout")
    p.add_argument("--racine", help="dossier distant (défaut : OBS_FTP_RACINE)")
    p.add_argument("--sauf", action="append", default=[], metavar="MOTIF",
                   help="écarte les chemins correspondants, répétable "
                        "(ex. --sauf 'donnees/verdicts.csv')")
    p.add_argument("--certificat-non-verifie", action="store_true",
                   dest="sans_verif",
                   help="conserve le chiffrement mais ne vérifie pas "
                        "l'identité du serveur (cas d'une connexion par IP)")
    p.add_argument("--fils", type=int, default=6, metavar="N",
                   help="nombre de connexions FTPS simultanées (défaut 6). "
                        "Ce qui coûte n'est pas le débit mais le temps par "
                        "fichier : mesuré le 17 août, une connexion tenait "
                        "593 Ko/s là où trois en cumulaient 9 585.")
    p.add_argument("--adopter", action="store_true",
                   help="déclare le distant conforme au local sans rien "
                        "envoyer, après un premier transfert fait autrement")
    args = p.parse_args()

    cfg = config()
    print(f"  connexion à {cfg['OBS_FTP_HOTE']}:{cfg['OBS_FTP_PORT']} …")
    session = Session(cfg, verifier=not args.sans_verif)
    ftp = session.ftp
    try:
        if args.explorer:
            print(f"  connecté. Dossier courant : {ftp.pwd()}\n")
            explorer(ftp)
            print("\n  Repérer le dossier du sous-domaine (celui qui contient "
                  "ou contiendra index.html),\n  puis le poser dans "
                  "OBS_FTP_RACINE.")
            return

        racine_distante = (args.racine or cfg["OBS_FTP_RACINE"]).rstrip("/")
        if not racine_distante:
            sys.exit("Dossier distant inconnu. Le découvrir avec --explorer, "
                     "puis poser OBS_FTP_RACINE.")
        if args.adopter:
            adopter(ftp, racine_distante, args.sauf)
        else:
            publier(session, racine_distante, args.simulation,
                    args.forcer, args.sauf, fils=args.fils)
    finally:
        try:
            session.ftp.quit()
        except Exception:
            try:
                session.ftp.close()
            except Exception:
                pass
        if session.reouvertures:
            print(f"  ({session.reouvertures} reconnexion(s) pendant l'envoi)")


if __name__ == "__main__":
    main()

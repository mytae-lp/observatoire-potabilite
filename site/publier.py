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
import ftplib
import getpass
import hashlib
import json
import os
import ssl
import sys
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


def connexion(cfg, verifier=True):
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


def envoyer(ftp, local, distant, connus, essais=3):
    assurer_dossier(ftp, distant.rsplit("/", 1)[0], connus)
    for tentative in range(1, essais + 1):
        try:
            with open(local, "rb") as f:
                ftp.storbinary(f"STOR {distant}", f, blocksize=131072)
            return True
        except (ftplib.error_temp, OSError, EOFError) as e:
            if tentative == essais:
                print(f"  ! échec définitif : {distant} ({e})")
                return False
            time.sleep(2 * tentative)
    return False


# --------------------------------------------------------------------------
# Publication
# --------------------------------------------------------------------------

def publier(ftp, racine_distante, simulation=False, forcer=False, sauf=()):
    if not os.path.isdir(PUBLIC):
        sys.exit(f"{PUBLIC} n'existe pas. Construire la vitrine d'abord :\n"
                 f"    python site/build_site.py")

    locales = empreintes_locales(PUBLIC, sauf)
    if not locales:
        sys.exit(f"{PUBLIC} est vide — rien à publier.")

    publiees = {} if forcer else lire_manifeste(ftp, racine_distante)

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
    try:
        for r in a_envoyer:
            if envoyer(ftp, os.path.join(PUBLIC, r.replace("/", os.sep)),
                       f"{racine_distante}/{r}", connus):
                etat[r] = locales[r]
                envoyes += 1
                if envoyes % 25 == 0 or envoyes == len(a_envoyer):
                    print(f"    {envoyes}/{len(a_envoyer)} envoyés")

        for r in a_supprimer:
            try:
                ftp.delete(f"{racine_distante}/{r}")
                etat.pop(r, None)
                print(f"    ✗ retiré : {r}")
            except ftplib.error_perm as e:
                print(f"  ! suppression refusée : {r} ({e})")
    finally:
        # Même après interruption, le manifeste reflète ce qui est réellement
        # en ligne : la reprise ne réenvoie que le reliquat. (Propriété 2)
        ecrire_manifeste(ftp, racine_distante, etat)

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
    args = p.parse_args()

    cfg = config()
    print(f"  connexion à {cfg['OBS_FTP_HOTE']}:{cfg['OBS_FTP_PORT']} …")
    ftp = connexion(cfg, verifier=not args.sans_verif)
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
        publier(ftp, racine_distante, args.simulation, args.forcer, args.sauf)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Le moissonneur des recueils des actes administratifs — chantier C10.

    py -X utf8 -u src/raa_moisson.py --dept 81 --depuis 2016 --inventaire
    py -X utf8 -u src/raa_moisson.py --dept 81 --moissonner
    py -X utf8    src/raa_moisson.py --dept 81 --etat
    py -X utf8    src/raa_moisson.py --dept 81 --termine

CE MODULE N'IMPORTE JAMAIS `duckdb`, ni directement ni par `common`
-------------------------------------------------------------------
C'est la garantie mécanique héritée de `src/moisson.py` : la base reste libre
pendant que le réseau travaille. Ici elle vaut encore plus cher, puisqu'un
inventaire départemental dure plus d'une heure et qu'une ingestion Hub'Eau peut
tourner en même temps. `RACINE` est donc recalculé sur place, comme le font
déjà `purger_versions.py` et `etude_panel.py`, plutôt qu'emprunté à `common`.

DEUX GESTES, ET LE PREMIER NE TÉLÉCHARGE RIEN
---------------------------------------------
    inventaire   parcourt années > mois > recueils, relève l'adresse, le
                 libellé, LA TAILLE et la date de chaque PDF. Aucun fichier
                 n'est téléchargé.
    moisson      télécharge, extrait le texte, garde le texte compressé et
                 **jette le PDF** (sauf --garder-pdf).

Le découpage n'est pas décoratif. Mesuré le 11 août 2026 sur le Tarn : le seul
recueil de janvier 2016 est publié en cinq parties, dont une de 23,5 Mo. Un
département sur onze ans peut donc peser des dizaines de gigaoctets, et
personne ne doit lancer ce téléchargement sans avoir vu le chiffre d'abord.
L'inventaire le rend en ne demandant que des pages HTML — **les tailles sont
écrites dans les libellés de lien**, il n'y a rien à deviner.

CE QUE LE CACHE GARDE, ET POURQUOI CE N'EST PAS LE PDF
-------------------------------------------------------
Le texte extrait pèse de l'ordre de 3 % du PDF. C'est lui la matière du
chantier : le pré-filtre, le découpage par le sommaire et la qualification ne
lisent que du texte. Garder les PDF entiers coûterait cinquante fois plus pour
une traçabilité que l'URL d'origine assure déjà — chaque entrée du journal
porte l'adresse exacte du fichier dont le texte vient. Les PDF des recueils
qui portent un candidat, eux, méritent d'être gardés : c'est ce que fera
`raa_lot.py` en les redemandant à l'unité.

ÉTIQUETTE (§3.2 transposé aux sites de préfecture)
---------------------------------------------------
Un site de préfecture n'est pas Hub'Eau, mais la règle vaut : un `User-Agent`
qui identifie le projet et laisse une adresse, une pause entre deux appels, une
reprise sur incident qui ne redemande jamais ce qui est déjà obtenu, et aucun
parallélisme. Ce sont des serveurs de service public : on passe une fois.
"""
import argparse
import gzip
import json
import os
import re
import sys
import time

import requests
from lxml import html as lx

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_CSV = os.path.join(RACINE, "referentiel", "sources_raa.csv")
RAA_DIR = os.path.join(RACINE, "data", "brut", "raa")
JOURNAL_DIR = os.path.join(RACINE, "data", "journal")

UA = ("Observatoire-potabilite/0.1 (projet citoyen de donnees ouvertes sur la "
      "qualite de l'eau ; contact y.mytae@agriatlas.org)")
PAUSE = 1.2          # secondes entre deux appels — décision du projet
PAUSE_PDF = 2.0      # un PDF pèse dix à mille fois une page HTML
TENTATIVES = 3


# ---------------------------------------------------------------------------
# La carte des sites — lue, jamais déduite
# ---------------------------------------------------------------------------
def lire_sources():
    """{departement: {base_url, chemin_raa, gabarit, ...}} depuis le CSV versionné."""
    sources = {}
    with open(SOURCES_CSV, encoding="utf-8") as fh:
        lignes = [l for l in fh if not l.startswith("#") and l.strip()]
    entete = lignes[0].rstrip("\n").split(";")
    for ligne in lignes[1:]:
        cols = ligne.rstrip("\n").split(";")
        if len(cols) != len(entete):
            raise SystemExit(f"sources_raa.csv : ligne mal formée -> {ligne[:60]}")
        e = dict(zip(entete, cols))
        sources[e["departement"]] = e
    return sources


# ---------------------------------------------------------------------------
# Réseau — une seule session, une pause, trois tentatives
# ---------------------------------------------------------------------------
_S = None


def _session():
    """
    La session courante, recréée à la demande.

    Elle se jette et se refait sur `ConnectionError`. Motif, rencontré le
    11 août 2026 dès le sixième mois de l'inventaire du Tarn : le serveur ferme
    une connexion maintenue ouverte, et `requests` réutilise la socket morte —
    les trois tentatives échouaient alors toutes les trois sur la MÊME
    connexion, ce qui donnait l'apparence d'un site indisponible alors qu'il
    répondait. Une nouvelle session ouvre une nouvelle socket.
    """
    global _S
    if _S is None:
        _S = requests.Session()
        _S.headers.update({"User-Agent": UA})
    return _S


def _oublier_session():
    global _S
    if _S is not None:
        try:
            _S.close()
        except Exception:                     # noqa: BLE001
            pass
    _S = None


def _demander(url, pause=PAUSE, flux=False):
    dernier = None
    for essai in range(1, TENTATIVES + 1):
        time.sleep(pause)
        try:
            r = _session().get(url, timeout=60, stream=flux)
            if r.status_code == 429 or r.status_code >= 500:
                dernier = f"HTTP {r.status_code}"
                time.sleep(pause * 4 * essai)   # on se retire, on n'insiste pas
                continue
            r.raise_for_status()
            return r
        except requests.ConnectionError as e:
            dernier = f"{type(e).__name__}: {e}"
            _oublier_session()                  # la socket est morte, pas le site
            time.sleep(pause * 3 * essai)
        except requests.RequestException as e:
            dernier = f"{type(e).__name__}: {e}"
            time.sleep(pause * 2 * essai)
    raise RuntimeError(f"{dernier} — {url}")


def _page(url):
    return lx.fromstring(_demander(url).text)


def _page_sure(dept, url, quoi):
    """
    La page, ou None — l'échec est journalisé et n'interrompt jamais le parcours.

    **Un échec réseau est transitoire ; il se retente.** C'est la règle que
    `src/journal.py` porte déjà pour les communes, et elle valait ici aussi :
    au premier essai, une seule page de mois injoignable a fait tomber tout
    l'inventaire après six mois de travail. Ce qui n'a pas été vu n'est pas
    marqué comme vu, donc la relance le reprendra.
    """
    try:
        return _page(url)
    except RuntimeError as e:
        ecrire_journal(dept, {"url": url, "etat": "erreur",
                              "geste": f"inventaire/{quoi}", "motif": str(e)})
        print(f"    ! {quoi} injoignable — {e}")
        return None


def _liens(doc, motif, base):
    """Les href distincts qui collent au motif, avec leur libellé, dans l'ordre."""
    vus, out = set(), []
    for a in doc.xpath("//a[@href]"):
        h = (a.get("href") or "").strip()
        if not re.search(motif, h) or h in vus:
            continue
        vus.add(h)
        out.append((h if h.startswith("http") else base + h,
                    " ".join((a.text_content() or "").split())))
    return out


# ---------------------------------------------------------------------------
# Journal et inventaire
# ---------------------------------------------------------------------------
def chemin_journal(dept):
    os.makedirs(JOURNAL_DIR, exist_ok=True)
    return os.path.join(JOURNAL_DIR, f"raa_{dept}.jsonl")


def ecrire_journal(dept, entree):
    with open(chemin_journal(dept), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entree, ensure_ascii=False) + "\n")


def lire_journal(dept):
    """{url: dernière entrée}. Une entrée en erreur ne compte pas comme faite."""
    chemin, vu = chemin_journal(dept), {}
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
                continue          # une ligne tronquée n'efface pas les autres
            if e.get("url"):
                vu[e["url"]] = e
    return vu


def chemin_inventaire(dept):
    os.makedirs(os.path.join(RAA_DIR, dept), exist_ok=True)
    return os.path.join(RAA_DIR, dept, "_inventaire.json")


def lire_inventaire(dept):
    chemin = chemin_inventaire(dept)
    if not os.path.exists(chemin):
        return {"departement": dept, "pages_vues": [], "fichiers": []}
    with open(chemin, encoding="utf-8-sig") as fh:
        return json.load(fh)


def ecrire_inventaire(dept, inv):
    with open(chemin_inventaire(dept), "w", encoding="utf-8") as fh:
        json.dump(inv, fh, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# La fenêtre — au mois, pas à l'année
#
# Décision de Yannick, 11 août 2026 : on travaille d'abord sur les six derniers
# mois, pas sur dix ans. Motif tenu en clair — un département sur onze ans pèse
# vraisemblablement des dizaines de gigaoctets, et l'objectif immédiat est de
# publier, pas d'accumuler.
#
# **La date annoncée par le site ne sert PAS à borner la fenêtre.** Le recueil
# de janvier 2016 porte « 09/06/2016 » : c'est la date de mise en ligne lors
# d'une reprise en masse, pas celle du recueil. S'y fier daterait faux. La
# période se lit sur le CHEMIN — `/RAA/2026/Fevrier-2026/…` — qui est ce que la
# préfecture affirme elle-même du recueil.
# ---------------------------------------------------------------------------
_MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
         "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10,
         "novembre": 11, "decembre": 12}


def lire_depuis(texte):
    """« 2016 » -> (2016, 1) ; « 2026-02 » -> (2026, 2)."""
    m = re.match(r"^(\d{4})(?:[-/](\d{1,2}))?$", str(texte).strip())
    if not m:
        raise SystemExit(f"--depuis attend AAAA ou AAAA-MM, reçu « {texte} »")
    return int(m.group(1)), int(m.group(2) or 1)


def _sans_accent(s):
    for a, b in (("éèê", "e"), ("û", "u"), ("à", "a"), ("î", "i"), ("ô", "o")):
        for c in a:
            s = s.replace(c, b)
    return s


def periode_du_chemin(url_mois):
    """« …/RAA/2026/Fevrier-2026 » -> « 2026-02 », ou None si illisible."""
    seg = _sans_accent(url_mois.rstrip("/").rsplit("/", 1)[-1].lower())
    an = re.search(r"(\d{4})", seg)
    for nom, num in _MOIS.items():
        if seg.startswith(nom) and an:
            return f"{an.group(1)}-{num:02d}"
    return None


# « Télécharger RAA 2016-001 JANVIER 2016 Partie 1 PDF - 23,50 Mb - 09/06/2016 »
_TAILLE = re.compile(r"([\d]+[.,]?\d*)\s*(Kb|Mb|Gb|Ko|Mo|Go)", re.I)
_DATE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
_FACTEUR = {"k": 1024, "m": 1024 ** 2, "g": 1024 ** 3}


def _octets(libelle):
    """La taille annoncée dans le libellé du lien, en octets, ou None."""
    m = _TAILLE.search(libelle or "")
    if not m:
        return None
    return int(float(m.group(1).replace(",", ".")) * _FACTEUR[m.group(2)[0].lower()])


def _date_publication(libelle):
    m = _DATE.search(libelle or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


# ---------------------------------------------------------------------------
# L'inventaire — aucun PDF téléchargé
# ---------------------------------------------------------------------------
def inventorier(dept, depuis, sources):
    an_min, mois_min = lire_depuis(depuis)
    src = sources[dept]
    base, racine_raa = src["base_url"], src["base_url"] + src["chemin_raa"]
    inv = lire_inventaire(dept)
    deja = set(inv["pages_vues"])
    connus = {f["url"] for f in inv["fichiers"]}

    print(f"inventaire du département {dept} — depuis {depuis}")
    print(f"  racine : {racine_raa}")

    doc_racine = _page_sure(dept, racine_raa, "racine")
    if doc_racine is None:
        raise SystemExit("la racine du RAA est injoignable — rien n'a été inventorié")
    annees = [(u, t) for u, t in _liens(doc_racine, r"/RAA/\d{4}$", base)
              if int(re.search(r"(\d{4})$", u).group(1)) >= an_min]
    annees.sort(key=lambda x: x[0])
    print(f"  {len(annees)} année(s) à parcourir : "
          f"{annees[0][1] if annees else '—'} … {annees[-1][1] if annees else '—'}")

    incomplets = []
    borne = f"{an_min}-{mois_min:02d}"
    for url_an, lib_an in annees:
        an = re.search(r"(\d{4})$", url_an).group(1)
        doc_an = _page_sure(dept, url_an, f"année {an}")
        if doc_an is None:
            incomplets.append(an)
            continue
        mois = _liens(doc_an, rf"/RAA/{an}/[^/]+$", base)
        retenus = []
        for u, t in mois:
            p = periode_du_chemin(u)
            if p is None:
                # Un mois dont le chemin ne se lit pas ne se jette pas en
                # silence — on le garde et on le dit. Écarter par défaut ferait
                # un trou que rien ne signalerait (§2.4).
                print(f"    ? période illisible : {u} — retenu par précaution")
                retenus.append((u, t, None))
            elif p >= borne:
                retenus.append((u, t, p))
        print(f"  {an} : {len(retenus)} mois retenu(s) sur {len(mois)} "
              f"(fenêtre à partir de {borne})")
        for url_mois, lib_mois, periode in retenus:
            if url_mois in deja:
                continue
            doc_mois = _page_sure(dept, url_mois, f"mois {lib_mois}")
            if doc_mois is None:
                incomplets.append(lib_mois)
                continue
            recueils = _liens(doc_mois, rf"/RAA/{an}/[^/]+/[^/]+$", base)
            # Le site replie une partie de la liste derrière un « voir plus »
            # qui ne recharge rien : les éléments cachés sont dans le HTML.
            # Si une vraie pagination apparaissait, la manquer perdrait des
            # recueils EN SILENCE — c'est le pire cas du §2.4. On la signale.
            pagin = [u for u, _ in _liens(doc_mois, r"[?&]page=", base)
                     if url_mois.split("://", 1)[-1] in u]
            if pagin:
                ecrire_journal(dept, {"url": url_mois, "etat": "avertissement",
                                      "geste": "inventaire",
                                      "motif": f"pagination detectee : {pagin[:3]}"})
                print(f"    ! {lib_mois} — PAGINATION détectée, à traiter")
            nouveaux, complet = 0, True
            for url_rec, lib_rec in recueils:
                if url_rec in deja:
                    continue
                doc_rec = _page_sure(dept, url_rec, f"recueil {lib_rec[:40]}")
                if doc_rec is None:
                    complet = False
                    continue
                pdfs = _liens(doc_rec, r"\.pdf(\?|$)", base)
                for url_pdf, lib_pdf in pdfs:
                    if url_pdf in connus:
                        continue
                    connus.add(url_pdf)
                    nouveaux += 1
                    inv["fichiers"].append({
                        "url": url_pdf,
                        "annee": an,
                        "periode": periode,
                        "mois": lib_mois,
                        "recueil": lib_rec,
                        "page_recueil": url_rec,
                        "libelle": lib_pdf,
                        "octets_annonces": _octets(lib_pdf),
                        "publie_le": _date_publication(lib_pdf),
                        "special": "SPECIAL" in lib_rec.upper(),
                    })
                deja.add(url_rec)
                inv["pages_vues"].append(url_rec)
            # **Un mois n'est marqué vu que si TOUS ses recueils l'ont été.**
            # Sinon la relance sauterait le mois et le recueil manquant ne
            # serait jamais repris — c'est exactement les quatre communes
            # perdues par le journal du 28 (`docs/REPRISE.md` §10.1), sauf
            # qu'ici la perte serait silencieuse : le compte final aurait l'air
            # entier. Le prix d'une relance est de redemander les pages du mois
            # déjà vues ; le prix de l'inverse est un trou invisible.
            if complet:
                deja.add(url_mois)
                inv["pages_vues"].append(url_mois)
            else:
                incomplets.append(lib_mois)
            ecrire_inventaire(dept, inv)      # refermé à chaque mois : reprenable
            print(f"    {lib_mois:<20} {len(recueils):>3} recueil(s), "
                  f"{nouveaux:>3} fichier(s)"
                  f"{'   INCOMPLET, à relancer' if not complet else ''}")

    resumer_inventaire([f for f in inv["fichiers"] if dans_fenetre(f, borne)])
    if incomplets:
        print(f"\n  ATTENTION — {len(incomplets)} période(s) incomplète(s) : "
              f"{', '.join(str(x) for x in incomplets[:8])}"
              f"{' …' if len(incomplets) > 8 else ''}")
        print("  relancer la même commande : ce qui est vu n'est pas redemandé.")
    return inv


def periode_du_fichier(fic):
    """
    La période d'un fichier, **relue du chemin** plutôt que d'un champ stocké.

    Le champ `periode` n'existait pas dans les premières entrées écrites le
    11 août 2026, et sans ce repli elles répondaient toutes « je ne sais pas »,
    donc « garde-moi » : les 88 fichiers de 2016 passaient une fenêtre ouverte
    sur 2026. Un champ absent d'un enregistrement ancien n'est pas une donnée
    inconnue quand l'information est ailleurs dans l'enregistrement.
    """
    return fic.get("periode") or periode_du_chemin(
        (fic.get("page_recueil") or "").rsplit("/", 1)[0])


def dans_fenetre(fic, borne):
    """
    Le fichier tombe-t-il dans la fenêtre ?

    Une période **réellement** illisible répond oui. Écarter ce qu'on ne sait
    pas dater reviendrait à décider d'une absence sans preuve — trois états,
    pas deux. Mais on épuise d'abord ce que l'enregistrement sait dire.
    """
    p = periode_du_fichier(fic)
    return p is None or p >= borne


def resumer_inventaire(fics):
    connus = [f["octets_annonces"] for f in fics if f["octets_annonces"]]
    total = sum(connus)
    print()
    print(f"  {len(fics)} fichier(s) PDF recensé(s), "
          f"{len({f['page_recueil'] for f in fics})} recueil(s)")
    print(f"  taille annoncée : {total / 1024**3:.2f} Go "
          f"({len(connus)} fichier(s) sur {len(fics)} annoncent la leur)")
    par_an = {}
    for f in fics:
        a = par_an.setdefault(f["annee"], [0, 0])
        a[0] += 1
        a[1] += f["octets_annonces"] or 0
    for an in sorted(par_an):
        n, o = par_an[an]
        print(f"    {an} : {n:>5} fichier(s)  {o / 1024**3:>6.2f} Go")


# ---------------------------------------------------------------------------
# La moisson — télécharger, extraire, garder le texte, jeter le PDF
# ---------------------------------------------------------------------------
def _chemin_texte(dept, fic):
    nom = fic["url"].rsplit("/", 1)[-1].rsplit(".", 1)[0]
    nom = re.sub(r"[^A-Za-z0-9_.-]", "_", nom)
    dossier = os.path.join(RAA_DIR, dept, fic["annee"])
    os.makedirs(dossier, exist_ok=True)
    return os.path.join(dossier, nom + ".txt.gz")


def moissonner(dept, depuis, garder_pdf=False, plafond=None):
    from pypdf import PdfReader          # importé ici : l'inventaire n'en a pas besoin

    an_min, mois_min = lire_depuis(depuis)
    borne = f"{an_min}-{mois_min:02d}"
    inv = lire_inventaire(dept)
    vu = lire_journal(dept)
    fenetre = [f for f in inv["fichiers"] if dans_fenetre(f, borne)]
    a_faire = [f for f in fenetre
               if (vu.get(f["url"]) or {}).get("etat") not in ("moissonne",)
               and not os.path.exists(_chemin_texte(dept, f))]
    if plafond:
        a_faire = a_faire[:plafond]
    print(f"moisson du département {dept} — fenêtre à partir de {borne}")
    print(f"  {len(a_faire)} fichier(s) à prendre sur {len(fenetre)} dans la "
          f"fenêtre ({len(inv['fichiers'])} inventoriés en tout)")

    tmp = os.path.join(RAA_DIR, dept, "_en_cours.pdf")
    for i, fic in enumerate(a_faire, 1):
        t0 = time.time()
        try:
            r = _demander(fic["url"], pause=PAUSE_PDF, flux=True)
            with open(tmp, "wb") as fh:
                for bloc in r.iter_content(chunk_size=1 << 16):
                    fh.write(bloc)
            octets = os.path.getsize(tmp)
            lecteur = PdfReader(tmp)
            pages = [p.extract_text() or "" for p in lecteur.pages]
            texte = "\n\f\n".join(pages)      # \f : la coupure de page, gardée
            cible = _chemin_texte(dept, fic)
            with gzip.open(cible, "wt", encoding="utf-8") as fh:
                fh.write(texte)
            vides = sum(1 for p in pages if len(p.strip()) < 40)
            ecrire_journal(dept, {
                "url": fic["url"], "etat": "moissonne", "geste": "moisson",
                "annee": fic["annee"], "recueil": fic["recueil"],
                "octets_pdf": octets, "octets_texte": os.path.getsize(cible),
                "pages": len(pages), "pages_vides": vides,
                "scan_probable": len(pages) > 0 and vides / len(pages) > 0.5,
                "secondes": round(time.time() - t0, 1),
            })
            if garder_pdf:
                os.replace(tmp, cible[:-len(".txt.gz")] + ".pdf")
            print(f"  [{i}/{len(a_faire)}] {fic['recueil'][:48]:<48} "
                  f"{len(pages):>4} p  {octets/1024**2:>6.1f} Mo -> "
                  f"{os.path.getsize(cible)/1024:>7.0f} Ko"
                  f"{'  SCAN ?' if vides / max(len(pages), 1) > 0.5 else ''}")
        except Exception as e:                # noqa: BLE001 — on journalise tout
            ecrire_journal(dept, {"url": fic["url"], "etat": "erreur",
                                  "geste": "moisson", "motif": f"{type(e).__name__}: {e}"})
            print(f"  [{i}/{len(a_faire)}] ! {fic['recueil'][:48]} — {e}")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)


# ---------------------------------------------------------------------------
# État et complétude — `--termine` est le seul juge (leçon du §10.1 de REPRISE)
# ---------------------------------------------------------------------------
def etat(dept, depuis):
    an_min, mois_min = lire_depuis(depuis)
    borne = f"{an_min}-{mois_min:02d}"
    inv = lire_inventaire(dept)
    vu = lire_journal(dept)
    fics = [f for f in inv["fichiers"] if dans_fenetre(f, borne)]
    faits = [f for f in fics if (vu.get(f["url"]) or {}).get("etat") == "moissonne"]
    erreurs = [u for u, e in vu.items() if e.get("etat") == "erreur"]
    scans = [e for e in vu.values() if e.get("scan_probable")]
    print(f"département {dept} — fenêtre à partir de {borne}")
    print(f"  inventaire : {len(fics)} fichier(s) dans la fenêtre, "
          f"{len({f['page_recueil'] for f in fics})} recueil(s) "
          f"({len(inv['fichiers'])} fichier(s) inventoriés en tout)")
    if fics:
        resumer_inventaire(fics)
    print(f"  moissonnés : {len(faits)} / {len(fics)}")
    print(f"  en erreur  : {len(erreurs)}")
    print(f"  scans probables : {len(scans)}")
    return len(fics), len(faits), len(erreurs)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dept", required=True)
    ap.add_argument("--depuis", default="2026-02",
                    help="AAAA ou AAAA-MM. Défaut : les six derniers mois "
                         "(décision du 11 août 2026 — on travaille le récent, "
                         "pas dix ans d'archives).")
    ap.add_argument("--inventaire", action="store_true")
    ap.add_argument("--moissonner", action="store_true")
    ap.add_argument("--garder-pdf", action="store_true")
    ap.add_argument("--plafond", type=int, default=None,
                    help="ne moissonner que N fichiers — pour mesurer avant le lot")
    ap.add_argument("--etat", action="store_true")
    ap.add_argument("--termine", action="store_true")
    ap.add_argument("--pause", type=float, default=None,
                    help="secondes entre deux appels — À MONTER, pas à baisser. "
                         "Le 11 août 2026, ~70 pages à 1 appel/s ont suffi à faire "
                         "fermer les connexions par la plateforme des préfectures.")
    a = ap.parse_args()

    if a.pause:
        global PAUSE, PAUSE_PDF
        PAUSE = a.pause
        PAUSE_PDF = max(a.pause, PAUSE_PDF)

    sources = lire_sources()
    if a.dept not in sources:
        raise SystemExit(
            f"département {a.dept} absent de referentiel/sources_raa.csv — "
            "il est NON INSTRUIT, ce qui n'est pas la même chose que sans arrêtés")

    if a.inventaire:
        inventorier(a.dept, a.depuis, sources)
    if a.moissonner:
        moissonner(a.dept, a.depuis, garder_pdf=a.garder_pdf, plafond=a.plafond)
    if a.etat:
        etat(a.dept, a.depuis)
    if a.termine:
        total, faits, erreurs = etat(a.dept, a.depuis)
        reste = total - faits + erreurs
        print(f"\n{faits}/{total} moissonné(s), {reste} restant(s)")
        sys.exit(0 if total and reste == 0 else 1)
    if not any([a.inventaire, a.moissonner, a.etat, a.termine]):
        ap.print_help()


if __name__ == "__main__":
    main()

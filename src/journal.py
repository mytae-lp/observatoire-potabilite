# -*- coding: utf-8 -*-
"""
Le journal de reprise d'un département, et le cache de son énumération.

    data/journal/dept_<dept>.jsonl     ce qui a été traité, commune par commune
    data/brut/<dept>/_communes.json    l'énumération, centroïdes compris

Ce fichier était le haut de `fetch_departement.py`. Il en est sorti pour une
raison de fond : **le journal doit être écrit par un processus qui n'ouvre pas
la base.** C'est lui qui permet de séparer les deux gestes que le projet
confondait —

    moissonner   réseau seul, parallèle, aucune base    src/moisson.py
    ingérer      base seule, hors ligne, quelques min   src/ingerer.py

— et il porte déjà tout ce qu'il faut pour cela : statut de couverture,
prélèvements retenus, commune de prélèvement en cas de repli, et l'identité
complète de la commune (nom, codes postaux, centroïde). Une moisson terminée
se figera donc **sans redemander une seule ligne à Hub'Eau**.

Ce que le journal N'EST PAS
---------------------------
Il n'est pas la vérité sur ce qui est en base. Le journal dit ce qui a été
*moissonné* ; ce qui est *ingéré* se lit dans la base elle-même, et ce qui est
*publiable* se lit dans les tables figées avec leur `version_referentiel`
(§8bis). Confondre les trois est l'erreur qui a fait citer pendant deux jours
un chiffre du Rhône qui n'existait dans aucune version figée.

Écriture concurrente
--------------------
La moisson parallèle fait écrire plusieurs fils dans le même fichier. Deux
protections, et elles ne se remplacent pas :

  · **un verrou par département** — deux `write()` simultanés sur le même
    fichier peuvent s'entrelacer et produire une ligne JSON illisible, donc
    une commune silencieusement perdue de la reprise ;
  · **une ligne écrite d'un seul `write`** — le mode ligne à ligne du système
    de fichiers ne garantit rien au-delà.

Le format reste strictement celui d'avant : un journal écrit par
`fetch_departement.py` se relit par `moisson.py`, et réciproquement. Un
département déjà collecté ne se recollecte pas.
"""
import json
import os
import re
import threading

import brut
from common import JOURNAL_DIR

_VERROUS = {}
_VERROU_REGISTRE = threading.Lock()


def _verrou(dept):
    with _VERROU_REGISTRE:
        v = _VERROUS.get(str(dept))
        if v is None:
            v = _VERROUS[str(dept)] = threading.Lock()
        return v


# ---------------------------------------------------------------------------
# Journal de reprise
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
    """Ajoute une entrée. Sûr entre fils : un verrou par département."""
    ligne = json.dumps(entree, ensure_ascii=False) + "\n"
    with _verrou(dept):
        with open(chemin_journal(dept), "a", encoding="utf-8") as fh:
            fh.write(ligne)


def reste_a_faire(communes, vu):
    """
    Les communes encore à traiter, dans l'ordre.

    **Une commune EN ERREUR n'est pas une commune faite.** Défaut réel, trouvé
    le 8 août 2026 : neuf communes du Tarn — dont Castres et Cordes-sur-Ciel —
    ont échoué sur des coupures réseau de Hub'Eau, sept d'affilée. Le journal
    portait bien leur échec, mais la reprise les considérait comme traitées et
    ne les redemandait jamais. Elles seraient restées « non documentées » à
    tort, ce qui est le pire cas du §2.4 transposé à la commune : une absence
    de donnée qui n'est pas une absence de fait, présentée comme un état
    stable. Un échec réseau est transitoire ; il se retente.

    La règle vit ici, et non recopiée dans chaque appelant : `--termine`, la
    boucle de `fetch_departement.py` et celle de `moisson.py` la partagent.
    """
    return [c for i, c in sorted(communes.items())
            if (vu.get(i) or {}).get("etat") in (None, "erreur")]


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


def lire_depts(texte):
    """
    « 69,71,01 » ou « 69 71 01 » -> ['69', '71', '01'] — sans doublon, dans l'ordre.

    Les doublons sont retirés en gardant le premier : moissonner deux fois le
    même département dans un seul lot serait une charge inutile sur un service
    public gratuit (§3.2), et l'ingérer deux fois du travail pour rien.
    """
    bruts = str(texte).replace(";", ",").replace(" ", ",").split(",")
    out, vus = [], set()
    for d in bruts:
        d = d.strip().upper()
        if d and d not in vus:
            vus.add(d)
            out.append(d)
    return out


# Un code de département : 2 chiffres, 2A/2B pour la Corse, 3 chiffres outre-mer.
#
# Le filtre n'est pas décoratif. Un dossier synchronisé produit des noms comme
# `dept_28 (# Edit conflict 2026-08-09 ujbaa9C #).jsonl`, et sans ce contrôle
# le fichier de conflit était énuméré comme un département à part entière : le
# tableau d'état annonçait « 222 communes traitées » pour un département qui
# n'existe pas, et le total de ce qui reste à faire devenait faux.
_CODE_DEPT = re.compile(r"^(?:[0-9]{2}[AB0-9]?|[0-9]{3})$")


def departements_du_cache():
    """Les départements pour lesquels quelque chose a été moissonné."""
    depts = set()
    if os.path.isdir(brut.BRUT_DIR):
        depts.update(d for d in os.listdir(brut.BRUT_DIR)
                     if os.path.isdir(os.path.join(brut.BRUT_DIR, d)))
    if os.path.isdir(JOURNAL_DIR):
        for f in os.listdir(JOURNAL_DIR):
            if f.startswith("dept_") and f.endswith(".jsonl"):
                depts.add(f[len("dept_"):-len(".jsonl")])
    return sorted(d for d in depts if _CODE_DEPT.match(d.upper()))

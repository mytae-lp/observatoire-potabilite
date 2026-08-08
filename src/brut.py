# -*- coding: utf-8 -*-
"""
Le cache brut : ce que Hub'Eau a répondu, tel quel, gardé sur disque.

    data/brut/<dept>/<code_prelevement>.jsonl.gz

Pourquoi ce fichier existe
--------------------------
`data/eau.duckdb` n'est pas versionnée et « se reconstruit ». À 45 bulletins,
reconstruire coûtait quelques minutes de collecte. À l'échelle d'un département
— le Tarn en porte plusieurs milliers — reconstruire voudrait dire plusieurs
heures de charge sur un service public gratuit et sans clé, **à chaque fois
qu'un bug d'ingestion est corrigé ou qu'une colonne est ajoutée**. Ce serait
exactement la charge abusive que le §3.2 interdit, et elle serait entièrement
évitable : la réponse ne change pas, c'est notre lecture qui change.

Le cache sépare donc deux gestes qui étaient confondus :

  · **collecter** — une fois, en ligne, poliment ;
  · **ingérer** — autant de fois qu'on veut, hors ligne, sans réseau.

Ce que le cache garde, et ce qu'il ne garde pas
-----------------------------------------------
Il garde la **réponse de la source**, pas notre interprétation : une ligne JSON
par ligne de résultat, dans l'ordre reçu. Aucun champ n'est écarté, aucune
valeur n'est convertie. C'est la matière première, et elle doit pouvoir être
relue par quelqu'un qui ne connaît pas ce dépôt.

Il ne garde **ni verdict ni seuil** : ceux-là dépendent du référentiel daté, ils
vivent dans les tables figées avec leur `version_referentiel` (§8bis). Mélanger
les deux ferait du cache une deuxième source de vérité, et elles divergeraient.

Poids mesuré le 8 août 2026 : un bulletin de 317 paramètres pèse 421 Ko en JSON
et **16 Ko une fois gzippé**. Un département de ~5 000 bulletins tient donc dans
~80 Mo. Non versionné (cf. `.gitignore`), mais à conserver et à sauvegarder :
c'est le seul objet du dépôt qu'on ne peut pas refabriquer tout seul.
"""
import glob
import gzip
import json
import os

from common import RACINE

BRUT_DIR = os.path.join(RACINE, "data", "brut")


def _dossier(dept):
    return os.path.join(BRUT_DIR, str(dept or "inconnu"))


def chemin(dept, code_prelevement):
    return os.path.join(_dossier(dept), f"{code_prelevement}.jsonl.gz")


def existe(dept, code_prelevement):
    return os.path.exists(chemin(dept, code_prelevement))


def ecrire(dept, code_prelevement, rows):
    """
    Écrit les lignes brutes d'un prélèvement. Écriture atomique : on passe par
    un fichier temporaire renommé à la fin, sinon une coupure au mauvais moment
    laisserait un `.gz` tronqué que `lire()` prendrait pour un bulletin valide
    — et un bulletin amputé qui passe sous SEUIL_COMPLET disparaît de l'analyse
    sans que rien ne le signale (§2.3).
    """
    os.makedirs(_dossier(dept), exist_ok=True)
    final = chemin(dept, code_prelevement)
    temporaire = final + ".part"
    with gzip.open(temporaire, "wt", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporaire, final)
    return final


def lire(dept, code_prelevement):
    """Les lignes brutes d'un prélèvement, ou None s'il n'est pas au cache."""
    chem = chemin(dept, code_prelevement)
    if not os.path.exists(chem):
        return None
    rows = []
    try:
        with gzip.open(chem, "rt", encoding="utf-8") as fh:
            for ligne in fh:
                ligne = ligne.strip()
                if ligne:
                    rows.append(json.loads(ligne))
    except (OSError, EOFError, json.JSONDecodeError) as e:
        # Un cache illisible n'est pas une donnée absente : on le dit, et on
        # laisse l'appelant retourner au réseau plutôt qu'ingérer un fragment.
        print(f"    cache brut illisible ({type(e).__name__}) : {chem}")
        return None
    return rows


def lister(dept=None):
    """[(dept, code_prelevement, chemin), ...] — ce que le cache contient."""
    if dept:
        motif = os.path.join(_dossier(dept), "*.jsonl.gz")
    else:
        motif = os.path.join(BRUT_DIR, "*", "*.jsonl.gz")
    out = []
    for chem in sorted(glob.glob(motif)):
        cp = os.path.basename(chem)[:-len(".jsonl.gz")]
        out.append((os.path.basename(os.path.dirname(chem)), cp, chem))
    return out


def etat(dept=None):
    """Compte et poids du cache — pour la page d'état et le rapport."""
    entrees = lister(dept)
    octets = sum(os.path.getsize(c) for _d, _cp, c in entrees)
    return {"bulletins": len(entrees), "octets": octets,
            "mo": round(octets / (1024 * 1024), 1)}

# -*- coding: utf-8 -*-
"""
Le relevé qui alimente l'alerte « analyse complète ancienne » (src/suivi_panel.py).

    py -X utf8 src/relever_suivi_panel.py

Pour chaque commune dont la dernière analyse complète a 24 mois ou plus, il
relève par UN appel Hub'Eau : combien de contrôles ont eu lieu depuis, leur
taille médiane, et surtout **la date de la dernière mesure de chaque substance
qui dépassait alors**. Écrit .

Trois choses à savoir avant de le relancer :

1. **Il n'ouvre pas la base.** Sa matière première est ce que le site a publié
   dans  — donc il faut avoir republié après toute
   collecte, sinon il travaille sur un corpus périmé.
2. **C'est l'ANCIENNETÉ de la dernière mesure qui fait foi**, jamais un test
   binaire « a-t-il été mesuré depuis ». Un paramètre recontrôlé une fois puis
   abandonné huit ans passerait pour suivi — l'erreur a été commise le 13 août
   2026 et rattrapée sur Réclainville, qui ressortait « rien d'abandonné »
   alors que trois substances s'arrêtent en septembre 2020.
3. **Idempotent, et reprenable** : une commune déjà présente dans le fichier de
   sortie n'est pas rappelée, et les incidents réseau sont repris avec une
   attente qui double. Un lot interrompu se relance sans précaution — c'est
   arrivé deux fois le 13 août.

Les deux populations sont traitées : les communes ayant leur propre analyse
complète et celles documentées par le bulletin de leur réseau. Décision de
Yannick du 13 août 2026 ; pour les secondes, le texte de l'alerte nomme le
réseau et le lieu du prélèvement.
"""
import csv
import gzip
import os
import sys
import time
from collections import defaultdict
from datetime import date

import requests

API = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis"
UA = ("Observatoire-potabilite/1.0 (projet citoyen de donnees ouvertes ; "
      "contact via editions-mytae)")
PAUSE = 0.4
SEUIL_MOIS = 24
AUJ = date.today()
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.path.join(RACINE, "site", "public", "donnees")
SORTIE = os.path.join(RACINE, "data", "suivi_panel",
                      "alerte_panel_reduit.csv")
COLONNES = ["code_insee", "commune", "dept", "statut", "commune_prelevement",
            "date_derniere_complete", "mois_ecoules", "nb_parametres",
            "nb_controles_depuis", "dernier_controle", "mediane_taille_controle",
            "nb_depassements_alors", "substances_abandonnees", "detail_abandons"]


def mois_depuis(iso):
    d = date(int(iso[:4]), int(iso[5:7]), int(iso[8:10]))
    return ((AUJ.year - d.year) * 12 + (AUJ.month - d.month)
            - (1 if AUJ.day < d.day else 0))


def lire(chemin):
    ouvre = gzip.open if chemin.endswith(".gz") else open
    with ouvre(chemin, "rt", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


# --- les candidats, les deux populations ----------------------------------
candidats = []
for r in lire(os.path.join(DONNEES, "couverture_communes.csv")):
    d = r.get("date_prelevement") or ""
    if not d or r["statut"] == "non_documentee":
        continue
    m = mois_depuis(d)
    if m >= SEUIL_MOIS:
        r["_mois"] = m
        candidats.append(r)
candidats.sort(key=lambda x: -x["_mois"])
print(f"{len(candidats)} candidat(s) à {SEUIL_MOIS} mois ou plus "
      f"({sum(1 for c in candidats if c['statut'] == 'analysee')} avec analyse "
      f"propre, {sum(1 for c in candidats if c['statut'] == 'rattachee_reseau')} "
      f"rattachée(s) au réseau)")

# --- ce qui dépassait à cette analyse complète ----------------------------
voulus = defaultdict(set)
for c in candidats:
    voulus[c["dept"]].add(c["code_prelevement"])
depassements = defaultdict(list)
for dept, codes in voulus.items():
    chemin = os.path.join(DONNEES, f"verdicts_{dept}.csv.gz")
    if not os.path.exists(chemin):
        print(f"  !! pas d'export de détail pour {dept} — "
              f"{len(codes)} bulletin(s) sans liste de dépassements")
        continue
    for v in lire(chemin):
        if v["code_prelevement"] in codes and v["depasse_applicable"] == "1":
            depassements[v["code_prelevement"]].append(v["libelle_parametre"])

# --- reprise : ce qui est déjà fait ---------------------------------------
faits = set()
if os.path.exists(SORTIE):
    faits = {r["code_insee"] for r in lire(SORTIE)}
    print(f"{len(faits)} commune(s) déjà traitée(s) — elles seront sautées")

reste = [c for c in candidats if c["code_insee"] not in faits]
print(f"{len(reste)} appel(s) à passer\n")

f = open(SORTIE, "a", encoding="utf-8", newline="")
w = csv.writer(f, delimiter=";")
if not faits:
    w.writerow(COLONNES)

def obtenir(u, essais=4):
    """
    Un appel, avec reprise sur incident réseau.

    Une seule coupure a tué le premier lot au bout de 34 communes sur 413 : sur
    quelques centaines d'appels, un délai dépassé n'est pas un accident, c'est
    une certitude. L'attente double à chaque échec — on ne rappelle jamais plus
    vite un service qui vient de ne pas répondre (CLAUDE.md §3.2).
    """
    attente = 5
    for n in range(1, essais + 1):
        try:
            r = requests.get(u, headers={"User-Agent": UA}, timeout=180)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if n == essais:
                raise
            print(f"    incident ({type(e).__name__}), reprise dans "
                  f"{attente} s [{n}/{essais - 1}]", flush=True)
            time.sleep(attente)
            attente *= 2


for i, c in enumerate(reste, 1):
    insee, depuis = c["code_insee"], c["date_prelevement"][:10]
    lignes, url, page = [], None, 1
    while True:
        u = url or (f"{API}?code_commune={insee}&date_min_prelevement={depuis}"
                    f"&size=5000&page={page}")
        d = obtenir(u)
        lignes += d.get("data") or []
        if not d.get("next"):
            break
        url, page = d["next"], page + 1
        time.sleep(PAUSE)

    prels = defaultdict(set)
    for l in lignes:
        prels[l["code_prelevement"]].add(l.get("libelle_parametre"))
    prels.pop(c["code_prelevement"], None)      # l'analyse complète elle-même

    # L'ANCIENNETÉ de la dernière mesure, jamais un booléen (REPRISE §19.10).
    derniere = {}
    for l in lignes:
        if l["code_prelevement"] == c["code_prelevement"]:
            continue
        p, dt = l.get("libelle_parametre"), l["date_prelevement"][:10]
        if p and (p not in derniere or dt > derniere[p]):
            derniere[p] = dt

    abandons = []
    for p in depassements.get(c["code_prelevement"], []):
        dt = derniere.get(p)
        m = mois_depuis(dt) if dt else None
        if m is None or m >= SEUIL_MOIS:
            abandons.append((p, dt, m))

    dates = sorted({l["date_prelevement"][:10] for l in lignes
                    if l["code_prelevement"] in prels})
    tailles = sorted(len(s) for s in prels.values())
    w.writerow([
        insee, c["commune"], c["dept"], c["statut"],
        c.get("commune_prelevement") or "", depuis, c["_mois"],
        c["nb_parametres"], len(prels), dates[-1] if dates else "",
        tailles[len(tailles) // 2] if tailles else 0,
        len(depassements.get(c["code_prelevement"], [])),
        len(abandons),
        " | ".join(f"{p} (dernière mesure {dt or 'jamais depuis'}"
                   + (f", {m} mois)" if m is not None else ")")
                   for p, dt, m in abandons),
    ])
    f.flush()
    if i % 25 == 0 or i == len(reste):
        print(f"  {i}/{len(reste)}", flush=True)
    time.sleep(PAUSE)

f.close()
print(f"\n-> {SORTIE}")

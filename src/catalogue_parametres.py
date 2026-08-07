# -*- coding: utf-8 -*-
"""
Récolte du catalogue réel des paramètres du contrôle sanitaire.

    python3 src/catalogue_parametres.py --depts 17,31,28,51 --communes 10

Produit referentiel/catalogue_parametres_hubeau.csv : un inventaire, daté et
reproductible, de ce que le contrôle sanitaire mesure VRAIMENT, avec pour
chaque paramètre son code Hub'Eau, son numéro CAS, son unité et la limite de
qualité telle que l'administration la déclare.

Pourquoi ce fichier existe
--------------------------
Le référentiel de seuils (referentiel/referentiel_seuils.csv) est saisi à la
main sur textes réglementaires : c'est la valeur ajoutée du projet et ça le
reste. Mais un bulletin complet porte 350 à 400 paramètres, dont ~300
pesticides nommés, quand le référentiel en décrit 54. Sans ce catalogue, 90 %
des mesures d'un bulletin ne sont rattachées à rien et ne pèsent sur aucun
verdict : la base conclut « aucun dépassement » après n'avoir lu qu'un
dixième de l'analyse. C'est exactement le travers que CLAUDE.md §2.3 interdit,
transposé du niveau du bulletin au niveau du paramètre.

Ce catalogue N'EST PAS un référentiel de seuils datés. Il ne porte qu'une
grille : celle d'aujourd'hui, telle que déclarée. Il ne dit rien de 2016 ni
du seuil le plus strict au monde — ces deux colonnes restent le travail
manuel et sourcé du projet.

Ce script fait des requêtes HTTP : environnement avec accès réseau depuis le
shell (cf. CLAUDE.md §3.1).
"""
import argparse
import collections
import csv
import datetime
import os
import sys
import time

from common import CATALOGUE_CSV, SEUIL_COMPLET, norm
import hubeau


def bulletins_echantillon(dept, n_communes, depuis=None):
    """Les n derniers bulletins complets du département, un par commune."""
    communes = hubeau.lister_communes(dept)
    retenus = []
    for insee, nom in sorted(communes.items()):
        if len(retenus) >= n_communes:
            break
        try:
            bulletins = hubeau.derniers_bulletins_complets(insee, depuis=depuis)
        except Exception as e:
            print(f"    {insee} {nom or ''} — ignoré ({type(e).__name__}: {e})")
            continue
        if not bulletins:
            continue
        # un seul bulletin par commune suffit pour inventorier des libellés
        b = max(bulletins.values(), key=lambda r: len(r))
        retenus.append((insee, nom, b))
        print(f"    {insee} {nom or ''} — {len(b)} paramètres")
        time.sleep(hubeau.PAUSE_COMMUNE)
    return retenus


def recolter(depts, n_communes, depuis=None):
    """(code_parametre, libellé) -> agrégat des observations."""
    obs = collections.defaultdict(lambda: {
        "libelles": collections.Counter(),
        "cas": collections.Counter(),
        "unites": collections.Counter(),
        "limites": collections.Counter(),
        "references": collections.Counter(),
        "nb_mesures": 0,
        "nb_bulletins": 0,
        "depts": set(),
    })
    for dept in depts:
        print(f"\ndépartement {dept}")
        for insee, _nom, rows in bulletins_echantillon(dept, n_communes, depuis):
            vus_ce_bulletin = set()
            for r in rows:
                code = r.get("code_parametre")
                lib = r.get("libelle_parametre")
                if not lib:
                    continue
                cle = str(code) if code not in (None, "") else f"SANSCODE:{norm(lib)}"
                o = obs[cle]
                o["libelles"][lib] += 1
                if r.get("code_parametre_cas"):
                    o["cas"][r["code_parametre_cas"]] += 1
                if r.get("libelle_unite"):
                    o["unites"][r["libelle_unite"]] += 1
                if r.get("limite_qualite_parametre"):
                    o["limites"][r["limite_qualite_parametre"]] += 1
                if r.get("reference_qualite_parametre"):
                    o["references"][r["reference_qualite_parametre"]] += 1
                o["nb_mesures"] += 1
                o["depts"].add(dept)
                if cle not in vus_ce_bulletin:
                    o["nb_bulletins"] += 1
                    vus_ce_bulletin.add(cle)
    return obs


def ecrire(obs, chemin=CATALOGUE_CSV, depts=(), n_communes=0):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    entete = [
        "code_parametre", "libelle_parametre", "libelle_norm", "code_cas",
        "unite", "limite_declaree", "reference_declaree",
        "nb_mesures", "nb_bulletins", "departements", "variantes_libelle",
    ]
    lignes = []
    for cle, o in obs.items():
        lib = o["libelles"].most_common(1)[0][0]
        variantes = [l for l, _ in o["libelles"].most_common()[1:]]
        lignes.append({
            "code_parametre": "" if cle.startswith("SANSCODE:") else cle,
            "libelle_parametre": lib,
            "libelle_norm": norm(lib),
            "code_cas": o["cas"].most_common(1)[0][0] if o["cas"] else "",
            "unite": o["unites"].most_common(1)[0][0] if o["unites"] else "",
            "limite_declaree": o["limites"].most_common(1)[0][0] if o["limites"] else "",
            "reference_declaree": o["references"].most_common(1)[0][0] if o["references"] else "",
            "nb_mesures": o["nb_mesures"],
            "nb_bulletins": o["nb_bulletins"],
            "departements": "|".join(sorted(o["depts"])),
            "variantes_libelle": "|".join(variantes[:6]),
        })
    lignes.sort(key=lambda d: (-d["nb_mesures"], d["libelle_parametre"]))

    with open(chemin, "w", encoding="utf-8", newline="") as fh:
        fh.write(
            f"# Catalogue des paramètres réellement mesurés par le contrôle sanitaire.\n"
            f"# Récolté le {datetime.date.today().isoformat()} sur Hub'Eau qualite_eau_potable/resultats_dis,\n"
            f"# à partir des derniers bulletins complets (> {SEUIL_COMPLET} paramètres)\n"
            f"# de {n_communes} commune(s) par département, départements {','.join(depts)}.\n"
            f"# limite_declaree = limite_qualite_parametre telle que fournie par la source :\n"
            f"# c'est la grille D'AUJOURD'HUI, pas un seuil daté. Voir CLAUDE.md §2.5 et §2.7.\n"
            f"# Reproductible : python3 src/catalogue_parametres.py --depts {','.join(depts)} --communes {n_communes}\n"
        )
        w = csv.DictWriter(fh, fieldnames=entete, delimiter=";")
        w.writeheader()
        w.writerows(lignes)
    return len(lignes)


def main():
    p = argparse.ArgumentParser(description="Inventaire des paramètres du contrôle sanitaire")
    p.add_argument("--depts", default="17,31,28,51",
                   help="départements à échantillonner, séparés par des virgules")
    p.add_argument("--communes", type=int, default=10,
                   help="nombre de communes à échantillonner par département")
    p.add_argument("--depuis", help="année minimale de prélèvement (ex. 2023)")
    a = p.parse_args()

    depts = [d.strip() for d in a.depts.split(",") if d.strip()]
    obs = recolter(depts, a.communes, a.depuis)
    n = ecrire(obs, depts=depts, n_communes=a.communes)

    avec_limite = sum(1 for o in obs.values() if o["limites"])
    avec_cas = sum(1 for o in obs.values() if o["cas"])
    sans_code = sum(1 for k in obs if k.startswith("SANSCODE:"))
    print(f"\ncatalogue : {n} paramètres distincts -> {CATALOGUE_CSV}")
    print(f"  dont limite de qualité déclarée : {avec_limite} ({100*avec_limite/max(n,1):.0f} %)")
    print(f"  dont numéro CAS                 : {avec_cas} ({100*avec_cas/max(n,1):.0f} %)")
    if sans_code:
        print(f"  ! {sans_code} paramètre(s) sans code Hub'Eau (appariement par libellé seul)")


if __name__ == "__main__":
    sys.exit(main())

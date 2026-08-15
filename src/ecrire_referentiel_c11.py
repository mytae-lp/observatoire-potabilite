# -*- coding: utf-8 -*-
"""
Phase 5 du chantier C11 : écrire au référentiel ce que les dossiers ont établi.

    py -X utf8 src/ecrire_referentiel_c11.py --essai     # montre, n'écrit rien
    py -X utf8 src/ecrire_referentiel_c11.py --faire     # écrit

Pourquoi un script et pas une saisie à la main
----------------------------------------------
Il y a ~360 lignes à ajouter dans un CSV de **21 colonnes séparées par des
points-virgules**. La saisie manuelle d'un tel volume est exactement la façon
dont l'erreur de décalage a été commise **deux fois** en août 2026 (`CLAUDE.md`
§5) — et les deux fois rien ne l'a signalée. Un générateur relit la même source
à chaque exécution, et son résultat se rejoue.

Ce que ce script écrit, et ce qu'il n'écrit pas
-----------------------------------------------
**Il n'écrit AUCUN seuil**, à une exception près, lue et sourcée : la ligne
« Total microcystines ». Tout le reste est une ligne SANS valeur, dont le seul
effet est de faire passer le libellé de `rien_ne_se_prononce_non_instruit` à
`rien_ne_se_prononce_etabli` — c'est-à-dire de « nous n'avons rien écrit » à
« nous avons cherché, aucun texte n'oppose de valeur ».

Le discriminant est `fiabilite IS NOT NULL` dans la cascade de `build_db.py` :
il suffit qu'une ligne existe. D'où l'importance de la colonne `fiabilite`.

**`verifie` n'est donné qu'aux dossiers réellement instruits le 15 août 2026.**
Les quatre dossiers que personne n'a lus contre un texte reçoivent
`a_verifier` : écrire « nous avons cherché » sans avoir cherché serait la faute
même que le §2.7 interdit, et elle serait invisible.
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RACINE, REF_CSV, norm

CLASSEMENT = os.path.join(RACINE, "data", "etudes",
                          "classement_non_apparies_2026-08-15.csv")

COLONNES = ["code_parametre", "code_cas", "libelle", "famille", "unite",
            "seuil_2016", "seuil_2026", "date_applicabilite_2026",
            "seuil_conditionnel", "condition_seuil", "statut_2026",
            "seuil_futur", "date_applicabilite_futur", "seuil_strict",
            "base_seuil_strict", "pe_reglementaire", "pe_scientifique",
            "sources", "fiabilite", "est_agregat", "cancerogenicite_circ"]

# ---------------------------------------------------------------------------
# Ce que chaque dossier a établi. La colonne `fiabilite` est la plus
# importante : elle dit si un texte a réellement été lu pour cette famille.
#
# JAMAIS de point-virgule dans une valeur (§5) — il décalerait la ligne.
# ---------------------------------------------------------------------------
DOSSIERS = {
    "cyanobacteries": dict(
        famille="biologique", fiabilite="verifie", sources="REG-01|REG-03|REG-10",
        statut="aucun seuil en eau destinee a la consommation humaine. La valeur "
               "de 100 000 cellules par mL releve des baignades artificielles "
               "(arrete du 15/04/2019), hors perimetre, et a ete supprimee le "
               "19/12/2025. Denombrement de surveillance, sans verdict"),
    "pcb": dict(
        famille="organique", fiabilite="verifie", sources="REG-01|REG-03|REG-10",
        statut="aucune valeur en eau destinee a la consommation humaine, et "
               "ABSENT DU PROGRAMME D ANALYSES. Six recherches distinctes sur "
               "quatre textes, aucune occurrence. La mesure n est expliquee ni "
               "par une valeur ni par une obligation de controle"),
    "cov": dict(
        famille="organique", fiabilite="verifie", sources="REG-01|REG-03|REG-06",
        statut="aucune valeur opposable en eau destinee a la consommation "
               "humaine. Inventaire exhaustif des parametres organiques des "
               "annexes fait le 15/08/2026"),
    "hap": dict(
        famille="organique", fiabilite="verifie", sources="REG-01|REG-03|REG-06",
        statut="HAP individuel hors des sommes reglementaires. ATTENTION deux "
               "perimetres sous le meme sigle - 4 composes en eau distribuee "
               "(0,10 ug/L, sans benzo a pyrene) et 6 en eau brute (1 ug/L)"),
    "phtalates": dict(
        famille="organique", fiabilite="verifie", sources="REG-01|REG-03|REG-06",
        statut="aucune valeur en eau destinee a la consommation humaine. Statut "
               "de perturbateur endocrinien a distinguer du statut reglementaire"),
    "phenols": dict(
        famille="organique", fiabilite="verifie", sources="REG-01|REG-03|REG-06",
        statut="aucune valeur en eau destinee a la consommation humaine. Le "
               "nonylphenol porte une valeur de VIGILANCE, distincte"),
    "medicaments": dict(
        famille="organique", fiabilite="verifie", sources="REG-01|REG-03|REG-06",
        statut="residu de medicament humain ou veterinaire. Aucune valeur en eau "
               "destinee a la consommation humaine"),
    "pesticides_divers": dict(
        famille="organique", fiabilite="verifie", sources="REG-01|REG-03|REG-06",
        statut="aucune valeur individuelle trouvee. A REPRENDRE contre la "
               "definition du pesticide de REG-05 - si la substance y entre, "
               "elle tombe sous la limite de 0,1 ug/L par substance"),
    "desinfection": dict(
        famille="desinfection", fiabilite="verifie", sources="REG-03|REG-06",
        statut="aucune valeur chiffree pour le desinfectant residuel. Seule "
               "existe une reference QUALITATIVE en II References de qualite - "
               "absence d odeur ou de saveur desagreable. Aucune obligation de "
               "desinfecter l eau elle-meme"),
    "calco_carbonique": dict(
        famille="mineral", fiabilite="verifie", sources="REG-03|REG-10",
        statut="support de calcul de l equilibre calcocarbonique. La note 3 de "
               "l annexe I de REG-10 impose que calcium magnesium et potassium "
               "soient exprimes concomitamment au calcul. L exigence est "
               "QUALITATIVE - les eaux doivent etre a l equilibre "
               "calcocarbonique ou legerement incrustantes - et sans valeur"),
    # --- les quatre dossiers que PERSONNE n'a instruits contre un texte ---
    "parametres_generaux": dict(
        famille=None, fiabilite="a_verifier", sources="",
        statut="NON INSTRUIT contre un texte au 15/08/2026 - aucune source lue "
               "pour cette famille. La ligne existe pour rendre la lacune "
               "visible, pas pour conclure"),
    "microbiologie": dict(
        famille="microbiologique", fiabilite="a_verifier", sources="",
        statut="NON INSTRUIT contre un texte au 15/08/2026. Les revivifiables "
               "relevent d une norme exprimee en VARIATION dans un rapport, que "
               "le modele ne sait pas porter - gele en amelioration future"),
    "organoleptique": dict(
        famille="organoleptique", fiabilite="a_verifier", sources="",
        statut="NON INSTRUIT contre un texte au 15/08/2026. Parametres "
               "qualitatifs sans echelle numerique"),
    "speciation_metaux": dict(
        famille="metal", fiabilite="a_verifier", sources="",
        statut="NON INSTRUIT - forme chimique d un metal deja au referentiel. "
               "La question est le PERIMETRE (entre-t-elle dans le total ?), "
               "pas la valeur. Trancher AVANT tout appariement par code"),
    # --- traités à part, voir SPECIAUX ---
    "radiologique": None,
    "pfas": None,
}

# ---------------------------------------------------------------------------
# Les gestes ciblés, tous lus et sourcés.
# ---------------------------------------------------------------------------

# 1. Les 14 radionucléides : concentration dérivée = dénominateur de la dose
#    indicative, JAMAIS un seuil individuel (RAD-02 tableau 1).
RADIO_DANS_SOMME = dict(
    famille="radiologique", fiabilite="verifie", sources="RAD-01|RAD-02",
    statut="dans somme - concentration derivee entrant au calcul de la dose "
           "indicative (RAD-02 tableau 1). Ce N EST PAS une limite "
           "individuelle. Le verdict se rend sur la dose indicative, jamais sur "
           "un radionucleide isole")

# 2. Les activités globales : valeurs guides, pas des seuils. Trois sources
#    concordantes — annexe III de RAD-01, colonne NOTES de REG-03, article 3
#    de RAD-02 qui écrit le mot.
RADIO_GUIDE = dict(
    famille="radiologique", fiabilite="verifie", sources="RAD-01|RAD-02|REG-03",
    statut="valeur guide - seuil de DECLENCHEMENT d investigation, pas de "
           "conformite. Alpha globale 0,10 Bq/L et beta globale residuelle "
           "1,0 Bq/L declenchent l analyse des radionucleides specifiques. "
           "Trois sources concordantes. Aucune non-conformite ne s y fonde")

# 3. Les 16 PFAS hors des 4 : ils sont dans la somme des 20, qui porte la limite.
PFAS_DANS_SOMME = dict(
    famille="PFAS", fiabilite="verifie", sources="REG-01|REG-03",
    statut="dans somme - entre dans la Somme de 20 substances "
           "perfluoroalkylees, qui porte la limite de 0,10 ug/L. La directive "
           "nomme 20 substances en annexe III partie B point 3. Aucune valeur "
           "individuelle")

# 4. Les variants de microcystine : dans la somme « Total microcystines ».
MICRO_DANS_SOMME = dict(
    famille="cyanotoxine", fiabilite="verifie", sources="REG-01|REG-03",
    statut="dans somme - entre dans Total microcystines, qui porte la limite de "
           "1,0 ug/L. Le droit francais ne nomme aucun variant individuel")

# 5. LA SEULE VALEUR ÉCRITE PAR CE SCRIPT, et elle est lue.
MICRO_TOTAL = {
    "code_parametre": "", "code_cas": "", "libelle": "Total microcystines",
    "famille": "cyanotoxine", "unite": "µg/L", "seuil_2016": "1.0",
    "seuil_2026": "1.0", "date_applicabilite_2026": "",
    "seuil_conditionnel": "", "condition_seuil": "",
    "statut_2026": "limite - ensemble des variants intra et extracellulaires, "
                   "uniquement pour les eaux d origine superficielle. Present "
                   "des le JO du 06/02/2007, redaction actuelle de l arrete du "
                   "30/12/2022 en vigueur au 01/01/2023. La valeur n a jamais "
                   "bouge. La directive nomme la microcystine-LR a 1,0 ug/L "
                   "(art. 25, applicable au 12/01/2026) - le droit francais "
                   "retient l agregat",
    "seuil_futur": "", "date_applicabilite_futur": "", "seuil_strict": "1.0",
    "base_seuil_strict": "Limite francaise et valeur de la directive (UE) "
                         "2020-2184 annexe I partie B, identiques a 1,0 ug/L",
    "pe_reglementaire": "non", "pe_scientifique": "a_documenter",
    "sources": "REG-01|REG-03", "fiabilite": "verifie", "est_agregat": "oui",
    "cancerogenicite_circ": "",
}

# 6. Les cinq lignes de l'article 25 sans date d'applicabilité.
#    L'arrêté français ne diffère RIEN : « 2026 » apparaît zéro fois dans REG-03,
#    qui entre en vigueur le 1er janvier 2023 (C11.7.1).
DATES_A_POSER = {
    "bisphenol a": "2023-01-01",
    "chlorates": "2023-01-01",
    "chlorites": "2023-01-01",
    "somme de 20 substances perfluoroalkylees (pfas)": "2023-01-01",
    "uranium": "2023-01-01",
}

RADIONUCLEIDES = ("activité américium", "activité carbone", "activité cobalt",
                  "activité césium", "activité iode", "activité plomb",
                  "activité plutonium", "activité polonium", "activité radium",
                  "activité strontium", "activité uranium")
ACTIVITES_GLOBALES = ("activité alpha globale", "activité béta globale",
                      "activité béta glob", "activité bêta attribuable")


def dossier_special(libelle, dossier):
    """Rend le gabarit d'une ligne qui n'obéit pas à son dossier."""
    b = libelle.lower()
    if dossier == "radiologique":
        if any(b.startswith(x) for x in RADIONUCLEIDES):
            return RADIO_DANS_SOMME
        if any(x in b for x in ACTIVITES_GLOBALES):
            return RADIO_GUIDE
        return RADIO_GUIDE
    if dossier == "pfas":
        return PFAS_DANS_SOMME
    if "microcystine" in b or "nodularine" in b:
        return MICRO_DANS_SOMME
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--faire", action="store_true", help="écrit réellement")
    p.add_argument("--essai", action="store_true", help="montre sans écrire")
    a = p.parse_args()
    if not (a.faire or a.essai):
        sys.exit("préciser --essai ou --faire")

    # Ce que le référentiel connaît déjà : on n'écrase jamais une ligne.
    deja = {}
    with open(REF_CSV, encoding="utf-8") as fh:
        lecteur = csv.DictReader(fh, delimiter=";")
        anciennes = list(lecteur)
    for l in anciennes:
        deja[norm(l.get("libelle"))] = l

    nouvelles, sautees, par_dossier = [], [], {}
    with open(CLASSEMENT, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            lib, dos = r["libelle"], r["dossier"]
            cle = norm(lib)
            if cle in deja:
                sautees.append(lib)
                continue
            gab = dossier_special(lib, dos) or DOSSIERS.get(dos)
            if gab is None:
                sautees.append(lib + " (dossier inconnu)")
                continue
            ligne = {c: "" for c in COLONNES}
            ligne.update({
                "code_parametre": r.get("code_parametre", ""),
                "code_cas": r.get("code_cas", ""),
                "libelle": lib,
                "famille": gab.get("famille") or "",
                "unite": r.get("unite", ""),
                "statut_2026": gab["statut"],
                "sources": gab["sources"],
                "fiabilite": gab["fiabilite"],
                "est_agregat": "non",
            })
            nouvelles.append(ligne)
            par_dossier.setdefault(dos, [0, gab["fiabilite"]])[0] += 1

    # La ligne de somme des microcystines, si elle manque.
    if norm(MICRO_TOTAL["libelle"]) not in deja:
        nouvelles.append({c: MICRO_TOTAL.get(c, "") for c in COLONNES})
        par_dossier["(somme microcystines)"] = [1, "verifie"]

    # Les cinq dates à poser sur des lignes existantes.
    datees = []
    for l in anciennes:
        cle = norm(l.get("libelle"))
        if cle in DATES_A_POSER and not (l.get("date_applicabilite_2026") or "").strip():
            l["date_applicabilite_2026"] = DATES_A_POSER[cle]
            datees.append(l["libelle"])

    print("=" * 74)
    print("PHASE 5 — ce qui sera écrit au référentiel")
    print("=" * 74)
    print("  lignes existantes            : %d" % len(anciennes))
    print("  lignes NOUVELLES             : %d" % len(nouvelles))
    print("  libellés sautés (déjà connus): %d" % len(sautees))
    print()
    for dos, (n, fia) in sorted(par_dossier.items(), key=lambda kv: -kv[1][0]):
        print("    %-24s %3d lignes   fiabilite=%s" % (dos, n, fia))
    print()
    print("  dates d'applicabilité posées : %d  -> %s"
          % (len(datees), ", ".join(datees) if datees else "aucune"))
    print()
    seuils = [l for l in nouvelles if l["seuil_2026"] or l["seuil_2016"]]
    print("  lignes PORTANT UN SEUIL      : %d" % len(seuils))
    for l in seuils:
        print("      %s = %s %s" % (l["libelle"], l["seuil_2026"], l["unite"]))

    if a.essai:
        print()
        print("  --essai : RIEN N'A ÉTÉ ÉCRIT.")
        return

    total = anciennes + nouvelles
    vus = set()
    for l in total:
        cle = norm(l.get("libelle"))
        if cle in vus:
            sys.exit("ARRÊT : libellé en double après fusion -> %s" % l.get("libelle"))
        vus.add(cle)

    with open(REF_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLONNES, delimiter=";",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(total)
    print()
    print("  ÉCRIT : %s — %d lignes au total." % (REF_CSV, len(total)))
    print("  Étape suivante : py -X utf8 tests/test_verdict.py")


if __name__ == "__main__":
    main()

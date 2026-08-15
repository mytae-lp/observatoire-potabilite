# -*- coding: utf-8 -*-
"""
Classer les libellés mesurés que le référentiel ne connaît pas.

    py -X utf8 src/etude_non_apparies.py

Écrit `data/etudes/classement_non_apparies_<jour>.csv` — un libellé par ligne,
son volume, l'état qu'on lui propose, le dossier de sourçage dont il relève, et
le motif. **Ce fichier ne touche pas au référentiel** : c'est un matériau de
travail, destiné à être relu par Yannick avant qu'une seule ligne ne soit écrite
dans `referentiel/referentiel_seuils.csv`.

Pourquoi ce fichier existe
--------------------------
Au 15 août 2026, **376 libellés** portent l'attribution
`rien_ne_se_prononce_non_instruit` — 1 364 674 mesures, dont **405 959
quantifiées**. Le décompte brut donne l'impression d'un gouffre. Il n'en est
pas un, et le dire serait un faux positif (§2.13) : la **température de l'eau**
est dans la liste, et elle n'a pas de seuil parce qu'elle n'en a pas à avoir.

C'est la leçon du 9 août qui se répète (`docs/AUDIT_NON_APPARIES.md`) : *le
compte n'est pas un compte d'angles morts*. Il faut donc trier avant de compter,
et c'est ce que fait ce script.

Le mécanisme qu'on exploite, et il existe déjà
----------------------------------------------
La cascade d'attribution de `build_db.py` distingue « établi » de « non
instruit » sur **un seul critère** : `fiabilite IS NOT NULL`, c'est-à-dire
**l'existence d'une ligne au référentiel**. Il n'y a donc aucun code à écrire
pour sortir un libellé de « non instruit » — il faut lui écrire sa ligne.

De même, `norme_non_exprimee` se déclenche sur `statut_2026 LIKE 'reference%'`.
Une ligne sans seuil mais avec ce statut suffit à dire « la norme existe, elle
ne s'exprime pas en valeur ».

Seul `hors_perimetre` n'existe pas encore et demande une branche supplémentaire
(décision de Yannick du 15 août 2026 : il sort AUSSI du dénominateur de
`pct_couverture`, mesuré à +0,34 point, de 90,07 % à 90,41 %).

Ce que le classement ne fait PAS
--------------------------------
Il ne décide d'aucune valeur de seuil, et il n'en écrit aucune. Les colonnes
`etat_propose` et `dossier` disent **où ranger le travail**, jamais quel chiffre
opposer. Tout libellé rangé dans un dossier `a_instruire` reste `non_instruit`
tant que sa source primaire n'a pas été lue (§2.7).

La colonne `certitude` sépare ce qui est mécanique de ce qui est un jugement :

  · `mecanique` — le libellé s'auto-désigne (« PCB 138 », « Activité Radium 226 »)
  · `a_relire`  — c'est une lecture de ma part, et elle peut être fausse

Les `A_DECIDER` sont les libellés qu'aucune règle n'attrape. Ils ne sont pas un
défaut du script : ce sont exactement ceux qui demandent une décision humaine.
"""
import csv
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import duckdb

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RACINE, "data", "eau.duckdb")
SORTIE = os.path.join(RACINE, "data", "etudes")


# ---------------------------------------------------------------------------
# Les règles, DANS L'ORDRE. La première qui accroche gagne.
#
# Chaque entrée : (motif regex, etat_propose, dossier, motif lisible, certitude)
#
# L'ordre est signifiant. « Chlorophylle A » doit être pris par le dossier
# cyanobactéries AVANT que la règle des phénols ne voie « phyll ». Les règles
# les plus spécifiques passent donc en premier.
# ---------------------------------------------------------------------------
REGLES = [
    # --- contexte du prélèvement : ce ne sont pas des paramètres de qualité ---
    (r"^Temp(érature|  ?de mesure)|^Temp de mesure|^Température de l",
     "hors_perimetre", "contexte",
     "condition de la mesure, pas objet de la mesure", "a_relire"),
    (r"^Pluviométrie",
     "hors_perimetre", "contexte",
     "donnée météo du jour du prélèvement", "mecanique"),
    (r"^Prélèvement sous acréditation",
     "hors_perimetre", "contexte",
     "métadonnée d'assurance qualité, pas une mesure", "mecanique"),

    # --- radiologique : chaque radionucléide se nomme lui-même ---
    (r"^Activité ",
     "non_instruit", "radiologique",
     "volet radiologique, angle mort declare du CLAUDE.md §8", "mecanique"),

    # --- PFAS : le nom porte 'perfluoro' ou le sigle entre parentheses ---
    (r"perfluoro|\(PF[A-Z]{2,5}\)",
     "non_instruit", "pfas",
     "PFAS hors des 20 du referentiel — question de perimetre (§2.14)", "mecanique"),

    # --- PCB : congeneres numerotes et leurs agregats ---
    (r"^PCB \d+$|^Polychlorobiph",
     "non_instruit", "pcb",
     "congenere ou agregat PCB, aucune ligne au referentiel", "mecanique"),

    # --- cyanobacteries et phytoplancton : surveillance, souvent eau brute ---
    (r" sp( \(cellules\))?$|\(cellules\)$|^% de colonies|^Colonies de|cyanobact|"
     r"^Chlorophylle|^Nodularine|^Cel\. de cyano|phytoplancton",
     "non_instruit", "cyanobacteries",
     "denombrement de taxon — verifier s'il porte sur l'eau distribuee", "a_relire"),

    # --- equilibre calco-carbonique ---
    (r"^Titre (hydrotim|alcalim)|^Calcium$|^Carbonates$|^Hydrogénocarbonates$|"
     r"équilibre|Equilibre calcocarb|^Essai marbre|^Indice de Leroy|"
     r"^CO2 libre|^Anhydride carbonique|^Silicates|^pH Equilibre",
     "norme_non_exprimee", "calco_carbonique",
     "equilibre calcocarbonique : la norme existe, non chiffree — A VERIFIER sur arrete",
     "a_relire"),
    (r"^Conductivité",
     "norme_non_exprimee", "calco_carbonique",
     "encadree par une PLAGE, que le modele ne sait pas porter", "a_relire"),

    # --- organoleptique ---
    (r"\(qualitatif\)|^Odeur|^Saveur|^Chang\. anormal de coloration|"
     r"^Couleur|^Aspect",
     "norme_non_exprimee", "organoleptique",
     "acceptabilite au consommateur, norme non chiffree — A VERIFIER", "a_relire"),

    # --- desinfection residuelle ---
    (r"^Chlore |^Bioxyde de chlore|^Résiduel de ClO2|^Ozone$|^Chlorite",
     "non_instruit", "desinfection",
     "residuel de desinfection — instruire si une valeur est opposable", "a_relire"),

    # --- microbiologie sans valeur chiffree ou hors perimetre distribue ---
    (r"^Bact\. aér\. revivifiables",
     "norme_non_exprimee", "microbiologie",
     "norme exprimee en VARIATION, pas en valeur absolue — A VERIFIER", "a_relire"),
    (r"^Bact\. et spores sulfito|^Bactéries sulfato|^Legionella|^Légionella|"
     r"^Salmonelles|^Pseudomonas|^Coliformes thermotol|giardia|crypto|^Amibe",
     "non_instruit", "microbiologie",
     "germe sans seuil au referentiel — verifier s'il releve de l'eau distribuee",
     "a_relire"),

    # --- HAP ---
    (r"^Hydrocarbures polycycliques|^Anthracène|^Acénapht|^Benzanthracène|"
     r"^Chrysène|^Dibenzo\(a,h\)|^Fluoranthène|^Fluorène$|^Naphtalène|"
     r"^Phénantrène|^Pyrène|^Pérylène|^Méthyl\(2\)fluoranthène|"
     r"^Méthyl\(2\)naphtalène|^Méthyl-1 naphtalène",
     "non_instruit", "hap",
     "HAP individuel hors des 4 sommes reglementaires", "mecanique"),

    # --- phtalates ---
    (r"phtalate|phthalate|^DEHP|^DBP ",
     "non_instruit", "phtalates",
     "phtalate — statut PE a distinguer du statut reglementaire (§2.15)", "mecanique"),

    # --- phenols et alkylphenols ---
    (r"phénol|phenol|Phénols",
     "non_instruit", "phenols",
     "phenol ou alkylphenol sans seuil au referentiel", "mecanique"),

    # --- medicaments et residus veterinaires ---
    (r"^17b-estradiol|^Acide salicylique|^Naproxene|^Tétracyclines|"
     r"^Ivermectine|^Afoxolaner",
     "non_instruit", "medicaments",
     "residu de medicament humain ou veterinaire — souvent liste de vigilance UE",
     "mecanique"),

    # --- COV, solvants chlores et aromatiques ---
    (r"^Dichloro|^Trichloro|^Tétrachloro|^Tetrachloro|^Bromo|^Dibromo|"
     r"^Chloro|^Chlorobenz|^Chloroéthane|^Chlorométhane|^Chloroprène|"
     r"^Hexachloro|^Pentachlorobenzène|^Fréon|^Triclhloro|"
     r"^Toluène|^Xylène|^Xylenes|^Ethylbenzène|^Styrène|^Cumène|^Mésitylène|"
     r"^Pseudocumène|^Cymène|^Butyl benzène|^Propylbenzène|^Isobutylbenzène|"
     r"^tert-butylbenzene|^Triméthylbenzène|^Biphényle|^Benzidine|"
     r"^Méthyl tert-buthyl|^Ethyl tert-buthyl|^Méthyl isobutyl cétone|"
     r"^1,4 dioxane|^Nitrobenzène|^3-Chloropropène|^Diisopropyl ether|"
     r"^Dichlorodiisopropyl éther|^Tétrachlorure de carbone",
     "non_instruit", "cov",
     "COV ou solvant — plusieurs ont une valeur UE, c'est une DETTE REELLE",
     "a_relire"),

    # --- parametres generaux de qualite ---
    (r"^Oxygène dissous|^DCO$|^Matières en suspension|^Orthophosphates|"
     r"^Polyphosphates|^Phosphore total|^Bromures|^AOX$|^Indice hydrocarbure|"
     r"^Hydrocarbures dissous|^Agents de surface|^Oxydab\. KMnO4|"
     r"^anion phosphonate|^Absorbance à 254|^Transmittance UV",
     "non_instruit", "parametres_generaux",
     "parametre general — verifier s'il porte une reference de qualite", "a_relire"),

    # --- speciation d'un metal DEJA au referentiel : cas a part ---
    #
    # « Arseniates » n'est pas une substance inconnue, c'est UNE FORME de
    # l'arsenic, qui a bien sa limite (§2.7 : ne pas l'ecrire ici sans la lire).
    # La question n'est donc pas « quel seuil » mais « cette forme entre-t-elle
    # dans le total arsenic, ou est-elle mesuree a cote ». C'est exactement le
    # cas des codes portant deux objets reglementaires (§11.2) : trancher AVANT
    # d'apparier, sous peine de fabriquer un faux positif.
    (r"^Arseniates",
     "non_instruit", "speciation_metaux",
     "forme chimique d'un metal deja au referentiel — question de perimetre, pas de valeur",
     "a_relire"),

    # --- pesticides, metabolites et divers organiques ---
    (r"^Chloroneb|^Desmethylnorflurazon|^Ethyluree|^Diphenylurée|"
     r"^N-\(2-Chloro|^benzotriazole|^Monobutylétain|^Phosphate de tributyle|"
     r"^2,2',4,4',5,5'-",
     "non_instruit", "pesticides_divers",
     "substance de synthese sans ligne au referentiel", "a_relire"),
]


def classer(libelle):
    for motif, etat, dossier, raison, certitude in REGLES:
        if re.search(motif, libelle, re.IGNORECASE):
            return etat, dossier, raison, certitude
    return "A_DECIDER", "a_decider", "aucune regle n'accroche ce libelle", "a_relire"


def main():
    if not os.path.exists(DB):
        sys.exit("base absente : %s" % DB)
    os.makedirs(SORTIE, exist_ok=True)
    jour = datetime.date.today().isoformat()
    chemin = os.path.join(SORTIE, "classement_non_apparies_%s.csv" % jour)

    con = duckdb.connect(DB, read_only=True)
    rows = con.execute("""
        SELECT v.libelle_parametre,
               ANY_VALUE(v.code_parametre), ANY_VALUE(v.code_cas), ANY_VALUE(v.unite),
               COUNT(*)                                            AS n,
               SUM(CASE WHEN v.est_quantifie THEN 1 ELSE 0 END)     AS nq,
               MAX(CASE WHEN v.est_quantifie THEN v.resultat_num END) AS mx,
               COUNT(DISTINCT p.code_insee)                        AS communes,
               COUNT(DISTINCT c.code_departement)                  AS depts,
               MIN(p.date_prelevement), MAX(p.date_prelevement)
        FROM v_mesures_verdict v
        JOIN prelevements p ON p.code_prelevement = v.code_prelevement
        JOIN communes c     ON c.code_insee = p.code_insee
        WHERE v.attribution = 'rien_ne_se_prononce_non_instruit'
        GROUP BY 1
    """).fetchall()
    con.close()

    lignes = []
    for r in rows:
        etat, dossier, raison, certitude = classer(r[0])
        lignes.append({
            "libelle": r[0], "code_parametre": r[1] or "", "code_cas": r[2] or "",
            "unite": r[3] or "", "nb_mesures": r[4], "nb_quantifiees": r[5],
            "taux_quantif_pct": round(100.0 * r[5] / r[4], 1) if r[4] else 0,
            "max_quantifie": r[6] if r[6] is not None else "",
            "nb_communes": r[7], "nb_departements": r[8],
            "premier": str(r[9])[:10], "dernier": str(r[10])[:10],
            "etat_propose": etat, "dossier": dossier,
            "motif": raison, "certitude": certitude,
        })
    # Tri : par dossier, puis par volume quantifié décroissant — on lit d'abord
    # ce qui pèse.
    lignes.sort(key=lambda d: (d["dossier"], -d["nb_quantifiees"], -d["nb_mesures"]))

    champs = list(lignes[0].keys())
    with open(chemin, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=champs, delimiter=";")
        w.writeheader()
        w.writerows(lignes)

    # --- ce qu'on montre à l'écran : le bilan par dossier, rien d'autre ---
    print("%d libelles classes -> %s" % (len(lignes), chemin))
    print()
    par_dossier = {}
    for d in lignes:
        c = par_dossier.setdefault(d["dossier"], {"lib": 0, "mes": 0, "q": 0,
                                                  "etat": d["etat_propose"]})
        c["lib"] += 1
        c["mes"] += d["nb_mesures"]
        c["q"] += d["nb_quantifiees"]
    print("%-20s %-22s %5s %10s %10s" % ("dossier", "etat propose", "lib.",
                                         "mesures", "quantif."))
    print("-" * 72)
    for nom, c in sorted(par_dossier.items(), key=lambda kv: -kv[1]["q"]):
        print("%-20s %-22s %5d %10d %10d" % (nom, c["etat"], c["lib"], c["mes"], c["q"]))
    print("-" * 72)
    print("%-43s %5d %10d %10d" % ("TOTAL", len(lignes),
                                   sum(c["mes"] for c in par_dossier.values()),
                                   sum(c["q"] for c in par_dossier.values())))

    restants = [d for d in lignes if d["etat_propose"] == "A_DECIDER"]
    if restants:
        print()
        print("--- %d libelles qu'aucune regle n'attrape ---" % len(restants))
        for d in sorted(restants, key=lambda x: -x["nb_mesures"]):
            print("  %-50s %7d mes. %7d quant." % (d["libelle"][:50],
                                                   d["nb_mesures"], d["nb_quantifiees"]))


if __name__ == "__main__":
    main()

# Index des sources — Projet Observatoire de la potabilité réglementaire

> Catalogue du dossier `Sources/`. Mis à jour le 21 juillet 2026.

## Nomenclature (à utiliser partout)

Chaque source porte un **code stable `FAMILLE-NN`**. Ce code est l'identifiant de citation : dans le référentiel, les notes ou le futur site, il suffit d'écrire par exemple **[PFAS-05]** pour pointer sans ambiguïté vers la source.

- Le **préfixe** indique la famille — et donc le sous-dossier :
  `REG` = réglementation & seuils · `PFAS` = comparatif international PFAS · `PE` = perturbateurs endocriniens · `MIX` = effet cocktail & mélanges · `MET` = métabolites & charge totale.
- Le **numéro** est attribué à la création et **ne change plus** (même si le fichier est déplacé).
- Nom de fichier complet : `CODE_Organisme_description_annee.ext` (le code reste toujours le premier segment).
- **Règle de tenue** : une nouvelle source = un fichier nommé selon ce schéma (prochain numéro libre de sa famille) rangé dans le sous-dossier de sa famille + une ligne ajoutée ici.

```
Data - Analyse de la qualité de l'eau en France/
├── Méthode_Analyse_Bulletins_Eau_HubEau.md
├── Plan_Projet_Observatoire_Potabilite_Reglementaire.md
├── INDEX_SOURCES.md            → ce fichier
└── Sources/
    ├── REG_Reglementation_et_seuils/
    ├── PFAS_Comparatif_international/
    ├── PE_Perturbateurs_endocriniens/
    ├── MIX_Effet_cocktail_et_melanges/
    ├── MET_Metabolites_et_charge_totale/
    └── _doublons_a_supprimer/    → à vider manuellement
```

---

## REG — Réglementation & seuils

| Code | Fichier | Source | Ce qu'elle fournit | Lien d'origine |
|---|---|---|---|---|
| **REG-01** | `REG-01_UE_directive-2020-2184.pdf` | UE, directive (UE) 2020/2184 | **Toutes les valeurs paramétriques UE 2026**. Source-mère des seuils | https://eur-lex.europa.eu/eli/dir/2020/2184/oj |
| **REG-02** | `REG-02_FR_arrete-2007-01-11_grille-2016.pdf` | France, JO du 06/02/2007 | Arrêté du 11/01/2007 — **grille française « 2016 »** | https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000465574/ |
| **REG-03** | `REG-03_FR_arrete-2022-12-30_grille-2026.pdf` | France, JO du 31/12/2022 | Arrêté du 30/12/2022 — **grille actuelle** (antimoine 5→10, sélénium 10→20, bore 1→1,5) | https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000046849403 |
| **REG-04** | `REG-04_OMS_directives-qualite-eau-4e-ed.pdf` | OMS, *Guidelines for Drinking-water Quality*, 4e éd. | **Valeurs guides sanitaires** + hypothèses d'exposition (60 kg, 2 L/j, allocation 20 %) | https://www.ncbi.nlm.nih.gov/books/NBK579461/ |

## PFAS — Comparatif international  (⚠️ = chiffre à verrouiller)

| Code | Fichier | Source | Ce qu'elle fournit | Lien d'origine |
|---|---|---|---|---|
| **PFAS-01** | `PFAS-01_US-EPA_regle-PFAS-MCL-4ngL_2024.pdf` | US EPA, Federal Register 2024-07773 | ⚠️ **MCL PFOA/PFOS = 4 ng/L** + Hazard Index | https://www.federalregister.gov/documents/2024/04/26/2024-07773/pfas-national-primary-drinking-water-regulation |
| **PFAS-02** | `PFAS-02_US-EPA_projet-revision_synthese_2025.pdf` | US EPA | ⚠️ Synthèse du **projet de révision 2025** | https://www.epa.gov/sdwa/proposed-pfas-rescission-rule |
| **PFAS-03** | `PFAS-03_US-EPA_projet-revision_texte_2026.pdf` | US EPA, Federal Register (20/05/2026) | Texte du projet de règle | https://www.epa.gov/sdwa/proposed-pfas-rescission-rule |
| **PFAS-04** | `PFAS-04_US-EPA_projet-revision_agenda-audience_2026.pdf` | US EPA | Ordre du jour audience publique (juillet 2026) | https://www.epa.gov/sdwa/proposed-pfas-rescission-rule |
| **PFAS-05** | `PFAS-05_OCDE_Danemark-somme4-2ngL.pdf` | OCDE, fiche pays Danemark | ⚠️ **Somme-4 PFAS = 2 ng/L** (la plus stricte au monde) | https://www.oecd.org/content/dam/oecd/en/topics/policy-sub-issues/risk-management-risk-reduction-and-sustainable-chemistry2/pfas-country-information/Denmark.pdf |
| **PFAS-06** | `PFAS-06_UBA_Allemagne-TrinkwV.pdf` | Allemagne, Umweltbundesamt | ⚠️ **Somme-4 = 20 ng/L**, THM = 50 µg/L, dates 2026/2028 | https://www.umweltbundesamt.de/en/press/pressinformation/new-drinking-water-ordinance-ensures-high-quality |
| **PFAS-07** | `PFAS-07_EFSA_dose-tolerable-groupe-PFAS_2020.pdf` | EFSA, *EFSA Journal* 2020;18(9):6223 | **Dose hebdo tolérable de groupe = 4,4 ng/kg/sem** | https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2020.6223 |

## PE — Perturbateurs endocriniens

| Code | Fichier | Source | Ce qu'elle fournit | Lien d'origine |
|---|---|---|---|---|
| **PE-01** | `PE-01_UE_edlists-liste1-PE-identifies.xlsx` | edlists.org (UE) | **Liste I** — PE **identifiés** au niveau UE (statut « avéré ») | https://edlists.org/the-ed-lists/list-i-substances-identified-as-endocrine-disruptors-by-the-eu |
| **PE-02** | `PE-02_UE_edlists-liste2-en-evaluation.xlsx` | edlists.org (UE) | **Liste II** — en cours d'évaluation | https://edlists.org/ |
| **PE-03** | `PE-03_UE_edlists-liste3-preoccupation-nationale.xlsx` | edlists.org (UE) | **Liste III** — préoccupation nationale/scientifique | https://edlists.org/ |
| **PE-04** | `PE-04_ECHA_bisphenols-PE-avere.pdf` | ECHA | Bisphénol A **PE avéré réglementaire** (seul contaminant de l'eau dans ce cas) | https://www.echa.europa.eu/hot-topics/bisphenols |
| **PE-05** | `PE-05_ANSES_strategie-PE-SNPE2.pdf` | ANSES | Stratégie PE (SNPE2) ; triptyque avéré/présumé/suspecté | https://www.anses.fr/en/content/accelerating-assessment-endocrine-disruptors |
| **PE-06** | `PE-06_TEDX_liste-PE-potentiels.pdf` | TEDX | Liste scientifique de PE potentiels | https://www.endocrinedisruption.org/interactive-tools/tedx-list-of-potential-endocrine-disruptors/about-the-tedx-list |
| **PE-07** | `PE-07_TEDX_liste-export-tableur.xls` | TEDX | **Export tableur** de la liste TEDX (à croiser avec les paramètres analysés) | idem TEDX |
| **PE-08** | `PE-08_ChemSec_SIN-List-PE.pdf` | ChemSec, SIN List | Liste scientifique PE (dont plusieurs PFAS) | https://sinlist.chemsec.org/endocrine-disruptors/ |
| **PE-09** | `PE-09_Endocrine-Society_hormones-et-PE.pdf` | Endocrine Society | Effets à faible dose, absence de seuil sûr | https://www.endocrine.org/ |

## MIX — Effet cocktail & mélanges

| Code | Fichier | Source | Ce qu'elle fournit | Lien d'origine |
|---|---|---|---|---|
| **MIX-01** | `MIX-01_EFSA_evaluation-cumulee-pesticides-FAQ.pdf` | EFSA | Groupes d'évaluation cumulée (CAG), MOET, additivité des doses | https://www.efsa.europa.eu/en/news/cumulative-risk-assessment-pesticides-faq |
| **MIX-02** | `MIX-02_Treu_facteur-melange-MAF_2024.pdf` | Treu et al. 2024, *Environ. Sci. Eur.* | ⚠️ Ampleur du **facteur mélange (MAF)** | https://link.springer.com/article/10.1186/s12302-024-00910-z |
| **MIX-03** | `MIX-03_Science_EDC-MixRisk-Kortenkamp_2020.pdf` | Kortenkamp et al. 2020, *Science* | EDC-MixRisk : risque des mélanges **systématiquement sous-estimé** | https://www.science.org/doi/10.1126/science.abe8244 |
| **MIX-04** | `MIX-04_Science_EDC-MixRisk-supplement_2020.pdf` | idem | Matériel supplémentaire | idem |
| **MIX-05** | `MIX-05_ANSES_polluants-emergents-eau-potable.pdf` | ANSES | Campagne nationale polluants émergents (métabolites, TFA) | https://www.anses.fr/en/content/emerging-pollutants-drinking-water-review-main-findings-latest-national-campaign |
| **MIX-06** | `MIX-06_Generations-Futures_Dans-mon-eau_2025.pdf` | Générations Futures, oct. 2025 | ⚠️ « Dans mon eau » (PFAS 96 % des communes ; 71 % métabolites non suivis — à vérifier) | https://www.generations-futures.fr/wp-content/uploads/2025/10/rapport-dans-mon-eau-vf.pdf |
| **MIX-07** | `MIX-07_US-EPA_Hazard-Index-PFAS-methode.pdf` | US EPA | **Méthode Hazard Index** (modèle d'indice cocktail) | https://www.epa.gov/system/files/documents/2024-04/pfas-npdwr_fact-sheet_hazard-index_4.8.24.pdf |

## MET — Métabolites & charge totale

| Code | Fichier | Source | Ce qu'elle fournit | Lien d'origine |
|---|---|---|---|---|
| **MET-01** | `MET-01_ANSES_avis-chlorothalonil-R417888-et-R471811_2024.pdf` | ANSES, avis du 29/04/2024, saisines 2023-SA-0041-a et 2023-SA-0142-a | R471811 reclassé **non pertinent** (0,1 → 0,9 µg/L, applicable au 29/04/2024, **sans rétroactivité**) ; R417888 classé **pertinent** (limite de qualité 0,1 µg/L, VST 3 µg/L UBA pour la restriction de consommation) — **deux conclusions opposées dans le même avis** | https://www.anses.fr/fr/system/files/EAUX2023SA0142.pdf |
| **MET-02** | `MET-02_Hamilton_seuil-0.1ugL-zero-substitution_2013.pdf` | Hamilton et al. 2013, *Environ. Sci. Technol.* | La limite pesticide **0,1 µg/L n'est pas sanitaire** (« zéro de substitution ») | https://pubs.acs.org/doi/10.1021/es304955g |

---

## Notes de tenue

- **Prochains numéros libres** : REG-05, PFAS-08, PE-10, MIX-08, MET-03.
- **Doublon à supprimer** : `Sources/_doublons_a_supprimer/` (copie identique, md5 vérifié, de PFAS-03). Suppression impossible depuis la session — **vider manuellement**.
- **Sources manquantes à ajouter** : rapport IGAS/IGEDD/CGAAER 2024 (→ MIX-08) ; California OEHHA Public Health Goals (→ PFAS-08 / REG-05) ; bilan national qualité eau/pesticides du ministère de la Santé (→ MET-03 ou MIX).
- **Chiffres ⚠️** : à confirmer dans les PDF avant inscription comme opposables dans le référentiel (lecture locale possible désormais).

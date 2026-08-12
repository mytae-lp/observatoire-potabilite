# Sourçage réglementaire — Phosphate de tributyle (SANDRE 1847, CAS 126-73-8)

Date du sourçage : 2026-08-11

Substance : phosphate de tributyle (tri-n-butyl phosphate, TBP, TnBP), CAS **126-73-8**,
formule C12H27O4P, unité de mesure dans le corpus : µg/L.
Corpus (chiffres **fournis par le brief**, non recomptés — la base `data/eau.duckdb` n'a pas été
ouverte, conformément à la consigne) : 1 520 mesures, 226 communes, 15 quantifications,
maximum **0,27 µg/L**, minimum quantifié **0,005 µg/L**, période 08/01/2016 → 04/11/2024.

## Avertissement d'identité — vérifié avant toute lecture

Le **phosphate de tributyle (126-73-8)** est un **ester organophosphoré** de l'acide phosphorique.
Il n'est **ni** le **tributylétain** (organostannique), **ni** le **dibutylétain cation**
(SANDRE 7074) ou le **monobutylétain cation** (SANDRE 2542, CAS 78763-54-9) présents par ailleurs
dans le corpus, **ni** un ester organophosphoré retardateur de flamme voisin (TCEP, TDCPP,
triphénylphosphate, tricrésylphosphate), **ni** un organophosphoré insecticide (chlorpyrifos,
diazinon, malathion), **ni** un paramètre minéral du phosphore (orthophosphates en PO₄, phosphore
total en mg de P₂O₅/L — unité ni identique ni convertible).

**Le piège s'est réellement présenté pendant ce sourçage** : dans les *Guidelines for
drinking-water quality* de l'OMS (REG-04), les quatre seules occurrences approchantes sont
`tributyltin` (l'organostannique), aux lignes 12344, 26185, 26222 et 30737 de l'extraction —
aucune ne porte sur le phosphate de tributyle. Elles ont été écartées.

Toutes les sources retenues ci-dessous portent le CAS 126-73-8 explicitement, sauf les textes
réglementaires qui ne nomment pas la substance — et c'est précisément l'objet du verdict.

---

## 1. Verdict

**C2 — aucune valeur réglementaire opposable, en France ni dans l'Union, ne nomme le phosphate de
tributyle dans l'eau destinée à la consommation humaine ; et la règle de catégorie « pesticides
(par substance individuelle) » ne s'y applique pas.**

Ce n'est **pas** un C-g. Le cas se distingue point par point du précédent biphényle :

| Critère | Biphényle (C-g retenu, non versé) | **Phosphate de tributyle** |
|---|---|---|
| Nommé dans un texte EDCH | non | **non** |
| Classement SANDRE | groupes 97 « Fongicides » **et** 204 « Liste B – Phytosanitaires » | **aucun groupe phytosanitaire** — classe chimique 65 « Organophosphorés », groupes 127/129/132/133 (polluants spécifiques de l'état écologique) et 211 |
| Base PPDB (substances actives phytopharmaceutiques) | fiche 82, *Substance type: Fungicide* | **absent de la base** |
| Usage phytosanitaire documenté | oui, interdit en Europe | **aucun trouvé** |
| Capté par `pesticide_individuel_0_1` | oui, sur 40 mesures | **non** (fait donné par le brief) |

Les quatre premières lignes se lisent dans les sources, la cinquième est un comportement de moteur
et ne fonde rien (§2.4 ci-dessous). **La conclusion tient sur le texte : le phosphate de tributyle
n'appartient à aucune des neuf catégories que l'annexe I énumère pour définir « pesticides ».**

Aucune valeur guide non opposable n'existe non plus au niveau international : l'OMS **a examiné**
la substance (EHC 112, IPCS, 1991) mais **n'a proposé ni valeur guide ni dose journalière
tolérable**, et le phosphate de tributyle est **totalement absent** des *Guidelines* 4ᵉ édition —
y compris de la table A3.2 des renoncements motivés. Deux valeurs sanitaires pour l'eau existent,
toutes deux **non opposables** et d'un ordre de grandeur très supérieur au corpus : 4 µg/L
(Minnesota, 2025) et 105 µg/L (calcul indicatif INERIS, 2013).

**Conséquence pratique à dire d'emblée** : maximum du corpus **0,27 µg/L**. C'est **au-dessus** de
la valeur qu'aurait portée la règle « pesticides » (0,10 µg/L) — d'où l'importance de ne pas
l'appliquer — et **très en dessous** de la seule valeur sanitaire calculée pour l'eau de boisson
(4 µg/L, facteur ~15). Le projet doit donc classer ces 1 520 mesures en **indéterminé**, ni
conforme ni dépassement : aucune norme ne les juge.

---

## 2. Valeurs

### 2.1 Registre réglementaire opposable — ce qui existe

| Valeur | Unité | Nature | Registre | Texte source | Date du texte | Date d'applicabilité | Fiabilité |
|---|---|---|---|---|---|---|---|
| *(aucune)* | — | limite de qualité EDCH nommant la substance | réglementaire opposable UE | Directive (UE) 2020/2184, **annexe I parties A, B et C et annexe III lues intégralement** | 16/12/2020 | 12/01/2023 | **verifie** — absence établie |
| *(aucune)* | — | idem | réglementaire opposable France, grille 2026 | Arrêté du 30 décembre 2022, annexes I et II | 30/12/2022 (JO 31/12/2022) | 01/01/2023 | **verifie** — absence établie |
| *(aucune)* | — | idem | réglementaire opposable France, grille 2016 | Arrêté du 11 janvier 2007, **rédaction d'origine** | 11/01/2007 | 11/01/2007 | **verifie** — absence établie |
| *(aucune)* | — | idem | France, norme en vigueur | Arrêté du 11 janvier 2007, **version consolidée**, annexe I (Légifrance `LEGIARTI000046890189`) | en vigueur au 01/01/2023 | — | **verifie** — absence établie |

**Les seuls paramètres organiques nommés à l'annexe I consolidée**, relevés un par un et vérifiés
absents du champ de notre substance : acides haloacétiques, acrylamide, benzène, benzo[a]pyrène,
bisphénol A, bromates, chlorates, chlorites, chlorure de vinyle, 1,2-dichloroéthane,
épichlorhydrine, HAP, total microcystines, somme des substances alkylées per et polyfluorées,
pesticides (par substance individuelle), aldrine/dieldrine/heptachlore/heptachlorépoxyde, total
pesticides, tétrachloroéthylène et trichloroéthylène, total THM.

### 2.2 Définition littérale des « pesticides » — la pièce centrale du dossier

**Directive (UE) 2020/2184, annexe I partie B, ligne « Pesticides »** (extraction du PDF local
REG-01, lignes 2007 à 2061 — texte anglais du JO L 435 du 23/12/2020, p. 37) :

> « `Pesticides' means:
> — organic insecticides,
> — organic herbicides,
> — organic fungicides,
> — organic nematocides,
> — organic acaricides,
> — organic algicides,
> — organic rodenticides
> — organic slimicides,
> — related products (inter alia, growth regulators),
> and their metabolites as defined in point (32) of Article 3 of Regulation (EC) No 1107/2009 of
> the European Parliament and of the Council, that are considered relevant for water intended for
> human consumption. […]
> The parametric value of 0,10 µg/l shall apply to each individual pesticide.
> In the case of aldrin, dieldrin, heptachlor and heptachlor epoxide, the parametric value shall
> be 0,030 µg/l. »

**Arrêté du 30 décembre 2022, annexe I** (extraction du PDF local REG-03, lignes 201 à 221),
transposition française, à la lettre :

> « Par pesticides, on entend :
> – les insecticides organiques ;
> – les herbicides organiques ;
> – les fongicides organiques ;
> – les nématocides organiques ;
> – les acaricides organiques ;
> – les algicides organiques ;
> – les rodenticides organiques ;
> – les produits antimoisissures organiques ;
> – les produits apparentés (notamment les régulateurs de croissance)
> et leurs métabolites, tels que définis à l'article 3, point 32), du règlement (CE) no 1107/2009
> du Parlement européen et du Conseil, qui sont considérés comme pertinents pour les eaux
> destinées à la consommation humaine. »

**La définition est une énumération de neuf fonctions d'usage, toutes phytopharmaceutiques ou
biocides.** Elle ne contient aucune catégorie chimique. Le rattachement d'une substance à cette
ligne suppose donc de démontrer un **usage** relevant de l'une de ces neuf fonctions.

### 2.3 Registre « valeur guide non opposable » — à ne jamais fusionner avec le précédent

| Valeur | Unité | Nature | Organisme | Source | Date | Fiabilité |
|---|---|---|---|---|---|---|
| **4** | **µg/L** | **Health-Based Value** (`nHBV`) court terme, subchronique **et** chronique pour l'eau de boisson — **valeur d'orientation sanitaire, non opposable** | **Minnesota Department of Health** (État du Minnesota, États-Unis) | *Toxicological Summary for: Tributyl phosphate*, Health Risk Assessment Unit — CAS 126-73-8 explicitement | publication web **mars 2025** | **verifie** (PDF lu verbatim) |
| **105** | µg/L | **QSdw_hh — norme de qualité pour la santé humaine via l'eau de boisson, *calculée* et donnée « à titre indicatif »**, non opposable, reprise par aucun texte | **INERIS** | Fiche *Valeur guide environnementale — Phosphate de tributyle*, DRC-10-102867-00045B | validation experts nov. 2012, version 3 du **27/03/2013** | **verifie** (lu verbatim, calcul reproduit dans le document) |
| **350** | µg/L | *indicatieve drinkwaterrichtwaarde* — valeur guide sanitaire indicative, non contraignante | **RIVM** (Pays-Bas) | Système *Risico's van stoffen*, fiche tributylfosfaat 126-73-8 | consultée le 11/08/2026 | **a_verifier** — lue sur la fiche de synthèse RIVM, pas dans le rapport primaire |
| **1,0** | µg/L | **paramètre de signalement** (*signaleringsparameter*) de la catégorie « **overige antropogene stoffen** » du **Drinkwaterbesluit** — **valeur de catégorie, pas nominative** ; déclenche une investigation, pas une non-conformité sanitaire | **Pays-Bas** | Drinkwaterbesluit / Drinkwaterregeling, bijlage A, via fiche RIVM | — | **a_verifier** — le Drinkwaterbesluit lui-même n'a pas pu être lu (voir §7) |
| **37** (eau douce) / **8** (eau marine) | µg/L | **valeur guide environnementale (VGE)** — protection des écosystèmes, **milieu naturel, pas eau du robinet** | INERIS | même fiche, page 1 | 27/03/2013 | **verifie** |
| **82** | µg/L | AA-QSwater_eco et MAC eau douce (écotoxicologie) | INERIS | même fiche, lignes 315-316 et 362 | 27/03/2013 | **verifie** |
| **30** | µg/kg de poids corporel/jour | **VTR orale chronique** — ce n'est **pas** une concentration dans l'eau et cela ne se compare à aucune mesure | INERIS | même fiche, ligne 826 | 27/03/2013 | **verifie** |
| **0,0059** | mg/kg/j | Reference Dose court terme (effets développementaux, rat) | Minnesota DH | *Toxicological Summary*, p. 1 | mars 2025 | **verifie** |

**Note d'unité, impérative** : les VGE (37 et 8 µg/L) et les NQE (82 µg/L) sont bien en µg/L mais
portent sur le **milieu aquatique**, jamais sur l'eau du robinet. Les VTR sont en µg ou mg **par kg
de poids corporel et par jour**. Aucune de ces valeurs ne se rapproche d'une mesure de bulletin.
Les seules valeurs comparables au corpus sont 4 µg/L (Minnesota), 105 µg/L (INERIS QSdw_hh),
350 µg/L (RIVM) et 1,0 µg/L (signalement néerlandais, valeur de catégorie).

### 2.4 La phrase qui ferme le dossier — citation verbatim

INERIS, fiche DRC-10-102867-00045B, section « **Norme de qualité pour la santé humaine via l'eau
de boisson (QSDW_HH)** », page 15 :

> « Pour le phosphate de tributyle, il n'existe aucune norme de qualité réglementaire dans l'eau
> de boisson fixée par la Directive 98/83/CE ou par l'OMS. »

Et sur le statut de la valeur qu'INERIS calcule ensuite (105 µg/L) :

> « on rappellera que ce calcul n'est donné qu'à titre indicatif et peut s'avérer inadéquat pour
> certaines substances et certaines populations. »

Deux réserves à porter : la fiche date de 2013 et vise la **directive 98/83/CE**, texte abrogé et
remplacé par la directive (UE) 2020/2184 ; l'absence a donc été **revérifiée directement** sur
2020/2184, sur l'arrêté de 2022 et sur l'annexe I consolidée (§2.1). Et le calcul de 105 µg/L
s'applique, de l'aveu du document, **à l'eau brute du milieu** (« en l'absence d'information, on
considérera que la fraction éliminée est nulle et le critère pour l'eau de boisson s'appliquera
alors à l'eau brute du milieu »).

### 2.5 Une valeur étrangère lue, puis écartée — le cas annoncé au brief s'est produit

La même fiche INERIS, page 3, rapporte sous « Normes de qualité existantes (ETOX, 2012) » :

> « Allemagne :
> – norme de qualité pour les eaux prélevées destinées à la consommation humaine = 10 µg/L,
> – critère de qualité pour l'eau douce = 9 µg/L »

**Cette valeur de 10 µg/L n'est pas retenue.** Trois motifs, tous vérifiés :

1. **la Trinkwasserverordnung ne connaît pas ce paramètre.** L'Anlage 2 de la TrinkwV 2023
   (`gesetze-im-internet.de/trinkwv_2023/anlage_2.html`) a été lue intégralement : ses Teil I et
   Teil II énumèrent 34 paramètres chimiques nommés (Acrylamid, Benzol, Bor, Bromat, Chrom,
   Cyanid, 1,2-Dichlorethan, Fluorid, Microcystin-LR, Nitrat, Pestizide, Pestizide-gesamt,
   Summe PFAS-20, Summe PFAS-4, Quecksilber, Selen, Tetrachlorethen und Trichlorethen, Uran,
   Antimon, Arsen, Benzo(a)pyren, Bisphenol A, Blei, Cadmium, Chlorat, Chlorit, Epichlorhydrin,
   HAA-5, Kupfer, Nickel, Nitrit, PAK, THM, Vinylchlorid). **Tributylphosphat n'y figure pas** ;
2. **le libellé même de la valeur porte sur un autre milieu** : « eaux **prélevées** destinées à la
   consommation humaine », c'est-à-dire la ressource brute, pas l'eau distribuée. Ce n'est pas le
   milieu de notre corpus de verdicts ;
3. **INERIS désavoue explicitement sa source.** Note 4 de la même page : « Les données issues de
   cette source (http://webetox.uba.de/webETOX/index.do) ne sont données qu'à titre indicatif ;
   elles n'ont donc pas fait l'objet d'une validation par l'INERIS. »

C'est très exactement le précédent décrit à la règle 1 du brief. La valeur est consignée ici pour
qu'on ne la « redécouvre » pas, et marquée **écartée**.

De la même page, écartée pour le même motif de milieu : **Pays-Bas, MPCdw,hh = 315 µg/L** (Smit et
Verbruggen, 2011) — norme de qualité eau potable dérivée, non lue en source primaire.

---

## 3. La question C-g, tranchée : la règle « pesticides » ne s'applique pas

### 3.1 La définition, appliquée à la substance

Les neuf catégories de l'annexe I sont des **fonctions d'usage**. Les usages documentés du
phosphate de tributyle, tous lus en source primaire, n'en relèvent d'aucune :

- INERIS, fiche DRC-10-102867-00045B, page 2 : « Le phosphate de tributyle est utilisé dans
  l'industrie en tant que **retardateur de flamme pour fluide hydraulique** et en tant que
  **solvant d'extraction** (principalement des métaux) **ou de purification** (UNEP, 2001). » ;
- SANDRE, fiche paramètre 1847 : « Substance chimique de formule brute C12H27O4P, de la famille
  des **organophosphorés**. » — la classe chimique retenue est 65 « Organophosphorés », qui est une
  classe **chimique**, pas une fonction d'usage ;
- OMS/IPCS, EHC 112 (1991) : évaluation consacrée aux usages industriels (fluides hydrauliques,
  solvant d'extraction), aucun usage phytosanitaire ni biocide décrit.

**Aucune source lue ne décrit un usage insecticide, herbicide, fongicide, nématocide, acaricide,
algicide, rodenticide, antimoisissure ou régulateur de croissance.**

### 3.2 Substance active phytopharmaceutique ou biocide dans l'UE ?

| Vérification | Résultat | Fiabilité |
|---|---|---|
| **PPDB** (Pesticide Properties DataBase, Univ. of Hertfordshire / AERU), index A-Z complet | **le phosphate de tributyle n'y figure pas** — ni sous « tributyl phosphate », ni sous « tributylphosphate » | **verifie** (index lu) |
| **Règlement (CE) 1107/2009** — statut d'approbation | **aucune approbation trouvée, aucune trace d'inscription** | **a_verifier** — la base européenne des pesticides est une application à formulaire, non atteinte par récupération d'URL |
| **Règlement (UE) 528/2012** — substance active biocide | **aucune approbation trouvée** | **a_verifier** — la fiche ECHA de la substance (`substanceinfo/100.004.365`) répond **HTTP 403** |
| **INERIS**, section « Évaluations existantes et informations réglementaires » | ne mentionne **que** REACH/CLP, OCDE HPVC et les arrêtés « polluants spécifiques de l'état écologique » ; **aucun statut phytosanitaire ni biocide** | **verifie** |

Comparaison qui donne sa force au constat : pour le **biphényle**, la PPDB porte une fiche
dédiée n° 82 mentionnant *Substance type: Fungicide* et un statut « Not approved / Expired » au
titre de 1107/2009 — c'est-à-dire qu'une approbation a existé. **Pour le phosphate de tributyle,
il n'y a pas de fiche du tout.** Ce n'est pas « non approuvé » : c'est hors du champ de la base.

### 3.3 La liste SANDRE — l'argument qui manque ici, et c'est décisif

Fiche paramètre **1847** (créée le 07/12/1999, dernière mise à jour le **29/01/2025**),
appartenances de groupes, relevées une par une :

| Groupe | Libellé | Nature |
|---|---|---|
| **65** | Organophosphorés | **classe chimique** de nomenclature |
| **127** | Polluants spécifiques de l'état écologique des eaux de surface | registre **DCE eaux de surface** |
| **129** | Polluants spécifiques de l'état écologique des eaux de surface_**Artois-Picardie** | idem, bassin |
| **132** | Polluants spécifiques de l'état écologique des eaux de surface_**Rhône-Méditerranée** | idem, bassin |
| **133** | Polluants spécifiques de l'état écologique des eaux de surface_**Corse** | idem, bassin |
| **211** | Substances pertinentes à surveiller dans les eaux de surface continentales | registre **DCE eaux de surface** |

**Aucun groupe phytosanitaire.** Ni le groupe 95 « Phytosanitaires », ni 97 « Fongicides », ni le
groupe 200, ni la « Liste A », ni la **« Liste B – Phytosanitaires » (groupe 204)**.

C'est l'inverse exact du biphényle. Le critère AQUAREF cité dans le dossier biphényle — la liste B
étant celle où « la décision sur le caractère pesticide ou pas doit être prise par le
gestionnaire » — **ne peut même pas être invoqué ici** : le phosphate de tributyle n'est dans
aucune des deux listes, donc la question du caractère pesticide n'est même pas ouverte par le
référentiel national de nomenclature. Le seul groupe qui pourrait tromper est le **65
« Organophosphorés »**, et c'est une **classe chimique** : elle contient aussi bien des
insecticides organophosphorés que des solvants et des retardateurs de flamme. **Une classe
chimique n'est pas une fonction d'usage, et la définition de l'annexe I est une liste de fonctions
d'usage.**

### 3.4 Le fait contraire, donné brut, avec sa portée exacte

**Un gestionnaire range effectivement le phosphate de tributyle dans une liste de « pesticides ».**
Bilan du contrôle sanitaire des EDCH de l'**ARS Île-de-France** pour 2021 (document publié par Eau
de Paris), **annexe 2 « LISTE DES PESTICIDES RECHERCHÉS »**, sous-titrée :

> « Nouvelle liste des pesticides ou métabolites de pesticides analysés dans le cadre du
> renouvellement du marché public du contrôle sanitaire des eaux destinées à la consommation
> humaine »

**« Phosphate de tributyle » y figure**, en colonne 4, entre « Pendiméthaline » et « Phoxine ».
Le **« Biphényle »** figure dans la même liste, ainsi que « Anthraquinone », « Dichlorophène »,
« Pentachlorophénol » et « Pipéronyl butoxyde ».

**Ce que ce document dit — et il le dit lui-même, annexe 1** :

> « En 2020, dans le cadre du renouvellement du marché public du contrôle sanitaire des eaux
> destinées à la consommation humaine, un groupe de travail de l'ARS Ile-de-France a conduit une
> étude pour définir une liste régionale de pesticides à rechercher dans le cadre du contrôle
> sanitaire. […] Ce travail a permis de cibler **145 pesticides** (contre 85 précédemment) à
> rechercher dans le cadre du contrôle sanitaire. **A ces 145 pesticides s'ajoute l'analyse
> d'autres pesticides ou métabolites de pesticides, dont la recherche n'engendre pas de surcoût
> dans le cadre du contrôle sanitaire.** »

**Ce que ce document ne dit pas** : il ne dit pas que le phosphate de tributyle est l'un des
145 pesticides ciblés plutôt qu'une des substances « dont la recherche n'engendre pas de surcoût »,
et il ne dit **nulle part** qu'une limite de 0,10 µg/L lui est appliquée. C'est une **liste de
recherche**, pas une **liste de jugement**. Elle documente un panier d'analyse, ce qui est la
réponse au §4 ci-dessous — pas un rattachement réglementaire.

### 3.5 Conclusion, et ce qu'elle produirait si elle était inverse

**La règle « pesticides (par substance individuelle), 0,10 µg/L » ne s'applique pas au phosphate de
tributyle.** Elle repose sur une définition de fonctions d'usage qu'aucune source lue ne rattache à
cette substance, le référentiel SANDRE ne le classe dans aucune liste phytosanitaire, et la base
PPDB ne le connaît pas.

**Ce que produirait la réponse inverse.** Le brief indique que « six ou sept des quinze
quantifications passeraient au-dessus de 0,10 µg/L » ; **je n'ai pas pu le vérifier**, la base
étant interdite d'ouverture — la valeur est relayée telle quelle, non vérifiée, et devra l'être
avant toute publication. Ce que je peux affirmer avec les seuls chiffres du brief :

- **maximum 0,27 µg/L, soit 2,7 fois la valeur de 0,10 µg/L** — un dépassement serait prononcé ;
- minimum quantifié 0,005 µg/L, soit 20 fois en dessous — celui-là ne le serait pas ;
- l'application de la règle ferait donc **apparaître des dépassements réglementaires là où aucun
  texte n'en prononce**. C'est un faux positif, et le §2.13 du `CLAUDE.md` projet en fait le coût
  le plus élevé possible pour l'observatoire.

**Avertissement de méthode, à conserver** : le brief signale que cette même règle sur-capture
quatre HAP (benzo(b)fluoranthène, benzo(k)fluoranthène, benzo(g,h,i)pérylène,
indéno(1,2,3-cd)pyrène) qui ne sont pas des pesticides. Le fait que le moteur **ne** capte **pas**
le phosphate de tributyle va ici dans le sens du texte — mais ce n'est **pas** ce qui fonde la
conclusion. La conclusion est fondée au §3.1 à §3.3, sur les textes et les référentiels. Le
comportement du moteur n'en est qu'une conséquence heureuse.

---

## 4. Pourquoi la substance est-elle mesurée ? (obligation du C2)

1 520 mesures, 226 communes, huit ans. Quatre appartenances documentées, du plus solide au moins
solide, avec leur registre exact.

1. **Polluant spécifique de l'état écologique (PSEE) des eaux de surface — registre DCE, établi.**
   Le phosphate de tributyle **figure à l'annexe II de l'arrêté du 17 octobre 2018** modifiant
   l'arrêté du 25 janvier 2010 relatif aux méthodes et critères d'évaluation de l'état écologique
   des eaux de surface (relevé sur le portail réglementaire de l'INERIS, qui reproduit l'annexe).
   Concordance indépendante : SANDRE le classe dans les groupes 127, **129 (Artois-Picardie)**,
   **132 (Rhône-Méditerranée)** et **133 (Corse)**. **La valeur de NQE associée n'a pas été lue en
   source primaire** — la version consolidée de l'arrêté sur Légifrance n'a pas restitué ses
   annexes techniques. `a_verifier`. **Registre : eaux de surface, pas EDCH.**
2. **Substance pertinente à surveiller dans les eaux de surface continentales** — groupe SANDRE
   **211**. Même registre DCE, même remarque.
3. **Inscription dans une liste régionale de « pesticides recherchés » du contrôle sanitaire
   EDCH — c'est la seule appartenance qui touche notre registre.** ARS Île-de-France, marché public
   renouvelé en 2020 (§3.4). Le document dit le mécanisme lui-même : une liste régionale, arrêtée
   par un marché pluriannuel, à laquelle **s'ajoutent des substances dont la recherche n'engendre
   pas de surcoût**. C'est la réponse « balayage chromatographique rendu pour les composés
   réglementés » : le phosphate de tributyle est un ester organophosphoré, il sort du même passage
   analytique que les insecticides organophosphorés qui, eux, sont réglementés. **Portée limitée à
   dire** : ce document concerne l'Île-de-France, et le corpus du projet porte sur d'autres
   départements. Il **documente un mécanisme**, il n'établit pas la cause pour nos 226 communes.
4. **Cohérence avec le mécanisme déjà établi par le projet** — listes régionales figées par les
   marchés pluriannuels des ARS, décrit par l'instruction DGS/EA4/2020/177 [REG-05]. **Aucune
   causalité n'est affirmée** : l'instruction est du 18 décembre 2020 et le corpus commence le
   08/01/2016. C'est la précaution du §2.11 du `CLAUDE.md` projet, appliquée telle quelle.

**Ce que je ne dis pas** : qu'un texte rende la recherche du phosphate de tributyle obligatoire au
contrôle sanitaire national. Je n'en ai trouvé aucun.

---

## 5. Les six sommes réglementées — une par une

| Somme | Périmètre acquis par le projet | Le phosphate de tributyle y entre-t-il ? |
|---|---|---|
| **Trihalométhanes** (total THM) | **4** substances nommées : chloroforme, bromoforme, dibromochlorométhane, bromodichlorométhane | **Non.** Périmètre nominatif fermé. La substance ne porte ni halogène ni structure méthane |
| **HAP**, 0,10 µg/L | **4** substances nommées | **Non.** Nominatif et fermé. Le phosphate de tributyle n'est pas un hydrocarbure : c'est un **ester de l'acide phosphorique**, il porte un atome de phosphore et quatre oxygènes |
| **Acides haloacétiques**, 60 µg/L au 01/01/2023 | **5** substances nommées (SANDRE 9064 → `[1465] [1481] [1546] [5427] [5426]`) | **Non.** Nominatif et fermé ; le code 1847 n'est pas dans la fiche de la somme |
| **PFAS**, somme des 20 | **20** substances énumérées à l'annexe III B.3 de la directive et reprises à l'annexe I de l'arrêté du 30/12/2022 (liste relue intégralement, lignes 174 à 193 de l'extraction REG-03) | **Non.** Nominatif et fermé ; la molécule ne porte **aucun atome de fluor** |
| **Tétrachloroéthylène + trichloroéthylène**, 10 µg/L | **2** substances nommées, deux éthylènes chlorés | **Non.** Nominatif et fermé |
| **Total pesticides**, 0,50 µg/L (SANDRE 6276) | « la somme de **tous les pesticides individuels quantifiés** » — périmètre **ouvert**, défini par la catégorie de la ligne précédente | **Non — et c'est la conséquence directe du §3.** Le périmètre du total est exactement celui de la ligne « pesticides (par substance individuelle) ». Le phosphate de tributyle n'étant pas un pesticide au sens de cette définition, il n'entre pas dans le total. Une quantification à 0,27 µg/L ne doit donc **pas** être ajoutée au total pesticides d'un bulletin |

**Le piège de l'agrégat de nomenclature, écarté explicitement.** Le phosphate de tributyle
appartient au groupe SANDRE **65 « Organophosphorés »**. Ce groupe **n'est pas une somme
réglementaire** : c'est une classe chimique de la nomenclature SANDRE, sans valeur dans aucun
texte. Le confondre avec un périmètre opposable serait l'erreur exacte de `[7485] « Somme de
COHV »` ou `[2925] xylènes méta+para`.

**Aucune autre somme opposable n'a été trouvée** dans les textes lus qui pourrait l'accueillir. Les
deux seules lignes-somme restantes de l'annexe I sont « Aldrine, dieldrine, heptachlore,
heptachlorépoxyde (par substance individuelle) », nominative et fermée à 0,03 µg/L, et « Total
microcystines ». Ni l'une ni l'autre.

**Trois cas d'école du projet, transposés ici pour mémoire** : le trichlorofluorométhane *est*
chimiquement un trihalométhane et n'entre pas dans le total des THM ; le trichloroéthane-1,1,1 est
un éthane, pas un éthylène ; les dichloroéthylènes-1,2 sont des produits de dégradation des deux
substances de leur somme et n'y entrent pas. **La ressemblance chimique ne fait jamais entrer dans
une somme. Le mot qui ferme un périmètre est dans le texte : « the following five substances »,
« these two parameters ».**

---

## 6. Balayage international — 15 juridictions

**Deux colonnes de nature à ne pas confondre** : une valeur **nominative** nomme le phosphate de
tributyle ; une valeur **de catégorie** s'appliquerait à lui par appartenance à un ensemble. Ce ne
sont pas deux valeurs de même espèce et elles ne s'alignent pas.

| Juridiction | Valeur applicable au TBP | Unité | Nature | Nominative / catégorie | Texte consulté | Statut de consultation |
|---|---|---|---|---|---|---|
| **Union européenne** | aucune | — | — | — | Directive (UE) 2020/2184, annexes I A/B/C et III | **lue en entier** — substance absente |
| **France** | aucune | — | — | — | Arrêté 11/01/2007 d'origine ; arrêté 30/12/2022 ; annexe I consolidée (Légifrance `LEGIARTI000046890189`) | **lues** — substance absente des trois |
| **Allemagne** | aucune ; *(10 µg/L cité par ETOX pour les eaux **prélevées** — **écartée**, §2.5)* | — | — | — | TrinkwV 2023, **Anlage 2** (Teil I et II) | **lue** — Tributylphosphat absent. **Anlage 3** (paramètres indicateurs) **non lue** |
| **Danemark** | non établi | — | — | — | BEK nr 1023 af 29/06/2023 om vandkvalitet | **inaccessible** — `retsinformation.dk` répond HTTP 403 |
| **Suède** | non établi | — | — | — | LIVSFS/SLVFS dricksvatten | **non consultée en source primaire** — aucune trace trouvée par recherche |
| **Pays-Bas** | **1,0** *(signalement)* ; **350** *(guide indicatif)* | µg/L | **paramètre de signalement** inscrit au Drinkwaterbesluit (déclenche une investigation, **pas une non-conformité**) ; et **valeur guide** RIVM non contraignante | **de catégorie** (« overige antropogene stoffen ») pour 1,0 ; nominative pour 350 | Drinkwaterbesluit bijlage A, via fiche RIVM 126-73-8 | **lue partiellement** — fiche RIVM lue, **Drinkwaterbesluit lui-même non lu** (bijlage A non restituée) → `a_verifier` |
| **Suisse** | non établi | — | — | — | Ordonnance du DFI sur l'eau potable (RS 817.022.11) | **inaccessible** — Fedlex est servi en JavaScript |
| **Royaume-Uni** | non établi | — | — | — | Water Supply (Water Quality) Regulations | **non consultée en source primaire** |
| **Norvège** | non établi | — | — | — | Drikkevannsforskriften | **non consultée en source primaire** |
| **États-Unis (fédéral)** | aucune | — | — | — | **40 CFR 141.61**, contaminants organiques de synthèse (33 substances nommées, liste relue) | **lue** — TBP absent |
| **Californie** | aucune parmi les *notification levels* nommés | — | — | — | State Water Board, *Drinking Water Notification Levels* (32 substances + 24 archivées) | **lue partiellement** — la page ne restitue pas les 32 noms ; TBP absent des substances énumérées → `a_verifier` sur l'exhaustivité |
| **Canada** | non établi ; **évaluation CEPA existante sans ligne directrice eau potable** | — | — | — | *Guidelines for Canadian Drinking Water Quality — Summary Table* | **inaccessible** — `canada.ca` répond HTTP 403. Une *Screening Assessment for Phosphoric Acid Tributyl Ester* (Santé Canada / ECCC, 2009) existe et est citée par le Minnesota DH, **non lue** |
| **Australie / Nouvelle-Zélande** | aucune | — | — | — | *Australian Drinking Water Guidelines* 4.0, index complet des fiches (Part 5) | **lue (index)** — aucune fiche pour le phosphate de tributyle ni pour les esters organophosphorés retardateurs de flamme |
| **Japon** | aucune | — | — | — | MOE/MHLW — 水質基準項目 (52 items), 水質管理目標設定項目 (26), 要検討項目 (46) | **lue** — TBP absent des trois listes |
| **OMS** | aucune | — | — | — | *Guidelines for drinking-water quality*, 4ᵉ éd. + 1er et 2e additifs (texte intégral + **table A3.2**) ; **EHC 112 (IPCS, 1991)** | **lues** — absent des *Guidelines* y compris de la table A3.2 ; EHC 112 évalue la substance mais **ne propose ni valeur guide ni TDI** |

### 6.1 Ce que ce balayage autorise à écrire — et ce qu'il interdit

- **Formulation autorisée** : « **aucune valeur opposable nommant le phosphate de tributyle dans
  l'eau destinée à la consommation humaine n'a été identifiée parmi les juridictions suivantes** :
  UE, France, Allemagne, Pays-Bas, États-Unis fédéral, Californie, Australie/Nouvelle-Zélande,
  Japon, OMS » — les neuf effectivement lues.
- **Formulation interdite** : « aucun pays au monde n'a de valeur ». Cinq juridictions de la liste
  standard (Danemark, Suède, Suisse, Royaume-Uni, Norvège) **n'ont pas pu être consultées en source
  primaire**, et le Canada est resté inaccessible. Sans elles, l'énoncé n'a pas de portée.
- **La valeur la plus basse identifiée applicable à cette substance est 1,0 µg/L (Pays-Bas)** —
  mais c'est un **paramètre de signalement de catégorie**, pas une limite de conformité, et il n'a
  pas été lu dans le Drinkwaterbesluit. **Elle ne peut pas servir de `seuil_strict`.** La confondre
  avec une limite reproduirait exactement l'erreur du *Public Health Goal* californien pour le
  plomb (0,2 µg/L confondu avec une limite alors que la Californie applique un niveau d'action à
  15 µg/L).

### 6.2 Bloc « recommandé, sourcé, non repris »

- Minnesota Department of Health, mars 2025 : **nHBV = 4 µg/L** pour l'eau de boisson (court terme,
  subchronique et chronique confondus). Valeur d'orientation d'un État américain, sans effet
  juridique en France, **hors des 15 juridictions de la liste standard**. Elle est la seule valeur
  sanitaire lue en source primaire qui porte spécifiquement sur l'eau de boisson et sur le CAS
  126-73-8. Classification cancérogène associée, citée verbatim : « Cancer classification: Likely
  to be Carcinogenic to Humans (EPA 2005) », sites tumoraux vessie et foie ; le Minnesota conclut à
  un cancérogène **non linéaire** et ne dérive pas de valeur cancer (`cHBV = Not Applicable`).
- INERIS, 2013 : **QSdw_hh = 105 µg/L**, calcul indicatif s'appliquant à l'eau brute du milieu.
- RIVM : **350 µg/L**, valeur guide indicative.

---

## 7. Ligne de référentiel — recommandation

### 7.1 Recommandation : **NE PAS verser de ligne portant un seuil**

Trois versements possibles, trois effets chiffrés :

| Ligne envisagée | Effet sur les 1 520 mesures | Verdict |
|---|---|---|
| `seuil_2026 = 0.10` au titre des pesticides | fabrique des **dépassements réglementaires** sur les quantifications au-dessus de 0,10 µg/L (le brief en annonce six ou sept, non vérifié) — alors qu'aucun texte ne les prononce | **à refuser.** Faux positif, le coût le plus élevé pour le projet |
| `seuil_2026 = 4` (Minnesota) ou `105` (INERIS) | maximum du corpus 0,27 µg/L : **les 1 520 mesures deviendraient « conformes »** contre une valeur qui n'est opposable nulle part et qui, pour l'INERIS, vise l'eau brute | **à refuser.** C'est l'erreur du biphényle (1 374 indéterminés transformés en conformes) et celle du fluoranthène (valeur portant sur un autre milieu) |
| `seuil_strict = 1.0` (signalement néerlandais) | fabriquerait une hiérarchie internationale à partir d'un paramètre de signalement de catégorie, non lu en source primaire | **à refuser.** §6.1 |

**L'état actuel — `grille_applicable = 'aucune'`, aucun seuil, mesures en indéterminé — est le
verdict juste.** Une substance sans seuil n'est pas sans danger : elle est indéterminée, et c'est
exactement ce que la base dit aujourd'hui.

### 7.2 Si une ligne documentaire est malgré tout souhaitée

Une ligne **sans aucun seuil**, de statut `vigilance`, qui ne produit aucun verdict mais rend la
substance et son absence de norme visibles et sourcées. Forme exacte : séparateur `;`, sources
séparées par la **barre verticale**, **aucun point-virgule dans une cellule**. Ordre des colonnes
repris de l'en-tête de `referentiel/referentiel_seuils.csv`.

```
code_parametre;code_cas;libelle;famille;unite;seuil_2016;seuil_2026;date_applicabilite_2026;seuil_conditionnel;condition_seuil;statut_2026;seuil_futur;date_applicabilite_futur;seuil_strict;base_seuil_strict;pe_reglementaire;pe_scientifique;sources;fiabilite;est_agregat;cancerogenicite_circ
1847;126-73-8;Phosphate de tributyle;Ester organophosphore - usage industriel;µg/L;;;;;Aucune valeur reglementaire EDCH ne nomme cette substance. La regle pesticides par substance individuelle ne s applique pas - la definition de l annexe I enumere neuf fonctions d usage phytopharmaceutiques et le TBP est un solvant d extraction et retardateur de flamme. SANDRE ne le classe dans aucune liste phytosanitaire (groupes 65 127 129 132 133 211). Absent de la base PPDB. Valeurs sanitaires non opposables identifiees - 4 ug/L Minnesota Dept of Health mars 2025 et 105 ug/L calcul indicatif INERIS 2013 pour l eau brute. Mesures a laisser en indetermine.;vigilance;;;;;non;non evalue;REG-01|REG-03|REG-04|INERIS-TBP|MDH-TBP|SAN-1847;verifie;non;
```

Points de forme à ne pas modifier sans y revenir :

- **`seuil_2016`, `seuil_2026`, `seuil_strict` volontairement vides.** C'est le cœur de la
  recommandation : la ligne documente, elle ne juge pas. **Aucune bascule ne peut naître de cette
  ligne**, ce qui est le résultat correct.
- **`fiabilite = verifie`** porte ici sur **l'absence**, qui est établie sur quatre textes lus
  (§2.1), et non sur une valeur. Si cela devait prêter à confusion dans les sorties, mettre
  `a_verifier` — le contenu de la ligne ne change pas.
- **`pe_reglementaire = non`**, sourcé : INERIS, fiche DRC-10-102867-00045B p. 3, « Le phosphate de
  tributyle **n'est pas cité dans la stratégie communautaire concernant les perturbateurs
  endocriniens** (E.C., 2004) ni dans le rapport d'étude de la DG ENV sur la mise à jour de la
  liste prioritaire des perturbateurs endocriniens à faible tonnage (Petersen et al., 2007). »
  Cohérent avec le §2.6 du projet : le seul PE avéré au sens réglementaire UE dans l'EDCH reste le
  bisphénol A. **`pe_scientifique = non evalue`** : les listes PE-01 à PE-08 du fonds local
  **n'ont pas été ouvertes** faute de temps (§9) — ne pas écrire « non ».
- **`cancerogenicite_circ` laissé vide** : le CIRC n'a pas été consulté (pages servies en
  JavaScript). **Ne pas y reporter le « Likely to be Carcinogenic to Humans » de l'US EPA ni le
  « Carc. 2 / H351 » du règlement CLP** — trois classifications, trois registres, aucun ne se
  déduit des autres (§2.15 du projet).
- **`INERIS-TBP`, `MDH-TBP`, `SAN-1847`** sont des codes de source **à créer** dans
  `docs/INDEX_SOURCES.md` s'ils sont retenus ; ils n'existent pas aujourd'hui.

---

## 8. Table des sources

| Organisme | Titre exact | Date | URL ou chemin local | Lecture |
|---|---|---|---|---|
| Parlement européen et Conseil | *Directive (UE) 2020/2184 relative à la qualité des eaux destinées à la consommation humaine* — texte intégral, annexes comprises | 16/12/2020 (JO L 435 du 23/12/2020) | `Sources\REG_Reglementation_et_seuils\REG-01_UE_directive-2020-2184.pdf` | **lue en entier** (3 005 lignes extraites ; annexe I A/B/C et annexe III présentes ; définition « Pesticides » citée verbatim, lignes 2007-2061) |
| République française | *Arrêté du 30 décembre 2022 modifiant l'arrêté du 11 janvier 2007…* (grille 2026) | 30/12/2022, JO du 31/12/2022 | `Sources\REG_Reglementation_et_seuils\REG-03_FR_arrete-2022-12-30_grille-2026.pdf` | **lue** (523 lignes ; annexes I et II relues ; définition « pesticides », liste des 20 PFAS et ligne « Total pesticides » citées) |
| République française | *Arrêté du 11 janvier 2007…* — **rédaction d'origine** | 11/01/2007 | `Sources\REG_Reglementation_et_seuils\REG-02_FR_arrete-2007-01-11_grille-2016.pdf` | **lue** (16 741 lignes extraites ; recherche `tributyl`, `126-73-8`, `phosphate de tri` : aucune occurrence) |
| Légifrance | Même arrêté, **version consolidée**, annexe I (`LEGIARTI000046890189`) | en vigueur au 01/01/2023 | https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000046890189 | **lue** — substance absente ; inventaire complet des paramètres organiques nommés obtenu |
| OMS | *Guidelines for drinking-water quality*, 4ᵉ éd. incorporant les 1er et 2e additifs | 4ᵉ éd. (millésime exact `a_verifier`) | `Sources\REG_Reglementation_et_seuils\REG-04_OMS_directives-qualite-eau-4e-ed.pdf` | **lue en entier** (33 631 lignes ; recherche `tributyl`, `126-73-8`, `butyl phosphate`, `phosphate` ; **table A3.2 relue**). Résultat : substance totalement absente ; les 4 occurrences de `tributyl` portent sur le **tributylétain** |
| OMS / IPCS | *Environmental Health Criteria 112 — Tributyl phosphate* | 1991 | https://www.inchem.org/documents/ehc/ehc/ehc112.htm | **lue** — **aucune valeur guide, aucune TDI/ADI, aucune valeur recommandée pour l'eau de boisson** |
| INERIS | *Valeur guide environnementale — Phosphate de tributyle, n° CAS 126-73-8*, **DRC-10-102867-00045B** | validation experts nov. 2012, **version 3 du 27/03/2013** | https://substances.ineris.fr/sites/default/files/archives/126-73-8%20--%20Phosphate%20de%20tributyle%20--%20NQE.pdf | **lue** (PDF converti localement ; §2.4 et §2.5 cités verbatim ; VGE, NQE, QSdw_hh, VTR relevés) |
| INERIS | *Portail Substances Chimiques — Phosphate de tributyle (126-73-8)* | consulté le 11/08/2026 | https://substances.ineris.fr/substance/126-73-8 | **lue** — VGE 37 / 8 µg/L, VTR orale chronique 30 µg/kg pc/j, CLP Carc. 2 H351, appartenance aux arrêtés PSEE, **aucune norme eau de boisson** |
| INERIS (portail réglementaire) | *Arrêté du 17 octobre 2018 — Annexe II : polluants spécifiques de l'état écologique* | 17/10/2018 | https://substances.ineris.fr/reglementation/arrete-du-17-octobre-2018-annexe-ii-polluants-specifiques-de-letat-ecologique | **lue** — le phosphate de tributyle **y figure** ; **la valeur de NQE n'a pas été restituée** → `a_verifier` |
| SANDRE / Eaufrance | *Phosphate de tributyle — Paramètre chimique*, fiche du paramètre **1847** | créée le 07/12/1999, mise à jour le **29/01/2025** | http://mdm.sandre.eaufrance.fr/id/parametre/1847/html | **lue** — CAS 126-73-8, classe chimique 65 « Organophosphorés », groupes 65/127/129/132/133/211, **aucun groupe phytosanitaire**, synonymes TBP |
| ARS Île-de-France (bilan publié par Eau de Paris) | *Contrôle sanitaire des Eaux Destinées à la Consommation Humaine — bilan 2021*, annexes 1 et 2 | 2021 | https://www.eaudeparis.fr/sites/default/files/import/ARS/BILAN_ARS_2021.pdf | **lue** (PDF converti localement) — « Phosphate de tributyle » figure à l'annexe 2 « Liste des pesticides recherchés » ; annexe 1 citée verbatim au §3.4 |
| Minnesota Department of Health, Health Risk Assessment Unit | *Toxicological Summary for: Tributyl phosphate* | publication web **mars 2025** | https://www.health.state.mn.us/communities/environment/risk/docs/guidance/gw/tbp.pdf | **lue en entier** (PDF converti localement) — nHBV 4 µg/L, RfD 0,0059 mg/kg/j, classification cancer EPA 2005 |
| Bundesministerium (Allemagne) | *Trinkwasserverordnung 2023*, **Anlage 2** (Teil I et II) | version en vigueur | https://www.gesetze-im-internet.de/trinkwv_2023/anlage_2.html | **lue** — 34 paramètres chimiques nommés relevés ; **Tributylphosphat absent**. Anlage 3 **non lue** |
| US EPA / eCFR | **40 CFR 141.61**, *Maximum contaminant levels for organic contaminants* | version courante | https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-40?chapter=I&subchapter=D&part=141&section=141.61 | **lue** — 33 contaminants organiques de synthèse nommés ; **TBP absent** |
| California State Water Resources Control Board | *Drinking Water Notification Levels* | consultée le 11/08/2026 | https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/NotificationLevels.html | **lue partiellement** — 32 substances annoncées, la page n'en énumère qu'une partie ; TBP absent de celles nommées |
| Ministère de l'Environnement (Japon) | 水質基準項目と基準値 (52 items) + 水質管理目標設定項目 (26) + 要検討項目 (46) | en vigueur | https://www.env.go.jp/water/water_supply/kijun/kijunchi.html | **lue** — TBP absent des trois listes |
| NHMRC (Australie) | *Australian Drinking Water Guidelines* 4.0, index complet des fiches | version courante | https://guidelines.nhmrc.gov.au/australian-drinking-water-guidelines/sitemap.md | **lue (index)** — aucune fiche pour le phosphate de tributyle ni pour les esters organophosphorés |
| RIVM (Pays-Bas) | *Risico's van stoffen — tributylfosfaat*, fiche 1265 | consultée le 11/08/2026 | https://rvszoeksysteem.rivm.nl/stof/detail/1265 | **lue** — signaleringsparameter 1,0 µg/L (« overige antropogene stoffen »), richtwaarde indicative 350 µg/L |
| Univ. of Hertfordshire / AERU | *Pesticide Properties DataBase (PPDB)* — index A-Z | consulté le 11/08/2026 | https://sitem.herts.ac.uk/aeru/ppdb/en/atoz.htm | **lu** — **le phosphate de tributyle n'y figure pas** |
| ECHA | *Tributyl phosphate — Substance Information* (100.004.365) | — | https://echa.europa.eu/substance-information/-/substanceinfo/100.004.365 | **NON LUE** — HTTP 403 |
| Santé Canada | *Guidelines for Canadian Drinking Water Quality — Summary Table* | — | canada.ca | **NON LUE** — HTTP 403 |
| Santé Canada / ECCC | *Screening Assessment for the Challenge — Phosphoric Acid Tributyl Ester (Tributyl Phosphate)* | 2009 | canada.ca | **NON LUE** — connue seulement par la bibliographie du Minnesota DH |
| Miljøministeriet (Danemark) | *BEK nr 1023 af 29/06/2023 om vandkvalitet og tilsyn med vandforsyningsanlæg* | 29/06/2023 | https://www.retsinformation.dk/eli/lta/2023/1023/pdf | **NON LUE** — HTTP 403 |
| Confédération suisse | *Ordonnance du DFI sur l'eau potable…* (RS 817.022.11) | — | fedlex.admin.ch | **NON LUE** — site servi en JavaScript |
| République française | *Arrêté du 25 janvier 2010*, version consolidée (Légifrance) | consolidé au 17/02/2026 | https://www.legifrance.gouv.fr/loda/id/JORFTEXT000021865356/2026-02-17 | **lue partiellement** — les annexes techniques portant les NQE **n'ont pas été restituées** |

---

## 9. Ce que je n'ai pas pu établir

1. **Tout ce qui aurait demandé la base de données.** Consigne respectée : `data/eau.duckdb` n'a
   jamais été ouverte. En conséquence, **je n'ai vérifié aucun des chiffres du corpus** — 1 520
   mesures, 226 communes, 15 quantifications, 0,27 µg/L de maximum, 0,005 µg/L de minimum quantifié,
   bornes 08/01/2016 et 04/11/2024 : tous sont repris du brief tels quels.
2. **Les quinze valeurs quantifiées ne sont pas connues.** L'affirmation du brief selon laquelle
   « six ou sept des quinze quantifications passeraient au-dessus de 0,10 µg/L » **n'a pas été
   vérifiée**, et ne doit pas être publiée avant de l'être. La seule chose que j'établis est que le
   maximum annoncé (0,27 µg/L) dépasse 0,10 d'un facteur 2,7.
3. **Le champ `limite_qualite_parametre` de SISE-Eaux n'a pas été consulté.** C'est lui qui, sur le
   biphényle, avait révélé qu'une ARS déclarait effectivement une limite de 0,10 µg/L à partir d'une
   date précise. **Si ce champ était renseigné sur des mesures de phosphate de tributyle, cela
   contredirait en pratique la conclusion du §3** — sans la contredire en droit. **C'est la
   première vérification à faire quand la base sera libre.**
4. **La valeur de NQE du phosphate de tributyle à l'annexe II de l'arrêté du 17 octobre 2018 n'a pas
   été lue.** L'appartenance à l'annexe est établie, la valeur ne l'est pas. Sans effet sur un
   verdict EDCH, mais nécessaire si le projet documente un jour le registre DCE.
5. **Six juridictions de la liste standard n'ont pas été atteintes** : Danemark et Canada (HTTP 403),
   Suisse (JavaScript), Suède, Royaume-Uni et Norvège (aucune source primaire trouvée). L'énoncé
   « aucune valeur opposable identifiée » est donc borné aux neuf juridictions lues (§6.1).
6. **Le statut d'approbation du phosphate de tributyle au titre des règlements (CE) 1107/2009 et
   (UE) 528/2012 n'a pas été lu dans une base officielle** — la base européenne des pesticides est
   un formulaire non atteignable, la fiche ECHA répond 403. La conclusion du §3.2 repose sur
   l'absence de la substance dans la PPDB et sur le silence de l'INERIS, deux sources concordantes
   mais indirectes. **C'est le seul point du raisonnement C-g qui reste `a_verifier`** ; il ne le
   renverse pas, puisque la définition d'usage (§3.1) et le classement SANDRE (§3.3) suffisent, mais
   il l'affaiblirait si une approbation existait.
7. **Le fonds local PE-01 à PE-09 n'a pas été ouvert.** Plusieurs esters organophosphorés figurent
   sur des listes de suspicion de perturbation endocrinienne (registre **scientifique**) ; je ne
   sais pas si le phosphate de tributyle y est. Ce qui est établi, et cité, c'est qu'il n'est **pas**
   dans la stratégie communautaire PE ni dans la liste prioritaire DG ENV — registre
   **réglementaire**. D'où `pe_scientifique = non evalue`, jamais « non ». À noter, du Minnesota DH :
   « A database uncertainty factor of 3 has been applied, in part, to account for the lack of
   adequate endocrine toxicity studies » — l'absence d'étude n'est pas une absence d'effet.
8. **Le classement CIRC n'a pas été établi** (pages servies en JavaScript). Champ laissé vide.
   Ne pas y reporter la classification CLP européenne (Carc. 2, H351) ni celle de l'US EPA
   (« Likely to be Carcinogenic to Humans », 2005) : trois registres distincts.
9. **La cause de la présence du paramètre dans le panier d'analyse de nos 226 communes n'est pas
   établie.** Le mécanisme est documenté (§4), mais sur le corpus francilien, pas sur le nôtre.
   Vérification possible sans la base : retrouver les listes régionales de pesticides des ARS des
   départements du corpus.
10. **L'Anlage 3 de la TrinkwV allemande et le Drinkwaterbesluit néerlandais (bijlage A) n'ont pas
    été lus.** Pour les Pays-Bas, cela laisse la valeur de signalement de 1,0 µg/L en `a_verifier`,
    alors que c'est la plus basse valeur identifiée applicable à cette substance.

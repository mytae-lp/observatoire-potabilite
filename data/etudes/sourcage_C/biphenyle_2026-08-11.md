# Sourçage réglementaire — Biphényle (SANDRE 1584, CAS 92-52-4)

Date du sourçage : 2026-08-11
Substance : biphényle (synonymes : diphényle, phénylbenzène, 1,1'-biphényle), CAS **92-52-4**,
formule C12H10, unité de mesure dans le corpus : µg/L.
Corpus annoncé au brief : 1 373 mesures, 240 communes (Tarn + Eure-et-Loir), 12 quantifications,
maximum 0,016 µg/L. **Corpus relu dans `data/eau.duckdb` le 11/08/2026 : 1 414 mesures,
13 quantifications, maximum 0,016 µg/L** — écart signalé au §7.

## Avertissement d'identité — vérifié avant toute lecture

Le **biphényle (CAS 92-52-4)** n'est ni un **polychlorobiphényle (PCB)** — famille de congénères
chlorés à CAS distincts, présente séparément dans le corpus sous dix-sept libellés individuels et
un libellé « Polychlorobiphéniles indicateurs » (code 7431, 454 mesures, 0 quantification) — ni le
**bisphénol A (CAS 80-05-7)**, qui porte lui une limite de qualité EDCH de 2,5 µg/L.
Aucune valeur trouvée pour ces deux familles n'a été retenue ici. Toutes les sources retenues
ci-dessous portent le CAS 92-52-4 explicitement, à l'exception des textes réglementaires qui ne
nomment pas la substance — et c'est précisément l'objet du verdict.

---

## 1. Verdict

**C1 conditionnel et daté — une valeur opposable existe et s'applique au biphényle, non pas
nommément mais par la définition générique des pesticides : « Pesticides (par substance
individuelle) — 0,10 µg/L », l'arrêté définissant les pesticides comme incluant « les fongicides
organiques ». L'administration elle-même applique cette limite au biphényle dans le corpus, à
partir du 31 mars 2026 et pas avant.**

Ce verdict n'est pas un C2 : ce serait affirmer qu'aucune valeur ne juge la substance, alors
qu'une ARS en déclare une, opposable, sur 40 mesures du corpus. Ce n'est pas non plus un C1
franc : **le biphényle n'est nommé dans aucun texte EDCH**, et son rattachement à la catégorie
« pesticides » est, au sens du référentiel SANDRE, une décision de gestionnaire et non un fait de
texte (§4). D'où la formulation retenue : la condition n'est ni le procédé ni la ressource, c'est
**le statut de la substance** — le cinquième cas du §2.13 du `CLAUDE.md` projet.

Aucune valeur guide OMS n'existe : le biphényle est **absent de l'intégralité** des *Guidelines
for drinking-water quality* 4e édition, y compris de la table A3.2 des substances pour lesquelles
l'OMS a renoncé à établir une valeur guide. L'OMS ne l'a donc pas écarté — elle ne l'a pas traité.

Conséquence pratique, à dire d'emblée : **aucun dépassement n'est en jeu.** Maximum du corpus
0,016 µg/L contre une limite de 0,10 µg/L, soit un facteur 6 en dessous ; LQ des laboratoires
0,005 à 0,025 µg/L, donc toujours inférieure à la limite — pas d'indéterminé par LQ non plus.
Le verdict change la **couverture** du bulletin, pas sa conclusion.

---

## 2. Valeurs

### 2.1 Ce qui existe

| Valeur | Unité | Nature | Registre | Texte source | Date du texte | Date d'applicabilité | Fiabilité |
|---|---|---|---|---|---|---|---|
| **0,10** | **µg/L** | **limite de qualité, par substance individuelle** | réglementaire **opposable** (France) | Arrêté du 11 janvier 2007, annexe I, ligne « Pesticides (par substance individuelle) », dans la rédaction de l'arrêté du 30 décembre 2022 | 30/12/2022 (JO du 31/12/2022) | **01/01/2023** | **verifie** pour la valeur et sa définition ; **a_verifier** pour son application au biphényle (§2.3) |
| **0,10** | **µg/L** | idem, texte-mère UE | réglementaire opposable (UE) | Directive (UE) 2020/2184, annexe I partie B, ligne « Pesticides » : « The parametric value of 0,10 μg/l shall apply to each individual pesticide. » | 16/12/2020 | 12/01/2023 (transposition) | **verifie** (lu dans le PDF local, annexe incluse) |
| **0,10** | **µg/L** | idem, grille 2016 du projet | réglementaire opposable (France) | Arrêté du 11 janvier 2007, **rédaction d'origine**, annexe I : « Pesticides (par substance individuelle) 0,10 µg/L » | 11/01/2007 | 11/01/2007 | **verifie** (lu dans le PDF local REG-02, ligne 3569 de l'extraction) |
| **0,50** | **µg/L** | limite de qualité de **somme** | réglementaire opposable (France) | Arrêté du 11 janvier 2007, annexe I, ligne « Total pesticides » : « Par total pesticides, on entend la somme de tous les pesticides individuels quantifiés » | 30/12/2022 | 01/01/2023 | **verifie** pour la valeur et le périmètre ; l'entrée du biphényle dans ce périmètre suit exactement la même condition qu'au §2.3 |

**La valeur de 0,10 µg/L est identique en 2016 et en 2026.** Aucune bascule ne peut donc naître de
cette ligne, quel que soit le choix fait au §5. C'est déjà la justification portée par la règle
`pesticide_individuel_0_1` de `referentiel/regles_famille.csv`.

### 2.2 Définition qui porte le rattachement — citation exacte

Arrêté du 30 décembre 2022, annexe I, note de la ligne « Pesticides (par substance individuelle) » :

> « Par pesticides, on entend :
> – les insecticides organiques ;
> – les herbicides organiques ;
> – **les fongicides organiques** ;
> – les nématocides organiques ;
> – les acaricides organiques ;
> – les algicides organiques ;
> – les rodenticides organiques ;
> – les produits antimoisissures organiques ;
> – les produits apparentés (notamment les régulateurs de croissance)
> et leurs métabolites, tels que définis à l'article 3, point 32), du règlement (CE) no 1107/2009
> du Parlement européen et du Conseil, qui sont considérés comme pertinents pour les eaux
> destinées à la consommation humaine. »

Deux lectures à ne pas confondre : la réserve « **qui sont considérés comme pertinents** » se
rattache grammaticalement aux **métabolites** — la phrase suivante de l'annexe ne définit la
pertinence que pour eux (« Un métabolite de pesticide est jugé pertinent… »). Une substance mère
qui est un fongicide organique relève donc de la ligne sans condition de pertinence. Le point de
droit qui reste ouvert n'est pas là : il est de savoir si le biphényle **est** un fongicide
organique au sens de cette annexe (§2.3).

### 2.3 Ce qui rattache — et ce qui retient — le biphényle à cette ligne

Le biphényle n'est nommé nulle part. Quatre éléments plaident pour le rattachement, deux contre.
Ils sont donnés bruts, avec leur source.

**Pour :**

1. **L'administration l'applique.** Dans le corpus, 40 mesures de biphényle portent le champ
   `limite_qualite_parametre` renseigné par SISE-Eaux à la valeur **`<=0,1 µg/L`**. Toutes en
   Eure-et-Loir, **du 31 mars 2026 au 29 mai 2026**, soit la totalité des mesures de biphényle
   postérieures à cette date. C'est la limite « pesticide individuel » et rien d'autre.
2. **SANDRE classe le biphényle parmi les fongicides.** Fiche paramètre 1584 : appartenance aux
   groupes **97 « Fongicides »** (groupe parent 95 « Phytosanitaires ») et **204 « Liste B –
   Phytosanitaires »** (groupe parent 200), cette dernière ajoutée le **29 janvier 2025**.
3. **Le biphényle est documenté comme fongicide.** Base PPDB (Univ. of Hertfordshire, AERU) :
   *Substance type: Fungicide* ; usages agrumes, raisin, pommes de terre, concombres, tomates ;
   « impregnated into paper wraps for individual fruits ».
4. **Un usage phytosanitaire a existé et a été interdit** — donc la substance a bien été un
   produit de traitement, comme l'atrazine l'a été. INERIS 2018 : « L'utilisation du biphényle
   pour la formulation de produits phytosanitaires est **interdite en Europe** ». PPDB, statut
   règlement (CE) 1107/2009 : **Not approved**, inclusion **expired**. Une interdiction ne fait
   pas sortir une substance du champ de la ligne « pesticides » (l'atrazine, interdite depuis
   2004, y reste).

**Contre :**

5. **L'INERIS écrit l'inverse, explicitement.** Portail Substances Chimiques, fiche 92-52-4,
   section « Norme de qualité pour la santé humaine via l'eau de boisson (QSdw_hh) » :
   > « Pour le biphényle, aucune valeur n'est mentionnée dans la Directive 98/83/CE ou l'OMS. »

   L'INERIS ne considère donc pas la ligne générique « pesticides » comme couvrant cette
   substance, et calcule à la place une valeur seuil provisoire de son cru (§2.4).
6. **La « liste B » de SANDRE est, par construction, la liste du doute.** Note AQUAREF 2019 sur
   les listes phytopharmaceutiques SANDRE, citation exacte du critère de scission A/B :
   > « une pour laquelle il existe peu/pas de doute sur l'identification
   > phyto/biocide/métabolite (liste A) [;] une pour laquelle des usages différents (ou origines
   > différentes – ex : SPD) sont possibles et donc pour laquelle **la décision sur le caractère
   > pesticide ou pas doit être prise par le gestionnaire** (liste B). »

   Et la même note nomme les familles particulièrement travaillées pour bâtir ces listes B :
   > « les composés halogénés volatils, **les substances de type hydrocarbures**, les paramètres
   > possédant une valeur seuil différente de 0,1 µg/L dans la circulaire eau souterraine de
   > 2012, les sous-produits de désinfection, … »

   Le biphényle est un hydrocarbure aromatique — SANDRE le classe d'ailleurs en classe chimique
   **56 « Benzène et dérivés »**, et sa définition SANDRE est « Substance chimique de formule
   brute C12H10, de la famille des dérivés benzèniques ». Son usage dominant n'est pas
   phytosanitaire : INERIS 2018, « Usage 1 : Production de fluides caloporteurs, >35 % des
   usages ; Usage 2 : Intermédiaire dans l'industrie chimique, pharmaceutique et agrochimique,
   >25 % des usages ». L'usage conservateur d'agrumes représentait **5 % des ventes en 2015**
   selon le producteur DOW cité par INERIS.

**Ce que j'en conclus, et rien de plus** : la limite de 0,10 µg/L est réelle, opposable et
effectivement appliquée à cette substance par l'ARS d'Eure-et-Loir depuis le 31 mars 2026. Elle
n'est pas déductible du seul texte : elle suppose une décision de classement que le référentiel
SANDRE renvoie explicitement au gestionnaire, et sur laquelle l'INERIS a tranché en sens inverse
dans un autre cadre. Le projet doit donc porter cette valeur **avec sa condition et sa date**,
pas comme un seuil nu.

### 2.4 Valeurs guides non opposables — registre à ne jamais fusionner avec le précédent

| Valeur | Unité | Nature | Organisme | Source | Fiabilité |
|---|---|---|---|---|---|
| *(aucune)* | — | valeur guide eau de boisson | **OMS** | *Guidelines for drinking-water quality*, 4e éd. incorporant les 1er et 2e additifs — **le mot « biphenyl » n'apparaît nulle part dans le document**, ni dans les valeurs guides, ni dans la table A3.2 des renoncements explicites | **verifie** |
| **0,9** | µg/L (eau douce) | **valeur guide environnementale (VGE)** INERIS — protection des écosystèmes, **pas** eau de boisson | INERIS | Fiche DRC-18-158744-00413A, §1.5.2 : « Il n'y a pas de norme de qualité environnementale pour le Biphényle. L'INERIS a défini des valeurs guides environnementales (VGE)… Valeur guide eau : 0,9 µg/L en eau douce » | **verifie** (lu verbatim) |
| **0,34** | µg/L (eau marine) | idem | INERIS | idem | **verifie** |
| **463** | µg/kg de biote (eau douce) | idem | INERIS | idem | **verifie** |
| **38** | µg/kg p.c./j | **VTR orale** (dose journalière tolérable) | **OMS – IPCS, CICAD n° 6** | citée par la fiche INERIS PSC 92-52-4 | **a_verifier** — non lue en source primaire (document INCHEM non ouvert) |
| **0,5** | mg/kg/j | VTR orale | **US EPA** | citée par la fiche INERIS PSC (année indiquée 2013) | **a_verifier** — non lue en source primaire |
| **0,53** | µg/L | **valeur seuil provisoire calculée** pour l'eau de boisson, non opposable, non reprise par un texte | **INERIS** | fiche PSC 92-52-4, dérivée de la VTR CICAD 38 µg/kg/j avec facteur 5 pour effets CMR | **a_verifier — NE PAS VERSER.** Restitution obtenue par un outil de lecture résumante, non lue verbatim ; c'est exactement le cas d'espèce qui a conduit un agent du projet à écarter hier une valeur guide OMS non lue en primaire |

**Note d'unité** : 0,10 µg/L (limite) et 0,016 µg/L (maximum du corpus) sont dans la même unité,
aucune conversion n'est nécessaire. Les VTR sont en µg ou mg **par kg de poids corporel et par
jour** : ce ne sont pas des concentrations dans l'eau et elles ne se comparent à aucune mesure.
Les VGE INERIS sont bien en µg/L mais portent sur le **milieu aquatique**, pas sur l'eau du
robinet : ne jamais les rapprocher d'un bulletin d'EDCH.

### 2.5 Absences vérifiées, texte par texte

| Texte | Portée | Recherche effectuée | Résultat |
|---|---|---|---|
| Directive (UE) 2020/2184, **texte intégral, annexes comprises** (PDF local REG-01 ; extraction de 3 005 lignes ; annexe I parties A, B et C et annexe III présentes et relues à l'écran) | UE, EDCH | `biphenyl`, `92-52-4`, `diphenyl`, `phenylbenzene`, insensible à la casse | **aucune occurrence** — le biphényle n'est pas un paramètre nommé de l'annexe I |
| Arrêté du 30 décembre 2022, grille 2026 (PDF local REG-03, annexes extraites et relues) | France, EDCH | `biphén`, `92-52-4`, `diphényl` | **aucune occurrence** |
| Arrêté du 11 janvier 2007, rédaction d'origine (PDF local REG-02, 16 741 lignes, annexes I et II présentes) | France, EDCH + eaux brutes | idem | **aucune occurrence** |
| Arrêté du 11 janvier 2007, **version consolidée**, annexe I (Légifrance, `LEGIARTI000046890189`) | France, EDCH, norme en vigueur | lecture ciblée du mot « biphényle » / « diphényle » + inventaire complet des paramètres organiques nommés | **absent** ; les 21 paramètres organiques nommés aux limites de qualité sont : acides haloacétiques, acrylamide, benzène, benzo[a]pyrène, bisphénol A, bromates, chlorates, chlorites, chlorure de vinyle, cyanures totaux, 1,2-dichloroéthane, épichlorhydrine, HAP, mercure, total microcystines, somme des PFAS, pesticides (par substance individuelle), aldrine/dieldrine/heptachlore/heptachlorépoxyde, total pesticides, tétrachloroéthylène et trichloroéthylène, total THM |
| OMS, *Guidelines for drinking-water quality*, 4e éd. + 1er et 2e additifs (PDF local REG-04, texte intégral + annexe 3) | valeur guide non opposable | `biphenyl`, `92-52-4`, `diphenyl` | **aucune occurrence isolée**. Les 6 occurrences de `diphenyl` relèvent toutes d'autres substances : dichloro**diphényl**trichloroéthane (DDT) et **diphényl**étain. **Table A3.2** (« Chemicals for which guideline values have not been established ») relue : entrées en B = Bentazone, Beryllium, Bromide, Bromochloroacetate, Bromochloroacetonitrile, *Bacillus thuringiensis israelensis* — **pas de Biphenyl**. L'OMS n'a donc pas renoncé à une valeur guide pour cette substance : elle ne l'a jamais examinée dans ce cadre |
| INERIS, fiche technico-économique DRC-18-158744-00413A (26 p., lue) | inventaire des valeurs et normes françaises | section 1.5 « Valeurs et normes appliquées en France », section 1.6 « Autres textes » | **aucune mention d'une valeur EDCH** ; les seules valeurs françaises citées sont un seuil de déclaration de rejet (300 g/jour dans l'eau), les VGE, et une VME professionnelle |

---

## 3. Sommes réglementées — réponse une par une

| Somme | Périmètre acquis par le projet | Le biphényle y figure-t-il ? |
|---|---|---|
| **Trihalométhanes** | 4 substances : chloroforme, bromoforme, dibromochlorométhane, bromodichlorométhane | **Non.** Périmètre nominatif fermé, le biphényle n'y est pas nommé |
| **HAP** | 4 substances : benzo[b]fluoranthène, benzo[k]fluoranthène, benzo[ghi]pérylène, indéno[1,2,3-cd]pyrène | **Non.** Nominatif et fermé. Piège à écarter : le biphényle est un **hydrocarbure aromatique** (deux cycles benzéniques reliés) mais **pas polycyclique condensé** ; et de toute façon la ligne ne vaut que pour les quatre composés nommés. Aucune extension par famille |
| **Acides haloacétiques** | 5 substances : monochloro-, dichloro-, trichloro-, bromo-, dibromoacétique | **Non.** Nominatif et fermé |
| **PFAS** | 20 substances énumérées (annexe III B.3 de la directive) | **Non.** Nominatif et fermé ; le biphényle ne porte aucun atome de fluor |
| **Tétrachloroéthylène + trichloroéthylène** | 2 substances, toutes deux des éthylènes | **Non.** Nominatif et fermé ; le biphényle n'est pas un éthylène halogéné |
| **Pesticides (total), 0,50 µg/L** | « la somme de tous les pesticides individuels quantifiés » — périmètre **ouvert**, défini par une catégorie et non par une liste | **OUI, sous la même condition qu'au §2.3.** C'est la seule des six sommes dont le périmètre n'est pas nominatif. Dès lors que le biphényle est traité comme un pesticide individuel — ce que fait l'ARS d'Eure-et-Loir depuis le 31/03/2026 — une quantification de biphényle entre dans ce total. Le corpus contient **une** telle quantification sous ce régime : 0,005 µg/L le 05/05/2026 (commune 28331) |

**Aucune autre somme opposable n'a été trouvée** dans les textes lus qui pourrait accueillir le
biphényle. Les seules autres lignes-somme de l'annexe I sont « Aldrine, dieldrine, heptachlore,
heptachlorépoxyde (par substance individuelle) » — nominative, fermée, 0,03 µg/L — et « Total
microcystines », sans rapport.

À écarter explicitement, car ce sont d'autres registres que l'EDCH : l'« indice hydrocarbures »
et l'« indice phénol » figurent dans des textes de qualité des eaux brutes ou des rejets ; je
**n'ai pas** établi si le biphényle entre dans leur périmètre analytique — `a_verifier`, et sans
effet sur un verdict EDCH.

---

## 4. Pourquoi la substance est-elle mesurée ?

Aucune source lue ne rend le biphényle obligatoire au contrôle sanitaire national. Trois
appartenances documentées expliquent sa présence dans les paniers d'analyse, et une quatrième
est propre au corpus.

1. **Liste de vigilance « polluant spécifique de l'état écologique »** — INERIS 2018, §1.6.3,
   verbatim : « Le biphényle est un "polluant spécifique de l'état écologique des eaux de
   surface" pour le **bassin Seine-Normandie** et fait partie des substances pertinentes
   complémentaires pour la métropole à surveiller dans les eaux de surface et la matrice
   sédiment ». L'Eure-et-Loir relève du bassin Seine-Normandie, et c'est le département qui
   porte l'essentiel des mesures du corpus. **Attention au registre** : il s'agit de la
   surveillance DCE des **eaux de surface**, pas du contrôle sanitaire de l'EDCH. Le lien est
   une explication plausible de la présence du paramètre au catalogue des laboratoires, pas une
   obligation EDCH — je ne le donne pas comme tel.
2. **Liste des substances dangereuses pour les eaux souterraines** — INERIS 2018, §1.6.2,
   verbatim : « Le biphényle est cité dans la liste des substances dangereuses de l'**arrêté du
   17 juillet 2009** "relatif aux mesures de prévention ou de limitation des introductions de
   polluants dans les eaux souterraines" ». Registre : prévention des introductions dans la
   ressource, pas limite de potabilité. Cet arrêté **n'a pas été lu en source primaire** —
   `a_verifier`.
3. **Listes phytosanitaires SANDRE** — groupes 97 « Fongicides » et 204 « Liste B –
   Phytosanitaires ». L'appartenance au groupe 204 a été enregistrée le **29 janvier 2025**
   (fiche paramètre 1584, mention « ajout des groupes 204 et 211 »).
4. **Fait de corpus, daté** : le champ `limite_qualite_parametre` de SISE-Eaux est **vide sur les
   1 374 mesures antérieures au 31 mars 2026** (2016 → mars 2026, Tarn et Eure-et-Loir confondus)
   et vaut **`<=0,1 µg/L` sur les 40 mesures du 31 mars au 29 mai 2026**, sans aucune exception
   dans un sens ni dans l'autre. La bascule est nette et se lit à la journée.

**Ce que je ne dis pas** : que l'ajout SANDRE du 29/01/2025 a **causé** la déclaration de limite
du 31/03/2026. Les deux faits sont datés, cohérents et distants de quatorze mois ; je n'ai lu
aucun texte qui établisse le lien. C'est la même prudence que celle imposée au projet sur la
rupture de panel de janvier 2020 : un ordre chronologique compatible n'est pas une causalité.

---

## 5. Ligne de référentiel — à verser ou non, la décision reste à Yannick

### 5.1 État actuel dans la base — à corriger dans l'énoncé du brief

Le brief indique que le biphényle « ne s'apparie à aucune ligne du référentiel ». **C'est vrai
pour 1 374 mesures sur 1 414, et faux pour les 40 dernières.** Vérification faite le 11/08/2026 :

```
SELECT * FROM v_regle_famille_appliquee WHERE lower(libelle_parametre) LIKE '%biph%';
→ ('pesticide_individuel_0_1', 'Biphényle', '1584', 'µg/L', 0.1, 40, 1)
```

La règle de famille `pesticide_individuel_0_1` capte **déjà** les 40 mesures qui portent la
limite déclarée, et une seule quantification parmi elles. Le moteur du projet fait donc, sans le
savoir, exactement ce que fait l'ARS : il attache 0,10 µg/L là où l'administration l'a déclaré,
et nulle part ailleurs.

### 5.2 Recommandation

**Ne pas verser de ligne nominative, et documenter le cas.** Motif : une ligne nominative
sortirait automatiquement le biphényle du champ de la règle de famille (c'est l'ordre
d'application inscrit en tête de `regles_famille.csv`) et appliquerait `seuil_2026 = 0,10` aux
**1 414** mesures — dont 1 374 pour lesquelles l'administration n'a rien déclaré et pour
lesquelles le caractère pesticide de la substance est, de l'aveu même du référentiel SANDRE, une
décision de gestionnaire non prise. Ce serait transformer 1 374 indéterminés en 1 374
« conformes » : exactement ce que le §2.4 interdit. Le comportement actuel est plus juste que
celui qu'une ligne nominative produirait.

### 5.3 Si la ligne doit malgré tout être créée

Forme exacte, séparateur `;`, sources séparées par la barre verticale, aucun point-virgule dans
une cellule. Ordre des colonnes repris de l'en-tête de `referentiel/referentiel_seuils.csv`.

```
code_parametre;code_cas;libelle;famille;unite;seuil_2016;seuil_2026;date_applicabilite_2026;seuil_conditionnel;condition_seuil;statut_2026;seuil_futur;date_applicabilite_futur;seuil_strict;base_seuil_strict;pe_reglementaire;pe_scientifique;sources;fiabilite;est_agregat;cancerogenicite_circ
1584;92-52-4;Biphényle;Pesticide - substance individuelle;µg/L;;0.10;2023-01-01;;Seuil applicable seulement lorsque le gestionnaire traite le biphenyle comme fongicide organique au sens de la note Pesticides de l annexe I. Le biphenyle n est nomme dans aucun texte EDCH. SANDRE le classe en Liste B - Phytosanitaires (groupe 204, ajout du 29/01/2025), liste definie par AQUAREF comme celle ou la decision sur le caractere pesticide revient au gestionnaire. Dans le corpus, l ARS d Eure-et-Loir declare la limite 0,1 ug/L a partir du 31/03/2026 et rien avant. INERIS ecrit au contraire qu aucune valeur n est mentionnee dans la directive 98/83/CE ou l OMS.;limite;;;;;non;non evalue;REG-01|REG-02|REG-03|SAN-1584;a_verifier;non;
```

Points de forme et de fond à ne pas modifier sans y revenir :

- **`seuil_2016` volontairement vide.** La valeur de 0,10 µg/L existait bien en 2016 (arrêté du
  11 janvier 2007 d'origine, lu), mais rien n'établit que le biphényle était alors traité comme
  un pesticide, et l'administration ne déclarait aucune limite. Remplir cette case fabriquerait
  un passé réglementaire à partir de la grille du jour — §2.8. Conséquence assumée : **aucune
  bascule 2016→2026 ne peut naître de cette ligne**, ce qui est le résultat correct puisque la
  valeur elle-même n'a pas bougé.
- **`date_applicabilite_2026 = 2023-01-01`** : date d'entrée en vigueur de la rédaction actuelle
  de l'annexe I (arrêté du 30 décembre 2022). Ce n'est **pas** le 31/03/2026, qui est une date
  d'observation dans le corpus et non une date de texte.
- **`fiabilite = a_verifier`**, et cela doit rester visible dans toute sortie publique : la
  valeur est lue, son rattachement à cette substance ne l'est pas.
- **`seuil_strict` vide** : aucun balayage international n'a été fait pour cette substance ; il
  n'y a donc pas de « plus strict identifié ».
- **`pe_scientifique = non evalue`** : je n'ai lu aucune source, ni dans un sens ni dans l'autre,
  sur un statut de perturbateur endocrinien du biphényle. Ne pas écrire « non ».
- **`SAN-1584`** est un code de source à créer dans `docs/INDEX_SOURCES.md` s'il est retenu ; il
  n'existe pas aujourd'hui.

---

## 6. Table des sources

| Organisme | Titre exact | Date | URL ou chemin local | Lecture |
|---|---|---|---|---|
| Parlement européen et Conseil | *Directive (UE) 2020/2184 relative à la qualité des eaux destinées à la consommation humaine* — **texte intégral, annexes comprises** | 16/12/2020 (JO L 435 du 23/12/2020) | `Sources\REG_Reglementation_et_seuils\REG-01_UE_directive-2020-2184.pdf` | **lue en entier** (extraction `pdftotext -layout`, 3 005 lignes ; annexe I A/B/C et annexe III effectivement présentes et relues à l'écran). **Le contournement local fonctionne** — inutile de repasser par EUR-Lex |
| République française | *Arrêté du 30 décembre 2022 modifiant l'arrêté du 11 janvier 2007…* (grille 2026) | 30/12/2022, JO du 31/12/2022 | `Sources\REG_Reglementation_et_seuils\REG-03_FR_arrete-2022-12-30_grille-2026.pdf` | **lue** (extraction complète, annexe I relue ; définition « pesticides » et « total pesticides » citées verbatim ci-dessus) |
| République française | *Arrêté du 11 janvier 2007 relatif aux limites et références de qualité des eaux brutes et des eaux destinées à la consommation humaine* — **rédaction d'origine** | 11/01/2007 | `Sources\REG_Reglementation_et_seuils\REG-02_FR_arrete-2007-01-11_grille-2016.pdf` | **lue** (16 741 lignes extraites ; annexes I et II présentes ; ligne « Pesticides (par substance individuelle) 0,10 µg/L » localisée) |
| Légifrance | Même arrêté, **version consolidée**, annexe I (`LEGIARTI000046890189`) | en vigueur au 01/01/2023 | https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000046890189 | **lue** — recherche ciblée « biphényle » / « diphényle » : absent ; inventaire complet des paramètres organiques obtenu |
| OMS | *Guidelines for drinking-water quality*, 4e édition incorporant les 1er et 2e additifs | 4e éd. (millésime exact `a_verifier`) | `Sources\REG_Reglementation_et_seuils\REG-04_OMS_directives-qualite-eau-4e-ed.pdf` | **lue en entier** (recherche plein texte + relecture de la table A3.2). Résultat : le biphényle n'y figure **pas du tout** |
| INERIS | *Données technico-économiques sur les substances chimiques en France : Biphényle*, **DRC-18-158744-00413A**, 26 p. | mise à jour du **14/02/2018**, version novembre 2017 | https://substances.ineris.fr/sites/default/files/archives/92-52-4%20--%20Biph%C3%A9nyle%20--%20FTE.pdf | **lue** (PDF converti localement après téléchargement par l'outil web ; sections 1.2 à 1.6 relues, citations verbatim au §2.4 et §4) |
| INERIS | *Portail Substances Chimiques — Biphényle (92-52-4)*, section « Norme de qualité pour la santé humaine via l'eau de boisson (QSdw_hh) » | consultée le 11/08/2026 | https://substances.ineris.fr/substance/92-52-4 | **lue partiellement** — la phrase d'absence est citée verbatim ; la **valeur seuil provisoire de 0,53 µg/L n'a pas été lue verbatim** et reste `a_verifier` |
| SANDRE / Eaufrance | *Biphényle — Paramètre chimique*, fiche du paramètre **1584** | créée le 26/03/1997, dernière mise à jour le **29/01/2025** | http://mdm.sandre.eaufrance.fr/id/parametre/1584/html · http://id.eaufrance.fr/par/1584 | **lue** — CAS 92-52-4, classe chimique 56 « Benzène et dérivés », groupes 97 « Fongicides », 127, 204 « Liste B – Phytosanitaires », 211 |
| SANDRE / Eaufrance | Groupes de paramètres **97 « Fongicides »** (créé 29/07/2010, 227 paramètres) et **204 « Liste B – Phytosanitaires »** (créé 02/07/2021, mis à jour 06/12/2022, 115 paramètres, groupe parent 200) | — | http://id.eaufrance.fr/gpr/97 · http://id.eaufrance.fr/gpr/204 | **lues** — les fiches SANDRE ne portent **aucune définition** ni commentaire pour ces groupes : le critère d'appartenance vient de la note AQUAREF ci-dessous |
| AQUAREF | *Listes de paramètres phytopharmaceutiques, biocides, et métabolites dans la base SANDRE* (rapport E2.1b) | 2019 | https://www.aquaref.fr/sites/default/files/Aquaref_2019_E2.1b_Note_SANDRE_liste%20usage%20phyto.pdf | **lue partiellement** (PDF converti localement ; le passage définissant les sous-listes A et B est cité verbatim au §2.3) |
| Univ. of Hertfordshire, AERU | *Pesticide Properties DataBase (PPDB) — Biphenyl*, fiche 82 | consultée le 11/08/2026 | https://sitem.herts.ac.uk/aeru/ppdb/en/Reports/82.htm | **lue** — *Substance type: Fungicide* ; groupe « Aromatic hydrocarbon compound » ; statut règlement (CE) 1107/2009 : **Not approved**, inclusion **Expired** ; **aucune** valeur « Drinking Water MAC » ni « WHO drinking water guideline » |
| Hub'Eau / SISE-Eaux (ministère chargé de la santé), via `data/eau.duckdb` | champ `limite_qualite_parametre` des mesures du paramètre 1584 | mesures du 04/08/2016 au 29/05/2026 | base locale du projet | **relue** — 1 374 mesures sans limite déclarée, 40 mesures à `<=0,1 µg/L` du 31/03/2026 au 29/05/2026 |
| République française | *Arrêté du 17 juillet 2009 relatif aux mesures de prévention ou de limitation des introductions de polluants dans les eaux souterraines* | 17/07/2009 | — | **NON LUE.** Citée uniquement d'après INERIS 2018 ; l'appartenance du biphényle à sa liste de substances dangereuses est `a_verifier` |
| OMS – IPCS | *Concise International Chemical Assessment Document (CICAD) n° 6 — Biphenyl* | 1999 | http://www.inchem.org/documents/cicads/cicads/cicad06.htm | **NON LUE.** La VTR de 38 µg/kg p.c./j en provient d'après INERIS ; `a_verifier` |
| Commission européenne | EU Pesticides Database, statut du biphényle au titre du règlement (CE) 1107/2009 | — | https://ec.europa.eu/food/plant/pesticides/eu-pesticides-database/ | **NON LUE** — base interrogeable par formulaire, non atteinte par récupération d'URL. Le statut « non approuvé » repose sur PPDB et sur la phrase INERIS 2018, deux sources concordantes mais secondaires |

---

## 7. Ce que je n'ai pas pu établir

1. **Le point de droit central reste ouvert : le biphényle est-il un « fongicide organique » au
   sens de l'annexe I de l'arrêté ?** Aucun texte lu ne le dit ni ne le nie. Les deux camps sont
   documentés au §2.3 et se contredisent : l'ARS d'Eure-et-Loir applique la limite depuis le
   31/03/2026, l'INERIS écrit qu'aucune valeur ne s'applique. **Je n'ai trouvé aucune instruction
   DGS, aucune circulaire, aucune note technique qui arbitre.** C'est ce point, et lui seul, qui
   fait que la ligne du §5.3 porte `a_verifier` et non `verifie`.
2. **Je n'ai pas identifié le texte ou la décision qui a fait apparaître la limite déclarée le
   31 mars 2026.** La date est certaine dans le corpus, sa cause ne l'est pas. Piste non
   explorée : le renouvellement du marché d'analyses de l'ARS Centre-Val de Loire, ou une mise à
   jour du référentiel SISE-Eaux. Aucune de ces hypothèses n'est sourcée.
3. **La valeur INERIS de 0,53 µg/L n'a pas été lue verbatim** et n'est donc pas versable. Elle
   n'est de toute façon ni opposable ni reprise par un texte : c'est un calcul de l'INERIS pour
   les besoins de la dérivation des normes environnementales.
4. **Trois sources primaires n'ont pas été atteintes** : l'arrêté du 17 juillet 2009 (eaux
   souterraines), le CICAD n° 6 de l'OMS-IPCS (VTR de 38 µg/kg p.c./j), et la base européenne
   des pesticides (statut d'approbation). Chacune est signalée comme telle dans la table des
   sources. Aucune des trois ne porte une valeur EDCH ; leur absence ne change pas le verdict,
   mais elle limite ce que le projet peut affirmer sur le statut de la substance.
5. **Le millésime exact de l'édition OMS lue** (4e édition, ou 4e édition incorporant les
   additifs, ou version 2022) n'est pas établi — le PDF local porte un titre générique. Sans
   effet ici, puisque le résultat est une absence totale, mais à préciser si la citation devait
   être datée.
6. **Registres non explorés**, à dire pour qu'on sache où chercher ensuite si une valeur existait
   ailleurs : matériaux au contact de l'eau (attestations de conformité sanitaire, limites de
   migration — le biphényle est un fluide caloporteur, ce registre n'est pas absurde) ; eaux
   conditionnées ; valeurs seuils « eaux souterraines » au titre de la DCE (la circulaire de 2012
   est nommée par AQUAREF mais n'a pas été ouverte) ; réglementations étrangères (Santé Canada,
   US EPA, Suisse). Aucun de ces registres n'est celui de la question posée.
7. **Écart de dénombrement avec le brief, non résolu.** Le brief annonce 1 373 mesures et
   12 quantifications ; la base lue le 11/08/2026 en donne **1 414 et 13**, dont **une mesure en
   Saône-et-Loire (dept 71)**, hors du périmètre « Tarn + Eure-et-Loir » annoncé. Le maximum,
   0,016 µg/L, est identique dans les deux comptes. Je n'ai pas cherché à réconcilier : soit le
   brief repose sur un instantané antérieur, soit son filtre départemental diffère. **Aucun
   chiffre de ce dossier ne dépend de cet écart** — mais il doit être tranché avant toute
   publication qui citerait un effectif.
8. **Je n'ai pas vérifié si les bulletins portant les 40 mesures sous limite déclarée sont des
   bulletins complets** au sens du §2.3 du projet (`nb_parametres > 200`). Sans effet sur le
   sourçage, mais nécessaire avant d'en tirer un indicateur.

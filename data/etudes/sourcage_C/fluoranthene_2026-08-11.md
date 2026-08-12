# Sourçage réglementaire — Fluoranthène (CAS 206-44-0)

- **Date du sourçage** : 2026-08-11
- **Substance** : Fluoranthène, SANDRE **1191**, CAS **206-44-0**, libellé SISE-Eaux « Fluoranthène * », unité **µg/L**

---

## 1. Le verdict, en une phrase

**C2 pour l'eau destinée à la consommation humaine** — aucune valeur réglementaire opposable
EDCH ne nomme le fluoranthène, ni dans la directive (UE) 2020/2184 ni dans l'arrêté du
11 janvier 2007 dans sa rédaction en vigueur — **et il n'entre pas dans la somme HAP
opposable de l'eau distribuée (0,10 µg/L, quatre composés nommés)** ; en revanche il est
nommé en toutes lettres dans la somme HAP à **six** composés de l'**annexe II** du même
arrêté, **limite 1 µg/L opposable aux eaux brutes** — un autre milieu que celui du corpus.

Réponses aux trois sommes, en une ligne chacune :

| somme | fluoranthène dedans ? | limite déclarée dans un texte ? |
|---|---|---|
| **2033** — HAP (4 substances) | **NON** | oui, 0,10 µg/L, EDCH, opposable |
| **2034** — HAP (6 subst.*) | **OUI** | oui, **1 µg/L, eaux brutes uniquement** — pas l'eau distribuée |
| **6136** — HAP (16 subst.) EPA | **OUI** | **non** — agrégat de nomenclature SANDRE, aucun texte ne lui attache de valeur |

---

## 2. Fiche d'identité et cadrage du corpus

| champ | valeur |
|---|---|
| libellé SISE-Eaux | Fluoranthène * |
| code SANDRE | 1191 |
| code SISE-Eaux court | FLUORA |
| CAS | 206-44-0 |
| groupe SANDRE | HAP (Hydrocarbures aromatiques, polycycliques, pyrolytiques et dérivés) [62] |
| unité du corpus | µg/L (code unité 133) |
| mesures / communes | 72 / 68 |
| quantifications | 30 |
| max relevé | 0,1983 µg/L |
| min quantifié | 0,001 µg/L |
| période | 07/02/2022 → 27/05/2026 |
| limite déclarée par la source | **aucune** — `limite_qualite_parametre = null`, vérifié 62/62 en Eure-et-Loir |
| lieu d'analyse | `code_lieu_analyse = "L"` sur 62/62 — **eau distribuée**, jamais eau brute |
| grille applicable au moteur | `aucune` |

Chiffres de cadrage fournis par le projet ; **revérifiés ici** sur les fichiers bruts
`data/brut/28/*.jsonl.gz` et `data/brut/71/*.jsonl.gz` (§5). Les comptages du projet
(30 quantifications pour 1191, 22 pour 2034) sont reproduits exactement.

**Le piège d'identité, tenu tout au long** : fluoranthène (206-44-0) ≠ fluorène (86-73-7)
≠ benzo(b)fluoranthène (205-99-2) ≠ benzo(k)fluoranthène (207-08-9) ≠ fluorures / fluor.
Chaque source ci-dessous a été appariée par CAS ou par nom littéral, jamais par
ressemblance de libellé.

---

## 3. Les valeurs trouvées

### 3.1 Registre réglementaire opposable — eau destinée à la consommation humaine

| Valeur | Unité | Nature | Texte source | Date du texte | Date d'applicabilité | Statut |
|---|---|---|---|---|---|---|
| *aucune* | — | — | Directive (UE) 2020/2184, **annexe I partie B** — paramètres chimiques, 34 lignes | 16/12/2020, JOUE L 435 du 23/12/2020 | 12/01/2021 (entrée en vigueur), transposition au 12/01/2023 | `verifie` — lue intégralement, aucun fluoranthène |
| *aucune* | — | — | idem, **annexe I parties A, C et D** | idem | idem | `verifie` — lues intégralement |
| *aucune* | — | — | idem, **annexe III** parties A et B (table 1 « uncertainty of measurement », notes 1 à 10, point 3 « Sum of PFAS ») | idem | idem | `verifie` — le fluoranthène n'y figure pas |
| *aucune* | — | — | Arrêté du 11/01/2007, **version consolidée en vigueur**, **annexe I** | consolidation lue le 11/08/2026 | en vigueur | `verifie` — Légifrance ; « fluoranthène » n'apparaît pas dans l'annexe I |
| *aucune* | — | — | Arrêté du 30/12/2022, **annexe I** — sections I (A et B), II, III (valeurs indicatives), IV (valeurs de vigilance) | JORF 31/12/2022, texte 161 sur 251 | **01/01/2023** (art. 2) | `verifie` — sections lues intégralement |
| *aucune* | — | — | Arrêté du 11/01/2007, **rédaction d'origine**, annexe I | JORF 06/02/2007, texte 17 sur 121 | 2007 → 31/12/2022 | `verifie` — la chaîne « fluoranth » n'y apparaît que dans « benzo[b]fluoranthène » et « benzo[k]fluoranthène » |

### 3.2 Registre réglementaire opposable — EAUX BRUTES et EAUX SUPERFICIELLES

**Ici le fluoranthène est nommé.** Ce n'est **pas** une valeur applicable à l'eau distribuée,
et le corpus ne contient aucune mesure d'eau brute (§5.3).

| Valeur | Unité | Nature | Texte source | Date du texte | Date d'applicabilité | Statut |
|---|---|---|---|---|---|---|
| **1** — somme de 6 composés dont le fluoranthène | **µg/L** | limite de qualité **opposable**, milieu = **eaux brutes de toutes origines utilisées pour la production d'EDCH** | Arrêté du 11/01/2007 **consolidé**, **annexe II** (remplacée par l'annexe II de l'arrêté du 30/12/2022) | 30/12/2022, JORF 31/12/2022 | **01/01/2023**, toujours en vigueur | `verifie` — lue deux fois : PDF local `REG-03` **et** version consolidée Légifrance |
| **1,0** — même somme de 6 | **µg/L** | idem, rédaction antérieure | Arrêté du 11/01/2007, **annexe II**, rédaction d'origine | JORF 06/02/2007 | 2007 → 31/12/2022 | `verifie` — groupe « substances toxiques », entre Cyanures 50 µg/L et Mercure 1,0 µg/L |
| **0,2 (A1 et A2) / 1,0 (A3)** — même somme de 6 | **µg/L** | limites de qualité des **eaux douces superficielles** utilisées pour la production d'EDCH, grille A1/A2/A3 | Arrêté du 11/01/2007, **annexe III**, rédaction d'origine | JORF 06/02/2007 | 2007 → **abrogée au 01/01/2023** | `a_verifier` sur les trois chiffres — le libellé de la somme est certain, l'affectation aux colonnes A1/A2/A3 repose sur une extraction `pdftotext -layout` d'un tableau à six colonnes, non recoupée. **L'annexe III est abrogée** : arrêté du 30/12/2022, art. 1er, 5° « L'annexe III est abrogée » |

**Libellé exact de la somme, annexe II en vigueur** :

> « Hydrocarbures aromatiques polycycliques (HAP) : Somme des composés suivants :
> fluoranthène, benzo[b]fluoranthène, benzo[k]fluoranthène, benzo[a]pyrène,
> benzo[g, h,i]pérylène et indéno[1,2,3-cd]pyrène. »

**Sur l'unité de cette ligne — le piège du décalage de colonnes, avéré.** La mise en garde du
projet sur `REG-03` est justifiée : l'extraction `-layout` de la page 7 décale bien la colonne
UNITÉS. La valeur **µg/L** est retenue sur **quatre recoupements convergents** :

1. la **version consolidée Légifrance** de l'arrêté du 11/01/2007 affiche pour l'annexe II
   « 1 µg/ L » — lecture indépendante du PDF, sur une mise en page différente ;
2. la même somme, dans la rédaction d'origine de 2007 (`REG-02`, annexe II, page 63),
   s'affiche sur une mise en page propre à « 1,0 » et « µg/L », dans le groupe
   « paramètres concernant les substances toxiques » ;
3. l'annexe III de 2007 place la même somme dans le même groupe, en µg/L ;
4. l'ordre des 15 unités de la colonne de l'annexe II 2022 se réaligne **sans reste** sur les
   15 paramètres chiffrés (Fluorures mg/L, HAP µg/L, Indice hydrocarbures mg/L, Mercure
   µg/L, Nickel µg/L, Nitrates mg/L ×2, pesticides µg/L ×2, Plomb µg/L, Sélénium µg/L —
   recoupé par la note (4) « 30 µg/L » —, Sodium mg/L, Somme PFAS µg/L, Sulfates mg/L,
   Taux de saturation %).

### 3.3 Registre valeur guide non opposable — OMS

L'OMS n'a pas « oublié » le fluoranthène : elle l'a examiné et a **explicitement renoncé** à
lui fixer une valeur guide. C'est un fait distinct de l'absence.

| Élément | Contenu | Statut |
|---|---|---|
| Table A3.2 « Chemicals for which guideline values have not been established » | entrée « Fluoranthene<sup>d</sup> », motif : **« Occurs in drinking-water at concentrations well below those of health concern »** ; note d = « See fact sheet on polynuclear aromatic hydrocarbons » | `verifie` |
| Table 8.16, rubrique **« Contaminants from pipes and fittings »** | entrée « Fluoranthene<sup>c</sup> », même motif | `verifie` |
| **Valeur fondée sur la santé** (*health-based value*) | **4 µg/L** — NOAEL 125 mg/kg p.c./j (étude de gavage 13 semaines chez la souris), facteur d'incertitude **10 000** (100 inter/intra-espèces, 10 étude subchronique et base de données insuffisante, 10 co-cancérogénicité avérée avec le benzo[a]pyrène en application cutanée chez la souris) | `verifie` |
| Nature juridique de ces 4 µg/L | **ce n'est pas une valeur guide** : l'OMS écrit « the establishment of a formal guideline value for fluoranthene is not deemed necessary ». L'annexe 3 précise que les *health-based values* « may be useful to guide actions by Member States when there is a reason for local concern » | `verifie` |
| Date d'évaluation | **1998** ; référence principale : WHO (2003) *Polynuclear aromatic hydrocarbons in drinking-water* | `verifie` |
| Pour mémoire, benzo[a]pyrène | valeur guide OMS **0,0007 mg/L (0,7 µg/L)** — autre substance, ne pas transposer | `verifie` |

**Registre littérature / VTR** : non exploré au-delà de l'OMS. Aucun avis Anses portant
nommément sur le CAS 206-44-0 en EDCH n'a été identifié (§9).

---

## 4. L'appartenance aux sommes, une par une

Méthode : pour chaque agrégat, **la fiche SANDRE qui désigne ses composants par code**, puis
**le texte réglementaire** qui lui attache — ou non — une valeur. Un agrégat de nomenclature
sans limite dans le texte n'est pas une somme opposable.

### 4.1 Somme HAP « 4 substances » — SANDRE 2033 — **le fluoranthène N'Y EST PAS**

Fiche SANDRE 2033, libellé « HAP somme(4) », définition verbatim :

> « Hydrocarbures Aromatiques Polycycliques, somme des concentrations en
> benzo(b)fluoranthène (code Sandre n°1116), benzo(k)fluoranthène (code Sandre n°1117),
> benzo(g,h,i)pérylène (code Sandre n°1118) et indéno(1,2,3-cd)pyrène (code Sandre n°1204). »

| composant | SANDRE | CAS |
|---|---|---|
| Benzo(b)fluoranthène | 1116 | 205-99-2 |
| Benzo(k)fluoranthène | 1117 | 207-08-9 |
| Benzo(g,h,i)pérylène | 1118 | 191-24-2 |
| Indéno(1,2,3-cd)pyrène | 1204 | 193-39-5 |

**Périmètre confirmé par trois textes, tous lus** :

- Directive (UE) 2020/2184, annexe I partie B, ligne « Polycyclic aromatic hydrocarbons »,
  valeur paramétrique **0,10 µg/l** :
  > « Sum of concentrations of the following specified compounds: benzo(b)fluoranthene,
  > benzo(k)fluoranthene, benzo(ghi)perylene, and indeno(1,2,3-cd)pyrene. »
- Arrêté du 30/12/2022, annexe I, **0,10 µg/L** :
  > « Pour la somme des composés suivants : benzo[b]fluoranthène, benzo[k]fluoranthène,
  > benzo[ghi]pérylène, indéno[1,2,3-cd]pyrène »
- Arrêté du 11/01/2007, rédaction d'origine, annexe I : même énumération de quatre.

**Le fluoranthène n'y est pas. Le benzo(a)pyrène non plus** : il porte sa valeur individuelle
propre, **0,010 µg/L** (directive annexe I partie B ; arrêté du 30/12/2022 annexe I) et **ne
doit pas être compté deux fois**.

C'est le cas d'école du projet sous une forme nouvelle : le fluoranthène **est** chimiquement
un HAP, c'est même le HAP le plus quantifié du corpus, et il n'entre pas dans le paramètre
« hydrocarbures aromatiques polycycliques » de l'eau du robinet, **qui nomme quatre composés
et ferme sa liste par énumération**. Même mécanique que le trichlorofluorométhane hors des
THM et que le trichloroéthane-1,1,1 hors de « tétrachloroéthylène + trichloroéthylène ».

### 4.2 Somme HAP « 6 subst.* » — SANDRE 2034 — **le fluoranthène Y EST**

Fiche SANDRE 2034, libellé « HAP somme(6) », définition verbatim :

> « Hydrocarbures Aromatiques Polycycliques, somme des concentrations en
> benzo(b)fluoranthène (code Sandre n°1116), benzo(k)fluoranthène (code Sandre n°1117),
> benzo(g,h,i)pérylène (code Sandre n°1118), indéno(1,2,3-cd)pyrène (code Sandre n°1204),
> **fluoranthène (code Sandre n°1191)** et benzo (3,4) pyrène (benzo(a) pyrène)
> (code Sandre n°1115). »

| composant | SANDRE | CAS |
|---|---|---|
| **Fluoranthène** | **1191** | **206-44-0** |
| Benzo(b)fluoranthène | 1116 | 205-99-2 |
| Benzo(k)fluoranthène | 1117 | 207-08-9 |
| **Benzo(a)pyrène** | **1115** | **50-32-8** |
| Benzo(g,h,i)pérylène | 1118 | 191-24-2 |
| Indéno(1,2,3-cd)pyrène | 1204 | 193-39-5 |

**Le périmètre SANDRE et le périmètre du texte coïncident exactement.** La somme de six de
l'annexe II est le périmètre de quatre **augmenté du fluoranthène et du benzo(a)pyrène** —
les deux substances que le corpus marque d'un astérisque (« Fluoranthène * »,
« Benzo(a)pyrène * »), astérisque que reprend le libellé de l'agrégat lui-même
(« 6 subst.**\*** »). Les quatre autres composants n'en portent pas. La convention de notation
corrobore la lecture des textes ; elle n'en tient pas lieu.

**Statut opposable de cette somme** : limite **1 µg/L**, **eaux brutes** (arrêté du 11/01/2007
consolidé, annexe II). **Elle ne s'applique pas à l'eau distribuée**, seul milieu présent dans
le corpus (§5.3). C'est pourquoi la source ne déclare aucune limite sur ces mesures.

### 4.3 Somme HAP « 16 substances » — SANDRE 6136 — le fluoranthène y est, **mais ce n'est pas une somme opposable**

Fiche SANDRE 6136, libellé « Somme HAP (16) - EPA », définition verbatim :

> « Ce paramètre est la somme des 16 paramètres suivants : - Indéno(1,2,3-cd)pyrène de code
> Sandre n°1204 ; - Benzo(k)fluoranthène de code Sandre n°1117 ; - Benzo(a)pyrène de code
> Sandre n°1115 ; - Benzo(g,h,i)pérylène de code Sandre n°1118 ; - **Fluoranthène de code
> Sandre n°1191** ; - Naphtalène de code Sandre n°1517 ; - Anthracène de code Sandre n°1458 ;
> - Phénanthrène de code Sandre n°1524 ; - Acénaphtène de code Sandre n°1453 ; - Chrysène de
> code Sandre n°1476 ; - Benzo(a)anthracène de code Sandre n°1082 ; - Dibenzo(a,h)anthracène
> de code Sandre n°1621 ; - Acénaphtylène de code Sandre n°1622 ; - Pyrène de code Sandre
> n°1537 ; - Fluorène de Sandre n°1623 ; - Benzo(b)fluoranthène de code Sandre n°1116. »

| composant | SANDRE | | composant | SANDRE |
|---|---|---|---|---|
| **Fluoranthène** | **1191** | | Chrysène | 1476 |
| Benzo(a)pyrène | 1115 | | Benzo(a)anthracène | 1082 |
| Benzo(b)fluoranthène | 1116 | | Dibenzo(a,h)anthracène | 1621 |
| Benzo(k)fluoranthène | 1117 | | Acénaphtène | 1453 |
| Benzo(g,h,i)pérylène | 1118 | | Acénaphtylène | 1622 |
| Indéno(1,2,3-cd)pyrène | 1204 | | Pyrène | 1537 |
| Naphtalène | 1517 | | **Fluorène** | **1623** |
| Anthracène | 1458 | | Phénanthrène | 1524 |

**Aucun texte EDCH consulté n'attache de valeur à cette somme de 16** : elle est absente de
la directive (annexes I A/B/C/D et III), des annexes I et II de l'arrêté du 11/01/2007
consolidé, et de l'annexe I de l'arrêté du 30/12/2022. La source ne déclare aucune limite
(`limite_qualite_parametre = null` sur les 8 mesures du corpus). **C'est l'agrégat de
nomenclature dont le §6 du brief met en garde** : le suffixe « EPA » renvoie à la liste
analytique des 16 HAP prioritaires de l'US EPA, pas à une norme d'eau potable.

Deux pièges à noter au passage : le **fluorène (1623, CAS 86-73-7)** est dans cette somme et
n'est **pas** le fluoranthène ; et l'appartenance à la somme de 16 ne crée aucune obligation.

### 4.4 Les autres sommes du référentiel — **non**, une par une

| somme | fluoranthène dedans ? | pourquoi |
|---|---|---|
| Trihalométhanes (4) | non | chloroforme, bromoforme, dibromochlorométhane, bromodichlorométhane — nommés, aucun HAP |
| Acides haloacétiques (5, SANDRE 9064) | non | mono-, di-, trichloroacétique, bromo-, dibromoacétique — nommés |
| PFAS (20, annexe III B.3) | non | liste nominative de 20 acides perfluorés |
| Tétrachloroéthylène + trichloroéthylène (2) | non | « the sum of concentrations of these two parameters » |
| Pesticides — somme et substance individuelle | non | le fluoranthène n'est pas un produit phytopharmaceutique ; voir §4.5 |

### 4.5 C-g — la règle de catégorie : vérifiée, **elle ne s'applique pas**

La question posée était celle du biphényle : la substance n'est nommée nulle part, mais une
règle de famille pourrait la capter.

Le référentiel du projet porte deux règles (`referentiel/regles_famille.csv`), déclenchées par
la **limite déclarée avec la mesure** : `pesticide_individuel_0_1` (0,1 µg/L) et
`pesticide_organochlore_0_03` (0,03 µg/L).

**Le fluoranthène ne peut être capté par aucune des deux : la source ne déclare aucune limite
avec ses mesures** — `limite_qualite_parametre = null` sur **62/62** enregistrements
d'Eure-et-Loir et **10/10** de Saône-et-Loire. Il n'y a donc rien à quoi la règle puisse
s'accrocher. C'est une vérification faite sur les fichiers bruts, pas une lecture de la vue.

Et sur le fond : la définition des pesticides de l'annexe I (« insecticides organiques,
herbicides organiques, fongicides organiques… et produits apparentés ») ne couvre pas un HAP
de combustion. Le raisonnement qui a fait entrer le biphényle (« fongicide organique ») n'a
pas d'équivalent ici. **Conclusion : ni C-g, ni C1. C2, avec la nuance de milieu du §1.**

> **À signaler, hors périmètre de ce dossier mais découvert en le faisant.** Les quatre
> composants de la somme de 4 — benzo(b)fluoranthène 1116, benzo(k)fluoranthène 1117,
> benzo(g,h,i)pérylène 1118, indéno(1,2,3-cd)pyrène 1204 — portent chacun une limite déclarée
> `<=0.1 µg/L` (c'est la limite de la somme, répétée sur chaque composant) et **aucun des
> quatre n'est nommé dans `referentiel/referentiel_seuils.csv`**, où seul l'agrégat 2033
> figure. Ils sont donc des candidats à la capture par `pesticide_individuel_0_1`, qui les
> compterait comme pesticides. La vue `SELECT * FROM v_regle_famille_appliquee` **n'a pas pu
> être exécutée** (§9) : à contrôler avant toute publication de comptes par famille.

---

## 5. La démonstration arithmétique, sur les bulletins du corpus

Le rapprochement des périmètres n'est pas resté au stade de l'indice.

### 5.1 Le dispositif

Les bulletins d'Eure-et-Loir portent, **sur le même prélèvement**, les six substances
individuelles ET les deux agrégats. Extraction directe de `data/brut/28/*.jsonl.gz` :
**496 enregistrements HAP, soit 62 mesures pour chacun des codes 1115, 1116, 1117, 1118,
1191, 1204, 2033 et 2034** — symétrie parfaite, aucun manquant.

### 5.2 La preuve

**Prélèvement `02800129138`** — le seul du corpus où trois HAP sont quantifiés ensemble :

| code | substance | résultat (µg/L) |
|---|---|---|
| 1115 | Benzo(a)pyrène * | 0,0004 |
| 1116 | Benzo(b)fluoranthène | 0,0005 |
| 1191 | Fluoranthène * | 0,007 |
| 1117, 1118, 1204 | les trois autres | 0 (non quantifiés) |
| **2033** | **HAP (4 substances)** | **0,0005** |
| **2034** | **HAP (6 subst.\*)** | **0,0079** |

- `2033 = 0,0005` = **le seul benzo(b)fluoranthène**. Le fluoranthène (0,007) et le
  benzo(a)pyrène (0,0004) n'y entrent pas : s'ils y entraient, l'agrégat vaudrait 0,0079.
- `2034 = 0,0079` = 0,0004 + 0,0005 + 0,007 = **benzo(a)pyrène + benzo(b)fluoranthène +
  fluoranthène**.

**C'est une preuve, pas un indice**, et elle est indépendante des textes : elle dit ce que le
laboratoire additionne. Elle concorde exactement avec les fiches SANDRE et avec les annexes.

Sur les 21 autres prélèvements d'Eure-et-Loir où le fluoranthène est seul quantifié, `2034`
reprend exactement sa valeur (0,001 ; 0,002 ; 0,004 ; 0,008 ; 0,009 ; 0,010 ; 0,0185 ; 0,019 ;
0,023 ; 0,0235 ; 0,027 ; 0,0341 ; 0,0468 ; 0,0503 ; 0,058 ; 0,0608 ; 0,1249 ; **0,1983**)
tandis que `2033` reste à 0. Idem en Saône-et-Loire, prélèvement `07100131957` : fluoranthène
0,0212 → `2034` 0,0212, `6136` non quantifié (`<0,0955`).

**Le maximum de 0,1983 µg/L relevé sur l'agrégat 2034 est la mesure de fluoranthène du
prélèvement `02800129563`.** L'indice signalé par le projet est confirmé : c'est bien le
fluoranthène qui porte cet agrégat.

### 5.3 Le milieu — le point qui commande l'usage de tout ce qui précède

**`code_lieu_analyse = "L"` sur 62/62 enregistrements de fluoranthène en Eure-et-Loir**, et le
champ `conclusion_conformite_prelevement` parle d'« Eau d'alimentation ». Ce sont des
prélèvements d'**eau distribuée**. Le corpus ne contient **aucune** mesure d'eau brute pour ce
paramètre. La limite de 1 µg/L de l'annexe II ne peut donc juger aucune des 72 mesures.

### 5.4 Limites déclarées par la source, sur ces mêmes bulletins

| code | libellé | `limite_qualite_parametre` |
|---|---|---|
| 1191 | Fluoranthène * | **null** (62/62) |
| 1115 | Benzo(a)pyrène * | `<=0.01 µg/L` — concorde avec la valeur individuelle 0,010 µg/L |
| 1116, 1117, 1118, 1204 | les quatre de la somme | `<=0.1 µg/L` chacun |
| 2033 | HAP (4 substances) | `<=0,1 µg/L` |
| 2034 | HAP (6 subst.*) | **null** (62/62) |
| 6136 | HAP (16 subst.) | **null** |

Cohérent de bout en bout : la source ne déclare de limite que pour ce que le texte juge.

**Anomalie de restitution, signalée sans être exploitée.** Sur le prélèvement `02800129222`,
le fluoranthène est quantifié à 0,0065 µg/L mais l'agrégat 2034 est rendu `<0,0155`,
c'est-à-dire non quantifié (somme des limites de quantification). L'agrégat 2034 sous-estime
donc dans certains bulletins. C'est une question de qualité de donnée, pas de réglementation ;
elle n'a aucune conséquence ici puisque aucun verdict n'est prononcé sur 2034.

---

## 6. Pourquoi la substance est-elle mesurée, alors que rien ne la juge ?

Trois raisons, toutes sourcées, qui se recoupent.

### 6.1 Le paquet analytique est celui d'un texte encore en vigueur — sur un autre milieu

L'annexe II de l'arrêté du 11 janvier 2007, **en vigueur**, impose pour les **eaux brutes**
une somme HAP portant sur six composés nommés, dont le fluoranthène. Le laboratoire livre donc
un paquet « HAP » à six substances. Sur un prélèvement d'eau distribuée, il rend les six
mesures individuelles **et les deux agrégats** — celui qui est jugé (2033, avec sa limite
déclarée) et celui qui ne l'est pas (2034, sans limite). Le fluoranthène arrive dans le
bulletin comme composant d'un paquet, pas comme paramètre à juger.

C'est la même mécanique que les réponses déjà obtenues sur d'autres dossiers du projet
(« balayage chromatographique COHV rendu pour les composés réglementés »). La symétrie 62/62
sur les huit codes (§5.1) en est la signature : jamais l'un sans les autres.

### 6.2 Le fluoranthène est le traceur des revêtements de canalisation au goudron de houille

L'OMS, fiche « Polynuclear aromatic hydrocarbons », 4<sup>e</sup> édition :

> « The main source of PAH contamination in drinking-water is usually the coal tar coating of
> drinking-water distribution pipes, used to protect the pipes from corrosion. **Fluoranthene
> is the most commonly detected PAH in drinking-water** and is associated primarily with coal
> tar linings of cast iron or ductile iron distribution pipes. »

Et, dans les *Additional comments* de la fiche benzo[a]pyrène :

> « The presence of significant concentrations of benzo[a]pyrene in drinking-water **in the
> absence of very high concentrations of fluoranthene** indicates the presence of coal tar
> particles, which may arise from seriously deteriorating coal tar pipe linings. »

Autrement dit, l'OMS fait du fluoranthène le **terme de comparaison** qui permet d'interpréter
le benzo[a]pyrène. Mesurer le premier n'a de sens que pour lire le second. La table 8.16 des
*Guidelines* classe d'ailleurs le fluoranthène sous la rubrique **« Contaminants from pipes
and fittings »**, et non parmi les contaminants de la ressource.

### 6.3 La lecture danoise dit la même chose, et en fait une norme

Le Danemark, seule juridiction des quinze consultées à donner au fluoranthène une valeur
opposable individuelle, l'accompagne d'une note d'une ligne : **« Indikator for
tjæreprodukter »** — indicateur de produits goudronnés (§7).

**Ce que ces trois raisons ne disent pas.** Aucune source consultée ne rattache le fluoranthène
du corpus à une liste de surveillance : la première liste de surveillance européenne
(décision d'exécution (UE) 2022/679, visée par l'arrêté du 30/12/2022) porte le
17 bêta-estradiol et le nonylphénol, et eux seuls — ils figurent tous deux à l'annexe I
section IV « valeurs de vigilance », où le fluoranthène est absent.

---

## 7. Le balayage international

**Liste standard du projet, 15 juridictions, toutes consultées.**

### 7.1 Le tableau

| Juridiction | Fluoranthène nommé ? | Valeur applicable au fluoranthène | Paramètre HAP et son **périmètre** | Nature | Consultation |
|---|---|---|---|---|---|
| **UE** | non | *aucune* | « Polycyclic aromatic hydrocarbons » **0,10 µg/l**, **4** composés : B(b)F, B(k)F, B(ghi)P, indéno(1,2,3-cd)P. Benzo(a)pyrene à part, 0,010 µg/l | opposable | **lue** — annexe I A/B/C/D et annexe III |
| **France** | **oui — eaux brutes seulement** | **1 µg/L** en somme de 6, **eaux brutes** ; *aucune* en eau distribuée | EDCH : **0,10 µg/L**, **4** composés. Eaux brutes : **1 µg/L**, **6** composés dont fluoranthène | opposable | **lue** — annexes I et II, PDF + Légifrance consolidé |
| **Allemagne** | **non** | *aucune* — « Fluoranthen » absent de l'Anlage 2 | PAK **0,00010 mg/l**, **4** composés (« Summe der folgenden nachgewiesenen und mengenmäßig bestimmten Stoffe: Benzo(b)fluor… »). Benzo(a)pyren 0,000010 mg/l | opposable | **lue** — TrinkwV 2023, Anlage 2 Teil I et II, Anlage 3 |
| **Danemark** | **OUI — individuellement** | **0,1 µg/L** au robinet du consommateur, **bilag 1 d** « Kvalitetskrav til nationalt fastsatte kemiske parametre (Sundhedshensyn) », note 8 « Indikator for tjæreprodukter » | en plus : somme HAP **4** composés (note 11) ; Benz(a)pyren à part | **opposable** | **lue** — bilag de la drikkevandsbekendtgørelse (projet mis en consultation) ; texte promulgué inaccessible (403) → valeur `a_verifier`, existence `verifie` |
| **Suède** | **non** | *aucune* — « fluoranten » n'apparaît que dans benso(b)- et benso(k)fluoranten | PAH **0,10 µg/l**, **4** composés | opposable | **lue** — LIVSFS 2022:12, tableau intégral |
| **Pays-Bas** | **OUI — dans la somme** | pris dans la somme, **0,10 µg/l** | **PAK's (som) 0,10 µg/l** sur **10** composés : pyreen, benzo(a)antraceen, benzo(ghi)peryleen, fenantreen, indeno(1,2,3-cd)pyreen, anthraceen, benzo(b)fluorantheen, benzo(k)fluorantheen, chryseen **en fluorantheen**. Benzo(a)pyreen à part, 0,010 µg/l | **opposable** | **lue** — Staatsblad 2022, 450 (décret du 08/11/2022 transposant 2020/2184), Bijlage A Tabel II, note verbatim |
| **Suisse** | **non** | *aucune* — « Fluoranthen » absent de toute l'ordonnance | « Kohlenwasserstoffe, polycyclische, aromatische » **0,1 µg/l**, **4** composés (« Summe von Benzo[b]fluoranthen, Benzo[k]fluoranthen, Benzo[ghi]perylen, Indeno[1,2,3-cd]pyren ») | opposable | **lue** — TBDV 817.022.11, Anhang 2, version au 01/01/2026 |
| **Royaume-Uni** | **non** | *aucune* | « Polycyclic aromatic hydrocarbon » **0,10 µg/l**, **4** composés (note vi). Benzo(a)pyrene **0,010 µg/l** | opposable | **lue** — Water Supply (Water Quality) Regulations 2016, Schedule 1 |
| **Norvège** | **non** | *aucune* — « fluoranten » n'apparaît qu'en composé | « Polyaromatiske hydrokarboner (PAH) » **0,10 µg/l**, **4** composés. Benzo(a)pyren **0,010 µg/l** | opposable | **lue** — drikkevannsforskriften, vedlegg 1 |
| **États-Unis fédéral** | **non** | *aucune* | **pas de paramètre HAP de groupe**. Benzo[a]pyrene MCL **0,0002 mg/l** (CAS 50-32-8) | opposable | **lue** — 40 CFR 141.61, table 1(c) |
| **Californie** | **non** | *aucune* — « fluoranthene » absent de la table des MCL | pas de MCL de groupe HAP ; benzo(a)pyrene présent | opposable | **lue partiellement** — table MCL/DLR/PHG parcourue par recherche de chaîne ; **valeurs numériques non retenues**, l'extraction décale les colonnes |
| **Canada** | **non identifié** | *aucune* identifiée | Recommandation benzo[a]pyrène, CMA **0,00001 mg/L** dans le document technique consulté ; une révision ultérieure exprimerait la recommandation en équivalents de puissance B[a]P | recommandation | **partielle** — document technique benzo[a]pyrène lu ; **tableau de synthèse Santé Canada inaccessible (403)** → valeur `a_verifier` |
| **Australie / Nouvelle-Zélande** | **non** | *aucune* — « Data are inadequate to set guidelines for other PAHs » | **pas de somme**. Benzo[a]pyrene **0,00001 mg/L (10 ng/L)** ; les autres HAP sont traités par puissances cancérogènes relatives | valeur guide | **lue** — ADWG, fiche PAH |
| **Japon** | **non** | *aucune* | **aucun paramètre HAP** parmi les 52 items du 水質基準 | — | **lue** — liste des 52 items, ministère de l'Environnement |
| **OMS** | **oui — renoncement explicite** | **pas de valeur guide** ; *health-based value* **4 µg/L**, non opposable, évaluation 1998 | Benzo[a]pyrene, valeur guide **0,0007 mg/l (0,7 µg/l)** ; pas de somme | valeur guide / renoncement motivé | **lue** — 4<sup>e</sup> éd., fiche PAH, tables 8.16 et A3.2 |

### 7.2 Ce que ce tableau permet de dire, et dans ces mots-là

**Sur la substance prise individuellement.** *À périmètre strictement identique — le
fluoranthène seul —, la seule valeur opposable identifiée parmi les quinze juridictions
consultées est celle du Danemark, 0,1 µg/L au robinet du consommateur.* Aucune valeur
opposable inférieure n'a été identifiée. Douze juridictions sur quinze ne nomment pas la
substance ; l'OMS la nomme pour dire qu'elle n'y fixe pas de valeur.

**Sur l'assiette — le point que le projet a manqué sur les PFAS.** Trois périmètres coexistent
sous la même étiquette « HAP » et **la même valeur de 0,10 µg/L** :

| périmètre | juridictions | fluoranthène dedans ? |
|---|---|---|
| **4 composés** | UE, France (EDCH), Allemagne, Suède, Suisse, Royaume-Uni, Norvège, Danemark | non |
| **10 composés** | **Pays-Bas** | **oui** |
| **6 composés** | France, **eaux brutes uniquement**, à 1 µg/L | oui |

*À valeur égale, les Pays-Bas sont plus stricts que l'UE sur ce paramètre, non par le chiffre
mais par l'assiette* : dix composés au lieu de quatre, fluoranthène compris. Comparer les
seuls chiffres aurait conclu à l'équivalence.

**Ce que le tableau ne dit pas.** Les valeurs danoise et néerlandaise ne s'appliquent pas en
France. On peut seulement constater, à titre de repère documenté, que la mesure la plus élevée
du corpus — 0,1983 µg/L, Eure-et-Loir, 2026 — est supérieure à la valeur danoise de 0,1 µg/L
et supérieure, à elle seule, à la valeur néerlandaise de somme. Cette comparaison est
documentaire ; elle ne produit aucun verdict.

**Bloc « recommandé, sourcé, non repris »** : OMS, *health-based value* 4 µg/L (1998) ;
Australie/NZ, valeurs dérivées par puissance cancérogène relative au benzo[a]pyrène ; Canada,
équivalents de puissance B[a]P. Aucune n'est opposable, aucune n'entre dans la comparaison.

---

## 8. La ligne de référentiel — **recommandation : ne rien verser**

**Ne verser aucune ligne nominative pour le fluoranthène (1191), ni pour les agrégats 2034 et
6136.** Trois raisons, dans l'ordre d'importance.

1. **Il n'y a pas de valeur à verser.** Aucun texte EDCH ne juge cette substance. Toute
   colonne `seuil_2016` ou `seuil_2026` renseignée serait une valeur qu'aucune source ne
   soutient.
2. **La seule valeur existante juge un autre milieu.** Verser 1 µg/L au titre de l'annexe II
   ferait juger 72 mesures d'eau distribuée par une limite d'eau brute, et rendrait
   « conformes » 30 quantifications que rien ne juge. **C'est le faux positif inversé** :
   celui qui transforme de l'indéterminé en conforme — exactement l'erreur que le projet a
   évitée sur le biphényle, dans l'autre sens.
3. **Ne rien verser ne change rien au moteur, et c'est le point.** Le fluoranthène n'a pas de
   limite déclarée (§4.5) : aucune règle de famille ne peut le capter. Son statut reste
   `aucune`, c'est-à-dire **indéterminé**, ce qui est le verdict juste. Une substance sans
   seuil n'est pas sans danger : elle est indéterminée.

**Aucun mot du vocabulaire contrôlé ne convient.** `limite` et `reference` supposent une valeur
opposable EDCH, qui n'existe pas. `vigilance` est réservé aux valeurs de vigilance de l'annexe I
section IV, où le fluoranthène ne figure pas. `dans somme` serait faux pour l'eau distribuée :
la seule somme opposable qui le contient ne porte pas sur ce milieu.

**Si Yannick veut néanmoins tracer la décision dans le référentiel**, la seule forme qui ne
fabrique aucun verdict est une ligne à seuils vides, dont le sens tient entièrement dans le
commentaire — et il faut alors vérifier d'abord que le chargeur accepte une ligne sans seuil
sans lui inventer de statut. Format, séparateur `;`, sources séparées par `|`, **aucun
point-virgule dans une cellule** :

```
1191;206-44-0;Fluoranthene;organique;µg/L;;;;;;;;;;;non;a_documenter;REG-01|REG-03|REG-04;verifie;non;
```

Colonne `statut_2026` volontairement **laissée vide** : aucun mot du vocabulaire contrôlé ne
décrit exactement cette situation, et en inventer un serait pire que l'absence. **Décision de
Yannick, pas du sourçage.**

**Ce qui change si le projet ingère un jour des points d'eau brute.** Alors, et alors
seulement, l'agrégat 2034 devient jugeable à 1 µg/L (arrêté du 11/01/2007 consolidé, annexe II)
et le fluoranthène y entre nommément. Il faudra à ce moment-là un champ de milieu dans le
moteur : la même somme SANDRE porte une limite sur un milieu et aucune sur l'autre.

**Action séparée recommandée**, hors de ce dossier : contrôler
`SELECT * FROM v_regle_famille_appliquee` pour les codes 1116, 1117, 1118 et 1204, qui portent
une limite déclarée `<=0.1 µg/L` sans être nommés au référentiel (§4.5).

---

## 9. Table des sources

### 9.1 Fonds local

| Organisme | Titre exact | Date | Chemin | Lecture |
|---|---|---|---|---|
| Parlement européen et Conseil | Directive (UE) 2020/2184 relative à la qualité des eaux destinées à la consommation humaine (refonte) | 16/12/2020, JOUE L 435 du 23/12/2020 | `Sources\REG_Reglementation_et_seuils\REG-01_UE_directive-2020-2184.pdf` | **annexes I A/B/C/D (p. 34-42) et III (p. 49-53) lues intégralement** ; corps du texte parcouru (liste de surveillance) |
| Ministère de la santé (FR) | Arrêté du 30 décembre 2022 modifiant l'arrêté du 11 janvier 2007… | 30/12/2022, JORF 31/12/2022, texte 161/251 | `…\REG-03_FR_arrete-2022-12-30_grille-2026.pdf` | **articles 1 à 3 et annexes I et II lus intégralement** |
| Ministère de la santé (FR) | Arrêté du 11 janvier 2007 relatif aux limites et références de qualité des eaux brutes et des EDCH — **rédaction d'origine** | 11/01/2007, JORF 06/02/2007, texte 17/121 | `…\REG-02_FR_arrete-2007-01-11_grille-2016.pdf` | **annexes I, II et III lues** (p. 59-66) |
| OMS | *Guidelines for drinking-water quality*, 4<sup>e</sup> éd. incorporant les 1<sup>er</sup> et 2<sup>e</sup> addenda | 2017 | `…\REG-04_OMS_directives-qualite-eau-4e-ed.pdf` | **partiellement** : fiche « Polynuclear aromatic hydrocarbons », table 8.16 et ses notes, table A3.2 et ses notes a-j |
| Projet | Fichiers bruts Hub'Eau, départements 28 et 71 | collecte du projet | `observatoire-potabilite\data\brut\28\*.jsonl.gz`, `…\71\*.jsonl.gz` | **496 + 28 enregistrements HAP extraits et analysés** |
| Projet | Référentiel de seuils et règles de famille | — | `referentiel\referentiel_seuils.csv`, `referentiel\regles_famille.csv`, `referentiel\catalogue_parametres_hubeau.csv` | **lus** sur les codes HAP |

### 9.2 Réseau

| Organisme | Titre | Date | URL | Lecture |
|---|---|---|---|---|
| SANDRE (MDM) | Fiche paramètre 2033 « HAP somme(4) » | consultée le 11/08/2026 | `mdm.sandre.eaufrance.fr/id/parametre/2033/html` | **définition intégrale** |
| SANDRE (MDM) | Fiche paramètre 2034 « HAP somme(6) » | 11/08/2026 | `…/parametre/2034/html` | **définition intégrale** |
| SANDRE (MDM) | Fiche paramètre 6136 « Somme HAP (16) - EPA » | 11/08/2026 | `…/parametre/6136/html` | **définition intégrale** |
| SANDRE (MDM) | Fiche paramètre 1191 « Fluoranthène » | 11/08/2026 | `…/parametre/1191/html` | **lue** — CAS 206-44-0, groupe HAP [62] |
| Légifrance | Arrêté du 11 janvier 2007…, **version consolidée** | 11/08/2026 | `legifrance.gouv.fr/loda/id/JORFTEXT000000465574/` | **lue** — annexes en vigueur, lignes HAP des annexes I et II |
| Bundesministerium der Justiz (DE) | TrinkwV 2023, **Anlage 2** (Grenzwerte chemische Parameter) et **Anlage 3** | 11/08/2026 | `gesetze-im-internet.de/trinkwv_2023/anlage_2.html`, `…/anlage_3.html` | **lues** |
| Miljø- og Ligestillingsministeriet (DK) | Bilag à la drikkevandsbekendtgørelse, **version mise en consultation avec marques de révision** | non datée sur le document | `prodstoragehoeringspo.blob.core.windows.net/…/Bilag%20til%20drikkevandsbekendtgørelsen%20med%20track%20changes.pdf` | **lue** — bilag 1 a à 1 f ; **c'est un projet, pas le texte promulgué** |
| Miljøstyrelsen (DK) | *Drikkevandsvejledningen* — Vejledning om vandkvalitet og tilsyn med vandforsyningsanlæg | 07/2025 (et éd. 02/2022) | `www2.mst.dk/Udgiv/publikationer/2025/07/978-87-7564-019-5.pdf` | **partiellement** — passage nommant le fluoranthène parmi les paramètres fixés nationalement |
| Miljøstyrelsen (DK) | Liste over drikkevandskvalitetskriterier | 08/2025 | `mst.dk/media/akuguzcw/liste-over-drikkevandskvalitetskriterier-august-2025.pdf` | **lue** — le fluoranthène n'y figure pas (cohérent : il a un kvalitetskrav, pas un critère) |
| Livsmedelsverket (SE) | LIVSFS 2022:12, föreskrifter om dricksvatten | 2022 | `livsmedelsverket.se/globalassets/…/livsfs-2022-12_web_t.pdf` | **lue** — tableau des paramètres chimiques |
| Overheid.nl (NL) | **Staatsblad 2022, 450** — Besluit du 08/11/2022 modifiant le Drinkwaterbesluit (transposition 2020/2184), Bijlage A Tabel II | 08/11/2022 | `zoek.officielebekendmakingen.nl/stb-2022-450.html` | **lue** — lignes PAK et benzo(a)pyreen, note verbatim |
| Fedlex (CH) | Ordonnance du DFI sur l'eau potable (TBDV), RS 817.022.11, Anhang 2 | version au 01/01/2026 | `fedlex.data.admin.ch/…/eli/cc/2017/153/20260101/de/pdf-a/…pdf` | **lue** — annexe des exigences chimiques |
| legislation.gov.uk | Water Supply (Water Quality) Regulations 2016, **Schedule 1** | 2016 | `legislation.gov.uk/uksi/2016/614/schedule/1/made` | **lue** |
| Lovdata (NO) | Drikkevannsforskriften, **vedlegg 1** | 22/12/2016 | `lovdata.no/dokument/SF/forskrift/2016-12-22-1868` | **lue** |
| eCFR (US) | 40 CFR 141.61 — Maximum contaminant levels for organic contaminants | courant | API de rendu eCFR, `title-40 … section=141.61` | **lue** |
| State Water Resources Control Board (CA) | Table des MCL / DLR / PHG de l'eau potable | rév. 2018 | reproduction PDF `gswater.com/…/california-drinking-water-standards-rev-21218.pdf` | **partiellement** — recherche de chaîne seulement ; **colonnes décalées à l'extraction, valeurs non retenues** |
| Santé Canada | *Guidelines for Canadian Drinking Water Quality — Guideline Technical Document: Benzo[a]pyrene* | 1997/2003 | `healthycanadians.gc.ca/publications/…/water-benzo-a-pyrene-eau-eng.pdf` | **lue** — la CMA benzo[a]pyrène ; aucune mention du fluoranthène |
| NHMRC (AU) | *Australian Drinking Water Guidelines*, fiche « Polycyclic aromatic hydrocarbons (PAHs) » | courante | `guidelines.nhmrc.gov.au/…/polycyclic-aromatic-hydrocarbons-pahs` | **lue** |
| Ministère de l'Environnement (JP) | 水質基準項目と基準値（52項目） | courante | `env.go.jp/water/water_supply/kijun/kijunchi.html` | **lue** — aucun paramètre HAP |

### 9.3 Sources tentées sans succès

| Source | Motif |
|---|---|
| Légifrance, article `LEGIARTI000046890189` | **HTTP 403** sur l'URL d'article. Contourné par l'URL du texte consolidé (`JORFTEXT000000465574`), qui répond. |
| EUR-Lex, directives 80/778/CEE et 75/440/CEE | **contenu vide** sur toutes les formes d'URL essayées — même comportement que celui déjà constaté par le projet sur 2020/2184 |
| retsinformation.dk (texte promulgué de la drikkevandsbekendtgørelse, BEK 1023/2023 et BEK 1633/2024) | **HTTP 403** sur `/eli/…`, `/eli/…/pdf` et `/api/pdf/…` |
| Santé Canada, tableau de synthèse des recommandations | **HTTP 403** |
| wetten.overheid.nl, Drinkwaterbesluit Bijlage A | contenu tronqué avant les annexes sur trois formes d'URL ; contourné par le Staatsblad, qui est la source d'origine |
| api.sandre.eaufrance.fr (API référentiels) | **HTTP 400** ; contourné par les fiches HTML du MDM |
| CIRC / IARC | non consulté — pages servies en JavaScript ; **champ `cancerogenicite_circ` laissé vide**, conformément à la consigne |

---

## 10. Ce qui n'a pas pu être établi

1. **La valeur danoise n'a pas été lue dans le texte promulgué.** Les 0,1 µg/L du bilag 1 d
   proviennent d'un **projet de bilag mis en consultation avec marques de révision**, hébergé
   sur le portail de consultation danois. Le texte promulgué (retsinformation) répond 403 sur
   toutes les formes d'URL essayées. Ce qui est solidement établi : **le Danemark fixe
   nationalement un kvalitetskrav pour le fluoranthène**, la *Drikkevandsvejledningen* de la
   Miljøstyrelsen le nomme explicitement en 2022 comme en 2025 parmi les paramètres
   « som ikke har ophæng i drikkevandsdirektivet ». Ce qui reste `a_verifier` : **le chiffre
   0,1 µg/L**. L'alignement des colonnes du bilag 1 d a toutefois été recoupé par une valeur
   connue du projet — la somme PFAS-4 danoise à 0,002 µg/L, soit 2 ng/L, cohérente avec
   `PFAS-05_OCDE_Danemark-somme4-2ngL.pdf`.
2. **Les valeurs A1/A2/A3 de l'annexe III de 2007 ne sont pas fiables.** L'extraction décale
   un tableau à six colonnes. Le libellé de la somme est certain, les chiffres non. Enjeu
   faible : l'annexe est abrogée depuis le 01/01/2023 et ne porte pas sur l'eau distribuée.
3. **Les valeurs californiennes n'ont pas été retenues.** La table extraite décale les
   colonnes MCL et DLR d'une ligne (le benzo(a)pyrene y apparaît avec la valeur de la ligne
   voisine). Seule l'**absence** du fluoranthène, établie par recherche de chaîne, est
   rapportée.
4. **La valeur canadienne actuelle n'est pas confirmée.** Le document technique lu (CMA
   benzo[a]pyrène 0,00001 mg/L) est ancien ; une révision ultérieure exprimerait la
   recommandation en équivalents de puissance B[a]P sur une valeur différente. Le tableau de
   synthèse de Santé Canada est inaccessible (403). Sans effet sur la conclusion : aucune
   valeur canadienne pour le fluoranthène n'a été identifiée dans les deux cas.
5. **La vue `v_regle_famille_appliquee` n'a pas été exécutée.** Aucun interpréteur Python
   n'est installé sur ce poste (`python`, `python3`, `py` renvoient vers l'alias d'exécution
   du Microsoft Store ; aucun `.venv` dans le dépôt), et la base DuckDB n'est donc pas
   interrogeable. La démonstration du §4.5 a été refaite **sur les fichiers bruts**, ce qui
   est équivalent pour le fluoranthène (limite déclarée nulle sur 72/72 mesures) mais ne
   remplace pas le contrôle de la vue pour les quatre composants de la somme de 4.
6. **L'origine historique du paquet à six substances n'est pas remontée en source primaire.**
   L'hypothèse naturelle — le paquet vient de l'ancienne directive 80/778/CEE et de la
   directive 75/440/CEE sur les eaux superficielles, qui portaient une somme HAP à six
   composés — **n'a pas été vérifiée** : EUR-Lex renvoie un contenu vide pour ces deux
   textes. L'explication retenue au §6.1 ne dépend pas de cette hypothèse : elle s'appuie sur
   l'annexe II **en vigueur**, qui suffit.
7. **Le classement CIRC du fluoranthène n'a pas été relevé** — pages en JavaScript. Le champ
   `cancerogenicite_circ` doit rester vide plutôt que recevoir le classement d'un HAP voisin.
8. **Aucun avis Anses portant nommément sur le CAS 206-44-0 en EDCH n'a été recherché de
   façon exhaustive.** Les valeurs guides et VTR nationales françaises pour cette substance
   n'ont pas été explorées au-delà de l'OMS. À traiter si le dossier doit alimenter un texte
   publié.
9. **Le corpus n'a été recontrôlé qu'en Eure-et-Loir et Saône-et-Loire**, les deux seuls
   départements portant des quantifications. Les 72 mesures annoncées se répartissent en
   62 (28) + 10 (71) ; la répartition des autres départements n'a pas été rouverte.

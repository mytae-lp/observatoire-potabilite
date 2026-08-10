# Audit des paramètres sans seuil de comparaison — 9 août 2026, soirée

Relecture demandée par le §2.8 avant de publier un département entier
(`docs/REPRISE.md` §10.2, point 1). État de la base au 9 août 2026, référentiel
`2cc3c1a9a6c9` (commit `550713a`), corpus 1 372 988 mesures — Eure-et-Loir et
Tarn collectés en entier.

**L'inventaire libellé par libellé est ailleurs et fait foi :**
`data/etudes/parametres_non_apparies_2026-08-09.md`, produit dans la journée,
avec sa colonne « cause » A/B/C et la référence déclarée par la source. Ce
document-ci ne le recopie pas : il porte ce que l'inventaire ne dit pas — ce qui
reste à décider, dans quel ordre, et ce que chaque décision changerait aux
chiffres publiés.

**Aucune valeur de seuil n'est écrite ici sans son extrait de texte** (§2.7).

---

## 1. Le compte de la vue surcompte — de 14 libellés et 23 189 mesures

```sql
-- v_parametres_non_apparies, src/build_db.py
WHERE ref_key IS NULL AND limite_declaree IS NULL
```

Le filtre teste la **limite** déclarée, pas la **référence** déclarée. Or depuis
le travail du §11 de `REPRISE.md`, le moteur lit les références de la source
(`reference_min` / `reference_max`) et en tire `hors_reference`. Conséquence :
des paramètres qui sont **effectivement comparés à une valeur** figurent quand
même dans la liste des « sans aucun seuil ».

| | libellés | mesures | part du corpus |
|---|---|---|---|
| listés par la vue, avant les six lignes | 157 | 114 812 | 8,4 % |
| dont une référence déclarée sur **100 %** de leurs mesures | 14 | 23 189 | 1,7 % |
| **listés après adoption des six lignes** (`6c9caf8b87a6`) | **150** | **99 078** | **7,2 %** |
| dont une référence déclarée | 7 | 7 455 | 0,5 % |
| **réellement comparés à rien** | **143** | **91 623** | **6,7 %** |

Les six lignes ont retiré sept libellés de la liste (les six paramètres, plus
« Fer dissous » qui partage le code 1393) et 15 734 mesures. **Les sept qui
restent surcomptés** : température de l'eau, équilibre calcocarbonique, bactéries
et spores sulfito-réductrices, coliformes thermotolérants, odeur et saveur par
dilution, chlorite en mg/L.

**Correctif proposé** — une ligne dans `VUE_NON_APPARIES` :

```sql
WHERE ref_key IS NULL AND limite_declaree IS NULL
  AND reference_max IS NULL AND reference_min IS NULL
```

Non appliqué : `src/build_db.py` a été modifié dans la journée par un autre fil
de travail, et le §7 du mode opératoire interdit deux éditeurs sur un même
fichier. À appliquer par le fil qui tient ce fichier. **Le compte passerait alors
de 150 à 143**, et l'énoncé cesserait d'être trompeur.

---

## 2. Répartition des 157 libellés

Synthèse par nature — le détail est dans l'inventaire cité en tête.

| catégorie | libellés | mesures | quantifiées | enjeu |
|---|---|---|---|---|
| physico-chimie et organoleptique | 36 | 50 590 | 21 835 | **partiel** — cf. §4 |
| COV, aromatiques, phénols | 47 | 13 502 | 133 | faible, sauf §5 |
| PCB (congénères + somme indicateurs) | 18 | 17 341 | **0** | nul aujourd'hui |
| PFAS individuels | 16 | 4 832 | 148 | à confirmer, §5 |
| microbiologie | 11 | 7 383 | 1 033 | faible |
| sous-produits de désinfection | 11 | 6 708 | 5 950 | **réel**, §5 |
| pesticides et substances émergentes | 10 | 4 099 | 26 | faible |
| radiologique | 4 | 10 193 | 5 837 | **§5** |
| HAP | 4 | 164 | 90 | **§3 — bloquant** |

---

## 3. Le seul dossier bloquant : l'anthraquinone

| libellé | code SANDRE | code CAS | mesures | quantifiées | max |
|---|---|---|---|---|---|
| Anthraquinone (pesticide) | 2013 | 84-65-1 | 3 094 | 141 | 0,16 µg/L |
| Anthraquinone (HAP) | 2013 | 84-65-1 | **39** | **39** | **0,15 µg/L** |

Même code SANDRE, même numéro CAS : **la même molécule**, sous deux libellés de
la source. Les mesures « (pesticide) » sont notées parce que l'administration y
déclare une limite de 0,1 µg/L, que `regles_famille` rattache à la ligne
« pesticide - substance individuelle ». Les 39 mesures « (HAP) » ne portent ni
limite ni référence déclarée, donc aucun verdict — **alors qu'elles sont toutes
quantifiées, et au-dessus de la valeur qui, sous l'autre libellé, produit un
dépassement**, dans 22 communes.

Ce n'est donc pas le libellé qui décide, c'est **ce que l'ARS a déclaré sur ce
bulletin-là** (`g.limite_declaree = m.limite_declaree`, `src/build_db.py:193`).
Trois autres libellés sont dans ce cas, sans enjeu de quantification : biphényle
(40 mesures notées sur 1 413), chloroneb (30 sur 1 065), bromométhane (2 sur
580).

**La décision n'est pas technique** : ajouter une ligne de référentiel portant
le code 2013 apparierait les deux libellés d'un coup, mais cela revient à dire
que la limite « pesticide » s'applique à la molécule mesurée sous son étiquette
HAP. C'est un raisonnement réglementaire, à sourcer.

**Et le §11.2 impose un contrôle préalable** : vérifier que le code 2013 ne
porte pas deux limites déclarées différentes selon les bulletins — c'est
exactement le piège qui a produit deux faux dépassements de sélénium dans la
journée.

**En attendant, ne rien publier sur l'anthraquinone**, ni comme présence ni
comme absence (§2.4).

---

## 4. Les six lignes préparées — arrêté du 11 janvier 2007

### 4.1 Ce qu'elles changent, et ce qu'elles ne changent pas

Ces six paramètres **sont déjà comparés** : la source déclare sa référence sur
100 % de leurs mesures, et `hors_reference` fonctionne — 27 dépassements de COT,
25 de turbidité, 3 d'ammonium, 3 de manganèse, 2 de fer sur le corpus figé.
Les inscrire au référentiel n'ajoute donc pas un verdict qui manquerait. Cela
ajoute **trois choses que le §2.8 refuse à une valeur seulement déclarée** :

1. une **grille 2016**, donc la possibilité d'un contrefactuel et d'une bascule ;
2. une valeur qui ne dépend plus de ce que l'ARS a choisi d'écrire sur tel
   bulletin — la turbidité est déclarée tantôt à 0,5, tantôt à 2 NFU selon les
   bulletins, ce qui rend les comptes incomparables entre eux (§2.11) ;
3. une `fiabilite` et des `sources` opposables.

Pour les six, la valeur **n'a pas bougé entre les deux grilles** : la version en
vigueur au 19 décembre 2015 et la version consolidée en vigueur portent les
mêmes chiffres. Donc `seuil_2016 = seuil_2026`, aucune
`date_applicabilite_2026`, et **aucune bascule ne naîtra de ces lignes**.

### 4.2 Les extraits, lus sur Légifrance

Source : arrêté du 11 janvier 2007, texte JORFTEXT000000465574, **annexe I**.
Deux lectures indépendantes de la version consolidée en vigueur, plus une
lecture de la version en vigueur du 19/12/2015 au 18/08/2017 pour la grille 2016.

> **II. − Références de qualité des eaux destinées à la consommation humaine**
> **B. − Paramètres chimiques et organoleptiques**
>
> | Carbone organique total (COT). | 2 et aucun changement anormal | mg/L |
> | Fer | 200 | µg/L |
> | Manganèse | 50 | µg/L |
> | Ammonium | 0,10 | mg/L | *S'il est démontré que l'ammonium a une origine naturelle, la référence de qualité est de 0,50 mg/L pour les eaux souterraines.* |
> | Couleur | Acceptable pour les consommateurs et aucun changement anormal. Inférieure ou égale à 15 | mg/L (Pt) |

La turbidité apparaît **trois fois**, et c'est ce qui fait sa difficulté :

> **I. − Limites de qualité** — **B. Paramètres chimiques**
> Turbidité | **1,0** | NFU | *La limite de qualité est applicable au point de
> mise en distribution, pour les eaux visées à l'article R. 1321-37 et pour les
> eaux d'origine souterraine provenant de milieux fissurés présentant une
> turbidité périodique supérieure à 2,0 NFU. En cas de mise en œuvre d'un
> traitement de neutralisation ou de reminéralisation, la limite de qualité
> s'applique hors augmentation éventuelle de turbidité due au traitement.*
>
> **II. − Références de qualité** — **B. Paramètres chimiques et organoleptiques**
> Turbidité | **0,50** | NFU | *(même périmètre que la limite ci-dessus)*
> Turbidité | **2** | NFU | *La référence de qualité s'applique aux robinets
> normalement utilisés pour la consommation humaine.*

**Réserve à lever avant de passer `fiabilite` à `verifie` sur la turbidité** :
`REG-06` est catalogué dans `docs/INDEX_SOURCES.md` **sans fichier sur le
disque** (défaut déjà signalé au §« défauts de tenue »). Ces extraits ont été
lus en ligne. `pypdf` étant désormais installé (§11.4), archiver le PDF de
Légifrance sous `REG-06_FR_arrete-2007-01-11-consolide.pdf` clôt la réserve.

### 4.3 Les lignes — **adoptées le 10 août 2026**

Décision de Yannick. Elles sont au référentiel, la base est refigée sous la
version **`6c9caf8b87a6`**, et le site est republié. Effet mesuré au §4.4.

**Un point relevé après coup, à garder** : le contrôle du §11.2 — un même code
porte-t-il deux objets réglementaires ? — répond **oui pour la turbidité**. Le
code 1295 porte, selon les bulletins, une limite déclarée de 1,0 NFU (247
mesures) et une référence déclarée de 0,5 ou de 2 NFU (2 729). C'est le motif
qui avait fait retirer les codes du sélénium et des chlorates. Ici l'appariement
a été maintenu, et c'est défendable — le seuil conditionnel empêche tout faux
positif au verdict daté — mais il a une conséquence : **deux mesures à 1,3 NFU
(Rueil-la-Gadelière le 13/02/2025, et une commune du Tarn le 18/01/2018)
passent d'un dépassement de *limite* à un dépassement de *référence***, donc du
rouge à l'ambre. Là où l'ARS déclare la limite, elle nous disait que le bulletin
relevait bien du périmètre de l'article R. 1321-37 — information que notre
ligne écrase. À rouvrir si le périmètre devient déterminable.

Contrôle de forme passé : **21 colonnes chacune, aucun point-virgule interne**
(§5 de `CLAUDE.md` — l'erreur commise deux fois).

```
1393;7439-89-6;Fer;metal;µg/L;200.0;200.0;;;;reference;;;200.0;Reference de qualite FR arrete 11/01/2007 annexe I partie II section B;non;non;REG-02|REG-06;verifie;non;
1394;7439-96-5;Manganese;metal;µg/L;50.0;50.0;;;;reference;;;50.0;Reference de qualite FR arrete 11/01/2007 annexe I partie II section B;non;non;REG-02|REG-06;verifie;non;
1335;14798-03-9;Ammonium;mineral;mg/L;0.10;0.10;;0.50;origine naturelle demontree - eaux souterraines (note de l annexe I partie II section B);reference;;;0.10;Reference de qualite FR arrete 11/01/2007 annexe I partie II section B;non;non;REG-02|REG-06;verifie;non;
1841;;Carbone organique total;organique;mg/L;2.0;2.0;;;;reference (la mention < aucun changement anormal > n est pas modelisable);;;2.0;Reference de qualite FR arrete 11/01/2007 annexe I partie II section B;non;non;REG-02|REG-06;verifie;non;
1309;;Coloration;organoleptique;mg/L;15.0;15.0;;;;reference (double enonce - acceptable pour les consommateurs ET inferieure ou egale a 15);;;15.0;Reference de qualite FR arrete 11/01/2007 annexe I partie II section B;non;non;REG-02|REG-06;verifie;non;
1295;;Turbidite;organoleptique;NFU;1.0;1.0;;2.0;prelevement au robinet - reference de qualite 2 NFU. La limite de qualite de 1,0 NFU ne vise que les eaux de l article R. 1321-37 et les eaux souterraines de milieux fissures - le corpus ne dit pas si le bulletin en releve;reference;;;0.50;Reference de qualite FR 0,50 NFU au point de mise en distribution - meme perimetre que la limite;non;non;REG-02|REG-06;a_verifier;non;
```

**Trois choix à valider, ils ne se déduisent pas du texte :**

- **`organoleptique` est une famille nouvelle** (les familles existantes sont
  PFAS, equilibre, metabolite, metal, metalloide, microbiologique, mineral,
  nitrates, nitrites, organique, pesticide, radiologique, sous-produit
  desinfection). Elle ne change rien au calcul — `famille` est descriptive — mais
  c'est une entrée de nomenclature.
- **Turbidité : `reference`, pas `limite`.** Le texte porte bien une limite de
  qualité, mais elle ne vise qu'une partie des eaux, et **rien dans les données
  ne dit si un bulletin en relève**. La déclarer `limite` la peindrait en rouge
  (§11.3) sur des bulletins qui ne sont peut-être pas dans son périmètre. C'est
  le §2.13 appliqué : seuil conditionnel à 2,0 NFU, dépassement prononcé
  seulement au-dessus, `indetermine_condition` entre 1,0 et 2,0. `a_verifier`
  jusqu'à ce que la question du point de prélèvement soit tranchée — la même
  question que celle qui bloque l'hypothèse de dilution (§7.2).
- **Fer : le code 1393 porte deux libellés**, « Fer total » (2 868 mesures) et
  « Fer dissous » (22). Le texte dit « Fer », sans précision. La ligne apparie
  donc les deux. À confirmer, ou à restreindre.

### 4.4 Ce que cela produirait, mesuré

Dépassements que ces lignes prononceraient, **après** application de
l'asymétrie du §2.13 (au-dessus de la valeur la plus permissive) :

| paramètre | seuil retenu | mesures au-dessus | dont 28 | communes |
|---|---|---|---|---|
| Carbone organique total | 2,0 mg/L | 27 | 7 | 9 |
| Turbidité | 2,0 NFU (conditionnel) | 16 | 9 | 15 |
| Manganèse | 50 µg/L | 3 | 1 | 3 |
| Fer | 200 µg/L | 2 | 1 | 2 |
| Ammonium | 0,50 mg/L (conditionnel) | **0** | 0 | 0 |
| Coloration | 15 mg/L (Pt) | **0** | 0 | 0 |

Soit **48 dépassements**, tous de nature `reference` — ambre, jamais rouge
(§11.3) — et **aucune bascule**. Les trois ammonium entre 0,10 et 0,50 et les
30 turbidités entre 1,0 et 2,0 sortent en `indetermine_condition`, à relire à la
main avant publication comme l'exige le §2.13.

**Et les chiffres publiés du 28 bougent** — c'est le point à ne pas manquer.
`nb_depasse_2026` compte tous les dépassements, quelle que soit leur nature :
douze bulletins jusqu'ici *conformes avec bascule* portent une turbidité (9) ou
un COT (3) au-dessus de sa valeur, et sortent donc de l'ensemble.

| | avant (`2cc3c1a9a6c9`) | après (`6c9caf8b87a6`) |
|---|---|---|
| conformes 2026 avec bascule | 274 | **262** |
| conformes à la date avec bascule datée | 225 | **219** |
| couverture moyenne du 28 | 88,7 % | **90,1 %** |

**Prévision fausse, corrigée par la mesure** : ce document annonçait 268, en
appliquant le seuil conditionnel de 2,0 NFU à la turbidité. C'est faux —
`depasse_2026` compare à `seuil_2026`, soit **1,0 NFU**, et seul
`depasse_applicable` applique la condition. D'où 262 et non 268, tandis que le
chiffre à la date, 219, était juste. La leçon est celle du §2.13 lui-même :
**l'asymétrie protège le verdict daté, pas les deux contrefactuels.**

Ce n'est pas un argument contre les six lignes : c'est la démonstration qu'un
« conforme » dépend de la grille qu'on lui applique, y compris de la nôtre. Et
la phrase de sortie doit dire que ces six-là sont des **références** de qualité,
dont le franchissement n'est pas une non-conformité sanitaire (§2.1, §11.3) :
sur les 876 dépassements applicables du 28, **575 portent sur une limite**.

---

## 5. Ce qui reste à instruire, sans bloquer

- **PFAS individuels** — 16 libellés, 302 mesures chacun, 186 communes ;
  quantifiés : PFBA (41), PFPeA (39), PFHxA (39), PFHpA (17), PFBS (11),
  PFPS (1), maximum 0,026 µg/L. Il n'y a **pas** de limite individuelle à leur
  chercher : la limite porte sur la somme, qui est mesurée à part et appariée.
  La question utile est l'inverse — **ces individus sont-ils dans le périmètre
  de la somme déclarée ?** À lire dans REG-03. Un individu quantifié hors somme
  serait une information.
- **Acides haloacétiques** — 5 libellés, 97 mesures chacun, 92 communes,
  157 quantifications, maximum 11,9 µg/L (acide trichloroacétique). Aucun seuil
  au référentiel, aucune référence déclarée.
- **Trichlorofluorométhane** — 12 quantifications, **maximum 160 µg/L**, la plus
  haute valeur du corpus sans aucune comparaison. Les 46 autres libellés COV
  totalisent 121 quantifications, toutes sous 8 µg/L.
- **Radiologique** — activité alpha globale, bêta globale, bêta résiduelle, bêta
  attribuable au K40 : 4 libellés, 10 193 mesures, 5 837 quantifications,
  ~280 communes, **11 % des mesures réellement sans comparaison**. Le §11 a
  apparié le radon, le tritium et la dose indicative ; **ces quatre-là restent
  hors grille**. La phrase du §11.1 — « le volet radiologique cesse d'être
  l'angle mort » — vaut pour les paramètres appariés, pas pour les activités
  globales.

## 6. Ce qui ne demande rien

- **PCB** — 18 libellés, 17 341 mesures, **zéro quantification**. À re-regarder
  si une quantification apparaît.
- **Physico-chimie d'équilibre et organoleptique qualitative** — TH, TAC, pH
  d'équilibre, calcium, hydrogénocarbonates, carbonates, silicates, essai marbre,
  aspect, saveur, odeur, couleur : ces paramètres n'ont pas de seuil sanitaire
  chiffré à leur chercher, et les qualitatifs n'ont pas de valeur numérique.
  **C'est le gros du compte**, et c'est normal.
- **Microbiologie non appariée** — revivifiables à 22 et 36 °C, Legionella,
  Pseudomonas, cryptosporidium, giardia. Les libellés qui portent le verdict
  bactériologique — *Escherichia coli*, entérocoques, *Bactéries coliformes
  /100ml-MS* — sont appariés et produisent 48 dépassements dans le 28.

---

## 7. File d'attente

| # | objet | qui décide | état |
|---|---|---|---|
| 1 | ~~adopter les six lignes du §4.3~~ | Yannick | **fait le 10/08** — version `6c9caf8b87a6`, 262/219 publiés |
| 2 | anthraquinone — une ligne au code 2013 ? avec le contrôle du §11.2 | Yannick | **ouvert, bloquant sur ce paramètre** |
| 3 | archiver le PDF `REG-06` et lever la réserve du §4.2 | à faire | ouvert — la turbidité reste en `a_verifier` |
| 4 | corriger le filtre de `v_parametres_non_apparies` (§1) | le fil qui tient `build_db.py` | ouvert |
| 5 | périmètre de la somme des 20 PFAS | à lire dans REG-03 | ouvert |
| 6 | acides haloacétiques, trichlorofluorométhane | à instruire | ouvert |
| 7 | activités alpha et bêta globales | chantier à part entière | ouvert |
| 8 | turbidité — le code 1295 porte deux objets réglementaires (§4.3) | Yannick | ouvert, non urgent |

## 8. Formulation à tenir dans les sorties

Ni « 157 angles morts », ni « 157 paramètres sans seuil ». La phrase exacte :

> *143 libellés dont aucune mesure n'est comparée à quoi que ce soit — 6,7 % du
> corpus. L'essentiel est de la physico-chimie sans seuil sanitaire ; quatre
> dossiers sont ouverts, et un paramètre, l'anthraquinone, attend une décision
> avant toute publication.*

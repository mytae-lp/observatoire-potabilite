# Méthode — mélange de réseaux et dilution

> Note préalable au chantier **C7 — CAPTAGE** (`docs/CHANTIERS.md`), exigée par
> le même principe que `METHODE_EFFET_COCKTAIL.md` : rien ne se publie sur ce
> sujet avant que la méthode et ses limites soient écrites.
> Version 1 — 8 août 2026. Corpus de référence : 45 bulletins complets,
> 60 communes, 8 départements.

---

## 0. L'hypothèse, et son statut

Formulation de Yannick, 8 août 2026 :

> « si pour une commune on mélange 3 captages alors la moyenne peut être bonne,
> même si un captage est hors caractéristique. Cette hypothèse veut également
> dire que "on injecte des molécules chimiques en moyennant" plutôt que de
> fermer ou traiter un captage ! Je précise, ceci est une hypothèse et non une
> affirmation, il faut investiguer. »

C'est le deuxième axe du projet, posé au §7bis de `CLAUDE.md` sous la formule
**« la dilution tient alors lieu de dépollution »**. Le premier axe — le
réétalonnage — montre une eau qui devient conforme parce que la limite a bougé.
Celui-ci montrerait une eau qui devient conforme parce qu'on l'a mêlée à une
autre. Dans les deux cas, rien n'a été fait à la pollution.

**Statut : hypothèse à instruire.** Ce document ne l'instruit pas. Il établit ce
que la donnée permet d'en voir aujourd'hui, ce qu'elle interdit d'en dire, et il
dénombre le terrain.

Et, comme partout ailleurs : **diluer est légal**. Le mélange de ressources est
une pratique d'exploitation ordinaire et parfois la seule disponible. La
question est posée à la norme — qui note l'eau distribuée et ne demande rien sur
ce qu'on y a mêlé — jamais à l'exploitant qui l'applique (§2.1).

---

## 1. La donnée : un champ, et ce qu'il veut dire

Hub'Eau attache à chaque prélèvement une liste `reseaux`, dont chaque entrée
porte `code`, `nom`, et **parfois** `debit` — une chaîne du type `« 80 % »` :

```json
"code_installation_amont": "081000896",
"nom_installation_amont": "LOUBERS BATESTE",
"reseaux": [{"code": "081000643", "nom": "LOUBERS", "debit": "80 %"}]
```

`hubeau.bulletin_meta` l'aplatit dans les colonnes `codes_reseaux` et
`noms_reseaux` de la table `prelevements`, séparateur `|`, la part restant
collée au nom : `LOUBERS (80 %)`.

### Ce que `debit` signifie, et comment on le sait

**La documentation de l'API ne décrit pas ce champ.** Sa signification est donc
**déduite du corpus**, et non lue dans un texte. Elle est marquée `a_verifier`
au sens du §2.7, et doit le rester tant que la source ne l'écrit pas.

Lecture retenue : **`debit` est la part du débit du réseau (UDI) apportée par
l'installation amont de ce prélèvement.**

Deux réseaux la démontrent en se refermant exactement sur 100 %, à partir de
bulletins distincts, sur des installations distinctes :

| Réseau | Sources | Somme |
|---|---|---|
| LOUBERS (081000643) | LOUBERS BATESTE 80 % + BOUYSSOUNADE 20 % | 100 % |
| VALLEE DU CEROU (081004092) | BOURNAZEL RÉSERVOIR 50 % + TTP MOULIN GALAT 50 % | 100 % |

La lecture concurrente — « part de l'eau de la commune » — est réfutée deux
fois : la commune de Loubers porte 80 % sur un bulletin et 20 % sur l'autre pour
le **même** réseau ; et le traitement du Moulin Galat alimente **quatre** réseaux
à quatre parts différentes (100 %, 100 %, 100 %, 50 %). La part est donc
attachée au couple *(installation, réseau)*, pas à la commune.

**Le critère de mélange est donc une part inférieure à 100 %, jamais le nombre
de réseaux desservis.** Une version antérieure de cette lecture confondait les
deux et prenait le nombre de réseaux pour un indice de mélange. Montech, en
janvier 2026, la réfute : le bulletin porte `FINHAN (UDI) (100 %)|MONTECH (UDI)`
— **une** installation qui alimente **deux** réseaux, chacun en totalité.
L'inverse d'un mélange.

### Trois pièges de lecture, inscrits dans le code

**1. Une part absente n'est pas 100 %.** Le `debit` disparaît quand la source ne
rattache le prélèvement à aucune installation amont : `CHALLET (100 %)` en 2022,
`CHALLET` tout court en 2026, sans que rien n'ait changé au réseau. C'est le
§2.4 transposé au mélange — l'absence d'information n'est pas une information
d'absence. `part_reseau_pct` reste `NULL`, `part_non_attribuee` reste `NULL`,
et `statut_melange` vaut `non_declare` : un **troisième état**, comme
l'indéterminé.

**2. Un réseau peut figurer deux fois dans le même bulletin.** Berchères-Saint-
Germain porte `BERCHERES ST GERMAIN|SECTEUR BERCHERES ST GERMAIN` sous le même
code `028000707` répété. Ce n'est pas un mélange, c'est un doublon de libellé :
le regroupement se fait sur le **code**, et `nb_libelles` le signale.

**3. Deux clés d'installation ne font pas deux sources.** Laparrouquial porte
`081000936 STATION LA MAFRESIE` puis `081004209 STATION DE LA MAFRESIE` : c'est
la même station recodée (constat du chantier C3). D'où la règle : un mélange
n'est **reconstitué** que si **plusieurs** sources déclarent chacune **moins de
100 %**. Une source à 100 % clôt la question, quel que soit le nombre de clés.

---

## 2. Les quatre statuts d'un réseau

`v_melange_reseau` en attribue un et un seul à chaque réseau :

| Statut | Ce qu'il dit | Ce qu'il ne dit pas |
|---|---|---|
| `melange_reconstitue` | plusieurs sources, chacune sous 100 %, dont la somme fait 100 % | que ces sources soient elles-mêmes non mélangées |
| `melange_partiel` | une part au moins est sous 100 %, et le reste vient d'une installation que le corpus ne connaît pas | combien de sources composent ce reste |
| `source_unique_declaree` | une installation déclare alimenter ce réseau à 100 % | qu'il n'y ait pas mélange **en amont**, dans l'installation |
| `non_declare` | aucune part n'est déclarée | rien du tout — ni mélange, ni absence de mélange |

`part_non_attribuee` est le chiffre du chantier : ce qu'un réseau reçoit sans
qu'aucun bulletin ne dise d'où. 75 % pour CHARTRES S1 signifie que trois quarts
de l'eau distribuée viennent d'ailleurs et que **le corpus ne sait pas d'où**.

---

## 3. Le dénombrement — état au 8 août 2026

Sur 45 bulletins complets desservant **42 réseaux** :

| Statut | Réseaux | Communes portant un bulletin |
|---|---|---|
| `source_unique_declaree` | 25 | 25 |
| `non_declare` | 11 | 11 |
| `melange_partiel` | 4 | 5 |
| `melange_reconstitue` | 2 | 5 |

La colonne des communes compte celles qui **portent un bulletin** sur le réseau,
pas celles qu'il dessert : 36 communes du corpus ont un bulletin propre, les 24
autres sont rattachées au réseau d'une voisine et n'apparaissent pas ici.

**Six réseaux sur 42 portent un mélange lisible**, et **18 bulletins sur 45 ne
déclarent aucune part** — pour ceux-là on ignore jusqu'à l'existence du mélange.

Les six :

| Réseau | Ce qu'on sait | Ce qui manque |
|---|---|---|
| CHARTRES S1 | usine de dénitrification 25 % | **75 %** d'origine inconnue |
| FONT POLEMIE | station Font Polémie 50 % | **50 %** d'origine inconnue |
| SYNDICAT VIEUX ITZAC | Itzac Guirbonde 50 % | **50 %** d'origine inconnue |
| LEVES B2 | usine de dénitrification 80 % | **20 %** d'origine inconnue |
| LOUBERS | Bateste 80 % + Bouyssounade 20 % | — |
| VALLEE DU CEROU | Bournazel réservoir 50 % + Moulin Galat 50 % | — |

**L'hypothèse a donc un terrain, et il est petit.** Sur 45 bulletins, deux
réseaux seulement portent un mélange dont toutes les parts sont connues *et*
dont plusieurs sources sont analysées. À cette échelle, aucun motif ne se lit ;
c'est le chantier C6 qui donnera le volume.

---

## 4. La question non tranchée, et elle est centrale

**Où, dans le réseau, le prélèvement a-t-il été fait ?**

Toute la portée de ce chantier en dépend, et la donnée ne le dit pas.
`code_lieu_analyse` vaut `L` sur les 45 bulletins du corpus — une seule valeur,
donc aucune information. L'endpoint est celui de l'eau **distribuée**.

Deux lectures possibles, et elles ne mènent pas au même endroit :

- si le prélèvement est fait **après** le point de mélange, alors un bulletin
  d'un réseau mélangé décrit **déjà la moyenne**. On ne verra jamais le captage
  dégradé, seulement son effet dilué — et l'hypothèse de Yannick est exactement
  celle-là, mais elle devient **indémontrable avec ces seules données** ;
- si le prélèvement est rattaché à son installation amont parce qu'il est fait
  **en amont du mélange**, alors deux bulletins d'un même réseau décrivent deux
  eaux différentes, et la comparaison a un sens.

Le fait que l'ARS attache chaque prélèvement à **une** installation amont
plaide pour la seconde lecture ; ce n'est pas une preuve. **Tant que ce point
n'est pas tranché, aucune conclusion de dilution ne doit être publiée** — la
comparaison entre sources reste un matériau d'étude.

Ce qu'il faudrait pour trancher : la nomenclature SISE-Eaux du lieu d'analyse,
ou une réponse de l'ARS. Aucune des deux n'est dans le dépôt.

---

## 5. Ce que le dénombrement ne voit pas, par construction

**Le mélange à l'intérieur d'une installation.** Une usine alimentée par trois
captages dont un seul est dégradé apparaît ici comme une `source_unique_declaree`
à 100 %. La dilution y est faite **en amont du seul point que la donnée expose**.
C'est très exactement le cas décrit par Yannick — « si pour une commune on
mélange 3 captages » — et c'est celui que ces vues **ne peuvent pas voir**.

Le maillon manquant est connu et documenté au §7bis :

| Maillon | Source | État |
|---|---|---|
| l'eau au robinet (le mélange) | `qualite_eau_potable/resultats_dis` | branché |
| les captages AEP et leur position | BNPE, `points_prelevement` | disponible, jamais collecté |
| la qualité de l'eau **brute** | `qualite_nappes`, `qualite_rivieres` | disponible, jamais collecté |
| **quel captage alimente quelle installation** | — | **non exposé** |

Le lien captage → installation ne pourra être établi que par **inférence
géographique**. Règle, posée dès maintenant : il devra être **affiché comme une
hypothèse, jamais comme un fait**, et toute sortie qui l'emploie devra dire sur
quoi l'inférence repose (distance, bassin, code BSS) et ce qu'elle peut manquer.

---

## 6. Comparer deux sources d'un même réseau : ce qui est permis

`melange_sources.csv` met côte à côte, pour un réseau mélangé, ce que chaque
source analysée apporte. Quatre règles, non négociables :

1. **L'effort de recherche de chaque terme est affiché** (§2.11). Deux bulletins
   qui ne cherchent pas le même nombre de paramètres n'ont pas la même chance de
   trouver ; comparer leurs comptes bruts est un contresens. Les colonnes
   exportées sont des **taux** — `depassements_pour_mille` — et le nombre de
   paramètres cherchés les accompagne toujours.
2. **Les dates sont affichées.** Deux sources analysées à sept mois d'intervalle
   ne décrivent pas le même instant, et un verdict se rend à la date du
   prélèvement (§2.10). Les parts elles-mêmes peuvent avoir bougé entre les deux.
3. **Un écart entre deux sources n'est pas une preuve de dilution.** Il rend
   l'hypothèse instruisible ; il ne la démontre pas.
4. **Aucune recommandation, d'aucune sorte** (§2.2). Le sujet est la norme, pas
   ce que quiconque devrait faire de son eau.

### Le premier cas que le corpus fait remonter — et pourquoi il n'en est pas un

VALLEE DU CEROU, mélange 50/50, quatre communes : le bulletin du Moulin Galat
(15 décembre 2025) porte un dépassement applicable, celui de Bournazel Réservoir
(24 novembre 2025) n'en porte aucun.

**Ce n'est pas un cas de dilution.** Le dépassement est *Escherichia coli*, à
1 pour 100 mL — un événement **bactériologique**, ponctuel, et l'ARS a bien
prononcé la non-conformité (`conf_limites_bact = 'N'`). Une bactérie ne se
« moyenne » pas comme une molécule : le raisonnement de dilution ne s'y applique
pas, et l'appliquer ici serait la première erreur à commettre.

Le corpus dit donc, pour l'instant : le mécanisme est lisible sur deux réseaux,
et aucun des deux ne montre encore ce qu'on cherche. C'est un résultat, et il
vaut d'être écrit tel quel.

---

## 7. Ce qui est construit

| Objet | Rôle |
|---|---|
| `v_reseau_bulletin` | la décomposition : une ligne par (bulletin × réseau desservi), part lue |
| `v_reseaux_illisibles` | contrôle : les prélèvements dont les listes codes/noms ne s'apparient pas — doit rester vide |
| `v_melange_bulletin` | par bulletin : combien de réseaux, à quelle part, mélange lisible ou non |
| `v_melange_reseau` | par réseau : sources connues, somme des parts, part non attribuée, statut |
| `src/etude_melange.py` | le dénombrement et trois exports dans `data/etudes/` |

Rien de tout cela n'est publié : ni la vitrine, ni la fiche ne lisent ces vues.
C'est un matériau d'étude, au même titre que `etude_panel.py`, et il le restera
tant que la question du §4 n'est pas tranchée.

---

## 8. Ce qu'il ne faut jamais écrire à partir de ces vues

- « cette eau est diluée pour rester conforme » — non démontré, et §4 ;
- « ce captage pollue le réseau » — le corpus voit des installations, pas des
  captages, et ne met en cause personne (§2.1) ;
- « ce réseau n'a qu'une source » à partir d'un `non_declare` — c'est un
  troisième état, pas un « non » ;
- toute recommandation, à qui que ce soit (§2.2).

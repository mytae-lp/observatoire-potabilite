# Chantiers d'améliorations

Ce fichier est le **carnet de commande** du projet. Yannick y dépose les
chantiers ; ils sont ensuite lancés, éventuellement en parallèle. Il ne
remplace ni `CLAUDE.md`, qui porte la méthode et les garde-fous, ni
`docs/REPRISE.md`, qui décrit l'état du dépôt à un instant donné.

Un chantier n'entre ici qu'avec **ce que Yannick demande**, **ce que les
données permettent réellement** (vérifié, daté), **le piège méthodologique**
qu'il faut éviter en le réalisant, et **ce qui reste à décider**. Un chantier
dont on ne sait pas encore s'il est faisable le dit.

Ouvert le 8 août 2026.

---

## L'index — un code, un nom, une phrase

Chaque chantier porte un **code court**. C'est lui qu'on nomme pour en lancer
un, ici ou dans une autre session.

| Code | Nom court | En une phrase | Statut |
|---|---|---|---|
| **C1** | FILTRATION | ce qu'un type de filtre retient, et ce qu'il ne retient pas | **gelé** — on ne touche à rien |
| **C2** | PANEL | quels paramètres on a cessé de chercher | **premier livrable posé** |
| **C3** | ÉVOLUTION | comparer les bulletins successifs d'un même point d'eau | en attente de C7 |
| **C4** | LQ | la finesse du laboratoire, et le biais qu'elle crée entre communes | **fait**, règle inscrite au §8bis |
| **C5** | TERRITOIRES | ne comparer qu'à des zones nommées, dont on a les données | **fait**, règle inscrite au §2.11 |
| **C6** | ÉCHELLE | passer de 60 à plusieurs milliers de communes | décidé, non planifié |
| **C7** | CAPTAGE | la dilution comme mode de gestion — hypothèse à instruire | **premier livrable posé** |
| **C8** | ATELIER | comprendre et fiabiliser le back-office | **prêt à lancer** |

### Lancer un chantier dans une autre session

Une phrase suffit, le carnet porte le reste :

> Lis `docs/CHANTIERS.md` et prends le chantier **C4 — LQ**. Applique
> `CLAUDE.md`. Ne touche à aucun autre chantier.

### Travailler en parallèle sans se marcher dessus

Les chantiers ont été découpés pour toucher des fichiers différents. Ce
tableau dit qui écrit où — à relire avant d'en lancer deux ensemble.

| Chantier | Écrit principalement dans | Croise |
|---|---|---|
| C2 PANEL | `src/build_db.py` (vues), `src/etude_panel.py` | — |
| C4 LQ | `sortie/indicateurs.py`, `sortie/rediger.py`, `src/figer.py` | C5 sur `rediger.py` |
| C5 TERRITOIRES | `sortie/redactions.json`, `tests/test_sorties.py` (contrôle 8), `CLAUDE.md` §2.11 | C4, C8 |
| C7 CAPTAGE | `src/build_db.py` (vues de mélange), `src/etude_melange.py`, `docs/METHODE_DILUTION.md` | C3 ; **C2 sur `build_db.py`** |
| C8 ATELIER | `atelier/atelier.py`, `tests/` | tous, en lecture |

Trois règles pour que ça tienne :

1. **`CLAUDE.md` ne se modifie que sur instruction de Yannick.** Un chantier
   qui a besoin d'y toucher le signale et attend.
2. **Ce fichier-ci est partagé.** Une session n'écrit que dans la section de
   SON chantier, plus une ligne au Journal en fin de course.
3. **Les trois suites de tests se lancent avant de rendre la main.** Elles sont
   le seul point de rendez-vous entre des sessions qui ne se parlent pas.

---

## C1 — FILTRATION

### Ce qu'un type de filtre retient, et la question « qu'est-ce que j'en fais ? »

### Ce que Yannick demande

> « solutions de filtrations, non pas un produit mais un type, on sait que le
> charbon actif retient les chaînes longues de PFAS mais très mal les chaînes
> courtes. On sait qu'une substance qui fait une certaine taille ne sera
> retenue que par certains types de filtration. »

Et la raison, qui est le cœur du chantier :

> « ton site il nous alerte, mais il peut créer une panique car on ne sait pas
> quoi faire de ces informations »

C'est un retour de lecteur, pas une intuition. Il désigne un manque réel : un
outil qui documente sans jamais ouvrir de suite laisse le lecteur avec une
inquiétude et aucune prise.

### Ce que cela touche

**Le §2.2 tel qu'il est écrit interdit ce chantier.** Il ne dit pas « pas de
marque » : il dit « aucune recommandation de filtration, d'osmoseur, de charbon
actif […] ni d'aucun équipement, jamais. Pas même en note de bas de page ». Le
chantier ne peut donc pas être mené par exception — il demande une **révision
écrite du §2.2**, comme le §8quater a été révisé le 8 août 2026 quand la règle
« la prose n'est jamais générée » a cessé de tenir.

La distinction que Yannick pose — **un type, pas un produit** — est exactement
ce qui rend une révision possible. « Le charbon actif retient mal les chaînes
courtes » est un fait de physico-chimie, vérifiable et sourçable. « Achetez tel
filtre » est un argumentaire commercial. Le §2.2 protégeait contre le second ;
il interdit aujourd'hui le premier par la même phrase.

Ce que la révision devra dire explicitement, sans quoi la porte s'ouvre trop
grand : pas de marque, pas de modèle, pas de prix, pas de fournisseur, pas de
lien d'achat, et jamais de conseil individuel du type « pour votre eau,
prenez… ». La frontière tient si l'objet décrit reste **une famille de
procédés et ce qu'elle retient**, jamais une chose qu'on achète.

### La forme qui respecterait la colonne vertébrale du projet

Le projet ne dit rien qui ne soit sourcé et daté (§2.7). Un chantier
« filtration » ne peut donc pas vivre dans de la prose : il lui faut sa table
versionnée, sur le modèle de `referentiel_seuils.csv` —

```
referentiel/retention_procedes.csv
  procede ; famille_substance ; taille_ou_propriete ; retention ;
  sources ; fiabilite
```

— avec la même règle qu'au §2.7 : **la source doit couvrir CE couple
procédé × substance précisément**. C'est le piège du chlorothalonil R417888
transposé : « le charbon actif retient les PFAS » étendu par analogie aux
chaînes courtes serait faux, et c'est précisément l'exemple que Yannick cite.

### Le cas Vourles, en attendant

La phrase « précisément celles que le charbon actif retient mal » est
aujourd'hui le seul point signalé par `tests/test_sorties.py`. Yannick :

> « je n'en suis pas certain »

**Décision : on ne la supprime pas, on ne la valide pas.** Elle reste en l'état,
signalée et non bloquante, jusqu'à ce que le §2.2 soit tranché. Si la révision
a lieu, la phrase devient conforme et le signalement tombe de lui-même ; si
elle n'a pas lieu, la phrase se retire en une ligne. Rien ne presse, et rien ne
se perd.

### Décision du 8 août 2026 — gelé

> « on fera une révision du §2.2 le moment voulu. Pour l'instant on touche pas. »

Rien ne bouge : ni le §2.2, ni la phrase de Vourles, ni le contrôle qui la
signale. Le chantier reste écrit ici pour qu'il soit repris tel quel le jour
venu, avec sa raison — le retour de lecteur — qui est le vrai déclencheur.

### Reste à décider, le moment venu

Le périmètre exact de la révision du §2.2, et si ce volet vit sur le site ou
seulement dans le livre — Yannick indique qu'il est lié aux deux.

---

## C2 — PANEL

### Les paramètres qu'on ne cherche plus

### Ce que Yannick demande

> « quand en 2018 on cherche 650 paramètres et qu'en 2026 on en recherche plus
> que 300, je veux connaître lesquels on ne recherche plus. Ainsi sur plusieurs
> centaines de communes on pourra peut-être trouver une direction commune et
> pousser une recherche sur les valeurs que l'on ne recherche plus et les lier
> potentiellement à des scandales ou à des recherches récentes. »

C'est le §2.11 poussé d'un cran : l'effort de recherche n'est pas seulement un
nombre, c'est une **liste**, et ce qui en sort est une décision que personne
n'annonce.

### Ce que les données permettent — vérifié le 8 août 2026

Faisable directement, sans collecte supplémentaire : la table `mesures` porte
un `libelle_parametre` et un `code_parametre` par prélèvement, et la différence
ensembliste entre deux bulletins se calcule en SQL.

Essai sur Boissezon, bulletin de juillet 2019 contre celui de juillet 2024 :

| | |
|---|---|
| paramètres présents en 2019, absents en 2024 | **299** |
| paramètres apparus en 2024 | **41** |
| exemples abandonnés | Picolinafen, Chinométhionate, Cycloate, PCB 153, Méthoxychlore, Flupyrsulfuron-méthyle, Hepténophos, Chloroneb |

299 sur 627, ce n'est pas un ajustement, c'est un changement de panel. Et
l'intérêt du chantier apparaît déjà dans cette liste : le méthoxychlore et le
PCB 153 sont des molécules anciennes et interdites, dont l'abandon se comprend
— mais c'est une hypothèse, pas une lecture. Seule l'agrégation sur des
centaines de communes dira si le retrait suit une logique nationale, un
laboratoire, ou une date d'arrêté.

### Le piège

**Ne pas confondre « plus cherché » avec « retiré du contrôle ».** Un paramètre
absent d'un bulletin peut l'être parce que le programme réglementaire a changé,
parce que le laboratoire a changé, ou parce que ce bulletin-là relevait d'un
autre type de contrôle. Le premier livrable du chantier est donc un
**dénombrement**, sans interprétation — indicateur A de la note de méthode, le
plus solide, avant tout ce qui suit.

Et l'unité de comparaison est le sujet du chantier C3 ci-dessous : comparer deux
bulletins de points d'eau différents mélange la dérive du panel et la
différence entre deux installations.

### Ce qui a été construit — 8 août 2026

Lancé sur instruction de Yannick. Quatre vues dans `src/build_db.py`, un
script d'export, huit contrôles de non-régression.

| Vue | Ce qu'elle porte |
|---|---|
| `v_panel_bulletin` | le panel de chaque bulletin complet |
| `v_panel_evolution` | la comparaison de deux bulletins consécutifs d'une commune |
| `v_parametres_abandonnes` | ce qui disparaît, et chez combien de communes |
| `v_parametre_presence` | la part des bulletins qui cherchent un paramètre, année par année |
| `v_parametre_presence_dept` | la même, par département — le contre-feu (ajoutée le 8 août 2026) |

```bash
py -X utf8 src/etude_panel.py
```

Cinq fichiers dans `data/etudes/`, non versionnés comme toute donnée dérivée.
C'est un matériau d'étude, pas une sortie publique : il ne dit rien de la
qualité de l'eau, il décrit ce qu'on a choisi d'en savoir.

**La quatrième vue est celle qui portera le chantier à l'échelle.** Elle
n'apparie rien : elle regarde une population et donne, pour chaque paramètre et
chaque année, la part des bulletins complets qui l'ont cherché. Un paramètre qui
passe de 90 % à 5 % en deux ans a été retiré des programmes, et aucune commune
n'a eu à le décider.

Deux points de méthode inscrits dans le code :

- la clé d'identité d'un paramètre est `code_parametre` quand la source le donne
  (15 613 mesures sur 15 617), sinon le libellé normalisé. Le code seul perdrait
  quatre mesures, le libellé seul éclaterait un paramètre renommé ;
- le nom de réseau porte sa part de mélange — « JOUY (100 %) » en 2025, « JOUY »
  en 2026. Sans nettoyage, toute comparaison d'une année sur l'autre croirait
  qu'il s'agit de deux réseaux.

### Ce que le corpus dit déjà — 45 bulletins, 9 paires

| Commune | Période | Panel | Abandonnés | Nouveaux | Point d'eau |
|---|---|---|---|---|---|
| Boissezon | 2019 → 2024 | 627 → 369 | **298** | 40 | différent |
| Challet | 2022 → 2026 | 359 → 234 | **145** | 20 | présumé le même |
| Laparrouquial | 2020 → 2025 | 366 → 391 | 9 | 34 | différent |
| Jouy | 2025 → 2026 | 291 → 314 | 7 | 30 | présumé le même |
| Loubers | 2025 → 2025 | 370 → 363 | 7 | 0 | différent |
| Montech | 2025 → 2026 | 374 → 388 | 6 | 20 | différent |
| Bailleau-l'Évêque | 2025 → 2026 | 289 → 315 | 4 | 30 | présumé le même |
| Souel | 2025 → 2026 | 311 → 313 | 0 | 2 | présumé le même |
| Boissezon | 2024 → 2024 | 369 → 369 | 0 | 0 | différent |

423 paramètres distincts ont été abandonnés au moins une fois. Et un signal
apparaît **déjà**, sur un corpus pourtant minuscule : **l'odeur** est cherchée
sur 85,7 % des bulletins en 2022, 100 % en 2024, 89,5 % en 2025 — et **7,7 % en
2026**, soit un bulletin sur treize. Un paramètre organoleptique retiré presque
partout la même année, dans quatre communes de trois départements. C'est le
genre de motif que Yannick cherche ; à cette échelle, ce n'est encore qu'une
piste.

Une nuance de lecture, sans conséquence mais à connaître : le nombre de
paramètres **distincts** peut différer du `nb_parametres` déclaré. Quatre
couples du corpus portent la même substance deux ou trois fois sur le même
bulletin — microcystines à Montech, essai marbre à Rostrenen. Écart maximal :
6 paramètres, sur un seul bulletin.

### Deux défauts du détecteur, trouvés et corrigés — 8 août 2026

La reprise du chantier a commencé par une vérification de ce qui était livré.
La machinerie tournait, ses chiffres étaient justes, et **la vue qui devait
porter le chantier à l'échelle ne savait pas dire l'essentiel.**

**1. Le zéro n'existait pas.** `v_parametre_presence` ne produisait de ligne que
pour les couples (année, paramètre) effectivement cherchés. Un paramètre tombé à
0 % n'avait donc plus de ligne du tout : le détecteur était aveugle au seul cas
qui l'intéresse vraiment — l'abandon complet. Une absence de ligne ne se
distingue pas d'une année non documentée. C'est le §2.4 transposé du laboratoire
au programme d'analyse : l'absence de trace n'est pas l'absence de fait, et elle
doit s'écrire. La vue porte désormais la grille pleine, à 0 % avec son
dénominateur.

Le contrôle de non-régression **affirmait le défaut** : « un paramètre qu'on ne
cherche plus n'a plus de ligne l'année suivante ». Il est retourné. C'est la
leçon du chantier C8 rencontrée ici : un test peut verrouiller un angle mort
aussi sûrement qu'il en protège.

**2. Une chute nationale n'était pas contrôlable.** Le corpus change de
composition d'une année sur l'autre — 7 bulletins sur 2 départements en 2022,
13 sur 6 en 2026. Un paramètre qui ne serait qu'une habitude du Tarn passerait
mécaniquement de 100 % à 20 % sans avoir été retiré nulle part. La vue ne
permettait pas de faire la différence, et c'est exactement le piège du chantier
— « plus cherché » ≠ « retiré du contrôle » — remonté d'un cran, de la commune
au corpus.

D'où `v_parametre_presence_dept`, et deux contrôles affichés sous chaque chute.
Le corpus ne porte pas le laboratoire : `code_lieu_analyse` vaut « L » sur les
45 bulletins. Le département est donc la strate la plus fine disponible pour
approcher les trois hypothèses du chantier — une logique nationale, un
laboratoire, une date d'arrêté — et il se lit comme un proxy, pas comme une
explication.

### Ce que le contrôle dit de l'odeur — il la renforce

Le premier usage des deux contrôles porte sur le seul signal du corpus, et il
aurait pu le démolir. Il fait l'inverse :

| Contrôle | Ce qu'il donne |
|---|---|
| **corpus** | 0 % dans **3 des 4** départements documentés en 2026 qui l'avaient cherchée — 28, 81, 82. Le seul qui la cherche encore (69) n'entre au corpus qu'en 2026 |
| **communes suivies** | abandonnée sur **4 des 9** paires de bulletins consécutifs, dans 4 communes — Bailleau-l'Évêque, Challet, Jouy, Montech |

Deux lectures indépendantes qui concordent : la chute se produit **à
l'intérieur** des départements qui cherchaient l'odeur, et sur des communes
qu'on suit d'un bulletin au suivant. Ce n'est donc pas un effet de composition
du corpus. Cela reste 45 bulletins, et donc une piste — mais une piste qui a
passé le contrôle qui aurait dû la tuer.

### Reste à faire

Rien avant le chantier C6. La machinerie est prête et attend le volume ; sur
9 paires, chercher une direction commune serait de la lecture de marc de café.

Ce qui a changé le 8 août 2026, c'est qu'elle est prête **à dire un zéro et à
contrôler une chute**. Les deux défauts corrigés ne se voyaient pas sur 45
bulletins et auraient produit, sur plusieurs milliers, une lecture fausse dans
les deux sens : des abandons complets invisibles, et des chutes de corpus prises
pour des retraits nationaux.

Une note pour le jour du volume : la strate départementale est un proxy. Si la
collecte à l'échelle expose un jour un identifiant de laboratoire, c'est lui qui
devra porter le contrôle — le carnet nomme le laboratoire parmi les trois
hypothèses, et les données ne permettent pas encore de la trancher.

---

## C3 — ÉVOLUTION

### Comparer les bulletins successifs d'une même commune

### Ce que Yannick demande

> « lorsque plusieurs analyses sont faites sur une même commune (comme Montech)
> je veux sur la plus récente également une évolution entre les X analyses.
> Cela permet de parler de dégradation ou d'améliorations. »

### Ce que les données permettent — vérifié le 8 août 2026

Huit communes du corpus portent plus d'un bulletin complet :

| Commune | Bulletins | Période | Paramètres |
|---|---|---|---|
| Boissezon (81) | 3 | 2019 → 2024 | 627 → 369 |
| Bailleau-l'Évêque (28) | 2 | 2025 → 2026 | 289 → 315 |
| Challet (28) | 2 | 2022 → 2026 | 359 → 234 |
| Jouy (28) | 2 | 2025 → 2026 | 291 → 314 |
| Laparrouquial (81) | 2 | 2020 → 2025 | 366 → 391 |
| Loubers (81) | 2 | 2025 → 2025 | 370 → 363 |
| Montech (82) | 2 | 2025 → 2026 | 380 → 388 |
| Souel (81) | 2 | 2025 → 2026 | 311 → 313 |

### Le piège, et il est sérieux

**Aucune de ces paires ne partage un `code_installation_amont`.** Vérifié :
zéro installation du corpus porte deux bulletins complets. En regardant les
noms, deux situations très différentes se cachent derrière ce zéro :

- **le même point d'eau, recodé ou non renseigné.** Laparrouquial :
  `081000936 STATION LA MAFRESIE` puis `081004209 STATION DE LA MAFRESIE` —
  même station, code changé. Challet, Jouy, Souel, Bailleau : le code est
  **vide** sur le bulletin récent, mais le réseau est identique ;
- **des points d'eau réellement différents.** Montech : `STATION DE MONTECH`
  puis `MONTECH (UDI)`. Loubers : deux captages qui alimentent la commune à
  80 % et 20 %. Boissezon : **trois captages distincts** — LE LINAS (2019),
  LABRO et LA PEYRARQUE (2024).

Conséquence directe, et elle touche un texte déjà publié : la section
« 627 paramètres en 2019, 369 en 2024 » de Boissezon compare le captage du
Linas à celui de La Peyrarque. La phrase reste vraie au niveau de la
**commune** — c'est bien l'effort consenti sur ce territoire qui a baissé —
mais elle ne décrit pas la même eau suivie dans le temps, et le texte ne le
dit pas. **À reprendre quand le chantier sera fait.**

Le §2.3 est formel : l'unité est le point d'eau, pas la commune. Une courbe
d'évolution qui enjambe deux captages fabriquerait exactement l'objet que le
projet s'interdit — un profil synthétique sans lieu réel.

### La règle à tenir

1. Identifier le point d'eau par le **réseau et le nom d'installation**, pas
   par `code_installation_amont` seul : il est vide sur les bulletins récents
   et il est recodé d'une année à l'autre.
2. Deux bulletins du **même** point d'eau : évolution légitime, on peut parler
   de dégradation ou d'amélioration.
3. Deux bulletins de points d'eau **différents** : on le dit, et on parle
   d'écart entre deux ressources, jamais d'évolution dans le temps.
4. Dans les deux cas, l'effort de recherche de chaque bulletin est affiché à
   côté (§2.11) : entre 234 et 359 paramètres, une variation du nombre de
   dépassements ne veut rien dire sans son dénominateur.

### Ce que ça produit

Un bloc sur la fiche du bulletin le plus récent, montrant les bulletins
antérieurs du même point d'eau : effort, couverture, dépassements pour mille,
bascules, et les paramètres apparus ou disparus (chantier C2). Rien qui ne se
déduise des tables figées.

---

## C4 — LQ

### Le plafond analytique : la limite de quantification comme limite de ce qu'on peut dire

### Ce que Yannick demande

À propos de Pont-de-Larn (81) :

> « Je veux que l'on rajoute en rouge cette mention : le seuil du laboratoire
> ne permet pas du tout de quantifier ce qui est en dessous de cette limite.
> C'est une donnée importante, car là aussi, si je compare avec une autre
> commune dont les limites du laboratoire sont beaucoup plus faibles, la
> comparaison des deux est biaisée. »

### Ce que les données permettent — vérifié le 8 août 2026

C'est massif, et la démonstration tient sur une seule molécule. Limites de
quantification relevées pour l'**hydrazide maléique**, dont la limite déclarée
est 0,1 µg/L :

| LQ du laboratoire | Où | Nombre de mesures |
|---|---|---|
| 0,05 µg/L | 22 (Rostrenen), 81, 82 | 5 |
| 0,1 µg/L | 17 | 1 |
| **0,5 µg/L** | 46, **81** | 22 |
| **2,5 µg/L** | 81 | 1 |

Un facteur **50** entre la meilleure et la pire, pour la même substance. Et le
Tarn porte à lui seul les trois valeurs : ce n'est donc pas une caractéristique
de département, c'est celle d'un laboratoire ou d'une campagne. La formulation
actuelle de la fiche de Pont-de-Larn — « c'est une caractéristique du
laboratoire, pas du territoire » — est juste ; il lui manque le chiffre.

À 0,5 µg/L de LQ contre 0,1 de limite, le laboratoire ne peut **rien** dire de
la zone où se joue la conformité. Le « non quantifié » de Pont-de-Larn et celui
de Rostrenen portent le même mot et pas la même information.

Plus largement : **55 mesures du corpus** sont non quantifiées avec une LQ
supérieure au seuil strict de comparaison. C'est le §2.4 — l'indéterminé — mais
vu par le bout de l'instrument.

### Proposition — trois niveaux, pas un seul barème

Yannick demande :

> « est-ce que l'on rajoute sur la fiche une mention ou un barème qui dit où se
> situe la finesse de quantification. Par exemple entre le plus fin et le plus
> grossier, cette commune se situe ici, avec un texte qui explique à quoi ça
> correspond, et on y rajoute une note dans la rédaction de l'analyse. »

Le barème est le bon geste, mais **une jauge unique par commune serait fausse**.
La finesse n'est pas une propriété du bulletin : elle est propre à chaque
paramètre. Un laboratoire peut descendre à 4 ng/L sur les PFAS et rester à
0,5 µg/L sur l'hydrazide maléique. Moyenner les deux produirait un score qui ne
correspond à rien de mesurable — exactement le profil synthétique que le §2.3
interdit, transposé à l'instrument.

D'où trois niveaux, du plus sûr au plus synthétique. Les deux premiers sont
solides et peuvent partir tout de suite ; le troisième est celui que Yannick
décrit, et il demande un arbitrage.

**1. La mention rouge, au paramètre.** Partout où la LQ dépasse le seuil auquel
on compare, la ligne le dit, avec le rapport :

> **LQ 0,5 µg/L, soit 5 × la limite de 0,1.** Sous cette valeur, l'analyse ne
> voit rien : on ne peut pas dire que l'eau respecte la limite, seulement qu'on
> ne sait pas.

C'est le §2.4 vu par le bout de l'instrument, et c'est vrai sans aucune
convention. À inscrire comme **onzième obligation d'affichage** du §8bis.

**2. Le taux, au bulletin.** Combien de paramètres cherchés sont dans ce cas,
rapporté au nombre de paramètres notés — un **taux**, seul comparable d'un
bulletin à l'autre (§2.11). C'est le pendant analytique de
`depassements_pour_mille`, et il conditionne toute comparaison entre communes au
même titre que l'effort de recherche. Nom proposé : `aveugles_pour_mille`, et en
clair sur la fiche : « la part de l'analyse qui ne peut pas conclure ».

**3. Le barème, et sa condition.** Situer une commune entre le plus fin et le
plus grossier n'a de sens qu'**à paramètre constant** :

> Hydrazide maléique — LQ observées dans le corpus : de 0,05 à 2,5 µg/L.
> Ici : **0,5 µg/L**. Dix fois moins fin que le meilleur relevé, cinq fois
> au-dessus de la limite à laquelle on compare.

Trois réserves, qui sont le prix de cet affichage :

- **la référence bouge avec le corpus.** « Le plus fin » sur 45 bulletins n'est
  pas celui sur 4 000. Le barème doit donc afficher sa base — « sur 45 bulletins,
  8 départements » — et être figé avec sa version, comme tout le reste. C'est le
  §2.14 transposé : le plus fin **identifié**, jamais le plus fin qui existe ;
- **un barème par paramètre ne tient pas sur une fiche** — 350 paramètres.
  Il ne s'affiche donc que là où il mord : sur les paramètres dont la LQ
  dépasse le seuil, c'est-à-dire ceux du niveau 1 ;
- **une LQ élevée n'est pas une négligence.** C'est une capacité d'instrument.
  Le §2.1 vaut ici comme ailleurs : on examine ce que le dispositif permet de
  savoir, on n'accuse pas le laboratoire — pas plus qu'on n'accuse l'exploitant.

**4. La note dans la rédaction.** `rediger.py` ajoute une section dérivée quand
le bulletin porte des paramètres aveugles, sur le modèle de ce qui existe déjà
pour les indéterminés. Origine `derive`, donc elle bouge si la donnée bouge.

### L'arbitrage, rendu le 8 août 2026

**Le niveau 3 est affiché, avec sa base.** Chaque barème porte le nombre de
bulletins et de départements sur lesquels il est calculé, et il est figé avec
sa version — le plus fin *identifié*, jamais le plus fin qui existe.

**Le compteur reste séparé.** `nb_aveugles` vit à côté de `nb_indetermines`,
qui ne bouge pas : aucun chiffre déjà publié ne change en silence, et les deux
faits restent distinguables. « On ne sait pas si le repère danois est tenu » et
« on ne sait pas si la limite française est tenue » ne sont pas la même
information — la seconde est plus grave.

### Le piège

Ne pas transformer une LQ élevée en soupçon. Une LQ est une capacité
d'instrument, pas une négligence, et le §2.1 vaut ici comme ailleurs : on
examine ce que le dispositif permet de savoir, on n'accuse pas le laboratoire.

### Ce qui a été construit — 8 août 2026

Les quatre niveaux, plus une garde que le carnet n'avait pas vue.

| Où | Quoi |
|---|---|
| `verdicts_figes.lq_aveugle`, `lq_rapport_seuil` | niveau 1 — au paramètre, avec le rapport |
| `analyses_figees.nb_aveugles`, `aveugles_pour_mille` | niveau 2 — le taux au bulletin |
| table `lq_corpus` | niveau 3 — l'étendue des LQ observées, par paramètre, estampillée |
| `sortie/rediger.py` | niveau 4 — la section dérivée « Ce que le laboratoire ne pouvait pas voir » |

Le calcul vit dans `src/figer.py` et non dans une vue de `build_db.py` : c'est
déjà là que sont calculés les indicateurs dérivés du bulletin (sommes, indice
de danger), et le chantier C2 travaillait sur `build_db.py` au même moment.

Sur la fiche : la mention en rouge sur la ligne du bulletin, l'état
« LQ au-dessus du seuil » — de la famille du gris, qui est la couleur du
troisième état, seule la mention étant rouge —, la tuile de taux dans « ce que
vaut cette lecture », et le bloc à barème logarithmique. `lq_corpus.csv` rejoint
les exports téléchargeables : une fiche qui affirme « dix fois moins fin que la
plus basse relevée » doit rendre la table qui le dit.

**Une garde qu'il fallait poser : `seuil > 0`.** Appliquée telle quelle, la
règle « LQ au-dessus du seuil » attrapait **69 mesures de bactériologie** —
entérocoques et *E. coli*, dont la limite de qualité est zéro et dont la « LQ »
d'un dénombrement vaut 1, puisqu'on ne compte pas une demi-bactérie. Aucune LQ
ne peut passer sous zéro. Sans cette condition, 69 faux positifs noyaient les
46 cas réels. Le contre-exemple est au test.

### Ce que le corpus dit — 45 bulletins

**46 mesures aveugles sur 39 bulletins**, jusqu'à 8,44 pour mille des paramètres
notés, sur 8 substances : hydrazide maléique (23), éthylènethiourée (9),
dichloropropylène-1,3 trans (5), diquat (4), 2,4-dinitrophénol (2),
dichloropropane-1,2, bromométhane, quinmérac.

Pont-de-Larn, le cas de départ, dit désormais : *« LQ 0,5 µg/L, soit 5 × la
limite de 0,1 »*, et *« de 0,05 à 2,5 µg/L sur 29 bulletins et 5 départements —
celle-ci en est dix fois moins fine que la plus basse relevée »*.

**Les 46 aveugles sont TOUS parmi les 55 indéterminés.** Ce n'est pas une
identité de principe — un paramètre sans repère strict pourrait être aveugle
sans être indéterminé — mais c'est le fait, et il a une conséquence de
rédaction : les additionner annoncerait 101 problèmes là où il y en a 55. La
prose compte donc le recouvrement au lieu de le supposer, et la section
« ce que ce bulletin ne permet pas de dire » ne redit plus ce que la nouvelle
section dit mieux.

### La règle est écrite — 8 août 2026

**Onzième obligation d'affichage du §8bis**, inscrite sur instruction de
Yannick. Elle porte les trois choses qui ne se déduisent pas du code : que la
mention se **chiffre**, qu'un **seuil de zéro ne se perce pas par le bas**, et
qu'une LQ élevée est une **capacité d'instrument** — donc que rien de tout cela
ne met en cause un laboratoire (§2.1), et que la base d'un classement s'affiche
avec lui (§2.14).

Écrite deux fois, et il faut le savoir pour relire l'historique : la première
version est tombée dans le **dégraissage de `CLAUDE.md`** mené en parallèle le
même jour, qui a ramené le fichier de 1 239 à ~400 lignes en déplaçant les
argumentaires. Réécrite dans le format d'arrivée — **l'énoncé au §8bis, son
argumentaire au §2.4 de `docs/GARDE-FOUS.md`**, où vit désormais le « pourquoi »
de chaque garde-fou. C'est là que se trouvent le cas Pont-de-Larn, le facteur 50
sur l'hydrazide maléique, les 69 faux positifs de la bactériologie et le
recouvrement des 46 aveugles avec les 55 indéterminés.

### Le même piège fermé sur `indetermine_strict` — 8 août 2026

Traité dès que le chantier C2 a rendu `src/build_db.py`. La garde `> 0` vaut
désormais aussi pour l'indéterminé ordinaire, avec son contre-exemple au test.

**Le mécanisme n'était pas celui annoncé, et la correction le dit.** Il avait
été écrit ici que la bactériologie échappait au piège parce que son seuil strict
n'était pas convertible vers l'unité de la mesure. Vérification faite, c'est
faux : ces mesures ne sont appariées à **aucune** ligne du référentiel. Les
libellés de la source — « Escherichia coli /100ml - MF », « Entérocoques
/100ml-MS » — ne rejoignent pas « Escherichia coli » et « Entérocoques », et
leur seuil vient de la seule limite déclarée. `seuil_strict` reste donc vide.

La différence compte, parce qu'elle change ce qui aurait déclenché le défaut :
non pas une conversion d'unité, mais **l'ajout d'un alias** — c'est-à-dire
exactement l'entretien courant que `alias_parametres.csv` est fait pour
recevoir. Le contrôle ajouté à `tests/test_verdict.py` ingère donc une ligne
« Enterocoques » au libellé et à l'unité du référentiel, celle qui aurait
existé si l'alias avait été écrit ; sans la garde, elle passe « indéterminée »,
et c'est vérifié.

Aucun chiffre du corpus ne bouge — 55 indéterminés, 46 aveugles, avant comme
après. C'est une règle qui cesse de dépendre d'une lacune du catalogue, pas une
correction de résultat.

`depasse_strict` n'appelait rien : trois entérocoques pour 100 mL franchissent
bel et bien une exigence d'absence. C'est la LQ, et elle seule, qui ne peut pas
passer sous zéro.

### Ce qui attend une décision de Yannick

---

## C5 — TERRITOIRES

### Nommer les zones auxquelles on compare

### Ce que Yannick demande

> « Il faut éviter de faire des comparaisons avec d'autres agglomérations, ou
> du moins les nommer (exemple mieux que l'agglomération chartraine qui est
> citée car on a des résultats de cette zone). »

### Ce qui existe aujourd'hui

Trois comparaisons dans la prose validée, de qualité inégale :

| Où | Formulation | Verdict |
|---|---|---|
| Challet | « contre 315 à 316 ailleurs sur **l'agglomération chartraine** » | conforme — zone nommée, données détenues |
| Mainvilliers | « sur l'ensemble du secteur — Lèves, Saint-Prest, Bailleau… » | conforme — les communes sont énumérées |
| Saint-Salvy-de-la-Balme | « comparable à celui **des grands réseaux du corpus** » | **à reprendre** — aucun territoire nommé |

Le titre de la section de Challet dit « plus modeste que **le voisinage** » :
le corps nomme la zone, le titre ne la nomme pas. À aligner.

*Deux rectifications faites en ouvrant le chantier.* La première ligne du
tableau n'est pas celle de Challet : la section vit sur la clé
`PREL:02800129616`, le bulletin de **La Bourdinière-Saint-Loup** du 9 avril
2026, qu'elle dessert avec Amilly et Cintray. La deuxième n'est pas celle de
Mainvilliers non plus, mais celle de `PREL:02800129069`, **Saint-Prest**, qui
dessert Mainvilliers. C'est la conséquence directe du passage de la prose à
une indexation par point d'eau (§8quater bis) : une section ne porte plus le
nom d'une commune. Et les deux formulations jugées « conformes » ici se sont
révélées inexactes dès qu'on est allé lire les bulletins de la zone nommée —
voir plus bas.

### La règle à écrire

Toute comparaison de territoire nomme la zone à laquelle elle compare, et cette
zone doit être une zone **dont le corpus détient les bulletins**. Pas de
« ailleurs », pas de « le voisinage », pas de « les grands réseaux » : ce sont
des comparaisons invérifiables, et elles sont d'autant plus tentantes qu'elles
ne demandent aucune donnée. À adosser au §2.11, qui impose déjà d'afficher
l'effort de recherche de chaque terme comparé.

### Ce qui a été fait — 8 août 2026

Quatre sections reprises dans `sortie/redactions.json`, un contrôle ajouté.

**La zone est dans les données, et personne ne s'en servait.** C'est la
découverte du chantier. `analyses_figees.nom_uge` porte le gestionnaire déclaré
par la source : « CHARTRES METROPOLE » sur douze bulletins du corpus,
« SME LEVEZOU SEGALA » sur sept, « SMAEP DU PAS DES BETES » sur quatre. La
zone à laquelle on compare n'a donc pas à être devinée ni empruntée au
vocabulaire courant — elle est **lisible en base, et elle est sourcée**. Une
comparaison peut désormais être écrite, vérifiée et refaite par un tiers.

C'est aussi ce qui a permis de trancher un point que la formulation vague
masquait : Soulaires, citée avec le « secteur chartrain », n'est pas sur
Chartres Métropole mais sur la régie des Portes Euréliennes. Le nom générique
avait absorbé la différence.

**Nommer la zone a fait tomber trois erreurs de fait.** Elles n'étaient pas
visibles tant que le terme de comparaison restait flou — c'est l'argument le
plus solide en faveur de la règle, et il ne se déduit pas d'elle.

| Où | Ce qui était écrit | Ce que disent les données |
|---|---|---|
| La Bourdinière-Saint-Loup | « 234 paramètres, contre 315 à 316 ailleurs sur l'agglomération chartraine » | Jouy est à 314 et **Challet à 234** : le panel étroit n'est pas propre à cette commune, et la fourchette réelle va de 234 à 316 |
| Saint-Salvy-de-la-Balme | « supérieur à celui de plusieurs communes de l'agglomération chartraine » | 370 paramètres, soit plus que **chacun** des douze bulletins de Chartres Métropole (234 à 359) — l'écart était sous-estimé |
| Monestiés | LQ « 2,5 µg/L contre 0,5 sur les bulletins plus récents du même département » | deux bulletins du Tarn sont à **0,05**, et le plus **ancien** du département est déjà à 0,5 : la lecture chronologique ne tient pas |

Une quatrième section, Saint-Prest, énumérait huit communes mais **oubliait
Challet**, qui porte pourtant la troisième valeur du corpus. L'énumération est
maintenant complète et chiffrée : onze bulletins d'Eure-et-Loir ont cherché le
chlorothalonil R471811, il y est quantifié onze fois, et onze fois au-dessus de
la limite de 0,1 µg/L antérieure à avril 2024.

**Le contrôle 8 de `tests/test_sorties.py`.** Il repère les désignations qui ne
nomment rien — « ailleurs », « voisinage », « les grands réseaux », « plusieurs
communes », « la moyenne nationale » — et vérifie qu'un nom propre ou le mot
« corpus » figure dans la même phrase. Deux emplois sont exclus parce qu'ils ne
comparent pas de territoire : « par ailleurs », et « prélevée ailleurs », qui
est l'obligation d'affichage n° 5 du §8bis.

Même asymétrie que le contrôle 6 : bloquant sur la prose générée, signalé sur
la prose d'auteur. Un outil qui censure son auteur n'est pas un garde-fou.

Ce qu'il **ne** sait pas faire, et qui doit rester une relecture humaine : dire
que la zone nommée est la bonne, que le corpus en détient les bulletins, et que
l'effort de recherche des deux termes est affiché à côté (§2.11). Il constate
qu'une zone est nommée, pas qu'elle est juste.

`sortie/rediger.py` a été relu : la prose dérivée ne compare qu'au prélèvement
**précédent de la même commune**, nommé et daté. Elle était déjà conforme, et
rien n'y a été touché — le fichier est celui du chantier C4.

### La règle est au §2.11 — 8 août 2026

> « ok change dans le §2.11 »

Inscrite sur instruction, en **seconde règle de sortie** du §2.11, à la suite
de celle qui impose d'afficher l'effort de recherche : une comparaison de
territoire nomme la zone, cette zone est une zone dont le corpus détient les
bulletins, et le nom se prend dans `nom_uge` plutôt que dans le vocabulaire
courant. Le §2.11 porte aussi les trois erreurs de fait qui sont tombées le
jour où on l'a appliquée — c'est ce qui justifie la règle, et ça ne se déduit
pas d'elle.

Le chantier n'attend donc plus rien : la demande est satisfaite, la règle est
écrite là où on la cherchera, et `tests/test_sorties.py` en tient le contrôle.

### Ce qui reste ouvert, et n'a pas été touché

Le mot « la série », employé dans les sept fiches de commune écrites pour le
livre — « le meilleur résultat PFAS de la série ». Ce n'est pas une comparaison
de territoire, donc hors du périmètre de ce chantier, mais c'est une portée
que le lecteur ne peut pas résoudre : il ne sait pas de quelle série on parle
ni combien de bulletins elle contient. À trancher avec Yannick, dont ce sont
les textes.

---

## C6 — ÉCHELLE

### Passer de 60 à plusieurs milliers de communes

### Ce que Yannick a tranché

Le passage de main demandait s'il fallait garder les 53 communes collectées
hors livre. La question était mal posée :

> « mon idée est d'avoir plusieurs milliers de communes, pour avoir une data
> significative. Je construis un outil citoyen, qui permettra à partir
> d'analyses officielles, mais agrégées de manière différente, d'offrir une
> situation. »

**Décision : on garde tout, et le corpus a vocation à croître d'un ordre de
grandeur.** Le point 4.3 de `docs/REPRISE.md` est clos.

### Ce que cela implique, et qui est déjà su

- les chantiers 2 et 4 ne prennent leur sens qu'à cette échelle : une direction
  commune dans les paramètres abandonnés ne se voit pas sur 45 bulletins ;
- `fetch_departement.py` est prêt et n'a jamais servi en entier. C'est le
  prochain pas naturel, et il donnera aussi les communes « non documentées »,
  qui n'existent aujourd'hui que dans les tests ;
- l'étiquette envers Hub'Eau (§3.2) devient une contrainte réelle et non plus
  théorique : un département = plusieurs milliers d'appels ;
- la vitrine statique approche 1,7 Go à l'échelle nationale et demandera d'être
  découpée par département (§8ter). Ce n'est pas bloquant avant d'y être.

---

## C7 — CAPTAGE

### Dilution, mélange, et ce qu'un réseau moyenne

### Ce que Yannick demande

> « si pour une commune on mélange 3 captages alors la moyenne peut être bonne,
> même si un captage est hors caractéristique. Cette hypothèse veut également
> dire que "on injecte des molécules chimiques en moyennant" plutôt que de
> fermer ou traiter un captage ! Je précise, ceci est une hypothèse et non une
> affirmation, il faut investiguer. »

**Cette remarque était bien sauvegardée** : elle est au §7bis de `CLAUDE.md`,
décidée le 7 août 2026, sous la formule « la dilution tient alors lieu de
dépollution ». Ce qu'elle gagne aujourd'hui, c'est sa formulation la plus dure —
non pas seulement *une eau devient conforme sans être traitée*, mais *le mélange
devient un mode de gestion*. Et elle gagne son statut : **hypothèse à
instruire**, pas constat.

### Pourquoi il précède le chantier C3

Le chantier « évolution » a buté exactement là. Sur les huit communes à
plusieurs bulletins, aucune paire ne partage un `code_installation_amont` ; à
Boissezon il y a trois captages, à Loubers deux qui alimentent la commune à
80 % et 20 %. Tant qu'on ne sait pas relier un bulletin à sa ressource, on ne
sait pas si deux analyses décrivent la même eau — donc ni parler d'évolution,
ni voir un mélange. **Le chantier C3 attend celui-ci.**

### Ce que les données permettent — état vérifié au §7bis

| Maillon | Source | État |
|---|---|---|
| l'eau au robinet (le mélange) | `qualite_eau_potable/resultats_dis` | branché |
| les captages AEP et leur position | BNPE, `points_prelevement` | disponible, jamais collecté |
| la qualité de l'eau **brute** | `qualite_nappes`, `qualite_rivieres` | disponible, jamais collecté |
| **quel captage alimente quelle UDI** | — | **non exposé par Hub'Eau** |

Le dernier maillon manque, et c'est celui qui porte l'hypothèse. Deux substituts
partiels existent déjà en base et ne demandent aucune collecte :
`code_installation_amont` donne l'usine, et `noms_reseaux` donne **le mélange
entre réseaux avec sa part en pourcentage** — c'est ce champ qui dit « LOUBERS
(80 %) » et « LOUBERS (20 %) ».

### Le premier pas, qui ne demande rien

Avant toute collecte nouvelle : **dénombrer les mélanges déjà lisibles**. Les
bulletins dont `noms_reseaux` porte plusieurs réseaux, ou une part inférieure à
100 %, décrivent une eau mélangée — Montech en janvier 2026 en est un
(« FINHAN (UDI) (100 %)|MONTECH (UDI) »). C'est le dénombrement qui dira si
l'hypothèse a un terrain, et il se fait sur la base actuelle.

### La règle, dès maintenant

Le lien captage → usine ne pourra être établi que par **inférence
géographique**. Il devra donc être affiché comme une hypothèse, jamais comme un
fait (§7bis). Et l'hypothèse de Yannick — le mélange comme substitut au
traitement — est une **question posée à la norme**, pas une accusation portée
contre un exploitant : diluer est légal, et c'est précisément ce qui la rend
intéressante (§2.1).

### Ce qui a été construit — 8 août 2026

Le premier pas est fait, sans aucune collecte nouvelle. Quatre vues dans
`src/build_db.py`, un script de dénombrement, une note de méthode, huit
contrôles de non-régression. Tout est écrit dans
**`docs/METHODE_DILUTION.md`**, qui est le document de référence du chantier.

| Vue | Ce qu'elle porte |
|---|---|
| `v_reseau_bulletin` | la décomposition : une ligne par (bulletin × réseau desservi), part lue |
| `v_reseaux_illisibles` | contrôle : les prélèvements dont les listes codes/noms ne s'apparient pas |
| `v_melange_bulletin` | par bulletin : combien de réseaux, à quelle part, mélange lisible ou non |
| `v_melange_reseau` | par réseau : sources connues, somme des parts, **part non attribuée**, statut |

```bash
py -X utf8 src/etude_melange.py
```

Trois fichiers dans `data/etudes/`, non versionnés comme toute donnée dérivée.
Matériau d'étude : ni la vitrine ni la fiche ne lisent ces vues.

### Ce que le champ dit vraiment, et une correction à ce carnet

Le `debit` de Hub'Eau **n'est pas documenté par l'API**. Sa signification a été
déduite du corpus et vérifiée deux fois : c'est la **part du débit du réseau
apportée par l'installation amont de ce prélèvement**. Deux réseaux se referment
exactement sur 100 % — LOUBERS (Bateste 80 % + Bouyssounade 20 %) et VALLEE DU
CEROU (Bournazel réservoir 50 % + Moulin Galat 50 %). La lecture concurrente
« part de l'eau de la commune » est réfutée par Loubers, où la même commune porte
80 % et 20 % sur le même réseau. Marqué `a_verifier` tant que la source ne
l'écrit pas (§2.7).

**Correction.** La phrase ci-dessus — « les bulletins dont `noms_reseaux` porte
plusieurs réseaux […] décrivent une eau mélangée », avec Montech en exemple — est
fausse, et c'est la lecture du champ qui le montre. Montech 2026 porte
« FINHAN (UDI) (100 %)|MONTECH (UDI) » : c'est **une** installation qui alimente
**deux** réseaux, chacun en totalité. L'inverse d'un mélange. Le critère n'est
pas le nombre de réseaux desservis, c'est **une part inférieure à 100 %**.

### Le dénombrement — ce que le corpus dit

Sur 45 bulletins desservant 42 réseaux :

| Statut | Réseaux | Communes portant un bulletin |
|---|---|---|
| `source_unique_declaree` | 25 | 25 |
| `non_declare` | 11 | 11 |
| `melange_partiel` | 4 | 5 |
| `melange_reconstitue` | 2 | 5 |

**Six réseaux sur 42 portent un mélange lisible**, et **18 bulletins sur 45 ne
déclarent aucune part** — pour ceux-là on ignore jusqu'à l'existence du mélange.
CHARTRES S1 reçoit 75 % de son débit d'une installation que le corpus ne connaît
pas ; FONT POLEMIE et SYNDICAT VIEUX ITZAC, 50 % chacun ; LEVES B2, 20 %.

**L'hypothèse a donc un terrain, et il est petit** : deux réseaux seulement —
LOUBERS et VALLEE DU CEROU — portent un mélange entièrement reconstitué dont
plusieurs sources sont analysées. C'est là, et seulement là, qu'on peut voir ce
que chaque source apporte.

### Le premier cas remonté n'en est pas un, et il faut le dire

VALLEE DU CEROU, 50/50 : le bulletin du Moulin Galat (15/12/2025) porte un
dépassement, celui de Bournazel Réservoir (24/11/2025) aucun. Le dépassement est
*Escherichia coli* à 1 pour 100 mL — **bactériologique**, ponctuel, et l'ARS a
prononcé la non-conformité. Une bactérie ne se moyenne pas comme une molécule :
appliquer le raisonnement de dilution ici serait la première erreur à commettre.
Le mécanisme est lisible sur deux réseaux, et aucun des deux ne montre encore ce
qu'on cherche. C'est un résultat.

### La question centrale, non tranchée

**Où, dans le réseau, le prélèvement a-t-il été fait ?** `code_lieu_analyse` vaut
`L` sur les 45 bulletins : une seule valeur, donc aucune information. Si le
prélèvement est fait **après** le point de mélange, un bulletin de réseau mélangé
décrit déjà la moyenne, et l'hypothèse devient indémontrable avec ces seules
données ; s'il est fait en amont, la comparaison entre sources a un sens. Que
l'ARS rattache chaque prélèvement à **une** installation plaide pour la seconde
lecture — ce n'est pas une preuve. **Tant que ce point n'est pas tranché, aucune
conclusion de dilution ne se publie.**

### Ce qui reste à faire

1. **Trancher la question ci-dessus** — nomenclature SISE-Eaux du lieu
   d'analyse, ou question à l'ARS. Rien dans le dépôt ne permet de le faire.
2. **Le volume** : sur 45 bulletins, six mélanges lisibles ne dessinent aucun
   motif. Ce chantier attend C6 comme C2 l'attend.
3. **Les captages** (BNPE) et **l'eau brute** (`qualite_nappes`,
   `qualite_rivieres`) restent non collectés. Ils ne servent à rien avant que
   le lien captage → installation soit inféré, et cette inférence sera
   géographique, donc affichée comme une hypothèse.
4. ~~**`CLAUDE.md` §7bis** à reformuler~~ — **fait le 8 août 2026, sur
   instruction de Yannick.** Le §7bis porte désormais la lecture établie du
   champ `debit`, la règle « une part absente n'est pas 100 % », le
   dénombrement, la question du lieu de prélèvement et le rappel que diluer est
   légal. Le paragraphe corrigé y est cité comme erreur, avec son mécanisme :
   il prenait le nombre de réseaux desservis pour un indice de mélange.

---

## C8 — ATELIER

### Comprendre et fiabiliser le back-office

### Ce que Yannick demande

> « on va rajouter un chantier sur le back office sérieux car je ne comprends
> pas tout bien (notamment pourquoi il me parle de plusieurs communes dont le
> rapport n'est pas généré (exemple Amarens INSEE 81009) alors que je croyais
> que l'on avait tout généré. »

### La réponse : l'atelier disait faux, et c'est corrigé

Amarens **a** sa page. `site/public/commune/81009.html` existe, et **aucune**
des 60 communes couvertes n'en est dépourvue. La commune est
`rattachee_reseau` : elle boit l'eau du point de prélèvement 08100130175,
analysé à Sainte-Croix le 13 janvier 2026 sur 411 paramètres.

La liste que Yannick a lue est l'étape 4 de la page d'état — « N commune(s)
sans prose écrite » — et Amarens y figurait en tête, par ordre alphabétique.
Elle en annonçait **54 sur 60**. Le nombre réel est **zéro**.

**Cause.** `circuit()` cherchait la prose d'une commune en testant si son code
INSEE figurait parmi les clés de `redactions.json` :

```python
if insee not in redigees and insee not in proposees:   # avant
```

Or la prose est indexée **par point d'eau** depuis le 8 août 2026 (§8quater
bis) : sur les 52 clés du fichier, **45 sont des `PREL:`** et 7 seulement des
codes INSEE. La page d'état est restée sur l'ancienne indexation et a donc
déclaré non rédigée presque chaque commune du corpus. Le compteur de la même
étape annonçait « 52 communes avec une prose écrite » — 52 étant un nombre de
**clés**, dont 45 désignent des points d'eau et non des communes.

**Correction appliquée le 8 août 2026.** L'atelier interroge désormais
`build_fiche.pour_bulletin`, c'est-à-dire **la même fonction que la fiche**, en
lui passant le bulletin que `couverture_communes` associe à la commune. La
règle des trois clés n'existe qu'à un seul endroit. Après correction : 60
couvertes, 60 publiées, 60 rédigées, rien en retard.

### Ce que ce défaut apprend, et qui est le vrai chantier

L'atelier **recopiait** une règle qui vit ailleurs. Toute connaissance
dupliquée entre l'atelier et la chaîne de sortie divergera à la première
évolution — ici, un refactor du matin a fait mentir la page d'état de
l'après-midi, sans qu'aucun contrôle ne l'attrape.

**Aucune suite de tests ne couvre l'atelier.** Les trois existantes contrôlent
le moteur, la sortie figée et les sorties publiées. Une page d'état qui ment
peut donc vivre indéfiniment — et elle l'a fait.

### Ce qui reste à faire

1. **Une quatrième suite, `tests/test_atelier.py`.** Elle vérifie que les
   compteurs du circuit disent la vérité : une commune rattachée dont le point
   d'eau porte un texte est rédigée ; une commune sans page est signalée ; les
   comptes portent sur des **communes** et jamais sur des clés de fichier.
2. **Auditer les trois autres étapes** au même standard — `collectees`,
   `a_figer`, `publiees`. Le défaut trouvé sur l'étape 4 n'a aucune raison
   d'être le seul.
3. **Nommer les choses une fois pour toutes.** « Rapport », « fiche », « page »,
   « prose », « bulletin » circulent comme des synonymes et ne le sont pas :
   Amarens a une **page** et une **prose**, mais aucun **bulletin** à elle. La
   confusion entre les trois est précisément ce qui a rendu le message
   incompréhensible.
4. **Rendre le rattachement lisible sur la page d'état.** Qu'on voie d'un coup
   d'œil qu'Amarens boit l'eau de Sainte-Croix — c'est déjà l'obligation
   d'affichage n° 5 du §8bis pour la vitrine, elle vaut autant pour l'atelier.
5. **Une page « d'où vient ce que je lis »** : pour une commune donnée, la
   chaîne complète — quel bulletin, prélevé où, quelle version de référentiel,
   quelle origine de prose section par section. C'est la demande de fond de
   Yannick : « je ne comprends pas tout bien ».

### Le piège

L'atelier **agit** mais ne juge pas : il ne recalcule jamais un verdict, il lit
les tables figées (§8bis). Et il ne se publie jamais (§8ter). Un chantier de
confort qui l'amènerait à recalculer pour « aller plus vite » casserait les
deux règles à la fois.

---

## Ce qui reste en attente d'une décision de Yannick

Repris de `docs/REPRISE.md` §4, mis à jour :

- **le barème de finesse analytique** — chantier C4, niveau 3 : **tranché le
  8 août 2026**, on l'affiche, avec sa base — nombre de bulletins et de
  départements sur lesquels l'étendue est calculée ;
- **la onzième obligation d'affichage du §8bis** — chantier C4 : **tranché le
  8 août 2026**, la règle est écrite dans `CLAUDE.md` sur instruction ;
- **le seuil nul dans `indetermine_strict`** — chantier C4 : le même piège que
  celui écarté pour les paramètres aveugles subsiste sur l'indéterminé
  ordinaire, dans `src/build_db.py`. Sans effet aujourd'hui, par accident ;
- **l'ordre des chantiers 3 et 7** — l'évolution attend le captage ;
- **le §2.2 et la filtration** — chantier C1, gelé jusqu'à nouvel ordre ;
- **le « charbon actif » de Vourles** — inchangé, décision liée au chantier C1 ;
- **les 53 communes hors livre** — tranché : on garde (chantier C6) ;
- **le mot « la série »** dans les sept fiches du livre — portée que le lecteur
  ne peut pas résoudre. Hors périmètre de C5, ce sont des textes d'auteur ;
- **le §7bis de `CLAUDE.md`** — chantier C7 : **tranché le 8 août 2026**, le
  §7bis est réécrit avec la lecture établie du champ `debit` ;
- **où le prélèvement est fait dans le réseau** — chantier C7, question ouverte
  qui commande la portée de tout l'axe dilution. Rien dans le dépôt ne permet de
  la trancher : il faut la nomenclature SISE-Eaux du lieu d'analyse, ou l'ARS ;
- **l'hébergement** — hébergeur, nom de domaine, et dépôt de code public ou
  non. Rien n'est publié en ligne à ce jour.

---

## Journal

- **8 août 2026** — ouverture du carnet. Chantiers C1 à C6 écrits. C1 gelé sur
  instruction. C2 lancé et premier livrable posé : quatre vues,
  `src/etude_panel.py`, huit contrôles. C7 ouvert, et C3 mis en attente
  derrière lui.
- **8 août 2026, plus tard** — le carnet passe aux codes `C1`…`C8` pour que les
  chantiers se lancent en sessions parallèles. **C8 ouvert** sur la question
  d'Amarens : la page d'état annonçait 54 communes « sans prose » sur 60, il
  n'y en avait aucune. Corrigé dans `atelier/atelier.py` ; le reste du
  chantier — dont l'absence totale de tests sur l'atelier — est écrit.
- **8 août 2026, reprise de C2** — deux défauts du détecteur à l'échelle,
  trouvés en vérifiant le livrable et corrigés : `v_parametre_presence` ne
  savait pas écrire un 0 % (l'abandon complet était invisible, et un contrôle
  de non-régression affirmait ce défaut), et aucune vue ne permettait de
  distinguer un retrait de programme d'un changement de composition du corpus.
  Vue `v_parametre_presence_dept` ajoutée, deux contrôles affichés sous chaque
  chute, cinquième export. Le signal de l'odeur passe les deux contrôles. C2
  reste en attente de C6 pour le volume.
- **8 août 2026, C5 fait** — quatre sections de `sortie/redactions.json`
  reprises, contrôle 8 ajouté à `tests/test_sorties.py`. La zone à laquelle on
  compare est dans les données depuis le début (`nom_uge`) et n'était pas
  utilisée. Nommer la zone a fait tomber **trois erreurs de fait** que le flou
  masquait — dont un « panel le plus étroit » qui ne l'était pas, Challet
  portant le même. Règle **inscrite au §2.11 de `CLAUDE.md`** dans la foulée,
  sur instruction de Yannick : c'est la seconde règle de sortie du paragraphe,
  à côté de celle qui impose d'afficher l'effort de recherche. Chantier clos.
- **8 août 2026, C7 premier livrable** — le dénombrement des mélanges est posé :
  quatre vues, `src/etude_melange.py`, `docs/METHODE_DILUTION.md`, huit
  contrôles. Le `debit` de Hub'Eau, que l'API ne documente pas, est **la part du
  débit du réseau apportée par l'installation amont** — déduit du corpus et
  vérifié sur deux réseaux qui se referment à 100 %. Six réseaux sur 42 portent
  un mélange lisible, dont deux entièrement reconstitués ; 18 bulletins sur 45
  ne déclarent aucune part, et une part absente n'est **pas** 100 %. Une phrase
  de ce carnet est corrigée au passage : Montech n'était pas un mélange mais une
  installation alimentant deux réseaux en totalité. **Le §7bis de `CLAUDE.md`
  est réécrit dans la foulée, sur instruction de Yannick** : il porte désormais
  la lecture du champ, le troisième état `non_declare`, le dénombrement et la
  question du lieu de prélèvement — et il cite sa propre formulation précédente
  comme erreur, avec son mécanisme. Reste la question qui commande tout : où,
  dans le réseau, le prélèvement a-t-il été fait ? C3 attend cette réponse.
  Note de session : `src/build_db.py` a été modifié par la session C2 pendant
  celle-ci ; les vues de mélange sont groupées en fin de fichier pour que les
  deux cohabitent.
- **8 août 2026, C4 fait** — le plafond analytique est posé sur les quatre
  niveaux : mention chiffrée au paramètre, taux `aveugles_pour_mille` au
  bulletin, barème logarithmique par paramètre avec sa base, et section dérivée
  dans la prose. Deux colonnes à `verdicts_figes`, deux à `analyses_figees`,
  la table `lq_corpus`, un export téléchargeable, treize contrôles.
  **46 mesures aveugles sur 39 bulletins**, 8 substances, jusqu'à 8,44 pour
  mille. Yannick tranche le niveau 3 — on l'affiche, avec sa base — et le
  compteur — séparé de `nb_indetermines`, qui ne bouge pas.
  Deux choses que le carnet n'avait pas vues. **Le seuil nul** : la règle
  attrapait 69 mesures de bactériologie, dont la limite est zéro et dont la LQ
  de dénombrement vaut 1 — aucune LQ ne passe sous zéro, garde posée et
  contre-exemple au test. **Le recouvrement** : les 46 aveugles sont tous parmi
  les 55 indéterminés, la prose les comptait deux fois ; elle mesure désormais
  le recouvrement au lieu de le supposer.
  **Onzième obligation d'affichage inscrite au §8bis de `CLAUDE.md`** dans la
  foulée, sur instruction de Yannick : la mention se chiffre, un seuil de zéro
  ne se perce pas par le bas, et une LQ élevée est une capacité d'instrument.
  Note de session : `src/build_db.py` étant en cours de modification par C2, le
  calcul a été porté dans `src/figer.py`, où vivent déjà les indicateurs dérivés
  du bulletin.

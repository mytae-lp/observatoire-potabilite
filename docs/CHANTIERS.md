# Chantiers d'améliorations

## ERGONOMIE — deux constats du 11 août 2026, pour le dossier ergonomie à venir

*Reportés à la demande de Yannick : un dossier ergonomie de site est prévu, ces
deux points en feront partie. Rien n'a été modifié.*

**1. « Rien trouvé » se lit comme « rien su ».** Toulouse (31555) : bulletin
propre du 4 mai 2026, **383 paramètres mesurés, 337 notés (88 % de couverture),
0 dépassement, 1 seule substance de synthèse quantifiée**. C'est le résultat le
plus rassurant que le corpus puisse produire — et la fiche l'affiche en tirets et
en « sous la limite de quantification », ce qui ressemble à un formulaire vide.

C'est le §2.11 retourné contre nous : *une eau correcte sur 200 paramètres est
une information plus faible qu'une eau moyenne sur 700.* Ici c'est une eau très
propre sur 383, et rien ne le dit. Pistes : remplacer le tiret par **« cherché,
non détecté »**, et porter en tête du bloc *« N paramètres recherchés, M
substances trouvées »* au lieu de laisser le lecteur additionner des absences.

**2. Le blanc de la carte se lit comme « on ne sait pas ».** Or une commune
blanche est **rattachée à un réseau** : elle boit une eau réellement analysée,
ailleurs. La proportion est structurelle, pas un défaut de collecte — elle suit
les métropoles.

| dept | analysées | rattachées | non documentées |
|---|---|---|---|
| 31 | 144 | **431** | 11 |
| 69 | 67 | **198** | 1 |
| 81 | 127 | 187 | 0 |
| 28 | 177 | 181 | 5 |
| 09 | 172 | 153 | 0 |

Les deux départements les plus « blancs » portent Toulouse Métropole et la
Métropole de Lyon : un grand réseau alimente des dizaines de communes depuis
quelques points de production. Le §8bis, point 5, impose déjà de dire **où**
l'analyse a été prélevée — à vérifier sur la carte autant que sur la fiche.

---

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
| **C1** | FILTRATION | ce qu'un type de filtre retient, et ce qu'il ne retient pas | **dégelé le 9 août 2026** — le §2.2 est révisé, la table reste à construire |
| **C2** | PANEL | quels paramètres on a cessé de chercher | **une rupture datée trouvée** — janvier 2020, à installation constante |
| **C3** | ÉVOLUTION | comparer les bulletins successifs d'un même point d'eau | **débloqué** — 165 installations à plusieurs bulletins |
| **C4** | LQ | la finesse du laboratoire, et le biais qu'elle crée entre communes | **fait**, règle inscrite au §8bis |
| **C5** | TERRITOIRES | ne comparer qu'à des zones nommées, dont on a les données | **fait**, règle inscrite au §2.11 |
| **C6** | ÉCHELLE | passer de 60 à plusieurs milliers de communes | **le Tarn est fait** — 314/314, 1 595 bulletins |
| **C7** | CAPTAGE | la dilution comme mode de gestion — hypothèse à instruire | **premier livrable posé** |
| **C8** | ATELIER | comprendre et fiabiliser le back-office | **prêt à lancer** |
| **C9** | VITRINE | le parcours, la carte, la liste, le référentiel, et « que faire » | **en cours** — ouvert le 9 août 2026 |
| **C10** | ARRÊTÉS | les actes préfectoraux qui touchent l'eau de consommation, par département | **élargi le 11 août 2026** — reconnaissance du Tarn faite, spécification écrite, collecte non lancée |

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
| C10 ARRÊTÉS | `referentiel/arretes_eau.csv`, `referentiel/motifs_arretes.csv`, `docs/CONSIGNE_QUALIFICATION_ARRETE.md`, `src/raa_*.py`, `docs/INDEX_SOURCES.md` | son lot C touchera au **modèle de seuils** (date de fin) — les lots A et B, non |
| C6 ÉCHELLE | `src/collecte.py`, `src/brut.py`, `src/fetch_departement.py`, `src/hubeau.py`, `src/observer.py` | **tous, par le corpus** — une collecte change les chiffres de chaque chantier |
| C9 VITRINE | `site/build_site.py`, `site/gabarits/`, `docs/VITRINE.md`, `referentiel/retention_procedes.csv` | **C6 par le corpus** ; C1, dont il porte le livrable |

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

### Dégel du 9 août 2026 — le §2.2 est révisé

Le moment est venu en ouvrant le chantier C9 : le volet « que faire quand mon
eau est compliquée » est demandé pour la vitrine, et il bute exactement sur ce
garde-fou.

**Le §2.2 de `CLAUDE.md` est réécrit**, sur instruction de Yannick. La frontière
ne passe plus entre « en parler » et « ne pas en parler », mais entre **un type
et un produit**. L'argumentaire long — le retour de lecteur qui déclenche tout,
le test qui repère une prescription déguisée, le cas de Vourles — est au §2.2 de
`docs/GARDE-FOUS.md`.

Ce qui reste à construire, et qui est le vrai coût du chantier :

1. **`referentiel/retention_procedes.csv`**, une ligne par couple procédé ×
   famille de substance, avec ses sources. Rien ne se publie avant qu'il existe :
   le §2.2 révisé n'autorise pas de la prose sur les procédés, il autorise une
   table sourcée.
2. **Les sources elles-mêmes**, à `fiabilite = verifie`, chacune couvrant son
   couple précisément. C'est le poste long, et il ne se sous-traite pas à une
   analogie de famille.
3. **Le cas de Vourles** — la phrase de Yannick devient conforme sur le fond,
   mais attend sa ligne dans la table. Le signalement de `tests/test_sorties.py`
   ne se retire pas avant.

### Reste à décider

Si ce volet vit sur le site **et** dans le livre, ou seulement dans l'un des
deux — Yannick indiquait le 8 août qu'il est lié aux deux.

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
| `v_parametre_presence_dept` | la même, par département — le contre-feu (ajoutée le 9 août 2026) |
| `v_panel_constant` | les paramètres cherchés chaque année documentée d'un département (9 août 2026) |
| `v_serie_panel_constant` | le taux de quantification à périmètre de mesure constant — la seule série lisible (§2.11) |

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

### Deux défauts du détecteur, trouvés et corrigés — 9 août 2026

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

### Le volume est arrivé — et il y a une rupture datée au mois près

Le Tarn a été collecté en entier le 8 août 2026 (chantier C6) : 314 communes,
1 575 bulletins complets, 2016 → 2026. La machinerie construite pour 45
bulletins a été lancée sur trente-cinq fois plus, et elle rend un motif.

**Le panel du Tarn passe de 606 à 352 paramètres entre 2019 et 2020.**

| Année | Bulletins | Panel moyen |
|---|---|---|
| 2016 | 95 | 626 |
| 2017 | 103 | 604 |
| 2018 | 114 | 600 |
| **2019** | 164 | **606** |
| **2020** | 121 | **352** |
| 2021 | 158 | 355 |
| 2024 | 217 | 349 |
| 2026 | 56 | 378 |

Le carnet exigeait deux contrôles avant d'appeler cela un retrait. Les deux
passent, et ils passent largement.

**1. À installation constante.** En ne gardant que les installations qui portent
un bulletin avant 2020 **et** un après — 135 d'entre elles, 431 bulletins avant,
720 après — le panel moyen passe de **606 à 362, soit −40 %**. Ce n'est donc pas
un effet de composition du corpus : ce sont les mêmes points d'eau qui cherchent
moins.

**2. Ce n'est pas une moyenne qui glisse.** **132 des 135 installations
baissent**, trois seulement sont stables ou en hausse.

Et la rupture n'est pas une pente, c'est une marche. La moyenne mensuelle passe
de **585 en décembre 2019 à 324 en janvier 2020** ; les six mois précédents
tiennent entre 578 et 627, les douze suivants entre 324 et 372.

**Mais la moyenne mensuelle n'est pas la bonne résolution**, et il a fallu un
troisième contrôle pour le voir : un point d'eau n'est analysé complètement
qu'une fois par an environ, donc une moyenne mensuelle porte sur six à vingt
bulletins et sa date apparente dépend de qui a été prélevé ce mois-là. Datée
installation par installation, la bascule paraissait d'abord s'étaler de janvier
2020 à novembre 2024.

**Ces datations tardives sont toutes un artefact d'échantillonnage.** Sur les 77
installations qui semblaient basculer en 2021 ou après, **77 n'ont aucun
bulletin entre leur dernier panel large et leur premier panel étroit** : elles
n'ont simplement pas été prélevées dans l'intervalle, et leur date apparente est
celle de leur retour, pas celle du changement. Aucune, pas une seule, ne cherche
un panel large entre les deux.

D'où l'énoncé le plus fort que la donnée supporte, et il est net :

| Dernière année où une installation cherche encore plus de 500 paramètres | Installations |
|---|---|
| 2016 | 4 |
| 2017 | 6 |
| 2018 | 11 |
| **2019** | **111** |
| 2020 et après | **0** |

**Aucune installation du Tarn n'a cherché un panel large après 2019.**

### Ce que perd exactement le Tarn — 276 pesticides sur 278

Deuxième test, sur les 47 installations qui portent un bulletin en 2019 **et**
un en 2020 : le panel distinct passe de 632 à 413 paramètres, **278 disparaissent**
et 59 apparaissent. La nature de la perte ne laisse aucune place au doute, et
c'est la source elle-même qui la déclare :

| Ce que la source déclarait en 2019 pour les paramètres disparus | Nombre |
|---|---|
| **limite de 0,1 µg/L — la grille pesticide** | **276** |
| aucune limite déclarée | 2 |
| une autre limite | **0** |

Aldicarbe et ses deux métabolites, acéphate, 2,4-DB, acrinathrine, anilophos,
amiprofos-méthyl… Ce qui sort du panel est un bloc homogène : des pesticides et
leurs métabolites, et rien d'autre.

### La cause documentée ne colle pas à la date — et c'est à instruire

Une session parallèle a documenté la cause réglementaire et l'a inscrite à
l'index sous **REG-05** : l'**instruction n° DGS/EA4/2020/177 du 18 décembre
2020**, dont le guide technique substitue au balayage de toutes les molécules
analysables une **liste régionale arrêtée par l'ARS**, ciblée « en fonction de
la probabilité de les retrouver ». Le mécanisme correspond exactement à ce que
le Tarn montre : un bloc de pesticides retiré d'un coup, sans que la nature de
l'eau y soit pour rien.

**Mais la date ne va pas, et l'écart est d'un an.**

| | |
|---|---|
| date de l'instruction | **18 décembre 2020** |
| installations du Tarn déjà passées au panel étroit avant cette date | **55 sur 132** |
| installations cherchant encore plus de 500 paramètres après cette date | **0 sur 132** |
| dernière année où une installation du Tarn cherche un panel large | **2019** |

Au 18 décembre 2020, le basculement du Tarn était **déjà entièrement acquis**.
Un texte ne peut pas causer ce qui l'a précédé : c'est l'erreur exacte que le
§2.5 et le §2.10 apprennent à ne pas commettre, transposée du seuil au
programme d'analyse.

Trois lectures restent ouvertes, et **aucune n'est tranchée** :

1. **l'instruction codifie une pratique déjà déployée.** Les listes régionales
   auraient précédé le texte qui les généralise. C'est fréquent, et cela rendrait
   REG-05 juste sur le mécanisme et faux sur la chronologie ;
2. **le Tarn a sa propre cause**, par exemple un marché pluriannuel ARS de
   prélèvements et d'analyses entré en vigueur au 1er janvier 2020. REG-05
   mentionne ce mécanisme de bascule par marché ;
3. **un texte antérieur** — l'instruction de 2020 en remplace une de 2010.

**Tant que ce point n'est pas tranché, REG-05 ne doit pas être présentée comme
la cause de ce qu'on observe dans le Tarn.** Elle documente un mécanisme, pas
cette bascule-là. Et les ordres de grandeur qu'elle cite (PACA ~600 → 150) sont
`a_verifier` : ils viennent de reprises documentaires, le PDF officiel n'a pas
été lu (§2.7).

### Ce que le retrait a coûté — presque rien, et il faut le dire

Ajouté le 9 août 2026. Les sections ci-dessus établissent **qu'on** a cessé de
chercher. Restait la question de Yannick : **a-t-on cessé de chercher des choses
qu'on trouvait ?** Elle se répond, et la réponse va contre l'intuition.

Population : les **298 paramètres** qui passent de ≥ 90 % des bulletins du Tarn
en 2019 à ≤ 10 % en 2020 (164 bulletins complets en 2019, 121 en 2020). C'est un
découpage différent de celui des 278 ci-dessus — qui porte sur les 47
installations présentes les deux années — et les deux se recoupent sans se
confondre. Sur ces 298, avant 2020 :

| | |
|---|---|
| mesures faites | **134 419** |
| mesures quantifiées | **6** |
| paramètres quantifiés au moins une fois | **2 sur 298** |
| taux de quantification | **0,004 %** |

Les deux seuls : **biphényle** (3 fois, 2 communes, 2016, max 0,01 µg/L) et
**phosphate de tributyle** (3 fois, 3 communes, 2016-2017, max 0,27 µg/L).

Et ce n'est pas un artefact d'instrument. Sur ces mêmes mesures non quantifiées,
la **LQ médiane est de 0,005 µg/L**, soit vingt fois plus fine que la limite de
0,1 µg/L à laquelle on compare un pesticide individuel : le laboratoire
regardait bien en dessous de la zone qui décide. Une seule mesure sur 134 413
n'a pas de LQ renseignée. (Réserve : la LQ maximale monte à 20 µg/L sur cette
population — une minorité de mesures était bel et bien aveugle, et c'est le
sujet du chantier C4, pas d'ici.)

**Conclusion, et elle est asymétrique dans le bon sens (§2.13).** Le Tarn a
retiré de son programme un bloc de molécules qu'il n'avait jamais détectées en
quatre ans de recherche fine. Présenter ce retrait comme une perte
d'information serait un faux positif — le genre qui se retourne contre
l'Observatoire. Ce qu'il faut en dire est plus intéressant et plus solide : **le
panel de 2019 cherchait massivement les mauvaises molécules.**

### Ce qui l'a remplacé — le panel n'a pas rétréci, il a tourné

C'est le vrai motif, et il n'apparaît qu'en regardant l'autre bout de la
période. **34 paramètres** passent de ≤ 10 % des bulletins en 2019 à ≥ 75 % en
2026 : 26 pesticides, 7 métabolites, 1 non apparié. Et ceux-là, on les trouve.

| Entré au panel | Quantifié | Communes touchées |
|---|---|---|
| **Chlorothalonil R471811** | **107 mesures sur 561 — 19,1 %** | **20** |
| Terbuthylazine et ses métabolites | 14 sur 998 — 1,4 % | 3 |
| Métolachlore NOA 413173 | 3 sur 741 — 0,4 % | 2 |
| Chloridazone desphényl | 2 sur 741 — 0,3 % | 2 |
| Chloridazone méthyl desphényl | 2 sur 741 — 0,3 % | 2 |
| Éthylènethiourée, flufénacet ESA, fluxapyroxad | 1 chacun | 1 chacun |

Un paramètre absent du panel de 2019 est aujourd'hui quantifié dans **une
analyse sur cinq et dans vingt communes du Tarn**. Mis en regard des 0,004 % du
bloc retiré, l'écart est de **quatre ordres de grandeur**.

Et les entrées sont **datées, et échelonnées** — ce n'est pas un second bloc :

| Paramètre | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| Hydrazide maléique | 0 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| Flufénacet ESA | 0 | 50 | 95 | 98 | 100 | 100 | 100 | 100 |
| Métolachlore NOA 413173 | 0 | 0 | 0 | 49 | 100 | 100 | 100 | 100 |
| Chloridazone desphényl | 0 | 0 | 0 | 49 | 100 | 100 | 100 | 100 |
| **Chlorothalonil R471811** | 0 | 0 | 0 | 3 | 46 | 100 | 100 | 100 |
| **Chlorothalonil R417888** | 0 | 0 | 0 | 0 | 0 | **20** | 100 | 100 |

(en % des bulletins complets du Tarn ; 164 bulletins en 2019, 217 en 2024,
56 en 2026)

La dernière ligne est la plus parlante. **Le R417888 entre au panel en 2024** —
l'année de l'avis ANSES du 29 avril 2024 qui le classe *pertinent* à 0,1 µg/L,
quand le R471811 est classé *non pertinent* à 0,9 (§2.7). Le programme
d'analyse suit la décision réglementaire, dans l'année. C'est la thèse du
projet vue par l'autre bout : **le réétalonnage ne déplace pas seulement le
seuil auquel on compare, il déplace la liste de ce qu'on regarde.**

Ce qu'il faut se garder d'en conclure, et c'est le §2.4 : on **ne sait pas** si
le R471811 était présent dans l'eau du Tarn avant 2022. Il n'y était pas
cherché. Ce n'est ni une absence ni une apparition — c'est un indéterminé, et
il porte sur vingt communes et trois années.

### La seule série qu'on ait le droit de lire — et elle est plate

Le §2.11 interdit depuis le 9 août 2026 toute série temporelle à panel
variable. La règle était écrite, rien ne l'outillait : deux vues le font
désormais (`v_panel_constant`, `v_serie_panel_constant`), et le panel constant
se définit sans arbitrage — cherché sur ≥ 75 % des bulletins **chaque** année
documentée du département.

Tarn : **260 paramètres**, constants sur les **11 années** du corpus.

| Année | Bulletins | Communes | Mesures | Quantifiées | Pour mille |
|---|---|---|---|---|---|
| 2016 | 95 | 46 | 24 687 | 451 | 18,27 |
| 2017 | 103 | 51 | 26 588 | 466 | 17,53 |
| 2018 | 114 | 50 | 29 380 | 530 | 18,04 |
| 2019 | 164 | 70 | 42 363 | 681 | 16,08 |
| 2020 | 121 | 52 | 31 423 | 562 | 17,88 |
| 2021 | 158 | 74 | 41 072 | 787 | 19,16 |
| 2022 | 156 | 66 | 40 536 | 765 | 18,87 |
| 2023 | 202 | 76 | 52 493 | 968 | 18,44 |
| 2024 | 217 | 73 | 56 406 | 998 | 17,69 |
| 2025 | 189 | 72 | 49 100 | 851 | 17,33 |
| 2026 | 56 | 44 | 14 560 | 253 | 17,38 |

**Onze ans, de 16,1 à 19,2 pour mille, sans tendance.** À périmètre de mesure
constant, ce que le Tarn trouve ne bouge pas. Toute la variation du dossier
tarnais entre 2016 et 2026 est une variation de **ce qu'on a cherché**, pas de
ce qu'on a trouvé.

C'est ce qui rend la règle du §2.11 opposable plutôt que déclarative : sans
elle, la chute de 606 à 352 paramètres se lirait comme une amélioration.

### Une seule vague — et une seconde, ailleurs et plus tard

Vérifié d'une année à la suivante, le Tarn ne connaît **qu'un** basculement.

| Passage | Retirés | Entrants |
|---|---|---|
| 2016→2017, 2017→2018, 2018→2019 | 0 | 0 |
| **2019→2020** | **298** | **30** |
| 2020→2021 | 9 | 4 |
| 2021→2022 … 2025→2026 | 0 | ≤ 1 |

(retiré = ≥ 75 % des bulletins une année, ≤ 10 % la suivante)

Le programme d'analyse tarnais est donc **stable huit années sur dix**. Ce
n'est pas une érosion continue : c'est une décision, prise une fois, appliquée
d'un coup. Ce qui rend d'autant plus lisible le fait qu'elle n'ait aucune cause
documentée à sa date.

**Mais un second mouvement existe, et il ne ressemble pas au premier.** Le
signal repéré sur 45 bulletins — l'odeur — tient à 1 575, et il se précise :

| Année | 2016-2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Odeur, % des bulletins du Tarn | 93 à 100 % | **67,3 %** | **62,4 %** | **0,0 %** |
| dénominateur | 95 à 202 | 217 | 189 | 56 |

Huit ans entre 93 et 100 %, puis une décrue sur deux ans, puis **zéro sur 56
bulletins**. Ce n'est ni la vague de 2020 (un pesticide n'y est pour rien), ni
sa forme (une marche) : c'est un retrait progressif puis total, sur un
paramètre organoleptique. Réserve : 2026 est une année partielle, 56 bulletins
sur les ~190 d'une année pleine — la valeur est nette, la date de la bascule
finale ne l'est pas encore.

Deux mouvements, deux formes, deux dates. La machinerie les sépare ; elle ne
dit d'aucun des deux **pourquoi**.

### Ce que ce constat n'est toujours pas

C'est un **dénombrement**, l'indicateur A, et le piège du chantier reste entier :
**« plus cherché » n'est pas « retiré du contrôle »**. Le corpus ne porte aucun
identifiant de laboratoire — `code_lieu_analyse` vaut toujours `L` — donc rien
n'y permet de distinguer un changement de programme d'un changement de
prestataire.

Et c'est **un seul département**. Rien ici ne dit qu'il se passe la même chose
ailleurs, ni à la même date — c'est la première chose à vérifier au département
suivant, et la vue `v_parametre_presence_dept` est faite pour ça.

### Reste à faire

1. **Lire le texte officiel de l'instruction** sur circulaires.legifrance, et
   vérifier si son annexe est antérieure ou si elle reprend des listes déjà en
   vigueur. C'est ce qui départage les lectures 1 et 3.
2. **Un second département**, pour savoir si la rupture est nationale ou
   tarnaise, et surtout **si elle y porte la même date**. Un département qui
   basculerait début 2021 pointerait vers l'instruction ; un autre qui
   basculerait aussi en 2020 pointerait vers une pratique antérieure.
3. ~~**La liste nominative des 278 disparus**~~ — **fait le 9 août 2026.**
   `src/etude_panel.py` la verse dans `data/etudes/` : `journal_abandons.csv`
   (une ligne par commune × paramètre abandonné) et `parametres_abandonnes.csv`
   (le cumul), plus `panel_constant.csv` et `serie_panel_constant.csv`.
4. **Le second département dira aussi si la rotation est nationale.** Le Tarn
   montre 34 paramètres entrants et un métabolite quantifié dans 20 communes ;
   savoir si les mêmes entrent ailleurs, et aux mêmes dates, vaut autant que la
   question du retrait.

Ce qui a changé le 9 août 2026, c'est qu'elle est prête **à dire un zéro et à
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

### Ce que le Tarn entier en dit — 9 août 2026

Le chantier a été construit sur 45 bulletins. Il en a maintenant 1 575 pour le
seul Tarn, et le constat change d'échelle **et de nature**.

**1 295 mesures aveugles, sur 1 128 des 1 575 bulletins — 72 %.**

| Tranche de `aveugles_pour_mille` | Bulletins |
|---|---|
| 0 | 447 |
| 0 à 3 ‰ | 355 |
| 3 à 6 ‰ | 633 |
| plus de 6 ‰ | 140 |

**Une molécule porte l'essentiel : l'hydrazide maléique**, 1 051 mesures
aveugles sur 123 communes. Elle entre au panel en 2020 — c'est l'une des
entrées que C2 documente — et depuis six ans elle n'a **jamais été quantifiée
une seule fois**, parce que la LQ courante de 0,5 µg/L vaut cinq fois sa limite
de 0,1. Le contrôle sanitaire la cherche partout et ne peut rien en dire nulle
part. Quarante-huit mesures à 0,05-0,1 µg/L en 2024-2025 établissent que dix
fois plus fin est faisable, et a été fait.

**Ce que le volume oblige à retirer.** Sur 45 bulletins, les LQ extrêmes
suggéraient une dispersion entre laboratoires d'un facteur 4 000
(prosulfocarbe, 0,005 à 20 µg/L). Le corpus complet la dément : ces 20 µg/L
sont **deux mesures de 2017** sur 1 573, et l'aminotriazole à 50 µg/L en est
**quatre**. Ce ne sont pas des laboratoires inégaux, ce sont des valeurs
isolées. Le fait réel est l'inverse d'une dispersion — c'est un **plafond
systématique et partagé** sur une molécule. La formulation « telle commune est
moins bien analysée que sa voisine » ne tient pas ici et ne doit pas être
écrite ; le niveau 3 garde tout son sens, mais ce qu'il montre est un ordre de
grandeur commun, pas un classement.

**Le taux monte quand le panel tourne.** Les bulletins d'avant 2020 (626
paramètres en moyenne) portent 0,12 ‰ d'aveugles ; ceux d'après (355) en
portent 3,55 ‰. Le programme d'analyse s'est resserré **et** ce qui est entré à
la place est moins concluant. Les deux faits sont indépendants et se cumulent.

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
- l'étiquette envers Hub'Eau (§3.2) devient une contrainte réelle et non plus
  théorique : un département = plusieurs milliers d'appels ;
- la vitrine statique approche 1,7 Go à l'échelle nationale et demandera d'être
  découpée par département (§8ter). Ce n'est pas bloquant avant d'y être.

### Quatre décisions de Yannick — 8 août 2026

| Question | Tranché |
|---|---|
| par où commencer | **le Tarn (81)** |
| profondeur | **tous les bulletins complets de chaque point d'eau, sans borne de date** |
| cache brut des réponses Hub'Eau | **oui**, un `.jsonl.gz` par bulletin |
| prose à l'échelle | **dérivée partout, proposée seulement sur les cas de thèse** |

Le Tarn n'était pas le choix proposé — le carnet penchait pour le 28, plus
dense. Il est meilleur : **les deux seuls mélanges entièrement reconstitués du
corpus y sont** (LOUBERS 80/20, VALLEE DU CEROU 50/50, chantier C7), et **les
trois valeurs de LQ de l'hydrazide maléique** — 0,05 / 0,5 / 2,5 µg/L, le
facteur 50 du chantier C4 — sont tarnaises toutes les trois. Un seul
département nourrit donc C2, C4 et C7 en même temps.

### Ce que « `fetch_departement.py` est prêt » cachait

Le carnet écrivait que le script était prêt et n'avait jamais servi. C'était
vrai de la collecte brute, et faux de tout le reste : **le dépôt portait deux
chemins de collecte qui ne faisaient pas la même chose.**

| | `observer.py` | `fetch_departement.py` |
|---|---|---|
| repli sur le réseau | oui | **non** |
| écrit `couverture_communes` | oui | **non** |
| fige | oui | **non** |
| journal de reprise | **non** | oui |

Lancé tel quel sur le Tarn, il aurait rempli `prelevements` et `mesures` sans
produire **une seule ligne figée ni une seule commune sur la carte** — donc
aucune page publiable, et pas de « non documentée » alors que c'est précisément
ce qu'un département entier devait enfin montrer. C'est la leçon du chantier C8
rencontrée une seconde fois : une règle recopiée à deux endroits diverge, et
rien ne le signale.

La règle de couverture vit désormais dans **`src/collecte.py`**, appelée par les
deux points d'entrée. Chacun garde ce qui lui est propre — `observer.py` résout
un code postal et restitue, `fetch_departement.py` énumère, journalise et fige.

### Ce que la sonde a établi sur l'API — 8 août 2026

Quatre faits mesurés, aucun documenté par Hub'Eau. Ils commandent la collecte :

| Ce qui a été testé | Résultat |
|---|---|
| `code_departement` | **honoré** — 1 024 569 lignes pour le Tarn contre 130 042 089 sans filtre |
| `nom_departement` | **ignoré en silence**, renvoie la France entière — le piège de `communes_udi`, à l'identique |
| `code_prelevement` | **honoré exactement** — `count` = le nombre de paramètres du bulletin, **0,1 s** |
| pagination par page | tient jusqu'au bout (205 pages), ordre stable, `sort=asc/desc` accepté |

**La voie départementale est pourtant la mauvaise**, et c'est contre-intuitif :
les pages profondes coûtent quatre fois plus que les premières — 4,6 s pour la
page 3, 20,6 s pour la page 100 — parce que le serveur balaie l'offset.
L'inventaire du Tarn en un balayage départemental prendrait ~45 min ; commune
par commune, où chaque jeu de résultats reste petit, **17 min**. Le filtre reste
utile pour compter, pas pour collecter.

Deux conséquences dans le code :

- `fetch_bulletin` interroge désormais `code_prelevement` directement, au lieu
  de demander toute la commune sur une fenêtre de deux jours et d'écarter le
  reste côté client. Un **garde-fou** lève une erreur si une ligne étrangère
  apparaît : si l'API cessait un jour d'honorer ce filtre — ce que fait déjà
  `communes_udi` — on ingérerait le contenu d'autres prélèvements sans rien voir ;
- `communes_departement()` rapporte les **centroïdes en un seul appel**, là où
  il fallait un `commune_par_insee` par commune. `couverture_communes` porte les
  coordonnées, et sans elles une commune non documentée n'a nulle part où
  s'afficher sur la carte (§8bis, obligation 4).

### Le cache brut — `src/brut.py`

`data/brut/<dept>/<code_prelevement>.jsonl.gz`. Un bulletin de 317 paramètres
pèse 421 Ko en JSON et **16 à 20 Ko gzippé**.

Il sépare deux gestes qui étaient confondus : **collecter** — une fois, en
ligne, poliment — et **ingérer** — autant de fois qu'on veut, hors ligne. Sans
lui, corriger un bug d'ingestion ou ajouter une colonne obligerait à redemander
des milliers de bulletins à un service public gratuit, c'est-à-dire exactement
la charge abusive que le §3.2 interdit, et entièrement évitable : la réponse ne
change pas, c'est notre lecture qui change.

Il garde la réponse de la source, pas notre interprétation : aucun champ écarté,
aucune valeur convertie, écriture atomique par fichier temporaire renommé — un
`.gz` tronqué serait relu comme un bulletin valide, et un bulletin amputé qui
passe sous `SEUIL_COMPLET` disparaît de l'analyse sans que rien ne le signale
(§2.3). Ni verdict ni seuil n'y entrent : ceux-là dépendent du référentiel daté
et vivent dans les tables figées avec leur version (§8bis).

Non versionné, **mais c'est le seul objet du dépôt qu'on ne peut pas
refabriquer seul.** À sauvegarder hors git.

### L'essai mesuré — 10 communes du Tarn, 8 août 2026

```bash
py -X utf8 src/fetch_departement.py --dept 81 --limite 10 --tous
```

| | |
|---|---|
| durée | 4,5 min — **27 s par commune** |
| bulletins rapatriés | 51 du réseau, 1 relu au cache |
| cache | 1,0 Mo pour 51 bulletins |
| statuts | 4 `analysee`, **6 `rattachee_reseau`**, 0 `non_documentee` |
| inscrites d'office | 7 communes, qui servent de repli à une voisine |

**Six communes sur dix n'ont aucun bulletin complet à elles.** Sur 45 bulletins
le repli réseau était un cas particulier ; à l'échelle, c'est le cas majoritaire,
et l'obligation d'affichage n° 5 du §8bis — dire où l'analyse a été prélevée —
devient la règle plutôt que l'exception.

Le corpus passe de 45 à **94 bulletins** et de 15 617 à **35 191 mesures**, sur
dix communes seulement.

### Ce que dix communes ont déjà débloqué

**Le verrou du chantier C3 saute.** Le carnet écrivait : « aucune paire ne
partage un `code_installation_amont` ; zéro installation du corpus porte deux
bulletins complets ». Il y en a maintenant **trois**, et Albi porte à elle
seule 29 bulletins de 2021 à 2026, dont une longue série sur STATION CAUSSELS.
C'est exactement l'objet de C3 — l'évolution d'un même point d'eau — et il
n'attendait que le volume.

**Le signal du chantier C2 devient lisible sur un point d'eau suivi.** Albine :
627 paramètres en 2016, 2017, 2018 et 2019 ; 345 à 409 depuis 2020. Sur la même
installation, dix ans de suite.

**Le barème de LQ a bougé, comme annoncé.** L'hydrazide maléique passe d'une
base de 29 bulletins à **71**, sur 5 départements, étendue inchangée (0,05 à
2,5 µg/L). Les fiches publiées affichent donc une base périmée tant qu'on n'a
pas republié — c'est le §2.14 qui joue exactement comme prévu, et c'est la
raison pour laquelle la base s'affiche avec le barème. Les mesures aveugles
passent de 46 sur 39 bulletins à **90 sur 81**.

### Ce que le contrôle a attrapé, et qui n'est pas un défaut

`tests/test_sorties.py` échoue : **« 72 communes couvertes, 12 sans page »**.
C'est le contrôle qui fait son travail — publier est un geste séparé de
collecter (§8quater bis), et c'est cette confusion qui avait laissé 28 communes
invisibles le 8 août au matin. Les 12 communes le resteront jusqu'à une
publication, qui refera aussi tous les barèmes de LQ.

### Ce qui reste à faire

1. ~~**Le Tarn en entier**~~ — **FAIT le 8 août 2026. 314 communes sur 314,
   zéro erreur.** 2 h 49 de collecte, plus deux rattrapages.

   | | | était |
   |---|---|---|
   | bulletins figés | **1 595** | 45 |
   | mesures | **684 883** | 15 617 |
   | communes couvertes | **339** — 143 analysées, 196 rattachées | 60 |
   | cache brut | 1 575 bulletins, **32,4 Mo** | — |
   | bulletins conformes 2026 avec bascule | **109** | 8 |

   Un défaut trouvé au dépouillement, et corrigé : **neuf communes avaient
   échoué sur des coupures réseau de Hub'Eau** — sept d'affilée, dont Castres et
   Cordes-sur-Ciel — et **la reprise les tenait pour traitées**. Elles seraient
   restées « non documentées » à tort, ce qui est le pire cas du §2.4 transposé
   à la commune : une absence de donnée présentée comme un état stable, alors
   qu'elle n'était qu'un incident de réseau. `a_faire` et `--termine` comptent
   désormais une erreur comme du travail restant, et une rafale d'échecs
   déclenche une pause croissante — insister au même rythme ne sert à rien et
   n'est pas courtois envers un service public gratuit (§3.2). Les neuf ont été
   rattrapées ; Paulinet à elle seule portait 98 bulletins.

   Les autres chantiers en sortent transformés : **165 installations portent
   plusieurs bulletins** (76 en portent au moins cinq) là où le corpus entier
   n'en portait aucune — **le chantier C3 n'attend plus rien** ; les mesures
   aveugles passent de 46 sur 39 bulletins à **1 316 sur 1 143**, et la base du
   barème de LQ de 29 à **1 595 bulletins** (C4) ; et le chantier C2 rend son
   premier motif, une rupture datée de janvier 2020 — voir sa section.
2. **Republier**, ce qui refait les 12 pages manquantes et met à jour toutes les
   bases de barème. À faire après la collecte, pas pendant.
3. **Le coût du figeage** : `figer.figer()` recalcule tout le corpus à chaque
   appel, bulletin par bulletin en Python. Invisible à 94 bulletins, à mesurer
   à 1 500. C'est le prochain goulot, pas la collecte.
4. **`v_parametres_non_apparies` passe à 103 libellés.** Le diagnostic du §4
   grossit avec le corpus : un paramètre sans seuil existe en base et ne pèse
   sur aucun verdict. À relire avant de publier le département.
5. **La prose** : `rediger_lot.py` fabrique déjà les dossiers et contrôle les
   réponses. Il lui manque un critère de sélection « cas de thèse », sinon
   `--dossiers` en produirait un par bulletin du département.

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

## C10 — ARRÊTÉS

### Les dérogations préfectorales, département par département, sur dix ans

### Ce que Yannick demande

> « Pour le Tarn il a été trouvé des arrêtés préfectoraux qui autorisent le
> dépassement de seuil ! Il y a ça dans chaque département, je propose une
> recherche à date avec un historique sur 10 ans par exemple de l'évolution de
> ces arrêtés, et cela par département. Donc chaque département aura sa liste
> d'arrêtés spécifiques ! »

### Ce que Yannick demande — l'élargissement du 11 août 2026

> « pour chaque département, je souhaite travailler sur l'historique à partir de
> 2016 des arrêtés préfectoraux qui portent sur l'eau de consommation. Je veux
> lister et quantifier les arrêtés portant sur l'interdiction de boire l'eau, de
> contourner une norme, etc. Je veux quelque chose qui se lance de manière
> automatisée lorsque tout un département est collecté. »

Trois déplacements par rapport à la commande d'origine, et il faut les nommer
parce qu'ils changent le chantier :

| | commande du 9 août | commande du 11 août |
|---|---|---|
| objet | la **dérogation** seule | **tout acte** touchant l'eau de consommation |
| livrable | une liste | une liste **et son dénombrement** |
| départ | un geste à la main | **accroché à la fin de collecte d'un département** |

**Deux décisions prises le 11 août 2026, elles commandent toute la suite :**

1. **Large en collecte, fin en qualification.** On ramasse et on compte tout
   acte qui touche l'eau de consommation — y compris les périmètres de
   protection et les autorisations de distribution, qui ne portent aucune
   thèse. Motif : sans eux il n'y a **pas de dénominateur**, et « 37 arrêtés de
   restriction dans le Tarn » ne se lit pas sans savoir sur combien. C'est le
   §2.8 appliqué au corpus documentaire. La qualification fine, elle, ne porte
   que sur les restrictions et les dérogations.
2. **L'automatisme s'arrête aux candidats.** L'enchaînement moissonne, extrait,
   découpe, pré-filtre et fabrique les dossiers, puis rend la main :
   *« 81 : 412 actes eau, 37 candidats, dossiers prêts »*. La lecture des actes
   reste un geste que Yannick lance, exactement comme la rédaction en lot —
   un arrêté est un texte de droit, et §3 du mode opératoire interdit d'appeler
   une API facturée à part depuis un script planifié.

### Pourquoi c'est le chantier le plus proche de la thèse

Le projet a documenté jusqu'ici **deux** mécanismes par lesquels une eau devient
conforme sans avoir changé :

| | Mécanisme | Où il est écrit |
|---|---|---|
| 1 | **le réétalonnage** — la limite nationale se déplace | la thèse fondatrice |
| 2 | **la dilution** — le mélange dilue un captage dégradé | §7bis, chantier C7 |
| 3 | **la dérogation** — la limite est relevée pour cette eau-là | **ce chantier** |

Le troisième est le plus direct, et c'est le seul qui soit **nominatif**. Un
réétalonnage est anonyme : une valeur change dans un arrêté national et
personne n'est désigné. Une dérogation, elle, porte un numéro, une date, une
signature, un périmètre nommé et une durée. C'est la formule du projet — *ce
n'est pas l'eau qui est devenue potable, c'est la limite qui a bougé* — écrite
noir sur blanc par l'administration, pour une commune précise.

C'est aussi le mécanisme le plus exposé au §2.1. Une dérogation est **légale**,
motivée, et généralement accordée parce qu'il n'existe pas d'autre moyen
raisonnable de maintenir la distribution. L'objet du chantier est de rendre
visible qu'elle existe et combien de temps elle dure — **jamais** de mettre en
cause le préfet, l'ARS ou l'exploitant qui l'ont demandée ou signée.

### Ce que la base dit aujourd'hui — vérifié le 9 août 2026

Base interrogée après la collecte du Tarn : **3 193 bulletins complets,
1 372 988 mesures, 310 communes**.

**Aucune trace visible de dérogation dans le corpus actuel.** Deux motifs
auraient pu en être le signe ; ni l'un ni l'autre n'en est un :

- les **13 écarts** entre notre seuil 2026 et la limite déclarée par la source
  (`v_ecarts_referentiel_source`) sont, à une ligne près, la famille des
  métabolites — 0,9 chez nous, 0,1 déclaré. C'est le réétalonnage d'avril 2024,
  pas une dérogation locale ;
- la **limite déclarée des nitrites varie** à l'intérieur d'un même département :
  0,5 mg/L sur 1 132 mesures du Tarn, 0,1 sur 184 ; 0,5 sur 107 mesures d'Eure-
  et-Loir, 0,1 sur 1 458. Ce n'est très probablement pas une dérogation mais la
  distinction entre la limite en distribution et la référence en sortie de
  production — **à confirmer sur source primaire avant d'en dire quoi que ce
  soit**, et c'est le premier piège du chantier.

Conclusion provisoire, et elle oriente tout le reste : **une dérogation ne se
lit pas dans les données Hub'Eau.** Elle n'existe que dans l'arrêté. Le travail
est documentaire, pas d'API.

### Ce qu'il faut établir AVANT toute collecte

Rien de ce qui suit n'est acquis ici, et aucune de ces valeurs ne doit être
écrite de mémoire (§2.7). La première tâche du chantier est de les lire sur
source primaire et de les inscrire dans `docs/INDEX_SOURCES.md` :

1. **le fondement juridique exact** — le mécanisme de dérogation aux limites de
   qualité de l'eau destinée à la consommation humaine relève du code de la
   santé publique, en transposition des directives européennes. Les articles
   précis, `a_verifier` ;
2. **le périmètre** — sur quels paramètres une dérogation est possible, et sur
   lesquels elle ne l'est pas. La bactériologie en est vraisemblablement exclue,
   `a_verifier` ;
3. **la durée maximale**, son renouvellement, et le plafond cumulé,
   `a_verifier` ;
4. **qui publie l'acte et où il fait foi** — recueil des actes administratifs de
   la préfecture, site de l'ARS, autre. `a_verifier`. Légifrance ne porte pas
   les actes préfectoraux ;
5. **la distinction avec les objets voisins**, qui est la question de méthode
   centrale de ce chantier :

| Objet | Ce qu'il fait | À ne pas confondre |
|---|---|---|
| **dérogation** | autorise à distribuer au-dessus d'une limite, pour un temps | — |
| **restriction de consommation** | interdit ou limite l'usage | c'est l'inverse d'une dérogation |
| **valeur sanitaire transitoire** | seuil au-delà duquel on restreint | déjà rencontrée : les 3 µg/L UBA du R417888 (§2.7) |
| **valeur indicative** | repère sans force de limite | les 0,9 µg/L du R471811 |

Confondre les deux premiers inverserait le sens du fait. Confondre les deux
derniers avec une limite de conformité est **l'erreur déjà commise une fois**
dans ce projet, sur le chlorothalonil.

### La forme — un fichier versionné, comme le référentiel

Un arrêté est une décision datée et attribuée : exactement ce que git sait
journaliser. Sur le modèle de `referentiel_seuils.csv`, séparateur `;`, barre
verticale à l'intérieur des cellules :

```
referentiel/derogations.csv
  departement ; reference_arrete ; date_signature ; date_debut ; date_fin ;
  perimetre ; codes_insee ; code_udi ; parametre ; valeur_derogee ; unite ;
  motif ; source ; fiabilite
```

Deux exigences non négociables : **une ligne sans `date_fin` n'est pas
exploitable**, et **une ligne sans source primaire reste `a_verifier`** et ne
peut produire aucun verdict.

### La dépendance technique, et elle est bloquante

Le modèle **ne sait pas exprimer une date de fin d'applicabilité**. Il connaît
`date_applicabilite_2026` — à partir de quand — et c'est déjà signalé comme un
manque au §2.13 pour les chlorites, dont la référence a expiré le 31 décembre
2025 sans remplacement connu.

Or une dérogation est bornée **des deux côtés** par nature : elle commence et
elle finit. Ce chantier ne peut donc pas être livré sans ajouter la borne haute
au modèle de seuils. **C'est la première tâche technique**, et elle profitera
aussi aux chlorites.

### Le croisement qui donnera la démonstration

Une fois les deux en place, la requête qui porte le chantier :

> les bulletins déclarés **conformes** alors qu'ils tombent dans la fenêtre
> d'une dérogation portant sur un paramètre qu'ils dépassent.

Chaque ligne retournée est un cas où la conformité est locale, datée, et
signée. C'est le pendant nominatif de la requête de la thèse.

### Le coût, et le découpage qui le rend tenable

Dix ans de recueils d'actes administratifs pour cent départements est hors de
portée d'un seul geste, et l'essentiel serait sans rapport avec l'eau.
Découpage proposé :

1. **le Tarn d'abord**, puisque des arrêtés y ont déjà été trouvés. Il sert de
   patron : où chercher, à quoi ressemble un acte, quels mots le désignent ;
2. **puis un département à la fois, adossé à C6** — un département dont on
   collecte les bulletins voit ses arrêtés collectés dans la foulée. La liste
   d'arrêtés et le corpus de mesures avancent ensemble, sinon l'une décrit une
   zone que l'autre ne couvre pas ;
3. **la lecture de chaque acte reste humaine ou assistée, jamais automatique.**
   Un arrêté est un texte de droit ; en extraire un paramètre et une valeur
   par motif est exactement le genre d'inférence qui a produit l'erreur du
   R417888.

### Les pièges, en clair

- **absence de trace ≠ absence de dérogation.** Ne pas trouver d'arrêté dans un
  recueil ne prouve rien : trois états, pas deux (§2.4). Un département sans
  ligne est un département **non instruit**, pas un département sans dérogation ;
- **une dérogation porte sur un périmètre nommé** — une UDI, une commune, un
  réseau — jamais sur un département entier. La rattacher au mauvais périmètre
  fabriquerait des faux positifs à la chaîne ;
- **le faux positif coûte plus cher que le faux négatif** (§2.13). Dans le
  doute sur la portée ou les dates d'un arrêté, on ne prononce rien ;
- **étiquette** — les sites de préfecture ne sont pas Hub'Eau, mais la règle du
  §3.2 vaut : débit modéré, journal de reprise, agent identifiant le projet.

---

### Mise à jour du 11 août 2026 — la reconnaissance du Tarn

**Ce qui suit a été lu ou mesuré, pas supposé.** Aucune collecte n'a été lancée :
quatre pages du site de la préfecture ont été consultées et **un seul recueil a
été téléchargé et sondé localement**. Les comptes qui en viennent portent sur ce
recueil-là et sur rien d'autre.

#### Où la matière se trouve, et sous quelle forme

Le recueil des actes administratifs du Tarn est publié sur
`www.tarn.gouv.fr`, rubrique *Publications → RAA*. L'index annonce les années
**2005 à 2026** : la profondeur d'archive, qui était le risque n° 1 du chantier,
**n'en est pas un ici**. Reste à vérifier qu'il en va de même ailleurs — un
département n'est pas cent.

L'arborescence est régulière : une page par année, une page par mois, une page
par recueil, avec pagination sur les pages de mois. Les fichiers, eux, sont à des
adresses opaques du type
`/contenu/telechargement/10325/112034/file/recueil-81-2016-050-…pdf` :
**les URL ne se fabriquent pas, il faut parcourir les pages.** C'est ce qui
décide la forme du moissonneur.

Deux repères de volume, et ce sont des repères, pas un compte : janvier 2016
porte au moins dix recueils sur sa première page **et en a une seconde** ; le
recueil `81-2026-286` est publié le 17 juillet 2026. L'ordre de grandeur est
donc de la centaine à quelques centaines de recueils par an — **à mesurer au
premier moissonnage, pas à annoncer.**

#### Le recueil sondé — 81-2026-286, publié le 17 juillet 2026

| ce qui a été mesuré | valeur |
|---|---|
| pages | 32 |
| caractères extraits | 65 189 |
| pages quasi vides (indice de scan) | **0** |

**C'est du texte, pas une image.** `pypdf`, déjà installé pour le perchlorate,
suffit. Une réserve : le recueil mensuel `81-2016-050` **dépasse 10 Mo** — les
fichiers ne sont pas petits, et rien ne dit encore que ceux de 2016 soient
également extractibles.

#### La découverte technique qui change l'architecture — le sommaire est structuré

Chaque recueil s'ouvre sur un sommaire régulier : le service émetteur, puis une
ligne par acte. Relevé littéralement :

```
Direction Départementale des Territoires / Service Eau Risques
Environnement Sécurité
81-2026-07-16-00004 - 260718 AP restriction Vdef-1 (29 pages) Page 3
```

On y lit d'un coup **l'identifiant de l'acte, sa date au jour près, son
intitulé, sa longueur et sa page de début**. Conséquence : le découpage
recueil → actes se fait **sur le sommaire**, jamais en cherchant des en-têtes
dans le corps — les motifs habituels (`Arrêté n°`, `ARRÊTÉ`, `DÉCISION`) sont
d'ailleurs **absents** du document sondé, un découpage qui s'y fierait rendrait
zéro acte. Le sommaire donne en prime le service signataire, qui est le premier
discriminant du pré-filtre.

#### Le piège principal, mesuré plutôt que redouté

L'acte que porte ce recueil est un **arrêté sécheresse** de la direction
départementale des territoires. Comptes relevés dans son texte :

| terme | occurrences |
|---|---|
| « restriction » | 91 |
| « eau potable » | 29 |
| « alerte » | 468 |
| « crise » | 247 |
| « sécheresse » | 22 |
| **« consommation humaine »** | **0** |
| **« agence régionale de santé »** | **0** |

Un pré-filtre bâti sur « restriction » et « eau potable » **le retiendrait**, et
il n'a rien à voir avec la potabilité : il limite l'arrosage et l'irrigation, il
ne dit rien de la qualité de l'eau bue. Les arrêtés sécheresse sont nombreux,
volumineux, annuels et saturent aussi la recherche web — chercher « arrêté
préfectoral restriction eau Tarn » ne rend qu'eux.

**Donc : le pré-filtre ne peut pas être une liste de mots isolés.** Il combine
au minimum le service émetteur, un terme d'inclusion fort — « consommation
humaine », « unité de distribution », l'agence régionale de santé — et une
exclusion explicite du vocabulaire sécheresse. C'est ce que porte
`referentiel/motifs_arretes.csv`, versionné parce que c'est une décision
éditoriale, pas un détail de code.

#### Pas de raccourci national

Cherché, non trouvé. La donnée ministérielle sur les dérogations **n'est plus
publiée depuis 2012** : la carte des dérogations de la Fondation Danielle
Mitterrand et de *60 millions de consommateurs* repose sur les données de
l'automne 2012 et n'a jamais été mise à jour — « plus d'un millier de
dérogations réparties sur 419 communes ». **Chiffre de seconde main, jamais
vérifié par le projet, cité ici comme ordre de grandeur historique et rien
d'autre.** Il n'entre nulle part sans lecture d'une source primaire.

C'est aussi ce qui donne au chantier sa portée réelle : si l'information
nationale s'arrête en 2012, la reconstituer département par département n'est
pas un doublon, c'est **la seule voie ouverte**.

#### La base juridique — lue le 11 août 2026, fiche `REG-09`

Faite, en agent de fond `opus`, sur le modèle de `docs/CONSIGNE_SOURCAGE.md`.
La fiche `REG-09_FR_csp-derogations-et-restrictions_2003-2026.md` est archivée
avec les autres sources réglementaires et sa ligne est à
`docs/INDEX_SOURCES.md`. **Deux affirmations centrales ont été recontrôlées à la
main sur Légifrance** avant d'être versées : le statut de R. 1321-34 et le
régime de la seconde dérogation.

**Cinq faits qui changent le chantier, et pas seulement le remplissent :**

1. **Le dénombrement sera structurellement minorant, et il faut le dire partout
   où le chiffre paraît.** Le silence de l'administration vaut acceptation au
   bout de quatre mois sur une première demande, six sur une seconde : **une
   dérogation peut exister sans qu'aucun arrêté ait été publié.** Compter les
   actes d'un recueil ne compte donc pas les dérogations, il compte **les
   dérogations écrites**. C'est le §2.8 dans sa forme la plus dure — un compte
   sans son dénominateur est une demi-vérité, et ici le dénominateur est
   inconnaissable par cette voie.
2. **Une rupture datée traverse la période étudiée.** L'article qui portait la
   troisième dérogation est **abrogé avec effet au 1er janvier 2024**. Le
   plafond cumulé passe de neuf ans à six. Une série ouverte en 2016 franchit
   cette date : la comparer d'un bout à l'autre sans la marquer serait
   exactement l'erreur du §2.5, transposée de la valeur à la procédure.
3. **L'objet d'une dérogation est l'unité de distribution, pas la commune.**
   Le corpus sait déjà travailler à cette maille. Le rattachement géographique
   passe par là, et une dérogation recopiée au niveau communal serait un faux.
4. **Il n'existe pas de dérogation bactériologique** — le champ est limité aux
   paramètres chimiques, et exclut aussi les références de qualité, les valeurs
   indicatives et les valeurs de vigilance. C'est un **contrôle** : un acte
   qualifié « dérogation » sur un paramètre microbiologique est une lecture
   fausse, pas une découverte.
5. **Les deux actes ne sont pas seulement inverses, ils sont exclusifs au-delà
   d'un certain point.** Sous la valeur sanitaire maximale, la dérogation est
   possible ; au-dessus, aucune dérogation ne peut être octroyée et la
   restriction des usages alimentaires s'impose. **La bascule de l'un à l'autre
   est donc lisible, et elle est un résultat en soi.**

**Et un gain pour le pré-filtre** : le **visa** discrimine mieux que n'importe
quel mot du corps du texte. Un acte de dérogation vise `R. 1321-31` et suivants,
une restriction sanitaire vise `R. 1321-29`, un arrêté sécheresse vise le code
de l'environnement. `referentiel/motifs_arretes.csv` a été refondu là-dessus, et
enrichi du vocabulaire littéral de trois arrêtés préfectoraux réellement ouverts.

**Un piège nouveau, trouvé sur un acte réel** : la formule *« hors eau destinée à
la consommation humaine »* contient mot pour mot le terme d'inclusion le plus
fort de la liste **et signifie l'inverse**. Une inclusion qui n'apparaît que dans
une expression d'exclusion ne compte pas — c'est la cinquième règle de
combinaison du fichier de motifs.

**Trois réserves, dans l'ordre d'importance :**

1. **Aucun arrêté de dérogation postérieur au 1er janvier 2024 n'a été lu.** Le
   régime a changé à cette date ; la forme des actes a pu changer avec lui, et
   le pré-filtre est calé sur des actes de l'ancien régime ;
2. l'instruction ministérielle qui organise le **bilan national des
   dérogations** n'a pas pu être ouverte — c'est pourtant la piste la plus
   directe vers un ordre de grandeur national, et elle reste à instruire ;
3. la version française de la directive européenne étant inaccessible, **les
   citations européennes de la fiche sont en anglais**. À signaler dans toute
   sortie publique qui s'y appuierait (§2.7).

#### Ce que la reconnaissance ne dit pas

Quatre inconnues assumées, à lever au premier moissonnage et pas avant :

1. si les recueils de 2016 sont eux aussi du texte extractible ;
2. le compte exact de recueils par année ;
3. s'il existe un moteur de recherche plein texte sur le site — il n'y en a
   aucun au niveau du RAA, et aucun n'a été localisé ailleurs ;
4. **s'il existe seulement des arrêtés de restriction de consommation dans le
   Tarn sur la période.** La recherche web n'en rend aucun. **Ne rien conclure
   de cette absence** : c'est le §2.4 appliqué au document — non trouvé n'est
   pas inexistant, tant que les recueils n'ont pas été lus.

---

### Mise à jour du 11 août 2026 — la contrainte de débit, et elle est dure

**Le premier inventaire du Tarn s'est arrêté sur une fermeture de connexion, et
la plateforme des sites de préfecture a cessé de répondre.** Ce n'est pas une
hypothèse : c'est ce qui a été mesuré, et c'est la contrainte la plus lourde du
chantier.

Le déroulé, pour qu'il ne soit pas réinterprété plus tard :

| | ce qui a été fait | ce qui s'est passé |
|---|---|---|
| sondage | 4 pages, 1 appel/s | tout répond |
| inventaire | ~70 pages, 1 appel/s | fermeture de connexion au 6ᵉ mois de 2016 |
| relance | 1 page | **la racine elle-même ne répond plus** |
| diagnostic | 6 appels | rien ne répond, y compris `robots.txt` |

**Le discriminant a été posé** : `tarn-et-garonne.gouv.fr`, **jamais sollicité
par le projet**, ne répond pas davantage ; Légifrance répond (403, mais il
répond) et Hub'Eau répond 200. **Ce n'est donc ni notre réseau, ni le site du
Tarn en particulier : c'est la plateforme des sites de préfecture qui refuse la
connexion.**

**Deux lectures possibles, et rien dans nos données ne tranche entre elles :**

1. la plateforme connaît une indisponibilité qui n'a rien à voir avec nous ;
2. notre adresse a été mise à l'écart par un pare-feu après quelques dizaines
   d'appels, et le blocage porte sur toute la plateforme d'un coup.

**Trois états, pas deux** (§2.4) : tant que le site n'a pas été retrouvé
disponible, la cause est **indéterminée**. Ne pas écrire que nous avons été
bloqués, ne pas écrire que le site était en panne.

**Ce qui est décidé, quelle que soit la cause :**

- **on s'arrête.** Aucune relance tant que la disponibilité n'est pas revenue,
  et aucun contournement — ni changement d'identité déclarée, ni détour par un
  autre chemin. Le `User-Agent` du projet dit qui nous sommes et laisse une
  adresse : c'est la condition pour être en droit de revenir ;
- **le débit devient un paramètre, et il ne se baisse jamais.** `--pause` est
  ajouté à `raa_moisson.py`, avec la mesure du jour en clair dans son aide ;
- **l'ordre de grandeur du chantier change.** Si quelques dizaines d'appels par
  minute suffisent à fermer la porte, un inventaire départemental ne se fait pas
  en une heure : il se fait **étalé, sur des jours**, et un lot national ne se
  fait pas du tout dans cette forme. C'est à instruire avant toute promesse de
  couverture ;
- **`robots.txt` n'a jamais pu être lu** — la seule tentative est tombée sur la
  même fermeture. Il devra l'être avant toute reprise, et ses règles priment sur
  les nôtres.

**Ce que l'inventaire a quand même établi**, sur les six premiers mois de 2016 :
**88 fichiers PDF pour 62 pages de recueil**, soit environ 1,4 fichier par
recueil — la découpe en parties n'est donc pas la règle générale, elle ne
concerne que les recueils mensuels volumineux. **Le corpus n'a pas de taille
connue à ce jour**, et il n'en aura pas avant que l'inventaire aille au bout.

### La typologie — liste fermée, et le hors-périmètre se compte aussi

Un acte reçoit un type et un seul. La liste est fermée : un acte qui n'entre
dans aucune case ne s'invente pas de case, il sort en `autre_eau_consommation`
et attend une relecture.

| type | ce qu'il fait | rôle |
|---|---|---|
| `restriction_consommation` | interdit ou limite l'usage alimentaire de l'eau distribuée | **thèse** |
| `levee_restriction` | met fin à une restriction antérieure | **thèse** — c'est lui qui donne la durée |
| `derogation_limite` | autorise à distribuer au-dessus d'une limite, pour un temps borné | **thèse** |
| `derogation_suite` | renouvelle, prolonge ou clôt une dérogation | **thèse** |
| `autorisation_distribution` | autorise la production ou la distribution | dénominateur |
| `perimetre_protection` | déclaration d'utilité publique, périmètres de captage | dénominateur |
| `autre_eau_consommation` | touche l'eau de consommation sans entrer dans les cases | dénominateur |
| `hors_perimetre` | sécheresse, police de l'eau, assainissement, baignade | **le bruit, compté à part** |

Compter le `hors_perimetre` n'est pas du zèle : c'est la seule façon de dire
plus tard *« le filtre a écarté 2 300 actes, en voici la composition »* au lieu
de demander qu'on lui fasse confiance.

### La forme du fichier de sortie

`referentiel/arretes_eau.csv` remplace le `derogations.csv` prévu le 9 août —
même esprit, périmètre plus large, la dérogation n'y étant qu'un type parmi
huit. Séparateur `;`, barre verticale à l'intérieur des cellules, jamais de
point-virgule dans une valeur (§5).

Une ligne par acte, et elle porte : **le département et l'identifiant de
l'acte** ; **le recueil dont il vient, sa page de début et son adresse** — la
traçabilité du §8bis n° 9, transposée du bulletin au document ; **la date de
signature et celle de publication** ; **le service signataire** ; **l'intitulé
littéral** ; **le type** ; **les deux bornes de la période** ; **le périmètre
nommé, les codes INSEE et l'unité de distribution** ; pour une dérogation, **le
paramètre, la valeur autorisée et son unité** ; **le motif tel qu'écrit dans
l'acte** ; enfin **la fiabilité et la date de qualification**.

Les deux exigences du 9 août tiennent, et une troisième s'ajoute :

- **une ligne sans date de fin ne produit aucune durée** — elle existe, elle se
  compte, elle ne se chronomètre pas ;
- **une ligne sans source primaire reste `a_verifier`** et ne produit aucun
  dénombrement publiable ;
- **une ligne dont le périmètre n'est pas nommé ne produit aucun rattachement
  géographique.** Rattacher au mauvais périmètre fabriquerait des faux positifs
  à la chaîne, et c'est le §2.13 : le faux positif coûte plus cher.

### La chaîne — le déterministe aux deux bouts, le modèle au milieu

Calquée sur `moisson.py` / `ingerer.py` et sur `rediger_lot.py`, qui sont les
deux découpages qui ont déjà fait leurs preuves dans ce dépôt.

```
py -X utf8 src/raa_moisson.py --dept 81 --depuis 2016   # réseau seul
py -X utf8 src/raa_lot.py --dept 81 --index             # sommaires → actes
py -X utf8 src/raa_lot.py --dept 81 --candidats         # pré-filtre → candidats
py -X utf8 src/raa_lot.py --dept 81 --dossiers          # dossiers de faits
                                                        # → qualifier en Claude Code
py -X utf8 src/raa_lot.py --dept 81 --verifier          # contrôle, sans rien écrire
py -X utf8 src/raa_lot.py --dept 81 --integrer          # contrôle puis écrit
py -X utf8 src/raa_lot.py --dept 81 --etat              # où en est le département
```

Quatre règles, et elles ne se déduisent pas du code :

1. **Aucun des deux scripts n'importe `duckdb`.** Le chantier ne touche jamais
   la base : il peut donc tourner **pendant** une ingestion, verrou tenu, sans
   rien attendre. C'est la garantie mécanique héritée de `moisson.py`, et elle
   vaut ici encore plus cher.
2. **Le découpage se fait sur le sommaire**, avec la page de début et le nombre
   de pages. Un recueil dont le sommaire ne se lit pas est **signalé, pas
   deviné**.
3. **L'idempotence se lit dans les fichiers de sortie**, comme partout dans le
   dépôt : un recueil déjà au cache ne se retélécharge pas, un acte déjà
   qualifié ne se requalifie pas. Un lot interrompu se relance sans précaution.
4. **Le pré-filtre ne décide de rien.** Il propose des candidats. Ce qui décide
   du type d'un acte, c'est la lecture — et elle est contrôlée au retour.

### Le contrôle au retour, qui est la vraie valeur du script

Sur le modèle exact de `rediger_lot.py`, et en **réutilisant** ses fonctions
plutôt qu'en écrivant une seconde version :

1. **le type est dans la liste fermée**, sinon blocage ;
2. **toute date et tout nombre absents du texte extrait de l'acte bloquent.**
   C'est le contrôle qui attrape la valeur inventée, la date recopiée de
   mémoire, la durée calculée de tête ;
3. **le périmètre est nommé, et ses codes INSEE existent** dans les communes de
   la base — sinon la ligne passe sans rattachement plutôt qu'avec un faux ;
4. **une dérogation sans paramètre nommé n'est pas une dérogation** : elle
   redescend en `autre_eau_consommation` ;
5. **trois états, jamais deux** — qualifié / hors périmètre / **indéterminé**.
   Un acte dont la portée est douteuse sort en indéterminé et se compte comme
   tel.

### Le déclenchement automatique, et où il s'arrête

Le point d'accroche existe : `--termine` est le seul juge de la complétude d'un
département (§10.1 de `docs/REPRISE.md`), et il rend 0. L'enchaînement est donc :

```
moisson → ingerer → si --termine rend 0 : raa_moisson, --index, --candidats, --dossiers
```

et il **s'arrête là**, sur une phrase de compte. La qualification est un geste
lancé à la main. Deux raisons, et la seconde est la vraie : un script planifié
qui appellerait un modèle passerait par une API facturée hors du canal de
Yannick (§3 du mode opératoire) ; et surtout, **on ne fait pas interpréter des
textes de droit en lot sans que quelqu'un ait décidé de lancer ce lot.**

### Ce qu'on quantifie, et le dénominateur qui va avec

Par département et par année : le nombre d'actes touchant l'eau de consommation,
sa **composition par type**, les communes concernées, les jours cumulés de
restriction — **uniquement sur les couples restriction/levée réellement
appariés** — et les dérogations par paramètre.

Deux règles de sortie qui découlent de tout ce qui précède :

- **la durée n'est pas dans l'acte, elle est dans le couple.** Une restriction
  est souvent levée par un acte distinct, publié plus tard. Sans appariement,
  toute durée annoncée est fausse. Une restriction non appariée se compte, elle
  ne se chronomètre pas ;
- **un département non moissonné est « non instruit », jamais « sans
  dérogation ».** C'est le §2.4 transposé au document, et c'est le piège le plus
  facile à commettre au moment de faire une carte.

### Les trois lots, et ce qui bloque quoi

| lot | ce qu'il rend | dépend du modèle de seuils |
|---|---|---|
| **A** | la liste des actes du Tarn, datée, typée, sourcée | non |
| **B** | les dénombrements, avec leur dénominateur | non |
| **C** | le croisement avec les bulletins — la démonstration nominative | **oui** — la borne haute reste à ajouter |

Le blocage annoncé le 9 août — *« ce chantier ne peut pas être livré sans
ajouter la borne haute au modèle de seuils »* — **ne vaut que pour le lot C**.
A et B se livrent seuls, et ce sont eux que la commande du 11 août demande.

### Le coût — à mesurer sur trois actes, jamais à annoncer

Le seul comparable mesuré dans le dépôt est le sourçage de substance :
**~140 000 tokens en `opus` par substance**, un agent à la fois
(`docs/CONSIGNE_SOURCAGE.md` §0). La qualification d'un acte est une tâche plus
étroite — un document déjà fourni, un schéma fermé, pas de recherche
documentaire — donc vraisemblablement moins chère, **et « vraisemblablement »
n'est pas un chiffre**. Protocole : trois actes qualifiés, compteurs relevés
avant et après, résultat montré, feu vert, puis le lot.

---

## Ce qui reste en attente d'une décision de Yannick

Repris de `docs/REPRISE.md` §4, mis à jour :

- **le moteur ne lit pas les références de qualité déclarées par la source** —
  trouvé le 9 août 2026 sur le Tarn entier, et c'est le plus gros écart connu
  entre l'Observatoire et l'administration. `seuil_2026_effectif` vaut
  `COALESCE(seuil du référentiel, limite_declaree)` et **n'utilise jamais
  `reference_declaree`**, pourtant renseignée sur 21 029 mesures. Résultat :
  **807 bulletins du Tarn — un sur deux — où l'ARS déclare une non-conformité
  et où le moteur ne voit rien.** 151 mesures dépassent une référence déclarée
  sans produire aucun verdict : carbone organique total (20, jusqu'à 3,6 pour
  une référence de 2), turbidité (13, jusqu'à 23 pour 2), aluminium (8, jusqu'à
  509 pour 200), radon 222 (8, jusqu'à 286 Bq/L pour 100), bactéries coliformes
  (43). **La question n'est pas technique, elle est éditoriale** : une référence
  de qualité n'est pas une limite sanitaire, et le projet doit décider s'il la
  note — et, s'il la note, comment il l'affiche sans la confondre avec une
  limite. En l'état, une fiche peut afficher « aucun dépassement » sous une
  conclusion d'ARS qui dit le contraire ;
- **`depasse_applicable` mélange limites de qualité et valeurs de vigilance** —
  même origine, même jour. Le Tarn porte **172 mesures en dépassement réparties
  sur 135 bulletins** ; **79 d'entre elles — 46 % — portent sur une valeur de
  vigilance** : 53 sur l'ESA métolachlore, 16 sur le chlorothalonil
  R471811. Le référentiel le sait — `statut_2026` vaut `vigilance (non
  pertinent depuis…)` — mais ni le moteur ni la fiche n'en tiennent compte, et
  la ligne s'affiche « dépassement du seuil applicable ». C'est la leçon du
  R417888 (§2.7) transposée : **une valeur indicative n'est pas une limite de
  conformité**. Cinq bulletins de Paulinet le montrent en clair — nous
  prononçons un dépassement d'ESA métolachlore entre 0,912 et 0,99 µg/L là où
  l'ARS conclut à la conformité pleine. Ce sont les **cinq seuls** désaccords de
  ce sens sur 135 : partout ailleurs (130 sur 135) une non-conformité déclarée
  accompagne notre dépassement ;

- **le barème de finesse analytique** — chantier C4, niveau 3 : **tranché le
  8 août 2026**, on l'affiche, avec sa base — nombre de bulletins et de
  départements sur lesquels l'étendue est calculée ;
- **la onzième obligation d'affichage du §8bis** — chantier C4 : **tranché le
  8 août 2026**, la règle est écrite dans `CLAUDE.md` sur instruction ;
- **le seuil nul dans `indetermine_strict`** — chantier C4 : le même piège que
  celui écarté pour les paramètres aveugles subsiste sur l'indéterminé
  ordinaire, dans `src/build_db.py`. Sans effet aujourd'hui, par accident ;
- **l'ordre des chantiers 3 et 7** — l'évolution attend le captage ;
- **le §2.2 et la filtration** — chantier C1 : **tranché le 9 août 2026**, le
  §2.2 est révisé, la frontière passe entre un type et un produit. Reste la
  table `retention_procedes.csv` et ses sources ;
- **le « charbon actif » de Vourles** — conforme sur le fond depuis la révision
  du §2.2, mais toujours non sourcé : il attend sa ligne dans la table ;
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

## C9 — VITRINE

### Le parcours, la carte, la liste, le référentiel, et « que faire »

### Ce que Yannick demande — 9 août 2026

> « je veux travailler maintenant sur le site vitrine. Il y a un gros travail en
> profondeur à réaliser. Parcours utilisateur, carte, liste de commune,
> référentiel, mais aussi toute une partie information. Que faire quand je vois
> que mon eau est vraiment compliquée etc. »

Quatre lots, plus un cinquième qui est le livrable du chantier C1 dégelé.

### Ce qui existe, mesuré le 9 août 2026

| | |
|---|---|
| pages | 5, plus **60 fiches de commune** — la base en couvre **90** |
| poids total | 9,5 Mo |
| `carte.html` | 190 304 o, dont **174 432 o de fond départemental** (92 %, 118 anneaux) |
| coût d'un point sur la carte | **203 o** — marginal |
| `communes.html` | 31 785 o pour 60 lignes, soit ~530 o par ligne |
| `donnees/index_communes.json` | 9 113 o pour 60 communes, soit ~152 o par commune |
| référentiel affiché | 74 paramètres, déversés en table brute au bas de `sources.html` |
| volet information | néant, hors quatre paragraphes en accueil et `methode.html` |

Le site publié est une photographie du 8 août à 20 h 23 : **30 communes
couvertes n'ont pas de page**, ce que `tests/test_sorties.py` signale déjà.

### Ce que l'échelle casse, et ce qu'elle ne casse pas

C'est le point que le carnet doit fixer, parce qu'il commande la conception et
que l'intuition se trompe dessus.

**La carte ne casse pas par le poids.** Son coût est fixe — le fond — et un
point ne coûte que 203 o : 5 000 communes ajouteraient ~1 Mo à une page qui en
pèse déjà 174 Ko. **Elle casse par la lisibilité.** Mesuré dans le navigateur le
9 août 2026 : sur une carte de France large de 926 px, le Tarn occupe
**85 × 73 px**, et chaque point de commune fait 5,5 px de rayon. Ses 314
communes ne peuvent pas y tenir côte à côte — elles s'empilent. Il faut donc un
**niveau géographique intermédiaire**, pas une compression. Sur sa propre page,
le même département occupe 926 × 793 px : le facteur est d'environ 120 en
surface.

**La liste casse par le poids**, elle : ~530 o par ligne, soit ~2,6 Mo d'HTML
d'un seul bloc à 5 000 communes, sans tri ni filtre ni pagination.

**L'index de recherche casse plus tard, mais il casse** : ~152 o par commune,
soit 760 Ko à 5 000 communes chargés dès la première frappe, et ~5 Mo si le
corpus atteignait un jour les 35 000 communes françaises. Le découpage par
département est la sortie, et il vaut pour les trois.

### Le piège méthodologique — un par lot

Ce chantier est le plus exposé du dépôt : c'est la seule surface que le public
voit, et **une règle de méthode qui ne se voit pas à l'écran n'existe pas.** Le
§8bis liste onze obligations d'affichage ; chaque lot ci-dessous peut en perdre
une par simple commodité d'interface.

**Lot 1 — le parcours.** Introduire un niveau *département* et un niveau
*réseau* crée deux occasions de fabriquer un agrégat interdit. Un département
n'a pas de verdict, un réseau non plus : ce sont des **collections de bulletins
datés**, chacun noté contre sa grille. Toute moyenne, tout « taux de conformité
du département », tout classement de communes serait exactement le profil
synthétique que le §2.3 interdit — sans date, donc non réétalonnable. Et le
§2.11 tient : aucun classement sans l'effort de recherche de chaque terme.

**Lot 2 — la carte.** Un zoom départemental rend visibles les communes **non
documentées**, qui sont aujourd'hui noyées. C'est un gain, et c'est un risque :
plus elles sont visibles, plus la tentation est grande de les rendre discrètes.
Le §8bis obligation 4 ne se négocie pas — gris n'est pas une couleur neutre,
c'est un troisième état.

**Lot 3 — l'information.** Deux pièges distincts. Le premier : le volet civique
est du **contenu réglementaire**, donc soumis au §2.7 comme un seuil. « L'ARS
contrôle », « la commune distribue », « vous avez un droit d'accès » sont des
affirmations qui se sourcent, pas des évidences qu'on rédige de mémoire — c'est
la faute la plus facile de tout le chantier. Le second : le §2.1. Expliquer qui
décide quoi ne doit pas devenir la désignation d'un responsable.

**Lot 4 — le référentiel.** Une fiche par paramètre invite à écrire ce qu'est la
substance, ses effets, sa dangerosité. Le §2.15 tient : trois registres, jamais
fusionnés — `pe_reglementaire`, `pe_scientifique`, `cancerogenicite_circ`. Et le
§2.12 : le seuil 2016 d'un métabolite est une extrapolation, et une fiche par
paramètre est précisément l'endroit où cela doit se lire.

**Lot 5 — les procédés.** Voir C1. Rien ne se publie avant que
`referentiel/retention_procedes.csv` existe et soit sourcé couple par couple.

### Les cinq lots

| Lot | Ce qu'il produit | Dépend de |
|---|---|---|
| **1 — parcours** | niveau département, entrée par réseau (`nom_uge`), fil d'Ariane, liste filtrable et paginée qui tient à 5 000 lignes | — |
| **2 — carte** | fond découpé par département, zoom, filtres par état, fond factorisé hors page | lot 1 pour les URL |
| **3 — information** | « comment lire un bulletin », et le « que faire » civique, sourcé | §2.2 révisé (fait) |
| **4 — référentiel** | page dédiée, recherche, filtres famille/fiabilité, une fiche par paramètre | — |
| **5 — procédés** | `referentiel/retention_procedes.csv` et son affichage | C1, sources à réunir |

Ordre arrêté par Yannick le 9 août 2026 : **1, 2, 3, 4**, le lot 5 venant se
loger dans le lot 3 quand la table existe.

### Ce qui a été construit — lots 1 et 2, 9 août 2026

**Le parcours.** `Accueil › Les communes du corpus › Tarn (81) › Albi › bulletin`.
Un niveau *département* est apparu entre la carte et la fiche, et
`communes.html` est devenu son index — un département par ligne, l'effort de
recherche en **étendue** et jamais en moyenne.

**Le fond découpé.** `carte_svg()` est indexée par code de département et cadre
sur ce qu'elle dessine. Il n'y a pas d'autre zoom : une carte du Tarn est un
fond du Tarn, pas un fond de France recadré.

**La légende est le filtre.** Cliquer un état le retire de la carte **et** du
tableau — les deux portent le même `data-niveau`, donc la même règle CSS les
atteint. Ils ne peuvent pas diverger. Et **le compte d'un état masqué reste à
l'écran, barré** : on retire un état de la vue, jamais du décompte. Un filtre
qui ferait disparaître « 52 communes non documentées » présenterait une absence
de donnée comme une bonne nouvelle (§8bis, obligation 4).

**La carte de situation d'une fiche.** Sur une commune rattachée, un trait
pointillé relie la commune à celle où l'analyse a réellement été prélevée. C'est
l'obligation d'affichage n° 5 rendue visible : à l'échelle, six communes sur dix
lisent le bulletin d'une voisine, et une phrase en petits caractères ne suffit
pas. Le trait n'est tracé que si les deux points sont connus — `commune_prelevement`
n'est qu'un **nom** dans `couverture_communes`, et un trait vers un point
approximatif dirait sur une carte quelque chose de faux, ce que l'absence de
trait ne fait pas.

**Un défaut corrigé en passant.** `page()` prend désormais un `prefixe` et un
`fil`. La version précédente réparait les adresses d'une page déjà rendue par
une chaîne de sept `.replace()`, une par entrée de menu : ajouter une page ou un
sous-dossier demandait de penser à l'allonger, sans quoi le lien pointait dans
le vide et rien ne le signalait. C'est la leçon de C8 une troisième fois — une
règle recopiée diverge.

**Mesures, sur un corpus d'essai de 374 communes** (synthétique, pour éprouver
l'échelle sans la base, verrouillée) :

| | |
|---|---|
| carte de France, 374 communes | 253 528 o |
| **page d'un département de 314 communes** | 240 698 o — c'est la nouvelle page lourde |
| index des départements | **3 751 o** |
| emprise du Tarn sur la carte de France | **85 × 73 px** sur 926 de large |
| le même sur sa propre page | **926 × 793 px** — environ 120× la surface |

Vérifié dans le navigateur : le filtre passe 314 points et 314 lignes à 262 et
262 d'un même clic, le second clic restaure, aucune erreur de console, aucun
débordement horizontal en 375 px, et les tableaux défilent dans leur cadre.

**Une estimation fausse attrapée par la mesure.** « Un département tient dans
une trentaine de pixels » avait été écrit de tête, puis propagé dans ce carnet,
dans deux commentaires de code **et dans un texte publié de la vitrine**. La
mesure donne 85 × 73. Rectifié partout. C'est le §2.7 hors de son domaine
habituel : la règle vaut pour un chiffre d'interface comme pour un seuil.

### Vérifié sur les données réelles — 9 août 2026, 15 h

Le Tarn collecté, le site construit, **les trois suites passent**.

| | |
|---|---|
| pages | 5 + **8 départements** + **339 fiches de commune** |
| `tests/test_sorties.py` | **339 communes couvertes, 0 sans page** — le trou est refermé |
| | 352 pages, **0 ressource distante**, 0 prescription générée, 0 comparaison anonyme |
| | 1 signalement non bloquant : le « charbon actif » de Vourles, cf. C1 |
| `departement/81.html` | 272 694 o pour 314 communes |
| `communes.html` (index) | **5 846 o** |

Le filtre tient sur les données réelles : masquer « rattachée au réseau » fait
passer carte et tableau de 314 à 127 **ensemble**. Le Tarn déclare **60
gestionnaires**.

**Le poids du site est un vrai problème, et il n'est pas là où on le cherchait.**
309 Mo au total, dont **173 Mo de `commune/`** et **137 Mo de `donnees/`** — les
pages construites par ce chantier pèsent 8 Ko à 273 Ko. Trois fiches dépassent
**5,4 Mo** à elles seules : ce sont les communes à nombreux bulletins, chaque
bulletin embarquant tout son détail de paramètres dans la page. À 5 000
communes, `commune/` seul dépasserait 2,5 Go. **Cela relève de la fiche
(`sortie/build_fiche.py`, `fiche.js`) et des exports, pas des lots 1 et 2** —
consigné ici parce que c'est le prochain mur de l'échelle, et qu'il n'était pas
identifié.

### Ce que le Tarn entier apprend, et qui n'était pas visible sur 45 bulletins

**Aucune commune non documentée sur 314** : 127 analysées, 187 rattachées au
réseau. Le carnet attendait d'un département entier qu'il révèle enfin cette
catégorie ; il révèle l'inverse — la règle de repli du §2.3 couvre tout le monde.

**Et surtout : 115 des 127 communes analysées portent au moins une mesure
indéterminée. Une seule est verte sans réserve.** Le chantier C4 avait établi le
plafond analytique sur 46 mesures aveugles ; à l'échelle d'un département, l'état
« indéterminé » n'est pas un cas particulier, **c'est l'état majoritaire des
communes analysées**. C'est le résultat le plus fort du corpus à ce jour, et il
appartient au volet information du lot 3 autant qu'à C4.

Le département porte par ailleurs 9 bascules et 13 dépassements à la date.

### Contrainte de session — 9 août 2026

La collecte du Tarn tourne depuis 11 h 43 (48 communes sur 314 à 12 h, 196
bulletins au cache brut, 4,6 Mo) et **tient le verrou d'écriture DuckDB** : la
base n'est ni lisible ni copiable pendant ce temps. Le travail commence donc par
ce qui ne demande pas la base, et la vérification — construction du site, tests
— attend la fin de la collecte. Décision de Yannick : **site d'abord, collecte
en parallèle**, sans l'interrompre.

### Ce qui reste à décider

- **la profondeur du volet information** : sur le site seul, ou site et livre ;
- **le niveau réseau** : `nom_uge` porte le gestionnaire déclaré, pas l'UDI. Une
  entrée « par réseau » sur ce champ regroupe par gestionnaire, ce qui n'est pas
  tout à fait la même chose que « l'eau que vous buvez vient d'ici ». À vérifier
  contre les données avant de nommer la page ;
- **l'hébergement**, toujours ouvert : rien n'est publié en ligne à ce jour.

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
- **9 août 2026** — **C10 ouvert** : des arrêtés préfectoraux autorisant le
  dépassement de seuils ont été trouvés dans le Tarn. C'est le **troisième
  mécanisme** de conformité sans changement de l'eau, après le réétalonnage et
  la dilution, et le seul qui soit nominatif et signé. Vérifié au passage :
  le corpus actuel n'en porte aucune trace lisible — une dérogation n'existe
  que dans l'arrêté. Dépendance identifiée : le modèle de seuils ne sait pas
  exprimer une date de **fin**, et une dérogation est bornée des deux côtés.
- **9 août 2026, C2 sur le Tarn** — la question de Yannick est répondue, et pas
  dans le sens attendu. Les 298 paramètres retirés en 2020 n'avaient été
  quantifiés que **6 fois sur 134 419 mesures** (0,004 %), avec une LQ médiane
  vingt fois plus fine que la limite : le retrait n'a presque rien coûté. Le
  motif est ailleurs — **le panel a tourné**. 34 paramètres sont entrés depuis,
  dont le **chlorothalonil R471811, quantifié dans 19,1 % des mesures et 20
  communes**, et le **R417888 entré en 2024**, l'année de l'avis ANSES qui le
  classe pertinent. Enfin, `v_panel_constant` / `v_serie_panel_constant`
  outillent le §2.11 : à panel constant, le Tarn est **plat sur onze ans**
  (16,1 à 19,2 ‰). Toute la variation du dossier est une variation de ce qu'on
  a cherché.
- **9 août 2026, reprise de C2** — deux défauts du détecteur à l'échelle,
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
- **8 août 2026, C6 outillé et mesuré** — quatre décisions prises (le Tarn, tous
  les bulletins sans borne de date, cache brut, prose dérivée par défaut), puis
  la découverte qui commandait le chantier : **`fetch_departement.py` n'était
  pas « prêt »**. Il collectait sans repli réseau, sans couverture et sans
  figeage — lancé sur un département, il n'aurait produit ni page ni carte. La
  règle de couverture vit maintenant dans `src/collecte.py`, appelée par les
  deux points d'entrée ; c'est la leçon de C8 rencontrée une seconde fois.
  Quatre faits mesurés sur l'API, aucun documenté : `code_departement` est
  honoré, **`nom_departement` est ignoré en silence** (le piège de
  `communes_udi`), `code_prelevement` est honoré exactement — d'où un
  rapatriement à 0,1 s au lieu d'une fenêtre de deux jours filtrée côté client,
  avec un garde-fou si l'API cessait de l'honorer —, et **les pages profondes
  coûtent 4× les premières**, ce qui disqualifie le balayage départemental
  (45 min) au profit de la voie commune par commune (17 min).
  `src/brut.py` pose le cache brut : 16 à 20 Ko par bulletin, écriture atomique,
  et surtout la séparation entre collecter une fois et ingérer autant qu'on veut.
  Essai sur 10 communes : 4,5 min, 27 s par commune, **6 communes sur 10 sans
  bulletin propre** — le repli réseau devient le cas majoritaire. Le corpus passe
  à 94 bulletins et 35 191 mesures, et dix communes suffisent à **débloquer C3** :
  trois installations portent plusieurs bulletins là où le corpus entier n'en
  portait aucune, Albi en aligne 29 de 2021 à 2026. Albine donne à C2 son premier
  point d'eau suivi dix ans : 627 paramètres de 2016 à 2019, 345 à 409 depuis.
  Le barème de LQ passe de 29 à 71 bulletins de base, comme le §2.14 le prévoyait.
  `tests/test_sorties.py` signale 12 communes couvertes sans page : c'est le
  contrôle qui fonctionne, publier restant un geste séparé.
- **9 août 2026, C9 ouvert et C1 dégelé** — Yannick demande le chantier de la
  vitrine en profondeur : parcours, carte, liste, référentiel, et un volet
  information « que faire quand mon eau est compliquée ». Ce dernier butant sur
  le §2.2, **il est révisé le jour même sur instruction** : la frontière ne
  passe plus entre en parler et ne pas en parler, mais entre **un type et un
  produit**. Énoncé au §2.2 de `CLAUDE.md`, argumentaire au §2.2 de
  `docs/GARDE-FOUS.md`, avec le retour de lecteur qui l'a déclenchée et le test
  qui repère une prescription déguisée. C1 passe de gelé à dégelé ; son livrable
  — `referentiel/retention_procedes.csv`, sourcé couple par couple — devient le
  lot 5 de C9, et rien ne se publie sur les procédés avant qu'il existe.
  Diagnostic mesuré de la vitrine, qui corrige une intuition fausse : **la carte
  ne casse pas par le poids** — 174 Ko de fond fixe, 203 o par point — mais par
  la lisibilité, le Tarn n'occupant que 85 × 73 px sur une carte de France large
  de 926 (mesuré, après qu'une première estimation « une trentaine de pixels »
  eut été écrite de tête et propagée jusque dans un texte publié). Ce sont
  **la liste**
  (~530 o/ligne, 2,6 Mo à 5 000 communes) et **l'index de recherche**
  (~152 o/commune) qui cassent par le poids. Le découpage par département est la
  sortie commune aux trois. Ordre arrêté : parcours, carte, information,
  référentiel. Session contrainte : la collecte du Tarn tourne (48/314 à 12 h)
  et tient le verrou d'écriture DuckDB — le travail commence par ce qui ne
  demande pas la base.
- **9 août 2026, C4 relu sur le Tarn entier** — 1 575 bulletins au lieu de 45.
  **1 295 mesures aveugles sur 72 % des bulletins**, dont 1 051 pour la seule
  **hydrazide maléique** : entrée au panel en 2020, cherchée sur 123 communes,
  **jamais quantifiée en six ans** parce que la LQ courante vaut cinq fois sa
  limite. Le volume oblige aussi à **retirer une affirmation** du chantier : les
  « facteurs 4 000 » entre LQ extrêmes sont portés par deux à quatre mesures
  isolées, ce n'est pas une dispersion entre laboratoires mais un plafond
  partagé — aucun classement de communes ne doit en être tiré.
  **Une alerte que j'avais donnée était fausse, et la corriger aurait fait un
  faux négatif.** J'avais annoncé « 16 faux dépassements sur les chlorites » et
  proposé un alias `chlorite` → `Chlorites` pour rendre son seuil conditionnel
  de 0,70 mg/L. Vérification faite avant d'écrire quoi que ce soit : **l'ARS
  déclare `conf_references_pc = 'N'` sur exactement ces bulletins** — « conforme
  aux limites de qualité et non conforme aux références de qualité ». Notre
  verdict était d'accord avec l'administration ; l'alias l'aurait transformé en
  « indéterminé ». Et il n'y avait pas de défaut d'appariement : la source
  déclare elle-même `<=0,25 mg/L` pour « Chlorite en mg/L » et `<=0,7 mg/L` pour
  « Chlorites en cas de traitement pouvant en générer », ce sont deux paramètres
  distincts. **Aucune modification n'a été faite au référentiel.** Reste vrai et
  mineur : ces libellés n'ont ni `seuil_2016` ni `seuil_strict`, donc aucune
  bascule n'est détectable sur les chlorites.
  En cherchant la cause, deux écarts autrement plus gros sont apparus et sont
  versés en attente de décision : **les références de qualité déclarées ne sont
  jamais lues** (807 bulletins où l'ARS voit une non-conformité et nous rien),
  et **`depasse_applicable` mélange limites et valeurs de vigilance** (79 des
  135 dépassements du Tarn). Aucun code touché : ce sont deux décisions
  éditoriales, pas deux bugs.

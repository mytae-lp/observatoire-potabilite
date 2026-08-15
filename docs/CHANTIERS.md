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
3. **Troisième décision, prise le 11 août au soir, après la mesure de volume —
   la fenêtre passe de dix ans à six mois.**

   > « je pense que nous allons chercher sur les 6 derniers mois pour l'instant
   > et non sur 10 ans. On ne va pas générer des centaines de Go pour rien. On
   > se focus sur le récent, le maintenant. […] l'objectif reste de publier le
   > site. »

   **Ce que la fenêtre courte permet, et ce qu'elle interdit — c'est la
   conséquence méthodologique, et elle n'est pas symétrique :**

   | | six mois | dix ans |
   |---|---|---|
   | **restrictions de consommation** | **bien couvertes** — un acte de ce type est court, daté, et s'il a lieu maintenant il est dans la fenêtre | mieux, mais marginalement |
   | **dérogations en cours** | **manquées** — une dérogation dure jusqu'à trois ans renouvelables une fois, donc celles en vigueur aujourd'hui ont été signées **avant** la fenêtre | seule voie |
   | **durées, séries, tendances** | impossibles | c'est leur condition |

   **Donc : sur une fenêtre de six mois, on peut dire « voici les restrictions
   prononcées ces six derniers mois » et on ne peut PAS dire « voici les
   dérogations en vigueur ».** Le second énoncé exige le stock, que seul
   l'historique donne. L'écrire quand même serait une affirmation d'absence
   (§2.4) sur le pire terrain possible.

   Le stock des dérogations en cours reste donc **une question ouverte, à
   instruire autrement** — la piste la plus directe étant le bilan national que
   le sourçage n'a pas pu ouvrir, ou une demande à l'ARS. Ce n'est pas abandonné,
   c'est daté et rangé.

   Outillage : `raa_moisson.py --depuis AAAA-MM` borne au mois, et la période se
   lit **sur le chemin** du recueil, jamais sur la date de mise en ligne
   annoncée par le site — celle-ci vaut « 09/06/2016 » pour le recueil de
   janvier 2016, vestige d'une reprise en masse. S'y fier daterait faux.

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

**Ce que l'inventaire a quand même établi**, et c'est déjà beaucoup — sur les
**six premiers mois de 2016** :

| | |
|---|---|
| recueils | **57** |
| fichiers PDF | **88**, soit ~1,5 par recueil |
| taille annoncée | **0,52 Go**, et **les 88 annoncent la leur** |
| scans probables | 0 — mais aucun fichier n'a encore été ouvert |

La découpe en parties n'est donc **pas** la règle générale : elle ne concerne
que les recueils mensuels volumineux.

**L'ordre de grandeur du département, et c'est une extrapolation, pas une
mesure** : un demi-2016 pèse 0,52 Go, et le rythme de publication a environ
**quadruplé** entre 2016 et 2026 — 57 recueils en six mois d'un côté, le
n° 286 atteint à la mi-juillet de l'autre. Le Tarn sur onze ans est donc
vraisemblablement dans **les dizaines de gigaoctets**. Ce chiffre sert à
décider d'une méthode, **pas à annoncer une date ni un volume** : seul
l'inventaire complet le dira. Et il justifie à lui seul le choix de ne garder
que le texte.

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

---

## C11 — RÉFÉRENTIEL : les 376 libellés mesurés que la grille ne regarde pas

**Ouvert le 15 août 2026.** Douze décisions de Yannick prises le jour même, en
une passe. Ce chantier remplace le point 1 du §10.2 de `docs/REPRISE.md`
(« les libellés listés sans seuil »), qu'il absorbe et dépasse.

### C11.0 L'état des lieux, mesuré

Sur un corpus de **40 725 bulletins complets, 33 départements représentés** dont
**24 collectés en entier**, l'attribution `rien_ne_se_prononce_non_instruit`
porte **376 libellés, 1 364 674 mesures, 405 959 quantifiées**.

**Ce n'est PAS un compte d'angles morts** — la leçon du 9 août
(`docs/AUDIT_NON_APPARIES.md`) se répète : la température de l'eau est dans la
liste. Le tri en 17 dossiers est produit par `src/etude_non_apparies.py` et
versé dans `data/etudes/classement_non_apparies_<jour>.csv`.

Deux faits établis par requête, et ils commandent une partie des décisions :

1. **L'administration n'oppose AUCUNE limite de qualité à ces 376 libellés.**
   Zéro `limite_declaree`. En revanche **8 portent une `reference_declaree`** —
   et notre cascade d'attribution ne lit pas cette colonne, d'où leur
   classement en « non instruit » alors que la source leur oppose un nombre.
2. **Les cyanobactéries sont dans le périmètre.** Elles apparaissent sur
   122 bulletins de 245 à 653 paramètres, même `code_lieu_analyse` que tout le
   reste du corpus : ce n'est pas de la surveillance d'eau brute.

Et un troisième, qui ferme une question ouverte : **le radon 222 et le tritium
sont déjà appariés** (§11.1). Le trou radiologique porte sur les activités
globales et les radionucléides individuels, pas sur eux.

### C11.1 Les douze décisions

| n° | sujet | décision |
|---|---|---|
| 1 | `reference_declaree` dans la cascade | **oui** — elle doit produire une attribution |
| 2 | Température de l'eau | **référence de qualité**, pas hors périmètre |
| 3 | Contexte du prélèvement (5 libellés) | **hors périmètre**, mais **affichés en bas de fiche** |
| 4 | Calco-carbonique (19) | **dossier de sourçage** — détailler, pas seulement totaliser |
| 5 | Organoleptique (9) | **couper en deux** : par dilution noté, qualitatif non exprimé |
| 6 | Revivifiables 22°/36° | **rien pour l'instant**, gardé en amélioration future |
| 7 | Cyanobactéries (94) | **un bloc « surveillance sans verdict »**, pas 94 dossiers |
| 8 | Radiologique (20) | **gros dossier, important** |
| 9 | PCB (33) | **fait d'effort de recherche** — et voir la réserve ci-dessous |
| 10 | PFAS (16) | **recherche poussée** — dire s'il existe une recherche plus large que les 20 |
| 11 | COV et solvants (81) | **on source, on affiche** — priorité haute |
| 12 | Désinfection (8) | **afficher les chiffres même sans seuil** |

### C11.2 Ce que chaque décision engage, et ce qu'elle coûte

**Décision 1 — `reference_declaree` entre dans la cascade.**
Modification de `build_db.py`, donc de `version_moteur` : refigeage complet
obligatoire. Effet mesuré d'avance : 8 libellés, ~77 000 mesures, reclassés
sans qu'aucune ligne de référentiel ne soit écrite. C'est la correction la
moins chère du chantier et la plus rentable.

**Décision 3 — « hors périmètre » ne veut pas dire « invisible ».**
Consigne de Yannick : *« nous pourrions les afficher en bas des fiches comme
indicateur de la qualité du prélèvement. Peut-être que nous pourrons à terme
faire des corrélations ? »*

Donc **trois effets distincts, qui ne se confondent pas** :

- sort du **dénominateur** de `pct_couverture` (90,07 % → 90,41 %) ;
- ne reçoit **aucun verdict** ;
- **reste affiché**, dans un bloc propre en bas de fiche, nommé pour ce qu'il
  est : les conditions du prélèvement, pas la qualité de l'eau.

C'est un quatrième état d'affichage, à écrire dans la charte. Et la piste des
corrélations est notée comme **hypothèse à instruire**, jamais comme un acquis
(§7.2 : le précédent de la dilution).

**Décision 4 — détailler le calco-carbonique.**
*« aujourd'hui il existe un total calco carbonique, et je crois qu'il est bon
de donner le détail. »* Le corpus porte en effet `Equilibre calcocarbonique
0/1/2/3/4`, un indice codé, sur 37 402 mesures — un agrégat sans ses termes.
Le dossier doit établir, sur source primaire, ce que la réglementation dit de
l'équilibre calcocarbonique et si elle l'exprime en valeur. **19 libellés,
191 752 quantifications — le plus gros bloc de l'inventaire.**

**Décision 9 — la réserve de Yannick, et elle est juste.**
*« je rappelle que nous n'avons pas tous les départements disponibles ! Sur
17 % difficile de dire que ça ne donne rien. »*

Le chiffre exact est **24 départements collectés en entier sur 101, soit 23,8 %**
(33 comptent au moins un bulletin complet, les autres étant partiels). La
précision ne change rien à la conclusion, elle la renforce.

**La règle qui en découle est plus forte que le cas des PCB** : 219 043 mesures
pour 3 quantifications ne se dit **jamais** « les PCB sont absents ». C'est le
§2.4 transposé du seuil de quantification à la couverture géographique — *zéro
n'est pas zéro*, et *pas encore cherché partout* n'est pas *pas trouvé*. La
formulation à tenir : « recherchés sur N bulletins de M départements,
quantifiés 3 fois » — le dénominateur, toujours.

**Décision 10 — les PFAS, et la question qui vaut le chantier.**
*« s'il existe une recherche plus large que les 20 du total des 20 il faut
l'indiquer ! »* C'est exactement le §2.14 : le corpus mesure **16 PFAS qui ne
sont dans aucun total opposable**, sur 2 629 bulletins chacun. Le laboratoire
cherche donc plus large que ce que la norme additionne. **Ce fait-là est la
thèse du projet appliquée au périmètre plutôt qu'à la valeur**, et il est
démontrable sur nos données.

À établir avant d'écrire : lesquels des 16 sont dans les 20 de la directive
2020/2184 et lesquels n'y sont pas. **Aucune liste ne doit être écrite de
mémoire** (§2.7).

**Décision 12 — afficher la désinfection, et le cadre dans lequel l'écrire.**
Décision retenue : les chiffres du chlore libre, total, combiné, du ClO2 et de
l'ozone sont affichés même sans valeur opposable. **62 008 quantifications**,
c'est une part majeure de ce que subit l'eau distribuée et l'invisibiliser
n'aurait pas de sens.

**Trois précautions de rédaction, non négociables**, parce que le motif avancé
touche à des affirmations sanitaires :

1. **Les sous-produits de chloration sont le terrain solide, et ils sont déjà
   au référentiel** — THM, chlorites, chlorates, bromates. Le lien « chloration
   → sous-produits » est documenté et déjà outillé ; c'est par là que le sujet
   se traite.
2. **« La chloration n'empêche pas réellement la désinfection » ne se publie
   pas en l'état.** L'énoncé est contesté, et la donnée du projet ne le porte
   pas : nous mesurons des résiduels de désinfectant, pas une efficacité.
   §2.7 s'applique entier — et §2.1 : le sujet est la norme, pas l'exploitant
   qui chlore parce que le texte le lui impose.
3. **L'antibiorésistance n'est pas dans le corpus.** Aucune mesure ne s'y
   rapporte. En parler serait sortir de ce que le dépôt peut démontrer, et
   ferait basculer un outil de conscience en outil d'alerte (§2.2).

Ce qui est publiable et fort : *« cette eau porte 0,3 mg/L de chlore libre ;
aucune limite de qualité française ne s'y oppose ; les sous-produits qu'engendre
cette désinfection, eux, sont limités — voici lesquels et où en est cette eau. »*

### C11.3 L'ordre de travail arrêté

**Rien n'est écrit dans `referentiel_seuils.csv` avant que les dossiers de
sourçage ne soient faits.** Le refigeage étant à ~13 h, il ne se paie qu'une
fois, à la toute fin.

| phase | contenu | dépendance |
|---|---|---|
| **1** ✅ | classement des 376 en 17 dossiers | fait le 15 août |
| **2** | décisions 1, 2, 3, 5 — mécaniques, sans source nouvelle | `build_db.py` |
| **3** | dossiers de sourçage : **11 COV**, **8 radiologique**, **10 PFAS**, **4 calco-carbonique**, **12 désinfection** | sources primaires |
| **4** | blocs sans verdict : 7 cyanobactéries, 9 PCB | rédaction |
| **5** | écriture du référentiel, en une seule passe | phases 2-4 |
| **6** | **un seul refigeage complet**, puis publication | phase 5 |

**Décision 6 — revivifiables — est explicitement gelée** et rangée en
amélioration future : la norme s'exprime en variation dans un rapport, que le
modèle ne sait pas porter. Même famille que les chlorites datés par le haut
(`CLAUDE.md` §8).

### C11.4 Phase 2 — FAITE le 15 août 2026, mesurée

**Nouvelles empreintes** : `version_referentiel` **`9a2777400815`** (était
`d0fb678dcbe2`), `version_moteur` **`5a5473295577`**. Les deux ont changé —
refigeage complet obligatoire, et il portera une version NEUVE, donc sans
écraser les 34 823 lignes de `d0fb678dcbe2`.

**Fichiers touchés** : `referentiel/hors_perimetre.csv` (créé, versionné),
`src/build_db.py`, `src/figer.py`. `tests/test_verdict.py` et
`tests/test_figer.py` passent tous les deux.

#### Ce qui a été fait, décision par décision

**Décision 1 et 2 — la référence déclarée produit désormais une attribution.**
Nouvelle branche `juge_sur_reference_declaree`, placée **après**
`juge_sur_valeur_declaree` : une limite est opposable, une référence ne l'est
pas, donc quand la source déclare les deux c'est la limite qui parle.

Le défaut corrigé était réel et mesurable : **7 940 mesures étaient
`hors_reference = TRUE`** — déclarées hors de leur référence par
l'administration, affichées comme telles par le bloc de la fiche — **tout en
portant « rien ne se prononce » et en ne comptant pas comme notées.** Deux
organes du même moteur se contredisaient sur la même mesure.

**Après : 0 mesure `hors_reference` non notée.** L'incohérence est fermée.

**Décision 3 — `hors_perimetre` existe**, testé EN PREMIER dans la cascade.
Ce n'est pas « on ne sait pas juger » mais « il n'y a rien à juger ».
5 libellés, 21 358 mesures. Un garde-fou refuse toute ligne dont le référentiel
porte par ailleurs un seuil : hors périmètre et jugé sont exclusifs, sans quoi
la mesure sortirait du dénominateur sans sortir du numérateur et fabriquerait
une couverture supérieure à 100 %. **Contrôlé : 0 bulletin au-dessus de 100 %.**

**Décision 5 — l'organoleptique s'est coupé tout seul.** Odeur et saveur *par
dilution* portent une référence déclarée de 3 : la décision 1 les fait basculer
en `juge_sur_reference_declaree` sans qu'aucune ligne de référentiel ne soit
écrite. Les qualitatifs (aspect, couleur, odeur, saveur) restent « non
instruits » — ils relèvent de la phase 5.

#### L'effet mesuré sur le corpus

| attribution | mesures | libellés |
|---|---|---|
| `juge` | 13 631 025 | 827 |
| `rien_ne_se_prononce_non_instruit` | **1 225 519** (était 1 364 674) | **362** (était 376) |
| `juge_sur_valeur_declaree` | 360 197 | 36 |
| **`juge_sur_reference_declaree`** | **117 797** | **10** |
| `norme_non_exprimee` | 79 005 | 4 |
| `rien_ne_se_prononce_etabli` | 78 886 | 5 |
| **`hors_perimetre`** | **21 358** | **5** |
| `juge_avec_son_groupe` | 20 253 | 13 |

**Couverture du corpus : 90,07 % → 91,46 %**, soit **+1,39 point**.

> **Une prévision fausse, et la même leçon qu'au §12.2 de `docs/REPRISE.md`.**
> J'avais annoncé +0,34 point. Ce chiffre ne portait que sur la sortie du
> dénominateur (décision 3) ; il ignorait que faire entrer la référence
> déclarée dans la cascade fait aussi entrer ces mesures au **numérateur**
> (décision 1). Les deux effets s'ajoutent : +0,34 par le dénominateur,
> +1,05 par le numérateur. **Ne jamais annoncer un chiffre de sortie avant de
> l'avoir mesuré** — la règle était déjà écrite, et elle vient de resservir.

#### Les 10 libellés qui basculent, et deux surprises

| libellé | mesures | hors référence | référence déclarée |
|---|---|---|---|
| Température de l'eau | 40 012 | **243** | 25 |
| **Equilibre calcocarbonique 0/1/2/3/4** | 37 402 | 0 | **2** |
| Bact. et spores sulfito-réductrices | 27 957 | **222** | 0 |
| Saveur par dilution à 25 °c | 5 915 | 13 | 3 |
| Odeur (dilution à 25 °c) | 3 320 | 0 | 3 |
| Oxydabilité KMnO4 | 2 163 | 5 | 5 |
| **Conductivité à 20 °C** | 1 002 | **313** | 1 000 |
| Chlorite en mg/L | 22 | 1 | 0,2 |
| Chlorite (utiliser CLITEMG) | 3 | 2 | 200 |
| Coliformes thermotolérants | 1 | 0 | 0 |

**Deux entrées changent la donne pour les dossiers de la phase 3 :**

1. **L'indice « Equilibre calcocarbonique 0/1/2/3/4 » porte une référence
   déclarée de 2.** L'agrégat que la décision 4 veut détailler n'est donc pas
   muet : la source lui oppose une valeur. Le dossier calco-carbonique doit
   partir de là — que vaut ce codage 0/1/2/3/4, et que signifie « 2 » ?
2. **La conductivité sort de sa plage 313 fois sur 1 002 mesures**, soit près
   d'une sur trois. C'est le motif de l'eau agressive (§11.3), et il est bien
   plus dense ici que partout ailleurs dans le corpus.

#### Ce que la phase 2 NE fait pas

Elle ne publie rien, ne fige rien, n'écrit aucune ligne dans
`referentiel_seuils.csv`. **La base porte désormais des vues neuves et des
tables figées calculées sous l'ancien moteur** : rien n'est citable tant que le
refigeage de la phase 6 n'a pas eu lieu. C'est l'état attendu, et
`figeage_moteur` le dira si quelqu'un tente de figer par inadvertance.

### C11.5 Dossier PFAS — instruit le 15 août 2026 sur source primaire

Deux agents, briefs disjoints : l'un lit la directive sans rien savoir du corpus,
l'autre compte le corpus avec **interdiction formelle de proposer un seuil**. Le
rapprochement n'a pas été délégué. Les deux livrables :
`data/etudes/PFAS_source_directive.md` et `data/etudes/PFAS_inventaire_corpus.md`.

**Tous les chiffres ci-dessous sont lus sur les vues vivantes, pas sur du figé.
Rien n'est citable avant le refigeage de la phase 6** (§8bis).

#### C11.5.1 Ce que dit la directive (UE) 2020/2184, lu et recompté

Source : `Sources/REG_Reglementation_et_seuils/REG-01_UE_directive-2020-2184.pdf`,
62 pages, **version anglaise** (aucune version française sur le disque).

| point | ce qui est lu | page |
|---|---|---|
| liste de la « Sum of PFAS » | **20 substances**, série C4→C13 complète pour les carboxyliques et pour les sulfoniques, sans trou | 53, annexe III B 3 |
| valeur « Sum of PFAS » | **0,10 μg/l** | 38, annexe I B |
| valeur « PFAS Total » | **0,50 μg/l** | 38, annexe I B |
| applicabilité | **12 janvier 2026** | 32, art. 25 §1 |
| transposition | 12 janvier 2023 | 32, art. 24 |

Le compte de 20 a été vérifié par trois compteurs indépendants sur le texte brut
(20 puces, 20 « perfluoro », 20 « acid » dont 10 « sulfonic ») — et non repris de
l'expression courante « les 20 PFAS ».

**Citation littérale de l'article 25 §1, vérifiée en session principale :**

> « By 12 January 2026, Member States shall take the measures necessary to ensure
> that water intended for human consumption complies with the parametric values
> set out in Part B of Annex I for **Bisphenol A, Chlorate, Chlorite, Haloacetic
> Acids, Microcystin-LR, PFAS Total, Sum of PFAS and Uranium**. »

**Ce report ne concerne donc PAS que les PFAS : il porte sur huit paramètres.**

**Ce que la directive ne donne pas** : aucun numéro CAS ; aucun acronyme pour
trois des vingt substances ; aucune liste ni méthode de dénombrement pour
« PFAS Total » — dont la valeur est en outre suspendue à des lignes directrices
techniques de la Commission, **sans date**.

#### C11.5.2 Le conflit de dates entre les deux textes

`REG-03_FR_arrete-2022-12-30_grille-2026.pdf` — **8 pages, extractible**, contre
ce qu'affirme `docs/INDEX_SOURCES.md` (erreur à corriger, voir C11.5.5) — porte
en tête :

> « Entrée en vigueur : le texte entre en vigueur le **1er janvier 2023**. »

**Aucune occurrence de « 12 janvier 2026 » dans l'arrêté.** Il transpose la seule
« somme » (0,10 µg/L en eau distribuée, 2 µg/L en eaux brutes) et **ne reprend pas
le paramètre « PFAS Total »**. Il sigle PFPeA/PFPeS là où la directive écrit
PFPA/PFPS — écart de nomenclature à porter dans l'appariement.

> **Deux textes, deux dates, même substance.** La directive fixe une échéance au
> 12 janvier 2026 ; l'arrêté français applique les valeurs depuis le 1er janvier
> 2023. Un État membre peut appliquer plus tôt que le minimum européen — c'est
> une lecture plausible, **ce n'est pas une lecture établie**, et elle demande
> une confirmation juridique avant toute publication (§2.7).

#### C11.5.3 Ce que le corpus contient

**22 libellés PFAS** : 20 substances individuelles, **chacune mesurée exactement
2 629 fois** — même bordereau, le laboratoire les cherche ensemble — plus deux
lignes de somme rendues par le laboratoire.

| ligne | mesures | quantifiées | max | référentiel |
|---|---|---|---|---|
| Somme de 20 (code 8847) | 2 629 | 904 | **0,203 µg/L** | seuil 0,1 · statut **limite** |
| Somme de 4 (code 9268) | 1 367 | 372 | 0,111 µg/L | **aucun seuil** · statut *vigilance* |

Total PFAS du corpus : 56 575 mesures, 4 766 quantifications, **2 629 bulletins
sur 29 départements**, dont 928 portent au moins une quantification.

#### C11.5.4 DEUX DÉFAUTS ÉTABLIS

**Défaut A — l'aiguillage des 20 individuelles est incomplet, et il pointe à
l'envers.**

Sur les 20 substances individuelles, **4 seulement portent `dans somme`** :
PFOA, PFOS, PFNA, PFHxS. Ce sont exactement les composants de la **somme de 4**,
celle qui ne porte **aucun seuil opposable** (statut *vigilance*). Les **16
autres n'ont aucune ligne** et tombent en `rien_ne_se_prononce_non_instruit`.

Or la seule limite opposable du dossier est portée par la **somme de 20**. Donc :

- 4 substances renvoient à une somme qui ne prononce rien ;
- 16 substances ne renvoient à rien, alors qu'une somme les juge à 0,10 µg/L.

La directive nommant bien 20 substances dans sa somme, **les 16 doivent porter
`dans somme`**. Ce n'était pas un trou de connaissance, c'est un défaut
d'aiguillage — et il se corrige par 16 lignes de référentiel, sans code.

**Défaut B — cinq lignes portent un seuil sans sa date d'applicabilité (§2.5).**

| ligne | seuil_2016 | seuil_2026 | date_applicabilite_2026 |
|---|---|---|---|
| Bisphenol A | — | 2,5 | **vide** |
| Chlorates | — | 0,25 | **vide** |
| Chlorites | 0,25 | 0,25 | **vide** |
| Somme de 20 PFAS | — | 0,1 | **vide** |
| Uranium | — | 30,0 | **vide** |
| Acides haloacétiques | — | 60,0 | **2023-01-01** ⚠️ |

Les six figurent dans la liste de l'article 25. La sixième porte une date, mais
**2023-01-01 — qui n'est ni celle de la directive (12/01/2026) ni rien de lu** :
à instruire.

**La portée du faux positif est réelle mais circonscrite, et il faut le dire
précisément** : une date d'applicabilité absente ne fabrique un faux verdict que
là où `seuil_2016` est vide. Pour les **chlorites**, `seuil_2016 = seuil_2026 =
0,25` : la date ne déplace aucun verdict, et les 135 dépassements de ce
paramètre **ne sont pas en cause**. Le risque porte sur bisphénol A, chlorates,
uranium et la somme des 20.

**Mesuré sur la somme des 20 :**

| année | quantifiées | au-dessus de 0,10 | max |
|---|---|---|---|
| 2022 | 5 | **1** | 0,1629 |
| 2023 | 19 | 0 | 0,0901 |
| 2024 | 44 | 0 | 0,0962 |
| 2025 | 458 | **2** | 0,1230 |
| 2026 | 378 | **1** | 0,2030 |

**4 bulletins dépassent, dans 4 communes de 4 départements.** Le dépassement de
2022 est **antérieur au 1er janvier 2023 : c'est un faux positif sous les deux
lectures**. Les deux de 2025 le seraient aussi si la date européenne du
12 janvier 2026 devait primer. **Entre 1 et 3 faux positifs sur 4**, et l'écart
entre ces deux chiffres est exactement le conflit de textes du C11.5.2.

#### C11.5.5 Ce qui reste à faire, et une erreur du dépôt à corriger

1. **Trancher le conflit de dates** — c'est un point de droit, pas de données.
   Tant qu'il n'est pas tranché, aucun verdict PFAS antérieur au 12/01/2026 ne
   se publie.
2. **Écrire les 16 lignes `dans somme`** en phase 5, en appariant sur les noms
   de l'arrêté français (PFPeA/PFPeS) autant que sur ceux de la directive.
3. **Reprendre les cinq dates manquantes** — le sujet dépasse les PFAS et
   touche sept autres paramètres.
4. **`docs/INDEX_SOURCES.md` est faux sur REG-03** : il affirme que « son PDF
   n'est pas extractible en texte ». Il l'est — 8 pages, 20 808 caractères,
   texte propre, vérifié en session principale le 15 août 2026. Cette mention
   a fait renoncer à une lecture qui aurait été possible dès le 10 août, et
   c'est elle qui laissait la ligne turbidité en `a_verifier` (§12.3).
5. ~~Le nom du fichier `REG-03_..._grille-2026.pdf` serait trompeur~~ —
   **ALERTE RETIRÉE le 15 août 2026, elle était fausse.** `grille-2026` n'est
   pas une affirmation sur une date du texte : c'est la **convention de nommage
   du dépôt**, qui relie une source à la colonne qu'elle alimente. Le fichier
   voisin le prouve : `REG-02_FR_arrete-2007-01-11_grille-2016.pdf` nourrit
   `seuil_2016`, `REG-03_..._grille-2026.pdf` nourrit `seuil_2026`. Le fichier
   ne doit **pas** être renommé — le renommer casserait la symétrie et la
   lisibilité de l'index.

   **Ce que cet épisode enseigne** : un agent qui ne connaît que le document
   qu'on lui donne ne peut pas juger d'une convention de dépôt. Le signalement
   était légitime de sa part ; l'erreur a été de le relayer sans regarder le
   fichier d'à côté.

### C11.6 Dossier RADIOLOGIQUE — instruit le 15 août 2026

Même dispositif que les PFAS : deux agents à briefs disjoints, rapprochement non
délégué, et **vérification en session principale de chaque fait décisif**.
Livrables : `data/etudes/RADIO_source_reglementaire.md` et
`data/etudes/RADIO_inventaire_corpus.md`.

**Chiffres lus sur les vues vivantes. Rien n'est citable avant le refigeage.**

#### C11.6.1 UNE ERREUR DE MA PART, CORRIGÉE — ce n'était pas un angle mort

En ouvrant C11, j'ai écrit que le radiologique était *« l'angle mort du §8
confirmé à l'échelle — 69 303 quantifications et le moteur ne prononce rien »*.
**Le comptage était juste, la conclusion était fausse.**

Table « C. – Paramètres indicateurs » de l'arrêté du 30/12/2022, lue en mode
`layout` et vérifiée colonne par colonne :

| PARAMÈTRES | RÉFÉRENCES DE QUALITÉ | UNITÉS | NOTES |
|---|---|---|---|
| Activité alpha globale | *(vide)* | *(vide)* | « En cas de valeur supérieure à **0,10 Bq/L**, il est procédé à l'analyse des radionucléides spécifiques… » |
| Activité bêta globale résiduelle | *(vide)* | *(vide)* | « En cas de valeur supérieure à **1,0 Bq/L**… » |
| Dose indicative (DI) | **0,1** | mSv/an | … |
| Radon | **100** | Bq/L | « Uniquement pour les eaux d'origine souterraine » |
| Tritium | **100** | Bq/L | … |

**Les 0,10 et 1,0 Bq/L ne sont pas des seuils de conformité.** Ce sont des
**déclencheurs d'investigation**, logés dans la colonne NOTES, colonnes
« références » et « unités » vides. Leur franchissement n'ouvre pas une
non-conformité : il ouvre une analyse complémentaire.

**Ne rien prononcer dessus était donc le bon comportement.** En avoir fait
69 000 verdicts aurait été le plus gros faux positif du projet — la leçon de
l'ESA métolachlore (§9.3 b), transposée telle quelle.

> **CE QUE ÇA OUVRE — une quatrième nature de valeur.** `nature_seuil` connaît
> `limite`, `reference`, `vigilance`. Il manque **`investigation`** : un nombre
> réel, publiable, opposable à personne. C'est une information citoyenne
> légitime — « au-dessus de cette valeur, l'ARS doit pousser l'analyse » — et
> elle ne se peint pas comme un dépassement.

#### C11.6.2 Ce que les textes ne portent pas

- **Aucun radionucléide individuel n'a de valeur.** Radium 226/228, plomb 210,
  polonium 210, césium 134/137, strontium 90, iode 131, cobalt 60, carbone 14,
  américium 241, plutonium : **zéro occurrence** dans les trois PDF. Ils
  n'interviennent que par le renvoi collectif au calcul de la dose indicative.
- **La bêta brute et le K40 n'ont aucun correspondant réglementaire.**
  « potassium » : 1 occurrence dans REG-01 et REG-02, 0 dans REG-03 ; « K40 » et
  « K-40 » : **zéro partout**. Seule la bêta **résiduelle** est nommée par les
  textes.
- **L'uranium n'est pas comparable.** Sa seule valeur est **30 µg/L, limite de
  qualité chimique en masse** — pas en Bq/L, donc sans rapport direct avec nos
  `Activité Uranium 234/238`, et aucun des textes ne donne le facteur de
  conversion (§2.9 : deux unités non convertibles, aucun verdict).
- **La directive (UE) 2020/2184 ne fixe AUCUNE valeur radiologique**, et le dit :
  *« Directive 2013/51/Euratom lays down specific arrangements […] Therefore,
  this Directive should not set out parametric values on radioactivity »*
  (considérant 52, vérifié littéralement).

#### C11.6.3 ⚠️ SECTION PÉRIMÉE LE JOUR MÊME — l'alarme des 51 verdicts était FAUSSE

> **Lire d'abord C11.6.3 bis.** La directive a été récupérée dans la foulée et
> elle infirme cette section **sur ses deux jambes**. Elle est conservée telle
> quelle comme trace du raisonnement, pas comme état courant.

#### C11.6.3 (texte d'origine, périmé) — la lacune documentaire, et elle coûte 51 verdicts

**La directive 2013/51/Euratom est absente du dossier `Sources/`.** C'est
pourtant elle qui porte tout le volet radiologique européen — la directive de
2020 y renvoie explicitement.

Conséquence immédiate et chiffrée. La ligne du référentiel :

```
Radon 222 | Bq/L | seuil_2016 = 100 | seuil_2026 = 100
          | date_applicabilite_2026 = VIDE
          | statut_2026 = « reference (valeur parametrique, directive 2013/51/Euratom) »
          | sources RAD-01|REG-06 | fiabilite = verifie
```

Or **le radon est ABSENT de l'arrêté de 2007** et n'entre en droit français
qu'au 1er janvier 2023 (source lue). Et nous prononçons :

| année | quantifiées | dépassements | max |
|---|---|---|---|
| 2019 | 292 | **1** | 109,6 |
| 2020 | 299 | **11** | 531,0 |
| 2021 | 268 | **18** | 1 212,0 |
| 2022 | 304 | **21** | 333,6 |
| 2023-2025 | 1 144 | 79 | 454,7 |

**51 dépassements de radon sont antérieurs au 1er janvier 2023.** Ils reposent
entièrement sur `seuil_2016 = 100`, dont la seule justification invoquée est un
texte que **le dépôt ne possède pas**. Deux issues, et rien ne permet de
trancher aujourd'hui :

- si 2013/51/Euratom fixait bien 100 Bq/L et était applicable avant 2016, la
  ligne est juste et les 51 verdicts tiennent ;
- sinon, `seuil_2016 = 100` est **un passé réglementaire fabriqué**, ce que le
  §2.8 interdit explicitement, et les 51 sont des faux positifs.

**C'est la plus grosse exposition trouvée à ce jour** — 51 verdicts contre 1 à 3
pour les PFAS. Et la ligne est marquée `fiabilite = verifie`, ce qui la fait
passer sans signalement dans toute sortie publique. **Récupérer 2013/51/Euratom
est la première action du dossier.**

#### C11.6.3 bis LA DIRECTIVE RÉCUPÉRÉE — les 51 verdicts tiennent

Récupérée le 15 août 2026 sur EUR-Lex, version française, et archivée :
`Sources/RAD_Radiologique/RAD-01_UE_directive-2013-51-Euratom_2013.md`.

**Elle infirme l'alarme sur ses deux jambes.**

**Jambe 1 — la date. Article 8 §1 :**

> « Les États membres mettent en vigueur les dispositions […] nécessaires pour se
> conformer à la présente directive au plus tard **28 novembre 2015** »

**Antérieure à 2016.** La valeur de 100 Bq/L était exigible avant le premier
prélèvement du corpus : `seuil_2016 = 100` n'est pas un passé réglementaire
fabriqué. Les 51 verdicts antérieurs à 2023 **tiennent**.

**Jambe 2 — la nature. Le moteur la traite DÉJÀ correctement**, vérifié en base :

```
radon : nature_seuil = reference | 9 321 mesures
        130 depasse_applicable, dont 130 hors_reference
sur les bulletins concernes : 155 depassements applicables, dont 7 sur une LIMITE
```

Les dépassements de radon **ne sont pas comptés comme des dépassements de limite**
et ne déclenchent donc pas le rouge (§11.3). Le modèle faisait déjà la
distinction que je croyais manquante.

**Ce que je n'avais pas vu, et qui aurait dû m'arrêter** : `docs/INDEX_SOURCES.md`
portait déjà, à la ligne RAD-01, la phrase *« un dépassement ne crée pas de
non-conformité, il déclenche une enquête »*. **La réponse était dans le dépôt.**
Coût de ne pas l'avoir lue : une alarme fausse annoncée comme « la plus grosse
exposition trouvée à ce jour ».

**Ce qui était vrai, en revanche, et qui est réparé** : le fichier annoncé par
l'index **n'existait pas sur le disque**. Le référentiel se réclamait de RAD-01
en `fiabilite = verifie` sans qu'aucun document ne soit consultable — le défaut
même que le §2.7 existe pour empêcher. Il est désormais archivé.

**Deux apports nets du relevé :**

1. **Les seuils alpha 0,1 et bêta 1,0 Bq/L sont en ANNEXE III** (méthodes de
   contrôle), **pas en annexe I** (valeurs paramétriques). La source européenne
   confirme indépendamment ce que la colonne NOTES de l'arrêté français
   indiquait : ce sont des seuils de dépistage. **Deux textes, même lecture.**
2. **La restriction du radon aux eaux souterraines est une ADDITION FRANÇAISE.**
   Aucune restriction de ce genre dans la directive — l'annexe II point 2 ne
   conditionne que le *contrôle*, pas la valeur. À dire comme telle dans toute
   sortie : c'est une condition nationale, pas européenne.

**Reste ouvert** : le PDF officiel (ce relevé vient de la page HTML) ; l'art. 2
pt 4 et l'art. 7 non relus littéralement ; l'exclusion du tritium du calcul de la
dose, non retrouvée dans ce relevé ; et surtout **le texte français de
transposition**, celui que l'arrêté du 30/12/2022 appelle « l'arrêté mentionné à
l'article R. 1321-20 » — c'est lui qui porte les radionucléides individuels.

#### C11.6.3 ter LE CHAÎNON MANQUANT TROUVÉ — arrêté du 12 mai 2004 [RAD-02]

L'arrêté que REG-03 désignait sans le nommer — « l'arrêté mentionné à l'article
R. 1321-20 » — est l'**arrêté du 12 mai 2004 fixant les modalités de contrôle de
la qualité radiologique des EDCH**, modifié par l'**arrêté du 9 décembre 2015**.
Relevé et archivé :
`Sources/RAD_Radiologique/RAD-02_FR_arrete-2004-05-12_controle-radiologique.md`.

**Il corrige DEUX affirmations que j'avais données comme établies.**

**Correction 1 — « aucun radionucléide individuel n'a de valeur » est FAUX.**
Le tableau 1 de son annexe porte **quatorze concentrations dérivées** —
américium 241 à 0,7 Bq/L, polonium 210 à 0,1, radium 228 à 0,2, uranium 234 à
2,8… — et **elles recouvrent exactement les radionucléides que le corpus
mesure**. Elles étaient absentes des trois PDF lus parce qu'elles ne sont dans
aucun des trois : elles vivent dans ce quatrième texte.

> **Mais une concentration dérivée n'est PAS une limite**, et cette distinction
> commande tout le dossier. C'est **le dénominateur d'une somme** : la
> concentration qui, seule, produirait la DI de 0,1 mSv/an. Le verdict se rend
> sur la DI, jamais sur un radionucléide isolé. Prononcer un dépassement parce
> qu'un radium 226 franchit 0,5 Bq/L serait exactement la faute évitée sur les
> quatre HAP — juger un composant à la valeur de sa somme. Le rapprochement à
> faire est `juge_avec_son_groupe`, **jamais `juge`**.

**Correction 2 — « le K40 n'a aucun correspondant réglementaire » est FAUX.**
Article 2.1, cité : la DI se calcule « à l'**exclusion** du tritium, du
potassium-40, du radon et de ses descendants ».

**Le K40 est nommé par le texte, comme exclusion.** C'est précisément pourquoi le
corpus le mesure : cette activité est mesurée **pour être retranchée**. Le
libellé « Activité bêta attribuable au K40 » n'est pas orphelin — c'est un terme
de soustraction, et il donne son sens à la bêta *résiduelle*.

**Ce que le texte confirme, en revanche, et pour la troisième fois.** Article 3 :

> « Lorsque l'activité alpha globale ou bêta globale résiduelle dépasse
> respectivement les **valeurs guides** de 0,1 Bq/L et 1 Bq/L, il est procédé à
> l'identification et à la quantification […] »

Le mot du texte est **« valeurs guides »**. Après l'annexe III de la directive
[RAD-01] et la colonne NOTES de l'arrêté de 2022 [REG-03], **trois sources
indépendantes disent la même chose**. Et l'article 4.1 donne leur rôle exact :
sous ces valeurs, « il est considéré que la DI est inférieure à la référence de
qualité de 0,1 mSv/an » — ce sont des **présomptions de conformité**, pas des
seuils.

**Le radon aux eaux souterraines est une restriction ANCIENNE** : elle figure
déjà à l'article 3 de la rédaction de 2004, bien avant l'arrêté de 2022 qui la
reprend. Elle reste une addition française — la directive ne la porte pas.

**Une réserve à tenir, et elle est importante.** L'arrêté du 9 décembre 2015
(publié le 18, JO n° 293) tombe trois semaines après l'échéance de transposition
du 28 novembre 2015. **Aucune mention de la directive 2013/51/Euratom n'a été
trouvée dans son texte.** La coïncidence est frappante, elle n'est pas une preuve :
ne pas écrire que cet arrêté transpose la directive tant qu'un texte ne le dit
pas. Ce serait refaire l'erreur du §8 de `docs/REPRISE.md`, où un mécanisme
plausible avait été pris pour une cause établie.

**Réserves ouvertes** : le plutonium 238 est listé à l'article 5 mais absent du
tableau ; et l'article 6 modifié en 2015 appelle **un cinquième texte**, l'arrêté
sur les modalités de contrôle du radon, non identifié.

#### C11.6.3 quater LES QUATORZE VALEURS SONT VÉRIFIÉES — et Légifrance est accessible

**Double lecture concordante, 15 août 2026.** Les quatorze concentrations
dérivées ont été relevées deux fois sur deux sources indépendantes — AIDA/INERIS,
puis le texte consolidé de **Légifrance** (`LEGITEXT000005787501`, en vigueur au
15/08/2026, dernière mise à jour des données au 19 décembre 2015). **Identiques
ligne pour ligne**, valeurs et unités comprises ; les articles 2, 3 et 4
concordent aussi. Elles passent de `a_verifier` à **`verifie`**. Le PDF du JO
n'est toujours pas archivé : deux consolidés concordants valent mieux qu'un, ils
ne valent pas le JO.

> **LE RÉSULTAT LE PLUS UTILE DE LA JOURNÉE, ET IL DÉPASSE LE RADIOLOGIQUE.**
>
> `docs/INDEX_SOURCES.md` porte depuis le 10 août que « Légifrance répond 403 au
> shell et oppose un contrôle anti-robot au navigateur ». **C'est vrai pour ces
> deux canaux — et faux pour l'outil web, qui passe.** Le texte consolidé a été
> lu intégralement, articles et annexes compris, sans blocage.
>
> **Trois conséquences à traiter :**
> 1. **REG-06 — l'arrêté du 11 janvier 2007 consolidé — est lisible.** Sa lecture
>    avait été renoncée le 10 août sur ce motif.
> 2. **La ligne turbidité peut sortir de `a_verifier`** — réserve n° 1 du §12.3
>    de `docs/REPRISE.md`, ouverte depuis cinq jours.
> 3. **La règle d'accès du projet est à réécrire** : non pas « Légifrance est
>    inaccessible », mais « inaccessible au shell et au navigateur, accessible à
>    l'outil web ». La nuance décide de ce qui est vérifiable, donc de ce qui peut
>    passer de `a_verifier` à `verifie`.
>
> C'est le §2.7 appliqué à nous-mêmes : **une impossibilité constatée sur un canal
> avait été généralisée en impossibilité tout court**, et elle a coûté cinq jours
> de `a_verifier` sur une ligne publiée.

#### C11.6.4 Le contrôle arithmétique : la relation bêta ne tient pas

`bêta globale − K40 = bêta résiduelle` est vérifiée à 5 % près dans
**2 075 cas sur 6 882, soit 30,2 %.**

Contrôle fait : restreindre aux mesures **toutes trois quantifiées** ne change
**rien** — mêmes 6 882 cas, mêmes 2 075. Ce n'est donc pas un artefact de
limite de quantification.

**Ce qu'on peut en conclure, et pas plus** : ces trois libellés ne satisfont pas
la relation que leurs noms suggèrent, dans 70 % des cas. **Ils ne sont donc pas
interchangeables, et la bêta résiduelle ne se recalcule jamais** à partir des
deux autres — elle se lit telle que le laboratoire la rend. La cause de l'écart
n'est pas établie (aliquotes distinctes, conventions de laboratoire, K40 déduit
d'un dosage de potassium) et **ne doit pas être devinée**.

#### C11.6.5 L'inventaire, et une discipline à saluer

24 libellés radiologiques, **195 576 mesures, 72 365 quantifications**,
33 625 bulletins sur 40 745 (**82,5 %**), 30 départements sur 33. Le volet est
cherché presque partout.

4 libellés ont une ligne au référentiel (Radon 222, Tritium, Dose indicative,
Dose totale indicative — noter le **doublon** des deux doses, à traiter) ;
20 n'en ont aucune.

**11 homonymes ont été écartés** par l'inventaire : dix isomères de pesticides
portant « alpha » ou « béta » dans leur nom, et « Uranium en µg/l » (famille
`metal`, masse chimique) distingué des `Activité Uranium` en Bq/L. Un tri par
sous-chaîne sans ce filtre aurait mêlé des pesticides au volet radiologique.

#### C11.6.6 Ce que le dossier laisse à faire

1. **Récupérer la directive 2013/51/Euratom** — bloquant pour 51 verdicts.
2. **Ajouter la nature `investigation`** et y ranger alpha globale et bêta
   résiduelle avec leurs 0,10 et 1,0 Bq/L. Ce n'est pas une ligne de seuil,
   c'est une quatrième colonne de sens.
3. **Écrire les lignes `rien_ne_se_prononce_etabli`** pour les radionucléides
   individuels : nous avons cherché, aucun texte ne leur oppose de valeur. C'est
   une réponse, pas un vide — et elle les sort de « non instruit ».
4. **Trancher le doublon** « Dose indicative » / « Dose totale indicative ».
5. **Ne jamais recalculer la bêta résiduelle** (C11.6.4).

---

### C11.7 Dossier COV et solvants — instruit le 15 août 2026

Livrables : `data/etudes/COV_source_reglementaire.md` et
`data/etudes/COV_inventaire_corpus.md`. Quatre affirmations décisives vérifiées
en session principale sur REG-03.

#### C11.7.1 LE RÉSULTAT QUI DÉPASSE LE DOSSIER — l'arrêté français ne diffère RIEN

**Vérifié : la chaîne « 2026 » apparaît ZÉRO fois dans tout l'arrêté du
30 décembre 2022.** Aucune clause de report, aucune date différée, pour aucun
paramètre. Le texte porte une seule date : « le texte entre en vigueur le
1er janvier 2023 ».

**Conséquence, et elle tranche une question ouverte depuis ce matin :** la
directive diffère huit paramètres au 12 janvier 2026 (art. 25 §1) ; **la France
ne transpose pas ce report**. En droit français, les huit s'appliquent depuis le
**1er janvier 2023** — trois ans avant le plancher européen.

**Ce que cela règle concrètement :**

1. **Les cinq lignes sans `date_applicabilite_2026`** (bisphénol A, chlorates,
   chlorites, somme des 20 PFAS, uranium — C11.5.4 défaut B) doivent recevoir
   **`2023-01-01`**, pas `2026-01-12`.
2. **Les dépassements PFAS se départagent proprement.** Sur les 4 bulletins
   au-dessus de 0,10 µg/L : celui de **2022 est un faux positif** (antérieur au
   1er janvier 2023) ; **ceux de 2025 et 2026 tiennent**. Ce n'est plus « entre
   1 et 3 », c'est **1**.
3. **UNE CORRECTION QUE JE ME DOIS.** J'avais signalé la ligne « acides
   haloacétiques » comme suspecte, au motif que sa date `2023-01-01` « ne
   correspond à rien de lu ». **Elle correspond exactement à l'entrée en vigueur
   de l'arrêté, et elle était juste.** C'est la seule des six lignes de
   l'article 25 qui était correctement datée, et j'ai jeté le doute dessus.

> **Et c'est un motif éditorial de première force pour C12** : sur ces huit
> paramètres, **la France applique trois ans plus tôt que ce que l'Europe
> exige**. Le réétalonnage ne va pas toujours dans le sens du relâchement — ici
> le droit national est plus strict que le plancher communautaire. À dire, parce
> que c'est vrai et parce que ça protège le projet du soupçon de réquisitoire
> (§2.1).

#### C11.7.2 Les 91 libellés — aucune collision, aucun alias à poser

Le périmètre réel est de **91 libellés**, pas 81 : l'inventaire a retenu en plus
8 chlorophénols, 5 chloronaphtalènes et chloronitrobenzènes, 2 PCB et 1 PBDE,
adjacents à la famille COV stricte et signalés pour arbitrage. Quatre faux
positifs ont été écartés (chlorophycées, chlorophylle A, chloronèbe,
forchlorfénuron).

**Collision de numéro CAS avec le référentiel : ZÉRO. 91 sur 91 réellement
absentes.** Vérifié par CAS *et* par `code_parametre`, dans les deux sens : nos
82 CAS distincts ne recoupent aucun des 39 CAS du référentiel.

**Ce n'est donc pas un défaut d'appariement** — contrairement au cas de mai 2026
où cinq libellés avaient un seuil sans s'y rattacher. Ces substances ne sont
nulle part dans le référentiel, et c'est un fait, pas un bug.

**Le poids réel du groupe** : 245 541 mesures pour **616 quantifications**, soit
un taux de 0,25 %. 22 311 bulletins, 28 départements. **62 des 91 libellés n'ont
jamais été quantifiés une seule fois dans tout le corpus.**

Les cinq plus trouvés : biphényle (104), trichloroéthane-1,1,1 (102), xylène
ortho (65), dichloroéthylène-1,1 (52), xylènes ortho+para+méta (47).

#### C11.7.3 Ce que les textes contiennent, et ce qu'ils ne contiennent pas

**24 paramètres organiques** en droit en vigueur, la nature lue au titre de
partie et non devinée : **16 limites de qualité** (annexe I partie I),
2 références de qualité (COT et indice permanganate — aucun composé nommé),
1 valeur indicative (métabolites non pertinents, 0,9 µg/L), 2 valeurs de
vigilance (17-bêta estradiol, nonylphénol), 6 limites en eau brute (annexe II).

**La catégorie « valeur guide » n'existe dans aucune annexe en vigueur** — elle
ne subsiste que dans l'annexe III de 2007, abrogée. À ne pas confondre avec les
« valeurs guides » radiologiques de l'arrêté du 12 mai 2004 [RAD-02], qui est un
autre texte et reste en vigueur.

**Sur les 91 : l'hypothèse est confirmée sur trois canaux concordants.** Ne sont
encadrés par aucun texte : dichloroéthylènes, trichloroéthanes, tétrachloro-
éthanes, tous les chlorobenzènes, xylènes, cumène, mésitylène, butylbenzènes,
fréons, MTBE, ETBE, biphényle, hexachlorobutadiène, tétrachlorure de carbone,
dichlorométhane, toluène, éthylbenzène, styrène, naphtalène. **Une dizaine
seulement sont encadrés.**

**C'est la réponse la plus utile du dossier** : la grande majorité des 91 relève
de `rien_ne_se_prononce_etabli` — nous avons cherché, aucun texte ne leur oppose
de valeur. Une réponse, pas un vide. Elles sortent de « non instruit » par une
ligne de référentiel sans seuil, exactement comme le perchlorate en août.

**Un seul numéro CAS figure dans les quatre textes** — 84852-15-3, nonylphénol.
Le rapprochement devra donc se faire sur les noms, pas sur les CAS.

#### C11.7.4 DEUX PÉRIMÈTRES SOUS UN MÊME SIGLE — le §2.14 pris sur le fait

Vérifié littéralement dans REG-03, **le même arrêté porte deux sommes « HAP »
différentes** :

| où | valeur | périmètre littéral |
|---|---|---|
| p. 3 — **eau distribuée** | **0,10 µg/L** | benzo[b]fluoranthène, benzo[k]fluoranthène, benzo[ghi]pérylène, indéno[1,2,3-cd]pyrène — **4 composés, SANS benzo[a]pyrène** |
| p. 7 — **eau brute** | **1 µg/L** | fluoranthène, benzo[b]fluoranthène, benzo[k]fluoranthène, **benzo[a]pyrène**, benzo[ghi]pérylène, indéno[1,2,3-cd]pyrène — **6 composés** |

Et le **benzo[a]pyrène porte en outre sa propre limite**, 0,010 µg/L (p. 2) : il
est jugé seul en eau distribuée, et dans la somme en eau brute.

**Le risque pour le corpus est direct.** Nous mesurons deux libellés agrégés —
« Hydrocarbures polycycliques aromatiques (6 subst.*) » (209 mesures) et
« (16 subst.) » (57 mesures). **Le premier a le compte de la liste EAU BRUTE.**
Le comparer à la limite de 0,10 µg/L de l'eau distribuée mêlerait deux
périmètres et deux valeurs. **À trancher avant toute ligne de référentiel** :
que mesure exactement ce libellé, et sur quelle eau ?

**Autre somme confirmée** : « Tétrachloroéthylène et trichloroéthylène », 10 µg/L,
note littérale « Somme des concentrations des paramètres spécifiés ». **Aucune
valeur individuelle pour l'un ni pour l'autre** — ils relèvent de
`juge_avec_son_groupe`, jamais de `juge`.

#### C11.7.5 Ce qui reste ouvert

1. **Le statut des chlorobenzènes** au titre de la définition « pesticides »
   (REG-05) est **indéterminé**. S'ils y entrent, ils tombent sous la limite de
   0,1 µg/L par substance et sortent entièrement de ce dossier.
2. **Le périmètre réel du libellé « HAP (6 subst.*) »** — voir ci-dessus.
3. **REG-04 (OMS)** est la piste directe pour les libellés orphelins : des
   valeurs guides sanitaires existent probablement pour le toluène, les xylènes,
   le styrène. **Aucune n'a été lue.** Elles ne seraient pas opposables, mais
   elles alimenteraient `seuil_strict`.
4. **Les 10 libellés adjacents** (chlorophénols, chloronaphtalènes, PCB, PBDE)
   attendent un arbitrage de périmètre.

---

### C11.8 Dossier CALCO-CARBONIQUE — instruit le 15 août 2026

Le plus gros bloc du chantier. Livrables : `data/etudes/CALCO_source_reglementaire.md`
et `data/etudes/CALCO_inventaire_corpus.md`. Légifrance a répondu aux cinq
requêtes de l'agent — **troisième confirmation** de son accessibilité par l'outil web.

#### C11.8.1 L'exigence existe, et elle n'a AUCUN chiffre

Vérifié en session principale sur REG-03, page 5, partie **« II. − Références de
qualité »** :

```
PARAMÈTRES                  | RÉFÉRENCES DE QUALITÉ                      | UNITÉS | NOTES
Equilibre calcocarbonique   | Les eaux doivent être à l'équilibre        | (vide) | (vide)
                              calcocarbonique ou légèrement incrustantes
pH                          | ≥ 6,5 et ≤ 9                    | Unité pH | Les eaux ne doivent pas être agressives.
Conductivité                | (plage)                         |          | Les eaux ne doivent pas être corrosives.
```

**L'exigence est purement qualitative.** Rédaction identique de 2007 à 2026.
L'agent a pris soin de vérifier que les tirets vus en mode `layout` étaient des
césures typographiques (`cal-cocarbonique`, `incrus-tantes`) et non des cases —
exactement la précaution que mon erreur de troncature de ce matin appelait.

**Zéro des 17 libellés n'a de valeur.** TH, TA, TAC, calcium, carbonates,
hydrogénocarbonates, silicates, CO2 libre, CO2 agressif, pH d'équilibre, essais
marbre, indice de Leroy : NON TROUVÉ partout, dans les quatre textes.

**Deux plages seulement dans toute l'annexe I**, toutes deux en références de
qualité : pH `≥ 6,5 et ≤ 9`, et conductivité `≥ 180 et ≤ 1 000 µS/cm à 20 °C`
(ou `≥ 200 et ≤ 1 100` à 25 °C). **La borne BASSE de conductivité est une
spécificité française** : la directive ne fixe qu'un plafond de 2 500 µS/cm et
tolère le pH jusqu'à 9,5. C'est un motif direct pour C12 — le droit national est
ici plus exigeant que le plancher européen, comme sur les huit paramètres
différés (C11.7.1).

**Le siège réel de l'exigence n'est pas l'arrêté, c'est le code de la santé
publique**, art. R. 1321-55 al. 2 : « À l'issue du traitement, l'eau distribuée
ne doit pas être agressive, corrosive ou gêner la désinfection. »

> **Nuance éditoriale décisive : cette exigence porte sur les INSTALLATIONS, pas
> sur l'eau comme risque sanitaire.** Une eau agressive n'est pas une eau
> dangereuse à boire — c'est une eau qui attaque les canalisations qu'elle
> traverse. Le §11.3 l'avait déjà posé ; le texte le confirme. À écrire ainsi,
> jamais autrement (§2.1, §2.2).

#### C11.8.2 L'INDICE N'EST PAS NUMÉRIQUE — il est textuel, et c'est décisif

**Le libellé « Equilibre calcocarbonique 0/1/2/3/4 » ne stocke aucun code
chiffré.** `resultat_num` est NULL sur **la totalité de ses 37 402 mesures** ; la
valeur vit en texte :

| catégorie | mesures |
|---|---|
| À l'équilibre | 17 873 |
| **Eau agressive** | **10 195** |
| Eau incrustante | 3 823 |
| Légèrement incrustante | 3 164 |
| Légèrement agressive | 2 345 |

**Conséquence immédiate** : la `reference_max` de 2,0 déclarée par la source ne
peut s'appliquer à aucune de ces mesures. Elle est structurellement inopérante.

**Et le codage n'est pas réglementaire.** C'est une convention SANDRE
(paramètre 2968, unité « sans objet »). La table des cinq codes n'a pas été
retrouvée, et l'agent ne l'a pas inventée. **Pire, il y a contradiction** : la
fiche SANDRE écrit « la référence de qualité à respecter est <= 1 », quand notre
source de données déclare 2. **À laisser en `indéterminé`** tant que ce n'est pas
tranché.

**Mais l'indice sépare des eaux réellement différentes.** Sur les 1 262 bulletins
portant l'indice et ses cinq composants simultanément quantifiés, les médianes
divergent nettement — TH médian **7,9** sous « Eau agressive » contre **22,35**
sous « À l'équilibre ». **Le détail que Yannick voulait donner a donc un
fondement mesurable**, et il ne vient pas du texte : il vient des données.

#### C11.8.3 L'eau agressive, dénombrée — et elle pointe vers l'Alsace

Écart entre pH initial et pH à l'équilibre : **1 079 mesures positives** (eau
sous-saturée, donc agressive) contre **193 négatives**. Mais le paramètre n'est
mesuré que sur **5 départements**, et deux portent l'essentiel : le **Bas-Rhin
(67)** avec 864 mesures à 77,8 % d'écart positif, et le **Lot-et-Garonne (47)**
avec 401 mesures à **100 %**.

> **C'est le motif alsacien qui ressort par une autre porte.** Le 67 a été
> collecté le 14 août pour l'angle « eau conforme et pourtant hors référence »
> (C11.5 / §26.5 de `docs/REPRISE.md`), sur l'hypothèse des chlorures. C'est
> l'agressivité qui répond. **À instruire — ce n'est pas encore un résultat**,
> le paramètre n'étant mesuré que sur 5 départements sur 33 : l'écart entre
> territoires mesurerait d'abord l'effort de recherche (§2.11).

#### C11.8.4 Deux doublons apparents, non tranchés

- **`Titre alcalimétrique` et `Titre alcalimétrique complet`** coexistent
  systématiquement quand le premier est quantifié (86 sur 86) — mais le TA n'est
  quasiment jamais quantifié : **86 fois sur 18 094 mesures**. Corrélation faible
  (−0,11 sur n=86).
- **`CO2 libre calculé` et `Anhydride carbonique libre`** partagent le **même
  code SANDRE 1344** mais portent des unités déclarées différentes, ne coexistent
  que partiellement (1 565 bulletins sur 6 510 + 4 240), et leur corrélation est
  quasi nulle (0,04). **Les données ne tranchent pas** entre doublon de méthode
  et grandeurs distinctes.

**Un même code SANDRE pour deux objets : c'est le motif du §11.2** (sélénium
1385, chlorates 1752, turbidité 1295). **Ne pas apparier par ce code avant
d'avoir tranché.**

#### C11.8.5 UN DÉFAUT QUE J'AI INTRODUIT CE MATIN, et sa mesure honnête

La phase 2 a fait entrer la référence déclarée dans `notee`. Pour l'indice
calcocarbonique, cela produit **37 402 mesures comptées comme « notées » alors
qu'aucune comparaison n'est possible en principe** — la valeur est un texte, pas
un nombre.

**Portée réelle : 37 402 sur 14 188 024, soit 0,26 % du numérateur.** Réel, à
corriger, sans urgence.

> **ET UNE ERREUR DE CONTRÔLE, À NE PAS REFAIRE.** J'ai d'abord mesuré cela par
> « combien de mesures notées n'ont pas de `resultat_num` » et trouvé
> 13 555 860 sur 874 libellés, soit un écart de couverture de 87 points. **Ce
> chiffre ne veut rien dire** : une mesure sous le seuil de quantification a
> `resultat_num` NULL et reste parfaitement notée — glyphosate, atrazine, diuron
> en tête de liste. Mon contrôle mesurait le taux de quantification du corpus, pas
> un défaut.
>
> **La leçon : un contrôle qui rend un chiffre spectaculaire doit être suspecté
> avant d'être publié.** C'est la règle du §22.5 — « un outil qui répond “rien à
> faire” se vérifie » — dans l'autre sens : un outil qui répond « catastrophe »
> se vérifie aussi.

Le correctif juste est étroit : **exiger que la comparaison soit possible**, pas
qu'un résultat soit quantifié. À écrire en phase 5.

#### C11.8.6 Ce qui reste ouvert

1. ~~L'arrêté du 21 janvier 2010~~ — **PISTE SUIVIE ET ABOUTIE le 15 août 2026,
   voir C11.9 ci-dessous. La réponse est trouvée, et elle est meilleure que
   l'hypothèse.**
2. **La table des cinq codes SANDRE 2968**, introuvable, et la contradiction
   `<= 1` (SANDRE) contre `2` (notre source).
3. **Le doublon SANDRE 1344**, non tranché.
4. **Une anomalie signalée, non corrigée** : un carbonate à **−1 124,4** sur le
   bulletin `00700196491`. Une concentration négative n'existe pas.
5. **L'angle éditorial le plus solide**, relevé par l'agent : la directive
   (annexe IV) **impose de communiquer** dureté, calcium, magnésium et potassium
   en les qualifiant expressément de « parameters not listed in Part C of
   Annex I ». **Une information due précisément parce qu'elle n'est pas normée.**
   C'est exactement le sujet de C12.

---

### C11.9 LA PISTE DE 2010 A ABOUTI — et elle renverse la question

Instruite en direct le 15 août 2026, sans agent : un texte, des questions
précises, **deux lectures indépendantes** de la même page pour se contrôler.
Source archivée : `Sources/REG_Reglementation_et_seuils/REG-10_FR_arrete-2007-01-11_programme-analyses.md`.

#### C11.9.1 Le texte cherché n'est pas celui de 2010 — et il y a DEUX arrêtés du 11 janvier 2007

L'arrêté du 21 janvier 2010 ne fait que **modifier** un texte antérieur, et il
n'apparaît même plus dans la liste des modificateurs de la version consolidée :
il a été absorbé. Le texte qui compte est :

**Arrêté du 11 janvier 2007 relatif au PROGRAMME de prélèvements et d'analyses**,
`LEGITEXT000006055434` — **entièrement absent du dossier `Sources/`**, désormais
catalogué **REG-10**.

> **PIÈGE À GRAVER : il existe deux arrêtés du 11 janvier 2007.**
> `JORFTEXT000000465574` porte les **limites et références de qualité** (nos
> REG-02 et REG-06) ; `LEGITEXT000006055434` porte le **programme d'analyses**.
> Même jour, objets différents. C'est le motif de REG-09 sur les arrêtés du
> 30 décembre 2022, transposé de 2022 à 2007.

#### C11.9.2 LA RÉPONSE AUX 191 752 MESURES — et elle est meilleure que l'hypothèse

Annexe I, tableau 1, **note (3)**, confirmée mot pour mot par deux lectures :

> « Les concentrations en **calcium, magnésium et potassium** doivent être
> exprimées par le laboratoire d'analyses **concomitamment au calcul de
> l'équilibre calcocarbonique**. »

**L'hypothèse était « ces paramètres sont imposés au programme sans être
normés ». La réalité est plus forte : le texte impose de les EXPRIMER, parce
qu'ils sont les termes du calcul.** Ce ne sont pas des paramètres oubliés par la
norme, ce sont des **supports de calcul** — exactement le statut des
concentrations dérivées du volet radiologique (C11.6.3 ter), et le même piège
si on les jugeait individuellement.

> **Cela fonde la demande de Yannick sur le texte, et pas seulement sur les
> données.** Il voulait « donner le détail » derrière le total calco-carbonique.
> **Le détail est prescrit par l'arrêté** : le laboratoire doit l'exprimer. La
> fiche peut donc l'afficher en s'appuyant sur une obligation, pas sur un choix
> éditorial. C'est le meilleur socle possible pour la décision 4.

#### C11.9.3 L'« analyse complète » a une définition réglementaire — inutilisable chez nous

Six programmes : **RP** et **RS** (ressource, souterraine / superficielle),
**RSadd**, **A** (routine), **B**, **Badd**. Et la définition littérale :

> B = « programme d'analyses complémentaire par rapport à A **permettant
> d'obtenir le programme d'analyses complet (A + B)** »

**L'analyse complète, c'est A + B.** Le texte ne donne aucun nombre de paramètres.

**Mais Hub'Eau n'expose pas le type de programme** — vérifié le 15 août sur le
cache brut : aucun champ A/B/RP/RS parmi les 30 champs rendus par l'API.

> **Conséquence pour `CLAUDE.md` §2.3.** `SEUIL_COMPLET = 200` reste le seul
> critère disponible, et **il faut continuer de le présenter comme une convention
> du projet** — jamais comme la définition réglementaire, qui existe et que nous
> ne pouvons pas appliquer. C'est une limite à déclarer, pas à masquer (§2.8).

#### C11.9.4 TROIS arrêtés du 30 décembre 2022, et un texte de 2026 que le dépôt ignore

| texte | NOR | objet | entrée en vigueur |
|---|---|---|---|
| Arrêté du 30/12/2022 | `SPRP2221010A` | limites et références de qualité | 1er janvier 2023 |
| Arrêté du 30/12/2022 | `SPRP2221012A` | modalités de dérogation | — |
| **Arrêté du 30/12/2022** | **`SPRP2221017A`** | **programmes d'analyses** | **1er janvier 2026** |
| **Arrêté du 28 juillet 2026** | — | article 3 du programme | **3 août 2026** |

**Deux faits neufs :**

1. **Ils sont trois, pas deux.** REG-09 en signalait deux ; voici le troisième.
   Seul le NOR les sépare de façon fiable — et **leurs dates d'entrée en vigueur
   diffèrent de trois ans** : la grille au 1er janvier 2023, les programmes au
   1er janvier 2026.
2. **Un arrêté du 28 juillet 2026 est en vigueur depuis le 3 août — il y a douze
   jours.** Le dépôt n'en sait rien et son contenu n'a pas été lu. **À traiter :
   c'est le texte le plus récent du corpus réglementaire du projet.**

#### C11.9.5 Une contradiction entre mes deux lectures, non tranchée

Sur le **titre hydrotimétrique** — 38 234 mesures au corpus — les deux lectures
de la même page se contredisent : la première conclut qu'il n'apparaît **nulle
part** dans le texte, la seconde le trouve sous « Dureté (ou Titre
hydrotimétrique) » en RP/RS.

**Aucune ne fait foi.** C'est une relecture humaine du tableau 1, et elle est
courte. Je la signale plutôt que de choisir — choisir ici serait exactement ce
que le §2.7 interdit.

**Ce que cet épisode enseigne sur la méthode** : deux lectures d'une même source
par le même outil ne sont pas redondantes. Elles ont concordé sur la note (3) —
ce qui la solidifie — et divergé sur le TH, ce qui a évité d'écrire une
affirmation fausse. **La double lecture est à garder pour toute source lue en
ligne.**

---

### C11.10 Dossier DÉSINFECTION — instruit le 15 août 2026. Dernier des cinq.

Livrables : `data/etudes/DESINFECTION_source_reglementaire.md` et
`data/etudes/DESINFECTION_inventaire_corpus.md`.

#### C11.10.1 LE TEXTE QUI FONDE LE DOSSIER — CSP art. R. 1321-23

**C'est la trouvaille du dossier**, et elle répond exactement à la décision 12.
Deux lectures en ligne mot pour mot identiques :

> « Lorsque la préparation ou la distribution […] comprend un traitement de
> désinfection, l'efficacité du traitement appliqué est vérifiée par la personne
> responsable […], qui **s'assure que toute contamination par les sous-produits
> de la désinfection est maintenue au niveau le plus bas possible sans
> compromettre la désinfection**. »
> — CSP art. R. 1321-23, en vigueur au 01/01/2023. Source : directive (UE)
> 2020/2184, art. 9 § 3 (d).

**L'arbitrage est écrit dans le droit lui-même** : le plus bas possible *sans
compromettre la désinfection*. Le sujet de Yannick n'a donc pas besoin d'une
affirmation sanitaire — **il est déjà posé par le texte**, et le corpus peut le
documenter.

Le même arbitrage est répété en note de tableau pour **bromates, chlorates,
chlorites et THM** — **mais pas pour les acides haloacétiques**. Asymétrie
constatée, non expliquée.

#### C11.10.2 Le désinfectant résiduel n'a aucune valeur numérique

Paramètre par paramètre, partie d'annexe lue et non devinée :

| paramètre | valeur |
|---|---|
| Chlore libre, chlore total | **aucune valeur chiffrée** — une entrée qualitative en **II. − Références de qualité** : « Absence d'odeur ou de saveur désagréable et pas de changement anormal ». Identique depuis 2007 |
| Chlore combiné, ClO₂, résiduel de ClO₂, ozone | **NON. Aucune entrée.** |

Et **aucune obligation de désinfecter l'eau** : R. 1321-56 impose de désinfecter
les **ouvrages** (avant mise en service, réservoirs une fois par an) ;
R. 1321-55 al. 2 interdit à l'eau de « gêner la désinfection » ; R. 1321-23
n'impose que de **vérifier** l'efficacité *si* la désinfection est pratiquée.

**Le classement en `rien_ne_se_prononce_etabli` est donc justifié** pour les six :
nous avons cherché, aucun texte ne leur oppose de valeur.

#### C11.10.3 Les sous-produits, et un piège de date

Tous en **I. – Limites de qualité**, en vigueur au 01/01/2023 : THM total
100 µg/L (somme de 4, aucune valeur individuelle), acides haloacétiques 60 µg/L
(somme de 5, **nouveau**), chlorates 0,25 mg/L (**nouveau**), chlorites
0,25 mg/L (**nouveau**), bromates 10 µg/L.

**Le seuil conditionnel, phrase exacte** :

> « La limite de qualité est fixée à **0,70 mg/L** lorsqu'une méthode de
> désinfection des eaux destinées à la consommation humaine **qui génère des
> chlorates** est utilisée. »

La condition porte sur **la méthode qui génère la substance**. Le texte français
ne nomme aucun procédé ; la directive ajoute « in particular chlorine dioxide ».
**Rien dans nos données ne dit quel procédé est employé** — d'où
`indetermine_condition`, et l'asymétrie assumée du §2.13.

**Piège de date signalé** : les chlorites portent en plus une **référence de
qualité de 0,20 mg/L « qui s'applique jusqu'au 31 décembre 2025 »**. C'est le cas
de seuil **daté par le haut** que le modèle ne sait pas exprimer (`CLAUDE.md` §8).

> **Contrôlé en base — le défaut redouté NE SE PRODUIT PAS.** La référence de
> 0,20 n'est plus déclarée par la source après 2020, et `reference_max` est NULL
> sur toutes les mesures de 2026. **Nous n'appliquons aucune référence éteinte.**
> Le trou du modèle est réel, il n'a pas de conséquence ici.

#### C11.10.4 Ce que le corpus montre, et comment il faut le dire

**17 libellés, 277 378 mesures, 151 411 quantifications, 38 679 bulletins,
33 départements.** 31 594 bulletins portent à la fois un chlore et un
sous-produit.

**Le gradient, vérifié en session principale sur 21 779 bulletins :**

| tranche de chlore libre | bulletins | chlore médian | THM médian | THM Q3 |
|---|---|---|---|---|
| non quantifié | 918 | — | **2,66** | 7,41 |
| Q1 | 5 445 | 0,15 | 3,76 | 8,91 |
| Q2 | 5 445 | 0,28 | 4,00 | 8,80 |
| Q3 | 5 445 | 0,40 | 4,70 | 10,60 |
| **Q4** | 5 444 | 0,60 | **6,70** | 13,50 |

**Et la corrélation, qui tempère tout : r = 0,177, soit 3,1 % de variance
expliquée.**

> **LES DEUX ÉNONCÉS SONT VRAIS ET NE DISENT PAS LA MÊME CHOSE.** Au niveau du
> bulletin, le chlore résiduel n'explique que 3 % de la variation des THM :
> connaître le chlore d'une commune ne permet pas de prédire ses THM. Au niveau
> des groupes, le gradient est net, monotone et vaut un facteur 2,5.
>
> **Écrire « le chlore fait monter les THM » sur un r de 0,18 serait un faux
> positif.** La formulation qui tient : *« les bulletins du quart le plus chloré
> portent une médiane de trihalométhanes 2,5 fois supérieure à ceux où le chlore
> n'est pas quantifié — sur 21 779 bulletins »*. Un fait, son dénominateur, son
> périmètre. C'est le §2.11 transposé du classement à la corrélation.

**Dépassements réels des sous-produits** : bromates **74**, chlorite **136**,
THM **25**, chloroforme 13, chlorate 3, plus **8 `indetermine_condition`**.
Bromoforme, chlorodibromométhane, dichloromonobromométhane et acides
haloacétiques : **zéro**. **Les bromates sont le premier poste, devant les THM.**

**Un fait constaté et NON expliqué** : les dépassements de chlorite s'effondrent
en 2023 — 26 en 2020, 18 en 2021, 17 en 2022, puis **2, 1, 1, 0**. Le seuil n'a
pourtant pas bougé (0,25 dans les deux grilles). Changement de pratique, de
procédé, de libellé porteur, ou effet du seuil conditionnel : **rien dans les
données ne tranche, et il ne faut pas le deviner.**

**Et la campagne d'hier a créé le dossier** : l'**ozone n'existe que dans la
Loire (42)** et le **bioxyde de chlore est dominant en Isère (38)** — les deux
départements collectés le 14 août. Sans eux, la variété des procédés de
désinfection n'était pas dans le corpus.

#### C11.10.5 LA VARIANCE DE LA CHLORATION — question de Yannick, mesurée le 15 août

*« Peut-on mesurer la variance de la chloration entre deux bulletins ? »* Oui, et
la réponse éclaire le gradient du C11.10.4. Deux questions à ne pas confondre :
la variation **d'un même point d'eau dans le temps**, et celle **d'un point d'eau
à l'autre**. Décomposition sur 28 737 mesures quantifiées, 3 553 installations,
médiane 0,32 mg/L.

```
variance totale                    0,108
  dont INTER-installations         0,039   ->  35,9 %
  dont INTRA-installation          0,070   ->  64,1 %
```

**Le point d'eau n'explique que 36 % de la variation du chlore libre. Près des
deux tiers se jouent à l'intérieur d'un même point d'eau.**

Sur les 1 731 installations à ≥ 5 bulletins : coefficient de variation interne
médian **0,358** (Q1 0,257 · Q3 0,493), étendue médiane max − min de
**0,37 mg/L**, et **rapport médian max/min de × 4,0**. D'un bulletin au suivant
(25 184 paires) : écart absolu médian 0,09 mg/L, **écart relatif médian 28 %**,
9ᵉ décile 0,29 mg/L.

> **CE QUE CELA CHANGE POUR LE GRADIENT DU §C11.10.4.** Si 64 % de la variation
> se joue dans un point d'eau, alors **la valeur de chlore d'un bulletin est un
> instantané, pas une caractéristique du lieu**. C'est très probablement une
> partie de l'explication du r = 0,177 : on corrèle un instantané bruité avec un
> cumul. Le découpage par tranches, lui, moyenne ce bruit — d'où sa netteté
> malgré une corrélation faible. **Les deux résultats se complètent au lieu de
> se contredire.**

**Trois réserves, et elles portent la moitié de la réponse :**

1. **Le chlore est mesuré au robinet, pas au point de dosage.** Il se dégrade
   avec le temps de séjour, la température, la longueur et le matériau du
   réseau. Une part de ces 64 % est de la physique de réseau, pas du pilotage.
2. **« Même point d'eau » signifie « même installation amont »**, pas « même
   robinet » : deux bulletins peuvent être prélevés à deux endroits du réseau.
3. **La saison n'a pas été neutralisée** — le chlore se dégrade plus vite en été.

**Et une variabilité n'est pas une faute** (§2.1). Il n'existe aucune valeur
opposable sur le chlore résiduel (§C11.10.2) : il n'y a donc ni cible à tenir,
ni écart à reprocher. Ce qui se dit : *le chlore résiduel au robinet n'est pas
une propriété stable d'un point d'eau — il est dominé par ce qui se passe entre
l'usine et le robinet.*

**Anomalie signalée, non corrigée** : le maximum de chlore libre du corpus est de
**31 mg/L**, valeur non plausible en eau distribuée. À ranger avec le carbonate à
−1 124,4 du §C11.8.6 : deux valeurs à instruire, probablement des erreurs
d'unité ou de saisie.

#### C11.10.6 Trois réserves de l'agent, à ne pas publier en l'état

1. **Les programmes d'analyses où le chlore est exigé donnent trois réponses
   divergentes** (RP+RS+A / A+B / RP) — non tranché.
2. **Le seuil de 0,5 mg/L déclenchant la mesure des THM** vient de lectures en
   ligne non confirmées sur un JO.
3. **Deux URL de section du CSP ont renvoyé 404** : la couverture du code n'est
   pas exhaustive.

---

### C11.11 Phases 4 et 5 — FAITES le 15 août 2026

#### C11.11.1 Phase 4 — les deux blocs, instruits

Livrable : `data/etudes/CYANO_PCB_source_reglementaire.md`. Quatre requêtes
Légifrance, **doubles lectures sans aucune divergence**.

**Microcystines — la France ne nomme pas la LR, elle agrège.** La directive fixe
la **microcystine-LR à 1,0 μg/l** (annexe I partie B, applicable au 12/01/2026,
art. 25). Le droit français retient **« Total microcystines », 1,0 µg/L, en
limite de qualité** — présent dès le JO du 6 février 2007, rédaction actuelle de
l'arrêté du 30/12/2022 en vigueur au 1er janvier 2023, « ensemble des variants,
intra et extracellulaires », « uniquement pour les eaux d'origine
superficielle ». **La valeur n'a jamais bougé.** Aucun variant individuel n'est
nommé.

> **Lacune trouvée au passage** : le corpus porte **16 libellés de microcystines
> dosées**, tous jugés en `juge_sur_valeur_declaree` — sur la seule foi de ce que
> l'administration déclare, **sans aucune ligne de référentiel derrière**. Ni
> date, ni source, ni fiabilité. Corrigé en phase 5.

**Dénombrements — aucun seuil en EDCH.** La valeur de 100 000 cellules/mL existe,
mais pour les **baignades artificielles** (arrêté du 15/04/2019), hors périmètre,
et elle a été **supprimée le 19 décembre 2025**. Chlorophylle A et nodularine :
nommées par aucun texte.

**PCB — non, nettement.** Six recherches distinctes sur quatre textes, aucune
occurrence. Et **absents du programme d'analyses** aussi. **219 043 mesures que
ni une valeur ni une obligation de contrôle n'expliquent** — cause non
identifiée, et non supposée. Fait remarquable pour C12.

#### C11.11.2 Phase 5 — 363 lignes, UNE seule valeur

Écrite par `src/ecrire_referentiel_c11.py`, reproductible, avec un mode
`--essai`. **Un générateur et non une saisie** : 360 lignes à la main dans un CSV
de 21 colonnes séparées par des points-virgules est exactement la façon dont
l'erreur de décalage a été commise deux fois en août (`CLAUDE.md` §5).

```
référentiel          94 -> 457 lignes
version_referentiel  9a2777400815 -> 4a4a38e2c622
version_moteur       5a5473295577 -> b964e3b00ad6   (vue ajoutée)
```

| attribution | mesures | libellés |
|---|---|---|
| **`rien_ne_se_prononce_non_instruit`** | **0** | **0 — la catégorie a disparu** |
| `rien_ne_se_prononce_etabli` | 1 343 844 | **334** (était 5) |
| `juge_avec_son_groupe` | 62 987 | **46** (était 13) |
| `hors_perimetre` | 21 358 | 5 |

**Une seule valeur écrite** : « Total microcystines » 1,0 µg/L, limite, lue et
sourcée. Plus quatre gestes ciblés : 16 PFAS et 14 radionucléides et les
variants de microcystine en `dans somme`, et **`2023-01-01` posé sur les cinq
lignes de l'article 25 qui n'avaient pas de date**.

**`fiabilite` sépare honnêtement ce qui a été lu de ce qui ne l'a pas été** :
`verifie` pour les sept dossiers instruits, **`a_verifier` pour les quatre que
personne n'a lus contre un texte** — paramètres généraux (15), microbiologie
(14), organoleptique (8), spéciation métaux (1). Écrire « nous avons cherché »
sans avoir cherché aurait été invisible et faux.

#### C11.11.3 DEUX TESTS ONT ÉCHOUÉ, ET ILS AVAIENT RAISON

`test_verdict.py` et `test_figer.py` prenaient tous deux **le calcium** pour
incarner « ce que le référentiel ignore ». Le dossier calco-carbonique lui a
donné une ligne : les montages ont cessé de tester ce qu'ils annonçaient.

Basculés sur un libellé **volontairement fictif**, qui ne peut plus se périmer.

> **Piège de conception à retenir : un test qui prend une VRAIE substance pour
> exemple d'absence devient faux le jour où l'on comble l'absence.** Le montage
> doit être fictif quand il incarne un manque.

#### C11.11.4 La vue de diagnostic était devenue menteuse — corrigée

En ajoutant 363 lignes sans valeur, la phase 5 a rompu une identité tacite :

```
v_parametres_non_apparies (aucune LIGNE)   :    5 libellés   (était 362)
sans aucun SEUIL de comparaison            :  380 libellés
```

`v_parametres_non_apparies` filtre sur l'appariement, pas sur le seuil. Tant que
le référentiel était pauvre, les deux questions avaient la même réponse.
**Un diagnostic qui sous-compte par 75 est pire qu'absent** — il fait croire le
problème résolu.

**Vue `v_parametres_sans_seuil` ajoutée** (décision de Yannick), et les deux sont
gardées parce qu'elles ne disent pas la même chose : l'une est un **défaut
d'appariement** à corriger, l'autre une **absence de valeur** qui peut être un
fait établi. `CLAUDE.md` §4 est corrigé — sa description attribuait à la première
ce que seule la seconde rend.

Ce qu'elle montre, et c'est la photographie du chantier :

| attribution | fiabilité | libellés | mesures | quantifiées |
|---|---|---|---|---|
| instruit, aucune valeur opposable | `verifie` | **294** | 1 097 819 | 463 731 |
| jugé avec son groupe | `verifie` | **46** | 62 987 | 5 087 |
| non instruit | `a_verifier` | **40** | 246 025 | 25 146 |
| **TOTAL** | | **380** | 1 406 831 | 493 964 |

**Les 46 « jugés avec leur groupe » sont l'entrée la plus utile** : ils n'ont
aucun seuil individuel et ne sont pourtant pas ignorés — PFAS, radionucléides et
variants de microcystine sont jugés par leur somme. Sans cette colonne, on les
compterait comme des angles morts.

---

### C11.12 L'ALUMINIUM ROUVERT — mais sur un autre versant (15 août 2026)

Source archivée : **CIV-06**, réponse de la secrétaire d'État à la santé au
Sénat, 15 février 2011 (question orale n° 1056S, JO du 14/10/2010).

**Le versant sanitaire reste clos.** L'angle Alzheimer et perturbation
endocrinienne avait été écarté le 9 août 2026, et cet abandon est confirmé par
le ministère lui-même — *« les données épidémiologiques et physiologiques dont
on dispose ne permettent pas d attribuer un rôle étiologique à l aluminium dans
la maladie d Alzheimer »*. Réserve : la position date de 2011 et s appuie sur
une expertise de 2003 confirmée en 2008. **Ce n est pas l état de la science**,
c est la position de l administration à cette date (§2.5).

**Ce que la phrase du ministère rouvre**, et c est la décision de Yannick :

> *« Ce paramètre est un indicateur de fonctionnement des INSTALLATIONS DE
> TRAITEMENT et non pas un paramètre de santé. »*

Si les 200 µg/L mesurent le fonctionnement d une installation, **l aluminium n
est pas un polluant de la ressource : c est un résidu de traitement.** Il rejoint
exactement la famille instruite en C11.10.

| ce que le traitement laisse | paramètres | nature de la valeur |
|---|---|---|
| **coagulant résiduel** | aluminium total, aluminium dissous | référence 200 µg/L, « indicateur de fonctionnement » |
| **désinfectant résiduel** | chlore libre, total, combiné, ClO2, ozone | **aucune valeur** (C11.10.2) |
| **sous-produits de désinfection** | THM, chlorites, chlorates, bromates, AHA | **limites de qualité** |

**Trois natures de valeur pour une même question — et c est ce qui fait le
sujet.** Il ne demande aucune affirmation sanitaire : *que reste-t-il dans l eau
de ce qu on y a mis pour la traiter ?*

**Ce que le corpus porte déjà** : aluminium total, 37 279 mesures, 13 499
quantifiées, **120 dépassements**, maximum à **2 000 µg/L** — dix fois la
référence. Ces 120 s affichent en ambre et non en rouge (§11.3), et **CIV-06 est
désormais la citation qui le justifie**, à la place d une déduction.

**À instruire** : le sulfate d aluminium comme coagulant ; ce que le résidu dit
du réglage de l installation ; et surtout **si un texte relie le coagulant à son
résidu** comme l article R. 1321-23 du CSP relie la désinfection à ses
sous-produits (C11.10.1). Si un tel texte existe, le dossier a le même socle
réglementaire que la chloration.

---

## C12 — LA CHAÎNE NORMATIVE : comment se fabrique la notion de potabilité

**Ouvert le 15 août 2026. Dossier ÉDITORIAL, à traiter plus tard.**
Décision de Yannick : *« c'est un super dossier éditorial. On le traitera plus
tard, mais il fera partie des dossiers : expliquer comment fonctionne la chaîne
normative pour définir la notion de potabilité. »*

**Rien n'est à coder ici.** C'est un dossier de prose, du même étage que les
dossiers de substance (`sortie/dossier_substance.py`), mais son objet n'est pas
une molécule : c'est **la norme elle-même**.

### C12.1 La thèse

Le projet démontre depuis l'origine que **le verdict bouge quand le seuil bouge**.
Ce dossier déplace la démonstration d'un cran : **le seuil lui-même n'est pas un
objet unique.** Pour savoir si une eau est potable sur un paramètre donné, il
faut souvent remonter quatre ou cinq textes qui se renvoient l'un à l'autre — et
le premier de la chaîne ne contient aucun chiffre.

> Ce n'est pas l'eau qui est devenue potable, c'est la limite qui a bougé.
> **Et cette limite n'est écrite nulle part en un seul endroit.**

**Précaution de ton, non négociable (§2.1)** : le sujet est la *construction* de
la règle, jamais son illisibilité présentée comme une faute, et jamais
l'administration. Une chaîne de renvois est le fonctionnement normal du droit,
pas une dissimulation. Écrire « voici comment la règle se construit », **jamais**
« on vous noie sous les textes ».

### C12.2 La matière déjà établie — tout est daté et cité

Elle a été produite les 14 et 15 août en instruisant les dossiers PFAS et
radiologique. **Tout est vérifié en session principale, citations littérales
disponibles dans les fichiers indiqués.**

**a) La chaîne radiologique, quatre sauts, aucun chiffre dans le premier texte :**

```
REG-03  arrêté du 30/12/2022
   └─ « les radionucléides spécifiques définis dans l'arrêté mentionné à
      l'article R. 1321-20 »          ← il ne le NOMME même pas
        └─ RAD-02  arrêté du 12 mai 2004 — porte les 14 concentrations dérivées
             └─ art. 6 (rédaction 2015) : « les modalités de contrôle du radon
                sont fixées par un arrêté du ministre chargé de la santé »
                                        ← 5ᵉ texte, non identifié à ce jour

REG-01  directive (UE) 2020/2184, considérant 52
   └─ « this Directive should not set out parametric values on radioactivity »
        └─ RAD-01  directive 2013/51/Euratom
```

**b) Deux textes, deux dates, même substance.** La directive diffère huit
paramètres au **12 janvier 2026** (art. 25 §1) — bisphénol A, chlorate, chlorite,
acides haloacétiques, microcystine-LR, PFAS Total, somme des PFAS, uranium.
L'arrêté français porte : *« le texte entre en vigueur le 1er janvier 2023 »*,
sans aucune date différée. Sur les 4 bulletins du corpus qui dépassent la somme
des 20 PFAS, **entre 1 et 3 changent de verdict selon le texte qu'on retient.**

**c) Une condition française absente du texte européen.** Le radon n'est encadré
« Uniquement pour les eaux d'origine souterraine » que par le droit français —
la directive 2013/51/Euratom ne porte aucune restriction de ce genre. La
restriction est même **antérieure** : elle figure déjà à l'article 3 de l'arrêté
de 2004.

**d) Cinq degrés de valeur, à l'intérieur même des textes contraignants :**

| degré | ce qu'un dépassement produit | exemple établi |
|---|---|---|
| limite de qualité | non-conformité | somme des 20 PFAS, 0,10 µg/L |
| référence de qualité | non-conformité aux références | radon 100 Bq/L, dose indicative 0,1 mSv/an |
| valeur indicative | actions correctives, **pas** de non-conformité | métabolites non pertinents, 0,9 µg/L |
| valeur de vigilance | suivi | 17-bêta estradiol |
| **valeur guide / seuil de dépistage** | **une analyse complémentaire, rien d'autre** | alpha 0,1 et bêta résiduelle 1,0 Bq/L |

Le dernier degré est le plus démonstratif : **trois textes indépendants**
concordent pour dire que ces nombres ne jugent rien — annexe III de la directive
Euratom, colonne NOTES de l'arrêté de 2022 (colonnes « références » et « unités »
vides), et l'article 3 de l'arrêté de 2004 qui écrit le mot **« valeurs
guides »**. Un lecteur qui verrait « 0,1 Bq/L » sans cette clé croirait à un
seuil.

**e) Un nombre qui n'est pas un seuil mais un dénominateur.** Les 14
concentrations dérivées des radionucléides ne sont pas des limites : chacune est
la concentration qui, **seule**, produirait la dose indicative de 0,1 mSv/an. Le
verdict se rend sur la somme, jamais sur un terme. Même figure que les quatre
HAP et que le « total pesticides ».

**f) Le corpus de sources lui-même est hétérogène.** 53 sources, 9 familles. Le
référentiel s'appuie 108 fois sur `REG`, 3 fois sur `RAD`, 1 fois sur `CIRC`. Et
une bonne part du catalogue n'est **pas** de la norme : valeurs guides de l'OMS,
valeurs de gestion de la DGS (famille `GEST`, créée exprès pour les distinguer),
réglementations étrangères qui alimentent `seuil_strict`, avis d'agences.

### C12.3 Ce qui manque pour l'écrire

1. **Le 5ᵉ texte radiologique** — l'arrêté sur les modalités de contrôle du
   radon, appelé par l'article 6 de RAD-02, jamais identifié.
2. **Le lien de transposition** entre l'arrêté du 9 décembre 2015 et la directive
   2013/51/Euratom : la coïncidence de dates est frappante (échéance au
   28 novembre 2015, arrêté du 9 décembre), **le texte n'en dit rien**, et
   l'écrire sans preuve serait refaire l'erreur du §8 de `docs/REPRISE.md`.
3. **Un schéma**. Ce dossier est le premier du projet qui se lit mieux en image
   qu'en prose : la chaîne des renvois demande à être vue.
4. **Le fichier `referentiel/sources.csv`** (voir C11) — sans lui, aucun renvoi
   n'est cliquable depuis une fiche.

### C12.4 Pourquoi ce dossier est solide

Il ne demande **aucune donnée nouvelle** et ne dépend d'aucun refigeage : tout
repose sur des textes lus et cités. Il ne prononce aucun verdict sur aucune eau,
donc il ne peut produire aucun faux positif. Et il répond à la question que pose
tout lecteur arrivé sur une fiche — **« d'où sort ce chiffre ? »** — au niveau
où elle mérite d'être posée.

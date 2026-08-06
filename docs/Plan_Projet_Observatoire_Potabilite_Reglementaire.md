# Plan de projet — Observatoire citoyen de la « potabilité réglementaire » de l'eau en France

> Projet open data. Document de cadrage v1 — 21 juillet 2026.
> Nom de travail : **REGL'EAU / L'Observatoire de la norme** (à arbitrer).
> Auteur du projet : Yannick (Éditions Mytae). Rédaction assistée par IA à partir de la note de méthode Hub'Eau (05/07/2026).

---

## 1. Vision en une phrase

**La potabilité n'est pas une propriété de l'eau : c'est une décision réglementaire, datée.** Ce projet rend cette décision visible, mesurable et ouverte à tous, en montrant qu'une eau administrativement « potable » en 2026 ne l'aurait pas toujours été avec la grille de 2016 — sans qu'une seule molécule n'ait changé.

Démarche : **citoyenne, transparente, reproductible et open data**. Chaque chiffre est traçable jusqu'à sa source officielle (API Hub'Eau + texte réglementaire). Rien n'est inventé.

---

## 2. Le principe fondateur : séparer la mesure du verdict

Tout le projet repose sur une distinction que le débat public confond en permanence :

- **La mesure** — ce que le laboratoire trouve réellement dans l'eau (`resultat_numerique`, en µg/L, mg/L…). C'est un fait physico-chimique.
- **Le verdict** — le « conforme / non conforme » affiché. Ce n'est PAS un fait : c'est le résultat d'une comparaison entre la mesure et un **seuil réglementaire en vigueur à une date donnée**.

Changez le seuil, et le même chiffre change de verdict. C'est exactement ce qui s'est produit ces dernières années.

**Le geste central du projet — le « réétalonnage réglementaire daté » :** on prend une mesure brute et on la confronte à **deux grilles** (celle de 2016 et celle de 2026). Quand le verdict s'inverse alors que la mesure est identique, on a une preuve chiffrée et opposable de « potabilisation par la norme ».

C'est ce geste qui manque à la méthode actuelle (qui lit le verdict de Hub'Eau) et qui fait l'originalité — et la valeur — de ce projet.

---

## 3. Preuves de concept déjà établies

Trois faits réglementaires vérifiés fondent la crédibilité du projet dès le départ.

### 3.1 Le reclassement d'un métabolite « pertinent » → « non pertinent » (le cas emblématique)

En **avril 2024, l'ANSES a reclassé le métabolite R471811 du chlorothalonil** (un fongicide) de « pertinent » à « non pertinent ». Conséquence directe : le seuil applicable passe de **0,1 µg/L (limite de qualité) à 0,9 µg/L (valeur de vigilance)**. Or, avant ce changement, **34 % des échantillons d'eau potable dépassaient 0,1 µg/L**.

Traduction concrète : une eau à 0,5 µg/L de R471811 était **non conforme au printemps 2024 et conforme quelques semaines plus tard**. Le même mécanisme concerne d'autres métabolites (ex. métolachlore ESA, cité dans la note de méthode — à documenter précisément en phase 1).

C'est le **pilote n°1** idéal : national, chiffrable, spectaculaire, et directement cartographiable via Hub'Eau (`code_parametre` du R471811).

### 3.2 Le relèvement de limites de qualité (directive 2020/2184)

La refonte de la directive européenne sur l'eau potable (**Directive (UE) 2020/2184**) a été transposée en droit français par l'**arrêté du 30 décembre 2022**, entré en vigueur au **1er janvier 2023**. Il a notamment *relevé* plusieurs seuils par rapport à la version antérieure de l'arrêté du 11 janvier 2007 :

- **Antimoine** : 5 → 10 µg/L
- **Bore** : 1 → 1,5 mg/L
- **Sélénium** : 10 → 20 µg/L

Là encore : des eaux hors limite hier deviennent conformes aujourd'hui, par décision administrative.

### 3.3 La nuance qui rend le projet crédible : la grille a aussi été durcie

Honnêteté intellectuelle indispensable — et c'est un atout, pas une faiblesse : la **même** directive a aussi **renforcé** le contrôle. Depuis le **1er février 2025**, la recherche des **PFAS** est intégrée au contrôle sanitaire systématique (somme de 20 PFAS, limite 0,1 µg/L) ; d'autres paramètres ont été ajoutés (bisphénol A, etc.).

Le message juste n'est donc pas « on a tout assoupli », mais **« on a redécoupé la grille »** — avec des cas d'assouplissement documentés et indéfendables du point de vue sanitaire (les métabolites), et des cas de durcissement réels. Cette rigueur protège le projet des accusations de militantisme approximatif et le rend opposable.

---

## 4. Architecture des données (conçue pour grandir)

Le cœur technique est une base de données **modulaire et incrémentale** : on commence avec un paramètre et quelques communes, et la même structure absorbe demain la France entière sans être refondue.

### 4.1 Les sources

- **Mesures** : API **Hub'Eau** — thème « Qualité de l'eau potable » (base SISE-Eaux du ministère de la Santé), endpoint `resultats_dis`. Données ouvertes, officielles, réutilisables.
- **Seuils** : textes réglementaires officiels (arrêté du 11/01/2007 modifié, arrêté du 30/12/2022, avis ANSES, directive 2020/2184). Chaque seuil est saisi à la main, sourcé et daté.

### 4.2 Les trois tables du socle

1. **`mesures`** — les faits bruts. Une ligne = un paramètre mesuré sur un prélèvement. Champs clés issus de Hub'Eau : commune (code INSEE), UDI/distributeur, ressource amont, date, `code_parametre`, `libelle_parametre`, `resultat_numerique`, unité, et les champs de conformité tels que fournis. On stocke **la mesure, pas seulement le verdict**.
2. **`referentiel_seuils`** — la grille réglementaire datée. Une ligne = (paramètre, seuil, statut « limite » ou « vigilance », date d'entrée en vigueur, date de fin, source légale, lien). C'est le moteur du réétalonnage.
3. **`reetalonnage`** — la table calculée. Pour chaque mesure : verdict-2016 vs verdict-2026, et un drapeau « bascule » quand ils diffèrent. C'est ce qui alimente les cartes, les stats et le site.

### 4.3 Principes de rigueur intégrés dès le schéma

- **Traçabilité totale** : chaque mesure garde son URL d'appel Hub'Eau ; chaque seuil garde sa référence légale. Un tiers peut tout revérifier.
- **`0 = < seuil de quantification`** : jamais interprété comme « zéro absolu ». On conserve, quand disponible, la limite de quantification du labo (enjeu majeur pour les PFAS : « <0,044 » peut masquer 44 ng/L).
- **Un prélèvement = un point espace-temps** : on horodate tout et on vise, à terme, des tendances (plusieurs prélèvements par UDI) plutôt que des instantanés.
- **Idempotence** : réinterroger la même commune ne crée pas de doublons (clé = commune + date + paramètre).

### 4.4 « Chaque recherche alimente la base »

Le flux voulu est : *lancer une recherche → les résultats sont ingérés dans `mesures` → le réétalonnage se recalcule → le site se met à jour.* On l'implémente d'abord de façon simple (scripts + fichiers/base légère type SQLite ou DuckDB), puis on industrialise seulement quand le volume et le financement le justifient. **On ne sur-construit rien au départ.**

---

## 5. Feuille de route par phases (chaque phase = un livrable finançable)

Logique voulue : **commencer petit, prouver, montrer, lever, étendre.** Chaque phase se suffit à elle-même et rend le projet plus « montrable » pour la suivante.

### Phase 0 — Fondations (immédiat, coût quasi nul)

*Objectif :* poser le socle intellectuel et technique.
*Livrables :*
- Le **référentiel de seuils daté** v1 (les paramètres des preuves de concept ci-dessus, sourcés).
- Le **schéma de base de données** et la méthode de réétalonnage figés et documentés.
- Ce document de cadrage + une page « manifeste » (le principe mesure ≠ verdict).

*Ce que ça débloque :* un discours clair et une méthode reproductible — le minimum pour convaincre un premier soutien.

### Phase 1 — Pilote « chlorothalonil R471811 » (petit périmètre)

*Objectif :* démontrer le réétalonnage sur un cas réel, sur **1 à 3 départements** de grande culture (ex. Eure-et-Loir, Marne, ou un département proche de vous).
*Livrables :*
- Extraction Hub'Eau du R471811 sur le périmètre → ingestion en base.
- Liste chiffrée des communes/UDI **« potabilisées par reclassement »** (mesures entre 0,1 et 0,9 µg/L) + population concernée.
- Une **première carte** et une note de résultats.

*Ce que ça débloque :* la preuve tangible « voici X communes et Y habitants dont l'eau a changé de statut sans changer de composition ». C'est LE livrable qui rend le projet finançable.

### Phase 2 — Élargissement maîtrisé

*Objectif :* étendre sans casser la méthode.
- Ajouter des paramètres (métolachlore ESA et autres métabolites ; métaux relevés : antimoine, sélénium, bore).
- Étendre à une région entière.
- Première version publique consultable (même rudimentaire).

### Phase 3 — Montée en charge nationale + site open data

*Objectif :* le balayage national par lots (délégué à des traitements automatisés), un **site public** avec cartes, filtres, exports, et la **base ouverte** téléchargeable + auto-alimentée à chaque nouvelle recherche.
*Prérequis :* financement acquis (hébergement, éventuel temps de développement).

### Phase 4 — Pérennisation & communauté

*Objectif :* gouvernance (association ?), licence de données claire, contributions extérieures, mises à jour régulières au rythme des nouveaux bulletins et des évolutions réglementaires. Le projet devient un commun.

---

## 6. Volet open data & diffusion

- **Licence** : données sous licence ouverte (ex. **ODbL** ou **Etalab / Licence Ouverte**, cohérentes avec l'origine publique des données) ; code sous licence libre (MIT/GPL) ; textes sous **Creative Commons**. À arbitrer, mais l'esprit est : **réutilisable par quiconque**.
- **Reproductibilité** : publication des scripts d'extraction, du référentiel de seuils et de la méthode, pour que n'importe qui puisse refaire les calculs.
- **Formats** : exports CSV/JSON, cartes, et à terme une petite API ou des jeux de données téléchargeables.
- **Hébergement du code** : dépôt public (type GitLab/GitHub) dès la phase 0 — c'est aussi une vitrine pour les financeurs.

---

## 7. Gouvernance, éthique et lignes rouges

- **Ne rien inventer** : tout chiffre vient de l'API ; tout seuil vient d'un texte. Pas d'extrapolation non signalée.
- **Interroger la norme, pas accuser les acteurs** : la cible est la **règle** (le seuil, le reclassement), pas les distributeurs ni les élus locaux, qui appliquent la réglementation en vigueur. Cette posture protège juridiquement le projet et le garde crédible.
- **Nuance systématique** : rappeler les durcissements réels (PFAS) à côté des assouplissements. Un projet honnête est un projet inattaquable.
- **Limites assumées et affichées** : un bulletin = un point espace-temps ; « conforme » ≠ « sain » ; « 0 » = sous seuil de quantification.
- **Protection des personnes** : on parle de communes/UDI (données publiques), jamais d'individus.

---

## 8. Financement (pistes à explorer)

Le format « open data citoyen, incrémental, scalable » correspond à plusieurs guichets français. À vérifier au cas par cas (je peux faire cette recherche pour vous) :

- **Financement participatif** (Ulule, HelloAsso si structure associative) — cohérent avec la démarche citoyenne et utile pour la première traction.
- **Fondations environnementales et de l'eau** (ex. fondations dédiées à la nature/l'environnement) et **mécénat**.
- **Appels à projets** : agences de l'eau, ADEME, régions/collectivités, programmes « données ouvertes » / « sciences citoyennes ».
- **Partenariats** avec des ONG déjà positionnées sur les pesticides et l'eau (crédibilité + audience), en gardant l'indépendance éditoriale.

**Argument de levée :** un livrable de Phase 1 chiffré (« X communes, Y habitants, une carte ») vaut mieux que n'importe quel discours. La stratégie de financement suit la stratégie de preuve : on lève **après** avoir montré, pas avant.

---

## 9. Risques et parades

- *Volume/coût de données* → on reste sur des périmètres restreints tant que le financement ne suit pas ; l'architecture est prévue pour absorber le national sans refonte.
- *Contraintes techniques de l'API* (longueur d'URL, grosses réponses, pagination) → déjà documentées dans la note de méthode ; on délègue les gros balayages à des traitements dédiés.
- *Complexité réglementaire* (seuils, dates, statuts limite/vigilance) → c'est justement la valeur ajoutée du projet ; on l'encapsule une fois pour toutes dans le `referentiel_seuils`.
- *Perception « militante »* → neutralisée par la rigueur, la nuance et la traçabilité.

---

## 10. Prochaines étapes immédiates (ce que je peux faire tout de suite)

1. **Bâtir le référentiel de seuils daté v1** (chlorothalonil R471811, métaux de la directive, PFAS) — sourcé, prêt à servir de moteur.
2. **Confirmer les dates et statuts** des reclassements de métabolites (chlorothalonil confirmé avril 2024 ; métolachlore ESA à préciser).
3. **Choisir le département pilote** et lancer la première extraction Hub'Eau du R471811 pour produire la première liste chiffrée + carte.
4. **Poser le squelette de la base** (les 3 tables) sous une forme légère et ouverte.

Dites-moi par où vous voulez commencer, et on attaque la Phase 0.

---

### Sources réglementaires

- ANSES, reclassement du métabolite R471811 du chlorothalonil (avril 2024) — [La France Agricole](https://www.lafranceagricole.fr/phytosanitaire/article/867624/l-anses-classe-un-metabolite-du-chlorothalonil-non-pertinent-pour-l-eau) ; [Générations Futures](https://www.generations-futures.fr/actualites/alerte-metabolite-chlorothalonil/) ; [synthèse chiffrée 0,1→0,9 µg/L, 34 %](https://environnementsantepolitique.fr/2024/05/27/lanses-vient-de-passer-de-01-a-09-%C2%B5g-l-le-seuil-dans-leau-potable-pour-un-metabolite-du-chlorothalonil-34-des-echantillons-des-eaux-potables-depassaient-la-limite-de-01-%C2%B5g-l/)
- Arrêté du 30 décembre 2022 modifiant l'arrêté du 11 janvier 2007 (transposition directive 2020/2184) — [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000046849403) ; [analyse Phytocontrol](https://www.phytocontrol.com/veille-reglementaire/transposition-de-la-directive-eau-potable-en-droit-francais-nouvel-arrete-limites-et-references-de-qualite/)
- Directive (UE) 2020/2184 — [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000045770552)
- Arrêté du 11 janvier 2007 (référentiel historique) — [Légifrance](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000465574/)
- Données : API Hub'Eau « Qualité de l'eau potable » (base SISE-Eaux) — `https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/`

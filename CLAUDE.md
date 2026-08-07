# CLAUDE.md — Observatoire de la potabilité réglementaire

Ce fichier est lu automatiquement par Claude Code au début de chaque session.
Il contient la méthode, les règles et les garde-fous du projet. **Ne pas les
contourner sans instruction explicite de Yannick.**

---

## 1. Ce qu'est ce projet

L'**Observatoire de la potabilité réglementaire** est un projet citoyen
d'exploitation de données ouvertes. Il est porté par Éditions Mytae
(Yannick Mytae) et il est **distinct du livre** : ce dépôt ne produit pas
de texte d'auteur, il produit une base de données, des vérifications et
des fiches reproductibles.

### La thèse fondatrice : le réétalonnage réglementaire daté

Le projet sépare **la mesure** du **verdict**.

Une mesure est un fait physique : *0,092 µg/L d'ESA métolachlore, le
14 mars 2025, à Saintes*. Ce fait ne change pas.

Le verdict est une convention administrative : *« conforme »*. Cette
convention change dans le temps. La même eau, avec la même mesure, peut
être « non conforme » en 2016 et « conforme » en 2026 — non parce que
l'eau s'est améliorée, mais parce que le seuil s'est déplacé.

**L'objet du projet est de rendre ce déplacement visible et vérifiable.**

Chaque mesure est donc notée trois fois :

| Grille | Question posée |
|---|---|
| `seuil_2016` | Cette eau aurait-elle été potable selon la norme d'il y a dix ans ? |
| `seuil_2026` | Est-elle potable selon la norme en vigueur aujourd'hui ? |
| `seuil_strict` | Serait-elle potable selon la norme la plus protectrice au monde ? |

L'indicateur central est la **bascule** (`bascule_2016_2026`) : une mesure
qui dépassait la limite de 2016 et qui ne dépasse pas celle de 2026. Un
bulletin déclaré conforme et comportant des bascules est la démonstration
matérielle de la thèse.

### La formule de référence

> Ce n'est pas l'eau qui est devenue potable. C'est la limite qui a bougé.

---

## 2. Garde-fous — à respecter sans exception

Ces règles ont été posées par Yannick. Elles ne sont pas négociables et
elles ne se déduisent pas du code : elles doivent être appliquées dans
chaque analyse, chaque texte, chaque fiche produite.

### 2.1 Interroger la norme, pas accuser les acteurs

Le sujet est **la construction réglementaire du seuil**. Ce n'est ni l'ARS,
ni le distributeur, ni le maire, ni l'agriculteur. Un exploitant qui
respecte une limite fixée par arrêté n'est pas en faute : c'est la limite
qu'on examine.

Formulation correcte : « cette eau est conforme à une limite qui a été
relevée de 0,1 à 0,9 µg/L en 2020 ».
Formulation interdite : « cette eau est polluée et on vous le cache ».

### 2.2 C'est un outil de conscience, pas un outil de prescription

Citation de Yannick, à conserver telle quelle :

> « non, ce n'est pas le propos. ici c'est un outils de conscience. »

**Aucune recommandation de filtration, d'osmoseur, de charbon actif,
d'eau embouteillée, ni d'aucun équipement ou produit, jamais.** Pas même
en note de bas de page, pas même en « pour information ». Toute suggestion
d'équipement transforme un travail de vérification en argumentaire
commercial et détruit la crédibilité du projet.

Si un utilisateur demande quoi faire de son eau, la réponse est de
l'orienter vers l'information publique (ARS, mairie, données Orobnat), pas
vers un produit.

### 2.3 Ne travailler que sur les bulletins complets

Citation de Yannick, à conserver telle quelle :

> « il ne faut travailler que sur les analyses qui intègrent tous les
> indicateurs… Si on ne travaille pas sur les analyses complètes on arrive
> toujours à la conclusion que tout est ok. »

C'est **la règle méthodologique la plus importante du projet**.

Le contrôle sanitaire produit deux types très différents de prélèvements :

- des analyses **de routine** (~20 à 30 paramètres : bactériologie, pH,
  conductivité, nitrates, chlore) — très nombreuses ;
- des analyses **complètes** (300 à 400 paramètres : pesticides,
  métabolites, PFAS, métaux, solvants) — rares, une à deux par an et par
  unité de distribution, parfois moins.

Mélanger les deux produit mécaniquement un résultat rassurant : les
milliers de mesures de routine, toutes conformes, noient les rares
mesures qui portent l'information. **La moyenne d'un corpus dominé par
la routine dit toujours « tout va bien ».**

Constante : `SEUIL_COMPLET = 250`. Un prélèvement est retenu comme complet
si `nb_parametres > 250`.

Corollaire : **ne jamais composer un profil synthétique** en prenant, pour
chaque paramètre, la dernière valeur connue sur douze mois. Cet objet
n'existe pas, n'a pas de date, et n'est pas réétalonnable — il ne peut pas
être noté contre une grille datée, ce qui détruit la thèse du projet.
Une analyse porte sur **un prélèvement, à une date, dans son intégralité**.

**L'unité est le `code_prelevement`, jamais la date.** Erreur réellement
commise ici et corrigée le 7 août 2026 : le code regroupait les mesures par
commune et par date. Or une commune a souvent plusieurs prélèvements le même
jour, sur des points d'eau différents — à Saintes, 27 dates sur 54. Le
regroupement par date fusionnait l'analyse complète d'un point avec l'analyse
de routine d'un autre, gonflait `nb_parametres`, et pour les paramètres
communs (pH, chlore, nitrates) retenait la valeur du premier enregistrement
rencontré, c'est-à-dire potentiellement celle de l'autre point. `ingest.py`
refuse désormais un lot portant plusieurs `code_prelevement`
(`BulletinHeterogene`).

**Le point d'eau est l'installation de production amont**
(`code_installation_amont`). Une commune alimentée par trois installations
donne trois bulletins, analysés séparément. C'est aussi ce qui permettra de
voir si un mélange conforme masque une ressource qui ne l'est pas — cf. §7bis.

### 2.4 Zéro n'est pas zéro

Dans les données SISE-Eaux, une valeur affichée `0` ou `< 0,01` signifie
**« inférieur au seuil de quantification du laboratoire »**, pas
« absent ». C'est une limite de l'instrument, pas une propriété de l'eau.

Conséquences dans le modèle de données :

- `resultat_num` : la valeur **seulement si elle est quantifiée** ;
- `lq` : la limite de quantification quand la valeur ne l'est pas ;
- `est_quantifie` : booléen.

Un dépassement ne peut être affirmé que si `est_quantifie = TRUE`.

Il existe donc **trois états de verdict**, pas deux :

1. conforme (quantifié, sous le seuil) ;
2. dépassement (quantifié, au-dessus du seuil) ;
3. **indéterminé** — la LQ du laboratoire est supérieure au seuil de
   comparaison. C'est le cas fréquent pour les seuils stricts (Danemark
   2 ng/L pour les PFAS, LQ courante 4 ng/L) : on ne peut pas dire que
   l'eau respecte le seuil, on peut seulement dire qu'on ne sait pas.

Ne jamais présenter un « indéterminé » comme un « conforme ». C'est
l'erreur la plus facile à commettre et la plus dommageable.

### 2.5 Un seuil sans sa date d'applicabilité est faux

Leçon apprise en corrigeant une erreur réelle de ce projet : la directive
UE 2020/2184, transposée par l'arrêté du 30 décembre 2022, comporte des
**valeurs à application différée**.

- **Plomb** : 10 µg/L aujourd'hui ; 5 µg/L à compter du **1er janvier 2036**.
- **Chrome total** : 50 µg/L aujourd'hui ; 25 µg/L à compter du
  **1er janvier 2036**.

Une base qui inscrit 5 µg/L comme seuil 2026 pour le plomb produit de
faux dépassements. Le référentiel comporte donc quatre colonnes liées :
`seuil_2026`, `seuil_futur`, `date_applicabilite_futur`, et le
`statut_2026`.

Règle générale : **toute valeur de seuil doit être accompagnée de la date
à laquelle elle s'applique effectivement.** Quand une source annonce un
durcissement, vérifier systématiquement s'il est immédiat ou différé.

### 2.6 Distinguer statut réglementaire et statut scientifique

Deux colonnes distinctes, jamais fusionnées : `pe_reglementaire` et
`pe_scientifique`.

Un perturbateur endocrinien reconnu par la littérature scientifique n'est
pas nécessairement reconnu comme tel par la réglementation. **Dans l'eau
destinée à la consommation humaine, le seul PE avéré au sens réglementaire
UE est le bisphénol A** (limite 2,5 µg/L depuis 2023). Écrire qu'un
pesticide « est un perturbateur endocrinien » sans préciser le registre
est une faute vérifiable qui décrédibilise l'ensemble.

### 2.7 Toute affirmation chiffrée est sourcée ou marquée

Chaque ligne du référentiel porte une colonne `sources` (codes du fichier
`docs/INDEX_SOURCES.md`) et une colonne `fiabilite` :

- `verifie` : valeur lue dans un texte réglementaire ou une source primaire
  identifiée ;
- `a_verifier` : valeur plausible mais non confirmée sur source primaire —
  **doit être signalée comme telle dans toute sortie publique**.

Ne jamais « arrondir » un `a_verifier` en `verifie` par confort. Le projet
tire sa force de sa vérifiabilité, pas de son volume.

### 2.8 Une conformité sans son dénominateur est une demi-vérité

Un bulletin complet porte 350 à 400 paramètres ; le référentiel saisi à la
main en décrit 55. Tant que les 300 pesticides nommés (Boscalid, Quinmérac,
Imazamox…) n'étaient rattachés à rien, la base annonçait « aucun
dépassement » après n'avoir lu qu'un dixième de l'analyse. C'est le travers
du §2.3, transposé du bulletin au paramètre.

Trois mécanismes le corrigent, et ils ne se confondent pas :

| Source du seuil | Ce qu'elle apporte | Ce qu'elle n'apporte PAS |
|---|---|---|
| `referentiel_seuils.csv` | 2016, 2026, strict, différé, sources, fiabilité | — |
| `regles_famille.csv` | rattache par la limite déclarée les substances d'une même famille à une ligne du référentiel | rien d'automatique : la règle est écrite, sourcée, et son effet est auditable |
| `limite_qualite_parametre` (source) | la grille **d'aujourd'hui** uniquement | 2016, seuil strict, seuil différé |

**Une limite seulement déclarée ne peut jamais produire une bascule ni un
verdict 2016.** On ne fabrique pas de passé réglementaire à partir de la
grille du jour. Quand le référentiel et la source se contredisent, le
référentiel daté du projet prime, et l'écart est signalé
(`v_ecarts_referentiel_source`) : chaque ligne est soit une erreur de notre
référentiel, soit un écart réel entre le texte et la pratique déclarée.

Toute sortie publique affiche le dénominateur : « 323 paramètres notés sur
383 ». `pct_couverture` est porté par `v_prelevement_verdict`.

### 2.9 Un seuil et une mesure dans deux unités différentes ne se comparent pas

Erreur réellement présente et détectée par le contrôle croisé : le chlorate
était au référentiel en 0,25 mg/L et mesuré en µg/L. La comparaison directe
se trompait d'un facteur 1000.

Les seuils sont désormais convertis vers l'unité de la mesure avant toute
comparaison. Quand les deux unités sont connues, différentes et non
convertibles, **aucun verdict n'est produit** — la mesure est listée dans
`v_unites_incomparables`. Un verdict faux est pire qu'un verdict absent.

---

## 3. Contraintes d'environnement

### 3.1 Accès réseau

Instruction de Yannick, à conserver telle quelle :

> « Interroger l'API **uniquement** via l'outil web. **Ne pas** utiliser
> curl/wget/python pour télécharger une URL. Le **traitement** de fichiers
> déjà sauvegardés localement (grep/jq/Read) est en revanche permis. »

Cette contrainte vient de l'environnement Cowork (sandbox sans accès
réseau sortant depuis le shell). **En Claude Code sur la machine de
Yannick, le réseau est disponible depuis le shell** : `src/fetch_hubeau.py`
et `src/fetch_departement.py` sont écrits pour être exécutés là, avec
`requests`. C'est le passage à Claude Code qui débloque la collecte
automatique à grande échelle.

Si une session tourne à nouveau dans un environnement sans réseau, la
règle ci-dessus redevient active.

### 3.2 Étiquette envers Hub'Eau

L'API Hub'Eau est un service public gratuit et sans clé. Le projet ne doit
jamais se comporter comme une charge abusive :

- pagination à `size=5000` (maximum accepté) ;
- `time.sleep(0.3)` minimum entre deux appels ;
- reprise sur incident via un journal, pour ne jamais retélécharger ce qui
  a déjà été obtenu ;
- un `User-Agent` identifiant le projet.

Un département = quelques centaines de communes = plusieurs milliers
d'appels. Le respect du débit n'est pas optionnel.

---

## 4. Modèle de données

DuckDB, schéma en étoile. Fichier `data/eau.duckdb` (non versionné).

```
communes            code_insee (PK), nom, code_departement, codes_postaux, lon, lat
prelevements        code_prelevement (PK, celui de la source), code_insee,
                    code_installation_amont, nom_installation_amont,
                    nom_distributeur, nom_uge, codes_reseaux, noms_reseaux,
                    code_lieu_analyse, date_prelevement, nb_parametres,
                    est_complet, conclusion_conformite, conf_limites_bact,
                    conf_limites_pc, conf_references_pc, source_url
mesures             code_prelevement, code_parametre, code_cas,
                    libelle_parametre, libelle_norm, resultat_num,
                    resultat_alpha, lq, est_quantifie, unite, unite_norm,
                    limite_brute, limite_declaree, reference_brute,
                    reference_declaree
referentiel_seuils  chargé depuis referentiel/referentiel_seuils.csv
alias_parametres    alias_norm -> libelle_norm
regles_famille      chargé depuis referentiel/regles_famille.csv
unites_masse        facteurs de conversion g/L, mg/L, µg/L, ng/L

analyses_figees     (code_prelevement, version_referentiel) : le résultat figé
verdicts_figes      (code_prelevement, version_referentiel, libelle) : le détail
couverture_communes (code_insee, version_referentiel) : analysee /
                    rattachee_reseau / non_documentee — ce que colorie la carte
```

Vues :

- `v_mesures_ref` — résolution du rapprochement mesure ↔ référentiel
  (par `code_parametre`, sinon par libellé normalisé, sinon par alias) ;
- `v_mesures_verdict` — les trois notations et la bascule ;
- `v_prelevement_verdict` — agrégat par prélèvement ;
- `v_parametres_non_apparies` — **diagnostic indispensable au passage à
  l'échelle** : les mesures qui n'ont AUCUN seuil de comparaison, ni par le
  référentiel ni par la limite déclarée. Un tel paramètre est invisible pour
  l'analyse : il existe en base et ne pèse sur aucun verdict ;
- `v_regle_famille_appliquee` — ce que la règle de famille a rattaché
  automatiquement, à relire : une substance qui n'est pas un pesticide et
  qui porte la même limite y figurerait à tort ;
- `v_ecarts_referentiel_source` — là où notre seuil 2026 contredit la limite
  déclarée par l'administration ;
- `v_unites_incomparables` — mesures dont l'unité ne peut pas être ramenée à
  celle du seuil : aucun verdict n'est produit.

### La sortie est figée, mais toujours estampillée

La mesure ne change jamais : c'est un fait. Le verdict, lui, dépend du
référentiel — et le sujet du projet est que les seuils bougent. Figer un
« conforme » sans dire contre quelle grille il a été calculé reproduirait, à
l'intérieur de l'outil, le défaut que l'outil dénonce.

Chaque ligne figée porte donc `version_referentiel` — empreinte du CONTENU des
fichiers du référentiel, pas un commit git : une modification non commitée doit
rester identifiable — et `calcule_le`. Refiger après modification produit une
nouvelle version ; les deux coexistent, et leur comparaison est la trace du
déplacement.

### Le référentiel est un fichier versionné, pas du code

`referentiel/referentiel_seuils.csv` (séparateur `;`, décimale `.`) est la
**source de vérité** des seuils. Il est lu par `build_db.py` ; il n'est
jamais recopié en dur dans un script Python.

Raison : le sujet du projet est la dérive des seuils dans le temps. Git
donne donc gratuitement ce qui manque partout ailleurs — un **journal daté
et attribué de chaque modification de seuil**. Tout changement de valeur
doit faire l'objet d'un commit dont le message dit *quelle* valeur change,
*de quoi à quoi*, et *sur quelle source*.

Ne jamais modifier un seuil sans mettre à jour `sources` et `fiabilite`
dans la même ligne.

---

## 5. Nomenclature

Sources documentaires : `FAMILLE-NN` (`REG-03`, `PFAS-05`, `MET-01`,
`MIX-08`, `PE-04`). Répertoriées dans `docs/INDEX_SOURCES.md`.

Fichiers de source : `CODE_Organisme_description_annee.ext`
(ex. `REG-03_UE_directive-2020-2184_2020.pdf`).

Quand une ligne du référentiel s'appuie sur plusieurs sources, les codes sont
séparés par une **barre verticale** : `REG-01|REG-03`. Ne jamais utiliser le
point-virgule à l'intérieur d'une cellule : c'est le séparateur de colonnes du
CSV, et il décale silencieusement toute la ligne (erreur réellement commise et
corrigée ici — elle avait déplacé `fiabilite` sur 14 lignes).

---

## 6. Circuit de travail

```
1. build      src/build_db.py                             → schéma + référentiel
2. fetch      src/fetch_hubeau.py 31520                    → une commune (code postal ou INSEE)
   ou         src/fetch_departement.py --dept 17           → un département entier
3. contrôle   v_parametres_non_apparies, pct_couverture    → couverture réelle
4. figer      src/figer.py                                → sortie estampillée
5. analyse    src/queries.sql                             → requêtes de thèse
6. fiche      sortie/build_fiche.py                       → fiche citoyenne

Le raccourci qui fait tout l'enchaînement pour une commune :

```
python3 src/observer.py 31520
```

Entretien du catalogue des paramètres (rare, quand de nouveaux libellés
apparaissent) :

```
python3 src/catalogue_parametres.py --depts 17,31,28,51 --communes 8 --depuis 2023
```
```

Test de non-régression, sans réseau, à lancer après toute modification de
`common.py`, `ingest.py` ou des vues :

```
python3 tests/test_verdict.py
python3 tests/test_figer.py
```

Il fabrique un bulletin complet fictif et vérifie que les règles §2.3 à §2.5
sont effectivement appliquées par les vues : bascule détectée, seuil différé
non compté comme dépassement actuel, non-quantifié traité en indéterminé,
appariement par code / libellé / alias fonctionnel. Si un contrôle échoue,
c'est une règle de méthode qui a cessé de s'appliquer — pas un détail
technique.

La collecte est **idempotente** : réingérer un prélèvement déjà présent le
remplace (DELETE puis INSERT sur `code_prelevement`), il ne se duplique
pas. On peut relancer une collecte interrompue sans précaution.

### La requête qui porte la thèse

```sql
SELECT commune, dept, date_prelevement, nb_bascules
FROM v_prelevement_verdict
WHERE est_complet AND nb_depasse_2026 = 0 AND nb_bascules > 0
ORDER BY nb_bascules DESC;
```

Traduction : *des bulletins complets, déclarés parfaitement conformes
aujourd'hui, qui ne l'auraient pas été il y a dix ans.* Chaque ligne
retournée est un cas.

---

## 7. Effet cocktail — statut

**Méthode écrite** : `docs/METHODE_EFFET_COCKTAIL.md` (7 août 2026), qui
définit trois indicateurs du plus solide au plus fragile — dénombrement,
charge massique cumulée, indice de danger. **Implémenté** dans `src/figer.py`.

L'indice de danger reste ce qu'il y a de plus contestable dans le projet et
doit donc rester le plus encadré : jamais nommé « risque », jamais publié
sans le nombre de substances qui le composent, jamais présenté comme un
verdict de potabilité.

Un piège rencontré et corrigé : calculé sur TOUS les paramètres notés,
l'indice était dominé par le potassium, les chlorures, les sulfates et le
sodium — des minéraux comparés à des références organoleptiques — et passait
au-dessus de 1 sans qu'aucun micropolluant n'y soit pour rien. Il est
restreint aux substances de synthèse.

Reste à faire : les cadres de référence (MAF, CAG/MOET de l'EFSA,
EDC-MixRisk) sont cités dans la note de méthode mais **non implémentés**.
Tant qu'ils ne le sont pas, l'indice sert à classer des bulletins entre eux,
pas à estimer un risque.

Ordre de grandeur utile, à présenter comme un raisonnement et non comme
une mesure : cent pesticides chacun à 0,1 µg/L font 10 µg/L de charge
totale, soit 20 µg par jour pour deux litres — alors que chaque substance,
prise séparément, est « conforme ». La réglementation note substance par
substance ; le corps boit le mélange.

Ne pas publier de chiffre d'effet cocktail sans avoir écrit la méthode et
ses limites.

---

## 7bis. Dilution — deuxième axe, non implémenté

Décidé le 7 août 2026. Le réétalonnage n'est pas le seul mécanisme par lequel
une eau devient conforme sans être traitée. Si un réseau est alimenté par
trois captages et qu'un seul est très dégradé, le mélange peut respecter la
limite alors qu'aucune action n'a été menée sur la pollution. **La dilution
tient alors lieu de dépollution.** C'est un problème citoyen, et il est
invisible dans l'eau distribuée — puisque celle-ci EST le mélange.

Ce que les données permettent, vérifié :

| Maillon | Source | État |
|---|---|---|
| l'eau au robinet (le mélange) | `qualite_eau_potable/resultats_dis` | branché |
| les captages AEP et leur position | `prelevements/referentiel/points_prelevement` (BNPE) | disponible |
| la qualité de l'eau **brute** | `qualite_nappes` (clé `code_bss`), `qualite_rivieres` | disponible |
| **quel captage alimente quelle UDI** | — | **non exposé par Hub'Eau** |

Le dernier maillon manque. Substituts partiels : `code_installation_amont`
donne l'usine, et le champ `reseaux` donne le mélange entre réseaux avec un
débit en pourcentage. Le lien captage → usine ne peut être établi que par
inférence géographique, et devra donc être **affiché comme une hypothèse,
jamais comme un fait**.

---

## 8. Angles morts connus

À conserver visibles, ce sont les prochains chantiers :

- **radiologique** : tritium, radon, dose indicative totale — présents au
  référentiel, non travaillés analytiquement ;
- **eaux embouteillées** : aucun corpus, alors que les repères
  « nourrissons » utilisés comme `seuil_strict` en viennent ;
- **effet cocktail** : cf. §7 ;
- **couverture géographique** : le moteur et la collecte sont prêts pour le
  département ; aucun département n'a encore été collecté en entier ;
- **communes sans bulletin complet** : règle arrêtée le 7 août 2026 — on prend
  le bulletin de l'UDI qui alimente la commune même s'il a été prélevé
  ailleurs, en le mentionnant ; à défaut la commune sort en **« non
  documenté »**, catégorie visible à part entière, ni conforme ni non
  conforme. Non implémenté ;
- **cartographie** : les coordonnées et le statut de couverture sont en base
  (`couverture_communes`), la carte elle-même reste à faire ;
- **fiche citoyenne** : `sortie/build_fiche.py` ne lit PAS la base, il lit
  `data/communes_params.json`. À rebrancher sur `analyses_figees` et
  `verdicts_figes` ;
- **eau brute et dilution** : cf. §7bis.

---

## 9. Licence et posture

Données et référentiel sous **ODbL 1.0** (partage à l'identique, mention
de la source). Voir `LICENCE.md`.

Les données brutes proviennent d'Hub'Eau / SISE-Eaux (ministère chargé de
la santé), sous Licence Ouverte. Le travail propre au projet est le
référentiel daté, la méthode et le code.

Toute réutilisation par un tiers doit mentionner l'Observatoire **sans le
faire endosser** ses propres conclusions : la mention de source n'est pas
une caution.

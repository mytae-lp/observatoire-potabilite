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
communes            code_insee (PK), nom, code_departement
prelevements        code_prelevement (PK), code_insee, nom_installation,
                    nom_distributeur, date_prelevement, nb_parametres,
                    est_complet, conclusion_conformite, conf_limites_bact,
                    conf_limites_pc, conf_references_pc, source_url
mesures             code_prelevement, code_parametre, libelle_parametre,
                    libelle_norm, resultat_num, resultat_alpha, lq,
                    est_quantifie, unite, limite_qualite
referentiel_seuils  chargé depuis referentiel/referentiel_seuils.csv
alias_parametres    alias_norm -> libelle_norm
```

Vues :

- `v_mesures_ref` — résolution du rapprochement mesure ↔ référentiel
  (par `code_parametre`, sinon par libellé normalisé, sinon par alias) ;
- `v_mesures_verdict` — les trois notations et la bascule ;
- `v_prelevement_verdict` — agrégat par prélèvement ;
- `v_parametres_non_apparies` — **diagnostic indispensable au passage à
  l'échelle** : les mesures qu'aucune règle n'a rattachées au référentiel.
  À consulter après chaque collecte : un paramètre non apparié est une
  mesure invisible pour l'analyse.

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
2. fetch      src/fetch_departement.py --dept 17          → collecte
3. contrôle   v_parametres_non_apparies                   → couverture réelle
4. analyse    src/queries.sql                             → requêtes de thèse
5. fiche      sortie/build_fiche.py                       → fiche citoyenne
```

Test de non-régression, sans réseau, à lancer après toute modification de
`common.py`, `ingest.py` ou des vues :

```
python3 tests/test_verdict.py
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

Sujet identifié, **pas encore implémenté**. À traiter avec prudence : il
est méthodologiquement le plus contestable du projet, donc celui qui doit
être le plus rigoureux.

Piste retenue : indice de danger (`hazard index`), somme des rapports
`mesure / seuil`, alerte si > 1. Cadres de référence à documenter avant
tout calcul : MAF (facteur d'ajustement des mélanges), CAG/MOET de l'EFSA,
projet EDC-MixRisk.

Ordre de grandeur utile, à présenter comme un raisonnement et non comme
une mesure : cent pesticides chacun à 0,1 µg/L font 10 µg/L de charge
totale, soit 20 µg par jour pour deux litres — alors que chaque substance,
prise séparément, est « conforme ». La réglementation note substance par
substance ; le corps boit le mélange.

Ne pas publier de chiffre d'effet cocktail sans avoir écrit la méthode et
ses limites.

---

## 8. Angles morts connus

À conserver visibles, ce sont les prochains chantiers :

- **radiologique** : tritium, radon, dose indicative totale — présents au
  référentiel, non travaillés analytiquement ;
- **eaux embouteillées** : aucun corpus, alors que les repères
  « nourrissons » utilisés comme `seuil_strict` en viennent ;
- **effet cocktail** : cf. §7 ;
- **couverture géographique** : sept communes témoins seulement à ce jour ;
  le passage au département est l'objet immédiat du travail en Claude Code.

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

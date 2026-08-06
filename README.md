# Observatoire de la potabilité réglementaire

Projet citoyen d'exploitation de données ouvertes sur la qualité de l'eau du
robinet en France. Porté par Éditions Mytae.

> Ce n'est pas l'eau qui est devenue potable. C'est la limite qui a bougé.

## Ce que fait cet outil

Il sépare **la mesure** du **verdict**.

Une mesure est un fait : *0,092 µg/L d'ESA métolachlore, le 14 mars 2025, à
Saintes*. Un verdict est une convention administrative : *« conforme »*. Le
fait ne change pas ; la convention, si.

L'outil prend un bulletin d'analyse réel, complet, daté, et note chacune de
ses mesures **trois fois** :

| Grille | Question |
|---|---|
| 2016 | Cette eau aurait-elle été potable selon la norme d'il y a dix ans ? |
| 2026 | Est-elle potable selon la norme en vigueur ? |
| stricte | Serait-elle potable selon la norme la plus protectrice au monde ? |

L'indicateur central est la **bascule** : une mesure au-dessus de la limite
de 2016 et sous celle de 2026. Un bulletin déclaré conforme et comportant
des bascules est la démonstration matérielle du réétalonnage.

Ce n'est **pas** un outil de recommandation. Aucun conseil de filtration,
d'équipement ou de produit n'y figure ni n'y figurera. C'est un outil de
conscience : il interroge la norme, pas les acteurs qui l'appliquent.

## Démarrage

```bash
git clone <url>  &&  cd observatoire-potabilite
python3 -m venv .venv && source .venv/bin/activate     # Windows : .venv\Scripts\activate
pip install -r requirements.txt

python3 src/build_db.py                     # crée data/eau.duckdb + charge le référentiel
python3 src/fetch_departement.py --dept 17 --limite 5    # essai sur 5 communes
python3 src/fetch_departement.py --dept 17               # le département entier
python3 src/fetch_departement.py --dept 17 --rapport     # couverture, sans rien collecter
```

Puis l'analyse :

```bash
duckdb data/eau.duckdb
```
```sql
.read src/queries.sql
```

## Arborescence

```
CLAUDE.md                        méthode, règles et garde-fous — À LIRE D'ABORD
referentiel/
  referentiel_seuils.csv         source de vérité des seuils (versionnée)
  alias_parametres.csv           variantes d'écriture des libellés
src/
  common.py                      norm(), parse_val(), constantes de méthode
  build_db.py                    schéma DuckDB + chargement du référentiel + vues
  ingest.py                      ingestion d'un bulletin, idempotente
  fetch_departement.py           collecte à l'échelle d'un département
  fetch_hubeau.py                collecte pour une liste de communes
  queries.sql                    requêtes de référence, dont la requête de la thèse
tests/
  test_verdict.py                test de bout en bout, sans réseau
data/
  communes_params.json           tableaux de paramètres des communes témoins
  eau.duckdb                     base (non versionnée, reconstructible)
  journal/                       journaux de reprise par département
sortie/
  build_fiche.py                 génération d'une fiche citoyenne
  _template.html                 gabarit de fiche
docs/
  Plan_Projet_...md              plan d'ensemble du projet
  INDEX_SOURCES.md              index des sources (codes FAMILLE-NN)
  Note_Comparative_...md         analyse comparative d'un projet voisin
```

## Les quatre règles qui font la valeur de l'outil

Elles sont détaillées dans `CLAUDE.md`. En résumé :

**1. Seuls les bulletins complets comptent.** Le contrôle sanitaire produit
beaucoup d'analyses de routine (20 à 30 paramètres) et très peu d'analyses
complètes (300 à 400). Mélanger les deux noie l'information dans le volume
et conduit toujours à « tout va bien ». Constante : `SEUIL_COMPLET = 250`.

**2. Zéro n'est pas zéro.** Un `0` ou un `< 0,01` signifie « inférieur au
seuil de quantification du laboratoire », pas « absent ». D'où trois états
de verdict et non deux : conforme, dépassement, et **indéterminé** — quand
la limite de quantification est au-dessus du seuil de comparaison, on ne
sait pas, et il ne faut pas l'écrire « conforme ».

**3. Un seuil sans sa date d'applicabilité est faux.** La directive UE
2020/2184 comporte des valeurs différées : le plomb passe à 5 µg/L au
**1er janvier 2036**, le chrome total à 25 µg/L à la même date. Aujourd'hui,
les limites applicables sont 10 et 50 µg/L. D'où les colonnes `seuil_futur`
et `date_applicabilite_futur`.

**4. Chaque valeur porte sa source et son niveau de fiabilité.** Colonnes
`sources` et `fiabilite` (`verifie` / `a_verifier`) dans le référentiel. Une
valeur `a_verifier` doit être signalée comme telle dans toute sortie
publique.

## Le référentiel est un fichier, pas du code

`referentiel/referentiel_seuils.csv` est lu au moment du `build_db.py` ; les
seuils ne sont jamais écrits en dur dans un script. Le sujet du projet étant
la dérive des seuils dans le temps, git fournit ainsi gratuitement ce qui
manque partout ailleurs : **un journal daté et attribué de chaque
modification de seuil**.

Convention de commit pour un changement de seuil :

```
ref: antimoine seuil_2026 5 -> 10 µg/L (arrêté 30/12/2022, REG-03)
```

Un changement de valeur sans mise à jour de `sources` et `fiabilite` dans la
même ligne est un commit incomplet.

## Contrôles à faire après chaque collecte

```sql
SELECT * FROM v_parametres_non_apparies LIMIT 40;   -- mesures invisibles pour l'analyse
SELECT * FROM v_referentiel_jamais_mesure;          -- lignes du référentiel jamais rencontrées
```

Un paramètre mesuré mais non apparié au référentiel existe en base sans
peser sur aucun verdict. À l'échelle d'un département, c'est le premier
endroit où regarder : les libellés varient d'un laboratoire à l'autre, et
c'est à quoi servent le `code_parametre` Hub'Eau et la table d'alias.

## Test de non-régression

```bash
python3 tests/test_verdict.py
```

Sans réseau. Fabrique un bulletin complet fictif et vérifie que les règles
ci-dessus sont bien appliquées par les vues : bascule détectée, seuil différé
non compté comme dépassement actuel, non-quantifié traité en indéterminé,
appariement par code / libellé / alias fonctionnel, ingestion idempotente.
Un échec signale une règle de méthode qui a cessé de s'appliquer.

## État et prochains chantiers

Fait : schéma, référentiel daté à 55 paramètres, réétalonnage à trois
grilles, appariement par `code_parametre` avec repli libellé puis alias,
collecte départementale avec reprise, fiche citoyenne.

À faire : effet cocktail (méthode à écrire avant tout chiffre — indice de
danger, MAF, CAG/MOET de l'EFSA), volet radiologique, corpus des eaux
embouteillées, verrouillage des valeurs encore en `a_verifier`, extension
au-delà du premier département.

## Sources et licences

Données : Hub'Eau / SISE-Eaux (ministère chargé de la santé), Licence
Ouverte 2.0. Référentiel : ODbL 1.0. Code : MIT. Documents : CC BY-SA 4.0.
Détail et conditions d'attribution dans `LICENCE.md`.

Une réutilisation conforme aux licences n'engage pas l'Observatoire sur les
conclusions qu'en tire le réutilisateur.

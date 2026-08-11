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
python3 src/observer.py 31520               # TOUT l'enchaînement pour une commune
python3 src/observer.py --csv data/communes_a_collecter.csv   # un lot piloté par fichier
python3 src/fetch_hubeau.py 31520           # collecte seule, sans figer
python3 src/fetch_departement.py --dept 17 --limite 5    # essai sur 5 communes
python3 src/fetch_departement.py --dept 17               # le département entier
python3 src/fetch_departement.py --dept 17 --rapport     # couverture, sans rien collecter

# À l'échelle : collecter et ingérer sont deux gestes séparés, et seul le
# second prend le verrou de la base — quelques minutes au lieu de trois heures.
python3 src/moisson.py --depts 17,79,86 --tous   # réseau, en parallèle, base LIBRE
python3 src/moisson.py --etat                    # avancement de chaque département
python3 src/ingerer.py --etat                    # ce qui attend au tampon
python3 src/ingerer.py --depts 17,79,86          # verse le tampon, puis fige

python3 site/build_site.py                  # la vitrine publique dans site/public/
python3 sortie/build_fiche.py               # la fiche autonome, en un seul fichier
python3 atelier/atelier.py                  # le poste de pilotage local, 127.0.0.1:8760
```

Ou, plus simplement, tout depuis l'atelier : `python3 atelier/atelier.py`, puis
<http://127.0.0.1:8760>.

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
  referentiel_seuils.csv         source de vérité des seuils datés (versionnée)
  alias_parametres.csv           variantes d'écriture des libellés
  regles_famille.csv             rattachement par limite déclarée (les ~300 pesticides)
  catalogue_parametres_hubeau.csv  inventaire daté de ce qui est réellement mesuré
  geo/departements-simplifie.geojson  fond de carte (IGN/Etalab, Licence Ouverte)
src/
  common.py                      norm(), parse_val(), parse_limite(), unités, constantes
  hubeau.py                      accès réseau : communes, inventaire, bulletins
  build_db.py                    schéma DuckDB + chargement du référentiel + vues
  ingest.py                      ingestion d'un bulletin, idempotente
  observer.py                    point d'entrée : code postal -> analyse figée
  figer.py                       sortie estampillée (version + date) et sommes
  fetch_departement.py           collecte d'un département, base ouverte de bout en bout
  moisson.py                     collecte parallèle de plusieurs départements, SANS base
  ingerer.py                     cache brut -> base, sans réseau, puis figeage
  journal.py                     journal de reprise et cache d'énumération
  console.py                     trace atomique et étiquetée par fil
  fetch_hubeau.py                collecte pour des communes (INSEE ou code postal)
  catalogue_parametres.py        inventaire des paramètres réellement mesurés
  queries.sql                    requêtes de référence, dont la requête de la thèse
tests/
  test_verdict.py                moteur de réétalonnage, sans réseau
  test_figer.py                  sortie figée et couverture, sans réseau
data/
  communes_params.json           tableaux de paramètres des communes témoins
  communes_a_collecter.csv       liste de travail : code ; motif
  eau.duckdb                     base (non versionnée, reconstructible)
  journal/                       journaux de reprise par département
sortie/
  build_fiche.py                 fiche citoyenne, dérivée de la base
  redactions.json                les textes d'analyse, écrits à la main
  _template.html                 squelette de la fiche autonome
site/                            LA VITRINE — le seul objet publié
  build_site.py                  générateur du site statique
  gabarits/observatoire.css      le design, partagé avec la fiche autonome
  gabarits/corps_fiche.html      le corps de fiche, partagé lui aussi
  gabarits/fiche.js              rendu d'un bulletin (les trois états, la bascule)
  gabarits/recherche.js          recherche par code postal, dans le navigateur
  public/                        produit, non versionné : à déposer tel quel
atelier/                         LE POSTE DE PILOTAGE — ne se publie jamais
  atelier.py                     import CSV, collecte, contrôles, rédactions, publication
docs/
  REPRISE.md                     état du chantier et passage de main — À LIRE AU DÉBUT
  Plan_Projet_...md              plan d'ensemble du projet
  INDEX_SOURCES.md              index des sources (codes FAMILLE-NN)
  Note_Comparative_...md         analyse comparative d'un projet voisin
  METHODE_EFFET_COCKTAIL.md      les trois indicateurs de cumul et leurs limites
```

## Couverture

Un bulletin complet porte 350 à 400 paramètres ; le référentiel saisi à la main
en décrit 55. Trois mécanismes assurent que le reste est tout de même noté, sans
jamais se confondre :

| Source du seuil | Apporte | N'apporte pas |
|---|---|---|
| `referentiel_seuils.csv` | 2016, 2026, strict, différé, sources | — |
| `regles_famille.csv` | rattache par la limite déclarée les substances d'une même famille | rien d'implicite : la règle est écrite et auditable |
| limite déclarée par la source | la grille **d'aujourd'hui** | 2016, seuil strict, seuil différé |

**Une limite seulement déclarée ne peut jamais produire une bascule.** Mesuré
sur données réelles : 84 à 94 % des mesures d'un bulletin sont notées, contre
10 % auparavant. Chaque sortie affiche son dénominateur (`pct_couverture`).

## Les quatre règles qui font la valeur de l'outil

Elles sont détaillées dans `CLAUDE.md`. En résumé :

**1. Seuls les bulletins complets comptent.** Le contrôle sanitaire produit
beaucoup d'analyses de routine (20 à 30 paramètres) et très peu d'analyses
complètes (200 à 700). Mélanger les deux noie l'information dans le volume
et conduit toujours à « tout va bien ». Constante : `SEUIL_COMPLET = 200`,
fixée sur la distribution réelle — sur 964 prélèvements mesurés, la tranche
150-199 est totalement vide.

**1 bis. L'effort de recherche se déclare.** On ne trouve que ce qu'on
cherche. Une eau « correcte » sur 200 paramètres est une information plus
faible qu'une eau « moyenne » sur 700 : la première n'a pas été beaucoup
interrogée. Le nombre de paramètres recherchés n'est donc pas un indicateur
de qualité de l'eau mais de transparence, et toute comparaison entre communes
passe par des **taux** (`depassements_pour_mille`), jamais par des comptes
bruts. Voir `v_effort_recherche`.

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
SELECT * FROM v_parametres_non_apparies LIMIT 40;   -- mesures sans aucun seuil : invisibles
SELECT * FROM v_regle_famille_appliquee;            -- ce que la règle a rattaché : à relire
SELECT * FROM v_ecarts_referentiel_source;          -- notre seuil contre celui de la source
SELECT * FROM v_unites_incomparables;               -- unités non réconciliables : aucun verdict
SELECT * FROM v_referentiel_jamais_mesure;          -- lignes du référentiel jamais rencontrées
```

Un paramètre mesuré mais non apparié au référentiel existe en base sans
peser sur aucun verdict. À l'échelle d'un département, c'est le premier
endroit où regarder : les libellés varient d'un laboratoire à l'autre, et
c'est à quoi servent le `code_parametre` Hub'Eau et la table d'alias.

## Test de non-régression

```bash
python3 tests/test_verdict.py     # le moteur de réétalonnage
python3 tests/test_figer.py       # la sortie figée et la couverture
python3 tests/test_sorties.py     # ce qui est réellement publié
```

`test_sorties.py` contrôle la vitrine et la fiche construites : que la version
publiée soit bien celle du référentiel actuel, que chaque compteur de bulletin
soit d'accord avec son propre détail, qu'aucune commune documentée n'ait perdu
sa page, qu'aucune ressource distante ne soit appelée, et **qu'aucune prose
générée ne prescrive quoi que ce soit** (§2.2). Sur ce dernier point le
contrôle est volontairement asymétrique : bloquant pour la prose produite par
la machine, simple signalement pour celle de l'auteur — un outil qui censure
son auteur ne serait pas un garde-fou.

Sans réseau. Fabrique un bulletin complet fictif et vérifie que les règles
ci-dessus sont bien appliquées par les vues : bascule détectée, seuil différé
non compté comme dépassement actuel, non-quantifié traité en indéterminé,
appariement par code / libellé / alias fonctionnel, ingestion idempotente.
Un échec signale une règle de méthode qui a cessé de s'appliquer.

## État et prochains chantiers

Fait : schéma, référentiel daté à 55 paramètres, réétalonnage à trois
grilles, appariement par `code_parametre` avec repli libellé, alias puis règle
de famille, conversion d'unités, collecte par point d'eau (`code_prelevement`),
entrée par code postal, contrôle croisé contre la limite déclarée, collecte
départementale avec reprise, fiche citoyenne.

Fiche : `python3 sortie/build_fiche.py` construit la fiche depuis
`analyses_figees` et `verdicts_figes`. Le factuel est calculé et estampillé ;
la prose vient de `sortie/redactions.json` et n'est jamais générée — une
commune non rédigée donne une fiche factuelle qui l'indique.

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

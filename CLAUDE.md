# CLAUDE.md — Observatoire de la potabilité réglementaire

Ce fichier est lu automatiquement au début de chaque session. Il porte **la
thèse, les règles et les commandes** — le strict nécessaire pour travailler sans
erreur de méthode. **Ne rien contourner sans instruction explicite de Yannick.**

Il a été ramené de 1 239 à ~400 lignes le 8 août 2026. **Rien n'a été supprimé,
tout a été déplacé** : chaque règle ci-dessous garde son énoncé complet, et son
argumentaire — la citation qui la fonde, l'erreur réelle qui l'a fait écrire —
vit dans un document appelé à la demande. Motif : ce fichier était rechargé en
entier à chaque session, soit ~18 000 tokens payés avant le premier mot.
L'état exact d'avant est conservé tel quel dans
`docs/_CLAUDE-avant-degraissage-2026-08-08.md.bak` — il n'avait jamais été
commité, l'historique git ne le porte donc pas.

| Quand on a besoin de… | Lire |
|---|---|
| le raisonnement complet derrière un garde-fou, ses cas, ses citations | `docs/GARDE-FOUS.md` |
| pourquoi le dépôt est construit ainsi — atelier/vitrine, prose, indicateurs, figeage | `docs/ARCHITECTURE.md` |
| l'effet cocktail | `docs/METHODE_EFFET_COCKTAIL.md` |
| le mélange de réseaux et la dilution | `docs/METHODE_DILUTION.md` |
| l'état du chantier, ce qui est en cours | `docs/REPRISE.md` puis `docs/CHANTIERS.md` |
| une source documentaire | `docs/INDEX_SOURCES.md` |

Le **mode opératoire général** (modèles, délégation, traitement par lot, économie
de contexte) est dans `~/.claude/CLAUDE.md`, chargé automatiquement lui aussi.

---

## 1. Ce qu'est ce projet

L'**Observatoire de la potabilité réglementaire** est un projet citoyen
d'exploitation de données ouvertes, porté par Éditions Mytae (Yannick Mytae) et
**distinct du livre** : ce dépôt ne produit pas de texte d'auteur, il produit une
base de données, des vérifications et des fiches reproductibles.

### La thèse fondatrice : le réétalonnage réglementaire daté

Le projet sépare **la mesure** du **verdict**.

Une mesure est un fait physique : *0,092 µg/L d'ESA métolachlore, le
14 mars 2025, à Saintes*. Ce fait ne change pas.

Le verdict est une convention administrative : *« conforme »*. Cette convention
change dans le temps. La même eau, avec la même mesure, peut être « non
conforme » en 2016 et « conforme » en 2026 — non parce que l'eau s'est
améliorée, mais parce que le seuil s'est déplacé.

**L'objet du projet est de rendre ce déplacement visible et vérifiable.**

Chaque mesure est donc notée trois fois :

| Grille | Question posée |
|---|---|
| `seuil_2016` | Cette eau aurait-elle été potable selon la norme d'il y a dix ans ? |
| `seuil_2026` | Est-elle potable selon la norme en vigueur aujourd'hui ? |
| `seuil_strict` | Serait-elle potable selon la norme la plus protectrice identifiée ? |

L'indicateur central est la **bascule** (`bascule_2016_2026`) : une mesure qui
dépassait la limite de 2016 et qui ne dépasse pas celle de 2026. Un bulletin
déclaré conforme et comportant des bascules est la démonstration matérielle de
la thèse.

> Ce n'est pas l'eau qui est devenue potable. C'est la limite qui a bougé.

---

## 2. Garde-fous — à respecter sans exception

Ces règles ont été posées par Yannick. Elles ne sont pas négociables et elles ne
se déduisent pas du code : elles doivent être appliquées dans chaque analyse,
chaque texte, chaque fiche produite.

**Chaque énoncé ci-dessous est la règle entière.** Ce qui vit dans
`docs/GARDE-FOUS.md`, c'est ce qui la justifie : la citation de Yannick, l'erreur
réellement commise, le détail des colonnes. **En cas de doute sur un cas
concret, aller y lire** — ces garde-fous ont presque tous été écrits après une
erreur, et l'erreur y est décrite.

**2.1 — Interroger la norme, pas accuser les acteurs.** Le sujet est la
construction réglementaire du seuil, jamais l'ARS, le distributeur, le maire ou
l'agriculteur. « Cette eau est conforme à une limite relevée de 0,1 à 0,9 µg/L
en 2020 » : correct. « Cette eau est polluée et on vous le cache » : interdit.

**2.2 — C'est un outil de conscience, pas un outil de prescription.**
*« non, ce n'est pas le propos. ici c'est un outils de conscience. »*
**On n'oriente jamais vers un produit.** L'orientation par défaut reste
l'information publique : ARS, mairie, Orobnat, rapport annuel du service.

**Révisé le 9 août 2026**, sur instruction de Yannick. La rédaction précédente
interdisait aussi de *décrire* un procédé, et laissait donc le lecteur alerté
sans aucune prise — *« ton site il nous alerte, mais il peut créer une panique
car on ne sait pas quoi faire de ces informations »*. La frontière ne passe plus
entre « en parler » et « ne pas en parler », mais entre **un type et un
produit** :

- **permis** — décrire une **famille de procédés et ce qu'elle retient**, comme
  un fait de physico-chimie sourcé et daté. Cela vit dans une table versionnée,
  `referentiel/retention_procedes.csv`, jamais dans de la prose : une ligne par
  couple **procédé × famille de substance**, avec ses `sources` et sa
  `fiabilite`. Le §2.7 s'y applique entier — **la source doit couvrir CE couple
  précisément**, jamais par analogie de famille ;
- **interdit, nulle part, pas même en note** — une marque, un modèle, un
  fournisseur, un prix, un lien d'achat ; un conseil individuel (« pour votre
  eau, prenez… », « il faudrait filtrer ») ; l'eau embouteillée présentée comme
  une solution, le projet n'en ayant aucun corpus (§8) ; et toute description
  tournée en recommandation — impératif, conditionnel de conseil, classement de
  procédés par « efficacité » hors du couple qui lui donne son sens.

Argumentaire, cas et contre-exemples : `docs/GARDE-FOUS.md` §2.2.

**2.3 — Ne travailler que sur les bulletins complets.** *« il ne faut travailler
que sur les analyses qui intègrent tous les indicateurs… »* C'est la règle
méthodologique la plus importante du projet : les milliers d'analyses de routine
noient les rares analyses complètes qui portent l'information.
`SEUIL_COMPLET = 200` (`nb_parametres > 200`).
Corollaire : **jamais de profil synthétique** composé de dernières valeurs
connues — cet objet n'a pas de date et n'est pas réétalonnable.
**L'unité est le `code_prelevement`, jamais la date** : une commune a souvent
plusieurs prélèvements le même jour sur des points d'eau différents.
Le point d'eau est l'installation de production amont (`code_installation_amont`).

**2.4 — Zéro n'est pas zéro.** `0` ou `< 0,01` signifie « inférieur au seuil de
quantification du laboratoire », pas « absent ». Un dépassement ne s'affirme que
si `est_quantifie = TRUE`. **Trois états de verdict, pas deux** : conforme /
dépassement / **indéterminé** (la LQ du laboratoire est au-dessus du seuil de
comparaison). Ne jamais présenter un indéterminé comme un conforme.

**2.5 — Un seuil sans sa date d'applicabilité est faux.** Plomb : 10 µg/L
aujourd'hui, 5 µg/L au 1er janvier 2036. Chrome total : 50 puis 25 à la même
date. Colonnes `seuil_2026`, `seuil_futur`, `date_applicabilite_futur`,
`statut_2026`. Quand une source annonce un durcissement, **vérifier
systématiquement s'il est immédiat ou différé**.

**2.6 — Distinguer statut réglementaire et statut scientifique.**
`pe_reglementaire` et `pe_scientifique`, jamais fusionnées. **Dans l'eau
destinée à la consommation humaine, le seul PE avéré au sens réglementaire UE
est le bisphénol A** (2,5 µg/L depuis 2023). Voir aussi §2.15.

**2.7 — Toute affirmation chiffrée est sourcée ou marquée.** Colonnes `sources`
(codes de `docs/INDEX_SOURCES.md`) et `fiabilite` (`verifie` / `a_verifier`).
Un `a_verifier` est signalé comme tel dans toute sortie publique et ne
s'« arrondit » jamais en `verifie`. **La source doit couvrir CE paramètre
précisément** : une source qui porte sur la substance d'à côté n'est pas une
source, et une valeur étendue par analogie de famille est une valeur fausse
déguisée en valeur sourcée.

**2.8 — Une conformité sans son dénominateur est une demi-vérité.** Toute
sortie publique affiche « 323 paramètres notés sur 383 » (`pct_couverture`).
Trois sources de seuil qui ne se confondent pas : le référentiel daté,
`regles_famille.csv`, et la limite déclarée par la source. **Une limite
seulement déclarée ne produit jamais une bascule ni un verdict 2016** — on ne
fabrique pas de passé réglementaire à partir de la grille du jour. Les
contradictions sont listées dans `v_ecarts_referentiel_source`.
**Le dénominateur d'un agrégat peut changer sans que la mesure bouge — cf.
§2.13.**

**2.9 — Un seuil et une mesure dans deux unités différentes ne se comparent
pas.** Le chlorate était au référentiel en mg/L et mesuré en µg/L : facteur
1000. Les seuils sont convertis avant comparaison ; quand les unités sont
connues, différentes et non convertibles, **aucun verdict n'est produit**
(`v_unites_incomparables`). Un verdict faux est pire qu'un verdict absent.

**2.10 — Un verdict se rend à la date du prélèvement.** Un reclassement n'est
pas rétroactif : *« Il n'y a pas de rétroactivité possible »* (ARS 17,
10 juin 2024). D'où `date_applicabilite_2026` et, dans `v_mesures_verdict` :
`seuil_applicable` / `grille_applicable`, **`depasse_applicable`** (le seul
comparable à la conclusion de l'ARS), `depasse_2016` / `depasse_2026` (les deux
contrefactuels), `bascule_datee`. Les seuils sans date sont listés dans
`v_seuils_sans_date` et signalés à chaque `build_db.py`.

**2.11 — L'effort de recherche est un indicateur, et il se déclare.** On ne
trouve que ce qu'on cherche. Le nombre de paramètres recherchés n'est pas un
indicateur de qualité de l'eau : **une eau « correcte » sur 200 paramètres est
une information plus faible qu'une eau « moyenne » sur 700.** D'où
`classe_effort`, `depassements_pour_mille`, `v_effort_recherche`.
Deux règles de sortie : **aucune comparaison ni classement sans afficher
l'effort de chaque terme** ; et **une comparaison de territoire nomme la zone,
qui doit être une zone dont le corpus détient les bulletins** — le nom se prend
dans `nom_uge` et `dept`, il ne s'invente pas. Pas de « ailleurs », pas de « le
voisinage », pas de « plusieurs communes ». Contrôle n° 8 de
`tests/test_sorties.py` (il constate qu'une zone est nommée, pas qu'elle est la
bonne : cette relecture reste humaine).

**Troisième règle, ajoutée le 9 août 2026 — aucune série temporelle à panel
variable.** Comparer deux années sans se restreindre à **l'intersection des
paramètres recherchés les deux années** fait passer une baisse des recherches
pour une baisse des détections. Ce n'est pas le seuil qui bouge, c'est le
périmètre de mesure. Outillé : `v_panel_constant` et `v_serie_panel_constant`
(cherché sur ≥ 75 % des bulletins **chaque** année documentée du département).

Le Tarn le démontre, et impose trois précautions de formulation (chiffres et
contrôles : `docs/CHANTIERS.md`, chantier C2, qui fait foi — ne pas les
recompter ailleurs) :

- **la rupture est un fait, sa cause ne l'est pas.** 627 paramètres au
  19 décembre 2019, 344 au 6 janvier 2020 ; une seule vague, 298 retraits dont
  279 pesticides. L'instruction DGS/EA4/2020/177 [REG-05] décrit un mécanisme
  cohérent — liste régionale ciblée, figée par les marchés pluriannuels ARS —
  mais elle est **du 18 décembre 2020, onze mois APRÈS**. Écrire « rupture de
  janvier 2020, compatible avec un renouvellement de marché ; l'instruction va
  dans le même sens mais lui est postérieure », **jamais « causée par »**.
  Attribuer un effet à un texte qui le suit est l'erreur même des §2.5 et
  §2.10, transposée du seuil au programme d'analyse ;
- **ne jamais présenter ce retrait comme une perte d'information.** Sur les 298
  retirés : 6 quantifications pour 134 419 mesures avant 2020 (0,004 %), LQ
  médiane vingt fois plus fine que la limite. Le dire autrement serait un faux
  positif, et la donnée dit l'inverse ;
- **le sujet est la rotation, pas le rétrécissement.** 34 paramètres entrent
  entre 2019 et 2026, et ceux-là sont trouvés — chlorothalonil R471811 quantifié
  dans 19,1 % de ses mesures et 20 communes. Le R417888 entre en 2024, l'année
  de l'avis ANSES qui le classe pertinent : le programme suit la décision
  réglementaire. Et à panel constant, le Tarn est **plat sur onze ans**
  (16,1 à 19,2 ‰). Ce qui change n'est pas l'eau, c'est la liste de ce qu'on
  regarde. Corollaire §2.4 : d'une substance entrée en 2022, on ne sait **rien**
  d'avant — ni absence ni apparition, un indéterminé.

**Quatrième règle, ajoutée le 9 août 2026 — un département se compare à
lui-même.** Décision de Yannick. Le terme de comparaison par défaut d'un
bulletin est **son propre département**, jamais un autre. Rapprocher les 262 cas
de l'Eure-et-Loir des 100 du Tarn n'a pas de sens : panels différents,
couverture différente (90,1 % contre 93,7 %), et l'écart mesurerait d'abord
l'effort de recherche. À l'intérieur d'un département les bulletins relèvent du
même marché pluriannuel d'analyses de l'ARS, donc à peu près du même panel — la
comparaison redevient lisible. C'est la troisième règle appliquée à l'espace
plutôt qu'au temps. Une comparaison entre départements reste possible mais
cesse d'être le défaut : elle affiche l'effort et la couverture de **chaque**
terme, et se dit explicitement comme telle.

**2.12 — Le seuil de 2016 des métabolites est une extrapolation, et il se
dit.** Les 0,1 µg/L des 24 lignes « métabolite » viennent de l'instruction
DGS/EA4/2020/177 **de décembre 2020**. L'appliquer à un prélèvement de 2016 est
un raisonnement raisonnable, pas la lecture d'un texte de 2016 — le dire
partout où la grille 2016 est invoquée sur un métabolite.

**2.13 — Un seuil peut dépendre du procédé ou de la ressource, pas seulement de
la date.** Chlorates et chlorites (0,25 → 0,70 mg/L selon désinfection),
sélénium (20 → 30 µg/L) et bore (1,5 → 2,4 mg/L) par exception géologique.
Colonnes `seuil_conditionnel` et `condition_seuil`. **Rien dans les données ne
dit si la condition est remplie** : un dépassement n'est prononcé que si la
mesure franchit AUSSI la valeur la plus permissive ; entre les deux c'est
`indetermine_condition` (`v_verdicts_sous_condition`, à vérifier à la main avant
publication). Choix asymétrique assumé : **un faux positif coûte plus cher au
projet qu'un faux négatif.**

**Cinquième cas, ajouté le 10 août 2026 — la condition n'est ni le procédé ni
la ressource, c'est le statut de la substance.** Un reclassement de pertinence
déplace deux verdicts, et ils n'ont pas la même portée : la valeur propre du
métabolite, qui devient indicative et cesse d'être opposable, et le périmètre
du « total pesticides », limite de qualité **opposable** dont il sort le même
jour. **Une somme ne se compare jamais sans sa date et son périmètre.**
Détail et citations : `docs/GARDE-FOUS.md` §2.13 ; chiffres :
`data/dossiers/SUBSTANCE-chlorothalonil-r471811.md`.

**2.14 — « Le plus strict identifié », jamais « le plus strict au monde ».** Un
balayage mondial n'a été fait que pour les PFAS. Sur la somme des 20 PFAS,
personne n'est plus strict que l'UE (0,100 µg/L) ; la hiérarchie n'est réelle
que sur la somme des 4 (Danemark 2 ng/L, Suède 4, Allemagne 20 en 2028).

**2.15 — Trois registres, jamais fusionnés.** `pe_reglementaire` (UE),
`pe_scientifique` (littérature), `cancerogenicite_circ` (CIRC). L'atrazine :
classée 2A par le CIRC en novembre 2025, **aucun statut PE réglementaire**,
interdite depuis 2004 pour un motif d'eaux souterraines. Trois faits vrais,
trois registres, aucun ne se déduit des autres.

---

## 3. Contraintes d'environnement

### 3.1 Accès réseau

Instruction de Yannick, à conserver telle quelle :

> « Interroger l'API **uniquement** via l'outil web. **Ne pas** utiliser
> curl/wget/python pour télécharger une URL. Le **traitement** de fichiers
> déjà sauvegardés localement (grep/jq/Read) est en revanche permis. »

Cette contrainte vient de l'environnement Cowork (sandbox sans accès réseau
sortant depuis le shell). **En Claude Code sur la machine de Yannick, le réseau
est disponible depuis le shell** : `src/fetch_hubeau.py` et
`src/fetch_departement.py` sont écrits pour être exécutés là, avec `requests`.
Si une session tourne à nouveau dans un environnement sans réseau, la règle
ci-dessus redevient active.

### 3.2 Étiquette envers Hub'Eau

L'API Hub'Eau est un service public gratuit et sans clé. Le projet ne doit
jamais se comporter comme une charge abusive :

- pagination à `size=5000` (maximum accepté) ;
- `time.sleep(0.3)` minimum entre deux appels ;
- reprise sur incident via un journal, pour ne jamais retélécharger ce qui a
  déjà été obtenu ;
- un `User-Agent` identifiant le projet.

Un département = quelques centaines de communes = plusieurs milliers d'appels.
Le respect du débit n'est pas optionnel.

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
                    (dont date_applicabilite_2026 — cf. §2.10)
alias_parametres    alias_norm -> libelle_norm
regles_famille      chargé depuis referentiel/regles_famille.csv
unites_masse        facteurs de conversion g/L, mg/L, µg/L, ng/L

analyses_figees     (code_prelevement, version_referentiel) : le résultat figé
verdicts_figes      (code_prelevement, version_referentiel, libelle) : le détail
couverture_communes (code_insee, version_referentiel) : analysee /
                    rattachee_reseau / non_documentee — ce que colorie la carte
```

Vues :

- `v_mesures_ref` — rapprochement mesure ↔ référentiel (par `code_parametre`,
  sinon libellé normalisé, sinon alias) ;
- `v_mesures_verdict` — les trois notations et la bascule ;
- `v_prelevement_verdict` — agrégat par prélèvement ;
- `v_parametres_non_apparies` — **diagnostic indispensable au passage à
  l'échelle** : les mesures sans aucun seuil de comparaison. Un tel paramètre
  existe en base et ne pèse sur aucun verdict ;
- `v_regle_famille_appliquee` — ce que la règle de famille a rattaché
  automatiquement, **à relire** : une substance qui n'est pas un pesticide et
  qui porte la même limite y figurerait à tort ;
- `v_ecarts_referentiel_source` — là où notre seuil 2026 contredit la limite
  déclarée par l'administration ;
- `v_unites_incomparables` — mesures sans verdict possible (§2.9).

**Trois principes de construction**, détaillés dans `docs/ARCHITECTURE.md` :
la fiche sépare le factuel de la prose ; toute sortie figée porte
`version_referentiel` et `calcule_le` ; le référentiel est un CSV versionné,
jamais recopié en dur dans un script — **ne jamais modifier un seuil sans mettre
à jour `sources` et `fiabilite` dans la même ligne, et sans un commit qui dit
quelle valeur change, de quoi à quoi, sur quelle source.**

---

## 5. Nomenclature

Sources documentaires : `FAMILLE-NN` (`REG-03`, `PFAS-05`, `MET-01`, `MIX-08`,
`PE-04`), répertoriées dans `docs/INDEX_SOURCES.md`.
Fichiers de source : `CODE_Organisme_description_annee.ext`
(ex. `REG-03_UE_directive-2020-2184_2020.pdf`).

Plusieurs sources sur une ligne du référentiel : séparateur **barre verticale**,
`REG-01|REG-03`. **Ne jamais utiliser le point-virgule dans une cellule** :
c'est le séparateur de colonnes du CSV, et il décale silencieusement toute la
ligne. L'erreur a été commise **deux fois** — d'abord sur 14 lignes, où elle
avait déplacé `fiabilite` ; puis le 7 août 2026 sur quatre lignes, en rédigeant
les corrections elles-mêmes — et les deux fois rien ne l'a signalée.
`build_db.py` refuse désormais un CSV dont une ligne n'a pas le bon nombre de
colonnes (`controler_forme`) : le chargement échoue au lieu de charger des
données décalées.

---

## 6. Circuit de travail

```
1. build      src/build_db.py                            → schéma + référentiel
2. fetch      src/fetch_hubeau.py 31520                  → une commune (CP ou INSEE)
   ou         src/fetch_departement.py --dept 17         → un département entier
3. contrôle   v_parametres_non_apparies, pct_couverture  → couverture réelle
4. figer      src/figer.py                               → sortie estampillée
5. analyse    src/queries.sql                            → requêtes de thèse
6. fiche      sortie/build_fiche.py                      → fiche citoyenne
```

Le raccourci qui fait tout l'enchaînement pour une commune :

```
python3 src/observer.py 31520
```

**Publier est un geste séparé de collecter/figer**, et c'est lui qui fabrique
les pages — voir `docs/ARCHITECTURE.md` §6. Erreur réellement commise le
8 août 2026 : 28 communes collectées et figées sans page, donc invisibles.

**Rédiger, quatrième étape, se découpe dès qu'il y a du volume** — le script
tient les deux bouts déterministes, des agents de fond tiennent le milieu :

```
py -X utf8 sortie/rediger_lot.py --etat      # ce qui reste à rédiger
py -X utf8 sortie/rediger_lot.py --dossiers  # fabrique les dossiers de faits
                                             # → faire rédiger en Claude Code
py -X utf8 sortie/rediger_lot.py --verifier  # contrôle, sans rien écrire
py -X utf8 sortie/rediger_lot.py --integrer  # contrôle puis écrit la prose
```

Aucun appel d'API, aucune clé : la rédaction se fait **dans Claude Code**, un
agent de fond par dossier, sur la consigne versionnée
`sortie/CONSIGNE_REDACTION.md`.

Ce que le script garantit : il écrit dans `redactions_proposees.json`, **jamais**
dans `redactions.json` — la préséance du §8quater est un ordre de confiance. Il
est idempotent, un point d'eau déjà servi par une clé `INSEE@date`, `INSEE` ou
`PREL:` est sauté. Et il **contrôle avant d'écrire** : prescription (§2.2),
comparaison anonyme (§2.11) — les fonctions de `tests/test_sorties.py`,
importées et non recopiées —, affirmation d'absence (§2.4), qualificatif
sanitaire, « risque » sur l'indice (§7.1), et **tout nombre décimal absent du
dossier de faits bloque l'intégration** (§2.7 transposé du chiffre au texte).

Entretien du catalogue des paramètres (rare, quand de nouveaux libellés
apparaissent) :

```
python3 src/catalogue_parametres.py --depts 17,31,28,51 --communes 8 --depuis 2023
```

Matériaux d'étude, hors chaîne de publication, écrits dans `data/etudes/` :

```
python3 src/etude_panel.py       # journal des abandons de paramètres
py -X utf8 src/etude_melange.py  # dénombrement du mélange de réseaux
```

Tests de non-régression, sans réseau, **à lancer après toute modification de
`common.py`, `ingest.py` ou des vues** :

```
python3 tests/test_verdict.py
python3 tests/test_figer.py
```

Ils fabriquent un bulletin complet fictif et vérifient que les règles §2.3 à
§2.5 sont effectivement appliquées par les vues. Si un contrôle échoue, c'est
une règle de méthode qui a cessé de s'appliquer — pas un détail technique.

La collecte est **idempotente** : réingérer un prélèvement déjà présent le
remplace (DELETE puis INSERT sur `code_prelevement`). On peut relancer une
collecte interrompue sans précaution.

### La requête qui porte la thèse

```sql
SELECT commune, dept, date_prelevement, nb_bascules
FROM v_prelevement_verdict
WHERE est_complet AND nb_depasse_2026 = 0 AND nb_bascules > 0
ORDER BY nb_bascules DESC;
```

*Des bulletins complets, déclarés parfaitement conformes aujourd'hui, qui ne
l'auraient pas été il y a dix ans.* Chaque ligne retournée est un cas.

---

## 7. Deux axes de méthode

### 7.1 Effet cocktail — `docs/METHODE_EFFET_COCKTAIL.md`

Trois indicateurs du plus solide au plus fragile : dénombrement, charge massique
cumulée, indice de danger. Implémentés dans `src/figer.py`.

Contraintes non négociables : **l'indice de danger n'est jamais nommé
« risque »**, jamais publié sans le nombre de substances qui le composent,
jamais présenté comme un verdict de potabilité. Il est **restreint aux
substances de synthèse** — calculé sur tous les paramètres notés, il était
dominé par le potassium, les chlorures, les sulfates et le sodium, et passait
au-dessus de 1 sans qu'aucun micropolluant n'y soit pour rien.

Les cadres de référence (MAF, CAG/MOET de l'EFSA, EDC-MixRisk) sont cités dans
la note de méthode mais **non implémentés**. Tant qu'ils ne le sont pas, l'indice
sert à classer des bulletins entre eux, pas à estimer un risque. **Ne pas
publier de chiffre d'effet cocktail sans avoir écrit la méthode et ses limites.**

### 7.2 Dilution — `docs/METHODE_DILUTION.md`

Si un réseau est alimenté par trois captages et qu'un seul est très dégradé, le
mélange peut respecter la limite sans qu'aucune action n'ait été menée sur la
pollution : **la dilution tient alors lieu de dépollution.**

> « ceci est une hypothèse et non une affirmation, il faut investiguer. »

Statut inchangé : **hypothèse à instruire**. Ce qui est acquis au 8 août 2026 :
le champ `debit` des `reseaux` est la part du débit du réseau apportée par
l'installation amont du prélèvement — lecture **déduite du corpus**, marquée
`a_verifier` (§2.7) tant que l'API ne la documente pas. Le critère de mélange
est **une part inférieure à 100 %**, jamais le nombre de réseaux desservis. Une
part absente n'est pas 100 % : c'est un troisième état, `non_declare`.

Sur 45 bulletins et 42 réseaux : 6 réseaux portent un mélange lisible, 25
déclarent une source unique, 11 ne déclarent rien. **L'hypothèse a un terrain,
et il est petit.**

**La question qui commande tout n'est pas tranchée** : où, dans le réseau, le
prélèvement a-t-il été fait ? `code_lieu_analyse` vaut `L` sur les 45 bulletins.
S'il est fait après le point de mélange, l'hypothèse est indémontrable avec ces
données. **Tant que ce point n'est pas tranché, aucune conclusion de dilution ne
se publie.** Rien de tout cela n'est lu par la vitrine ni par la fiche.

Et **diluer est légal** : la question est posée à la norme, jamais à
l'exploitant (§2.1).

---

## 8. Angles morts connus

À conserver visibles, ce sont les prochains chantiers (détail et priorités dans
`docs/CHANTIERS.md`) :

- **radiologique** : tritium, radon, dose indicative totale — au référentiel,
  non travaillés analytiquement ;
- **eaux embouteillées** : aucun corpus, alors que les repères « nourrissons »
  utilisés comme `seuil_strict` en viennent ;
- **effet cocktail** : cf. §7.1 ;
- **couverture géographique** : moteur et collecte prêts pour le département ;
  **aucun département n'a encore été collecté en entier** ;
- **communes sans bulletin complet** : règle arrêtée le 7 août 2026 — prendre le
  bulletin de l'UDI qui alimente la commune même s'il a été prélevé ailleurs, en
  le mentionnant ; à défaut la commune sort en « non documenté », catégorie
  visible à part entière. **Non implémenté** ;
- **cartographie** : `couverture_communes` porte statut et coordonnées ; le fond
  départemental est en place, la couverture nationale (~1,7 Go) devra être
  découpée par département ;
- **eau brute et dilution** : cf. §7.2 — le maillon « quel captage alimente
  quelle installation » n'est pas exposé par Hub'Eau et ne pourra être établi
  que par inférence géographique, **affichée comme hypothèse** ;
- **seuils dépendant de la ressource** : cf. §2.13 — sélénium et bore ;
- **chlorites** : référence de qualité 0,20 mg/L expirée au 31 décembre 2025,
  remplacement inconnu. Cas de seuil daté **par le haut**, que le modèle ne sait
  pas exprimer (il connaît `date_applicabilite_2026`, pas de date de fin) ;
- **famille métabolite** : 24 lignes issues de MET-05. Le tableau ANSES est mis
  à jour périodiquement — le resynchroniser fait partie de l'entretien.

---

## 8bis. Ce que l'interface doit porter

Les règles de méthode ne servent à rien si elles s'arrêtent à la base : ce sont
des **obligations d'affichage**.

**La surface à consommer, et elle suffit** — ne jamais recalculer un verdict à
la volée dans l'interface : une vue suit le référentiel du jour, une ligne figée
dit contre quelle grille elle a été calculée.

| Table | Ce qu'elle porte |
|---|---|
| `analyses_figees` | une ligne par bulletin : verdicts, couverture, effort, sommes |
| `verdicts_figes` | le détail paramètre par paramètre |
| `couverture_communes` | statut et coordonnées de chaque commune — **ce que colorie la carte** |

1. **Jamais un « conforme » sans son dénominateur.** « 214 paramètres notés sur
   234 mesurés » accompagne tout verdict (§2.8).
2. **L'effort de recherche à côté de toute comparaison ou de tout classement**,
   et la zone comparée est nommée (§2.11). Utiliser les taux, jamais les comptes.
3. **Trois états, pas deux.** Conforme / dépassement / **indéterminé**, qui a sa
   propre couleur (§2.4).
4. **« Non documentée » est une catégorie visible**, ni verte ni rouge (§2.3).
5. **Quand l'analyse est empruntée au réseau, dire où elle a été prélevée.**
6. **Le verdict s'affiche à la date du prélèvement** (§2.10) : c'est
   `depasse_applicable`, pas `depasse_2026`.
7. **L'indice de danger n'est jamais nommé « risque »**, jamais publié sans le
   nombre de substances qui le composent (§7.1).
8. **Une valeur en `fiabilite = a_verifier` est signalée comme telle** (§2.7).
9. **Chaque écran porte sa traçabilité** : version de référentiel, date de
   calcul, lien vers l'appel Hub'Eau d'origine (`source_url`).
10. **Aucune recommandation de produit, d'équipement ou de filtration, nulle
    part, jamais** (§2.2). Et on interroge la norme, jamais les acteurs (§2.1).
11. **Quand la LQ dépasse le seuil, la ligne le dit et le chiffre** — « LQ
    0,5 µg/L, soit 5 × la limite de 0,1 » : sous cette valeur l'analyse ne voit
    rien, là où la conformité se joue (§2.4). Le bulletin porte en outre
    `aveugles_pour_mille`, la part de l'analyse qui ne peut pas conclure — un
    taux, donc comparable, ce que le compte brut n'est pas (§2.11). **Un seuil
    de zéro ne se perce pas par le bas** : la bactériologie exige l'absence et
    la LQ d'un dénombrement vaut 1. Et une LQ élevée est une **capacité
    d'instrument**, jamais une négligence (§2.1) ; situer la sienne parmi celles
    du corpus impose d'afficher la base — « sur 29 bulletins, 5 départements »
    — car elle se déplace : le plus fin **identifié** (§2.14).

**Le parcours minimal** : `code postal → commune(s) → point(s) d'eau → dernier
bulletin complet → fiche`. C'est ce que fait déjà `src/observer.py` en ligne de
commande ; l'interface n'a pas à réinventer cette chaîne, elle l'expose.

Comment tout cela est construit — atelier/vitrine, origine de la prose, clés de
rédaction, indicateurs de la fiche, défauts trouvés en chemin :
**`docs/ARCHITECTURE.md`**.

---

## 9. Licence et posture

Données et référentiel sous **ODbL 1.0** (partage à l'identique, mention de la
source). Voir `LICENCE.md`.

Les données brutes proviennent d'Hub'Eau / SISE-Eaux (ministère chargé de la
santé), sous Licence Ouverte. Le travail propre au projet est le référentiel
daté, la méthode et le code.

Toute réutilisation par un tiers doit mentionner l'Observatoire **sans le faire
endosser** ses propres conclusions : la mention de source n'est pas une caution.

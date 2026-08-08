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

Constante : `SEUIL_COMPLET = 200`. Un prélèvement est retenu comme complet
si `nb_parametres > 200`.

Valeur fixée sur la distribution réelle, mesurée le 7 août 2026 sur 964
prélèvements des départements 17, 28 et 31 : la routine s'éteint vers 100,
les analyses complètes commencent à 236, et **la tranche 150-199 est
totalement vide**. La coupure n'arbitre donc rien. Elle était auparavant à
250, ce qui amputait le bas du groupe des complètes : le bulletin de Challet
du 10/03/2026 (234 paramètres), sur lequel l'ARS a prononcé une
non-conformité pour le chlorothalonil R417888, en était exclu — la règle
faisait manquer le bulletin le plus probant du projet.

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

### 2.11 L'effort de recherche est un indicateur, et il se déclare

On ne trouve que ce qu'on cherche. Une commune qui fait analyser 700
paramètres a mécaniquement plus de chances d'en voir un dépasser qu'une
commune qui en fait analyser 200. Comparer leurs nombres bruts de
dépassements est un contresens, et il pénalise la transparence.

**Le nombre de paramètres recherchés n'est pas un indicateur de qualité de
l'eau. C'est un indicateur de l'effort de recherche, et il se lit dans
l'autre sens :** une eau « correcte » sur 200 paramètres est une information
plus faible qu'une eau « moyenne » sur 700. La première n'a pas été beaucoup
interrogée.

Conséquences dans le modèle :

- `nb_parametres` et `nb_synthese_recherchees` — ce qui a été cherché ;
- `classe_effort` — `restreinte` (<200), `standard` (200-299),
  `approfondie` (300-449), `exhaustive` (≥450) ;
- `depassements_pour_mille` et `synthese_quantifiees_pour_mille` — des
  **taux**, seuls comparables d'un bulletin à l'autre. Les comptes bruts ne
  le sont pas ;
- `v_effort_recherche` — la vue qui met en tête les communes les plus
  interrogées, donc les plus transparentes.

Cas d'école, Challet : 660 paramètres en 2018 et aucun dépassement ; 234 en
2026 et quatre. L'effort a baissé et les dépassements ont augmenté : la
dégradation est réelle, et même sous-estimée. Sans l'effort affiché, on ne
pourrait pas l'affirmer.

Règle de sortie : **aucune comparaison entre deux communes, ni aucun
classement, sans afficher l'effort de recherche de chacune.** Cette règle
vaut aussi pour les indicateurs de cumul, dont le dénombrement dépend
directement de ce que le laboratoire a cherché
(cf. `docs/METHODE_EFFET_COCKTAIL.md`, indicateur A).

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

### 2.14 « Le plus strict identifié », jamais « le plus strict au monde »

La colonne `seuil_strict` a longtemps été présentée comme « la norme la plus
protectrice au monde ». C'est une prétention à l'exhaustivité que le projet ne
peut pas soutenir : un balayage mondial n'a été fait que pour les PFAS.
Partout ailleurs, la valeur est le plus strict **que nous ayons identifié**,
et c'est ce qu'il faut écrire.

La différence n'est pas rhétorique. Sur la somme des 20 PFAS, le référentiel
affichait 0,020 µg/L comme « le plus strict au monde » — c'était en réalité le
seuil allemand portant sur la somme de **4** substances, et applicable
seulement au 12 janvier 2028. La valeur juste est 0,100 µg/L, et à ce niveau
**personne n'est plus strict que l'Union européenne** : Danemark 0,100 (sur 22
substances), Suède 0,100 (sur 21), Allemagne 0,100. L'axe international ne
mord pas sur ce paramètre, et prétendre le contraire était un argument faux.

Il mord en revanche sur la somme des 4, où la hiérarchie est réelle :
Danemark 2 ng/L, Suède 4 ng/L, Allemagne 20 ng/L en 2028.

### 2.15 Trois registres, jamais fusionnés

Le §2.6 en distinguait deux. Il y en a trois, et le référentiel a désormais
une colonne par registre :

| Registre | Colonne | Autorité |
|---|---|---|
| réglementaire | `pe_reglementaire` | UE — le seul PE avéré dans l'EDCH est le bisphénol A |
| scientifique | `pe_scientifique` | littérature, agences |
| cancérogénicité | `cancerogenicite_circ` | CIRC, référence mondiale |

L'atrazine l'illustre : classée **2A par le CIRC en novembre 2025**, elle n'a
**aucun statut PE réglementaire** — jamais évaluée au titre des critères de
2018/605, parce qu'interdite depuis 2004 et donc jamais soumise à
renouvellement. Et son interdiction elle-même (décision 2004/248/CE) est
motivée par les eaux souterraines, pas par la perturbation endocrinienne.
Trois faits vrais, trois registres différents, aucun ne se déduit des autres.

L'ANSES en donne la formulation exacte pour l'atrazine déséthyl : son avis
2015-SA-0084 retient « une suppression du pic de l'hormone lutéinisante
entraînant une perturbation du cycle œstral » comme effet critique — et
n'emploie jamais le mot « perturbateur endocrinien ». Le fait toxicologique
est reconnu, la qualification réglementaire ne l'est pas.

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

**La source doit couvrir CE paramètre précisément.** Ajout du 7 août 2026,
après une erreur réelle. Le référentiel portait le chlorothalonil R417888 à
0,9 µg/L, sourcé `MET-01`, marqué `verifie`. La source existait bel et bien —
l'avis ANSES du 29 avril 2024, saisines 2023-SA-0041-a et 2023-SA-0142-a —
mais elle ne disait pas cela. Un seul avis, deux métabolites, **deux
conclusions opposées** :

- **R471811** → *non pertinent*, valeur indicative 0,9 µg/L. Il ne partage
  très probablement pas le mode d'action néphrotoxique de la substance mère ;
- **R417888** → *pertinent*, limite de qualité 0,1 µg/L. « Il n'est pas
  possible d'exclure l'existence d'un potentiel génotoxique ». S'y ajoute une
  valeur sanitaire transitoire de 3 µg/L reprise de l'UBA allemande, qui est
  le seuil de **restriction de consommation** — à ne jamais confondre avec la
  limite de conformité.

L'entrée d'index s'intitulait `avis-chlorothalonil-R471811.pdf` et la valeur
0,9 avait été étendue à R417888 **par analogie de famille**. C'est le même
mécanisme que l'erreur sur le plomb : une source réelle, une extrapolation
vers un paramètre voisin, et une valeur fausse qui prend l'apparence du
sourcé. Une source qui porte sur la substance d'à côté n'est pas une source.

Corollaire opérationnel : le nom de fichier d'une source doit énumérer les
paramètres qu'elle couvre, et un `⚠️ à confirmer dans le PDF` dans l'index
interdit de s'appuyer sur la ligne.

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

### 2.10 Un verdict se rend à la date du prélèvement

Un reclassement n'est pas rétroactif. La note d'information de la délégation
départementale de Charente-Maritime du 10 juin 2024 est formelle :

> « Il n'y a pas de rétroactivité possible. C'est pourquoi l'expression des
> non-conformités mises en évidence avant le 29/04/2024 est maintenue. »

Une mesure de R471811 à 0,5 µg/L prélevée en 2023 **est** une non-conformité,
et elle le reste. La même valeur prélevée en 2025 est conforme. C'est la thèse
du projet, écrite noir sur blanc par l'administration elle-même.

Le moteur comparait toujours à `seuil_2026`, sans regarder la date du
prélèvement : il aurait déclaré « conforme » une mesure de 2023 que l'ARS
avait déclarée non conforme. C'est l'erreur **symétrique** de celle du plomb,
où un seuil futur était appliqué trop tôt.

D'où la colonne `date_applicabilite_2026` et, dans `v_mesures_verdict` :

| Colonne | Ce qu'elle dit |
|---|---|
| `seuil_applicable` / `grille_applicable` | le seuil en vigueur **le jour du prélèvement** |
| `depasse_applicable` | le verdict tel qu'il devait être rendu ce jour-là — le seul comparable à la conclusion de l'ARS |
| `depasse_2016` / `depasse_2026` | les deux contrefactuels, inchangés |
| `bascule_datee` | la bascule **datable au jour près** : ce prélèvement est conforme parce qu'il a été fait après le déplacement |

Une ligne dont le seuil a bougé sans qu'on sache quand produit un verdict
anachronique : `v_seuils_sans_date` les liste, et `build_db.py` les signale à
chaque construction. Six lignes y figurent aujourd'hui — ESA/OXA métolachlore,
ESA métazachlore, antimoine, sélénium, bore.

### 2.12 Le seuil de 2016 des métabolites est une extrapolation, et il se dit

La colonne `seuil_2016` vaut 0,1 µg/L sur les 24 lignes de la famille
métabolite. Le fondement est l'**instruction n° DGS/EA4/2020/177 du
18 décembre 2020** : « en l'absence d'éléments permettant d'écarter le
potentiel d'activité pesticide ou le risque de génotoxicité, le métabolite est
caractérisé comme pertinent » — donc noté à 0,1 µg/L tant qu'il n'est pas
reclassé.

**Mais cette instruction date de décembre 2020 et remplace celle de 2010.**
Appliquer 0,1 µg/L à un prélèvement de 2016 est un raisonnement raisonnable,
pas la lecture d'un texte de 2016. C'est une **extrapolation assumée**, et
elle doit être présentée comme telle partout où la grille de 2016 est
invoquée sur un métabolite.

C'est exactement le glissement qui a produit l'erreur sur le R417888 : une
source réelle, une inférence par-dessus, et un résultat qui prend l'apparence
du sourcé. La différence est qu'ici l'inférence est écrite.

### 2.13 Un seuil peut dépendre du procédé ou de la ressource, pas seulement de la date

Quatre cas connus, et c'est assez pour être structurel :

| Paramètre | Seuil de base | Seuil conditionnel | Condition |
|---|---|---|---|
| chlorates | 0,25 mg/L | 0,70 mg/L | désinfection générant des chlorates |
| chlorites | 0,25 mg/L | 0,70 mg/L | désinfection générant des chlorites |
| sélénium | 20 µg/L | 30 µg/L | exception géologique |
| bore | 1,5 mg/L | 2,4 mg/L | exception géologique |

Deux colonnes le portent : `seuil_conditionnel` et `condition_seuil`.

**Rien dans les données ne dit si la condition est remplie.** On ne connaît ni
le procédé de désinfection de l'usine, ni la nature géologique de la
ressource. La règle est donc : **un dépassement n'est prononcé que si la
mesure franchit AUSSI la valeur la plus permissive.** Entre le seuil de base
et le seuil conditionnel, c'est un `indetermine_condition` — pas une
non-conformité. `v_verdicts_sous_condition` les liste, et ils doivent être
vérifiés à la main avant toute publication.

Ce choix est asymétrique et assumé : **un faux positif coûte plus cher au
projet qu'un faux négatif.** Une non-conformité annoncée à tort se retourne
contre l'Observatoire ; une non-conformité manquée reste à trouver.

Le modèle ne sait toujours pas exprimer une date de **fin** d'applicabilité :
la référence de qualité des chlorites, 0,20 mg/L, a expiré le 31 décembre 2025
sans remplacement connu. Elle est documentée dans `statut_2026`, pas
calculée.

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
                    (dont date_applicabilite_2026 : à partir de quand la
                     grille 2026 s'applique — cf. §2.10)
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

### La fiche sépare le factuel de la prose

`sortie/build_fiche.py` dérive de la base **tout ce qui est factuel** :
mesures, seuils, verdicts, couverture, effort de recherche, conclusion de
l'ARS. Chaque fiche porte la version de référentiel et la date de calcul qui
l'ont produite.

**La prose porte toujours son origine.** Règle révisée le 8 août 2026 sur
instruction de Yannick : la prose *peut* être générée, elle ne peut jamais être
anonyme. Voir §8quater — trois origines (`auteur`, `propose`, `derive`), une
préséance stricte, et chaque section affiche la sienne.

C'était la dernière partie non traçable du dépôt : les chiffres y étaient
écrits en dur à côté des textes.

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
CSV, et il décale silencieusement toute la ligne.

L'erreur a été commise **deux fois** : d'abord sur 14 lignes, où elle avait
déplacé `fiabilite` ; puis le 7 août 2026 sur quatre lignes, en rédigeant les
corrections elles-mêmes. Les deux fois, rien ne l'a signalée. `build_db.py`
refuse désormais un CSV dont une ligne n'a pas le bon nombre de colonnes
(`controler_forme`), et le chargement échoue au lieu de charger des données
décalées.

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
- **cartographie** : `couverture_communes` porte le statut et les
  coordonnées de chaque commune ; la carte elle-même reste à faire ;
- **eau brute et dilution** : cf. §7bis ;
- **seuils dépendant de la ressource** : cf. §2.13 — sélénium et bore ;
- **chlorites** : référence de qualité de 0,20 mg/L « applicable jusqu'au
  31 décembre 2025 », donc expirée, et on ignore ce qui la remplace. Le
  référentiel ne porte pas cette ligne. C'est un cas de seuil daté **par le
  haut**, que le modèle ne sait pas non plus exprimer : il connaît
  `date_applicabilite_2026` (à partir de quand), pas de date de fin ;
- **famille métabolite** : 24 lignes issues de MET-05. Le tableau ANSES est
  mis à jour périodiquement — le resynchroniser fait partie de l'entretien.

---

## 8bis. Ce que l'interface doit porter

Section écrite le 7 août 2026, à l'ouverture du chantier web. Les règles de
méthode ne servent à rien si elles s'arrêtent à la base : ce sont des
obligations d'affichage.

### La surface à consommer

Trois tables, et elles suffisent. Ne jamais recalculer un verdict à la volée
dans l'interface : une vue suit le référentiel du jour, une ligne figée dit
contre quelle grille elle a été calculée.

| Table | Ce qu'elle porte |
|---|---|
| `analyses_figees` | une ligne par bulletin : verdicts, couverture, effort, sommes |
| `verdicts_figes` | le détail paramètre par paramètre |
| `couverture_communes` | statut et coordonnées de chaque commune — **ce que colorie la carte** |

### Obligations d'affichage

1. **Jamais un « conforme » sans son dénominateur.** « 214 paramètres notés
   sur 234 mesurés » accompagne tout verdict (§2.8).
2. **L'effort de recherche à côté de toute comparaison ou de tout
   classement.** Une eau correcte sur 200 paramètres n'est pas comparable à
   une eau moyenne sur 700 (§2.11). Utiliser les taux, jamais les comptes.
3. **Trois états, pas deux.** Conforme / dépassement / **indéterminé**. Un
   indéterminé n'est pas un conforme et doit avoir sa propre couleur (§2.4).
4. **« Non documentée » est une catégorie visible**, ni verte ni rouge. Une
   commune sans bulletin ne disparaît pas de la carte (§2.3).
5. **Quand l'analyse est empruntée au réseau, dire où elle a été prélevée.**
   Sans cela, l'habitant croit que l'analyse a eu lieu chez lui.
6. **Le verdict s'affiche à la date du prélèvement**, pas contre la grille du
   jour (§2.10). C'est `depasse_applicable`, pas `depasse_2026`.
7. **L'indice de danger n'est jamais nommé « risque »**, jamais publié sans le
   nombre de substances qui le composent, jamais présenté comme un verdict de
   potabilité (§7 et docs/METHODE_EFFET_COCKTAIL.md).
8. **Une valeur en `fiabilite = a_verifier` est signalée comme telle** (§2.7).
9. **Chaque écran porte sa traçabilité** : version de référentiel, date de
   calcul, lien vers l'appel Hub'Eau d'origine (`source_url`).
10. **Aucune recommandation de produit, d'équipement ou de filtration, nulle
    part, jamais** — pas même en note de bas de page (§2.2). Et on interroge
    la norme, jamais les acteurs qui l'appliquent (§2.1).

### Le parcours minimal

`code postal → commune(s) → point(s) d'eau → dernier bulletin complet → fiche`

C'est ce que fait déjà `src/observer.py` en ligne de commande. L'interface
n'a pas à réinventer cette chaîne : elle l'expose.

---

## 8ter. Ce qui a été construit, et pourquoi ainsi

Chantier web ouvert le 7 août 2026. Trois décisions structurantes, à ne pas
défaire sans raison.

### L'atelier et la vitrine sont deux objets distincts

| | `atelier/` | `site/` |
|---|---|---|
| Ce qu'il fait | il **agit** : télécharge, écrit en base, fige, publie | il **montre** |
| Où il écoute | 127.0.0.1 uniquement | partout |
| Publié ? | **jamais** | c'est le seul objet publié |
| Coût d'hébergement | aucun, il tourne chez Yannick | aucun, ce sont des fichiers |

Un formulaire public qui déclencherait une collecte serait deux fautes à la
fois : une charge abusive sur Hub'Eau, service public gratuit et sans clé
(§3.2), et une porte d'entrée sur la base. La séparation n'est pas une
précaution technique, c'est la conséquence de ce que chacun fait.

**La vitrine est statique**, et ce n'est pas qu'une économie d'hébergement.
Une ligne figée est une photographie datée — elle porte `version_referentiel`
et `calcule_le` précisément pour qu'on sache contre quelle grille elle a été
calculée. Un serveur qui rejouerait le verdict à chaque visite reproduirait, à
l'intérieur de l'outil, le défaut que l'outil dénonce.

Limite connue : à l'échelle nationale (~35 000 communes), le site statique
approche 1,7 Go et demandera d'être découpé par département, ou repensé. Ce
n'est pas un problème avant la Phase 3.

### `verdicts_figes` porte désormais le verdict à la date

Défaut réel trouvé en construisant l'interface : la table ne stockait que
`depasse_2026`. Une sortie qui ne lit que les tables figées — ce qu'impose
§8bis — ne pouvait donc **pas** honorer l'obligation 6, et affichait
« conforme » sur une ligne que l'ARS avait déclarée non conforme, pendant que
le compteur `nb_depasse_applicable` du même écran annonçait un dépassement.

Cinq colonnes ajoutées : `seuil_applicable`, `grille_applicable`,
`depasse_applicable`, `bascule_datee`, `indetermine_condition`. Elles
existaient déjà dans `v_mesures_verdict` ; elles ne survivaient simplement pas
au figeage.

Corollaire outillé : `figer.assurer_schema()` compare les colonnes déclarées à
celles présentes et **reconstruit** une table figée dont le schéma a dérivé.
`CREATE TABLE IF NOT EXISTS` ne dit rien quand la table existe avec d'autres
colonnes — un dépôt plus ancien aurait gardé la sienne en silence.

### Le design vit dans un seul fichier

`site/gabarits/observatoire.css`, `corps_fiche.html` et `fiche.js` sont
partagés par les deux sorties : la vitrine les **sert**, la fiche autonome les
**inline** pour rester transmissible d'un bloc et consultable sans réseau. Deux
copies auraient divergé dès la première retouche, et la fiche et le site se
seraient mis à dire deux choses différentes du même bulletin.

Le violet est réservé à la **bascule**. C'est l'indicateur central du projet :
le noyer dans l'ambre des « signaux d'attention » le rendrait invisible.

### La carte ne fait aucune requête vers un tiers

Le fond départemental est projeté en SVG à la construction, à partir de
`referentiel/geo/departements-simplifie.geojson` (IGN/Etalab, Licence
Ouverte), et incorporé à la page. Aucun serveur de tuiles n'est appelé — donc
aucune adresse IP de visiteur transmise à un tiers, et aucune bannière de
consentement à imposer. Même raison pour la recherche par code postal, qui
travaille sur un index JSON chargé par le navigateur : **ce que quelqu'un
cherche ne nous parvient jamais.** Pour un outil qui parle de l'eau que les
gens boivent chez eux, ce n'est pas un détail d'implémentation.

Non couvert : les départements et collectivités d'outre-mer ne figurent pas sur
ce fond.

---

## 8quater. La prose et son origine

Règle **révisée le 8 août 2026**. Le dépôt portait jusque-là : « la prose n'est
jamais générée ». Instruction de Yannick, à l'ouverture du chantier de
rédaction :

> « Il n'y a aucune rédaction ? C'est là où l'IA doit rentrer en compte. […]
> c'est bien à toi de rédiger les résultats. »

La règle change donc, mais **ce qu'elle protégeait ne change pas** : le lecteur
doit pouvoir savoir d'où vient chaque phrase. C'est le §2.7 — toute affirmation
est sourcée ou marquée — transposé du chiffre au texte, et il vaut d'autant
plus quand le texte sort d'une machine.

### Trois origines, une préséance stricte

| Origine | Où elle vit | Ce qu'elle peut dire | Affichage |
|---|---|---|---|
| `auteur` | `sortie/redactions.json` | tout | rien à signaler |
| `propose` | `sortie/redactions_proposees.json` | le contexte que la base ignore | « proposition, à relire » |
| `derive` | **nulle part** — calculé par `sortie/rediger.py` | rien qui ne vienne d'une requête | « dérivé de la base » |

La fusion se fait **champ par champ**, pas commune par commune : un verdict de
la main de Yannick peut voisiner avec un inventaire dérivé. Le champ `analyse`
fait exception et **s'assemble** au lieu de s'écraser — les faits dérivés
d'abord, le contexte proposé ensuite — sauf si Yannick l'a écrit, auquel cas sa
version se suffit.

### Pourquoi le dérivé n'est stocké nulle part

Un texte figé à côté de chiffres qui évoluent est exactement la demi-vérité que
l'outil dénonce. `rediger.py` compose ses phrases au moment de construire la
fiche : si le référentiel bouge et qu'on refige, **la phrase bouge avec le
chiffre**. Elle ne peut pas rester vraie pendant qu'il devient faux.

### Ce que le dérivé s'interdit

Aucune connaissance extérieure. Aucun qualificatif sanitaire — « dangereux »,
« sain », « inquiétant » n'y figurent pas : il décrit des écarts à des seuils
datés. Aucune affirmation d'absence : un non-quantifié est « sous la limite de
quantification », jamais « absent » (§2.4). Et jamais de recommandation de
produit ni de mise en cause d'un acteur (§2.1, §2.2) — cela vaut pour les trois
origines.

Le générateur a d'ailleurs déjà évité deux pièges qu'un modèle pressé aurait
manqués : à Soulaires, les deux dépassements sont **bactériologiques** et non
chimiques, sur un plateau céréalier où l'on attendait des pesticides ; à
Boissezon, il a relevé de lui-même que l'effort de recherche est passé de 627 à
369 paramètres entre 2019 et 2024.

### Valider une proposition

Recopier la section dans `redactions.json`. Elle devient `auteur` et cesse
d'être signalée. La supprimer de `redactions_proposees.json` la fait
disparaître : la fiche retombe alors sur le texte dérivé, jamais sur du vide.

---

## 8quinquies. Les indicateurs de la fiche

Refonte du 8 août 2026. Les six indicateurs d'origine parlaient tous de
**l'analyse** — effort, couverture, nombre de dépassements. Aucun ne parlait de
**l'eau**. Quatre niveaux désormais, de poids visuel décroissant :

1. **le bandeau de tête** — le réétalonnage, démontré par une jauge où la
   mesure, la limite de 2016 et celle du jour sont sur la même règle ;
2. **ce qu'on a trouvé** — pesticides, PFAS, nitrates, sous-produits de
   chloration, cumul ;
3. **quelle eau c'est** — pH, conductivité, dureté, COT, turbidité, chlore.
   Ce n'est pas de la pollution : c'est le caractère de la ressource ;
4. **ce que vaut cette lecture** — effort, couverture, indéterminés.

Chaque indicateur porte une **barre** : « 0,493 µg/L » ne se lit pas,
« 99 % du seuil applicable » se lit. Et chacun porte sa phrase de lecture — ce
qu'il veut dire *et son piège*.

`referentiel/indicateurs.csv` est versionné : ce qu'on choisit de mettre en
avant est une décision éditoriale et doit laisser une trace datée. **Il ne
contient aucun seuil** — ils viennent tous du référentiel ou de la limite que
la source déclare, sans quoi il y aurait deux sources de vérité.

### Le résidu sec n'existe pas dans SISE-Eaux

Ni au corpus, ni au catalogue Hub'Eau : le contrôle sanitaire ne le mesure pas.
La **conductivité** mesure la même chose — la minéralisation totale — par la
conductance plutôt que par pesée. Elle est présentée comme telle. Ne pas
fabriquer de conversion.

### Les plages viennent de la source, pas de nous

`parse_plage()` lit les références encadrées par le haut ET par le bas que la
source déclare avec la mesure : `>=6,5 et <=9` pour le pH, `>=200 et <=1100`
pour la conductivité. Le modèle ne connaissait que le dépassement par le haut,
et ces paramètres disparaissaient de toute lecture. Une eau agressive est un
vrai sujet : elle dissout les matériaux du réseau qu'elle traverse.

### Perturbateurs endocriniens : trois registres, jamais fusionnés

Application directe du §2.6, et le troisième registre est le plus important :

| Registre | Ce qu'il dit | Dans le corpus |
|---|---|---|
| `pe_reglementaire` | reconnu par le droit européen | **bisphénol A seul** |
| `pe_scientifique` | rapporté par la littérature | PFAS, atrazine |
| `a_documenter` | **la question n'a pas été instruite** | 45 lignes |

« Non documenté » n'est pas « non ». Ranger ces 45 lignes avec les non-PE
serait un faux négatif, avec les suspects un faux positif. Elles ont leur
colonne, comme les indéterminés ont leur couleur. S'y ajoute le compte des
substances quantifiées **hors référentiel**, dont on ne sait rien du tout.

### PFAS : longueur de chaîne, et pourquoi

`referentiel/pfas_chaines.csv`, convention OCDE (carboxyliques longues à partir
de C8, sulfoniques à partir de C6), marquée `a_verifier` tant que le document
n'a pas été relu ici.

L'objet est réglementaire et lui seul : **la « somme de 4 » mise en avant par
la réglementation ne contient que des chaînes longues**, celles dont l'usage
est en cours d'interdiction. Les courtes qui les remplacent sont mesurées et
n'entrent dans aucun total opposable hormis la somme de 20. À Vourles :
3 longues quantifiées pour 0,015 µg/L, **5 courtes pour 0,047** — trois fois
plus, et hors de l'indicateur réglementaire. La mesure existe, la norme ne la
regarde pas. C'est le même mécanisme que le réétalonnage.

**Ce fichier ne sert à aucune recommandation** et ne doit jamais être utilisé
pour en suggérer une, de traitement, de procédé ou d'équipement (§2.2).

### Repères nourrissons

Cinq lignes du référentiel portent un `seuil_strict` issu de la réglementation
des eaux embouteillées autorisées à porter la mention « convient à
l'alimentation des nourrissons » (arrêté du 14 mars 2007) : nitrates 10 mg/L,
nitrites 0,05, fluorures 0,5, sulfates 140, magnésium 50.

**Ce ne sont pas des limites au robinet**, et la fiche le dit à chaque fois.
Le cas qui porte l'information est celui de Challet : nitrates à 48,3 mg/L,
conforme à la limite de 50, et près de cinq fois le repère nourrissons. Une eau
parfaitement conforme qui ne serait pas vendue sous cette mention.

### Défauts trouvés en construisant ces indicateurs

- **le repère danois disparaissait au figeage.** `verdicts_figes` ne retenait
  que les mesures « notées », c'est-à-dire ayant un seuil dans la grille du
  jour. La somme de 4 PFAS n'en a aucun — seulement le repère danois à 2 ng/L.
  Elle n'était donc jamais figée, et l'indéterminé le plus fréquent du projet
  (LQ courante 4 ng/L) s'évaporait. Filtre corrigé en
  `notee OR seuil_strict IS NOT NULL` ;
- **« Total des pesticides analysés » n'était apparié à rien.** Noté par la
  seule limite déclarée, donc sans grille 2016 : *une bascule sur la somme des
  pesticides était indétectable*. Alias ajouté ;
- **la version publiée était choisie par date de calcul.** Deux versions figées
  le même jour ne se départagent pas ainsi, et le site a publié l'ancienne
  grille en silence. `version_a_publier()` interroge désormais l'empreinte du
  référentiel actuel et refuse de se taire si elle n'est pas figée ;
- **refiger perdait les rattachements.** Les statuts `rattachee_reseau` et
  `non_documentee` ne sont écrits que par `observer.py`, pour les communes
  demandées. Or ils décrivent les DONNÉES disponibles, pas la grille : dix
  communes disparaissaient du site d'une publication à l'autre. Ils sont
  désormais reportés d'une version à la suivante ;
- **la prose était indexée par commune, pas par bulletin.** Clé
  `INSEE@AAAA-MM-JJ` disponible pour viser un prélèvement précis.

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

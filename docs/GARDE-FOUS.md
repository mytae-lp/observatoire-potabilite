# Garde-fous — le texte complet, avec ses cas

Ce document porte les **quinze garde-fous du projet dans leur version longue** :
la règle, mais aussi la citation de Yannick qui la fonde, l'erreur réellement
commise qui l'a fait écrire, et la conséquence dans le modèle de données.

`CLAUDE.md` §2 n'en garde que l'énoncé — c'est ce qui doit tenir en mémoire à
chaque session. **Ce fichier-ci est la référence** : quand un énoncé du
`CLAUDE.md` ne suffit pas à trancher un cas, c'est ici qu'on vient lire.

Les garde-fous sont ici **dans l'ordre numérique**. Ils ont été écrits dans un
autre ordre — celui de leur découverte — et les renvois se font par numéro.

Déplacé depuis `CLAUDE.md` le 8 août 2026, sans modification du texte.

---

## 2.1 Interroger la norme, pas accuser les acteurs

Le sujet est **la construction réglementaire du seuil**. Ce n'est ni l'ARS,
ni le distributeur, ni le maire, ni l'agriculteur. Un exploitant qui
respecte une limite fixée par arrêté n'est pas en faute : c'est la limite
qu'on examine.

Formulation correcte : « cette eau est conforme à une limite qui a été
relevée de 0,1 à 0,9 µg/L en 2020 ».
Formulation interdite : « cette eau est polluée et on vous le cache ».

---

## 2.2 C'est un outil de conscience, pas un outil de prescription

Citation de Yannick, à conserver telle quelle :

> « non, ce n'est pas le propos. ici c'est un outils de conscience. »

### La rédaction d'origine, et pourquoi elle a tenu un an

**Aucune recommandation de filtration, d'osmoseur, de charbon actif,
d'eau embouteillée, ni d'aucun équipement ou produit, jamais.** Pas même
en note de bas de page, pas même en « pour information ». Toute suggestion
d'équipement transforme un travail de vérification en argumentaire
commercial et détruit la crédibilité du projet.

Si un utilisateur demande quoi faire de son eau, la réponse est de
l'orienter vers l'information publique (ARS, mairie, données Orobnat), pas
vers un produit.

Cette rédaction protégeait contre un danger réel et elle l'a fait
efficacement : un observatoire qui suggère un équipement devient
indistinguable d'un site d'affiliation, et aucune rigueur en amont ne rachète
cela.

### La révision du 9 août 2026

Elle a été demandée par Yannick après un **retour de lecteur**, qui est le vrai
déclencheur et qu'il faut garder sous les yeux :

> « ton site il nous alerte, mais il peut créer une panique car on ne sait pas
> quoi faire de ces informations »

Ce n'est pas une intuition d'auteur, c'est un constat d'usage. Un outil qui
documente sans jamais ouvrir de suite laisse le lecteur avec une inquiétude et
aucune prise — et une inquiétude sans prise se résout ailleurs, souvent chez le
premier vendeur venu. La règle, écrite pour éloigner du commerce, y renvoyait
donc par omission.

La distinction posée par Yannick est celle qui rend la révision possible :

> « solutions de filtrations, non pas un produit mais un type, on sait que le
> charbon actif retient les chaînes longues de PFAS mais très mal les chaînes
> courtes. »

« Le charbon actif retient mal les PFAS à chaîne courte » est un **fait de
physico-chimie**, vérifiable et sourçable, du même statut qu'un seuil.
« Achetez tel filtre » est un argumentaire commercial. L'ancienne rédaction
interdisait les deux par la même phrase.

### Où passe exactement la frontière

**Permis** : décrire une famille de procédés et ce qu'elle retient. Et cela ne
vit **pas dans de la prose** — le projet ne dit rien qui ne soit sourcé et daté
(§2.7), donc cette matière prend la même forme que le référentiel de seuils :

```
referentiel/retention_procedes.csv
  procede ; famille_substance ; taille_ou_propriete ; retention ;
  sources ; fiabilite
```

Une ligne par couple **procédé × famille de substance**. Et le §2.7 s'y
applique entier : **la source doit couvrir CE couple précisément.** C'est le
piège du chlorothalonil R417888 transposé — « le charbon actif retient les
PFAS » étendu par analogie aux chaînes courtes serait une valeur fausse
déguisée en valeur sourcée, et c'est exactement l'exemple que Yannick cite pour
justifier la révision. La règle se retournerait alors contre elle-même.

**Interdit**, sans exception, nulle part, pas même en note :

| Ce qui est interdit | Le test qui le repère |
|---|---|
| marque, modèle, fournisseur, prix, lien d'achat | le lecteur peut-il acheter la chose nommée ? |
| conseil individuel — « pour votre eau, prenez… », « il faudrait filtrer » | la phrase s'adresse-t-elle à *ce* lecteur plutôt qu'à la substance ? |
| l'eau embouteillée comme solution | le projet n'en a **aucun corpus** (§8) : ce serait un conseil non documenté |
| description tournée en recommandation | impératif, conditionnel de conseil, classement de procédés par « efficacité » détaché de son couple procédé × substance |

Le dernier cas est le plus insidieux parce qu'il ne nomme aucun produit. « Le
meilleur procédé contre les PFAS est… » est déjà une prescription : un procédé
n'est efficace **que sur un couple**, et le classer dans l'absolu fabrique la
recommandation que le reste de la règle interdit.

### Le cas de Vourles, qui se referme

`tests/test_sorties.py` signalait, dans une section de la main de Yannick, la
phrase « précisément celles que le charbon actif retient mal ». Elle était
laissée en l'état — ni supprimée, ni validée — dans l'attente de cette révision
(chantier C1, gelé le 8 août 2026 : *« on fera une révision du §2.2 le moment
voulu. Pour l'instant on touche pas. »*).

La révision la rend conforme **sur le fond**. Elle ne la rend pas sourcée pour
autant : Yannick lui-même écrivait *« je n'en suis pas certain »*. La phrase
attend donc sa ligne dans `retention_procedes.csv` — charbon actif × PFAS à
chaîne courte, avec sa source — et non un simple retrait du signalement.

---

## 2.3 Ne travailler que sur les bulletins complets

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

---

## 2.4 Zéro n'est pas zéro

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

### Le plafond analytique — le §2.4 vu par le bout de l'instrument

Chantier C4, 8 août 2026. C'est l'argumentaire de la **onzième obligation
d'affichage du §8bis**.

Demande de Yannick, à propos de Pont-de-Larn (81) :

> « Je veux que l'on rajoute en rouge cette mention : le seuil du laboratoire ne
> permet pas du tout de quantifier ce qui est en dessous de cette limite. C'est
> une donnée importante, car là aussi, si je compare avec une autre commune dont
> les limites du laboratoire sont beaucoup plus faibles, la comparaison des deux
> est biaisée. »

La démonstration tient sur une molécule. Limites de quantification relevées pour
l'**hydrazide maléique**, dont la limite déclarée est 0,1 µg/L : 0,05 µg/L dans
les départements 22, 81 et 82 ; 0,1 dans le 17 ; **0,5** dans le 46 et le 81 ;
**2,5** dans le 81. Un facteur **50** entre la meilleure et la pire, pour la
même substance — et le Tarn porte à lui seul trois de ces valeurs, donc ce n'est
pas une caractéristique de département mais d'un laboratoire ou d'une campagne.

À 0,5 µg/L de LQ contre 0,1 de limite, le laboratoire ne peut **rien** dire de
la zone où se joue la conformité. Le « non quantifié » de Pont-de-Larn et celui
de Rostrenen portent le même mot et pas la même information.

**Trois niveaux, et ils ne se remplacent pas.** La mention chiffrée au
paramètre, vraie sans aucune convention ; le taux `aveugles_pour_mille` au
bulletin, seul comparable d'un bulletin à l'autre ; le barème, qui situe une LQ
parmi celles du corpus **à paramètre constant** — un laboratoire peut descendre
à 4 ng/L sur les PFAS et rester à 0,5 µg/L sur l'hydrazide maléique, et une
jauge unique par commune moyennerait deux instruments différents, ce qui serait
le profil synthétique interdit au §2.3 transposé à l'instrument. Le barème ne
s'affiche donc que là où il mord, et son échelle est logarithmique : les LQ
s'étalent sur des facteurs, pas sur des écarts.

**Un seuil de zéro ne se perce pas par le bas.** La limite de qualité de la
bactériologie est zéro — absence exigée — et la « LQ » d'un dénombrement vaut 1,
puisqu'on ne compte pas une demi-bactérie. Aucune LQ ne peut passer sous zéro.
Sans cette garde, **69 mesures** du corpus au 8 août 2026 étaient déclarées hors
de portée du laboratoire alors qu'elles sont parfaitement lisibles, et elles
noyaient les **46 cas réels**. La garde vaut pour `lq_aveugle` comme pour
`indetermine_strict` ; elle ne vaut pas pour `depasse_strict`, car trois
entérocoques pour 100 mL franchissent bel et bien une exigence d'absence.

Sur `indetermine_strict`, le corpus n'y échappait que **par accident** : les
libellés de la source — « Escherichia coli /100ml - MF », « Entérocoques
/100ml-MS » — ne rejoignent aucune ligne du référentiel, si bien que
`seuil_strict` y reste vide. Il aurait suffi d'un alias, c'est-à-dire de
l'entretien courant, pour que 69 mesures basculent en « indéterminé » sans que
rien n'ait changé dans l'eau. Une règle qui ne tient que par une lacune du
catalogue n'est pas une règle.

**Les deux ensembles se recouvrent, et on les compte au lieu de les supposer.**
Les 46 mesures aveugles sont toutes parmi les 55 indéterminés — un paramètre
dont la LQ dépasse la limite réglementaire dépasse a fortiori le repère plus
strict, quand il en existe un. Les additionner annoncerait 101 problèmes là où
il y en a 55, ce qui serait exactement l'arithmétique dont le projet fait le
reproche au reste du monde. Rien n'interdit pourtant qu'un paramètre sans repère
strict soit aveugle sans être indéterminé : le recouvrement se mesure sur les
lignes, il ne se déduit pas des compteurs.

**Enfin, on n'accuse pas le laboratoire.** Une LQ élevée est une capacité
d'instrument, pas une négligence — le §2.1 vaut ici comme ailleurs : on examine
ce que le dispositif permet de savoir. Et parce que la référence se déplacera
avec le corpus, tout barème affiche sa base : c'est le §2.14 transposé à
l'instrument, le plus fin **identifié**, jamais le plus fin qui existe.

---

## 2.5 Un seuil sans sa date d'applicabilité est faux

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

---

## 2.6 Distinguer statut réglementaire et statut scientifique

Deux colonnes distinctes, jamais fusionnées : `pe_reglementaire` et
`pe_scientifique`.

Un perturbateur endocrinien reconnu par la littérature scientifique n'est
pas nécessairement reconnu comme tel par la réglementation. **Dans l'eau
destinée à la consommation humaine, le seul PE avéré au sens réglementaire
UE est le bisphénol A** (limite 2,5 µg/L depuis 2023). Écrire qu'un
pesticide « est un perturbateur endocrinien » sans préciser le registre
est une faute vérifiable qui décrédibilise l'ensemble.

Ce garde-fou est complété par le §2.15, qui porte le registre manquant :
la cancérogénicité.

---

## 2.7 Toute affirmation chiffrée est sourcée ou marquée

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

---

## 2.8 Une conformité sans son dénominateur est une demi-vérité

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

---

## 2.9 Un seuil et une mesure dans deux unités différentes ne se comparent pas

Erreur réellement présente et détectée par le contrôle croisé : le chlorate
était au référentiel en 0,25 mg/L et mesuré en µg/L. La comparaison directe
se trompait d'un facteur 1000.

Les seuils sont désormais convertis vers l'unité de la mesure avant toute
comparaison. Quand les deux unités sont connues, différentes et non
convertibles, **aucun verdict n'est produit** — la mesure est listée dans
`v_unites_incomparables`. Un verdict faux est pire qu'un verdict absent.

---

## 2.10 Un verdict se rend à la date du prélèvement

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

---

## 2.11 L'effort de recherche est un indicateur, et il se déclare

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

Seconde règle de sortie, ajoutée le 8 août 2026 sur instruction de Yannick
(chantier C5) : **une comparaison de territoire nomme la zone, et cette zone
est une zone dont le corpus détient les bulletins.**

> « Il faut éviter de faire des comparaisons avec d'autres agglomérations, ou
> du moins les nommer (exemple mieux que l'agglomération chartraine qui est
> citée car on a des résultats de cette zone). »

Pas de « ailleurs », pas de « le voisinage », pas de « les grands réseaux »,
pas de « plusieurs communes » : ce sont des affirmations qu'aucun lecteur ne
peut vérifier ni contredire, et elles sont d'autant plus tentantes qu'elles
ne coûtent aucune donnée. La règle précédente s'applique à chaque terme
nommé — la zone est nommée **et** son effort de recherche est affiché.

Le nom se prend dans la base, il ne s'invente pas : **`nom_uge` porte le
gestionnaire déclaré par la source** — « CHARTRES METROPOLE », « SME LEVEZOU
SEGALA » — et `dept` porte le département. Une zone désignée par ces colonnes
est nommée, sourcée, et ses bulletins sont dans le corpus par construction.

Nommer la zone n'est pas une politesse d'écriture, c'est ce qui oblige à
aller lire les bulletins. **Trois erreurs de fait sont tombées le jour où on
l'a fait**, et aucune n'était visible tant que le terme de comparaison restait
flou : un « panel le plus étroit » que Challet partageait à l'identique, un
écart d'effort sous-estimé — 370 paramètres dépassent *chacun* des douze
bulletins de Chartres Métropole, pas « plusieurs » —, et une progression des
performances analytiques dans le temps que le plus ancien bulletin du Tarn
contredit. Le flou ne protégeait pas de l'erreur : il la cachait.

`tests/test_sorties.py` en tient le contrôle n° 8. Il constate qu'une zone est
nommée ; il ne peut pas constater qu'elle est la bonne, ni que l'effort de
chaque terme est affiché. Cette relecture-là reste humaine.

---

## 2.12 Le seuil de 2016 des métabolites est une extrapolation, et il se dit

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

---

## 2.13 Un seuil peut dépendre du procédé ou de la ressource, pas seulement de la date

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

### Un reclassement déplace deux choses, pas une

*(établi le 10 août 2026, sur les textes)*

Cinquième cas, de même nature que les quatre du tableau : ce qui commande le
verdict n'est pas la valeur mesurée. La condition n'est ici ni le procédé ni la
ressource, c'est le **statut de la substance** — et elle joue sur deux verdicts
à la fois, dont un seul est opposable.

**1. Le « total pesticides » est une somme de limites de qualité.** L'arrêté du
11 janvier 2007 modifié, dans sa rédaction issue de l'arrêté du 30 décembre
2022 — annexe I, « Limites et références de qualité, valeurs indicatives et
valeurs de vigilance des eaux destinées à la consommation humaine » — fixe le
total à 0,50 µg/L et le définit comme « la somme de tous les pesticides
individuels quantifiés » [REG-06]. L'instruction DGS/EA4/2020/177 porte la même
définition : « Par "total pesticides", on entend dans la réglementation
relative aux EDCH la somme de tous les pesticides individualisés détectés et
quantifiés » [REG-05]. Ce que recouvre « pesticides » est borné dans la même
note : les familles organiques énumérées « ainsi que leurs métabolites,
produits de dégradation et de réaction **pertinents** ». Un métabolite n'entre
donc dans le périmètre de la somme que s'il est pertinent — « jugé pertinent
[…] s'il y a lieu de considérer qu'il possède des propriétés intrinsèques
comparables à celles de la substance mère en ce qui concerne son activité cible
pesticide ou qu'il fait peser […] un risque sanitaire pour les consommateurs »
[REG-06].

**2. Les non pertinents relèvent d'une autre partie du même texte.** Partie III
de l'annexe I, « Valeurs indicatives » : « Métabolites de pesticides non
pertinents, par substance individuelle | 0,9 | µg/L », après évaluation de
l'ANSES [REG-06]. Une valeur indicative n'est pas une limite de qualité : elle
ne fonde ni non-conformité ni dérogation. L'ARS Bourgogne-Franche-Comté le dit
dans les mêmes termes : « Les métabolites non pertinents ne sont pas soumis à
la limite de qualité de 0,1 µg/l, et ne sont pas inclus dans le paramètre somme
des pesticides » [REG-08].

**3. Donc un reclassement fait tomber deux verdicts.** Le jour où un métabolite
passe de pertinent à non pertinent, il quitte **sa propre limite** — 0,1 µg/L,
opposable — pour une valeur indicative de 0,9 µg/L qui ne l'est pas ; et il
quitte **le dénominateur du total**. À composition d'eau strictement inchangée,
deux lignes du bulletin changent de sens le même jour. Le §2.10 s'applique
entier : le verdict se rend à la date du prélèvement, le reclassement n'est pas
rétroactif.

**Ce qu'il faut en faire en sortie.** Une somme « total pesticides » ne se
compare à rien sans sa date et son périmètre : deux totaux calculés de part et
d'autre d'un reclassement ne portent pas sur la même liste de substances. Le
corpus contient des analyses où un métabolite reclassé figure encore dans le
total : c'est un **écart constaté, de cause inconnue** — somme calculée avant le
reclassement, chaîne de transmission, périmètre retenu par le laboratoire ; rien
dans les données ne permet de trancher, et cela ne vaut reproche à personne
(§2.1). Cela ne dit rien non plus de la qualité de l'eau : cette page décrit ce
que la norme fait, pas ce que l'eau vaut. Les dénombrements sont dans
`data/dossiers/SUBSTANCE-chlorothalonil-r471811.md`, qui fait foi — ne pas les
recopier ici, deux copies d'un chiffre divergent à la première recollecte.

**Fiabilité, au 10 août 2026.** Les citations de l'instruction sont vérifiées
sur le fichier archivé [REG-05], celle de l'ARS sur la page archivée [REG-08].
Celles de l'arrêté ont été **lues en ligne, sur un texte non archivé** : le PDF
consolidé n'a pas pu être téléchargé (Légifrance répond 403), la ligne [REG-06]
reste `a_verifier` et toute sortie publique qui s'y appuie doit le dire (§2.7).
Non lus à ce jour, et donc non invoqués ci-dessus : l'annexe I partie B de la
directive (UE) 2020/2184 [REG-01], le guide « Pesticides et métabolites dans
les EDCH » de juillet 2024, l'avis du HCSP du 16 janvier 2025. La chaîne
française suffit à établir les trois points ; elle ne dispense pas de les
confirmer sur la source européenne avant de la citer.

**Un cas reste ouvert** : celui du métabolite **dont la pertinence n'a pas
encore été évaluée**. La valeur de 0,9 µg/L de la partie III est attachée à une
évaluation de l'ANSES, et la règle par défaut de l'instruction (§2.12) range
l'inconnu du côté pertinent — l'articulation exacte des deux n'a pas été
vérifiée sur le texte du guide annexé. Ne pas trancher, marquer `a_verifier`.

---

## 2.14 « Le plus strict identifié », jamais « le plus strict au monde »

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

---

## 2.15 Trois registres, jamais fusionnés

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

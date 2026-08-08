# Architecture — ce qui a été construit, et pourquoi ainsi

Ce document porte les **décisions de construction** du dépôt : le schéma de base
dans le détail, la séparation atelier / vitrine, l'origine de la prose, le
circuit de publication et les indicateurs de la fiche.

`CLAUDE.md` n'en garde que les règles qui doivent tenir en mémoire à chaque
session (§4 pour le schéma, §8bis pour les obligations d'affichage). **Ce
fichier-ci est la référence** pour tout le reste : quand une décision
d'architecture est remise en cause, c'est ici qu'on vient lire *pourquoi* elle a
été prise — la plupart le sont après un défaut réel, et les défauts sont écrits.

Déplacé depuis `CLAUDE.md` le 8 août 2026, sans modification du texte.

---

## 1. La fiche sépare le factuel de la prose

`sortie/build_fiche.py` dérive de la base **tout ce qui est factuel** :
mesures, seuils, verdicts, couverture, effort de recherche, conclusion de
l'ARS. Chaque fiche porte la version de référentiel et la date de calcul qui
l'ont produite.

**La prose porte toujours son origine.** Règle révisée le 8 août 2026 sur
instruction de Yannick : la prose *peut* être générée, elle ne peut jamais être
anonyme. Voir §4 ci-dessous — trois origines (`auteur`, `propose`, `derive`), une
préséance stricte, et chaque section affiche la sienne.

C'était la dernière partie non traçable du dépôt : les chiffres y étaient
écrits en dur à côté des textes.

## 2. La sortie est figée, mais toujours estampillée

La mesure ne change jamais : c'est un fait. Le verdict, lui, dépend du
référentiel — et le sujet du projet est que les seuils bougent. Figer un
« conforme » sans dire contre quelle grille il a été calculé reproduirait, à
l'intérieur de l'outil, le défaut que l'outil dénonce.

Chaque ligne figée porte donc `version_referentiel` — empreinte du CONTENU des
fichiers du référentiel, pas un commit git : une modification non commitée doit
rester identifiable — et `calcule_le`. Refiger après modification produit une
nouvelle version ; les deux coexistent, et leur comparaison est la trace du
déplacement.

## 3. Le référentiel est un fichier versionné, pas du code

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

## 4. L'atelier et la vitrine sont deux objets distincts

Chantier web ouvert le 7 août 2026. Trois décisions structurantes, à ne pas
défaire sans raison.

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

## 5. La prose et son origine

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

## 6. Le circuit de travail, et la clé de la prose

### Quatre étapes, et la troisième s'oublie

```
1. COLLECTER  →  2. FIGER  →  3. PUBLIER  →  4. RÉDIGER
   (réseau)      (automatique)  (un geste)     (proposé, puis validé)
```

**Collecter et figer ne font qu'un** : `observer.py` enchaîne jusqu'au figeage.
**Publier est un geste séparé, et c'est lui qui fabrique les pages.** Erreur
réellement commise le 8 août 2026 : 28 communes collectées et figées, sans
page, donc invisibles pour tout visiteur — et rien ne le signalait. La page
d'état de l'atelier affiche désormais les quatre étapes et ce qui est en retard
sur quoi.

### La prose s'indexe par POINT D'EAU

`sortie/redactions.json` et `redactions_proposees.json` acceptent trois formes
de clé, de la plus précise à la plus générale :

| Clé | Portée |
|---|---|
| `28068@2026-03-10` | cette commune, ce prélèvement |
| `28068` | cette commune, tous ses prélèvements |
| `PREL:08100134523` | **ce point d'eau** — partagé par toutes les communes qu'il alimente |

La clé `PREL:` répond à un fait de terrain : le traitement du Moulin Galat
alimente **huit** communes. Écrire huit fois le même texte serait absurde, et
les huit versions divergeraient à la première correction. Sur 60 communes
couvertes, il n'y a que 45 bulletins.

Indexée sur `code_prelevement` et non sur `code_installation_amont`, vide sur
un tiers des bulletins — et parce qu'un texte citant une valeur décrit un
prélèvement daté, pas une installation en général.

### Rédiger en lot — le script tient les deux bouts, pas le milieu

Les 45 premiers bulletins ont été rédigés dans une conversation, un par un. À
l'échelle d'un département ce n'est plus tenable, et la raison est
arithmétique : chaque bulletin repaie le contexte accumulé par les précédents,
donc le coût croît en N², la session sature, et rien n'est rejouable.

Le levier n'est **pas** de sortir du canal — la rédaction reste dans Claude
Code, où le travail est déjà payé. Un premier `sortie/rediger_lot.py` avait été
écrit pour l'API Batch avec une clé facturée à part : mauvais canal, refait le
8 août 2026. Le levier est la **découpe**, et `rediger_lot.py` la porte :

| Étape | Qui la tient |
|---|---|
| choisir les bulletins sans prose | le script |
| fabriquer le dossier de faits de chacun | le script |
| **écrire le texte** | **un agent de fond Claude Code, un par dossier** |
| contrôler ce qui revient | le script |
| intégrer dans `redactions_proposees.json` | le script |

Un agent par bulletin repart d'un contexte neuf : N agents = N contextes
complets, aucun n'hérite du précédent, et le coût redevient linéaire.

**La consigne est un fichier versionné**, `sortie/CONSIGNE_REDACTION.md`, et non
un prompt enfoui dans du Python. Ce qu'on demande au modèle est une décision
éditoriale, au même titre qu'un seuil : git en tient le journal daté.

**Le dossier de faits est construit entièrement par requête** — bulletin,
effort, verdicts, lignes notables, série des autres bulletins de la commune, et
le texte déjà dérivé pour que l'agent ne le répète pas. Le rédacteur n'a le
droit de citer aucun chiffre absent de ce dossier. Donc ce qui manque là ne sera
pas écrit, et ce qui y est faux le sera : c'est la seule surface à vérifier.

**Le contrôle au retour est la raison d'être du fichier.** Un texte proposé par
un modèle entre dans un projet dont toute la valeur est la vérifiabilité : il
est donc contrôlé avant d'être écrit, pas seulement au moment de publier. Les
règles §2.2 et §2.11 sont celles de `tests/test_sorties.py`, **importées et non
recopiées** — deux copies d'un même garde-fou divergent à la première retouche,
et l'écart ne se voit pas. S'y ajoutent les affirmations d'absence (§2.4), les
qualificatifs sanitaires, le mot « risque » sur l'indice de danger (§7.1), et
surtout : **tout nombre décimal absent du dossier bloque l'intégration.** C'est
le contrôle le plus utile — il attrape la valeur inventée, la conversion d'unité
faite de tête et le seuil recopié de mémoire, c'est-à-dire les trois façons dont
ce projet s'est déjà trompé, par la main humaine comme par la machine.

Deux défauts trouvés en éprouvant ce contrôle sur une réponse fautive fabriquée
exprès : les champs de prose étaient recollés sans ponctuation terminale, si
bien qu'un nom propre du `sous_titre` faisait passer pour « nommée » une
comparaison anonyme du `delta` ; et « la plupart des communes » manquait à la
liste partagée des comparaisons vagues, qui connaissait « plusieurs » et
« certaines ».

Le journal de reprise n'est pas un fichier à part, ce sont les deux fichiers de
prose eux-mêmes — un point d'eau déjà servi par une clé `INSEE@date`, `INSEE` ou
`PREL:` est sauté. Même idempotence que la collecte Hub'Eau, même conséquence :
on relance un lot interrompu sans précaution.

Le script écrit dans `redactions_proposees.json` et **jamais** dans
`redactions.json`. La préséance ci-dessus est un ordre de confiance : la main de
Yannick ne se surcharge pas depuis un script.

### Valider, commenter, ou ne rien faire

L'onglet **Valider** de l'atelier porte les trois gestes. Un **commentaire**
(`_commentaire` dans le fichier des propositions) vaut « pas encore » : la
proposition passe « à revoir », sa case se décoche, et « tout valider »
l'ignore en le disant. Les commentaires ne sont jamais publiés — `fusionner()`
ne connaît que les champs de prose, et un champ préfixé par un souligné n'en
fait pas partie.

### L'atelier lance des sous-processus

Un serveur Python garde en mémoire le code chargé à son démarrage. L'atelier
étant lancé une fois et laissé ouvert, une collecte déclenchée après une
modification de `src/` s'exécutait avec l'**ancien** code — un figeage a ainsi
reconstruit `verdicts_figes` sans trois colonnes ajoutées le matin même, en
silence. Collecte et publication passent donc par des sous-processus. **Ne pas
revenir à un appel en direct.**

La publication enchaîne quatre étapes et la dernière est le contrôle :
refiger → vitrine → fiche → `tests/test_sorties.py`. Publier sans vérifier
serait exactement ce que l'outil reproche au reste du monde.

---

## 7. Les indicateurs de la fiche

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

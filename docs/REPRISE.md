# Reprise — état au 8 août 2026

> **9 août 2026 — l'Eure-et-Loir (28) est collecté en entier, 363/363
> communes, zéro erreur réseau.** `--termine` rend 0. Deuxième département
> complet du corpus, après le Tarn. Chiffres et suites : §10 en bas de fichier.
>
> **Le verrou DuckDB était la contrainte d'ordonnancement du projet — levé le
> 11 août 2026.** `fetch_departement.run()` tenait une connexion
> lecture-écriture ouverte de bout en bout : pendant une collecte
> départementale — deux heures et plus — **aucun autre processus ne pouvait
> ouvrir la base, même en lecture seule**. La collecte est désormais coupée en
> deux gestes, `src/moisson.py` (réseau, parallèle, base jamais ouverte) et
> `src/ingerer.py` (base prise quelques minutes, puis rendue). Voir §15 en bas
> de fichier. `fetch_departement.py` reste tel quel pour un département isolé,
> et l'avertissement ci-dessus vaut encore **si on l'emploie** : dans ce cas,
> ce qui reste faisable en parallèle est **rédiger**, à condition d'avoir
> fabriqué les dossiers de faits AVANT de lancer la collecte. Les agents ne
> lisent alors que `data/dossiers/PREL-*.md` et écrivent dans
> `data/dossiers/reponses/`. Seul `--integrer` attend la fin.

Document de passage de main entre deux sessions. **`CLAUDE.md` reste la
référence** : il porte la méthode, les garde-fous et les décisions
d'architecture, et il est relu automatiquement au début de chaque session. Ce
fichier-ci ne dit que ce que `CLAUDE.md` ne peut pas dire : l'état du chantier
à cet instant, et ce qui attend une décision.

> **Depuis ce passage de main**, la reprise a eu lieu et plusieurs points du §4
> sont tranchés. Ce qui est décidé, lancé ou gelé vit désormais dans
> `docs/CHANTIERS.md`, qui fait foi en cas de désaccord avec ce fichier :
> les 45 propositions sont validées, la clé de Challet est corrigée, le corpus
> est confirmé et destiné à croître, et le journal des abandons de paramètres
> est construit.
>
> **Mise à jour du 8 août 2026, en soirée.** Trois commits sont arrivés depuis :
> C4 + C5 + C7 livrés d'un bloc, `sortie/rediger_lot.py` écrit, et `CLAUDE.md`
> ramené de 1 246 à ~400 lignes. Les §1, §4.1 et §4.3 ci-dessous ont été
> corrigés en conséquence. **Le chantier C6 — ÉCHELLE est en cours** : voir
> `docs/CHANTIERS.md`.

---

## 1. Où en est le dépôt

**Branche `chantier-interface`**, 16 commits en avant de `master`, arbre de
travail propre. `master` est intact et n'a pas été touché.

```
1d2e186  docs: CLAUDE.md ramené à sa charge utile, l'argumentaire en documents appelés
66ec049  feat: rédiger en lot — dossiers de faits, et contrôle avant intégration
6a9bd6e  feat: le plafond analytique, les territoires nommés, le mélange dénombré
029d7d3  docs: passage de main — etat du chantier, circuit de travail, corpus reimportable
4b1b141  feat: commenter une proposition plutot que la valider ou la jeter
d5d997d  feat: une page pour relire et valider les redactions proposees
e733fa2  feat: une redaction par POINT D'EAU, et les 45 bulletins rediges
1d774ee  fix: l'atelier lance des sous-processus, et montre ou en est chaque commune
5e912c9  docs: architecture de l'interface, origine de la prose, indicateurs
67eefa2  test: controle des sorties publiees, avec asymetrie sur le garde-fou §2.2
c46cec1  feat: l'atelier — le poste de pilotage local, qui ne se publie jamais
f33e1b0  feat: la vitrine publique statique, avec sa carte et sa recherche
ff53afa  feat: la fiche — indicateurs, jauge du reetalonnage, origine de la prose
431a769  feat: collecte pilotee par un fichier CSV, et lecture des references encadrees
2fa1b40  fix: ce qui disparaissait au figeage — verdict a la date, repere strict, couverture
7eb8687  ref: alias du total des pesticides, longueurs de chaine PFAS, indicateurs
```

Rien n'est poussé : il n'y a pas de dépôt distant configuré.

Pour fusionner : `git checkout master && git merge chantier-interface`

---

## 2. Ce que contient la base

`data/eau.duckdb` n'est **pas versionnée** et se reconstruit. État actuel :

**État au 8 août 2026 — le Tarn est collecté en entier, 314 communes sur 314,
zéro erreur. Tout est figé.**

| | | était au passage de main |
|---|---|---|
| version de référentiel | `3a66a7b928d0` | inchangée |
| prélèvements figés | **1 595** | 45 |
| mesures | **684 883** | 15 617 |
| communes couvertes | **339** — 143 analysées, 196 rattachées au réseau | 60 |
| départements | 15, 17, 22, 28, 46, 69, **81 (entier)**, 82 | idem |
| bulletins conformes 2026 **avec bascule** | **109** | 8 |
| — dont conformes *à la date du prélèvement* (§2.10) | **63** | 8 |
| installations à plusieurs bulletins | **165**, dont 76 à ≥ 5 | **0** |
| mesures aveugles (§8bis n° 11) | **1 316** sur 1 143 bulletins | 46 sur 39 |
| cache brut `data/brut/81/` | 1 575 bulletins, **32,4 Mo** | — |

Le corpus a été multiplié par 35 en bulletins et par 44 en mesures. **Les deux
chiffres de la thèse ne se lisent pas de la même façon** : 109 est la requête
canonique du §6 (`nb_depasse_2026 = 0`), 63 applique le verdict à la date du
prélèvement (`nb_depasse_applicable = 0`), qui est le seul comparable à la
conclusion de l'ARS et donc le plus prudent. Publier le premier sans le second
serait un faux positif de 46 bulletins.

### Ce qui a été trouvé, et qui attend une suite

**Le panel du Tarn s'effondre de 606 à 352 paramètres entre 2019 et 2020**, à
installation constante (−40 % sur 135 installations suivies, 132 en baisse sur
135), avec une rupture nette entre décembre 2019 (585) et janvier 2020 (324).
C'est le premier motif rendu par le chantier C2, il a une date, et il reste un
**dénombrement** : rien dans les données ne dit la cause. Détail et contrôles
dans `docs/CHANTIERS.md` §C2.

*Yannick indique avoir documenté ce point dans un autre fil — la cause et sa
source restent à reporter ici.*

### Refaire ou reprendre une collecte départementale

```bash
py -X utf8 -u src/fetch_departement.py --dept 81 --tous
```

Idempotente et reprenable : le journal `data/journal/dept_81.jsonl` porte une
ligne par commune, refermée à chaque fois, et le cache brut évite de redemander
un bulletin déjà obtenu. Trois filets :

- `--termine` — code de sortie 0 si le département est entièrement traité.
  **Une commune en erreur compte comme restant à faire** (corrigé le 8 août 2026
  après que neuf échecs réseau ont failli passer pour des communes traitées) ;
- `--figer` — fige ce qui est collecté, sans réseau ;
- `--reingerer` — rejoue tout le cache brut dans la base, sans un seul appel
  réseau, si `data/eau.duckdb` est abîmée ou reconstruite ;
- `--rapport` — la couverture du département, sans rien collecter.

**Ne pas lire `data/journal/collecte_81.log`** pour suivre l'avancement sans
`-u` : Python tamponne sa sortie quand elle est redirigée. C'est `--termine` et
`--rapport` qui disent la vérité, parce qu'ils lisent le journal.

### Avant de republier — trois choses, dans cet ordre

1. **`tests/test_sorties.py` échoue : 339 communes couvertes, 279 sans page.**
   Ce n'est pas une régression, c'est le contrôle qui fonctionne — publier est
   un geste séparé de collecter (§8quater bis). Il faut publier pour l'éteindre.
2. **Tous les barèmes de LQ déjà publiés ont changé de base** — de 29 à 1 595
   bulletins (§2.14). Les fiches existantes affichent une base périmée.
3. **`v_parametres_non_apparies` passe de 103 à 118 libellés.** Un paramètre
   sans seuil existe en base et ne pèse sur aucun verdict : à relire avant de
   publier un département entier.

**La base se reconstruit entièrement**, et deux listes versionnées permettent
de choisir quoi restituer :

```bash
python3 src/build_db.py

# le corpus du livre seul — 7 communes
python3 src/observer.py --csv data/communes_a_collecter.csv

# le corpus tel qu'il est aujourd'hui — 60 communes
python3 src/observer.py --csv data/corpus_actuel.csv
```

`data/corpus_actuel.csv` a été écrit exprès pour ce passage de main : les 53
communes hors livre (Chartres Métropole, secteur de Cordes-sur-Ciel, Ségala
tarnais) avaient été collectées à la main depuis l'atelier et ne figuraient
dans aucune liste. Sans ce fichier, une reconstruction les aurait perdues.

---

## 3. Ce qui est construit

```
site/          la vitrine statique — accueil, carte, communes, méthode, sources,
               une page par commune. `site/public/` est un PRODUIT, non versionné.
atelier/       le poste de pilotage local, 127.0.0.1:8760, jamais publié
sortie/        la fiche autonome (un fichier), la prose, les indicateurs
tests/         trois suites : moteur, sortie figée, sorties publiées
```

Lancer :

```bash
python3 atelier/atelier.py                  # tout se pilote de là
python3 -m http.server 8765 -d site/public  # relire la vitrine
```

Les trois suites de tests passent. `tests/test_sorties.py` contrôle ce qui est
réellement publié et doit être lancé après chaque publication — c'est d'ailleurs
la quatrième étape du bouton « Publier ».

---

## 4. Ce qui attend une décision de Yannick

### 4.1 Les 45 propositions de rédaction — validées

**Fait.** `sortie/redactions.json` porte désormais **52 clés** : 45 `PREL:`
(les propositions validées), 6 codes INSEE et 1 `INSEE@date` — la clé de
Challet corrigée. `sortie/redactions_proposees.json` est vide (il ne garde que
son `_lisez_moi`), et **aucun bulletin n'est sans prose** :

```bash
py -X utf8 sortie/rediger_lot.py --etat
```

La machinerie de rédaction en lot est écrite depuis (`sortie/rediger_lot.py`,
consigne versionnée dans `sortie/CONSIGNE_REDACTION.md`) : elle choisit,
fabrique les dossiers de faits, **contrôle avant d'écrire**, et n'appelle
aucune API — la rédaction se fait par agents de fond dans Claude Code.

### 4.2 Deux points signalés, non corrigés

**La fiche de Challet s'applique à ses deux bulletins.** Le texte de Yannick
décrit celui de 2026 — « chlorothalonil à 1,662 µg/L » — et s'affiche aussi
sous celui de 2022, où cette valeur n'existe pas. Correction : renommer la clé
`"28068"` en `"28068@2026-03-10"` dans `redactions.json`. Le bulletin de 2022
retombera alors sur la proposition écrite pour lui, qui parle des perchlorates
et de l'avis nourrissons. **Non fait : c'est son fichier.**

**Le « charbon actif » de Vourles.** `tests/test_sorties.py` signale, dans une
section de sa main, la phrase « précisément celles que le charbon actif retient
mal ». Elle contrevient au §2.2, qui interdit toute mention d'un équipement.
Le contrôle est volontairement **non bloquant** pour la prose d'auteur : un
outil qui censure son auteur ne serait pas un garde-fou. **La décision lui
revient.**

### 4.3 Le corpus lui-même — tranché

**On garde tout, et le corpus a vocation à croître d'un ordre de grandeur.**

> « mon idée est d'avoir plusieurs milliers de communes, pour avoir une data
> significative. Je construis un outil citoyen. »

C'est le chantier **C6 — ÉCHELLE**, en cours, qui commence par le **Tarn**.
Quatre décisions prises le 8 août 2026 : tous les bulletins complets de chaque
point d'eau sans borne de date ; un cache brut sur disque pour que la base se
reconstruise sans retoucher Hub'Eau ; prose dérivée partout, proposée seulement
sur les cas de thèse. Détail dans `docs/CHANTIERS.md` §C6.

---

## 5. Chantiers ouverts, par ordre d'utilité

1. **Publier pour de vrai.** `site/public/` part tel quel sur GitHub Pages,
   Netlify ou Cloudflare Pages — gratuit, HTTPS inclus. Restent à choisir
   l'hébergeur, le nom de domaine, et à décider si le dépôt de code devient
   public en même temps (le plan le recommande dès la phase 0).
2. **Relire les propositions**, puis me redemander une réécriture à partir des
   commentaires laissés dans `_commentaire`.
3. **Les indicateurs restants**, déjà proposés et non faits : perchlorates (le
   cas de Challet et Clévilliers, avec l'avis nourrissons), métaux (plomb,
   nickel, arsenic), volet radiologique (tritium et dose indicative, mesurés
   sur 21 bulletins mais jamais quantifiés), et un indicateur composite
   « somme des métabolites de chlorothalonil » qui rendrait lisible d'un coup
   la saturation du secteur chartrain.
4. **Un département entier.** `fetch_departement.py` est prêt et n'a jamais
   servi en entier. Cela donnerait enfin une carte avec ses trous — et des
   communes « non documentées », qui n'existent aujourd'hui que dans les tests.
5. **La carte n'a pas les DOM.** Le fond départemental s'arrête à la métropole.

---

## 6. Pièges rencontrés, à ne pas refaire

- **L'atelier tourne avec le code chargé à son démarrage.** Corrigé par des
  sous-processus (cf. `CLAUDE.md` §8quater bis). Ne pas revenir en arrière.
- **Publier est un geste séparé de collecter.** 28 communes sont restées
  invisibles à cause de cela.
- **Deux versions de référentiel figées le même jour ne se départagent pas par
  une date.** `version_a_publier()` interroge l'empreinte du référentiel actuel.
- **`CREATE TABLE IF NOT EXISTS` ne dit rien quand la table existe avec
  d'autres colonnes.** `figer.assurer_schema()` compare et reconstruit.
- **Le CSS reste en cache d'une publication à l'autre.** Les ressources portent
  l'empreinte de leur contenu.
- **PowerShell et bash ne partagent pas la syntaxe des chaînes multilignes.**
  Les here-strings `@'…'@` passés à bash finissent dans le message de commit.
- **Python n'est accessible que par `py`** sur cette machine, pas `python` ni
  `python3`. Avec `-X utf8`, sans quoi les accents cassent la sortie.

---

## 7. Ce qui a été trouvé dans les données, et qui mérite d'être exploité

Ces constats sont dans les rédactions proposées, mais ils dépassent la fiche :

- **Le chlorothalonil sature le secteur chartrain.** Neuf bulletins, neuf
  valeurs de R471811, **toutes** au-dessus de la limite de 2016. La frontière
  entre non-conforme et conforme passe au milieu du nuage, à une valeur fixée
  en avril 2024. C'est la démonstration la plus massive du réétalonnage dans
  le corpus, et elle mériterait sa propre page.
- **Marnaves** : sulfates ET nitrates au-dessus de leur repère nourrissons,
  aucune non-conformité. Le cas le plus net de l'écart entre deux référentiels
  pour la même eau.
- **Vourles** : cinq PFAS à chaîne courte quantifiés pour une masse trois fois
  supérieure aux trois chaînes longues — et les courtes n'entrent dans aucun
  total réglementaire opposable hormis la somme de 20.
- **Boissezon** : 627 paramètres en 2019, 369 en 2024. L'effort de recherche
  divisé par deux, sans que rien n'indique une dégradation de l'eau.
  **La cause est trouvée — 9 août 2026** : instruction n° DGS/EA4/2020/177 du
  18 décembre 2020, fiche `REG-05` (`Sources/REG_Reglementation_et_seuils/REG-05_FR_instruction-DGS-2020-177_listes-pesticides.md`).
  Voir ci-dessous §8.

---

## 8. Mise à jour du 9 août 2026 — ⚠️ PÉRIMÉ, conservé comme trace de l'hypothèse

> **Ne pas lire cette section comme l'état courant.** Le §9.1 ci-dessous la
> corrige sur son point central : l'instruction invoquée est postérieure de onze
> mois à la rupture qu'elle est censée expliquer. Le titre d'origine était « la
> chute du panel a une cause réglementaire » ; elle a un **mécanisme** plausible,
> pas une cause établie.

Le motif « ~600 paramètres en 2019, ~300 en 2020 » observé dans le Tarn n'est pas
un artefact de collecte : c'est l'**instruction n° DGS/EA4/2020/177 du
18 décembre 2020** et son guide technique, qui remplacent le balayage de toutes
les molécules analysables par une **liste régionale de pesticides et métabolites
arrêtée par l'ARS**, ciblée « en fonction de la probabilité de les retrouver ».
La bascule se fait au renouvellement des **marchés pluriannuels d'analyses** des
ARS, d'où une rupture nette d'une année civile à l'autre. Ordres de grandeur
repris du guide : PACA ~600 → 150 molécules ; Grand Est 160 substances actives +
42 métabolites.

**Ce qui a été écrit** (aucune donnée touchée, aucun test relancé — ce sont des
documents) :

| Fichier | Ce qui y a été ajouté |
|---|---|
| `Sources/REG_Reglementation_et_seuils/REG-05_FR_instruction-DGS-2020-177_listes-pesticides.md` | la fiche complète : texte, calendrier, motivation officielle, critiques, sources |
| `docs/INDEX_SOURCES.md` | la ligne `REG-05` dans la section REG ; la ligne `REG-05` de la section MET renvoie désormais au même texte ; numéros libres corrigés ; **trois défauts de tenue signalés** (voir plus bas) |
| `src/etude_panel.py` | la cause en tête de docstring, avec le test qu'elle appelle et la règle de sortie |
| `CLAUDE.md` §2.11 | troisième règle : **aucune série temporelle à panel variable** |

**Trois réserves, dans l'ordre d'importance :**

1. **Le PDF officiel de l'instruction n'a pas pu être téléchargé** en session
   (circulaires.legifrance, sante.gouv). Les chiffres PACA et Grand Est viennent
   de reprises documentaires du guide, **pas d'une lecture de l'annexe**. À
   verrouiller avant toute publication (§2.7).
2. **Le test de confirmation sur le Tarn n'a pas été lancé.** Il est écrit en
   §4 de la fiche : lister les `code_parametre` présents en 2019 et absents en
   2020, vérifier qu'ils sont bien majoritairement pesticides/métabolites, et
   dater la bascule au mois près. Une coupure franche = changement de marché ;
   une décroissance progressive = effet d'échantillonnage. **Tant qu'il n'est
   pas fait, la cause est plausible et sourcée, pas démontrée sur nos données.**
   **À n'exécuter qu'une fois la collecte du Tarn terminée** (consigne de
   Yannick, 9 août 2026) : `data/eau.duckdb` est en cours d'écriture, DuckDB
   n'admet qu'un seul écrivain, et un panel mesuré sur 26 communes sur 314
   n'aurait de toute façon pas le même sens qu'un panel départemental complet.
   `py -X utf8 src/fetch_departement.py --dept 81 --termine` dit où en est la
   collecte.
3. **`docs/INDEX_SOURCES.md` a trois défauts de tenue** constatés au passage et
   volontairement non corrigés, parce qu'ils demandent une décision de
   renumérotation : `PFAS-07` et `PE-05` désignent chacun deux documents
   différents ; `RAD-01` et `CIRC-01` sont rangés dans la section MET ;
   `REG-06` et `REG-07` sont catalogués sans fichier sur le disque.

Deux facteurs à ne jamais confondre avec la cause principale : le **Covid**
(baisse du nombre de *prélèvements* en 2020, pas du nombre de *paramètres*) et
l'**effet d'échantillonnage** (le nombre de paramètres distincts sur une année
dépend du nombre de bulletins complets réalisés cette année-là).

---

## 9. Mise à jour du 9 août 2026 — le Tarn est collecté en entier

**314 communes sur 314**, 1 575 bulletins complets du 8 janvier 2016 au
29 mai 2026. Le corpus passe de 45 à **1 595 bulletins** et de ~15 600 à
**684 883 mesures**. Couverture : 91,8 % des mesures notées. La chaîne est à
jour de bout en bout — 339 pages publiées pour 339 communes couvertes, le piège
« collecté et figé mais pas publié » n'est pas là.

### 9.1 Le test réservé au §8 a été exécuté — le §8 est infirmé sur sa date

Le §8 ci-dessus attribuait la chute du panel à l'instruction
**DGS/EA4/2020/177 du 18 décembre 2020**, en réservant le test de confirmation
à la fin de la collecte. **Il est fait, et la section C2 de `docs/CHANTIERS.md`
en est désormais le document de référence** — elle va bien au-delà de ce test et
ses chiffres font foi. Ne pas recompter ici : s'y reporter.

Ce qu'il faut retenir au niveau de ce fichier :

- la coupure est **franche et datée de janvier 2020** — 585 paramètres en
  décembre 2019, 324 en janvier, la signature d'un renouvellement de marché ;
- elle porte **quasi exclusivement sur des pesticides** ;
- **l'instruction invoquée est postérieure de onze mois.** Au 18 décembre 2020,
  le basculement du Tarn était déjà entièrement acquis. Elle ne peut pas l'avoir
  causé.

**Conséquence : ne plus écrire que la chute du panel est causée par
DGS/EA4/2020/177.** Une cause plausible n'est pas une cause établie (§2.7).
Le §8 ci-dessus est conservé tel quel, comme trace de l'hypothèse, mais il est
**périmé sur ce point** ; C2 porte la lecture à jour — dont le fait, plus
intéressant, que le panel **n'a pas rétréci, il a tourné**.

### 9.2 La thèse, démontrée sur une décennie

**ESA métolachlore**, limite déplacée de 0,1 à 0,9 µg/L le **30 septembre 2022** :

| année | quantifiées | dépassements | bascules | max |
|---|---|---|---|---|
| 2020 | 29 | 11 | 10 | 0,956 |
| 2021 | 42 | 11 | 9 | 0,989 |
| 2022 | 43 | 7 | 7 | 0,860 |
| 2023 | 38 | 1 | 10 | 0,952 |
| 2024 | 42 | 2 | 8 | 0,943 |
| 2025 | 42 | **0** | 12 | 0,833 |

Quantifications stables, maxima stables, dépassements de 11 à zéro. Sur le
département : 135 bascules, **59 bulletins conformes aujourd'hui et porteurs
d'une bascule**, sur 15 communes. Paulinet en concentre 22.

### 9.3 Ce qui a été trouvé et qui attend une décision

**a) Le moteur ne lit pas les références de qualité déclarées.**
`seuil_2026_effectif` vaut `COALESCE(seuil du référentiel, limite_declaree)` et
**n'utilise jamais `reference_declaree`**, pourtant renseignée sur 21 029
mesures. Conséquence : **807 bulletins du Tarn où l'ARS déclare une
non-conformité et où le moteur ne voit rien** — soit un sur deux. 151 mesures
dépassent une référence déclarée sans produire aucun verdict : carbone
organique total (20, jusqu'à 3,6 pour 2), turbidité (13, jusqu'à 23 pour 2),
aluminium (8, jusqu'à 509 pour 200), radon 222 (8, jusqu'à 286 Bq/L pour 100),
bactéries coliformes (43). Question de fond, pas de code : **le projet
veut-il noter les références de qualité, et si oui les distinguer des limites ?**

**b) 79 des 172 mesures en dépassement du Tarn — 46 % — portent sur une valeur
de VIGILANCE**, pas sur une limite de qualité. *(Corrigé le 9 août 2026 : la
première rédaction disait « 79 des 135 dépassements » en rapportant un compte de
mesures à un compte de bulletins. 172 mesures, 135 bulletins.)* Le détail :
53 sur l'ESA métolachlore, 16 sur le
chlorothalonil R471811. Le référentiel le sait (`statut_2026` = `vigilance
(non pertinent depuis…)`), la fiche l'ignore et affiche « dépassement du seuil
applicable ». C'est la leçon du R417888 du §2.7, transposée : une valeur
indicative n'est pas une limite de conformité. Cinq bulletins de Paulinet le
montrent — nous prononçons un dépassement d'ESA métolachlore entre 0,912 et
0,99 µg/L là où l'ARS conclut à la conformité pleine.

**c) Accord global avec l'ARS** : sur les 135 bulletins où nous voyons un
dépassement, **130 portent une non-conformité déclarée**. L'écart est donc
concentré sur les cinq cas ci-dessus et sur les 807 du point a).

### 9.4 Une alerte que j'avais donnée, et qui était fausse

J'avais signalé « 16 faux dépassements sur les chlorites », en attribuant à un
alias manquant (`chlorite` au singulier contre `chlorites` au pluriel) la perte
du seuil conditionnel de 0,70 mg/L. **C'était faux, et la correction aurait
introduit un faux négatif.**

Vérification faite : l'ARS déclare `conf_references_pc = 'N'` sur exactement ces
bulletins — *« Eau d'alimentation conforme aux limites de qualité et non
conforme aux références de qualité »*. Notre verdict est **d'accord avec
l'administration**. La source déclare d'ailleurs elle-même `<=0,25 mg/L` pour
« Chlorite en mg/L » et `<=0,7 mg/L` pour « Chlorites en cas de traitement
pouvant en générer » : ce sont deux paramètres distincts, pas un défaut
d'appariement. **Aucune modification n'a été faite au référentiel.**

Ce qui reste vrai et mineur : ces trois libellés n'ont pas de `seuil_2016` ni de
`seuil_strict`, donc **aucune bascule ne peut être détectée sur les chlorites**
(§2.8, une limite seulement déclarée ne fabrique pas de passé réglementaire).

### 9.5 Le plafond analytique à l'échelle (chantier C4) — chiffres du Tarn seul

**1 295 mesures aveugles, sur 1 128 des 1 575 bulletins (72 %).** Dominé par
l'**hydrazide maléique** : entrée au panel en 2020, cherchée sur ~1 100
bulletins, et **jamais quantifiée une seule fois** — la LQ courante de
0,5 µg/L vaut 5 × sa limite de 0,1. 48 mesures à 0,05-0,1 en 2024-2025 prouvent
que dix fois plus fin est faisable et a été fait.

À rapprocher de C2, qui montre que l'hydrazide maléique est l'une des entrées
de 2020 : le panel a bien été renouvelé, mais **cette entrée-là est illisible
là où sa conformité se joue** depuis six ans. C'est le même paramètre lu par
les deux chantiers, et les deux lectures ne se contredisent pas — elles
s'ajoutent.

À écarter en revanche : les « facteurs 4000 » entre LQ extrêmes sont portés par
deux ou quatre mesures isolées (prosulfocarbe 20 µg/L en 2017, aminotriazole
50 µg/L en 2022). **Ce n'est pas une dispersion entre laboratoires, c'est un
plafond systématique sur une molécule.**

---

## 10. Mise à jour du 9 août 2026 — l'Eure-et-Loir est collecté en entier

**363 communes sur 363, zéro erreur réseau.**
`py -X utf8 src/fetch_departement.py --dept 28 --termine` rend **0**.
Deuxième département complet, après le Tarn. Le corpus double.

**Chiffres relevés contre le référentiel `6c9caf8b87a6`** — figé le 10 août 2026,
après adoption des six lignes de l'arrêté du 11/01/2007 (§12). C'est la version
publiée. Trois versions l'ont précédée en deux jours, et **les chiffres de la
thèse ont bougé à chacune** : c'est la démonstration en acte de ce que le projet
énonce — un « conforme » dépend de la grille qu'on lui applique, y compris de la
nôtre.

| version | date | 28 : conformes avec bascule | à la date |
|---|---|---|---|
| `3a66a7b928d0` | 9 août | 280 | 230 |
| `2cc3c1a9a6c9` | 9 août (codes SANDRE, §11) | 274 | 225 |
| **`6c9caf8b87a6`** | **10 août (six lignes, §12)** | **262** | **219** |

Le Tarn, contre la version publiée : **100 conformes avec bascule, 59 à la
date** (le 63 du §2 ci-dessus est celui de `3a66a7b928d0`). Les mêmes chiffres
sont propagés au §2.11 de `CLAUDE.md`.

| | 28 | ensemble de la base |
|---|---|---|
| communes traitées | 363/363 | — |
| analysée / rattachée au réseau / non documentée | 177 / 181 / 5 | — |
| bulletins complets | 1 611 | **3 193** figés |
| mesures | — | **1 372 988** |
| couverture moyenne des mesures | **90,1 %** | — |
| conformes 2026 **avec bascule** | **262** | — |
| — dont conformes *à la date* avec bascule datée (§2.10) | **219** | — |
| bascules cumulées | 502 | — |
| bulletins non conformes **à la date** | **411** sur 1 611, soit 25,5 % | — |
| — dont sur une **limite** de qualité | 575 dépassements sur 876 | — |
| cache brut `data/brut/28/` | 1 611 bulletins, 35,2 Mo | — |
| libellés listés sans seuil | — | **150** (163 → 157 → 150) |

Collecte en deux temps : 128,2 min pour 360 communes (21,4 s/commune — plus
rapide que les 35,2 s du Tarn), puis 0,7 min pour les 4 dernières.

**Le chiffre à publier est 262, et le chiffre prudent est 219** (§2.10) : c'est
le second qui se compare à la conclusion de l'ARS. Les deux se recalculent avec
`select version_referentiel, count(*) ... from analyses_figees` — et se
revérifient après toute retouche du référentiel, puisqu'ils en dépendent.
**Ne jamais reprendre un de ces chiffres sans sa version de référentiel** : ils
ont changé trois fois en deux jours.

### 10.1 Quatre communes perdues par le journal, pas par la collecte

La passe de fond s'est terminée sur un code de sortie 0 en affichant
`[360/360]` et **zéro erreur journalisée** — mais `--termine` rendait
`359/363, 4 restante(s)` : Moléans, Mondonville-Saint-Jean, Montboissier,
Montharville n'avaient **aucune ligne** au journal. Le fichier n'était pas
corrompu (359 lignes, toutes lisibles) : quatre `ecrire_journal` ont été
**perdues en écriture**, pas mal formées.

La reprise les a traitées en 0,7 min avec **0 appel réseau, 15 bulletins relus
au cache** : la collecte les avait donc bien faites, seul le journal ne le
disait pas. Une machine qui s'est arrêtée un court instant pendant la collecte
est une cause plausible — **elle n'est pas établie**, et le mécanisme exact
reste inconnu.

**Ce qu'il faut en retenir** : le code de sortie 0 et le compteur `[N/N]` ne
sont pas des preuves de complétude. **`--termine` est le seul juge**, et il a
fonctionné exactement comme il a été écrit pour le faire le 8 août. Le lancer
systématiquement après toute collecte départementale.

### 10.2 Ce qui attend, avant toute publication du 28

1. **157 libellés listés par `v_parametres_non_apparies`** (163 avant les
   corrections du §11 ; 118 avec le Tarn seul). Inventaire libellé par libellé :
   `data/etudes/parametres_non_apparies_2026-08-09.md`, qui fait foi.
   **Relecture du 9 août au soir : `docs/AUDIT_NON_APPARIES.md`** — elle porte
   ce que l'inventaire ne dit pas : ce qui reste à décider, et dans quel ordre.
   Trois conclusions : le compte **n'est pas** un compte d'angles morts ;
   la vue **surcompte** les libellés qui portent une référence déclarée et sont
   donc bel et bien comparés — le compte honnête est **143 libellés, 6,7 % du
   corpus**, contre 150 affichés. Les **six lignes de l'arrêté du 11/01/2007
   ont été adoptées le 10 août** (fer, manganèse, ammonium, COT, coloration,
   turbidité) : voir §12. **Reste bloquante l'anthraquinone** — même code SANDRE
   et même CAS sous deux libellés, dont un seul est noté, 39 mesures toutes
   quantifiées au-dessus de 0,1 µg/L, dans 22 communes.
2. **Ne pas comparer les 262 cas du 28 aux 100 du Tarn** sans afficher
   l'effort de recherche de chacun (§2.11). Les deux panels ne sont pas les
   mêmes, et la couverture non plus — **90,1 % contre 93,7 %**.
3. **Publier reste un geste séparé.** `tests/test_sorties.py` échouera tant
   que les communes couvertes n'ont pas leur page — c'est le contrôle qui
   fonctionne, pas une régression (§8quater bis).
4. **35 bulletins du Tarn sans prose**, dossiers de faits déjà fabriqués dans
   `data/dossiers/` (9 août 2026), plus 2 réponses en attente d'intégration.
   Yannick indique que les analyses du Tarn sont faites : c'est donc
   l'intégration qui reste à vérifier. **Au 9 août au soir, `data/dossiers/` ne
   contient plus que `reponses/`, vide** : les dossiers ont été consommés, et
   aucun dossier n'existe pour le 28.
5. ~~Commiter la modification du référentiel~~ — **fait**, commit `550713a`.
   `2cc3c1a9a6c9` est reconstituable depuis l'historique.
6. **Cinq bulletins où notre verdict à la date contredit la conclusion de
   l'ARS** — Alluyes (19/04/2024), Gilles (04/08/2025), Ymeray (20/02/2025),
   Saint-Bomer (12/01/2026), Cloyes-les-Trois-Rivières (12/09/2022). Quatre sur
   cinq portent le chlorothalonil R471811 **au-dessus de 0,9 µg/L**, que l'ARS
   traite ici comme valeur indicative sans conclure à la non-conformité, alors
   qu'elle conclut l'inverse sur d'autres bulletins du même département. La
   contradiction est dans la source. **Relecture humaine obligatoire avant
   publication** (§2.13 : un faux positif coûte plus qu'un faux négatif).
   Le cas d'Alluyes est par ailleurs le plus démonstratif du corpus :
   0,94 µg/L mesuré **dix jours avant** la date d'applicabilité du seuil de
   0,9 (29/04/2024) — même eau, même mesure, verdict inverse dix jours plus
   tard.

---

## 11. Mise à jour du 9 août 2026 — les 163 libellés sans seuil, et la nature du seuil

Point 1 de la file du §10.2, traité en entier, publié et contrôlé.
**Version de référentiel publiée : `2cc3c1a9a6c9`.**

### 11.1 Les trois causes, et ce qui a été fait de chacune

Les 163 libellés de `v_parametres_non_apparies` ne relevaient pas d'un problème
mais de trois. Inventaire complet dans
`data/etudes/parametres_non_apparies_2026-08-09.md`.

| cause | libellés | traitement |
|---|---|---|
| **A** — le seuil EST au référentiel, le libellé ne s'y apparie pas | 5 | corrigé |
| **B** — la source déclare une référence que le moteur ignorait | 13 | déjà outillé (§11.3) |
| **C** — ni ligne, ni référence déclarée | 145 | 1 traité (perchlorate), le reste documenté |

**39 lignes du référentiel ont reçu leur `code_parametre`** — 32 lus dans le
corpus, 7 établis à la main. Restent 5 lignes volontairement vides : deux règles
de famille (ce ne sont pas des substances), le chlorure de vinyle (jamais
mesuré), le 1,2,4-triazole (aucun libellé Hub'Eau ne le porte — aminotriazole
et benzotriazole sont d'autres substances) et les chlorites (le code 1735
couvre deux objets réglementaires).

Effet mesuré, avant/après : **+8 567 mesures notées**, dépassements applicables
de 1 003 à 1 081 — soit exactement **70 bactéries coliformes et 8 radon 222**,
tous deux de nature `reference`. Le volet radiologique cesse d'être l'angle mort
du §8 de `CLAUDE.md` : il n'était pas « non travaillé », il n'était **jamais
apparié**.

**Deux corrections d'unités**, dans `norm_unite()` : `n/(100mL)` devenait `n/`,
la parenthèse étant traitée comme une espèce chimique. Pire — `n/(100mL)`,
`n/(250mL)` et `n/(100L)` se réduisaient **tous les trois à `n/`**, donc se
déclaraient mutuellement comparables. Et `mSv/an` ≡ `mSv/a`. 10 354 mesures
renormalisées par migration sur place (`renormaliser_unites`, sur le modèle de
`migrer_mesures`).

### 11.2 Un faux positif produit, détecté, corrigé — la leçon vaut d'être gardée

Renseigner `code_parametre` a d'abord introduit **deux faux dépassements de
sélénium** (Sainville, Aunay-sous-Auneau) : 29 µg/L comparés à 20 alors que la
source déclare 30 pour ces mesures au titre de l'exception géologique.

**Le code SANDRE 1385 couvre deux objets réglementaires** — « Sélénium » et
« Sélénium si conditions géologiques particulières ». Même cas pour 1752
(chlorates, 250 contre 700 µg/L), qui n'avait pas encore produit de faux
positif. Les deux codes ont été retirés.

> **Règle à retenir : avant d'apparier par code, vérifier qu'un même code ne
> porte pas deux limites déclarées différentes.** Trois codes sont dans ce cas
> sur tout le corpus : 1385, 1752, 1339. Et **ne jamais automatiser
> l'appariement par ressemblance de libellé** : essayé le même jour, 32
> candidats faux sur 37 — « Ethylbenzène » se rattachait à « Benzene », et tout
> ce qui contient les lettres « ph » à la ligne « pH ».

Écart signalé, non corrigé : `CLAUDE.md` §2.13 annonce que le sélénium est
modélisé par `seuil_conditionnel` et `condition_seuil`. **La ligne du
référentiel a ces deux colonnes vides.**

### 11.3 La nature du seuil est affichée — 195 bulletins changent de couleur

Le moteur lisait déjà les références de qualité : ce travail existait **non
commité** dans l'arbre (`nature_seuil`, `hors_reference`, `sens_hors_reference`,
`reference_min` / `reference_max`, et leurs compteurs figés). **Le §9.3(a) est
donc périmé.** Ce qui manquait était l'affichage, ajouté le 9 août :

- **le rouge est réservé à la limite de qualité.** `niveau()` prend désormais
  `nb_depasse_limite` : **195 bulletins sur les 566 qui portent un dépassement
  n'en ont aucun sur une limite** et passent de rouge à ambre. Paulinet est le
  cas type — nous affichions « dépassement » sous une conclusion ARS de
  conformité pleine ;
- **le bandeau a deux titres** : « N paramètres dépassaient la limite de
  qualité » ou « Aucune limite de qualité dépassée » ;
- **chaque carte porte sa nature** — limite / référence / vigilance — et la
  phrase qui l'explique ;
- **le résumé citoyen nomme** au lieu de compter : « 7 limite(s) de qualité ·
  1 référence(s) · 1 valeur(s) de vigilance » ;
- **`depassements_en_tete` trie les limites d'abord.**

**Nouveau bloc « Hors de la référence de qualité »** (`hors_references()` +
`renderReferences()`), sur le périmètre décidé par Yannick : **hors référence ET
sans limite de qualité**. Là où une limite existe, c'est elle qui parle.
**617 bulletins sont hors d'une référence, dont 484 par le BAS** — l'eau
agressive, premier écran du projet qui montre une eau sous sa plage. Le bloc
porte un liseré, pas une couleur d'alerte : ce n'est pas une non-conformité.

`nb_depasse_applicable` ne bouge pas : les compteurs le **décomposent**, et ils
sont lus dans `analyses_figees`, jamais recalculés à l'affichage (§8bis).

### 11.4 Perchlorate — et la famille de sources `GEST`

Ligne ajoutée au référentiel : **aucun `seuil_2016`, aucun `seuil_2026`** — il
n'existe aucune limite réglementaire, ni UE ni française. `seuil_strict = 1`
µg/L, décision de Yannick : « ce n'est pas le cadre légal, c'est le cadre strict
que l'on a documenté ». Résultat : **0 notée, 0 dépassement de conformité,
214 `depasse_strict`** sur 44 communes.

Chronologie lue sur source primaire — VTR 0,7 µg/kg pc/j (2011) ; valeurs de
gestion DGS 15 µg/L adultes et 4 µg/L nourrissons de moins de 6 mois (2011,
reconduites le 8/4/2014) ; **avis Anses du 26/12/2018 recommandant 1 µg/L pour
l'eau de reconstitution des biberons et 5 µg/L pour l'adulte** ; OMS 2017 = 70 ;
US-EPA 2019 = 56 ; VTR portée à 1,5 le 3/2/2022. **La DGS n'a pas repris le 5** —
vérifié sur un document ARS d'octobre 2022 qui présente les valeurs de 2014
comme « toujours en vigueur ».

Ce qui déplace la valeur d'un facteur six n'est ni la molécule ni l'eau : c'est
**la part de l'exposition totale attribuée à l'eau de boisson**, 60 % en 2014 et
20 % en 2018. La thèse du projet, sur une substance qui n'a jamais eu de limite.

Nouvelle famille de sources **`GEST` — valeurs de gestion hors limite
réglementaire**, quatre entrées, fichiers rangés dans
`Sources/GEST_Valeurs_de_gestion/`. `REG` porte la réglementation *des seuils* ;
y ranger une valeur qui n'en est pas une ferait prononcer des non-conformités
contre une valeur qui n'en fonde aucune.

**`pypdf` a été installé** à cette occasion. Sans lecteur PDF, toute source
réglementaire primaire restait hors de portée et retombait en `a_verifier` —
c'était la réserve n° 1 du §8.

### 11.5 Publication — faite, contrôlée

```
683 commune(s) couverte(s), 0 sans page      678 fiches + 5 non documentées
691 page(s), 0 ressource(s) distante(s)
les 8 contrôles de tests/test_sorties.py passent
```

Un seul signalement non bloquant, connu : le « charbon actif » de Vourles
(§4.2), prose d'auteur, décision de Yannick.

### 11.6 Ce que cette publication laisse ouvert

1. **207 communes portent une prose PROPOSÉE**, à relire — contre 45 avant le
   passage à l'échelle.
2. **La fiche autonome pèse 136 Mo.** Elle a été conçue comme « un fichier
   unique qu'on peut archiver ou transmettre » : à 3 193 bulletins, elle ne
   l'est plus. `site/public/` pèse 651 Mo. **À traiter avant le prochain
   département.**
3. **Trois versions de référentiel cohabitent** dans la base — 9 579 lignes
   figées pour 3 193 bulletins, base passée de 142 à 522 Mo. Purger les versions
   périmées est une décision à prendre : elles sont la trace de ce qui a été
   publié sous chaque grille.
4. **La règle de comparaison intra-départementale** (`CLAUDE.md` §2.11,
   quatrième règle) est écrite mais **pas outillée** : le contrôle n° 8 de
   `test_sorties.py` vérifie qu'une zone est nommée, pas qu'elle appartient au
   même département.
5. Les points 2 à 4 du §10.2 restent ouverts, ainsi que le perchlorate côté
   fiche : la ligne existe, aucun bloc ne l'explique encore au lecteur.
6. **Proton Drive a verrouillé `data/eau.duckdb` deux fois** en pleine écriture,
   faisant échouer un figeage. Yannick a suspendu la synchronisation. La base
   n'est pas versionnée et se reconstruit (`--reingerer`) : elle n'a rien à faire
   dans un dossier synchronisé.


---

## 12. Mise à jour du 10 août 2026 — les six lignes de l'arrêté, et 262/219

Décision de Yannick : **adopter les six paramètres de l'annexe I de l'arrêté du
11 janvier 2007** qui manquaient au référentiel, refiger, republier.
Instruction, extraits littéraux et choix de modélisation :
`docs/AUDIT_NON_APPARIES.md` §4.

**Version publiée : `6c9caf8b87a6`**, figée le 10 août 2026 sur 3 193 bulletins.

| ligne ajoutée | valeur | nature | source |
|---|---|---|---|
| Fer (code 1393) | 200 µg/L | reference | REG-02\|REG-06 |
| Manganese (1394) | 50 µg/L | reference | REG-02\|REG-06 |
| Ammonium (1335) | 0,10 mg/L — conditionnel 0,50 si origine naturelle démontrée en eaux souterraines | reference | REG-02\|REG-06 |
| Carbone organique total (1841) | 2,0 mg/L | reference | REG-02\|REG-06 |
| Coloration (1309) | 15 mg/L (Pt) | reference | REG-02\|REG-06 |
| Turbidite (1295) | 1,0 NFU — conditionnel 2,0 au robinet | reference, `a_verifier` | REG-02\|REG-06 |

Les six valeurs sont **identiques dans les deux grilles** — vérifié sur la
version consolidée et sur celle en vigueur au 19/12/2015 — donc `seuil_2016 =
seuil_2026`, aucune date d'applicabilité, **aucune bascule nouvelle**.

### 12.1 Ce que ça change, mesuré

| | avant (`2cc3c1a9a6c9`) | après (`6c9caf8b87a6`) |
|---|---|---|
| 28 — conformes 2026 avec bascule | 274 | **262** |
| 28 — conformes à la date (§2.10) | 225 | **219** |
| 28 — couverture moyenne | 88,7 % | **90,1 %** |
| 28 — bulletins non conformes à la date | 397 | **411** |
| 81 — conformes avec bascule / à la date | 109 / 59 | **100 / 59** |
| 81 — couverture moyenne | 92,6 % | **93,7 %** |
| libellés listés sans seuil | 157 | **150** |

Les 12 bulletins que le 28 perd sont **9 turbidités et 3 COT**. Aucun n'est un
dépassement de limite de qualité : sur les 876 dépassements applicables du 28,
**575 portent sur une limite**, le reste sur une référence ou une valeur de
vigilance — c'est ce que `nature_seuil` sert à dire (§11.3).

### 12.2 Une prévision fausse, et ce qu'elle apprend

L'audit annonçait **268**. Le refigeage rend **262**. La prévision appliquait le
seuil conditionnel de 2,0 NFU à la turbidité, or `depasse_2026` compare à
`seuil_2026` — 1,0 NFU — et **seul `depasse_applicable` applique la condition**.
Le chiffre à la date, 219, était juste ; le contrefactuel ne l'était pas.

> **L'asymétrie du §2.13 protège le verdict daté, pas les deux contrefactuels.**
> Une estimation d'effet faite à la main sur `nb_depasse_2026` doit reproduire
> cette différence, ou se taire. Ne jamais annoncer un chiffre de sortie avant
> de l'avoir refigé.

### 12.3 Réserves ouvertes

1. **`REG-06` n'a toujours pas de fichier sur le disque.** Les extraits ont été
   lus sur Légifrance en ligne. La turbidité reste en `fiabilite = a_verifier`,
   et doit être signalée comme telle dans toute sortie publique (§2.7).
2. **Le code 1295 porte deux objets réglementaires** — une limite déclarée de
   1,0 NFU sur 247 mesures, une référence de 0,5 ou 2 NFU sur 2 729. C'est le
   motif qui avait fait retirer les codes du sélénium et des chlorates (§11.2).
   L'appariement a été maintenu ; conséquence : deux mesures à 1,3 NFU passent
   d'un dépassement de limite à un dépassement de référence.
3. **`organoleptique` est une famille nouvelle** (turbidité, coloration), sans
   effet sur le calcul mais nouvelle au vocabulaire.
4. L'anthraquinone reste **le dossier bloquant** du §10.2, point 1.


---

## 13. Mise à jour du 10 août 2026, après-midi — ÉTAT ACTUEL

**Version publiée : `435b9a089f1d`**, figée le 10 août 2026 sur 3 193 bulletins.
Le corpus n'a pas bougé de la journée : **aucun prélèvement nouveau**. Tout ce
qui suit est un déplacement de grille ou de méthode.

### 13.1 Les chiffres à publier

| | Eure-et-Loir | Tarn |
|---|---|---|
| bulletins complets | 1 611 | 1 575 |
| **conformes 2026 avec bascule** | **260** | **100** |
| **conformes à la date** (§2.10) | **218** | **59** |
| dépassements applicables | 880 | 251 |
| — dont sur une **limite** de qualité | 579 | 84 |
| couverture moyenne | 90,1 % | 93,7 % |

**Ne jamais reprendre un de ces chiffres sans sa version de référentiel.** Le
chiffre de l'Eure-et-Loir est passé de 280 à 260 en quatre versions dans la
même journée, sans qu'un seul prélèvement change :

| version | ce qui a changé | 28 |
|---|---|---|
| `3a66a7b928d0` | état du matin | 280 / 230 |
| `2cc3c1a9a6c9` | codes SANDRE renseignés | 274 / 225 |
| `6c9caf8b87a6` | six lignes de l'arrêté du 11/01/2007 | 262 / 219 |
| **`435b9a089f1d`** | anthraquinone, libellés de panel | **260 / 218** |

### 13.2 Ce qui a changé dans la méthode

- **La fiche communale ne porte plus aucune prose.** Décision de Yannick :
  le dérivé et les accroches vers les dossiers de substance, rien d'autre. Le
  bandeau « lectures dérivées » a disparu avec elle. `redactions.json` (74) et
  `redactions_proposees.json` (88) sont **conservés et versionnés**, simplement
  plus affichés ; l'atelier les lit toujours.
- **Le raisonnement a changé d'étage** : il s'écrit une fois par substance
  (`sortie/dossier_substance.py` + `dossier_page.py` + la consigne versionnée),
  se relit une fois, et chaque fiche concernée y renvoie. Quatre dossiers de
  substance publiés, plus un dossier de panel.
- **`classe_effort` ne classe plus** : panel de routine / ciblé / intermédiaire
  / étendu, au lieu de restreinte → exhaustive.
- **`CLAUDE.md` §2.13 et §2.8** portent le reclassement de pertinence : il
  déplace deux verdicts, dont un opposable — le « total pesticides ».
- **L'anthraquinone est au référentiel** (code 2013, `a_verifier`).

### 13.3 L'état matériel

- base **313 Mo**, deux versions figées (`435b9a089f1d` et `6c9caf8b87a6`) —
  purgée avec `src/purger_versions.py`. **DuckDB ne rend la place qu'en
  RECOPIANT la base** (`COPY FROM DATABASE`), jamais par `VACUUM` ;
- site 655 Mo, fiche autonome 134 Mo ;
- **`data/` et `site/public/` sont exclus de Proton Drive** — plus de verrou
  ni de fichier renommé depuis ;
- **42 commits d'avance sur `master`**, aucun dépôt distant.

### 13.4 Avant d'ajouter un département — à lire

1. **La collecte prend le verrou d'écriture de DuckDB pendant deux heures.**
   Aucun autre processus ne peut ouvrir la base, même en lecture : ni
   `build_site.py`, ni les tests, ni un dossier de faits.
2. **Refiger refige TOUT le corpus** et le temps croît avec lui : 20 minutes à
   3 193 bulletins.
3. **Les cinq proses seront bloquées par `--verifier`.** Leurs nombres — 794,
   645, 255, 70 paramètres entrés, 648 communs… — dépendent du corpus entier.
   C'est le contrôle qui fonctionne, pas une régression : il faut recaler les
   textes sur les nouveaux dossiers de faits. **Une prose est couplée à une
   version de référentiel ET à l'étendue du corpus.**
4. **Le dossier de panel devra être refait** : sa prose dit elle-même que deux
   départements ne font pas une règle nationale.
5. **Le barème des LQ change de base** (§2.14) : les fiches publiées affichent
   un repère périmé jusqu'à republication.
6. `--termine` **est le seul juge** de la complétude d'une collecte. Le code de
   sortie 0 et le compteur `[N/N]` ne le sont pas (§10.1).
7. **`fetch_departement.py` refige de lui-même en fin de course** —
   `run(..., figeage=True)` par défaut. Conséquence constatée le 10 août 2026 :
   une sonde `--limite 3` censée coûter 5 minutes en a coûté 25, dont 20 de
   refigeage du corpus entier. Deux corollaires. **Il n'y a pas de sonde
   bon marché** : toute collecte, même de trois communes, entraîne le
   refigeage — utiliser `--sans-repli`/`--limite` ne l'évite pas, seul un
   `--rapport` est vraiment sans effet. Et **l'étape 4 de la séquence du §13.5
   est déjà faite** à la sortie d'une collecte non interrompue : le vérifier
   plutôt que relancer `figer.py` à l'aveugle. Aucune version nouvelle n'est
   créée au passage — `version_referentiel()` est une empreinte du référentiel,
   qui n'a pas bougé : le figeage réécrit dans la version courante, et rien
   n'est à purger.

### 13.5 La séquence complète, dans l'ordre

```bash
py -X utf8 -u src/fetch_departement.py --dept NN --tous     # ~2 h
py -X utf8 src/fetch_departement.py --dept NN --termine     # doit rendre 0
py -X utf8 src/build_db.py
py -X utf8 -u src/figer.py                                  # ~20 min
py -X utf8 src/purger_versions.py --faire                   # garde 2 versions
py -X utf8 sortie/dossier_panel.py                          # dossiers de faits
py -X utf8 sortie/dossier_substance.py --libelle "..."      # une par substance
py -X utf8 sortie/dossier_substance.py --verifier           # recaler les proses
py -X utf8 sortie/dossier_panel.py --verifier
py -X utf8 -u site/build_site.py                            # ~10 min
py -X utf8 -u sortie/build_fiche.py                         # ~5 min
py -X utf8 tests/test_verdict.py && py -X utf8 tests/test_figer.py
py -X utf8 tests/test_sorties.py                            # les 8 blocs
```

### 13.6 Ce qui reste ouvert

- **`REG-06` n'est pas archivé** — Légifrance oppose un contrôle anti-robot.
  Deux règles publiées s'y appuient (turbidité, §2.13) et restent
  `a_verifier`. **REG-03, lui, est extractible et porte la définition du total
  pesticides** : la dépendance est réduite, pas levée ;
- **`CLAUDE.md` fait 607 lignes** pour une cible de 400, et le tri est
  **déprioritisé — décision de Yannick, 10 août 2026.** Motif : le dégraissage
  était une mesure d'économie de tokens, et le poste dominant a changé. Le
  fichier vaut ~9–10 k tokens rechargés une fois par session (estimation sur
  32 750 octets, non mesurée) ; en retirer un tiers économiserait ~3 k. Un seul
  agent de fond qui recale une prose sur son dossier de faits en consomme
  plusieurs dizaines de milliers, et il y en a cinq. **Optimiser le coût fixe
  pendant que le coût variable a pris toute la place n'est pas le levier** :
  celui-ci est la découpe du §3 du mode opératoire — un agent de fond par
  unité, contexte neuf — et le variateur `effort`. À rouvrir si la rédaction
  se tarit ou si le fichier repart à la hausse ;
- **la fiche autonome pèse 134 Mo** — elle n'est plus « un fichier qu'on peut
  transmettre », et elle grossira ;
- **le choix du prochain département n'est pas une question technique** : un
  voisin de la Beauce rend les nitrates et les métabolites comparables sur un
  même bassin ; un département de profil très différent teste mieux la
  robustesse du référentiel. Ce n'est pas la même enquête ;
- **La cause C devient un chantier de fond — décision de Yannick, 10 août
  2026.** *« C'est la plus-value du travail. Documenter l'invisible qui est
  pourtant officiellement collecté. »* Les 145 libellés de cause C (§11.1) ne
  sont plus un reliquat de diagnostic à résorber : ils sont un **objet
  d'enquête à part entière**. Une substance mesurée par l'ARS, quantifiée dans
  l'eau, et qu'aucun texte ne permet de déclarer conforme ou non conforme —
  c'est la thèse fondatrice déplacée du seuil qui bouge vers **le seuil qui
  n'existe pas**.

  Ce que le chantier suppose, et qui n'est pas fait :

  1. **Trier C en deux**, ce que le compteur actuel confond — (C1) une limite
     réglementaire existe et nous ne l'avons pas identifiée : c'est notre
     manque, réparable ligne par ligne avec `sources` et `fiabilite` ; (C2)
     **aucune limite n'existe**, et c'est le sujet. Le tri ne se déduit
     d'aucune donnée du corpus : il se fait source en main, substance par
     substance. **Tant qu'il n'est pas fait, on ne peut rien affirmer sur le
     volume de C2** — dire « 145 substances sans norme » aujourd'hui serait un
     faux positif de méthode ;
  2. **le modèle sait déjà porter C2** : le perchlorate en est le précédent
     (§11.4) — `seuil_2016` et `seuil_2026` vides parce qu'il n'y a rien à y
     mettre, `seuil_strict` documenté et assumé comme tel. C'est le patron à
     reprendre, pas à réinventer ;
  3. **§2.7 s'applique entier** : une substance sans norme se démontre par une
     recherche qui n'a rien trouvé, et cette recherche se date et se source.
     « Nous n'avons pas trouvé de limite » et « il n'existe pas de limite » ne
     sont pas le même énoncé — le second demande d'avoir cherché où il aurait
     fallu, et de le dire ;
  4. **§2.4 transposé** : une substance sans seuil n'est pas « sans risque »,
     elle est **indéterminée**. Aucune sortie ne doit laisser lire l'absence de
     norme comme une absence de problème — ni l'inverse.

  Prérequis matériel : `v_parametres_non_apparies` sur le corpus élargi au 69,
  donc après la collecte et le figeage. L'inventaire du 9 août est dans
  `data/etudes/parametres_non_apparies_2026-08-09.md` — il est à refaire, pas à
  compléter ;
- les cinq proses (quatre substances, un panel) sont **PROPOSÉES, à relire** :
  `py -X utf8 sortie/dossier_substance.py --relire`.


---

## 14. Mise à jour du 10 août 2026, soir — le lot pilote de sourçage C

Trois substances témoins et un dossier de famille, lancés pendant la collecte du
69 en agents de fond `opus`. Rendus dans `data/etudes/sourcage_C/`.
**Le pilote a validé le brief et trouvé trois défauts qui auraient coûté cher
sur un lot de quarante.**

### 14.1 §2.14 de `CLAUDE.md` est FAUX et doit être révisé

**La contradiction la plus grave, et c'est notre propre règle qui tombe.**

§2.14 énonce : « Sur la somme des 20 PFAS, personne n'est plus strict que l'UE
(0,100 µg/L) ». Lu en source primaire, c'est inexact — non sur la valeur, mais
sur le **périmètre** :

| pays | valeur | nombre de substances |
|---|---|---|
| UE / France | 0,10 µg/L | **20** |
| Suède | 100 ng/L | **21** |
| Danemark | 100 ng/L | **22** |
| Canada (recommandation) | 30 ng/L | **25** |
| Italie | — | 24 à 30 (`a_verifier`, à ne pas publier) |

**Même valeur sur un périmètre plus large = plus strict.** C'est très
exactement le §2.13 cinquième cas retourné contre nous : *une somme ne se
compare jamais sans sa date et son périmètre* — nous avons comparé des valeurs
en négligeant l'assiette.

Seule formulation défendable, à substituer : **« à périmètre strictement
identique, aucune valeur opposable inférieure n'a été trouvée »** — avec le
« identifié » du §2.14 lui-même, qui reste la bonne posture.

Le reste de §2.14 est **confirmé** en primaire (DK 2 ng/L, SE 4, DE 20 en 2028
sur la somme des 4), à compléter : Danemark en vigueur depuis 2022, Norvège
4 ng/L en 2026. **Décision de Yannick requise avant de toucher `CLAUDE.md`.**

### 14.2 Les 16 PFAS non appariés entrent TOUS dans la somme des 20

Croisement fait sur l'annexe III B.3 de la directive lue en primaire. Les quatre
substances de la somme absentes de nos non-appariés sont exactement PFOA, PFOS,
PFNA et PFHxS — déjà au référentiel.

**Conséquence : « ces mesures ne pèsent sur aucun verdict » est faux en droit.**
Elles n'ont pas de limite individuelle — c'est normal et ce n'est pas un manque
— mais elles alimentent un paramètre **opposable**. L'absence d'appariement
individuel est donc correcte ; ce qui reste à vérifier est **si notre moteur
calcule la somme des 20**, et sinon c'est un défaut de notre côté, pas un vide
de la norme. Question C-c du document `cause_C_familles_2026-08-10.md`,
**toujours ouverte** : elle demande la base.

Piège de calcul relevé par l'agent : **la somme des maxima n'est pas une somme
observée.** Le seul calcul juste est la somme des 20 **par prélèvement**.

### 14.3 PFAS et perturbation endocrinienne — la réponse est « non » au registre réglementaire

Trois registres tenus séparés (§2.15), et ils ne disent pas la même chose :

- `pe_reglementaire` — **aucun PFAS sur la List I des ED Lists de l'UE**
  (double contrôle : export tableur archivé + lecture en ligne). **Le
  référentiel du projet reste exact : le seul PE avéré au sens réglementaire UE
  dans l'EDCH est le bisphénol A.** Le PFBS est la seule substance du corpus en
  List II, sous *intention* de classification harmonisée en 2026 — une
  procédure ouverte, pas un statut ;
- `pe_scientifique` — signal réel mais fragmenté. Fait primaire à retenir :
  l'ECHA constate une baisse de T4 pour le PFHpA, puis écrit que *« This
  concern is not taken into account in the ELoC assessment »* ;
- `cancerogenicite_circ` — PFOA groupe 1, PFOS groupe 2B (vol. 135, 2023).
  **Aucun classement pour aucun des 16** libellés du corpus.

**À arbitrer par Yannick** : l'angle « PE » sur les 16 PFAS du corpus repose
aujourd'hui sur le seul registre scientifique, fragmenté, et sur des substances
qui ne sont pas celles que le corpus quantifie. La situation ressemble à celle
de l'aluminium, écartée le 9 août 2026 pour un motif voisin. L'angle **« sommes
et périmètres »** est en revanche solide, primaire, et porte une erreur réelle
de notre référentiel (§14.1).

### 14.4 Trois défauts d'outillage, corrigés ou à corriger

1. **Le fonds documentaire est HORS du dépôt** et le brief ne le disait pas :
   `…/Data - Analyse de la qualité de l'eau en France/Sources/`, ~30 PDF classés
   par famille. Deux agents ont fait sept tentatives contre EUR-Lex — qui
   **tronque la directive avant ses annexes** sur toutes les formes d'URL —
   alors que `REG-01_UE_directive-2020-2184.pdf` était sur le disque. Corrigé en
   cours de vol ; il a fait passer l'annexe I de `a_verifier` à `verifie`.
   **Le brief-type doit porter ce chemin.**
2. **Légifrance est accessible** par l'outil web du harnais — deux lectures
   indépendantes et concordantes de l'arrêté du 11 janvier 2007 consolidé,
   annexes I et II (identifiant `LEGIARTI000046890189`). Le §13.6 tient
   `REG-06` pour inatteignable : **c'est le shell et le navigateur qui étaient
   bloqués, pas cette voie-là.** Deux règles publiées (turbidité) et le
   périmètre du « total pesticides » en dépendent. **À retester proprement et à
   archiver.**
3. `pfas_chaines.csv` existe dans `referentiel/` — non examiné, à confronter à
   la liste nominative des 20.

### 14.5 Les trois témoins — et une correction sur les acides haloacétiques

| substance | verdict | remarque |
|---|---|---|
| Toluène | **C2** | repère OMS **0,7 mg/L** (santé), non opposable ; seuils odeur/goût distincts et plus bas |
| Trichloroéthane-1,1,1 | **C2** | l'OMS a **explicitement renoncé** à une valeur guide (table A3.2), motif d'exposition. CIRC **2A**, vol. 130 (2022) |
| Biphényle | en cours | |

Le trichloroéthane-1,1,1 a été **écarté** de la somme « tétrachloroéthylène +
trichloroéthylène » : périmètre de deux substances, des éthylènes ; c'est un
éthane. **Le non-appariement actuel est donc correct.**

**Correction à porter au document de familles** : le périmètre « acides
haloacétiques, 5 substances » a été relevé dans l'annexe française. Si les cinq
acides haloacétiques du corpus (157 quantifications cumulées) y entrent, ils
sortent de C-e et basculent en C-c, et le noyau « quantifié et non jugé » tombe
de 8 substances à 3 : perchlorate, anthraquinone, phosphate de tributyle.
**Observation faite au passage par un agent travaillant sur autre chose — à
sourcer avant d'en tirer quoi que ce soit.**

### 14.7 ÉTAT ACTUEL au 10 août 2026, 21 h 30 — remplace le §13 sur ces points

**La base est LIBRE** (aucun python en vie, collecte arrêtée). **Le référentiel a
changé** : six lignes versées, donc `version_referentiel` va changer et le
prochain `figer.py` refigera TOUT le corpus sous une version nouvelle. Les
chiffres du §13.1 (260/218 Eure-et-Loir, 100/59 Tarn) vont bouger une cinquième
fois — **aucun ne se reprend sans sa version**.

#### Le 69 est à l'arrêt à 57/266, et on sait pourquoi

**`--termine` : 57/266 communes traitées, 209 restantes.** Ce qui est acquis est
en base et figé sous `435b9a089f1d`.

**Le blocage est une commune, pas le réseau** — c'est la conclusion de la
soirée, et elle a coûté trois hypothèses fausses avant d'être trouvée :

1. *« les communes de la Métropole sont plus lourdes »* — faux, elles passent ;
2. *« instabilité réseau intermittente »* — faux ;
3. la bonne : **`69063` Collonges-au-Mont-d'Or fige le collecteur, de façon
   reproductible.** Trois relances successives, trois fois `[1/209] 69063` puis
   plus une ligne pendant 10 minutes, **sans même une `ConnectionError`**. Le
   premier blocage de la soirée, lui, était sur `69044` Charbonnières-les-Bains,
   franchi après relance.

Ce que le code dit : `MAX_TENTATIVES = 4` et chaque reprise **imprime**. Un
silence prolongé sans message signifie donc que le processus n'est PAS dans la
boucle de reprise — il est figé dans un `SESSION.get(..., timeout=90)` qui ne
déclenche pas son propre timeout, ou dans une pagination qui ne se termine pas
(`_pages()` boucle tant que l'API annonce une page suivante, sans rien imprimer
entre deux).

**Prochain geste, avant toute relance du département :** instruire `69063`
seule, avec une trace des appels et des pages. Deux issues à départager —
pagination sans fin (le bogue est chez nous) ou requête qui ne revient jamais
(le bogue est dans la couche HTTP). Ne PAS relancer `--tous` en aveugle : le
superviseur l'a fait trois fois sans avancer d'une commune.

**Le superviseur** (relance sur 10 min de silence, piloté par `--termine`) est
écrit et fonctionne, mais il ne sert à rien contre un blocage déterministe : il
tue et relance sur la même commune indéfiniment. À reprendre **une fois `69063`
réglée**, où il redeviendra utile contre les aléas réels.

#### Ce qui a été livré ce soir

- **§2.14 de `CLAUDE.md` corrigé** (§14.1) — décision de Yannick ;
- **six lignes versées au référentiel** : la somme `9064` des acides
  haloacétiques à **60 µg/L applicable au 01/01/2023**, et ses cinq composants
  en `dans somme (9064)`. Contrôle de forme passé (21 colonnes, 82 lignes
  existantes revérifiées au passage) ;
- **`GEST-05`** (avis Anses du 22/11/2023) et la **famille `SAND`** déclarées
  dans `INDEX_SOURCES.md` ;
- quatre dossiers de sourçage dans `data/etudes/sourcage_C/` : PFAS, toluène,
  trichloroéthane-1,1,1, acides haloacétiques ;
- le découpage de la cause C en six familles : `cause_C_familles_2026-08-10.md`.

#### La file d'attente, dans l'ordre

1. **`69063`** — instruire le blocage. Rien d'autre ne peut avancer sur le 69 ;
2. **la requête PFAS du §14.6** — la base est libre, elle prend une minute et
   elle décide si le moteur doit recalculer la somme des 20 ;
3. `build_db.py` puis `figer.py` — la base doit intégrer les six lignes
   nouvelles. **Attention : nouvelle version de référentiel, refigeage complet** ;
4. corriger `src/hubeau.py` — le timeout qui ne couvre pas toutes les phases.
   **Les tests peuvent tourner maintenant que la base est libre** ;
5. le lot C-d (~40 substances), par paquets de 5, brief-type au §14.4 ;
6. reprendre le noyau éditorial : perchlorate, anthraquinone, phosphate de
   tributyle — **3 substances, plus 8** (§14.5).

#### En vol au moment de la sauvegarde

- **l'agent « biphényle » tourne encore** — son fichier
  `data/etudes/sourcage_C/biphenyle_2026-08-10.md` apparaîtra peut-être seul.
  Le lire avant de relancer quoi que ce soit sur cette substance.

### 14.8 RÉPONDU le 11 août 2026 au matin — les sommes vont bien

Requêtes en lecture seule, base libre, corpus à 69 partiel (57 communes).
**La question du §14.6 est tranchée : c'est la première des trois issues.**

| somme | bulletins | avec individuels | **individuels SANS la somme** | limite déclarée |
|---|---:|---:|---:|---|
| **8847** PFAS (20) | 323 | 323 | **0** | 0,1 µg/L |
| **9064** acides haloacétiques (5) | 117 | 117 | **0** | 60,0 µg/L |

**Zéro quantification orpheline dans les deux cas.** L'ARS publie systématiquement
le paramètre de somme à côté des substances individuelles. **Le moteur n'a donc
rien à recalculer** — ni pour les PFAS, ni pour les AHA. L'inquiétude du §14.2
(« des PFAS quantifiés qui ne pèsent sur rien ») **était infondée**.

Conséquence sur les six lignes versées le 10 août au soir : leur effet est plus
étroit que je ne l'ai dit. La somme 9064 **recevait déjà un verdict** par sa
limite déclarée (60,0). Ce que les lignes ajoutent réellement :
1. l'adossement au **référentiel daté et sourcé** plutôt qu'à la seule déclaration
   de la source — c'est la hiérarchie du §2.8 ;
2. le garde-fou `dans somme (9064)` sur les cinq composants, qui rend **explicite**
   une absence de verdict jusque-là seulement accidentelle.
Ce n'est pas rien, mais ce n'est pas la correction d'un défaut de calcul.

Autres relevés :
- **169 libellés** sans aucun seuil de comparaison (163 le 9 août, 168 hier) ;
- `2034` HAP (6 subst.) et `7431` PCB indicateurs **n'ont aucune limite
  déclarée** — contrairement à `2033` HAP (4) et `2036` THM. À instruire ;
- **requête à refaire** : ma question n° 4, censée dire si une somme obtient un
  verdict, comptait les lignes de `v_mesures_verdict` et non celles portant un
  seuil. **Elle ne conclut rien** — la refaire en testant `seuil_applicable`.

#### Le 69 partiel donne un signal fort, à confirmer

| dept | bulletins complets | couverture moy. | conformes 2026 AVEC bascule |
|---|---:|---:|---:|
| 28 | 1 611 | 90,1 % | 260 — soit **16 %** |
| 81 | 1 575 | 93,7 % | 100 — soit **6 %** |
| **69 (57/266 communes)** | **295** | **77,6 %** | **155 — soit 52 %** |

**Plus d'un bulletin complet sur deux du Rhône est déclaré conforme aujourd'hui
et ne l'aurait pas été en 2016.** Trois fois le taux de l'Eure-et-Loir, huit fois
celui du Tarn. Trois réserves avant d'en faire quoi que ce soit :
- corpus **partiel** (57 communes sur 266) et **44 des 57 sont `rattachee_reseau`**,
  donc les 295 bulletins se concentrent sur peu de réseaux — biais d'échantillon
  probable, à recompter sur le département entier ;
- la couverture est basse (77,6 %), ce qui **déprime** les bascules plutôt que de
  les gonfler : le taux est donc plutôt conservateur sur cet axe ;
- **§2.11 quatrième règle : un département se compare à lui-même.** Ce tableau
  est un instrument de travail, pas une comparaison publiable.

### 14.9 Le biphényle ouvre une SEPTIÈME famille — couvert sans être nommé

Dossier : `data/etudes/sourcage_C/biphenyle_2026-08-11.md`.

**Le découpage C-a…C-f du 10 août est incomplet.** Le biphényle n'est ni C1 (une
valeur nominative que nous aurions ratée) ni C2 (aucune valeur) :

- **il n'est nommé dans AUCUN texte EDCH** — absence vérifiée en plein texte dans
  la directive 2020/2184 **annexes comprises**, l'arrêté du 30/12/2022, l'arrêté
  du 11/01/2007 d'origine, l'annexe I consolidée sur Légifrance, et les
  *Guidelines* de l'OMS ;
- **mais une valeur opposable lui est applicable par CATÉGORIE** : « Pesticides
  (par substance individuelle) — 0,10 µg/L », l'annexe définissant les pesticides
  comme incluant « les fongicides organiques ». Applicable au 01/01/2023, valeur
  identique en 2016 — **aucune bascule possible** ;
- **et notre moteur le capte déjà** : la règle `pesticide_individuel_0_1` de
  `regles_famille.csv` s'applique. Mon brief affirmait « ne pèse sur aucun
  verdict » : c'était faux.

**Nouvelle famille à ajouter — C-g : couvert par une règle de catégorie, sans
être nommé.** À vérifier sur le reste de C-d avant de conclure C2 sur quoi que
ce soit : `v_regle_famille_appliquee` est la vue qui le dit, et le §4 de
`CLAUDE.md` demande déjà qu'elle soit relue.

#### Le fait daté, et ce qu'il est vraiment

SISE-Eaux déclare `<=0,1 µg/L` sur les **40 mesures du 31/03/2026 au 29/05/2026**
(Eure-et-Loir), et **rien** sur les 1 374 antérieures. Le basculement est net et
daté à la journée.

**Ce n'est PAS une bascule au sens du projet** — le seuil n'a pas bougé, il vaut
0,10 en 2016 comme en 2026. Ce qui change, c'est **la déclaration** : la même
substance passe de « non rattachée » à « rattachée aux pesticides » dans ce que
la source publie. C'est le §2.11 transposé du panel à la qualification — ce qui
bouge n'est ni l'eau ni la norme, c'est le classement de ce qu'on regarde.
**Ne jamais l'écrire comme un durcissement réglementaire.**

#### Pourquoi AUCUNE ligne nominative n'a été versée

Recommandation de l'agent, suivie : verser une ligne nominative
**sortirait le biphényle de la règle de famille** et appliquerait 0,10 µg/L aux
**1 374 mesures sans limite déclarée** — transformant des **indéterminés en
conformes**. C'est le §2.4 qui l'interdit, et un faux positif de conformité est
exactement ce que le §2.13 nous fait redouter le plus. La ligne est écrite
« prête à verser » au §5.3 du dossier si Yannick tranche autrement.

Statut **`a_verifier`**, pour une contradiction non levée : l'INERIS écrit
qu'« aucune valeur n'est mentionnée dans la Directive 98/83/CE ou l'OMS », et le
SANDRE classe la substance en « **Liste B – Phytosanitaires** », qu'AQUAREF
définit comme celle où « la décision sur le caractère pesticide ou pas doit être
prise par le gestionnaire ». **Le rattachement aux pesticides est donc un choix
de gestionnaire, pas une évidence de texte.** Aucune instruction DGS arbitrant
ce point n'a été trouvée.

L'OMS est absente **y compris de la table A3.2 des renoncements** : elle n'a pas
écarté le biphényle, elle ne l'a jamais examiné. Ce n'est pas la même chose.

#### Deux notes d'outillage

- **`REG-01` s'extrait intégralement**, annexes I A/B/C et III comprises. Le
  contournement d'EUR-Lex par le PDF local est confirmé — à mettre dans tous les
  briefs.
- **Écart de comptage à trancher** : la base donne 1 414 mesures / 13
  quantifications (dont une en dept 71), le brief disait 1 373 / 12 d'après
  l'inventaire du 9 août. Maximum identique (0,016 µg/L). L'inventaire est
  antérieur au 69 partiel — à recompter en même temps que le reste.

### 14.6 À exécuter DÈS QUE LA BASE EST LIBRE — la requête PFAS

**C'est le point bloquant du dossier PFAS**, et il ne se tranche que sur la base.

Ce qui est déjà acquis, sans la base : le référentiel **connaît** la somme des
20 sous le code SANDRE **8847** (`referentiel_seuils.csv` ligne 2, `seuil_2026`
0,10 µg/L, nature `limite`, `verifie`) ; et le moteur **sait recalculer une
somme** — `_sommes()` dans `src/figer.py` produit déjà
`somme_pesticides_declaree` ET `somme_pesticides_recalculee`, avec le garde-fou
qui évite de compter une somme en même temps que ses composants.

La seule inconnue est donc : **l'ARS publie-t-elle le paramètre 8847, ou
seulement les substances individuelles ?**

```sql
-- 1. Le paramètre 8847 existe-t-il dans le corpus, et où ?
SELECT p.dept, COUNT(*) AS mesures,
       COUNT(DISTINCT m.code_prelevement) AS bulletins,
       COUNT(*) FILTER (WHERE m.est_quantifie) AS quantifiees
FROM mesures m JOIN v_prelevement_verdict p USING (code_prelevement)
WHERE m.code_parametre = '8847'
GROUP BY p.dept;

-- 2. Combien de bulletins portent des PFAS individuels SANS porter 8847 ?
--    Ce sont ceux où la limite opposable n'est vérifiée par personne.
WITH indiv AS (
  SELECT DISTINCT code_prelevement FROM mesures
  WHERE libelle_norm LIKE '%perfluor%' AND code_parametre <> '8847'),
somme AS (
  SELECT DISTINCT code_prelevement FROM mesures WHERE code_parametre = '8847')
SELECT COUNT(*) FROM indiv WHERE code_prelevement NOT IN (SELECT * FROM somme);
```

**Trois issues, trois conduites :**

- **8847 présent et apparié partout** → tout fonctionne, rien à corriger, il
  n'y a qu'à l'expliquer dans le dossier ;
- **8847 absent ou partiel** → le moteur doit recalculer la somme, sur le
  modèle exact de `somme_pesticides_recalculee`. La liste nominative des 20 est
  à prendre dans l'**annexe III B.3 de la directive** (REG-01, sur le disque,
  lue en primaire le 10 août 2026), **jamais reconstituée de mémoire** : le
  périmètre d'une somme est une définition réglementaire (§2.13) ;
- **8847 présent mais non apparié** → défaut d'appariement, cause A, corrigible
  en une ligne.

Vérifier au passage `referentiel/pfas_chaines.csv` (60 lignes, longueur de
chaîne, sourcé) — **non examiné à ce jour**, à confronter à la liste des 20.

---

## 15. Mise à jour du 11 août 2026 — la collecte se coupe en deux, la base reste libre

> **État du corpus au soir du 11 août 2026 — 7 279 bulletins figés sous
> `f3e1d448101f`**, cinq départements entiers : Tarn (81), Eure-et-Loir (28),
> Rhône (69), **Ariège (09)** et **Haute-Garonne (31)**, plus 14 communes de
> Saône-et-Loire (71) et un bulletin isolé des Hautes-Pyrénées (65), repli d'un
> réseau à cheval sur deux départements.
>
> | | couverture des mesures | cas (conformes 2026 avec bascule) | bascules |
> |---|---|---|---|
> | Ariège (09) | 93,2 % | **5** | 12 |
> | Haute-Garonne (31) | 92,3 % | **45** | 73 |
>
> Ces deux départements ont été collectés **par la nouvelle voie**, et sont donc
> aussi la vérification que le résultat produit est le même. Tout chiffre repris
> ici se cite avec `f3e1d448101f` (§8bis).

### 15.1 Le problème, et pourquoi il devenait bloquant

Demande de Yannick : *« à chaque fois que je collecte un département cela fige
la base et je ne peux plus rien faire […] il me reste +35K communes à charger,
j'en ai pour une vie entière si je ne fais pas du parallèle. »*

Deux défauts distincts, et le second est le vrai frein :

1. **DuckDB n'a qu'un seul écrivain**, et `fetch_departement.run()` ouvrait la
   connexion avant la première commune pour la fermer après la dernière. Deux à
   trois heures de verrou pour quelques minutes d'écriture réelle : tout le
   reste était de l'attente réseau, faite le verrou à la main.
2. **La collecte était strictement séquentielle**, un département à la fois, un
   appel à la fois. Aux cadences mesurées — 16,7 s/commune (Rhône partiel),
   21,4 s (Eure-et-Loir), 35,2 s (Tarn) — les 35 000 communes restantes
   représentent de l'ordre de **200 heures d'horloge**, soit huit jours et demi
   sans interruption.

### 15.2 Ce qui a été fait

Le cache brut était déjà le tampon : `brut.py` existe depuis le 8 août 2026
pour séparer *collecter* (une fois, en ligne) de *ingérer* (autant de fois
qu'on veut, hors ligne). Il manquait un chemin qui n'ingère pas du tout.

```
py -X utf8 src/moisson.py --depts 69,71,01 --tous   # réseau, N fils, base LIBRE
py -X utf8 src/ingerer.py --depts 69,71,01          # base prise, puis rendue
```

| fichier | rôle |
|---|---|
| `src/moisson.py` | moisson parallèle. **N'importe pas `duckdb`, et cela doit le rester.** |
| `src/ingerer.py` | cache brut → base, sans réseau, puis figeage. Le seul à prendre le verrou. |
| `src/journal.py` | journal de reprise et cache d'énumération, sortis de `fetch_departement.py` |
| `src/console.py` | trace atomique et étiquetée par fil — `[71] page 4 — 20000 lignes lues` |

La règle de couverture **n'a pas été recopiée** : `collecte.traiter_commune`
accepte `con=None`, et c'est tout le mécanisme. Même fonction, même ordre
d'essais, même repli réseau, même statut rendu, même journal — seule
l'insertion en base est différée. `ingest.identifier()` a été extrait de
`ingest_bulletin` pour que la trace de moisson annonce le nombre de paramètres
calculé **par le même code** que l'ingestion réelle.

Le journal et le cache sont identiques des deux côtés : un département commencé
par `fetch_departement.py` se termine par `moisson.py`, et réciproquement.

### 15.3 Trois protections que le parallélisme rendait nécessaires

Elles ne se remplacent pas, et chacune couvre un défaut que les autres
laisseraient passer.

- **`hubeau.REGULATEUR`** — les pauses `PAUSE` / `PAUSE_COMMUNE` sont locales à
  un fil : quatre fils qui les respectent chacun **quadruplent** la charge vue
  par Hub'Eau, et rien ne le dirait. Le régulateur borne le débit du *processus
  entier* — appels en vol, appels ouverts par seconde — et met **tous** les
  fils en retenue dès qu'un seul reçoit un 429. Les plafonds (4 en vol,
  3 ouvertures/s) sont **les nôtres** : Hub'Eau ne publie aucun quota, et le
  §2.7 interdit d'écrire un seuil qu'on n'a pas lu, y compris un seuil de
  politesse. Les relever engage le projet et ne se fait pas sans mesure.
- **`hubeau._verrou_du_reseau`** — un verrou **par clé de réseau**, pas
  seulement autour du dictionnaire. Signalé par Yannick pendant le chantier :
  la mémoïsation `_INVENTAIRES_RESEAU` posée le matin même est parfaite en
  mono-fil, mais à N fils deux communes du même réseau lyonnais arrivent
  ensemble, constatent toutes deux l'absence de l'entrée et lancent toutes deux
  l'inventaire — la mémoïsation cesse de protéger au moment précis où elle sert
  le plus. Le second fil doit **attendre** le premier, pas recalculer. Le
  régulateur ne couvre pas ce gaspillage-là : il borne la charge instantanée,
  pas le travail dupliqué.
- **`journal.ecrire_journal`** — un verrou par département. Deux `write()`
  simultanés peuvent s'entrelacer et produire une ligne JSON illisible, donc
  une commune silencieusement perdue de la reprise.

Et `collecte.compter()` : `Counter[k] += 1` est une lecture puis une écriture,
et deux incréments simultanés en perdent un. Un compteur faux ferait
sous-estimer ce qu'on demande à Hub'Eau — précisément le chiffre à ne pas
fausser.

### 15.4 Mesure réelle — deux départements entiers, 4 fils, `--tous`

Les premiers essais portaient sur 6 puis 8 communes de Saône-et-Loire et
donnaient 7,1 puis 14,2 s/commune — deux chiffres qui ne concordaient pas,
parce qu'un échantillon de cette taille ne donne pas la distribution. Deux
départements ont été moissonnés en entier le 11 août 2026.

| | Ariège (09) | Haute-Garonne (31) |
|---|---|---|
| profil | rural | rural **et** métropole |
| communes | 325 / 325 | 586 / 586 |
| moisson | **13,1 min** | **21,9 min** |
| coût | **2,4 s/commune** | **2,2 s/commune** |
| erreurs | **0** (4 incidents réseau rattrapés) | **0** (4 rattrapés) |
| 429 reçus | **aucun** | **aucun** |
| analysées / rattachées / non documentées | 172 / 153 / 0 | 144 / 431 / **11** |
| bulletins rapatriés | 1 192 | 1 235 |
| bulletins relus au cache | 150 | **432** |
| inventaires de réseau épargnés | — | **387** |

Contre **16,7 à 35,2 s/commune** sur les trois collectes séquentielles
précédentes, et sur le mode `--tous`, le plus lourd. La base est restée
ouverte au travail pendant les deux moissons — la Haute-Garonne a même été
moissonnée **pendant que l'Ariège s'ingérait**, ce qui était impossible avant.

**Les 387 inventaires de réseau épargnés valident le verrou par clé.** Ce sont
387 fois où un fil est arrivé sur un réseau qu'un autre inventoriait déjà, a
attendu, et n'a fait aucun appel — sur la Métropole toulousaine, dont les
communes partagent leurs réseaux. Sans lui, c'étaient 387 inventaires
redemandés à Hub'Eau, et le régulateur de débit n'en aurait attrapé aucun :
il borne la charge instantanée, pas le travail dupliqué.

Trois faits à conserver :

- **La métropole toulousaine n'a pas coûté ce que coûte la lyonnaise.** 93
  paginations profondes sur le 31, aucune du calibre du réseau CENTRE de Lyon
  (492 871 lignes, 99 pages, une demi-heure). Le pire cas connu du projet
  **n'est pas représenté** dans ces deux mesures.
- **Les 11 communes non documentées du 31 sont les premières du corpus.** Ni
  vertes ni rouges : la catégorie visible du §8bis, correctement remplie.
- **Un réseau franchit les frontières départementales.** Le bulletin
  `03100180348`, repli d'une commune de Haute-Garonne, a été prélevé dans les
  **Hautes-Pyrénées** et s'est donc écrit dans `data/brut/65/`. Il est ingéré
  sous la commune où il a réellement eu lieu (§2.3), et `ingerer.py --etat` l'a
  signalé comme un département en attente — ce qu'il faut lire comme un
  fonctionnement correct, pas comme une anomalie. **Après une moisson, vérifier
  `ingerer.py --etat` : un département voisin peut y être apparu.**

### 15.5 Le second verrou, trouvé en vérifiant — et levé

La première ingestion réelle a mesuré ceci :

```
ingéré : 65 bulletin(s)
verrou de la base tenu 33.7 min
```

**Trente-trois minutes pour verser soixante-cinq bulletins.** L'ingestion elle-même
en coûtait 1,3 ; le figeage qui suit en coûtait **32,4**, parce que
`figer.figer()` refigeait les 4 745 bulletins du corpus à chaque appel — 0,41 s
l'unité. Le découpage moisson/ingestion avait levé un verrou de trois heures
pour en installer un autre, qui **croît avec le corpus et non avec le lot** : à
35 000 communes, chaque ingestion aurait immobilisé la base des heures durant.
C'était la moitié du problème, non résolue.

`figer.figer()` est donc incrémental depuis le 11 août 2026. Il ne refige que
les bulletins absents d'`analyses_figees` **sous la version courante**.

Mesures après, sur la vraie base :

| | avant | après |
|---|---|---|
| ingestion de 65 bulletins (corpus 4 745) | **33,7 min** de verrou | — |
| ingestion de 108 bulletins (corpus 4 853) | — | **2,5 min** de verrou |
| relance sur corpus inchangé | 33,7 min | **1 seconde** |

Le figeage suit désormais la taille du **lot**, plus celle du corpus.

Ce qui rend l'incrémentalité sûre, et non seulement rapide — quatre façons de
périmer une ligne figée, quatre réponses :

| ce qui change | ce qui l'attrape |
|---|---|
| un bulletin nouvellement ingéré | il n'est pas dans `analyses_figees` |
| le **référentiel** | `version_referentiel` change → personne n'est figé sous la nouvelle → tout est refigé |
| un bulletin **réingéré** | `ingest.ingest_bulletin` efface ses lignes figées, **toutes versions confondues** |
| le **code de calcul** | `figer.version_moteur()` — empreinte de `figer.py` + `build_db.py` + `common.py` |

La quatrième est celle qui n'existait pas et qu'il fallait inventer. Tant que
tout était refigé à chaque appel, corriger un défaut de calcul se propageait
tout seul. En incrémental, le référentiel n'ayant pas bougé, les 4 700 lignes
déjà figées **garderaient silencieusement l'ancien calcul** pendant que les
nouvelles porteraient le bon : deux calculs sous une seule version, et rien
pour le dire. L'empreinte est volontairement grossière — elle porte sur les
octets des fichiers, commentaires compris — parce qu'un refigeage inutile coûte
du temps quand un refigeage manquant produit un chiffre faux. C'est le §2.13
appliqué à notre propre outillage.

**Un défaut réel a été attrapé en chemin, par le test et non par moi.**
`assurer_schema` reconstruit une table figée dont le schéma a dérivé. Elle
reconstruisait `verdicts_figes` seule, en laissant `analyses_figees` pleine :
avec l'incrémental, le bulletin restait « déjà figé », son détail n'était
jamais réécrit, et le compteur annonçait des dépassements dont le détail était
vide. Les deux tables sont **un seul figeage**, et l'une ne se reconstruit plus
sans que l'autre soit vidée. Le contrôle « et refigée sans perte » de
`tests/test_figer.py` est passé au rouge au premier essai — c'est exactement ce
pour quoi il existe.

Sept nouveaux contrôles couvrent l'incrémental (section 3quater de
`tests/test_figer.py`). Les deux suites passent.

**Une réserve, à lever quand ce sera commode.** Les 4 745 lignes présentes ont
été figées **avant** que l'empreinte de moteur existe ; le mécanisme les a
enregistrées comme calculées par le code actuel sans l'avoir vérifié. Contrôle
fait le 11 août 2026 : 40 bulletins refigés sous une version jetable et
comparés colonne par colonne aux lignes stockées — **46 colonnes, 0 écart**. Le
refactor n'a donc déplacé aucune valeur. C'est un échantillon, pas une preuve
sur les 4 745 : un `src/ingerer.py --depts <NN> --refiger` (~33 min, une fois)
rendrait la garantie mécanique.

### 15.6 Le poste dominant a changé — c'est maintenant l'ingestion

Mesuré sur les deux départements, verrou de la base tenu :

| | bulletins | insertion | figeage | **verrou total** |
|---|---|---|---|---|
| Ariège (09) | 1 189 | 15,1 min | 8,0 min | **23,1 min** |
| Haute-Garonne (31) | 1 236 | 20,9 min | 10,4 min | **31,3 min** |
| Hautes-Pyrénées (65), 1 bulletin | 1 | — | — | **0,0 min** |

Soit environ **0,8 à 1,0 s par bulletin inséré** et **0,4 à 0,5 s par bulletin
figé**. Le figeage, qui était tout le problème, n'est plus que le tiers du
coût : sur le 31 il a figé 1 236 bulletins sur un corpus de 7 278, là où
l'ancien code les aurait tous refigés — 7 278 × 0,5 s, soit **une heure au lieu
de dix minutes**.

**Ce qui reste est linéaire en nombre de bulletins, et c'est la bonne
propriété** : le verrou suit désormais la taille du lot, jamais celle du
corpus. Un lot d'un seul bulletin coûte 0,0 min, ce qui était impensable avant.

Extrapolation, et elle est fragile : à ~2 400 bulletins pour 911 communes, les
35 000 communes restantes représenteraient de l'ordre de **90 000 bulletins**,
donc ~22 h de moisson et ~35 h de verrou cumulé, fractionnées en autant de lots
qu'on veut. **Deux départements du Sud-Ouest ne sont pas la France**, et le pire
cas connu — une métropole du calibre de Lyon — n'y figure pas. Le chiffre sert
à décider d'un ordre de grandeur, pas à annoncer une date.

Piste si l'insertion devient gênante : elle se fait bulletin par bulletin, en
`executemany` par bulletin. Un chargement en masse (table temporaire puis un
seul INSERT … SELECT) irait vraisemblablement plus vite, **mais il faudrait
d'abord mesurer où passe réellement la seconde** — rien ne dit aujourd'hui que
c'est l'INSERT plutôt que la lecture des `.jsonl.gz` ou le parsing.

### 15.7 Ce qui reste ouvert

- **Trois états à ne jamais confondre** : moissonné (journal), ingéré (base),
  figé (`analyses_figees` avec sa `version_referentiel`). Seul le troisième est
  citable — c'est le §8bis, et c'est l'erreur qui a fait citer deux jours durant
  un chiffre du Rhône qui n'existait dans aucune version figée. `moisson.py
  --etat` et `ingerer.py --etat` disent les deux premiers, et le disent
  explicitement.
- **`outils/reprendre_collecte.cmd` appelle encore `fetch_departement.py`**,
  donc encore la voie à verrou tenu. À reprendre si la reprise automatique au
  démarrage doit servir au passage à l'échelle.

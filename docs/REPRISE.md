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

---

## 16. Mise à jour du 11 août 2026 — C10 ARRÊTÉS élargi et spécifié, collecte non lancée

Yannick a élargi le chantier C10 : il ne porte plus les seules dérogations mais
**tout acte préfectoral touchant l'eau de consommation, depuis 2016, par
département**, avec dénombrement, et il doit **se déclencher à la fin de la
collecte d'un département**.

**`docs/CHANTIERS.md` §C10 fait foi** — tout est là, y compris la reconnaissance.
Ce qui suit n'en est que le repère.

**Deux décisions prises** : large en collecte et fin en qualification (sans quoi
il n'y a pas de dénominateur) ; l'automatisme s'arrête à la fabrication des
dossiers de candidats, la lecture des actes restant un geste lancé à la main.

**Reconnaissance du Tarn faite le 11 août** — quatre pages consultées, **un seul
recueil téléchargé et sondé**. Ce qu'elle établit :

- l'archive du RAA du Tarn **remonte à 2005** : la profondeur, qui était le
  risque n° 1, n'en est pas un ici ;
- les recueils sont **du texte extractible**, pas des scans — 32 pages,
  65 189 caractères, zéro page vide sur celui qui a été sondé ;
- **le sommaire est structuré** : service, identifiant, intitulé, longueur, page
  de début. Le découpage recueil → actes se fait là, et nulle part ailleurs —
  les motifs d'en-tête habituels sont absents du corps ;
- **le bruit dominant est la sécheresse**, et il est mesuré : l'acte sondé porte
  91 fois « restriction » et 29 fois « eau potable » pour **zéro** « consommation
  humaine » et **zéro** « agence régionale de santé ». Un filtre par mots isolés
  ne tient pas ;
- **il n'existe aucun raccourci national** : la donnée ministérielle sur les
  dérogations n'est plus publiée depuis 2012.

**Trois fichiers écrits, aucun code** : `docs/CHANTIERS.md` §C10 réécrit,
`referentiel/motifs_arretes.csv` (le pré-filtre, versionné parce qu'éditorial) et
`docs/CONSIGNE_QUALIFICATION_ARRETE.md` (le brief d'agent). La forme des
collecteurs dépend de ce que le premier moissonnage mesurera : l'écrire avant
serait du travail à jeter.

**Ce qui n'est pas fait, et ne doit pas être présenté autrement** : rien n'a été
moissonné, aucun acte n'a été qualifié, `referentiel/arretes_eau.csv` n'existe
pas encore.

### 16.1 Le sourçage juridique est fait — fiche `REG-09`, 11 août 2026

Agent de fond `opus`, ~169 000 tokens, une heure. La fiche est archivée avec les
sources réglementaires, sa ligne est à `docs/INDEX_SOURCES.md`, et
`referentiel/motifs_arretes.csv` a été refondu sur ce qu'elle apprend.
**`docs/CHANTIERS.md` §C10 fait foi** ; le détail des cinq conséquences y est.

**Deux affirmations ont été recontrôlées à la main sur Légifrance** avant d'être
versées, parce qu'elles portent tout le reste : R. 1321-34 est bien abrogé
**avec effet au 1er janvier 2024**, et la seconde dérogation est bornée à trois
ans pour les seuls cas 1° et 2°. Les deux tiennent.

Ce qu'il faut retenir au niveau de ce fichier :

- **le dénombrement d'arrêtés sera structurellement minorant** — le silence de
  l'administration vaut acceptation au bout de quatre ou six mois, donc une
  dérogation peut exister sans arrêté publié. À dire partout où le chiffre
  paraît ;
- **le plafond cumulé passe de neuf à six ans au 1er janvier 2024** : une
  rupture datée traverse la période étudiée depuis 2016 ;
- **l'objet d'une dérogation est l'unité de distribution, pas la commune** ;
- **il n'existe pas de dérogation bactériologique** — c'est un contrôle, pas une
  précision ;
- **le visa discrimine mieux que le corps du texte** : `R. 1321-31` pour une
  dérogation, `R. 1321-29` pour une restriction sanitaire, le code de
  l'environnement pour la sécheresse.

**Réserve principale** : **aucun arrêté de dérogation postérieur au 1er janvier
2024 n'a été lu.** Le régime a changé à cette date, le pré-filtre est calé sur
des actes de l'ancien régime, et il faudra le recaler.

### 16.2 Le moissonneur est écrit — l'inventaire du Tarn est INTERROMPU

`src/raa_moisson.py` et `referentiel/sources_raa.csv` sont écrits et commités.
Le module **n'importe jamais `duckdb`**, vérifié à l'exécution : la base reste
libre. Deux gestes, et le premier ne télécharge aucun fichier — l'inventaire
relève l'adresse, la taille et la date de chaque PDF en ne lisant que des pages
HTML, parce qu'un recueil mensuel peut peser plus de 70 Mo et qu'on ne lance pas
un téléchargement départemental sans avoir vu le chiffre.

**L'inventaire n'est pas allé au bout.** Il a couvert **les six premiers mois de
2016 — 88 fichiers pour 62 pages de recueil** — puis la **plateforme des sites
de préfecture a cessé de répondre**, y compris sur `tarn-et-garonne.gouv.fr`
que le projet n'avait jamais sollicité. Légifrance et Hub'Eau répondaient au
même moment : ce n'est pas notre réseau.

**La cause est indéterminée** — indisponibilité de la plateforme, ou mise à
l'écart de notre adresse après quelques dizaines d'appels. Ne pas trancher sans
l'avoir constaté (§2.4). **Décision : on s'arrête, sans contournement d'aucune
sorte.** Détail, chiffres et conséquences : `docs/CHANTIERS.md` §C10, mise à
jour du 11 août, qui fait foi.

**Deux défauts trouvés et corrigés au passage**, tous deux du genre que le dépôt
a déjà payé : un mois était marqué vu alors qu'un de ses recueils avait échoué —
la relance l'aurait sauté et le recueil aurait manqué **en silence**, comme les
quatre communes du 28 (§10.1) ; et une seule page injoignable faisait tomber
tout l'inventaire, alors que `src/journal.py` porte déjà la règle inverse pour
les communes.

### 16.3 La fenêtre passe à six mois — décision du 11 août au soir

Décision de Yannick, après la mesure de volume : **on travaille les six derniers
mois, pas dix ans.** « On ne va pas générer des centaines de Go pour rien. On se
focus sur le récent, le maintenant. […] l'objectif reste de publier le site. »

Le défaut de `--depuis` est passé à **`2026-02`**, la borne se lit au mois, et
elle se lit **sur le chemin du recueil** — jamais sur la date de mise en ligne
annoncée par le site, qui vaut « 09/06/2016 » pour le recueil de janvier 2016 et
daterait faux.

**La conséquence à ne jamais perdre de vue, parce qu'elle n'est pas
symétrique** : la fenêtre courte couvre bien **les restrictions de
consommation** — actes courts et datés — et **manque les dérogations en
vigueur**, qui durent jusqu'à trois ans renouvelables une fois et ont donc été
signées avant. On pourra écrire « voici les restrictions prononcées ces six
derniers mois » ; on ne pourra **pas** écrire « voici les dérogations en
vigueur ». Le stock reste une question ouverte, rangée, pas abandonnée.

**Rien n'a pu être relancé** : la plateforme des préfectures refusait toujours
la connexion au moment de l'écriture, y compris sur `robots.txt`.

**La suite, dans l'ordre** : une requête de test quand la plateforme répond ;
lire `robots.txt`, qui n'a jamais pu l'être ; l'inventaire des six derniers mois
à débit nettement plus bas — `--pause` existe pour cela et ne se baisse jamais ;
puis les trois premiers actes qualifiés, compteurs relevés, montrés — feu vert
avant le lot.

---

## 17. Incident du 11 août 2026 — une ingestion détruit le figeage du corpus

**À lire avant de retoucher `figer.py`, `build_db.py` ou `common.py`.**

### 17.1 Les faits

`py -X utf8 src/ingerer.py --depts 32,47,64,65,82` a versé ses 2 196 bulletins,
puis **effacé les 7 279 lignes de `analyses_figees`** et commencé à tout
recalculer. Le processus est mort au bulletin 3 780 (code de sortie 127,
inexpliqué à ce jour). Le corpus s'est retrouvé **dans un état pire qu'avant la
commande** : 9 475 prélèvements en base, 3 780 figés, et le figeage complet
d'avant définitivement perdu.

Aucune donnée brute n'a été perdue : le cache brut est intact, et c'est lui qui
a permis de tout refaire.

### 17.2 La cause, et elle n'est pas où on la cherche

À 15 h 54, une **autre session** a ajouté `departements_publies()` à
`src/common.py` — une fonction éditoriale, **sans le moindre effet sur un
verdict**. `figer.version_moteur()` hache les octets de `figer.py`,
`build_db.py` et `common.py` : il a vu changer le fichier, en a conclu que le
calcul avait changé, et a forcé un refigeage complet.

Le principe est juste : deux calculs sous une seule `version_referentiel`
seraient invisibles, et c'est le pire cas du §8bis. **La réponse était fausse
sur quatre points**, tous corrigés :

| défaut | ce qui est fait maintenant |
|---|---|
| détruire le figeage **d'office** | `figer()` lève `MoteurChange`, **n'écrit ni n'efface rien**. Refiger se demande (`--refiger`) |
| effacer **tout en amont**, donc corpus amputé si interruption | remplacement **bulletin par bulletin** : une interruption laisse un corpus mixte, mais rien n'est perdu |
| progression **non flushée**, invisible si le processus meurt | `flush=True` — l'incident a dû être reconstitué en interrogeant la base |
| empreinte trop grossière | **inchangée et assumée** : elle ne peut pas distinguer un ajout inoffensif d'un changement de calcul. Mais elle ne détruit plus rien, donc son excès de zèle ne coûte qu'un refus explicite |

La règle de fond, et elle dépasse ce fichier : **détruire une sortie figée ne
doit jamais être un effet de bord.** C'est un geste qu'on demande, jamais un
geste qu'on subit.

### 17.3 La contrainte que cela crée, et qu'il faut connaître

**Pendant une campagne de collecte, `figer.py`, `build_db.py` et `common.py`
sont gelés.** Toute modification de l'un des trois — même un commentaire, même
une fonction sans rapport — change l'empreinte et fait refuser le prochain
figeage jusqu'à un `--refiger` complet, soit ~100 min sur le corpus actuel.

Ce n'est pas un défaut à corriger : c'est le prix de la garantie. Mais il se
sait à l'avance, et il se dit aux autres sessions qui travaillent en parallèle.

### 17.4 Réparation, et coût réel du refigeage complet

```
figé : 9475 nouveau(x) bulletin(s) — 9475 au total sous f3e1d448101f
verrou de la base tenu 101.9 min
```

Vérifié après coup : 9 475 prélèvements, 9 475 figés, 9 475 avec leur détail,
**écart nul**, et l'empreinte enregistrée égale l'empreinte courante.

**Un refigeage complet coûte donc ~0,65 s par bulletin** (101,9 min pour
9 475), contre ~0,41 s en figeage incrémental — le remplacement au fil ajoute
deux DELETE par bulletin. C'est le prix de ne plus jamais amputer le corpus, et
il est payé une fois par changement de moteur, pas à chaque ingestion.

### 17.5 Ce qui reste inexpliqué

**Le code de sortie 127.** C'est « commande introuvable » pour un shell, ce qui
n'a aucun sens pour un processus qui tournait depuis vingt minutes. Deux
hypothèses ont été examinées et écartées : un figeage concurrent d'une autre
session (les journaux montrent que ses figeages portaient sur une base
temporaire de test, jamais sur `data/eau.duckdb`), et une contention DuckDB
(un second écrivain échoue à ouvrir, il ne tue pas le premier).

Le refigeage suivant, plus long et plus lourd, s'est terminé en code 0. **C'est
donc un incident isolé sans cause établie, et il est écrit ici comme tel** — pas
comme un mystère résolu. S'il se reproduit, ce sera un signal, et cette note
sera le premier point de comparaison.

### 17.6 État du corpus au terme de la journée

**9 475 bulletins figés sous `f3e1d448101f`, écart nul.**

| dept | bulletins | couverture | cas |
|---|---|---|---|
| Ariège (09) | 1 189 | 93,2 % | 5 |
| Eure-et-Loir (28) | 1 611 | 90,1 % | 260 |
| Haute-Garonne (31) | 1 236 | 92,3 % | 45 |
| Gers (32) | 897 | 94,4 % | **299** |
| Hautes-Pyrénées (65) | 576 | 92,8 % | 49 |
| Rhône (69) | 1 486 | 75,1 % | 275 |
| Saône-et-Loire (71), partiel | 174 | 86,9 % | 40 |
| Tarn (81) | 1 575 | 93,7 % | 100 |
| Tarn-et-Garonne (82) | 722 | 92,6 % | 116 |

Huit départements entiers, un partiel. **1 189 cas** — des bulletins complets,
déclarés conformes en 2026, qui ne l'auraient pas été il y a dix ans. Le Gers
en porte à lui seul 299 pour 897 bulletins, la proportion la plus forte du
corpus : **à regarder de près, et à ne pas citer avant vérification.**


---

## 18. Mise à jour du 11 août 2026, soir — chapitre sourçage réglementaire

Session parallèle à celle du §17, sur un autre objet : **cinq substances
sourcées en agents de fond**, sans jamais toucher au code ni au référentiel.
Rendus dans `data/etudes/sourcage_C/`.

### 18.1 CORRECTION AU §17.5 — le code de sortie 127 a une cause, et c'est moi

**Le §17.5 tient l'arrêt au bulletin 3 780 pour « un incident isolé sans cause
établie ». Il en a une : j'ai tué le processus.**

Déroulé :

- **16 h 08 min 28** — le processus démarre. Je ne le vois pas partir.
- **~16 h 20** — je cherche à interroger la base pour un dossier de sourçage :
  elle est verrouillée. Je constate un processus Python à ~3,5 cœurs, un journal
  d'écriture de 13 Mo, et le fichier de base passé de 855 à 915 Mo.
- **17 h 20** — je présente les faits à Yannick comme un probable débordement
  d'agent, il tranche « tout arrêter », et j'exécute `Stop-Process -Force`.
- **17 h 26** — un second processus démarre. Cette fois je lis sa ligne de
  commande **avant** d'agir : `ingerer.py --depts 32,47,64,65,82 --refiger`,
  travail légitime d'une autre session. Je n'y touche pas.

**Ce que j'ai mal fait, et c'est la leçon** : j'ai constaté qu'un processus
écrivait dans la base et j'en ai conclu qu'il n'avait rien à y faire, **sans
avoir lu sa ligne de commande**. `Get-CimInstance Win32_Process -Filter
"ProcessId=N"` la donne en une seconde, et elle aurait dit `ingerer.py`. **Un
processus inconnu se lit avant de se tuer** — remonter l'arbre des parents dit
en outre s'il vient d'un terminal ou d'un outil.

Conséquence : le refigeage a été payé deux fois, ~68 min perdues. Rien
d'irréversible, la relance étant en `--refiger`, qui reprend les 9 475 de toute
façon. **Le §17.2 reste entièrement valide** : c'est bien un changement de
`common.py` qui a déclenché le refigeage. Je n'ai causé que son interruption,
pas son déclenchement.

**Le §17.5 est donc clos, pas ouvert.** Si un code 127 réapparaît sans qu'une
session ait tué un processus, ce sera un vrai signal — mais il n'y a pas de
précédent à invoquer.

### 18.2 Les cinq dossiers rendus

| substance | verdict | fait principal |
|---|---|---|
| **Fluoranthène** | C2 pour l'eau distribuée | nommé dans une somme opposable française — mais **eaux brutes**, 1 µg/L, six composés : autre milieu que le corpus |
| **Fréon 113** | C2 | l'OMS ne l'a **jamais examiné** ; absent même de la table des renoncements motivés |
| **Phosphate de tributyle** | C2, **pas** C-g | le SANDRE ne le range dans aucune liste phytosanitaire : la question du caractère pesticide n'est même pas ouverte |
| **Dalapon** | **C-g, le texte répond oui** | « les herbicides organiques » figurent littéralement dans la définition des pesticides ; SANDRE Liste A, pas Liste B |
| **Tétrachlorure de carbone** | C2 | **la somme suisse le capte** — voir 18.4 |

**Aucun ne recommande de verser un seuil. Cinq fois sur cinq.** C'est un
résultat, pas une absence de résultat : dans chaque cas, choisir une valeur
plutôt qu'une autre **produirait** le verdict au lieu de le constater.

Le tétrachlorure de carbone le démontre en une ligne. Maximum du corpus
**0,67 µg/L** : **dépassement** contre la valeur californienne (0,5 µg/L),
**conforme** contre la suisse (2), la japonaise (2), la britannique (3) et le
repère OMS (4). Même eau, même mesure, deux verdicts opposés selon la
juridiction.

Le dalapon porte l'écart le plus large mesuré à ce jour : les seules
juridictions qui le **nomment** sont américaines, à **0,2 mg/L** — deux mille
fois plus permissif que les 0,10 µg/L de la règle européenne de catégorie.

### 18.3 Quatre acquis de méthode, réutilisables hors sourçage

1. **L'appariement par code SANDRE bat la ressemblance de libellé, trois fois
   sur trois.** La fiche d'une somme désigne ses composants par code. L'agrégat
   « Somme de COHV » (7485) liste 14 codes : les deux fréons en sont **absents**,
   le tétrachlorure de carbone y **figure**. Le libellé aurait dit l'inverse
   pour les fréons.
2. **L'arithmétique du bulletin est une preuve de composition d'agrégat.**
   Quand un bulletin porte un agrégat et ses composants, la somme observée dit
   ce que le laboratoire additionne. Vérifié sur `02800129138` :
   benzo(a)pyrène 0,0004 + benzo(b)fluoranthène 0,0005 + fluoranthène 0,007 →
   la somme des 4 vaut 0,0005 (le seul benzo(b)), la somme des 6 vaut 0,0079
   (les trois). C'est une preuve, pas un indice.
3. **La classification SANDRE discrimine le C-g.** « Liste B – Phytosanitaires »
   = AQUAREF renvoie l'arbitrage au gestionnaire, donc question ouverte
   (biphényle). Liste A, ou aucune liste = la question est tranchée (dalapon,
   phosphate de tributyle). **Réserve : la note AQUAREF définissant la Liste A
   n'a pas pu être lue** — une tentative, PDF muet.
4. **La nature d'une valeur ne se déduit jamais de son rang.** L'objectif de
   santé publique californien a été, sur trois dossiers : plus permissif que la
   limite opposable (Fréon 113, 4 mg/L contre 1,2), plus élevé qu'elle
   (dalapon, 0,79 contre 0,2 mg/L), et cinq fois plus bas (tétrachlorure,
   0,1 contre 0,5 µg/L). Sur le plomb il est cinquante fois sous le niveau
   d'action. **Il faut lire ce qu'est chaque valeur, jamais où elle se situe.**

### 18.4 Une somme opposable fermée par une DÉFINITION, pas par une liste

**C'est le résultat qui dépasse les cinq dossiers, et il remet en cause des
conclusions déjà rendues.**

La Suisse fixe **10 µg/L** (ordonnance du DFI, RS 817.022.11, annexe 2) à :

> « Hydrocarbures halogénés, volatils : somme de toutes les substances
> halogénées dont la structure fondamentale comporte entre un et trois atomes
> de carbone et aucun autre groupe fonctionnel »

Toute la doctrine du projet sur les périmètres — *chercher le mot qui ferme la
liste*, « the following five substances » — **suppose des périmètres
nominatifs**. Celui-ci ne l'est pas : il se ferme par une définition
structurale, et attrape donc des substances qu'aucun texte ne nomme.

Deux agents l'ont lu indépendamment. Le second a ouvert le texte officiel
lui-même et relève **deux confirmations internes au texte** : le dichlorométhane
et le 1,2-dichloroéthane y portent la note « *Voir aussi : Hydrocarbures
halogénés, volatils* » — le mécanisme « valeur individuelle **et** comptage dans
la somme » est celui du législateur suisse, pas une interprétation de notre
part. Et la Suisse fixe **en plus** une valeur nominative :
tétrachlorométhane **2 µg/L**.

**CONTRADICTION NON LEVÉE, à trancher avant tout usage.** Le premier agent
annonce l'état au **01/02/2024**, vérifié par double extraction ; le second n'a
pu ouvrir qu'un document portant « **État le 1er mai 2018** », le site officiel
n'ayant jamais répondu (JavaScript, 4 URL essayées). **Les valeurs suisses sont
donc établies sur l'état 2018 et `a_verifier` sur l'état en vigueur.** Le
dossier Fréon 113 est à corriger sur ce point.

**Ce que ça oblige à faire** : les dossiers rendus sur les organohalogénés
volatils — Fréon 113, Fréon 11, trichloroéthane-1,1,1, dichloroéthane-1,1,
dichloroéthylènes-1,2, dichloroéthylène-1,1, dibromométhane, tétrachlorure de
carbone — concluent tous « aucune valeur opposable identifiée ». **À relire un
par un contre cette définition avant toute publication.**

### 18.5 Deux défauts du moteur, confirmés en base APRÈS le refigeage

**Ils survivent au refigeage : ce sont le référentiel et les règles de famille
qu'il faut corriger, pas le calcul.**

1. **Quatre HAP sont captés par la règle `pesticide_individuel_0_1`** —
   benzo(b)fluoranthène (1116), benzo(k)fluoranthène (1117),
   benzo(g,h,i)pérylène (1118), indéno(1,2,3-cd)pyrène (1204). Chacun reçoit
   0,10 µg/L en grille 2026, sur 297 mesures. **Ce ne sont pas des pesticides,
   et la directive ne leur donne aucune limite individuelle** : seule leur somme
   (2033) en a une. C'est exactement le cas que le §4 de `CLAUDE.md` demande de
   surveiller sur `v_regle_famille_appliquee`.
   Aucun faux dépassement aujourd'hui — maximum quantifié 0,0005 µg/L, deux
   cents fois sous le seuil — mais le piège est armé, et ces quatre lignes
   gonflent le dénominateur de couverture comme si elles avaient été jugées.
   **Correctif : quatre lignes `dans somme (2033)`, symétrique de ce qui a été
   fait le 10 août pour les cinq acides haloacétiques.**
2. **Le benzo(a)pyrène (1115) est jugé par la seule limite déclarée** —
   0,010 µg/L, grille `declare`, 297 mesures. Il a pourtant sa propre valeur
   dans la directive. Conséquence du §2.8 : une limite seulement déclarée ne
   produit jamais de verdict 2016 ni de bascule, donc **cette substance ne peut
   pas apparaître dans la démonstration centrale du projet**, et elle n'est pas
   jugée du tout sur un bulletin où la limite n'est pas déclarée.
   **Correctif : une ligne sourcée.**

Les deux correctifs changent le référentiel, donc la version, donc **imposent un
refigeage complet (~100 min, §17.4). Les faire ensemble, pas l'un après
l'autre.**

### 18.6 Reliquat en base : 3 209 lignes figées sous l'ancienne version

`analyses_figees` porte 9 475 lignes sous `f3e1d448101f` **et 3 209 sous
`435b9a089f1d`**, antérieures aux six lignes des acides haloacétiques. Rien de
faux n'est publiable — chaque ligne porte sa version, et la vitrine lit la
courante — mais toute requête qui oublie de filtrer mélange deux générations de
verdicts. Purge mécanique, quelques secondes, aucun recalcul.

Observé au passage, à vérifier quand `figer.py` sera repris : **9 475 bulletins
figés pour 9 455 marqués complets**, soit 20 de plus.

### 18.7 Le coût réel d'un dossier — le chiffre du §0 de la consigne est faux

`docs/CONSIGNE_SOURCAGE.md` §0 fonde la règle « un seul agent à la fois » sur
une mesure de **~140 000 tokens par substance**. Mesures de la soirée :

| dossier | tokens | outils | durée |
|---|---:|---:|---:|
| Fluoranthène | 247 305 | 140 | 36 min |
| Fréon 113 | 197 880 | 76 | 18 min |
| Phosphate de tributyle | 180 886 | 64 | 17 min |
| Dalapon (3ᵉ tentative) | 130 292 | 59 | **12 min** |
| Tétrachlorure de carbone | 125 061 | 61 | 15 min |

**881 424 tokens pour cinq dossiers, soit ~176 000 en moyenne**, jusqu'à
247 000 — et **trois tentatives abandonnées en plus, au coût non mesuré**. Le
chiffre de 140 000 sous-évalue de 25 % en moyenne et de 75 % dans le pire cas.
**À corriger dans la consigne.**

Corrélation utile : les deux dossiers les plus chers sont les deux qui ont fait
le plus d'appels d'outil (140 et 76). Le plus rapide (12 min, 59 appels) est
celui qui portait les règles de cadence du 18.8.

### 18.8 Trois agents ont tourné à vide — cause probable et correctif appliqué

Trois tentatives (dalapon deux fois, tétrachlorure, éthylbenzène) ont écrit une
fois puis **plus rien pendant 1 h 30 à 2 h 15**, sans aucun processus vivant sur
la machine. Aucun diagnostic direct n'est possible : **les fichiers de
transcription des agents font 0 octet**, y compris pour les agents qui
aboutissent. Le seul signal disponible est la date de modification du fichier de
sortie.

Hypothèse la plus probable : un appel réseau qui ne revient pas. Même schéma que
le blocage sur la commune 69063 (§14.7) — un silence prolongé sans message
d'erreur signifie que le processus n'est pas dans une boucle de reprise.

**Correctif appliqué au brief, et il a marché** : le dalapon est passé de deux
échecs à un dossier rendu en 12 minutes.

1. **écrire dans le fichier après CHAQUE source lue**, avant de passer à la
   suivante ;
2. **une seule tentative par URL** : une page qui ne répond pas est notée
   « inaccessible » dans le tableau des juridictions, et on passe ;
3. **budget annoncé de 30 minutes**, avec les mesures du 18.7 comme repère ;
4. **ordre de travail imposé**, avec une écriture entre chaque étape.

**À porter dans `docs/CONSIGNE_SOURCAGE.md` §6**, qui demande déjà d'écrire tôt
mais pas d'écrire *à chaque source*. C'est la nuance qui fait la différence, et
elle est mesurée.

### 18.9 Deux erreurs de comptage de ma part, dans des briefs d'agents

Dans le brief du phosphate de tributyle j'ai écrit « six ou sept des quinze
quantifications dépassent 0,10 µg/L » sans avoir les valeurs sous les yeux :
**il y en a une**. Dans celui du dalapon j'ai écrit « six des treize » en ayant
les treize valeurs recopiées dans le brief lui-même : **il y en a huit**. Les
deux agents ont relevé l'écart, rien ne s'est propagé dans un dossier.

**C'est la règle 1 de la consigne enfreinte dans le document qui la porte.** Un
compte se compte, il ne s'estime pas — y compris quand il ne sert qu'à cadrer un
agent, parce qu'un brief est lu comme un fait établi.

### 18.10 Sur la numérotation de ce fichier

**FAIT le 11 août 2026 au soir, sur accord de Yannick — plus rien ne tournait.**
Deux sections portaient le numéro 16 : « C10 ARRÊTÉS élargi » et « Incident du
11 août », écrites par deux sessions parallèles. Renumérotation :

| avant | après |
|---|---|
| §16 C10 ARRÊTÉS élargi | **inchangé, §16** |
| §16 Incident / ingestion | **§17**, sous-sections 16.1 à 16.6 → 17.1 à 17.6 |
| §17 sourçage réglementaire | **§18**, sous-sections 17.1 à 17.11 → 18.1 à 18.11 |

27 lignes touchées, renvois internes compris. **Et le pointeur de `CLAUDE.md`
§6, qui renvoyait à `docs/REPRISE.md` §16 pour l'incident, a été corrigé en
§17** — c'était le seul renvoi hors de ce fichier.

### 18.11 État matériel au terme de cette session

- **Base libre**, cohérente, 9 475 prélèvements, refigeage complet vérifié.
- **Aucun agent en vol**, aucun processus Python hors les deux serveurs du site
  (port 8765, vivants depuis 9 h 50).
- **Aucun fichier du dépôt modifié par cette session hors ce §17** : le
  référentiel, `common.py`, `figer.py` et `build_db.py` sont intacts. Sauvegarde
  du fichier avant ajout : `docs/REPRISE.md.bak-avant-17`.
- Cinq dossiers dans `data/etudes/sourcage_C/`, plus un répertoire
  `_interrompus_2026-08-11/` contenant l'état exact des trois tentatives
  arrêtées — dont **`ethylbenzene_INTERROMPU`, 11,5 Ko, verdict rédigé et dix
  sections structurées, avec la valeur guide OMS 0,3 mg/L et sa mention « (C) »
  signalant que goût et odeur peuvent être affectés en dessous de cette
  valeur. Celui-là est à terminer, pas à refaire.**

### 18.12 EXÉCUTÉ le 11 août 2026 au soir — les neuf points, sur décision de Yannick

Décisions prises point par point et appliquées dans la foulée.

**Six lignes versées au référentiel, aucune valeur écrite sans lecture en source
primaire par la session principale elle-même** — pas par un agent, pas de
mémoire :

| lignes | contenu | source lue |
|---|---|---|
| 1116, 1117, 1118, 1204 | benzo(b)fluoranthène, benzo(k)fluoranthène, benzo(g,h,i)pérylène, indéno(1,2,3-cd)pyrène → `dans somme (2033)`, aucun seuil individuel | REG-01 annexe I partie B **et** REG-02 annexe I d'origine, extraites et lues |
| 1115 | benzo(a)pyrène → `limite` **0,010 µg/L en 2016 comme en 2026** | idem, valeur identique dans les deux textes |
| 2094 | dalapon → `vigilance`, **aucun seuil**, `a_verifier` | REG-01, définition des pesticides |

**Le périmètre des quatre est confirmé mot pour mot dans les deux grilles**, ce
qui n'était pas acquis : directive 2020/2184, « *Sum of concentrations of the
following specified compounds: benzo(b)fluoranthene, benzo(k)fluoranthene,
benzo(ghi)perylene, and indeno(1,2,3-cd)pyrene* » ; arrêté de 2007 d'origine,
« *Pour la somme des composés suivants : benzo[b]fluoranthène,
benzo[k]fluoranthène, benzo[ghi]pérylène, indéno[1,2,3-cd]pyrène* ». **Même
périmètre de quatre substances en 2007 et aujourd'hui.** Et l'annexe II de 2007
porte bien, elle, la somme de **six** composés à 1 µg/L pour les **eaux
brutes** — le dossier fluoranthène est confirmé indépendamment.

Le contrôle de forme écrit pour l'occasion a **refusé une première version** :
un point-virgule dans une cellule de la ligne 1115. C'est l'erreur qui a décalé
quatorze lignes puis quatre autres par le passé, attrapée cette fois avant
écriture.

**RÉSULTAT PARTIEL, à connaître — la correction des quatre HAP n'a produit que
la moitié de l'effet voulu.** Vérification en base après chargement :

- la règle `pesticide_individuel_0_1` ne les capture plus : **zéro ligne** dans
  `v_regle_famille_appliquee`. Ce défaut-là est corrigé ;
- **mais les quatre reçoivent maintenant 0,10 µg/L par la limite déclarée par la
  source** (`grille_applicable = 'declare'`). Le moteur retombe sur le troisième
  niveau de la hiérarchie du §2.8, et **notre ligne à seuils vides ne l'en
  empêche pas**.

Comparaison qui éclaire le mécanisme : les cinq acides haloacétiques, corrigés
le 10 août de la même façon, sortent bien en `grille = aucune`. **La différence
ne vient pas du correctif mais de la source** : SISE-Eaux ne déclare aucune
limite sur les cinq acides, et déclare `<= 0,1 µg/L` sur chacun des quatre HAP.

**Le fait est intéressant en soi, et il est éditorial** : l'administration
applique individuellement, dans ce qu'elle publie, la valeur que la directive ne
fixe que pour la somme. Conséquence pratique atténuée — une limite seulement
déclarée ne produit ni verdict 2016 ni bascule (§2.8) — mais elle produit
toujours un « conforme » individuel contre un seuil que le texte ne fixe pas.

**Question ouverte, à trancher par Yannick, et elle touche le moteur** : une
ligne du référentiel portant `dans somme` doit-elle **bloquer** le repli sur la
limite déclarée ? Ce serait dire que notre référentiel prime sur la déclaration
de la source pour affirmer une **absence** de seuil. C'est une décision de
méthode, pas un correctif technique — et elle demande de toucher les vues, ce
qui impose à son tour un refigeage complet.

**Autres points exécutés :**

- **la fiche de relecture de la somme suisse est écrite** :
  `data/etudes/sourcage_C/RELECTURE_somme-suisse_2026-08-11.md`. Elle rassemble
  les huit dossiers concernés, la définition suisse, les trois précautions de
  méthode et ce qu'il reste à décider. Écrite parce que « relire les dossiers »
  n'est pas une consigne actionnable si on ne dit pas où ils sont ;
- **règle arrêtée par Yannick sur les textes étrangers : on se réfère toujours à
  la version la plus récente en vigueur.** Elle tranche la contradiction
  2018 / 2024 sur l'ordonnance suisse dans son principe — reste à ouvrir la
  version en vigueur, Fedlex n'ayant jamais répondu ;
- **`CONSIGNE_SOURCAGE.md` corrigée sur deux points** : la règle « un agent à la
  fois » est reformulée telle que Yannick l'énonce — elle porte sur ce qu'on peut
  **suivre**, pas sur ce que ça coûte, avec jusqu'à trois agents sur décision
  explicite et **l'obligation de surveiller la date de modification du fichier de
  sortie** ; et le §6 porte désormais la règle d'écriture **après chaque source**,
  avec son effet mesuré ;
- **le dossier éthylbenzène est relancé** pour être terminé, pas refait ;
- **la purge des générations figées est reportée à après le prochain refigeage**,
  et c'est délibéré : le référentiel ayant changé, les 9 475 lignes actuelles
  vont elles aussi devenir une génération périmée. Une seule purge au lieu de
  deux.

**État à la clôture** : le référentiel porte 94 paramètres, la base est
cohérente et libre, **et elle attend un refigeage complet** — les six lignes
nouvelles ne produiront leurs effets sur les sorties figées qu'après lui.


### 18.13 Sixième dossier — l'éthylbenzène, et le quatuor BTEX bouclé

Terminé, pas refait : l'agent a repris le fichier interrompu et l'a complété.
**92 042 tokens, 29 appels d'outil, 7 minutes** — le tiers du coût moyen des
cinq autres. **Reprendre un dossier interrompu coûte trois fois moins que le
relancer de zéro** : à retenir avant de jeter un travail à moitié fait.

**Verdict C2, assorti d'un C-g organoleptique**, et une recommandation de ne
verser aucun seuil — la sixième consécutive.

**Le résultat éditorial : quatre substances, un seul paquet analytique, quatre
régimes.** Benzène, toluène, éthylbenzène, xylènes sortent de la même injection,
sur le même prélèvement, au même instant. **Seul le benzène peut produire une
non-conformité en France.** Les trois autres sont des indéterminés — mesurés,
parfois quantifiés, jugés par rien. Et **aucune somme BTEX opposable n'existe** :
l'OMS écrit que ces substances s'évaluent « individually ».

Lu en source primaire : fédéral américain **0,7 mg/L**, ligne
`(11) 100-41-4 | Ethylbenzene | 0.7` du 40 CFR 141.61(a) ; **absence** de
l'éthylbenzène au 40 CFR 143.3, les recommandations américaines fondées sur le
goût et l'odeur ne portant qu'un paramètre « Odor — 3 threshold odor number »
non nominatif, et se qualifiant elles-mêmes de *reasonable goals* ; TrinkwV 2023
annexe 2 lue intégralement, **Ethylbenzol absent**, le benzène y étant à
0,0010 mg/L.

**Quatrième configuration du couple californien**, et elle achève la
démonstration : limite opposable 0,3 mg/L et objectif de santé publique
0,3 mg/L, **identiques**. Sur quatre dossiers, ce couple a été tour à tour plus
permissif que la limite, plus élevé, cinq fois plus bas, et égal. **Le rang ne
se déduit jamais — la nature se lit.**

**Axe sanitaire contre acceptabilité** : les deux quantifications du corpus,
0,056 et 0,78 µg/L, sont 5 357 et 385 fois sous la valeur à fondement sanitaire,
et **sous le plus bas seuil d'odeur relevé (2 µg/L)**. À ces concentrations
l'eau ne sent rien et n'est jugée par rien.

**Non établi, déclaré comme tel** : classement CIRC laissé **vide** plutôt que
déduit d'une substance voisine ; aucun texte trouvé imposant nominativement
cette recherche au programme français ; six juridictions non instruites, dont le
Canada inaccessible (403 sur deux adresses, valeurs de moteur de recherche
écartées à dessein).

**Total de la journée : six dossiers, 973 466 tokens**, plus trois tentatives
abandonnées au coût non mesuré.

### 18.14 Décision de méthode — toute substance mesurée reçoit une attribution

**Décision de Yannick, 11 août 2026 au soir. Note écrite :
`docs/METHODE_ATTRIBUTION.md`. Rien n'est implémenté.**

Point de départ, chiffré ce soir : **327 592 mesures sur 240 libellés ne
reçoivent aucun verdict** — une mesure du corpus sur dix — et **environ 76 000
d'entre elles sont des quantifications**. Le laboratoire a cherché, il a trouvé,
et la sortie du projet n'en dit rien.

Principe arrêté : *« si la substance ressort, on doit lui donner une attribution,
même si cette attribution est rien ne se prononce sur cette partie »*.

Quatre attributions, une par situation réelle : **jugé** (trio actuel conforme /
dépassement / indéterminé) · **compte dans un ensemble** · **rien ne se
prononce**, avec deux sous-états *établi par un dossier* et *non encore instruit*
· **jugé sur la seule déclaration de l'administration**.

**Le mot « vigilance » a été écarté à dessein** : il qualifie déjà une substance
dont la norme **a bougé ou est contestée** (chlorothalonil, dalapon). Ces cas
disent « ça bouge », le cas nouveau dit « c'est muet » — deux faits sous un même
mot, l'erreur que le projet évite partout ailleurs.

**Effet de bord qui résout la question ouverte du 18.12** : « compte dans un
ensemble » **est une réponse, pas un vide**, donc elle prime sur la limite
déclarée par la source. Les quatre hydrocarbures aromatiques cessent d'être notés
individuellement contre une valeur que la directive ne fixe que pour leur somme.
L'arbitrage de hiérarchie devient inutile.

**Deux points de vigilance portés dans la note** :

1. **la rédaction**, et c'est le plus délicat. « Rien ne se prononce » ne doit
   jamais se lire comme un feu vert. Yannick formule l'intention ainsi :
   *« attention, dans votre eau conforme vous buvez déjà toute cette soupe
   chimique »*. **L'intention est juste, le mot ne l'est pas** : « soupe
   chimique » est un qualificatif de notre cru, donc la seule prise par laquelle
   ce travail est attaquable (§2.1, §2.2). La version factuelle est **plus dure,
   pas plus douce** — « cette eau est déclarée conforme, elle contient N
   substances de synthèse quantifiées, dont M que la réglementation ne juge pas,
   vérification faite sur les textes nommés » — et elle ne se conteste pas. Test
   à appliquer avant publication : *si on retire tous les adjectifs, reste-t-il
   un fait daté et sourcé ?*
2. **l'attribution doit être produite par le moteur et figée**, pas déduite à
   l'affichage — sinon deux écrans peuvent dire deux choses du même bulletin,
   ce que le figeage existe pour empêcher. Cela touche les vues, donc **impose un
   recalcul complet**.

**Écart à réconcilier avant tout chiffre public** : la vue de diagnostic compte
215 libellés sans seuil, la vue des verdicts en compte 240. Les deux ne filtrent
pas pareil.

**Ce que ça ouvre** : les dossiers de sourçage cessent d'être un travail interne
et deviennent la pièce justificative d'une attribution affichée. Et les deux
sous-états de « rien ne se prononce » rendent **l'avancement public et honnête à
chaque étape** d'un chantier de plusieurs mois — ce qui est démontré est marqué
démontré, ce qui ne l'est pas est marqué comme tel.


---

## 19. État au 12 août 2026, 18 h 30 — PÉRIMÉ, voir le §22

> **Ne plus lire cette section comme l'état courant.** Elle a été
> remplacée par le **§22**, écrit le 13 août au soir. Plusieurs de ses
> affirmations sont infirmées depuis : le rattachement Sicoval (§20.2),
> la question du point de prélèvement (§20.7), le décompte des
> candidats à l'alerte (§20.15) et « le département le plus
> profondément collecté » (§20.16). Elle est conservée pour l'histoire
> du chantier, pas pour agir.

**Cette section remplace le §18.11 sur l'état matériel. À lire en premier.**

Le dépôt **n'est pas versionné** (`git rev-parse` échoue) : aucun commit n'a pu
clore cette session. Le fichier de reprise est donc la seule mémoire.

---

### 19.1 CE QUI TOURNE, ET CE QU'IL FAUT EN FAIRE

**1. L'ingestion de PACA — en cours, interruptible sans coût.**

```
py -X utf8 src/ingerer.py --depts 04,05,06,13,24,26,33,46,83,84,99 --sans-figer
```

12 645 bulletins à verser, environ 6 h au rythme mesuré (35/min). Elle en était
au cinquième département sur onze à 18 h 30. **Elle saute ce qui est déjà en
base** : la tuer et relancer la même commande reprend où elle en était. Yannick
ne pouvant pas laisser la machine allumée la nuit, c'est le geste prévu.

**2. Le refigeage complet — À LANCER DEMAIN MATIN, d'une traite.**

```
py -X utf8 src/ingerer.py --tous --refiger > data/journal/refigeage_2026-08-13.log 2>&1
```

Environ **6 heures sur ~24 000 bulletins**, base verrouillée. `figer.py` n'a pas
d'option de refigeage, il faut passer par l'ingesteur, et il exige `--tous`.

**CE GESTE NE SE DÉCOUPE PAS.** Avec `--refiger`, tous les bulletins sont
repris ; sans, le figeage refuse tant que l'empreinte du moteur ne correspond
pas — et elle n'est écrite qu'à la toute fin. Un refigeage interrompu se
relance donc depuis zéro. C'est le garde-fou du §17, il fonctionne comme prévu.

**Pourquoi ce refigeage est nécessaire** : le filtre du détail figé a été élargi
(§19.2). Sans lui, l'attribution « rien ne se prononce » reste invisible.

**3. Après le refigeage, dans l'ordre :**

- **purger les générations périmées de `couverture_communes`** — elle en porte
  **quatre** (`d0fb678dcbe2` 4 151 lignes, `f3e1d448101f` 3 004, `435b9a089f1d`
  687, `a74139a57d87` 29). La purge du 12 août ne regardait qu'`analyses_figees` ;
- **ajouter les six départements PACA** à `referentiel/departements_publies.csv` :
  04 (198 communes), 05 (162), 06 (163), 13 (119), 83 (153), 84 (151). **Les six
  passent `--termine` à zéro**, vérifié le 12 août ;
- **régénérer les dossiers de faits** — leurs comptes changent de sens avec le
  filtre élargi (§19.2) ;
- **reconstruire la vitrine** : `py -X utf8 site/build_site.py`.

---

### 19.2 LE FILTRE DU FIGEAGE A ÉTÉ ÉLARGI — conséquence à connaître

`figer.py` ne filtrait que les mesures ayant un seuil de comparaison
(`notee OR seuil_strict IS NOT NULL OR hors_reference`). **Le détail figé est
désormais la photographie ENTIÈRE du bulletin.**

Motif, mesuré : le moteur calculait l'attribution « rien ne se prononce, non
instruit » sur **413 050 mesures**, et le détail figé n'en conservait que
**364** — 0,1 %. La population qu'on venait de décider de rendre visible était
exactement celle que le figeage écartait.

**Conséquence : tout compte tiré de `verdicts_figes` change de sens.** Il portait
sur « les mesures notées », il porte sur « les mesures ». Volume : +11 %
(~450 000 lignes sur 4,2 millions). **Les dossiers de faits en tirent des
chiffres — les régénérer après le refigeage.**

---

### 19.3 LA DÉCOUVERTE DU 12 AOÛT — conformité sur panel réduit

**Le chantier éditorial le plus fort de la journée.** Tout est dans
`data/etudes/conformite_sur_panel_reduit/` : un README de méthode, l'analyse
d'ensemble `ANALYSE_2026-08-12.md`, 18 dossiers commune par commune, une
synthèse CSV, et 21 PDF dans `pdf/`.

**Le fait :** sur 37 communes instruites, **18 portent au moins un paramètre qui
était en dépassement à la dernière analyse complète et n'a plus été mesuré
depuis au moins deux ans**. 49 paramètres. 555 contrôles de routine depuis. Le
plus ancien abandon remonte à **119 mois**.

**Sur les 61 analyses complètes de ces 18 communes, 55 sont non conformes — 90 %.
Pour 15 communes sur 18, elles le sont TOUTES.**

**Ce qui cesse d'être mesuré :** l'atrazine déséthyl (13 communes), le **total
des pesticides analysés** (12), l'atrazine déséthyl déisopropyl (6), l'atrazine
(4), l'ESA métolachlore (4). Des métabolites d'un herbicide interdit en 2003.

**Le mécanisme le plus important, et il est neuf :** le « total des pesticides »
est une **limite opposable** (0,5 µg/L) et c'est une **somme**. Cesser de mesurer
les termes rend l'agrégat **incalculable**. Le paramètre le plus protecteur du
dispositif s'éteint quand ses composants s'éteignent.

**Une hypothèse séduisante ÉCARTÉE, à ne pas ressortir** : « vingt ans après
l'interdiction ». Les arrêts s'étalent de 2016 à 2023 — Oinville en 2016, Gas et
Nottonville en 2018, Varize et Louville en 2019. Il n'y a pas de règle des vingt
ans, il y a un cas qui y ressemble (Thiville). **C'est le piège du Tarn, §2.11.**
Ce que la chronologie montre : des **pics en 2018, 2020 et 2023**, compatibles
avec des renouvellements de marché — *jamais « causés par »*.

**Prudence de lecture, obligatoire :** 16 des 18 communes sont en Eure-et-Loir,
mais l'Eure-et-Loir pèse 22 des 37 instruites parce que c'est le département le
plus profondément collecté. **Un département mieux documenté produit
mécaniquement plus de candidats** (§2.11). Cette carte ne se lit pas comme une
carte de France.

**Outil :** `src/etude_panel_reduit.py`
(`--candidats`, `--insee 28389,…`, `--limite N`, `--tous`). Cache disque, pause
de 0,4 s entre appels. Il écrit ses sorties sous le préfixe **`auto_`** — un
script ne doit jamais pouvoir écraser ce qu'une main a écrit ; il l'a fait une
fois le 12 août, sur l'étude rédigée de Thiville.

---

### 19.4 CE QUE CE CHANTIER DEMANDE — non fait

1. **L'alerte sur la fiche de chaque commune :**
   > **Aucune analyse complète (plus de 200 paramètres) depuis X mois.**

   Avec ses deux compléments **obligatoires** : le **nombre de contrôles**
   intervenus depuis, sans quoi l'alerte se lit comme un abandon de surveillance
   — ce qui serait faux et injuste (§2.1) ; et le **nom des paramètres** qui
   étaient en dépassement et ne sont plus mesurés.

   **Coût nul en appels** pour la première : `hubeau.selectionner_bulletins`
   construit déjà l'inventaire de TOUS les bulletins avec leur nombre de
   paramètres, puis **jette** ceux qui sont sous le seuil. Il suffit d'en garder
   la date la plus récente et la taille maximale.

2. **Rechercher les bulletins postérieurs au dernier complet** pour alimenter le
   second complément. Le corpus ne les contient pas : la collecte filtre à la
   source (`nb_lignes > SEUIL_COMPLET`). C'est un appel API par commune.

3. **Étendre le balayage à PACA** une fois l'ingestion et le figeage faits.

4. **Revoir le critère** : il exige un dépassement à la dernière analyse
   complète. Une commune conforme en apparence, dont un paramètre approchait la
   limite et n'est plus mesuré, échappe au filtre.

5. **Relecture humaine avant toute publication.** Chaque dossier nomme une
   commune et un exploitant implicite. Vérifier phrase à phrase qu'aucune ne
   glisse du constat vers le procès.

---

### 19.5 LA RECHERCHE DOCUMENTAIRE — chantier de Yannick

**Le maillon qui manque n'est pas informatique.** La liste des paramètres
recherchés est **régionale** et **figée par les marchés pluriannuels d'analyses
des ARS** : le laboratoire retenu applique le catalogue annexé pour toute la
durée du marché. Mécanisme décrit par l'instruction **DGS/EA4/2020/177**
(`REG-05`), avec la réserve d'usage — elle décrit, elle ne prouve aucun cas.

**Deux conséquences déjà écrites au README du dossier :** un exploitant n'a pas
la main sur ce qu'on mesure chez lui ; et la formulation reste **« compatible
avec un renouvellement de marché »**, jamais « causé par ».

**À retrouver, et c'est public :** les marchés d'analyses de l'ARS
Centre-Val de Loire — date de notification, durée, **liste de paramètres
annexée**. Ces pièces transformeraient l'hypothèse en fait établi, ou
l'infirmeraient. Yannick prévoit en parallèle une recherche en presse locale
commune par commune.

**Les six communes aux abandons les plus anciens**, par où commencer :
Oinville-Saint-Liphard (119 mois), Gas (103), Villars (102), Nottonville (101),
Varize (100), Louville-la-Chenard (90) — toutes en Beauce, plusieurs sur la même
intercommunalité.

---

### 19.6 LES CINQ ATTRIBUTIONS — implémentées, PAS ENCORE AFFICHÉES

Décision du 11 août, implémentée le 12 : `v_mesures_verdict` porte une colonne
**`attribution`**, et `verdicts_figes` la fige. Cinq valeurs, définies dans
`docs/METHODE_ATTRIBUTION.md` §0 : `juge` · `juge_avec_son_groupe` ·
`juge_sur_valeur_declaree` · `norme_non_exprimee` ·
`rien_ne_se_prononce_{etabli,non_instruit}`.

**Ce qui manque : l'affichage.** Ni la fiche ni la vitrine ne lisent encore
cette colonne. La décision est appliquée dans le moteur, invisible pour le
lecteur.

**Défaut corrigé au passage :** les quatre HAP de la somme réglementée
(benzo(b)fluoranthène, benzo(k)fluoranthène, benzo(g,h,i)pérylène,
indéno(1,2,3-cd)pyrène) étaient notés individuellement contre 0,10 µg/L — valeur
que la directive ne fixe que pour leur somme. Une ligne « dans somme » prime
désormais sur la limite déclarée par la source.

**Cinquième attribution née d'un défaut trouvé à la vérification** : le pH, la
conductivité et la turbidité ressortaient en « rien ne se prononce », ce qui est
**faux** — le texte les encadre par une **plage**, que le modèle ne sait pas
exprimer.

---

### 19.7 LA FICHE ET LA CARTE — modifiées, à vérifier après republication

**Trois changements de fiche**, demandés le 12 août :

1. **le tiret a disparu** — « recherché, seuil de détection non communiqué »
   remplace le « — » ambigu. Et jamais « 0 » : un laboratoire qui ne trouve rien
   ne mesure pas zéro (§2.4) ;
2. **le bloc PFAS ne s'efface plus jamais.** Sans PFAS cherché, il l'écrit :
   *« Ce n'est pas un résultat : c'est une absence de recherche. »* Vérifié sur
   Chein-Dessus (31140) ;
3. **toutes les substances cherchées sont listées**, pas seulement les
   quantifiées, et les PFAS non recherchés sont nommés. Vérifié sur Calmont
   (31100) : 22 lignes dont 20 en « < 0,0015 µg/L ».

**Livraison partielle assumée** : le troisième changement n'est implémenté que
dans le bloc PFAS. Ailleurs, une substance non cherchée ne produit toujours
aucune ligne.

**La carte** : une commune rattachée à un réseau garde son verdict. La fonction
`niveau_commune` sortait sur le rattachement **avant** de regarder le verdict —
il était calculé, puis jeté. Cercle bicolore : moitié blanche pour l'emprunt,
moitié colorée pour le verdict. Vérifié sur l'Eure-et-Loir : 181 cercles,
181 demi-disques, **95 bascules et 49 dépassements qui étaient invisibles**.

---

### 19.8 LE SOURÇAGE RÉGLEMENTAIRE — six dossiers, et ce qui reste ouvert

Six dossiers rendus le 11 août au soir dans `data/etudes/sourcage_C/` —
fluoranthène, Fréon 113, phosphate de tributyle, dalapon, tétrachlorure de
carbone, éthylbenzène. **Aucun ne recommande de verser un seuil**, six fois sur
six : dans chaque cas, choisir une valeur produirait le verdict au lieu de le
constater. **973 466 tokens** au total.

**Sept dossiers corrigés le 12 août** après lecture de l'ordonnance suisse dans
sa **version en vigueur (état au 1er janvier 2026)** — les deux versions citées
la veille, 2018 et 2024, étaient périmées **toutes les deux**. Voie d'accès
réutilisable : le *filestore* de Fedlex sert du HTML statique là où le portail
résiste.

**Restent ouverts :**

- **les deux dichloroéthylènes** : la double liaison C=C compte-t-elle comme
  « autre groupe fonctionnel » au sens du texte suisse ? Non tranché, `a_verifier`
  dans les deux sens ;
- **le dossier Fréon 113** attribuait un renvoi à un paramètre « toxicité
  inconnue » que la version en vigueur ne porte pas — marqué comme lecture de
  version périmée, non supprimé ;
- **la ligne « prête à verser » du fréon 11**, écrite sur un mauvais en-tête :
  **ne pas la verser en l'état** ;
- **l'écart de comptage 215 contre 240** sur les substances sans seuil : la vue
  de diagnostic et la vue des verdicts ne filtrent pas pareil. **À réconcilier
  avant de citer un chiffre en public** ;
- **la file de sourçage** : dibromométhane (réponse déjà connue par le dossier
  suisse), les HAP hors somme en un seul dossier, puis la queue longue ;
- **la troisième grille de la thèse — `seuil_strict` — est vide pour presque tout
  le référentiel.** Un seul balayage mondial a été fait, sur les PFAS.

---

### 19.9 ÉTAT MATÉRIEL

- **11 départements publiés** : 28, 81, 69, 09, 31, 12, 32, 47, 65, 71, 82.
  3 955 fiches de commune, 807 Mo, version `d0fb678dcbe2`.
- **Corpus en base** : 12 652 bulletins avant l'ingestion PACA en cours.
- **Deux serveurs debout** : vitrine sur **8765**, atelier sur **8760**.
  `.claude/launch.json` les connaît tous les deux depuis le 12 août.
- **L'atelier est bloqué** pendant tout verrou de la base ; **la vitrine, non** —
  c'est un dossier de fichiers statiques, elle reste consultable et
  démontrable pendant l'ingestion comme pendant le refigeage.
- **Outils nouveaux** : `src/etude_panel_reduit.py`, `src/md_en_pdf.py`
  (Pandoc + Chrome sans interface — pas de LaTeX sur cette machine, WeasyPrint
  réclame des bibliothèques GTK absentes).

---

### 19.10 CE QUI A ÉTÉ CORRIGÉ EN COURS DE ROUTE — à ne pas refaire

- **deux comptages faux dans des briefs d'agents** : « six ou sept sur quinze »
  (il y en avait une), « six sur treize » (huit). Un compte se compte ;
- **l'indicateur binaire « jamais recherché »** ratait quatre communes sur cinq :
  un paramètre recontrôlé une fois puis abandonné huit ans passait pour suivi.
  Remplacé par l'**ancienneté de la dernière mesure** ;
- **le test de non-conformité ratait le trait d'union** — « non-conforme » contre
  « non conforme ». Villemaury ressortait à 8 non conformes sur 10 au lieu de 10.
  L'erreur allait dans le sens qui **affaiblit** le constat ;
- **un script a écrasé une étude rédigée à la main** : même dossier, même nom.
  Préfixe `auto_` désormais, avec la date et le motif dans le code ;
- **un processus tué sans avoir lu sa ligne de commande** (§18.1). Un processus
  inconnu se lit avant de se tuer.

---

### 19.11 ÉTAT RÉEL DE L'INGESTION AU MOMENT DE L'ARRÊT — 12 août, 21 h 40

**L'ingestion a été arrêtée volontairement** (Yannick ne peut pas laisser la
machine allumée). Arrêt propre, base rendue.

**Corpus en base : 20 794 prélèvements** (12 652 avant).

| département | versé |
|---|---|
| Alpes-de-Haute-Provence (04) | **1 749 — terminé** |
| Hautes-Alpes (05) | **1 584 — terminé** |
| Alpes-Maritimes (06) | **2 182 — terminé** |
| Bouches-du-Rhône (13) | **2 623 — terminé** |
| Var (83) | **interrompu en plein versement** (3 618 attendus) |
| Vaucluse (84) | **pas commencé** (884 attendus) |
| 24, 26, 33, 46, 99 | 1 bulletin chacun, résidus d'essais |

**Il reste environ 4 500 bulletins à verser**, soit à peu près deux heures.

**PREMIER GESTE DEMAIN MATIN — reprendre l'ingestion, la même commande :**

```
py -X utf8 src/ingerer.py --depts 04,05,06,13,24,26,33,46,83,84,99 --sans-figer
```

Elle saute les 20 794 déjà en base et reprend au Var. **Ne lancer le refigeage
qu'après** : il balaie le corpus entier, et le lancer sur un corpus incomplet
obligerait à tout refaire.

---

### 19.12 SICOVAL AEP — un défaut d'affichage sérieux, à ouvrir demain

Trouvé le 12 août au soir sur une question de Yannick, et **c'est probablement
le défaut d'affichage le plus grave repéré cette semaine.**

**Le constat.** La fiche annonce « SICOVAL AEP — 35 communes » et montre le
bulletin de Ramonville-Saint-Agne. Or **ces 35 communes ne boivent pas la même
eau.** Ce que Hub'Eau rend comme réseau, commune par commune :

| commune | réseau(x) déclaré(s) |
|---|---|
| Castanet-Tolosan, Labège | SICOVAL PSSE **+** VENERQUE |
| Baziège, Escalquens | **SICOVAL MONTAGNE NOIRE** |
| Montgiscard | VENERQUE + SICOVAL PSSE |
| Venerque | VENERQUE seul |
| Ramonville-Saint-Agne | VENERQUE + SICOVAL PSSE, parfois **SAGE PINSAGUEL** + SICOVAL PSSE |

**Le bulletin de Ramonville ne décrit pas l'eau de Baziège.** L'unité de gestion
regroupe au moins quatre configurations de réseau réellement distinctes.

**Ce que ça met en cause :** la règle du 7 août — *prendre le bulletin de l'UDI
qui alimente la commune même s'il a été prélevé ailleurs, en le mentionnant* —
suppose **une UDI homogène**. Ici elle ne l'est pas.

**Trois points à ouvrir, décision de Yannick du 12 août au soir :**

1. **vérifier si le rattachement d'une commune se fait par unité de gestion ou
   par réseau.** Si c'est par UDI, on attribue à Baziège une eau qu'elle ne boit
   pas — c'est un faux positif d'un genre nouveau, et il touche l'affichage le
   plus consulté du site ;
2. **afficher le ou les réseaux réels** de chaque commune, pas seulement
   l'unité de gestion, et nommer la commune où l'analyse a été prélevée
   (le §8bis obligation 5 l'exige déjà, il n'est pas honoré ici) ;
3. **garder SICOVAL comme terrain du chantier dilution** (§7.2), qui attend un
   cas concret depuis le 8 août : plusieurs réseaux, des mélanges déclarés, une
   usine de production par branche — Vieille-Toulouse, Calmont, Pinsaguel.

**Deux faits mesurés à l'appui**, échantillon de six communes desservies,
analyses depuis 2024 :

- **toutes sont contrôlées régulièrement** — 9 à 26 prélèvements chacune — mais
  **aucun ne dépasse 37 paramètres**. L'analyse complète se fait au point de
  production, les contrôles de routine en distribution : c'est l'architecture
  normale du contrôle sanitaire, pas une négligence ;
- **3 communes sur 35 seulement ont un bulletin complet en propre** dans le
  corpus — Ramonville, Vieille-Toulouse et Odars.

**Sur le captage, la réponse reste « on ne sait pas »**, et c'est un angle mort
déjà déclaré : le maillon *quel captage alimente quelle installation* n'est pas
exposé par Hub'Eau (§8). On voit l'installation de production — usine de
Vieille-Toulouse, usine de Calmont, SICOVAL PSSE — jamais la ressource derrière.

---

## 20. ÉTAT ACTUEL au 13 août 2026, matin — remplace le §19 sur ce qui suit

### 20.1 CE QUI TOURNE — ingestion puis refigeage, enchaînés avec une barrière

Lancé à **08 h 30** dans un script unique
(`scratchpad/ingestion_puis_refigeage.sh`, hors dépôt) :

1. `py -X utf8 src/ingerer.py --depts 83,84,99 --sans-figer`
   → `data/journal/ingestion_paca_2026-08-13.log`
2. **barrière** : le refigeage ne part que si l'ingestion sort en code 0 **et**
   que `--etat` montre 0 bulletin restant sur 83 et 84 ;
3. `py -X utf8 src/ingerer.py --tous --refiger`
   → `data/journal/refigeage_2026-08-13.log`

Motif de la barrière : un refigeage lancé sur corpus incomplet oblige à tout
refaire (§19.11), et la barrière rend ce garde-fou mécanique au lieu de le
laisser à la vigilance de qui relance.

**Le débit réel est plus bas que celui du §19.1** : 400 bulletins en 21 minutes,
soit **~19/min** et non 35/min. Reste ~4 100 bulletins → l'ingestion finit vers
**12 h**, le refigeage vers **18 h**. Le chiffre de « deux heures » du §19.11 est
optimiste d'un facteur deux.

### 20.2 SICOVAL — LE §19.12 SE TROMPE, et le vrai défaut est ailleurs

Instruit le 13 août sans ouvrir la base.
Dossier : `data/etudes/sicoval_rattachement/RATTACHEMENT_2026-08-13.md`.

**Le rattachement se fait par RÉSEAU** (`code_reseau`), pas par unité de
gestion — `src/collecte.py:167`, `src/hubeau.py:666-685`, qui n'a aucun accès à
`nom_uge`. Le faux positif redouté n'existe pas : Baziège et Escalquens
reçoivent le bulletin d'**Odars**, qui est bien sur leur réseau (SICOVAL
MONTAGNE NOIRE), et non celui de Ramonville. **Sur 35 communes : 32
rattachements identiques au réseau déclaré, 3 avec leur bulletin propre, 0
sans réseau commun.** 49 appels Hub'Eau, régulateur à 2/s.

**Le défaut réel est un défaut de VOCABULAIRE, et il est massif.** La clé du
rattachement est utilisée puis jetée — `couverture_communes` n'a pas de colonne
de réseau (`src/figer.py:225-241`) — et l'affichage retombe sur `nom_uge`, qui
est le **gestionnaire**. `sortie/build_fiche.py:501` écrit littéralement
« eau du **réseau** SICOVAL AEP ». Portée mesurée sur les pages publiées :
**2 829 fiches** portent cette phrase, **135 groupes sur 505** sont hétérogènes,
**2 653 communes** concernées. `S.M.D.E.A` : 187 communes, 113 configurations.

Cas qui le démontre : **Venerque déclare `SMEA VENERQUE`, jamais SICOVAL AEP** —
le groupement n'est pas même fidèle à sa propre clé.

Options chiffrées : corriger le vocabulaire et sortir `noms_reseaux` du repli
(`build_fiche.py:501-504`) = une republication, pas de refigeage ; sous-grouper
la page de département par configuration = même republication ; afficher le
réseau **de la commune** = colonne dans `couverture_communes`, donc `figer.py`,
donc refigeage complet + ~2 868 appels de recollecte. Tout basculer en « non
documentée » est à déconseiller : 72 % du corpus couvert passerait au gris pour
réparer un rattachement exact 32 fois sur 35.

### 20.3 L'ALERTE « ANALYSE COMPLÈTE ANCIENNE » — conçue, non implémentée

Dossier : `data/etudes/panel_reduit_alerte/CONCEPTION_ALERTE_2026-08-13.md`.

**La piste du §19.4 point 1 est fausse en partie.** Le jet n'a pas lieu dans
`selectionner_bulletins` mais à `src/collecte.py:137-138`. Et « garder la date
la plus récente et la taille maximale » ne sert aucun des trois éléments : la
date la plus récente est celle du dernier contrôle de routine, pas de la
dernière analyse complète.

**Économie plus grande qu'annoncé** : ajouter `code_parametre` à
`CHAMPS_INVENTAIRE` (`src/hubeau.py:141`) n'ajoute **aucune requête** — la
pagination porte sur les lignes — et donnerait gratuitement le nombre de
contrôles **et** les paramètres cessés. Mesuré sur 37 réponses réelles :
1 233 lignes/commune, donc **1 appel par commune** à `size=5000`.
`src/etude_panel_reduit.py:139` pagine à `size=1000` et paie **76 % d'appels de
trop** — à corriger.

Seuil proposé : **24 mois → 421 communes (10,6 %)**. À 12 mois, 891, soit une
fiche sur quatre : ce n'est plus une alerte. Les quatre chiffres du §19.3
(18 communes, 49 paramètres, 555 contrôles, 119 mois) sont **confirmés** par
recomptage indépendant.

**Défaut d'architecture à connaître** : les bandeaux existants ont leur texte
écrit en dur dans `site/gabarits/fiche.js:908-919`, donc **aucun contrôle de
`tests/test_sorties.py` ne les relit**. Le texte de l'alerte doit être fabriqué
en Python et sa clé ajoutée à la moisson, sinon c'est de la prose publiée sur
3 955 fiches que rien ne vérifie.

### 20.4 LE TABLEAU DE DÉPARTEMENT — deux colonnes de plus, et il tient enfin

Demandé par Yannick le 13 août. **Écrit, non exécuté** : la base est prise, rien
n'est republié avant ce soir.

Le tableau ne débordait pas de la page — il **défilait horizontalement sans que
rien ne l'annonce** (table 1 076 px dans une boîte de 958). Les colonnes de
droite paraissaient absentes. Corrigé dans `site/gabarits/observatoire.css` :
la boîte déborde la colonne de texte au-delà de 1 040 px de large
(`.tableau-communes.large`), le nom de commune reste **collé à gauche** au
défilement, et une **ombre portée** au bord dit qu'il reste des colonnes.
Les intitulés se replient sur deux lignes au lieu d'étirer le tableau.

**Deux colonnes ajoutées** (`site/build_site.py`) :

- **« Hors de portée du laboratoire »** — `nb_aveugles` / `aveugles_pour_mille`,
  déjà figés et déjà sur la fiche, absents de l'endroit où l'on compare les
  communes. Coût nul ;
- **« Statut hormonal des substances trouvées »** — trois nombres côte à côte,
  **jamais additionnés à l'écran** (§2.6, §2.15). Le total existe comme **clé de
  tri** seulement : c'est ce qui permet de remonter vite les communes à
  regarder, sans écrire « 17 perturbateurs endocriniens », énoncé qui fondrait
  un statut de droit européen, un soupçon de la littérature et une question non
  instruite.

La règle de classement était écrite dans `sortie/indicateurs.py::perturbateurs`.
Elle est **extraite** en `statut_hormonal()` et appelée par la fiche comme par
le tableau : une seule copie, sans quoi la même eau finirait par se lire
différemment selon la page. Le comptage se fait en **une requête pour tout le
corpus** (`compter_hormonal()`), pas une par commune sur 4,2 millions de lignes.

**Vérifié dans le navigateur, à colonnes simulées** (valeurs fictives, base
verrouillée) : 9 colonnes, table 1 227 px dans une boîte de 1 227, la page ne
défile plus latéralement ; à 900 px de large, le tableau défile dans son cadre
et le nom de commune reste visible. **Ce qui reste à vérifier ce soir** : que la
requête sort les bons comptes, et son temps sur le corpus entier.

### 20.5 TROIS DÉCISIONS DE YANNICK — 13 août 2026, matin

1. **Pas de total hormonal affiché.** Trois nombres côte à côte, le total ne
   servant que de clé de tri. Proposition retenue telle quelle.
2. **On travaille par réseau réel.** La phrase fausse de la fiche est corrigée
   et le regroupement de la page de département passe du gestionnaire au
   réseau.
3. **Seuil de l'alerte : 24 mois**, soit 421 communes.

**Appliqué dans le code, pas encore visible** (base occupée jusqu'au soir) :

- `sortie/build_fiche.py` — le sous-titre nomme le **réseau**
  (`noms_reseaux`), plus le gestionnaire. Deux lignes ajoutées aux
  métadonnées : « Réseau de distribution » et « Gestionnaire », qui étaient
  confondus sous un seul mot ;
- `site/build_site.py` — le bloc « Les gestionnaires déclarés » devient
  **« Les réseaux de distribution »**, groupé sur `noms_reseaux`. Les communes
  dont le bulletin ne déclare aucun réseau sortent du regroupement et sont
  nommées à part : les ranger sous leur gestionnaire affirmerait un
  rattachement que la source ne donne pas. `noms_reseaux` vient
  d'`analyses_figees` (`figer.py:93`) — **aucun refigeage nécessaire**, la
  donnée est déjà figée ;
- `sortie/indicateurs.py` — `statut_hormonal()` extrait, `compter_hormonal()`
  ajouté.

**Reste à faire ce soir, dans l'ordre** : purge des générations périmées de
`couverture_communes` (elle en porte quatre, §19.1) ; ajout des six
départements PACA à `referentiel/departements_publies.csv` ; régénération des
dossiers de faits ; `py -X utf8 site/build_site.py`. Puis vérifier sur une
commune du Sicoval que le réseau affiché est bien le sien.

**L'alerte des 24 mois n'est pas implémentée** — elle demande un module neuf,
un lot de 421 appels Hub'Eau, et la correction de la pagination de
`src/etude_panel_reduit.py:139` (size=1000 → 5000, 76 % d'appels de trop).
Le lot d'appels ne peut pas se faire avant la republication : la liste des
communes concernées change avec l'arrivée de PACA.

### 20.6 UN CONTRÔLE QUI TENAIT LA RÈGLE D'AVANT — corrigé

`tests/test_figer.py` échouait sur « une mesure sans aucun seuil n'est pas
figée ». **Ce n'était pas une régression** : le contrôle encodait la règle
d'avant le 12 août, et l'élargissement du filtre (§19.2) l'a laissé derrière.
Retourné pour exiger l'inverse — le calcium, mesuré et sans seuil de
comparaison, **doit** rester au bulletin figé. `tests/test_verdict.py` passe
entièrement. Les deux tournent sur une base temporaire et n'ont pas approché
`data/eau.duckdb`.

### 20.7 DILUTION — la question centrale du §7.2 est TRANCHÉE

Instruit le 13 août 2026 sans ouvrir la base.
Dossier : `data/etudes/dilution_avant_apres/FAISABILITE_2026-08-13.md`.
`docs/METHODE_DILUTION.md` §3 et §4 sont **réécrits** en conséquence.

**`code_lieu_analyse` n'était pas le bon champ.** Documentation Hub'Eau : c'est
le lieu de l'**analyse** — terrain (T) ou laboratoire (L) —, pas le lieu du
prélèvement. Sur 25 293 bulletins et 10 111 697 lignes lues au cache :
`L` 9 997 172, `T` 114 525, et **97,6 % des bulletins portent les deux**, parce
que c'est un champ de maille *résultat*. Le §7.2 de `CLAUDE.md` (« vaut `L` sur
les 45 bulletins ») lisait une valeur arbitraire.

**Le champ qui répond est `code_installation_amont`, déjà collecté et déjà en
base.** Renseigné ⇔ prélèvement fait en amont de l'unité de distribution ;
vide ⇔ fait sur l'UDI. Deux sources officielles concordantes, contrôle interne
parfait (aucun bulletin sans installation amont ne porte de part de débit),
corroboré géographiquement.

- **avant le mélange : 24 209 bulletins, 95,7 %** ;
- **après le mélange : 1 084 bulletins, 4,3 %** ;
- **62 réseaux portent les deux**, 15 départements — mais **3 seulement** avec
  moins de 30 jours d'écart.

**Le mélange lisible : 279 réseaux sur 3 487, dans 19 départements** — contre
6 sur 42 au 8 août.

**Le nouveau verrou, et il est méthodologique** : l'arithmétique ne se referme
pas. Albi–Lescure, mélange 85/15 reconstitué, nitrates 4,5 et 3,3 mg/L en
amont pour **9,0 mg/L** en distribution. Les trihalométhanes se forment dans le
réseau (attendu) ; les nitrates, non. **Une comparaison brute amont/aval
produirait des chiffres faux.** Il faut d'abord écrire le périmètre des
**substances conservatives**, sourcé substance par substance.

Les panels, eux, ne bloquent pas : Vieille-Toulouse ↔ Saubens, 367 paramètres
identiques des deux côtés, 325 limites de quantification identiques, 83 jours
d'écart. Lourdes a deux sources prélevées **le même jour**.

**Le §8 de `CLAUDE.md` est trop pessimiste d'un cran** : le jeu data.gouv.fr
« Résultats du contrôle sanitaire de l'eau du robinet » publie les fichiers
**CAP (captages)** et **TTP (production)** en plus des UDI — mêmes paramètres,
même cadre réglementaire. Ce qui manque vraiment, c'est le lien *quel captage
alimente quelle installation* (référentiel ADES retiré de la diffusion
publique fin 2023). Aucune des 13 API Hub'Eau ne porte d'analyse d'eau
destinée à la consommation en amont ; `qualite_nappes` et `qualite_rivieres`
sont des mesures environnementales, autre objet et autres seuils — **les
rapprocher donnerait un chiffre faux déguisé en chiffre sourcé.**

**File d'attente proposée** : (1) §4 de la note de dilution corrigé — *fait* ;
(2) télécharger les tables de référence `eaurob-ref-*.zip` de data.gouv.fr,
qui pourraient porter le lien captage → production → distribution — **1
téléchargement, la vérification la plus rentable, en attente du feu vert de
Yannick** ; (3) écrire le périmètre des substances conservatives ; (4)
densifier les 3 cas à moins de 30 jours (~60 appels) ; (5) après la campagne,
une colonne de position du prélèvement et une vue amont/aval.

### 20.8 LES TABLES DE RÉFÉRENCE SISE-EAUX — téléchargées, et ce qu'elles disent

Feu vert de Yannick, 13 août 2026. Fichier : `eaurob-ref-20260812.zip`,
71 751 octets, licence ouverte v2, publié le 12 août 2026 — conservé dans
`data/sources_externes/`.
Source : `https://www.data.gouv.fr/datasets/resultats-du-controle-sanitaire-de-leau-du-robinet`

**LE LIEN CAPTAGE → INSTALLATION N'Y EST PAS.** L'hypothèse du §20.7 point 2
est **infirmée**. L'angle mort du §8 de `CLAUDE.md` reste entier : le
rattachement d'une ressource à une installation n'est toujours pas public.

**Mais les cinq tables portent autre chose, et c'est important.** Trois de ces
nomenclatures décrivent des champs que **l'API Hub'Eau n'expose pas** — vérifié
sur le cache brut, qui ne porte aucun des trois. La voie data.gouv.fr est donc
**plus riche que l'API que le projet interroge**. À confirmer en ouvrant un
fichier de prélèvements réel : les tables prouvent l'existence de la
nomenclature, pas celle de la colonne.

| Table | Contenu | Pourquoi ça compte |
|---|---|---|
| `PAR` | **2 321 paramètres** : code SISE-Eaux, code SANDRE, numéro CAS, famille, statut | notre catalogue en connaît **782**. C'est le référentiel officiel des libellés, avec les CAS — de quoi réduire les paramètres non appariés |
| `MOP` | 12 **motifs de prélèvement** | voir ci-dessous |
| `CPLV` | 18 **conditions de prélèvement**, dont la position par rapport au réseau public | voir ci-dessous |
| `NAE` | 3 natures d'eau : souterraine, superficielle, **EAU MIXTE** | le mélange a un code officiel |
| `FRT` | 202 fractions analysées | peu d'usage ici |

**Les motifs de prélèvement (`MOP`) touchent la thèse de plein fouet.**
L'administration distingue elle-même : `S2` eaux **brutes** · `S3` tendance
**défavorable** · `S4` **dérogation** · `S6` **« paramètre sans norme avec
danger potentiel »** · `S8` réseaux intérieurs · `CP` contrôle plomb-cuivre-
nickel. Deux conséquences immédiates :

- `S6` est la **catégorie administrative** de ce que le §19.2 a mesuré chez
  nous — 413 050 mesures sur lesquelles rien ne se prononce. L'administration
  a un mot pour ça, et il contient « danger potentiel ». **À instruire.**
- `S4` **dérogation** : un dépassement autorisé, daté, motivé. C'est de la
  matière de thèse à l'état pur, et le projet n'en a aucun corpus.

**Les conditions de prélèvement (`CPLV`) ouvrent une distinction que le projet
ne fait pas** : la position du point de prélèvement **par rapport au réseau
public** — `P` directement sur la canalisation publique · `B` sur la partie
publique du branchement · `C` en aval immédiat du compteur · `I` / `L` sur un
réseau **intérieur**. Plus les conditions de purge et de préparation du
robinet.

Enjeu §2.1 : **un plomb mesuré sur le réseau intérieur d'un immeuble ne décrit
pas l'eau distribuée** — c'est la plomberie de l'immeuble. Sans cette
distinction, un dépassement peut être imputé au distributeur alors qu'il vient
du bâtiment. Le projet ne peut pas faire cette distinction aujourd'hui : le
champ n'existe pas dans ce qu'il collecte.

**Ce qui en découle, et qui n'est pas décidé** : la voie data.gouv.fr n'est
plus seulement le chemin vers le captage et l'usine, c'est peut-être une
**source plus complète que Hub'Eau pour l'eau distribuée elle-même**. Avant
d'ouvrir ce chantier, ouvrir un seul fichier de prélèvements et lire ses
colonnes.

### 20.9 UN DÉFAUT DE `src/md_en_pdf.py`, CORRIGÉ

Le convertisseur échouait sur tout fichier, avec pour seul message « pas de PDF
produit ». Cause : `--print-to-pdf` recevait un chemin **relatif**, et le
navigateur sans interface n'écrit pas dans un chemin relatif — il ne partage
pas notre répertoire courant. Il sortait en code 0 malgré tout, donc
`subprocess.run(check=True)` ne levait rien et l'échec restait muet.
`os.path.abspath` sur le chemin de sortie ; commentaire posé sur place.

Produit : `docs/pdf/CE_QUE_FAIT_LOBSERVATOIRE.pdf`, 6 pages, 116 Ko.
Contrôle de fidélité : 25 titres au Markdown, **25 titres** dans le HTML
imprimé, tableau conservé.

Le document source est `docs/CE_QUE_FAIT_LOBSERVATOIRE.md`, écrit le 13 août
2026 à la demande de Yannick : ce que le projet fait, ce qu'il met en lumière
(huit mécanismes), les enquêtes ouvertes, ce qu'il refuse de faire, l'état du
corpus. **Le PDF est une sortie, jamais une source** — il se régénère, on ne
le corrige pas.

### 20.10 LES FICHIERS DE PRÉLÈVEMENTS data.gouv.fr — vérifiés sur mai 2026

`eaurob-202605.zip`, 16,3 Mo (le plus petit mois disponible), dans
`data/sources_externes/`. Six fichiers : prélèvements et résultats pour la
distribution (UDI), le captage (CAP) et la production (TTP). 41 colonnes au
prélèvement.

**LE LIEN CAPTAGE → RÉSEAU N'Y EST TOUJOURS PAS, et c'est maintenant démontré.**
Le fichier des captages porte bien une colonne `cdreseau` — mais elle contient
le code de **l'installation elle-même**, pas celui du réseau qu'elle alimente :
sur 1 909 codes de captage, **0 n'apparaît dans les 10 873 codes de la
distribution**. Vérifié sur 2 019 prélèvements de captage et 16 112 de
distribution. L'angle mort du §8 tient. **Ne pas rouvrir cette piste sans
élément neuf.**

**Ce qui EST disponible, et que Hub'Eau n'expose pas :**

| Colonne | Remplissage sur mai 2026 |
|---|---|
| `finaliteprel` — motif du prélèvement | **16 112 / 16 112, soit 100 %** — CS 14 516, CP 776, S1 600, S3 147, CV 47, CD 22 |
| `plvcondition` — conditions et position | 5 973 / 16 112, **37 %** — trois lettres concaténées, une par position, décodables par `CPLV` |
| `inae` — nature de l'eau (dont EAU MIXTE) | présent |
| `codebss` — point d'eau souterraine du captage | 1 334 / 2 019 captages |
| `coord_x` / `coord_y` | **vides — 0 / 2 019** |

Le `codebss` ouvre le raccordement aux bases d'eau souterraine, **pas** à nos
réseaux : il documente la ressource, sans dire qui elle alimente.

**Volumes** : un mois pèse 16 Mo compressés pour ~277 Mo décompressés ; une
année pleine, ~210 Mo compressés. Le corpus Hub'Eau du projet ne serait pas
remplacé sans une reprise complète de la collecte et du modèle.

**Ce que ça ne dit pas** : ce contrôle porte sur **un seul mois**. Le taux de
remplissage de `plvcondition` peut varier par région et par année.

### 20.11 CE QUE LA JOURNÉE CHANGE DURABLEMENT — synthèse pour décision

Quatre choses ne seront plus jamais comme avant dans ce projet. Elles appellent
des révisions de `CLAUDE.md`, **non faites** — à passer quand la base sera
rendue.

**1. Le chantier dilution n'est plus bloqué — `CLAUDE.md` §7.2 est périmé.**
Il écrit : *« La question qui commande tout n'est pas tranchée : où, dans le
réseau, le prélèvement a-t-il été fait ? `code_lieu_analyse` vaut `L` sur les
45 bulletins. »* Les deux phrases sont fausses. Le champ cité dit où la
**mesure** a été faite (terrain ou laboratoire), et la question se lit dans
`code_installation_amont`, collecté depuis le premier jour. **À réécrire.**

**2. Un angle mort passe de « pas encore trouvé » à « vérifié absent ».**
Le lien captage → réseau n'est ni dans les tables de référence, ni dans les
fichiers de prélèvement (0 code de captage sur 1 909 retrouvé côté
distribution). `CLAUDE.md` §8 devient plus fort : ce n'est plus une lacune de
notre collecte, c'est une donnée non publiée. **Cesser de la chercher.**

**3. Il existe une seconde source officielle, plus riche que la nôtre.**
Même cadre réglementaire, trois informations que Hub'Eau n'expose pas — le
motif du prélèvement (rempli à 100 %), la position par rapport au réseau
public (37 %), la nature de l'eau dont « eau mixte » —, plus les analyses au
captage et à l'usine. **Ce n'est pas un complément, c'est une alternative** :
l'adopter serait reprendre la collecte et le modèle. Décision non prise.

**4. Un risque d'injustice est identifié, et c'est le premier de ce genre.**
Sans la position du prélèvement, un dépassement mesuré sur la **plomberie
intérieure d'un immeuble** est indiscernable d'un dépassement du réseau public.
Le projet peut donc aujourd'hui imputer à un distributeur ce qui vient du
bâtiment. Tous les angles morts connus jusqu'ici produisaient de
l'imprécision ; **celui-ci peut produire un faux procès** (§2.1). À porter au
§8 comme tel, et à surveiller particulièrement sur le plomb, le cuivre et le
nickel — que la source distingue par un motif de prélèvement dédié (`CP`).

**Et un garde-fou neuf, à ajouter à la note de dilution** : avant toute
comparaison amont/aval, écrire le périmètre des **substances conservatives**.
Les trihalométhanes se forment dans le réseau ; les comparer amont/aval produit
un écart qui ne doit rien à la dilution.

### 20.12 LE BANC D'ESSAI DILUTION — RÈGLE ÉCRITE, TEST INEXÉCUTABLE

Livré le 13 août 2026 dans `data/etudes/dilution_avant_apres/echantillon/` :
la note de sourçage, la table `perimetre_conservatif.csv`, les trois fiches de
cas et le protocole. **Aucune valeur de mesure n'a été regardée** — la règle a
été fixée avant les résultats, exprès.

**Résultat central, et il est méthodologique : le test ne peut être exécuté
sur aucun des trois cas.**

| réseau | écart amont/aval | parts déclarées | panel commun | substances éligibles |
|---|---|---|---|---|
| Sault (84) | **0 jour** | 37 % | 422 | **0** |
| Albi–Lescure (81) | 14 jours | **100 %** | 311 | **0** |
| Mouans-Sartoux (06) | 29 jours | **0 %** | 203 | **0** |

**La cause, et elle est structurelle** : là où deux prélèvements sont assez
rapprochés pour décrire le même instant, **ils ne cherchent pas les substances
qui permettraient de les comparer**. Sur Albi–Lescure, le bulletin aval à
14 jours est un panel de micropolluants sans un seul minéral ; le seul bulletin
aval portant les treize traceurs candidats est à **160 jours**. Simultanéité et
traceurs s'excluent.

**La table** : 79 substances instruites — `conservatif` **1**,
`non_conservatif` 30, `a_verifier` 48. 22 lignes `verifie`, 57 `a_verifier`.

- **seuls les nitrates** ressortent conservatifs, sur une étude qui mesure
  exactement notre question (sortie d'usine contre robinet). **Deux réserves
  écrites** : corpus danois, où l'on distribue sans désinfectant ; et le seul
  mécanisme de formation en réseau, la nitrification, est borné par l'ammonium
  et les nitrites — à regarder avant toute conclusion ;
- **la dureté**, qui aurait été le meilleur traceur, est disqualifiée par la
  source : au-delà d'environ 200 mg/L une eau dure dépose du tartre ;
- **les minéraux** (chlorures, sodium, sulfates, calcium, alcalinité,
  conductivité, fluorures, bore) : **aucune source lue** décrivant leur
  comportement entre production et distribution, et trois mécanismes contraires
  identifiés — l'hypochlorite de sodium apporte sodium et chlorures, l'équilibre
  calco-carbonique déplace calcium et alcalinité, les sulfates peuvent être
  réduits en anaérobie. **C'est LE verrou : il vide les trois périmètres.**

**Deux écarts de comptage avec le §20.7, expliqués** : 226 réseaux à deux
sources sous 100 % (contre 215) et 66 portant l'avant et l'après (contre 62),
parce que la faisabilité ne regardait que le **dernier** bulletin de chaque
installation. Et « moins de 30 jours » se lit de deux façons : 3 réseaux si
chaque amont est à moins de 30 jours de l'aval, **2 seulement** si toutes les
sources déclarantes doivent tenir dans la même fenêtre.

**Un défaut du critère de sélection, à corriger** : Mouans-Sartoux n'entre dans
la sélection que parce que `0 % < 100 %`. Ses cinq sources déclarent toutes
`0 %`, sa source dominante à 85 % n'a aucun bulletin dans les trois années
encadrant la fenêtre, et sa part a varié de 85 à 100 % dans le temps. **Une
part à 0 % ne doit pas compter comme un mélange déclaré** tant que sa
signification n'est pas établie (547 occurrences dans le corpus, §20.7).

**Le protocole** porte deux critères. Le premier — un mélange ne peut pas
sortir de l'intervalle de ses termes — **n'a besoin d'aucun seuil**, mais
n'est valide que si les parts somment à 100 %, ce qui n'est vrai que
d'Albi–Lescure. Le second, quantitatif, **n'a volontairement pas de valeur de
seuil** : l'incertitude analytique n'est pas publiée par Hub'Eau. Chemin posé
pour la mesurer sans inventer de chiffre — relever la dispersion d'une
substance entre deux bulletins d'un même point espacés de moins de quinze
jours. **Faisable sur le cache, sans un appel réseau.**

**File d'attente du chantier, par ordre d'utilité** : (1) lever le verrou des
minéraux par du sourçage ; (2) passer les 66 réseaux au crible des cinq
conditions — aucun ne l'a été ; (3) mesurer le budget d'incertitude sur le
cache ; (4) corriger le critère de sélection sur les parts à 0 %.

**Indéterminés déclarés** : le sens de `debit = 0 %` ; le rattachement
d'Aubignosc (04) au réseau de Sault (84) ; les 63 % d'origine inconnue de
Sault ; la part analytique du budget d'incertitude ; et l'existence même d'un
cas exploitable.

### 20.13 ÉTAT AU 13 AOÛT, 13 h — ingestion finie, refigeage en cours

**Ingestion PACA terminée** : 4 503 bulletins versés, verrou tenu 176 min, base
rendue proprement. **Corpus : 25 297 analyses complètes** (20 794 avant).
La barrière du §20.1 a fonctionné — le refigeage est parti seul à 12 h 28.

**Refigeage en cours** : 3 792 / 25 297 à 13 h 30, ~5 h 50 annoncées par le
script lui-même. Fin attendue **vers 18 h 30**. Base prise jusque-là.

**L'indice de danger est documenté.** `docs/METHODE_EFFET_COCKTAIL.md` §4 porte
désormais « Le calcul, ligne à ligne » : formule, exemple chiffré repris du
contrôle automatique, les quatre filtres d'entrée, le choix du dénominateur et
son exception « dans somme », et deux propriétés à dire (grille du jour et non
grille applicable ; substance sans famille exclue). PDF dans `docs/pdf/`.
La page Méthode du site porte la version publique — **écrite, pas encore
publiée**, elle sortira à la republication de ce soir.

**Défaut relevé au passage, non corrigé** : la règle de publication de ce
document exige d'afficher « la part des seuils issus du référentiel daté
plutôt que de la limite déclarée ». **Cette part n'est pas calculée** —
`analyses_figees` ne porte que `indice_danger` et `indice_danger_n`. Corriger
le moteur ou retirer la règle ; ne pas laisser une obligation d'affichage que
rien n'alimente.

### 20.14 LA FILE D'ATTENTE, ORDONNÉE — décision de méthode du 13 août

Yannick : *« je veux bien cumuler, mais je veux rester focus et traiter les
sujets un par un. »* Ordre proposé, un seul sujet actif à la fois.

**0 — La chaîne de republication de ce soir.** Mécanique, aucune décision :
purge des générations périmées de `couverture_communes` (quatre, §19.1) ; ajout
des six départements PACA à `referentiel/departements_publies.csv` ;
régénération des dossiers de faits ; `py -X utf8 site/build_site.py` ; puis
vérifier une commune du Sicoval et une page de département.

**1 — Panel réduit / marchés ARS.** *Le sujet éditorial le plus fort, et le
plus avancé.* Seuil de 24 mois validé (421 communes). Reste : implémenter
l'alerte (§20.3), le lot de 421 appels — **à passer après la republication**,
la liste changeant avec PACA —, et la recherche documentaire de Yannick sur
les marchés d'analyses de l'ARS Centre-Val de Loire (§19.5).

**2 — Dilution.** Verrou identifié et unique : le statut conservatif des
minéraux (§20.12). Trois chantiers derrière, dont le crible des 66 réseaux.

**3 — Origine des seuils pesticides.** Ouvert le 13 août : la valeur est
sourcée, sa **justification ne l'est pas**, et notre référentiel écrit « zéro
de substitution » comme base en citant un texte qui ne le dit pas. Un article
scientifique sur la dérivation du 0,1 µg/L dort dans les sources
(`MET-02_Hamilton_seuil-0.1ugL-zero-substitution_2013.pdf`) — **jamais
exploité, texte non extractible par `pdftotext`**, encodage de polices brouillé.

**4 — La source data.gouv.fr et le risque d'injustice.** Le plus lourd de
conséquences, le moins mûr (§20.11 point 4).

**5 — Sourçage réglementaire, file existante** : les deux dichloroéthylènes,
la ligne « prête à verser » du fréon 11 **à ne pas verser en l'état**, et
l'écart 215/240 à réconcilier avant de citer un chiffre en public (§19.8).

### 20.15 ALERTE PANEL RÉDUIT — essai sur trois communes, concluant

Fait le 13 août sans ouvrir la base : les exports publiés sur le disque
(`site/public/donnees/bulletins.csv` et `verdicts_<dept>.csv.gz`) suffisent à
désigner les candidats. Scripts au scratchpad, non versionnés.

**Pagination corrigée** : `src/etude_panel_reduit.py` passe de `size=1000` à
`size=5000`, motif et mesure dans le code. **Mesuré en réel : 1 appel par
commune** pour 1 128 à 2 175 lignes.

**Le décompte des candidats à 24 mois — 254, et non 421.**

| population | à 24 mois ou plus |
|---|---|
| communes ayant leur propre analyse complète (1 110) | **254** |
| communes documentées par le bulletin de leur réseau (2 868) | **159** |
| **total** | **413** |

Le chiffre de 421 du §20.3 portait sur les deux populations réunies ; l'écart
résiduel tient à la convention de calcul des mois. **La question éditoriale est
là, non tranchée : l'alerte s'affiche-t-elle sur une commune qui n'a pas
d'analyse à elle ?** Si oui, le texte doit dire que l'analyse est celle du
réseau, pas de la commune.

Parmi les 254 : **39 portaient au moins un dépassement** à leur dernière
analyse complète, 215 aucun. Le 39 recoupe exactement le comptage du §20.3.

**MON ERREUR, ATTRAPÉE ET CORRIGÉE — c'est celle du §19.10.** Le premier essai
testait « ce paramètre a-t-il été mesuré depuis ? », test binaire déjà écarté
par le projet le 12 août. Réclainville en est la démonstration : le binaire dit
« rien d'abandonné », l'ancienneté dit que trois paramètres s'arrêtent au
**11 septembre 2020, soit 71 mois**. Et ce 71 recoupe exactement le chiffre du
§20.3 pour cette commune. **Toujours l'ancienneté de la dernière mesure,
jamais un booléen.**

**Les trois cas d'essai**, un appel chacun :

- **Oinville-Saint-Liphard (28)** — dernière complète 09/09/2016, 651
  paramètres, 119 mois. **34 contrôles depuis**, médiane 18 paramètres.
  Atrazine, atrazine déséthyl et total des pesticides **jamais remesurés** ;
  les nitrates le sont encore (04/2026) ;
- **Réclainville (28)** — 29/09/2016, 651 paramètres, 118 mois. **41 contrôles
  depuis**. Les trois mêmes s'arrêtent au 11/09/2020 (71 mois) ; nitrates
  mesurés en 05/2026 ;
- **Génat (09)** — 18/07/2016, 323 paramètres, 120 mois. **41 contrôles
  depuis**. Le seul dépassement d'alors était bactériologique et **reste
  mesuré** (02/2026) : aucun abandon. Cas témoin — l'alerte d'ancienneté doit
  s'y afficher sans le complément sur les substances.

**Coût du lot complet mesuré : 254 appels, ~2 minutes.** Les six départements
PACA feront un second lot après la republication.

### 20.16 LOT COMPLET DES 413 — et le constat change de nature

Lot passé le 13 août : **413 communes, un appel chacune, 7 incidents réseau
tous repris**. Décision de Yannick : les communes rattachées sont incluses,
avec un texte qui nomme le réseau et le lieu du prélèvement. Sortie au
scratchpad, `alerte_panel_reduit.csv`.

**LA CHAÎNE COMPLÈTE, ET ELLE SE RESSERRE VITE**

| étape | communes |
|---|---|
| analyse complète de 24 mois ou plus | **413** (254 propres + 159 rattachées) |
| …qui portaient un dépassement à cette analyse | **40** |
| …dont au moins une substance n'est plus mesurée depuis 24 mois | **23** |

**23 communes sur 413, soit 5,6 %.** 22 avec analyse propre, **1 seule
rattachée** — la décision d'inclure les 159 ajoute donc beaucoup d'alertes
d'ancienneté et **un seul** cas de substance abandonnée. À savoir avant de
présenter l'effet de cette décision.

**LE PHÉNOMÈNE N'EST PAS GÉOGRAPHIQUE, IL EST CHIMIQUE — et cela remplace la
précaution du §19.3.**

| dept | candidats | avec un dépassement | avec abandon |
|---|---|---|---|
| 65 Hautes-Pyrénées | **136** | 1 | 0 |
| 09 Ariège | **110** | 5 | 0 |
| 31 Haute-Garonne | 46 | 3 | 0 |
| **28 Eure-et-Loir** | **41** | **25** | **21** |
| 12, 81, 71, autres | 80 | 6 | 2 |

**L'Eure-et-Loir n'est pas le département le plus fourni en candidats — il est
quatrième.** Les Hautes-Pyrénées en comptent trois fois plus et ne produisent
aucun cas. L'explication « un territoire mieux documenté produit plus de cas »
**ne tient pas ici** et ne doit plus être écrite telle quelle.

**La cause est la nature de la substance dépassée** :

- **en Eure-et-Loir** : atrazine déséthyl (15), total des pesticides (14),
  nitrates (13), atrazine déséthyl déisopropyl (6), chlorothalonil R471811 (6) ;
- **ailleurs, 17 des 20 dépassements sont bactériologiques** — coliformes (12),
  entérocoques (3), *E. coli* (2).

**Un dépassement bactériologique ne peut structurellement pas être abandonné :
la bactériologie est dans TOUS les contrôles de routine.** Un dépassement de
pesticide, lui, n'est mesuré que dans les analyses complètes — donc il
disparaît avec elles. Sur les **trois** seuls dépassements de pesticides hors
Eure-et-Loir, **deux** ont produit un abandon.

**Formulation à tenir** : le phénomène suit la substance, pas le territoire. La
Beauce ressort parce que c'est là que les dépassements de pesticides se
produisent — pas parce qu'on y surveillerait moins.

**LES CONTRÔLES CONTINUENT, ET C'EST MESURÉ** : **10 368 contrôles** sur les
413 communes depuis leur dernière analyse complète, de 1 à 188, médiane 15.
**Aucune commune n'est à zéro.** Taille médiane d'un contrôle : **18
paramètres**, contre 651 pour une analyse complète de 2016.

**55 abandons, 12 substances distinctes** : atrazine déséthyl (15), total des
pesticides (14), atrazine déséthyl déisopropyl (6), atrazine (4), ESA
métolachlore (4), chlorothalonil R471811 (4), puis la queue.

**Les dix plus anciennes**, toutes en Eure-et-Loir : Oinville-Saint-Liphard
(119 mois, 34 contrôles, 3 abandons), Réclainville (118, 41, 3), Dambron (109,
36, 1), Gas (102, 70, 4), Nottonville (101, 30, 5), Villars (101, 34, 2),
Varize (99, 28, 4), Louville-la-Chenard (95, 31, 3), Neuville-Saint-Denis (93,
70, 2), Poinville (93, 25, 1).

**Reste à faire** : le second lot pour les six départements PACA après la
republication ; promouvoir les scripts du scratchpad dans `src/` ; écrire
l'alerte elle-même.

---

## 21. Mise à jour du 13 août 2026, après-midi — audit de forme externe, phases A et B

**Périmètre : la FORME, jamais le fond.** Ni les seuils, ni les dates
d'applicabilité, ni l'angle éditorial, ni les choix de méthode réglementaire.
Consigne appliquée : `docs/CONSIGNE_AUDIT_FORME.md`. Rapport rendu :
`docs/AUDIT_FORME_2026-08-13.md`.

**L'audit a été coupé en deux, et il faut savoir pourquoi.** `eau.duckdb` était
tenue en écriture exclusive par `py -X utf8 src/ingerer.py --tous --refiger`,
lancé à 11 h 26. DuckDB n'a qu'un seul écrivain : la base ne pouvait être
ouverte par personne, pas même en lecture seule. L'auditeur a donc reçu
l'interdiction nommée de toute commande touchant la base ou l'API Hub'Eau —
motif : lancer `figer.py` ou `build_db.py` pendant un refigeage aurait détruit
le travail en cours, exactement l'incident du §17.

- **Menées** : phase A (lecture froide, sans aucune documentation), phase B
  (écart annoncé / réel), axe 1 en lecture, axe 3 en entier sur le site déjà
  servi en local, plus `tests/test_verdict.py` et `tests/test_figer.py` — lancés
  après lecture de leur code confirmant qu'ils fabriquent une base temporaire.
  L'auditeur rapporte 21 s cumulées ; **cette durée n'a pas été remesurée en
  session principale.**
- **Reportées, à mener quand la base sera rendue** : `tests/test_sorties.py`, le
  build du site, le `diff` de deux builds successifs, la mesure du goulot sur une
  unité réelle, l'épreuve du facteur 100. **Rien n'est armé pour les lancer** :
  une surveillance de la libération de la base avait été posée, elle a été
  annulée le 13 août 2026 à 15 h 20 sur décision de Yannick, qui a d'autres
  travaux à mener d'abord. La phase C attend donc un feu vert explicite — elle
  ne repartira pas d'elle-même, et l'audit reste incomplet sur l'axe 2, la
  chaîne de production.

### Ce qui a été revérifié en session principale, avec les chiffres mesurés

**Le livrable ne tient pas ses propres invariants, et le contrôle qui l'attrape
existe déjà.** Mesuré sur `site/public/donnees/index_communes.json` :

```
Entrees dans l'index      : 4144
Entrees pointant une page : 3978
LIENS MORTS (404)         : 23     → 100 % en dept 47
```

Les 23 portent toutes le statut affiché **« rattachée au réseau »** : elles sont
donc annoncées au lecteur comme documentées, et rendent 404. Le contrôle qui
couvre exactement ce cas est écrit — `tests/test_sorties.py:254-259` — et la
publication ne l'exécute pas.

**Aucune valeur mesurée n'atteint un lecteur sans JavaScript.** Mesuré sur les
pages produites :

```
pages commune          : 3960
pages avec <noscript>  : 0
page témoin commune/28001.html : 397 Ko
décimales hors <script> : 0,01 | 1.0 | 2.0
```

Les données sont bien dans le HTML, mais enfermées dans un `<script>`. Le seul
`0,01` visible sans JS appartient à un paragraphe de garde-fou. La page de
département, elle, écrit déjà son bloc de tête en dur.

### Ce qui vient de l'auditeur et n'a PAS été revérifié

La documentation décrirait un dépôt d'il y a quatre jours — 17 des 35 fichiers
Python de production absents de l'arborescence du README, dont `site/publier.py`
— et quatre implémentations du formatage de nombre coexisteraient avec trois
précisions par défaut différentes. **À confirmer avant d'agir dessus.**

### Les trois chantiers proposés, dans l'ordre, avec le premier geste

- **A — refermer la boucle publication → contrôle.** Appeler
  `tests/test_sorties.py` en tête de `site/publier.py:main()` et sortir en
  erreur si le code de retour n'est pas 0.
- **B — rendre la page de commune lisible sans JavaScript.** Écrire en dur le
  bloc de tête (commune, date, trois verdicts, « n notés sur m », version) depuis
  `d0`, `site/build_site.py:2123`.
- **C — une seule commande pour ajouter un département.** Créer
  `src/publier_departement.py` : refuser de continuer si `--termine` ne rend
  pas 0, écrire la ligne dans `referentiel/departements_publies.csv`, puis
  enchaîner figeage, build et contrôle. Cette étape n'est aujourd'hui écrite que
  dans l'en-tête de ce CSV.

**Aucun de ces constats n'est une décision prise** : l'auditeur diagnostique,
l'arbitrage revient à Yannick.

### 20.17 REPUBLICATION FAITE ET VÉRIFIÉE — 13 août, 19 h

Chaîne automatique déclenchée seule à 18 h 17, une minute après la libération
de la base. Journal : `data/journal/apres_refigeage_2026-08-13.log`.

| étape | durée |
|---|---|
| refigeage complet | **396 min** — 25 297/25 297, aucune erreur |
| dossiers de faits | **1 min** |
| reconstruction du site | **42 min** (18 h 18 → 19 h 00) |

**Débit mesuré de la reconstruction : 112 fiches/minute.** 4 924 fiches de
commune, 1,2 Go. À reprendre pour toute estimation future.

**Le corpus publié**, mesuré sur la page d'accueil reconstruite :

| | 12 août | 13 août |
|---|---|---|
| communes documentées | 3 978 | **4 919** (dont 3 041 par leur réseau) |
| analyses complètes | 12 644 | **25 284** |
| bascules | 1 138 | **1 151** |
| dépassements à la date | 454 | **572** |

25 284 publiées contre 25 297 figées : les 13 manquantes sont les bulletins
d'essai des départements non publiés. Cohérent.

**LES QUATRE CHANGEMENTS DU JOUR, VÉRIFIÉS SUR LES PAGES RÉELLES**

1. **Le tableau de département porte 9 colonnes** avec de vraies valeurs, et la
   page **ne défile plus latéralement** — le tableau défile dans son cadre, nom
   de commune collé à gauche. Vérifié sur l'Aveyron, 286 lignes.
2. **Les deux nouvelles colonnes sont alimentées** : « hors de portée du
   laboratoire » (compte + taux sur une seconde ligne grise, `display:block`
   vérifié) et « statut hormonal » en trois nombres non additionnés.
3. **Sicoval réparé.** Baziège porte désormais en sous-titre *« 31 · réseau
   SICOVAL MONTAGNE NOIRE, analyse prélevée à Odars »*, et dans ses
   métadonnées : réseau **SICOVAL MONTAGNE NOIRE**, gestionnaire **SICOVAL
   AEP**, distributeur **SICOVAL**. Les trois sont enfin distingués.
   La page de la Haute-Garonne titre **« Les réseaux de distribution — 143 »**
   (l'ancien « Les gestionnaires déclarés » a disparu), chaque entrée nommant
   son gestionnaire — 143 mentions.
4. **La page Méthode porte le calcul de l'indice de danger**, exemple chiffré
   compris (3,4667 sur trois substances).

**DÉFAUT TROUVÉ À LA VÉRIFICATION — le site ne nettoie jamais son dossier de
sortie.** Dix fichiers du 11 août survivent : les pages de département **01,
15, 17, 22, 46** et les cinq fiches de commune qui les citent (01027, 15003,
17415, 22266, 46040). Ces départements **ne sont pas publiés** ; ces pages
portent une version de référentiel périmée et un corpus d'il y a deux jours.

Elles ne sont **atteignables par aucun lien du site actuel** — chaque page de
département périmée n'est citée que par sa fiche périmée, l'îlot est clos —
mais elles restent servies à qui a l'URL. **Sévérité faible aujourd'hui,
croissante à chaque campagne**, et une page qui affiche un estampillage périmé
est exactement ce que la traçabilité du §8bis existe pour empêcher. À traiter :
soit `build_site.py` nettoie, soit une purge du dossier avant reconstruction.

**RESTE À FAIRE**, dans l'ordre : la purge des générations périmées (base
libre, à faire maintenant que le site est vérifié) ; le second lot d'appels
pour les communes PACA ; l'écriture de l'alerte.

### 20.18 PURGE — la purge elle-même était aveugle, corrigée puis exécutée

**`src/purger_versions.py` répondait « rien à purger » alors que quatre
générations cohabitaient.** Cause : il énumérait les versions sur la seule
`analyses_figees`. Or un refigeage complet réécrit cette table sous la version
courante et y **fait disparaître les anciennes** — pendant que
`couverture_communes` et `lq_corpus` gardent les leurs, orphelines et
invisibles. C'est le point aveugle annoncé au §19.1, et il rendait l'outil
inopérant exactement quand il servait.

État constaté avant correction :

| table | versions |
|---|---|
| `analyses_figees` | 1 |
| `verdicts_figes` | 1 (10 097 257 lignes) |
| `couverture_communes` | **4** |
| `lq_corpus` | **3** |

**Corrigé** : l'énumération porte sur **toutes** les tables estampillées, la
date se prend là où elle existe (`verdicts_figes` n'a pas `calcule_le`), et
l'affichage distingue une génération **orpheline** — plus aucun bulletin, mais
des lignes ailleurs. Deux défauts de ma correction attrapés à l'exécution : la
requête de date sur une table qui n'a pas la colonne, et un dépaquetage resté à
trois valeurs dans le récapitulatif final. **Les suppressions, elles, avaient
abouti** — c'est l'affichage de fin qui a échoué.

**Exécuté** avec la règle du 10 août (`--garder 2`) : `435b9a089f1d` et
`a74139a57d87` supprimées, **1 625 lignes**. Base 1 837 Mo avant et après : ces
générations ne pesaient rien. **La place n'était pas l'enjeu — la cohérence
l'était.**

**Reste une anomalie, non traitée, décision de Yannick** : la génération
conservée `f3e1d448101f` est **orpheline** — 3 983 lignes dans
`couverture_communes` et `lq_corpus`, **aucun bulletin**. Elle ne peut donc
servir de filet de sécurité, ce qui était la raison d'être de la règle « on
garde une antérieure ». La règle a été écrite quand les générations
antérieures étaient complètes ; elle ne décrit plus la situation. À trancher :
`--garder 1` la supprimerait.

**Suite, décision de Yannick du 13 août au soir : `--garder 1`.** La génération
orpheline `f3e1d448101f` est supprimée à son tour (3 983 lignes).

**La base ne porte plus qu'UNE génération, et elle est complète** — vérifié
table par table après coup :

| table | versions | lignes |
|---|---|---|
| `analyses_figees` | 1 | 25 297 |
| `verdicts_figes` | 1 | 10 097 257 |
| `couverture_communes` | 1 | 5 102 |
| `lq_corpus` | 1 | 1 060 |

**La règle « on garde la publiée et une antérieure » est donc suspendue de
fait**, faute d'antérieure qui vaille. À réécrire quand une génération
complète coexistera de nouveau : ce qui mérite d'être gardé, c'est une
génération **avec ses bulletins**, pas une version au sens du numéro.

### 20.19 L'ALERTE EST ÉCRITE ET CÂBLÉE — 13 août, 19 h 30

**Le relevé** : `data/suivi_panel/alerte_panel_reduit.csv`, **559 communes**
(398 avec analyse propre, 161 rattachées), un appel Hub'Eau chacune, deux lots.
Incidents réseau repris automatiquement.

**PACA n'apporte aucun cas d'abandon.** 146 candidats à 24 mois — 04 (55),
05 (54), 06 (25), 83 (6), 84 (5), 13 (1) — et **zéro** substance abandonnée.
Le total reste **23 communes sur 559** : 21 en Eure-et-Loir, 1 dans le Gers,
1 en Tarn-et-Garonne. **Cela renforce le §20.16** : le phénomène suit la
substance dépassée, pas le territoire ni la profondeur de collecte.

**Le module** : `src/suivi_panel.py`. Il compose **le texte en Python**, pas
dans le navigateur — les deux bandeaux voisins ont leur prose en dur dans
`site/gabarits/fiche.js` et **aucun contrôle de sortie ne les relit**. La clé
`alerte_panel` descend dans le JSON de la fiche via `sortie/build_fiche.py`.

**Trois règles inscrites dans le code, pas seulement dans la note :**

1. **sans le nombre de contrôles, aucune alerte** — l'ancienneté seule se lit
   comme un abandon de surveillance, et ce serait faux ;
2. **le bandeau est GRIS, jamais ambre** — l'ambre est la couleur d'un verdict
   ici, et cette alerte n'en est pas un ;
3. **le troisième paragraphe n'existe que s'il y a matière** — inventer un
   manque serait un faux positif. 536 communes sur 559 reçoivent l'alerte
   d'ancienneté sans liste de substances.

**Vérifié dans le navigateur** sur une page réellement construite
(Oinville-Saint-Liphard) : bandeau gris présent, cinq paragraphes, gras rendu,
aucun marqueur `**` résiduel. Essai construit dans `site/public/_essai`, puis
supprimé.

**Reste ouvert** : ajouter la clé `alerte_panel` à la moisson de
`tests/test_sorties.py`, sans quoi ce texte reste non contrôlé comme ses deux
voisins — c'est le défaut qu'on vient d'éviter, il faut refermer la porte.
Et les dix pages périmées du 11 août que le site ne nettoie pas (§20.17).

### 20.20 REPUBLIÉ AVEC L'ALERTE — 13 août, 20 h 10, vérifié

Reconstruction complète relancée à 19 h 27, terminée à 20 h 09 — **42 minutes**,
exactement le même temps que la précédente. 6 pages, **17 pages de
département**, **4 919 fiches**, 21 exports, **1 151 Mo**.
Journal : `data/journal/republication_alerte_2026-08-13.log`.

**558 fiches portent l'alerte** (559 au relevé ; l'écart est une commune sans
page). Vérifié dans le navigateur sur deux cas réels :

- **Oinville-Saint-Liphard** — analyse propre, 119 mois, trois substances
  nommées, l'encart sur la somme des pesticides ;
- **Les Autels-Villevillon** — commune **rattachée**, 35 mois : les deux
  bandeaux cohabitent proprement, celui du réseau (« analyse empruntée ») puis
  celui de l'ancienneté (« du réseau qui alimente cette commune »), et ils ne
  se répètent pas.

Fond gris confirmé (`rgb(232,236,239)`), aucun marqueur `**` résiduel.
Une commune de PACA porte bien l'alerte d'ancienneté seule — 04009, 107 mois,
sans liste de substances, ce qui est le comportement voulu.

**LES DIX PAGES PÉRIMÉES DU 11 AOÛT SONT TOUJOURS LÀ** — deux reconstructions
complètes n'y ont rien changé, ce qui confirme que le site n'efface jamais son
dossier de sortie. Départements 01, 15, 17, 22, 46 et les cinq fiches qui les
citent. **À traiter au prochain passage.**

**ÉTAT DE LA JOURNÉE — tout ce qui était prévu est fait et vérifié** : PACA
versé (25 297 bulletins), refigé, publié ; tableau de département réparé et
enrichi de deux colonnes ; Sicoval corrigé sur 2 829 fiches et sur les pages de
département ; calcul de l'indice de danger publié ; base purgée et ramenée à
une seule génération complète ; alerte « analyse complète ancienne » conçue,
sourcée, écrite, câblée et publiée sur 558 fiches.

**FILE D'ATTENTE À LA REPRISE**, par ordre :

1. **ajouter `alerte_panel` à la moisson de `tests/test_sorties.py`** — ce
   texte est publié sur 558 fiches et rien ne le relit encore ; c'est le
   défaut qu'on a voulu éviter, il reste ouvert d'un cran ;
2. **le nettoyage du dossier de sortie** (les dix pages périmées) ;
3. **la recherche documentaire sur les marchés d'analyses de l'ARS
   Centre-Val de Loire** — le maillon qui transformerait l'hypothèse en fait,
   et il n'est pas informatique ;
4. la dilution, bloquée sur le sourçage des minéraux (§20.12) ;
5. l'origine des seuils pesticides (§20.14 point 3) ;
6. la source data.gouv.fr et le risque d'injustice sur le plomb (§20.11).

---

## 22. ÉTAT ACTUEL au 13 août 2026, 20 h 30 — À LIRE EN PREMIER

**Cette section remplace le §19 en entier.** Le §20 raconte la journée du
13 août dans le détail ; celle-ci porte l'état et la file d'attente.

### 22.1 RIEN NE TOURNE — la base est libre, le site est à jour

Aucun processus en cours. Aucune décision en attente de Yannick.

- **Corpus : 25 297 analyses complètes**, 17 départements publiés
  (28, 81, 69, 09, 31, 12, 32, 47, 65, 71, 82 + **04, 05, 06, 13, 83, 84**) ;
- **Site republié et vérifié** à 20 h 09 : 4 919 fiches, 17 pages de
  département, 1 151 Mo, version `d0fb678dcbe2` ;
- **Base ramenée à UNE seule génération complète**, purgée dans les quatre
  tables estampillées ;
- **Le dépôt est désormais versionné** (branche `chantier-interface`) — ce
  n'était pas le cas le 12 août. **Aucun dépôt distant** : `git push` est
  impossible, la sauvegarde reste locale.

### 22.2 LES COMMANDES QUI SERVENT

```
py -X utf8 src/moisson.py --depts 04,05 --tous      # réseau, base LIBRE
py -X utf8 src/ingerer.py --depts 04,05 --sans-figer
py -X utf8 src/ingerer.py --tous --refiger          # ~6 h 30 sur 25 000
py -X utf8 src/purger_versions.py --garder 1 --faire
py -X utf8 sortie/rediger_lot.py --dossiers
py -X utf8 site/build_site.py                       # 42 min mesurées
py -X utf8 src/relever_suivi_panel.py               # relevé de l'alerte
py -X utf8 src/md_en_pdf.py <fichier.md> --sortie docs/pdf
```

**Durées mesurées le 13 août, à réutiliser** : ingestion **19 bulletins/min** ;
refigeage **63 bulletins/min** (396 min sur 25 297) ; construction du site
**112 fiches/min** (42 min) ; dossiers de faits **1 min** ; relevé de l'alerte
**1 appel Hub'Eau par commune**, ~1,5 s.

### 22.3 LA FILE D'ATTENTE — un sujet à la fois, décision de Yannick

1. **Ajouter `alerte_panel` à la moisson de `tests/test_sorties.py`.** 558
   fiches portent un texte que rien ne relit. Le texte est déjà en Python pour
   ça (`src/suivi_panel.py`) — il ne manque que la moisson. **Petit, et c'est
   la dette la plus fraîche.**
2. **Le site n'efface jamais son dossier de sortie.** Dix pages du 11 août
   survivent à deux reconstructions : départements 01, 15, 17, 22, 46 et les
   cinq fiches qui les citent. Non publiés, estampillage périmé, inatteignables
   par un lien mais servis à qui a l'URL.
3. **La recherche documentaire de Yannick** — marchés d'analyses de l'ARS
   Centre-Val de Loire (§19.5). **Le maillon qui transformerait l'hypothèse en
   fait, et il n'est pas informatique.**
4. **Dilution** — verrou unique et identifié : le statut conservatif des
   minéraux (§20.12). Puis le crible des 66 réseaux portant l'amont et l'aval.
5. **Origine des seuils pesticides** (§20.14 point 3) — la valeur est sourcée,
   sa justification ne l'est pas, et notre référentiel écrit « zéro de
   substitution » en citant un texte qui ne le dit pas.
6. **La source data.gouv.fr** et le risque d'injustice sur le plomb (§20.11
   point 4) — le plus lourd de conséquences, le moins mûr.

### 22.4 CE QUI N'EST PAS À MOI, ET QUE JE N'AI PAS COMMITÉ

`docs/AUDIT_FORME_2026-08-13.md` et `docs/CONSIGNE_AUDIT_FORME.md`, écrits par
une autre session le 13 août à 14 h 38. **Laissés non suivis par git**
volontairement : je ne les ai ni lus ni vérifiés. À intégrer par qui les a
écrits, ou après relecture.

### 22.5 LES TROIS PIÈGES DE LA JOURNÉE — à ne pas refaire

- **Le test binaire « a-t-il été mesuré depuis »** rate les abandons. C'est
  l'ancienneté de la dernière mesure qui fait foi. Réclainville ressortait
  « rien d'abandonné » alors que trois substances s'arrêtent en 2020 ;
- **un outil qui répond « rien à faire » se vérifie.** La purge disait « rien à
  purger » avec quatre générations en base : elle ne regardait qu'une table ;
- **un superlatif non compté est un faux.** « Le département le plus
  profondément collecté » a circulé de note en note sans que personne ne le
  compte — et il était faux.

---

## 23. Clôture de session du 13 août 2026, 21 h 10 — phase C de l'audit interrompue

**Arrêt propre.** Tous les processus Python ont été arrêtés sur demande : les
deux builds de l'audit et le serveur `http.server` du port 8765. Base libre,
aucun `.wal` résiduel, aucune écriture en attente. Rien n'a été commité.

### Ce que la phase C a donné avant l'interruption

- **`tests/test_sorties.py` ÉCHOUE** : code de sortie 1, 8,33 s, sur le contrôle
  « la fiche autonome porte cette version ». **Conséquence directe sur le
  chantier A** : brancher ce contrôle sur `site/publier.py` aujourd'hui
  bloquerait toute publication. Le chantier A n'est donc pas le geste d'une ligne
  annoncé l'après-midi — l'échec se traite d'abord.
- **Le `diff` de reproductibilité n'a PAS été fait.** `buildA` a été interrompu à
  4 092 fichiers produits pour ~4 984 attendus (débit mesuré : 2,4 fichiers/s,
  démarré à 20:34:25). `buildB` n'a jamais démarré. Compter **~35 min** pour
  refaire les deux.
- **Le goulot et l'épreuve du facteur 100 ne sont pas mesurés.**
- L'audit n'a **jamais touché `site/public`** : `site/build_site.py` accepte
  `--sortie`, les deux builds écrivaient dans un répertoire temporaire.

### L'état du site, et pourquoi il ne prouve rien

Le site a été republié à 20:09 **par une autre session**, avec six départements
de plus. Mesuré après cette republication :

```
pages commune : 4924
entrees : 5090 | pointant une page : 4919 | LIENS MORTS : 0
departements : 04 05 06 09 12 13 28 31 32 47 65 69 71 81 82 83 84
```

**Les 23 liens morts du Lot-et-Garonne mesurés à 15 h ont disparu — par
republication, pas par correction.** Le défaut n'a reçu aucun diagnostic : rien
ne dit qu'une prochaine publication partielle ne le reproduira pas. C'est
exactement ce que le chantier A vise, et la question posée à l'auditeur — le
défaut est-il dans la publication ou dans la génération de l'index ? — **reste
sans réponse mesurée.**

### Un constat de chaîne, né de la journée elle-même

Deux sessions ont travaillé en concurrence sur ce dépôt le 13 août : l'une
auditait, l'autre publiait et écrivait dans ce fichier. **Rien dans la chaîne
n'empêche deux publications concurrentes**, et l'audit a dû mesurer une cible
mouvante. À verser à l'axe 2.

### Pour reprendre

Deux entrées possibles, dans cet ordre de préférence :

1. **Traiter l'échec de `tests/test_sorties.py`** — il bloque le chantier A et
   c'est le seul résultat dur de la phase C.
2. **Relancer la phase C** (~35 min) : deux builds via
   `site/build_site.py --sortie <répertoire temporaire>`, jamais vers
   `site/public` ; puis le `diff`, la mesure du goulot, le facteur 100.
   `src/build_db.py` et `src/figer.py` restent interdits à l'auditeur.

Rapport de l'audit : `docs/AUDIT_FORME_2026-08-13.md`. Consigne appliquée :
`docs/CONSIGNE_AUDIT_FORME.md`. Contexte des phases A et B : §21 ci-dessus.

---

## 24. Mesures de la phase C — consignées le 14 août 2026 à 08 h 45, hors du rapport

**Pourquoi ici et pas dans le rapport d'audit.** L'auditeur a été interrompu à
08 h 38 par une erreur serveur (`API Error: 529 Overloaded`) avant d'avoir
reporté ses mesures dans `docs/AUDIT_FORME_2026-08-13.md`. Elles ne vivaient
plus que dans une conversation. **Une mesure qui n'est pas sur disque n'existe
pas** — elles sont donc écrites ici, telles quelles, en attendant que
l'auditeur les intègre à son rapport.

### 24.1 Le goulot n'est pas où on le croyait — c'est `sys.path`

Profil d'un build réel du **Tarn-et-Garonne** (195 communes, **98,4 s**) :
**12 815 appels `execute()`**, dont **34,6 s passées à rescanner `sys.path`**.
DuckDB tente d'importer `pandas` et `pyarrow` à chaque appel, ne les trouve pas,
et **ne met pas l'échec d'import en cache**.

```
2,282 ms par execute()  avec le sys.path gonflé par le dépôt
0,859 ms par execute()  avec le sys.path de base
        soit +165,6 %
```

**Vérifié en session principale** : `pandas` ABSENT, `pyarrow` ABSENT,
`duckdb 1.5.5`.

**Ce n'est pas une recommandation d'installer `pandas`** : l'installer changerait
le comportement de DuckDB lui-même. C'est un constat mesuré, l'arbitrage revient
à Yannick.

### 24.2 Le facteur 100 cède sur UN gros département, pas sur leur nombre

Maillon : **`site/build_site.py:1720`** — `rows = con.execute(requete, …).fetchall()`,
qui charge tout l'export en mémoire d'un coup. Mesuré au `tracemalloc` :

```
233 038 lignes (dépt 82)  →  270 Mo        soit 1 213 octets / ligne
1 787 047 lignes (le Var, DÉJÀ au corpus)  →  2,02 Go en un seul fetchall()
```

**Vérifié en session principale** : la ligne 1720 fait bien `.fetchall()` ;
l'écriture qui suit est en flux (générateur, ligne 1724). C'est donc bien la
lecture, pas l'écriture, qui porte le risque.

### 24.3 Le soupçon de tri instable est INFIRMÉ — l'auditeur se contredit lui-même

Trois builds directs successifs du 82 : **218 fichiers sur 218 identiques octet
pour octet**. Le rendu HTML est reproductible.

Ce qui diffère, et c'est beaucoup plus petit : les `verdicts_*.csv.gz` changent à
chaque build **à contenu décompressé identique** — l'en-tête gzip écrit à
`site/build_site.py:1726` porte un horodatage.

### 24.4 Ce qui n'est PAS fait

**La durée du build complet, elle, est mesurée** — c'était l'une des épreuves
du §4 :

```
buildA | code de sortie 0 | duree 2 486,8 s (41,4 min) | 4 974 fichiers
```

Reste le `diff` des **deux** builds complets. `buildB` s'est arrêté à
2 410 fichiers sur 4 956 le 14 août à 09 h 01, sans erreur au journal, avec
389 Go de disque et 9,9 Go de RAM libres — **ni la mémoire ni l'espace ne sont
en cause, et la cause réelle n'est pas établie** ; l'hypothèse la plus
vraisemblable est le nettoyage des processus rattachés à l'agent d'audit, mort
une minute plus tôt d'une erreur serveur. À ne pas imputer au dépôt sans
preuve.

`buildA` étant complet et valide, **il suffit de relancer UN build** (~41 min)
et de comparer les deux arborescences.

### 24.5 Le `diff` des deux builds complets — ÉPREUVE NON CONCLUANTE

Menée le 14 août 2026. **Le résultat ne peut pas être interprété**, et il faut
dire pourquoi avant de citer le moindre chiffre.

```
buildA | code 0 | 2 486,8 s (41,4 min) | 4 974 fichiers   [08:02 → 08:43]
buildB | code 0 | 2 385,8 s (39,8 min) | 4 974 fichiers   [09:03 → 09:43]

seulement dans A : 0      seulement dans B : 0
DIFFERENTS : 4 964  →  4 946 .html, 17 .csv.gz, 1 .css
```

**Ces 4 964 fichiers ne mesurent pas le non-déterminisme du build.**
`site/gabarits/observatoire.css` a été modifié **à 08 h 24 34, pendant
`buildA`**, par une session travaillant en parallèle (42 488 o / 708 lignes du
côté A, 43 790 o / 730 lignes du côté B). Les deux builds ne partent donc pas du
même code source. La précaution prise portait sur la base — inchangée depuis le
13 août 19 h 12 — mais **pas sur le dépôt** : c'est un défaut du protocole de
mesure, pas un défaut du dépôt.

**Ce qui reste valide malgré tout :**

1. **Deux durées cohérentes pour un build complet** : 41,4 et 39,8 min sur
   ~4 974 fichiers.
2. **Le build produit exactement le même ENSEMBLE de fichiers** : 4 974 des deux
   côtés, zéro fichier orphelin d'un côté ou de l'autre. Le grief « le site
   n'efface jamais son dossier de sortie » ne se reproduit pas ici — mais ces
   builds visaient un répertoire neuf, ce qui n'est pas le cas de `site/public`.
3. **Un mécanisme de conception, mesuré** : les pages portent
   `observatoire.css?v=<hash>`. **Modifier une seule ligne de CSS fait donc
   changer les 4 946 pages HTML.** C'est voulu — c'est un cache-buster — mais
   cela signifie qu'aucun `diff` de publication ne sera jamais lisible après une
   retouche de style : tout bouge à chaque fois.

**Ce qui n'est PAS établi** : le déterminisme du rendu à l'échelle du site
complet. La seule mesure propre reste celle du Tarn-et-Garonne (§24.3) : trois
builds successifs, 218 fichiers sur 218 identiques octet pour octet. Elle a
abouti **parce qu'elle était courte**.

**L'enseignement de méthode, et il vaut pour l'axe 2** : sur ce dépôt, une
épreuve de reproductibilité de 80 minutes ne peut pas aboutir tant qu'une autre
session modifie le code en parallèle. Refaire cette épreuve suppose de **geler
le dépôt** le temps des deux builds — ou de se contenter de l'échelle
départementale, qui tient en quelques minutes.

---

## 26. ÉTAT ACTUEL au 14 août 2026, 20 h 15 — campagne de 7 départements, refigeage EN COURS

**Cette section remplace le §22 sur l'état du corpus.** Elle est écrite pendant
que le refigeage tourne : au moment où tu la lis, il a fini ou il est mort.
**Commence par le journal, pas par ce texte.**

### 26.1 CE QUI TOURNE — un refigeage complet, détaché de toute session

```
PID au lancement : 6196          (lancé le 14 août à 20 h 14)
journal          : data/journal/refigeage_2026-08-14.log
erreurs          : data/journal/refigeage_2026-08-14.err
commande         : py -X utf8 -u src/ingerer.py --tous --refiger
```

**40 745 bulletins à refiger sous `d0fb678dcbe2`.** Compter **~11 h** à
63 bulletins/min, donc une fin vers 7 h - 9 h le 15 août, probablement plus tard
— le débit baisse à mesure que la base grossit (mesuré ce jour : l'ingestion est
passée de 47 à 23 bulletins/min selon le département).

Le journal porte un jalon tous les 5 % avec le temps restant estimé, écrit avec
`flush=True`. **Il survit à la mort du processus** — c'est la seule source de
vérité sur l'avancement. Il est en UTF-8 ; `Get-Content` de PowerShell l'affiche
avec des accents cassés, `tail` le rend correctement — c'est la console qui
déforme, pas le fichier.

**Trois lectures possibles de la dernière ligne :**

| ce que dit le journal | ce que ça veut dire | quoi faire |
|---|---|---|
| le bilan du figeage + « la base est rendue » | terminé | passer à la suite (§26.4) |
| un jalon `N/40745`, processus mort | coupé en route | **tout relancer**, même commande |
| `MoteurChange` | `figer.py` a rebougé pendant | relancer avec `--refiger` |

**Le refigeage ne reprend PAS où il s'est arrêté** : en mode `complet`, la liste
à traiter est le corpus entier, sans saut des bulletins déjà refaits. Une
interruption coûte tout le temps écoulé — **mais rien n'est détruit** : le
remplacement se fait bulletin par bulletin, et `figeage_moteur` n'est écrit
qu'à la toute fin, donc une base à moitié refigée refuse tout autre figeage au
lieu de mélanger deux calculs (leçon du 11 août, §17).

### 26.2 POURQUOI un refigeage complet et pas incrémental

**`src/figer.py` a été modifié le 14 août par une autre session** (non commité au
lancement, 19 insertions) : l'indice de danger divisait par `seuil_2026_effectif`
— la valeur du jour — au lieu de `seuil_applicable`, la valeur en vigueur à la
date du prélèvement. C'est le §2.10 appliqué à l'indice comme il l'était déjà au
verdict. Exemple porté par le commentaire du code : à Thiville, le
chlorothalonil R471811 donnait un indice de 15,15 contre 0,9 µg/L, et 29,2
contre la valeur applicable à la date.

`version_moteur()` a donc changé, et le figeage incrémental **refuse** de
tourner. Le refigeage complet n'était pas un choix.

**Conséquence à ne pas manquer : l'indice de danger change sur TOUT le corpus
déjà publié**, pas seulement sur les sept nouveaux départements. Les chiffres
d'effet cocktail des fiches en ligne sont périmés jusqu'à republication.

### 26.3 LE CORPUS APRÈS LA CAMPAGNE

**40 725 analyses complètes, 15 534 040 mesures, 33 départements représentés.**
Le corpus passe de 25 297 à 40 725 bulletins, **+61 %**.

Sept départements moissonnés le 14 août, **tous à 100 %, `--termine` rend 0 pour
chacun**, zéro erreur résiduelle :

| dept | communes | bulletins | installations | analysées | rattachées | non doc. |
|---|---|---|---|---|---|---|
| 48 Lozère | 152/152 | 446 | 228 | 87 | 15 | 23 |
| 07 Ardèche | 335/335 | 1 973 | 449 | 212 | 115 | 8 |
| 26 Drôme | 362/362 | 1 227 | 258 | 205 | 99 | 58 |
| 38 Isère | 512/512 | 5 338 | **729** | 372 | 133 | 5 |
| 42 Loire | 320/320 | 1 803 | **152** | 114 | **194** | 11 |
| 68 Haut-Rhin | 366/366 | 2 146 | 272 | — | — | — |
| 67 Bas-Rhin | 514/514 | 2 516 | 246 | — | — | — |

**2 561 communes, 15 449 bulletins.** Les cinq premiers ont été demandés par
Yannick dans cet ordre ; le 68 et le 67 ont été ajoutés en cours de journée pour
sortir du sud — voir §26.5.

**Deux profils opposés, à retenir avant toute comparaison (§2.11) :**

- **l'Isère est fragmentée**, pas sur-analysée. 729 installations de production,
  contre 150 à 450 partout ailleurs, sur la même période 2016-2026. Ses 7,3
  bulletins par installation sont *en dessous* de la Loire (11,9), du Bas-Rhin
  (10,2) et du Tarn (8,6). Département de montagne, très nombreux petits
  captages indépendants ;
- **la Loire est l'inverse** : 152 installations pour 320 communes, de gros
  syndicats, d'où **194 communes rattachées au réseau pour 114 analysées** —
  seul département du corpus où les rattachées dominent. Le §8bis n° 5
  s'applique en force : dire où le prélèvement a été fait.

**Mesures de débit du 14 août, à réutiliser** — elles corrigent celles du 13 :

| geste | débit mesuré |
|---|---|
| moisson | 2,5 à 6,8 s/commune, 4 ouvriers ; 2,0 à 2,5 appels/s (plafond projet : 3,0) |
| ingestion | **47/min** (42+68+67), **41/min** (48+07), **23/min** (38 Isère) |
| refigeage | 63/min au 13 août sur 25 297 — **à remesurer**, il baisse avec la taille |

Le débit d'ingestion **n'est pas une constante** : il tombe de moitié sur un gros
département en fin de campagne. Ne pas reporter 47/min sur un devis.

### 26.4 CE QUI EST INTERDIT, ET CE QUI ATTEND

**Décision de Yannick, 14 août : ne rien publier.** Il reprend entièrement le
graphisme des fiches (`docs/CHARTE_GRAPHIQUE.md`, `site/gabarits/observatoire-v2.css`,
`marque.svg`, `polices/` — non commités, ce n'est pas mon travail).
**`site/build_site.py` et `site/publier.py` ne doivent pas être lancés.**

Figer et publier sont deux étages séparés : figer calcule et estampille en base,
publier ne fait que rendre ce qui est déjà figé. D'où l'ordre choisi — figer
cette nuit, publier quand la charte sera prête, **sans repayer 11 h**.

Ce qui attend, une fois le refigeage terminé :

1. **Relever les chiffres des sept départements** — conformes 2026 avec bascule,
   conformes à la date, dépassements sur limite, couverture. **Jamais sans leur
   version de référentiel** (§13.1). Aucun n'a encore été lu : au 14 août au
   soir, **on ne sait rien des excès ni des bascules de ces départements.**
2. **`v_parametres_non_apparies` sur un corpus de 33 départements** — le compte
   va monter, et chaque libellé nouveau est un paramètre qui ne pèse sur aucun
   verdict.
3. **L'Alsace, et la raison éditoriale de l'avoir collectée** : voir §26.5.
4. La file du §22.3 reste ouverte, inchangée.

### 26.5 POURQUOI L'ALSACE — le motif éditorial, à instruire

Le corpus était à 19 départements sur 21 au sud de la Loire. Le 68 et le 67 ont
été choisis le 14 août sur un raisonnement, **pas sur une source lue en
session** : la nappe d'Alsace, son héritage industriel (terrils salés des mines
de potasse, Stocamine, plateforme de Chalampé-Ottmarsheim, chrome d'Ochsenfeld).
**Tout cela est à sourcer avant le moindre usage (§2.7).**

**Ce qui rend ce terrain intéressant pour la thèse, et c'est vérifiable :** les
chlorures sont au référentiel à **250 mg/L de nature `reference`, pas `limite`**
(ligne code 1337, source REG-01, `verifie`). Une eau chargée en chlorures est
donc **hors de la référence de qualité sans être non conforme** — elle passe,
réglementairement. Le bloc « Hors de la référence de qualité » du §11.3 est
déjà écrit pour l'afficher.

Trois bénéfices de méthode : une ARS différente donc un marché d'analyses
différent donc un panel différent (met à l'épreuve la 3ᵉ règle du §2.11) ; un
motif de contamination **minéral et ponctuel** là où tout le corpus est pesticide
et diffus ; et une géographie enfin hors du sud.

**Réserve à tenir** : nos données sont l'eau **distribuée**, après captage,
mélange et traitement — pas la nappe. Un bassin industriel très contaminé peut
rendre une eau distribuée propre. **Il faut accepter que le résultat soit
« rien »**, et un résultat négatif ne fait pas un chapitre.

### 26.6 DEUX PIÈGES DE LA JOURNÉE

- **Le code de sortie 0 d'une moisson ne dit rien.** La Lozère est ressortie
  « terminée » à 125/152 : 27 communes en `ConnectionResetError 10054`, une
  salve coupée côté serveur, dont Mende et Marvejols. Idem 510/512 sur l'Isère,
  319/320 sur la Loire. **`--termine` est le seul juge**, et il a fonctionné
  les trois fois. Le relancer systématiquement, et relancer la moisson tant
  qu'il ne rend pas 0.
- **Deux sessions ont encore travaillé en parallèle sur ce dépôt**, et l'une a
  modifié `figer.py` pendant que l'autre collectait — ce que le §6 du CLAUDE.md
  interdit explicitement pendant une campagne. Coût : le refigeage complet de
  11 h au lieu d'un incrémental de 4 h. Ce n'est pas une faute de calcul, c'est
  un défaut de coordination, et il est maintenant chiffré.

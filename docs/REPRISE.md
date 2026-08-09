# Reprise — état au 8 août 2026

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

**b) 79 des 135 dépassements du Tarn portent sur une valeur de VIGILANCE**,
pas sur une limite de qualité — 53 sur l'ESA métolachlore, 16 sur le
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

### 9.5 Le plafond analytique à l'échelle (chantier C4)

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

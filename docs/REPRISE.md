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

## 8. Mise à jour du 9 août 2026 — la chute du panel a une cause réglementaire

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

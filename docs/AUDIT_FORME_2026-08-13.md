# Audit externe de forme — 13 août 2026

Application de `docs/CONSIGNE_AUDIT_FORME.md`. Périmètre : structure du code,
chaîne de production, livrable. Aucun jugement sur les seuils, les dates
d'applicabilité, l'angle éditorial ou la méthode réglementaire.

## État des épreuves

| Épreuve | Menée ? | Détail |
|---|---|---|
| `tests/test_verdict.py` | **oui** | code lu d'abord (base temporaire, `tests/test_verdict.py:204-208`) — passe, 14,01 s |
| `tests/test_figer.py` | **oui** | code lu d'abord (base temporaire, `tests/test_figer.py:44-48`) — passe, 7,36 s |
| Ouvrir des pages produites | **oui** | 5 pages ouvertes dans un navigateur sur `http://localhost:8765` + mesures sur 120 pages tirées au sort |
| Inventaire chiffré du §6 de la consigne | **oui** | vérifié ligne à ligne — voir §3 |
| `tests/test_sorties.py` | **non — reportée** | ouvre `data/eau.duckdb` en lecture (`tests/test_sorties.py:207`), base tenue en écriture exclusive par le refigeage en cours (PID 34848 depuis 11 h 26) |
| Build du site, diff de deux builds | **non — reportées** | `site/build_site.py` lit la même base |
| Mesure du goulot sur une unité réelle, épreuve du facteur 100 | **non — reportées** | même motif. Les soupçons correspondants sont en annexe, **sans chiffre**, désignés par `fichier:ligne` |

Aucun fichier du dépôt n'a été modifié hors celui-ci. Aucun processus n'a été
arrêté. Aucun appel Hub'Eau n'a été émis.

---

## 1. Verdict en cinq lignes

1. Le moteur est solide et il se prouve : deux suites de non-régression qui
   fabriquent leur propre base, passent en 21 s cumulées, et testent des règles
   de méthode et non des accesseurs. Un repreneur peut modifier `figer.py` sans
   avancer à l'aveugle.
2. Le code est **le meilleur document du dépôt** : chaque module porte une
   docstring qui dit ce qu'il fait, pourquoi, et quelle erreur l'a fait écrire.
   J'ai reconstitué la chaîne de production sans ouvrir un seul `.md`.
3. Ce qui ferait renoncer, premier motif : **le livrable ne tient pas ses
   propres invariants et rien ne l'en empêche.** 23 communes du Lot-et-Garonne
   sont dans l'index de recherche du site servi, en vert, et leur page n'existe
   pas — 404. Le contrôle qui attrape exactement ce cas est écrit
   (`tests/test_sorties.py:254-259`) et la publication ne l'exécute pas.
4. Ce qui ferait renoncer, second motif : **sur une page de commune, aucune
   valeur mesurée n'existe dans le HTML.** Sur 120 pages tirées au sort, la
   seule décimale présente hors du `<script>` est le « 0,01 » d'un paragraphe de
   garde-fou. Tout le reste est un littéral JavaScript rendu par le navigateur,
   sans `<noscript>`.
5. Ce qui coûtera au dixième contributeur : la documentation décrit un dépôt
   d'il y a quatre jours (18 des 35 fichiers Python de production sont absents
   de l'arborescence du README), et quatre implémentations du formatage de
   nombre coexistent avec trois précisions par défaut différentes.

---

## 2. Lecture froide — phase A

*Écrit avant toute lecture de `README.md`, `docs/` et du journal git. Non
retouché. Le `CLAUDE.md` du projet était chargé dans la session et a été traité
comme une déclaration d'intention, pas comme une description.*

### 2.1 Que fait ce dépôt, d'après le seul code et les seuls fichiers produits ?

Il rapatrie les analyses du contrôle sanitaire de l'eau potable depuis une API
publique (Hub'Eau), les range dans une base DuckDB en étoile
(`communes` / `prelevements` / `mesures`), puis confronte chaque mesure à un
référentiel de seuils tenu en CSV versionné (`referentiel/referentiel_seuils.csv`)
sous trois grilles à la fois — celle de 2016, celle d'aujourd'hui, la plus stricte
retenue. Le résultat de cette confrontation est ensuite *figé* dans trois tables
estampillées d'une empreinte de référentiel (`analyses_figees`,
`verdicts_figes`, `couverture_communes`), et ces trois tables seules alimentent
la génération d'un site statique.

Ce que produisent réellement les fichiers sur disque, mesuré :
3 986 fichiers HTML dans `site/public/` — 3 960 pages de commune, 16 pages de
département, 4 pages de substance, 6 pages de tête (`index`, `carte`,
`communes`, `substances`, `methode`, `sources`) — plus 11 exports
`donnees/verdicts_NN.csv.gz`, un `bulletins.csv` de 8,4 Mo et un
`couverture_communes.csv` de 4 144 lignes. Le corpus couvre 11 départements
déclarés publiés.

L'indicateur mis en avant partout dans le code produit est la *bascule* : une
mesure au-dessus de la limite de 2016 et sous celle d'aujourd'hui.

Deux surfaces annexes, non publiées : un serveur HTTP local
(`atelier/atelier.py`, 1 164 l.) qui sert de poste de pilotage, et un ensemble
de scripts d'étude (`src/etude_*.py`, `data/etudes/**/*.py`) qui écrivent des
Markdown hors chaîne.

### 2.2 Par quel fichier commencerais-tu si on te demandait d'ajouter un département ?

Par `src/moisson.py` — c'est la seule docstring du dépôt qui nomme à la fois
l'étape amont et l'étape aval (`moisson.py:19-32`), et `outils/moissonner.cmd`
la confirme en donnant la commande suivante en toutes lettres.

Mais je ne serais pas arrivé au bout avec ce seul fichier, et c'est le vrai
constat : rien dans `moisson.py` ni dans `ingerer.py` ne dit qu'il faut ensuite
inscrire le département dans `referentiel/departements_publies.csv`. Je ne l'ai
découvert qu'en lisant l'en-tête de ce CSV, où quarante lignes de commentaire
expliquent pourquoi il existe. Sans ce détour, j'aurais collecté, ingéré, figé,
reconstruit le site — et le département serait resté invisible, parce que
`site/build_site.py:1797` ne construit que ce que ce CSV énumère.

L'ordre que je reconstitue depuis le seul code, et que je n'ai trouvé écrit
nulle part en un seul endroit :

    src/build_db.py                          (une fois)
    src/moisson.py --depts NN --tous         (réseau, base libre)
    src/ingerer.py --depts NN                (base prise)
    src/figer.py
    éditer referentiel/departements_publies.csv   ← l'étape qui ne se devine pas
    site/build_site.py
    tests/test_sorties.py
    site/publier.py

Le seul endroit du dépôt qui enchaîne quatre de ces huit étapes est
`atelier/atelier.py:1032-1037` — une fonction d'un serveur web local, ce qui
n'est pas là qu'un repreneur ira chercher la séquence.

### 2.3 Qu'est-ce que tu n'as pas compris, et où t'es-tu perdu ?

**Deux chemins de collecte, et je ne sais pas lequel fait foi.**
`src/moisson.py` + `src/ingerer.py` d'un côté, `src/fetch_departement.py` de
l'autre (424 l., ses propres options `--figer --refiger --reingerer --termine`).
Les deux annoncent journal et reprise. `src/observer.py:22-26` dit que les deux
chemins avaient déjà divergé une fois. Un repreneur qui prend le mauvais ne s'en
apercevra pas tout de suite.

**Trois fichiers pour ce qui semble être une même chose.** `src/collecte.py`
(règle de couverture), `src/ingest.py` (un bulletin), `src/ingerer.py` (le lot).
Les noms ne portent pas la différence ; il faut ouvrir les trois.

**Quatre `redactions*.json` dans `sortie/`, et je n'ai pas su dire lequel fait
autorité** : `redactions.json` (138 Ko), `redactions_proposees.json` (298 Ko),
`redactions_substances_proposees.json`, `redactions_panel_proposees.json`. Un
`redactions_substances.json` est attendu par `dossier_substance.py:613` et
n'existe pas sur disque. Quatre fichiers de données à la racine d'un dossier de
code, aucun schéma, aucun index.

**`src/etude_panel.py` (352 l.), `src/etude_panel_reduit.py` (468 l.),
`src/etude_cause_c.py` (264 l.), `src/etude_melange.py` (230 l.)** vivent dans
`src/`, à côté du moteur, sans rien qui les en distingue au premier regard. Et
17 autres fichiers Python (2 528 l.) vivent sous `data/etudes/`, c'est-à-dire
dans le dossier de données. Je n'ai pas trouvé la règle qui range un script
d'étude ici plutôt que là.

**`atelier/atelier.py`** : 1 164 lignes, un `BaseHTTPRequestHandler`, du HTML,
du CSS et l'orchestration de la publication dans le même fichier. Rien d'autre
dans le dépôt ne l'importe. Je n'ai pas compris si c'est un outil vivant ou un
prototype qu'on garde.

**La page produite.** J'ai ouvert `site/public/commune/69266.html` dans un
navigateur avant de lire une ligne de `build_site.py`, et je n'ai pas compris
pourquoi 2 126 414 des 2 209 940 octets du fichier sont un unique
`<script>` inline. Le reste — les 13 170 caractères de texte réellement présents
dans le HTML — ne contient aucun chiffre : ni verdict, ni paramètre, ni mesure.

---

## 3. Écart annoncé / réel — phase B

### 3.1 L'inventaire du §6 de la consigne est juste

Vérifié, et il tient : 67 commits, dernier le 12 août ; 20 784 lignes de Python
sur 52 fichiers ; `src/` 22 / 8 590, `sortie/` 7 / 4 303, `site/` 2 / 2 616,
`atelier/` 1 / 1 164, `tests/` 3 / 1 583 ; les cinq plus gros modules aux
lignes annoncées ; 3 986 HTML, 25 293 `.gz`, 27 CSV, 19 `.jsonl` ;
`CLAUDE.md` 695 lignes ; `docs/REPRISE.md` 3 209, `docs/CHANTIERS.md` 2 664.

Une seule chose manque à cet inventaire, et elle est significative : la somme
des cinq dossiers listés fait 18 256 lignes, pour un total de 20 784. **Les
2 528 lignes manquantes sont 17 fichiers Python qui vivent sous `data/etudes/`**
— 12 % du code du dépôt, dans le dossier où l'on range les données. L'inventaire
ne les compte pas parce qu'on ne les voit pas.

### 3.2 La règle du `CLAUDE.md` que le code ne respecte pas

`CLAUDE.md` §2.14 énonce : « "Le plus strict identifié", jamais "le plus strict
au monde" ». La formule interdite est écrite **en dur trois fois** dans le
générateur : `site/build_site.py:1431`, `:1877`, `:2143`. Elle est présente
dans **les 3 960 pages de commune servies**, dont la balise
`<meta name="description">` — c'est-à-dire le texte qu'un moteur de recherche
affiche.

    $ grep -l "stricte au monde" site/public/commune/*.html | wc -l
    3960

### 3.3 La documentation décrit un dépôt d'il y a quatre jours

Quatre écarts mesurés, tous vérifiables sans exécuter quoi que ce soit :

- **`README.md:74-124`** — l'arborescence nomme 18 fichiers `.py` ; le disque en
  porte 35 dans `src/ sortie/ site/ tests/ atelier/`. **17 sont absents**
  (6 678 lignes), dont `site/publier.py` (441 l., le seul script qui met le site
  en ligne) et `tests/test_sorties.py` (366 l.) — que le même README dit de
  lancer à la ligne 210 ;
- **`CLAUDE.md:612`** — « aucun département n'a encore été collecté en entier ».
  `referentiel/departements_publies.csv` en déclare **11**, datés du 9 au
  12 août, et le site publie 11 pages de département.
  `docs/CHANTIERS.md:66` dit « le Tarn est fait », soit 1 sur 11 ;
- **taille du `CLAUDE.md`** — le fichier dit de lui-même, ligne 7, avoir été
  « ramené de 1 239 à ~400 lignes » ; `docs/REPRISE.md:920` dit « 607 lignes
  pour une cible de 400 » et « 32 750 octets » ; le disque dit **695 lignes,
  38 265 octets**. Trois chiffres, aucun courant ;
- **`docs/REPRISE.md:899-913`, « La séquence complète, dans l'ordre »** — la
  séquence canonique commence par `src/fetch_departement.py --dept NN --tous`,
  c'est-à-dire le chemin que **l'en-tête du même fichier** (`REPRISE.md:6-14`)
  déclare remplacé depuis le 11 août par `moisson.py` + `ingerer.py`. Ni
  `moisson.py`, ni `ingerer.py`, ni l'édition de
  `referentiel/departements_publies.csv` n'y figurent.

- **`docs/REPRISE.md:707-712`, « Publication — faite, contrôlée »** affiche
  « 683 commune(s) couverte(s), 0 sans page / 691 page(s) ». Le site servi
  aujourd'hui porte 4 144 communes couvertes, 3 986 pages et **23 sans page**.

### 3.4 Ce que la documentation annonce et qui est vrai

Trois affirmations vérifiées et exactes, à citer parce qu'elles sont ce qui
tient le dépôt debout :

- `CLAUDE.md` §6 règle 1, « `moisson.py` n'importe jamais `duckdb` » : exact,
  aucune occurrence d'import dans `src/moisson.py` ;
- `docs/ARCHITECTURE.md:107-113`, « le design vit dans un seul fichier » :
  exact — `sortie/build_fiche.py:876-878` inline les trois mêmes gabarits que
  `site/build_site.py:82` et `:1869` servent ;
- `tests/test_sorties.py` contrôle 5, « la vitrine n'appelle aucune ressource
  distante » : vérifié moi-même sur les 3 986 pages, **0 ressource distante**.

---

## 4. Tableau des constats

Du plus grave au plus léger. Un constat sans preuve a été supprimé.

| # | Axe | Constat | Preuve | Ce que ça coûte si on ne fait rien | Effort | Gain |
|---|---|---|---|---|---|---|
| 1 | 3 | **23 liens morts dans le site servi.** `donnees/index_communes.json` porte 23 communes du 47 avec `u: "commune/470XX.html"`, `k: "vert"` — la page n'existe pas. Vérifié en navigateur : `commune/47057.html` rend **404 File not found**. Le générateur les saute par deux `continue` silencieux ; la commune reste dans `couverture_communes` et dans l'index. | `site/build_site.py:2100-2101` et `:2105-2106` ; 23/4 144 entrées de `site/public/donnees/index_communes.json` sans fichier cible ; Bourlens (47036), Castillonnès (47057), Cavarc (47063)… | Un lecteur qui cherche sa commune reçoit une erreur serveur après avoir vu une pastille verte. C'est le seul cas du site où le lecteur ne sait pas s'il est devant une absence de donnée ou devant une panne. | faible | fort |
| 2 | 2 | **Le contrôle qui attrape le constat 1 existe et ne barre rien.** `tests/test_sorties.py:254-259` calcule exactement `sans_page`. Il n'est appelé que par `atelier/atelier.py:1036`, **après** la construction, et `site/publier.py` — le script d'envoi FTPS — ne l'appelle pas : aucune occurrence de `test_sorties` ni de `subprocess` dans ses 441 lignes. | `tests/test_sorties.py:254-259` ; `atelier/atelier.py:1032-1037` ; `grep -n "test_sorties\|subprocess" site/publier.py` → aucune ligne | Le dépôt sait détecter ses régressions de sortie et publie quand même. Chaque nouveau département rejoue le tirage. | faible | fort |
| 3 | 3 | **Aucune valeur mesurée dans le HTML d'une page de commune.** Sur 120 pages tirées au sort, la **seule** décimale présente hors du `<script>` est `0,01`, tirée du paragraphe de garde-fou. Zéro `<noscript>`. La page de département, elle, est complète sans JS (`departement/81.html` : 0 octet de script inline, 67 055 caractères de texte). | 120/120 pages commune → `('0,01',)` comme unique jeu de décimales hors script ; `commune/69266.html` : 2 126 414 des 2 209 940 octets en un `<script>`, texte hors script 13 170 car., `document.querySelectorAll('noscript').length === 0` | Sans JS — lecteur d'écran mal servi, extension de blocage, aperçu de partage, archivage, moteur qui n'exécute pas — la page ne dit rien de l'eau. Le projet devient invérifiable par le canal le plus simple : « voir la source ». | fort | fort |
| 4 | 2 | **La séquence de production n'est écrite nulle part en entier, et l'étape qui rend un département visible ne se devine pas.** L'édition de `referentiel/departements_publies.csv` n'apparaît dans aucune docstring de `moisson.py`, `ingerer.py`, `figer.py`, et pas non plus dans la « séquence complète » de `docs/REPRISE.md:899-913`, qui décrit par ailleurs l'ancien chemin de collecte. | `site/build_site.py:1797` (`depts or departements_publies()`) ; `docs/REPRISE.md:899-913` ; en-tête de `referentiel/departements_publies.csv` (40 lignes de commentaire, seul endroit où la règle est écrite) | Reproduction de l'erreur déjà documentée : collecter et figer sans publier. Un repreneur perd une demi-journée à comprendre pourquoi son département n'apparaît pas. | faible | fort |
| 5 | 1 | **Quatre implémentations du formatage de nombre à la française, trois précisions par défaut.** `fr(x, n=2)`, `fr(x, n=3)`, `_nb(x)` à 6 décimales, `_nb(x, dec=6)`. Le commentaire qui corrige le bug du `rstrip("0")` est **recopié mot pour mot** dans deux d'entre elles : la même correction a dû être faite deux fois. | `sortie/dossier_panel.py:51` ; `sortie/dossier_substance.py:84` ; `sortie/build_fiche.py:214` ; `sortie/indicateurs.py:71` | Le même nombre s'affiche avec deux arrondis selon la surface qui le rend. Erreur muette : rien ne casse, la valeur est simplement différente d'une page à l'autre. | faible | moyen |
| 6 | 1 | **Le code de production importe le code de test.** `sortie/rediger_lot.py:60` insère `tests/` dans `sys.path` puis `:66` `import test_sorties` ; `sortie/dossier_substance.py:609` fait de même pour atteindre `rediger_lot`. La dépendance est inversée. Cause structurelle : **19 fichiers font `sys.path.insert`**, il n'y a **aucun `__init__.py`, aucun `pyproject.toml`, aucun `setup.py`**. | `sortie/rediger_lot.py:59-66` ; `sortie/dossier_substance.py:609-610` ; `grep -rn "sys.path" --include=*.py` → 19 fichiers ; `find . -name "__init__.py" -o -name "pyproject.toml"` → vide | Renommer ou déplacer un fichier de test casse la chaîne de rédaction. Aucun outil (linter, IDE, `pytest`) ne résout les imports du dépôt sans exécuter les scripts. | moyen | moyen |
| 7 | 1/3 | **`site/build_site.py` : 2 175 lignes, 1 209 balises HTML littérales dans des f-strings Python, un seul gabarit lu.** Le mécanisme de gabarit existe (`site/gabarits/`) et n'est employé que pour `corps_fiche.html`. Aucun test ne couvre ce module — et le constat 1 prouve que ses erreurs sont muettes. | `site/build_site.py` : 1 918 des 2 175 lignes dans des corps de fonction, `lire("...")` appelé une seule fois, ligne 2082 ; 42 défs de niveau 0, la plus grosse 207 l. (`page_departement`, `:1151`) | La responsabilité que je détacherais : **les gabarits de page** (`accueil`, `carte`, `communes`, `departement`, `methode`, `sources`) vers `site/gabarits/`, comme `corps_fiche.html` déjà. Tant qu'elle reste dedans, toucher au design impose de relire du Python. | moyen | moyen |
| 8 | 1 | **Frontières illisibles sans les avoir apprises.** 2 528 lignes de Python (17 fichiers) vivent sous `data/etudes/` — le dossier de données —, et 1 314 lignes de scripts d'étude (`etude_panel`, `etude_panel_reduit`, `etude_cause_c`, `etude_melange`) vivent dans `src/`, à côté du moteur. Rien ne distingue au premier regard ce qui est chaîne de production de ce qui est matériau. | `find data -name "*.py" -not -path "*__pycache__*"` → 17 fichiers, 2 528 l. ; `src/etude_panel.py` 352 l., `src/etude_panel_reduit.py` 468 l., `src/etude_cause_c.py` 264 l., `src/etude_melange.py` 230 l. | Un repreneur ne sait pas ce qu'il peut supprimer. `.gitignore` traite déjà `data/etudes/*` par exceptions nominatives (`!data/etudes/sourcage_C/`), signe que la frontière a déjà coûté une fois. | faible | moyen |
| 9 | 3 | **Le build ne purge pas ce qu'il ne produit plus.** 5 pages de commune et 5 pages de département du 11 août survivent au build du 12 : départements 01, 15, 17, 22, 46, absents de `departements_publies.csv` et sans lien depuis `communes.html`. Le code connaît ce problème et ne l'a résolu que pour `donnees/`. | `site/build_site.py:1712-1715` (ménage limité à `verdicts*.csv`, avec le commentaire « sans ce ménage ils resteraient sur place, et seraient publiés ») ; `site/public/departement/{01,15,17,22,46}.html` datées 2026-08-11 ; `site/public/commune/17415.html` idem | `site/publier.py:324-384` synchronise sur ce qu'il trouve : les pages périmées sont donc mises en ligne et y restent, atteignables par un moteur de recherche, avec une version de référentiel obsolète. | faible | moyen |
| 10 | 1 | **`requirements.txt` ne décrit pas ce qui est importé.** Il déclare `duckdb>=1.0` et `requests>=2.31`. Le dépôt importe aussi `lxml` et `pypdf`. Aucune borne haute, aucune version de Python déclarée. | `src/raa_moisson.py:59` (`from lxml import html as lx`) et `:470` (`from pypdf import PdfReader`) ; `requirements.txt` (2 lignes) | Un clone frais + `pip install -r requirements.txt` puis `raa_moisson.py` s'arrête sur `ImportError`. Une montée de `duckdb` non bornée peut casser la base sans qu'un fichier du dépôt l'ait annoncé. | faible | moyen |
| 11 | 3 | **Contraste sous le seuil AA sur les pastilles de verdict.** Mesuré dans le navigateur sur `commune/81004.html` : 7 paires couleur/fond sous le minimum. « Verdict » 3,26:1, « Eau d'alimentation conforme… » 3,54:1, « Aucun dépassement à la date » 3,26:1 (AA exige 4,5:1 sous 18,66 px gras). L'anneau de focus `#7FD4DA` sur blanc mesure 1,70:1 (3:1 exigé). | mesures sur les 72 paires distinctes de la page ; `site/gabarits/observatoire.css:34` (`:focus-visible{outline:3px solid #7FD4DA}`) | Le verdict est l'objet même du site et il est porté par la couleur. Un lecteur presbyte ou sur écran en plein soleil lit mal ce qui compte le plus. | faible | moyen |
| 12 | 3 | **La fiche autonome pèse 25,4 Mo dont 99,8 % en un seul `<script>`, et elle est d'une autre génération que le site.** Produite le 11 août 15 h 25 ; le site l'a été le 12 août 16 h 17. C'est pourtant elle que `tests/test_sorties.py:58` contrôle. | `sortie/Resultat_Analyse_Standardise.html` : 25 384 806 octets, un script inline de 25 337 623 octets ; dates de modification comparées à `site/public/index.html` | L'objet « transmissible d'un bloc » est intransmissible en pratique et peut dire autre chose que le site. Le contrôle 4 valide un artefact périmé. | faible | faible |

---

## 5. Les trois chantiers à faire d'abord

### Chantier A — refermer la boucle publication → contrôle (constats 1 et 2)

**Premier geste :** ajouter au début de `site/publier.py:main()` un appel
`subprocess.run([sys.executable, "tests/test_sorties.py"])` et sortir en erreur
si le code de retour n'est pas 0. Une dizaine de lignes, aucune logique nouvelle
— le contrôle existe déjà et il sait déjà nommer les communes fautives.

Ce geste seul aurait empêché les 23 liens morts d'atteindre le lecteur. Le
correctif de `build_site.py:2100/2105` (décider quoi faire d'une commune
couverte sans ligne figée : page « non documentée », ou retrait de l'index)
vient ensuite, et c'est une décision de Yannick, pas de l'auditeur.

### Chantier B — rendre la page de commune lisible sans JavaScript (constat 3)

**Premier geste :** dans `site/build_site.py`, écrire en dur dans le HTML le
seul bloc de tête — commune, date du prélèvement, verdict des trois grilles,
`n notés sur m`, version de référentiel. Une dizaine de champs, tous déjà dans
`d0` à la ligne 2123. Le grand tableau de paramètres peut rester rendu par
`fiche.js` : c'est lui qui justifie le mécanisme, pas l'entête.

Mesure d'appui pour l'arbitrage : la page de département fait déjà tout le
contraire (0 octet de script inline, 67 055 caractères de texte) et pèse
341 860 octets. Le modèle existe donc dans le dépôt.

### Chantier C — une seule ligne de commande pour ajouter un département (constat 4)

**Premier geste :** créer `src/publier_departement.py` qui prend un code, refuse
de continuer si `moisson.py --termine` ne rend pas 0, ajoute la ligne dans
`referentiel/departements_publies.csv`, puis enchaîne `figer`, `build_site`,
`test_sorties`. Pas un nouveau moteur : un fichier qui écrit la séquence une
fois, à l'endroit où on la cherche — et qui rend l'étape invisible impossible à
oublier.

---

## 6. Ce qu'il ne faut pas toucher

Cette section est obligatoire, et elle n'est pas de la politesse : plusieurs des
choses ci-dessous ressemblent à des cibles d'optimisation et n'en sont pas.

1. **Les docstrings de module.** C'est le meilleur document du dépôt, et de
   loin. J'ai reconstitué la chaîne de production sans ouvrir un `.md`. Elles
   sont longues, elles racontent l'erreur qui a fait écrire la règle
   (`src/observer.py:22-26`, `src/build_db.py`, `referentiel/departements_publies.csv`),
   et c'est exactement pour cela qu'elles valent quelque chose. **Les raccourcir
   au nom de la concision détruirait le seul actif documentaire à jour.**

2. **Les 1 305 lignes de niveau module de `src/build_db.py`.** Sur 1 605 lignes,
   1 305 sont des constantes SQL — schéma et vues. Ce n'est pas du code trop
   long, c'est une déclaration. Découper ce fichier en modules le rendrait plus
   dur à lire, pas moins.

3. **Le partage des trois gabarits entre la vitrine et la fiche autonome.**
   `site/build_site.py:82`/`:1869` les sert, `sortie/build_fiche.py:876-878` les
   inline. Une seule source pour `observatoire.css`, `corps_fiche.html` et
   `fiche.js`. Vérifié, c'est vrai, et c'est le bon découpage — le constat 12
   porte sur le poids de la fiche, jamais sur ce partage.

4. **`src/moisson.py` sans `duckdb`.** La garantie est mécanique et elle est
   tenue. Ajouter la moindre lecture de base « juste pour l'état d'avancement »
   annulerait le découpage entier.

5. **Les deux suites `test_verdict.py` / `test_figer.py`.** Elles fabriquent
   leur base, ne touchent jamais `data/eau.duckdb`, passent en 21 s cumulées, et
   testent des règles de méthode formulées en français — pas des accesseurs. Ne
   pas les migrer vers `pytest` pour la forme : leur sortie lisible ligne à ligne
   est ce qui les rend relisables par un humain qui n'est pas développeur.

6. **Le traitement de la commune non documentée.** 166 communes `non_documentee`
   pointent vers `communes.html` en gris, avec leurs coordonnées conservées.
   C'est le cas vide correctement traité, et la section « arrêtés préfectoraux »
   d'une page de département fait la même chose : elle explique pourquoi elle est
   vide. Ne pas « simplifier » en masquant ces cas.

7. **`site/public/` hors de git.** `.gitignore` porte le raisonnement complet et
   la conclusion est bonne : l'historique de ce qui a été affiché vit dans les
   lignes figées, mieux placé. (Note de cohérence, sans conséquence :
   `site/build_site.py:15-16` affirme l'inverse — « git en garde l'historique ».
   C'est la docstring qui est en retard sur la décision, pas la décision.)

8. **La structure des fiches.** Sur 40 pages de commune tirées au sort, 2
   squelettes seulement, et la différence est fonctionnelle (13 ancres, plus
   `switch` sur les communes à plusieurs prélèvements). La cohérence de forme
   entre unités du même type : **rien à signaler.**

---

## 7. Annexe

### 7.1 Épreuves non menées, et pourquoi

- `tests/test_sorties.py` — **non lancée.** `tests/test_sorties.py:207` ouvre
  `data/eau.duckdb` ; la base est tenue en écriture exclusive par le refigeage
  en cours. Non concluante. Le constat 1 la concerne et a été établi
  indépendamment, sur les fichiers produits.
- Build du site, et `diff` de deux builds successifs — **non menés**, même
  motif. **Reproductibilité du rendu : non évaluée.**
- Mesure du goulot sur une unité réelle, épreuve du facteur 100 — **non menées**,
  même motif. Aucun chiffre n'est avancé à leur sujet.

### 7.2 Soupçons non mesurés, à éprouver quand la base sera libre

Écrits comme des soupçons. **Aucun chiffre, aucun ordre de grandeur** : ils
n'ont pas été mesurés.

- Goulot soupçonné à la construction du site : `site/build_site.py:2085` boucle
  sur toutes les communes et exécute au moins une requête par commune
  (`:2091` et `:2104`), soit un aller-retour DuckDB par unité. À mesurer contre
  une lecture unique par département.
- Second soupçon au même endroit : `site/build_site.py:2079` construit le
  dictionnaire complet des accroches avant la boucle, et `:2083`
  (`par_departement(lignes)`) matérialise le regroupement — à vérifier si l'un
  des deux est reconstruit par itération.
- Déterminisme du rendu : `site/build_site.py:2121` trie les prélèvements par
  `date_iso` seule. Un tri sans clé de départage est instable ; à éprouver sur
  une commune à plusieurs prélèvements le même jour — ce que
  `CLAUDE.md` §2.3 dit être fréquent.
- Reprise et idempotence de la collecte : non éprouvées, une campagne étant en
  cours. Lue seulement.

### 7.3 Hors périmètre — une ligne chacun, non développé

- Les 23 communes du 47 sans page portent `k: "vert"` dans l'index de recherche
  alors que `e`, `b`, `x` valent `null` : une couleur de conformité sur une
  entrée sans donnée. À arbitrer côté méthode, pas côté forme.
- `docs/CHANTIERS.md:96` désigne `docs/VITRINE.md` comme fichier de travail du
  chantier C9 ; le fichier n'existe pas sur disque.
- 10 fichiers suivis par git sont modifiés et non commités, dont
  `site/build_site.py`, `sortie/build_fiche.py`, `sortie/indicateurs.py`,
  `site/gabarits/observatoire.css` et `tests/test_figer.py`.
- 4 imports morts (`src/fetch_departement.py:67`, `src/hubeau.py:57`, et 2 sous
  `data/etudes/`) et 1 fonction publique jamais appelée
  (`src/hubeau.py:715`, 3 l.). **Code mort : rien à signaler**, c'est
  remarquablement propre pour 20 784 lignes.
- La date de calcul s'affiche au format ISO brut en pied de chaque page
  (« Calculé le : 2026-08-12 »), là où toutes les autres dates du site sont en
  français.

---

*Rapport produit le 13 août 2026. Aucun fichier du dépôt modifié hors
celui-ci ; aucun processus arrêté ; aucun appel Hub'Eau émis.*

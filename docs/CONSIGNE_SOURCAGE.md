# Consigne de sourçage réglementaire — brief type pour un agent de fond

Version du 11 août 2026. **Fichier versionné : ce qu'on demande à un agent est
une décision de méthode, git en tient le journal daté.**

Écrite après six dossiers rendus les 10 et 11 août (toluène, trichloroéthane-1,1,1,
PFAS, acides haloacétiques, biphényle, dichloroéthane-1,1, dichloroéthylènes-1,2).
Chaque règle ci-dessous vient d'une erreur réellement commise ou évitée de
justesse — les cas sont cités, ils valent mieux qu'un principe.

---

## 0. Règles d'emploi, avant d'écrire le brief

- **Un agent à la fois, et seulement quand Yannick le demande.** Décision du
  11 août 2026, après qu'un lot de cinq agents lancés en parallèle a consommé une
  part importante d'une fenêtre de quota. Coût mesuré : **~140 000 tokens par
  substance** en `opus`.
- **`opus` obligatoire.** On touche à des seuils, des dates d'applicabilité, des
  unités et des sources : §1 du mode opératoire.
- **Interdire explicitement à l'agent de lancer ses propres sous-agents.** Le
  11 août, cinq agents en ont lancé une douzaine ; les tuer n'a pas tué les
  enfants, qui ont continué à consommer. Sans cette clause, la dépense est
  imprévisible.
- **Un fichier de sortie par agent, nommé dans le brief.** Jamais deux agents sur
  le même fichier.

---

## 1. Le squelette du brief

### La substance

Libellé, **code SANDRE**, **numéro CAS**, unité, et les comptes du corpus :
nombre de mesures, de communes, de **quantifications**, valeur maximale relevée.
Les quantifications sont ce qui compte — une substance jamais quantifiée est le
cas le moins intéressant du dossier.

### La question, en deux issues à trancher explicitement

- **C1** — une valeur existe et le projet ne l'a pas identifiée → la donner,
  entièrement sourcée, prête à verser.
- **C2** — aucune valeur réglementaire en EDCH → **le démontrer** : dire quels
  textes ont été consultés et ce qu'ils contiennent ou non ; puis chercher une
  valeur guide non opposable (OMS, Anses, VTR) pouvant servir de repère documenté.

**Ajouter systématiquement une troisième issue depuis le biphényle** :

- **C-g** — la substance n'est nommée nulle part **mais une règle de catégorie
  s'applique**. Le biphényle n'apparaît dans aucun texte et reçoit pourtant
  0,10 µg/L au titre des « pesticides, par substance individuelle », l'annexe
  définissant les pesticides comme incluant les fongicides organiques. Notre
  moteur le captait déjà. **Avant de conclure C2, faire vérifier
  `v_regle_famille_appliquee`.**

### Le piège d'identité, nommé

Toujours lister les substances voisines à ne pas confondre, avec leur CAS.
Cas réels :

- le **dichloroéthane-1,2** (107-06-2) porte 3,0 µg/L, le **1,1** (75-34-3) rien ;
- le **biphényle** (92-52-4) n'est ni un PCB ni le bisphénol A ;
- une fiche INERIS attribuait un CAS au mauvais isomère de dichloroéthylène.

---

## 2. Les règles absolues à recopier dans chaque brief

1. **N'écris jamais une valeur que tu n'as pas lue** dans une source que tu as
   ouverte toi-même. Pas de tableau comparatif secondaire, pas de mémoire, pas de
   « c'est probablement ». Sans source primaire : `a_verifier`, et le dire.
   *Cas :* un agent a lu « Allemagne 10 µg/L » dans un résumé INERIS ; la seconde
   lecture, littérale, ne l'a pas retrouvée et la TrinkwV n'a pas ce paramètre.
   Valeur écartée. Elle serait entrée marquée `verifie`.
2. **La source doit couvrir CETTE substance**, identifiée par son CAS. Une source
   sur la substance d'à côté n'est pas une source.
   *Cas :* un avis Anses remonté par la recherche portait sur le 1,4-dioxane ; un
   autre sur les isomères du dinitrotoluène.
3. **Un seuil sans sa date d'applicabilité est faux.** Immédiat ou différé.
   *Cas :* plomb 10 aujourd'hui, 5 au 01/01/2036 ; chrome total 50 puis 25.
4. **Vérifie l'unité, et ne convertis pas.** Facteur 1000 entre mg/L, µg/L, ng/L.
   Facteur ~4,43 entre NO3 et NO3-N. µg/L et Bq/L ne sont pas convertibles.
   Reporter l'unité exacte du texte.
5. **« Je n'ai pas trouvé » ≠ « il n'existe pas ».** Le second n'est permis que si
   les textes de référence ont été consultés et sont nommés.
6. **Trois registres jamais fusionnés** : réglementaire opposable / valeur guide
   non opposable / littérature scientifique. Plus, pour certains composés, un
   quatrième axe : **sanitaire contre acceptabilité** (odeur, goût).
7. **Un faux positif coûte plus cher qu'un faux négatif.** Dans le doute,
   `a_verifier`.

---

## 3. Les périmètres de sommes — la section qui a le plus servi

**Une substance peut n'avoir aucune valeur propre tout en entrant dans une somme
opposable.** Et l'inverse est vrai : la ressemblance chimique ne fait pas entrer
dans une somme.

Périmètres établis en source primaire, à donner d'entrée à tout nouvel agent :

| somme | périmètre |
|---|---|
| Trihalométhanes | **4** substances nommées : chloroforme, bromoforme, dibromochlorométhane, bromodichlorométhane |
| HAP | **4** substances (une somme « 6 substances » existe dans les données, sans limite déclarée) |
| Acides haloacétiques | **5** : monochloro-, dichloro-, trichloro-, bromo-, dibromoacétique (SANDRE 9064) |
| PFAS | **20** (annexe III B.3 de la directive) |
| Tétrachloroéthylène + trichloroéthylène | **2** substances nommées, deux éthylènes |
| Pesticides | somme des pesticides individuels quantifiés |

**Le mot qui ferme un périmètre.** La directive écrit « the sum of concentrations
of **these two** parameters », « the following **five** substances ». Chercher
cette formulation plutôt que de raisonner par famille.

**Trois cas d'école à citer dans les briefs :**

- le **trichlorofluorométhane** *est* chimiquement un trihalométhane, et n'entre
  pas dans le total des THM, qui nomme quatre composés ;
- le **trichloroéthane-1,1,1** n'entre pas dans « tétrachloroéthylène +
  trichloroéthylène » : ce sont deux éthylènes, c'est un éthane ;
- les **dichloroéthylènes-1,2** non plus, alors qu'ils sont les produits de
  dégradation des deux substances de cette somme. Enjeu chiffré : le maximum du
  *cis* est à 7,6 µg/L pour une limite de somme à 10 — une agrégation erronée
  aurait fabriqué des dépassements inexistants.

**Le piège de l'agrégat SANDRE.** Le SANDRE porte des agrégats de nomenclature —
`[7485] « Somme de COHV »`, `[2925] xylènes méta+para`, `[1780]` — qui ressemblent
à des sommes réglementaires **et n'en sont pas**. Seul le texte fait foi.
Réciproquement, la fiche SANDRE d'une somme **désigne ses composants par code**
(9064 → `[1465] [1481] [1546] [5427] [5426]`), ce qui permet un appariement sans
pari — là où le rapprochement par ressemblance de libellé avait donné, le 9 août,
**32 candidats faux sur 37**.

---

## 4. Les sources, et l'ordre dans lequel les lire

**Le fonds local d'abord**, avec l'outil `Read` (les PDF s'ouvrent via `pages`) :

`C:\Users\ymyta\Documents\EDITIONS MYTAE\2 - Water\Data - Analyse de la qualité de l'eau en France\Sources\`

| fichier | ce qu'on y prend |
|---|---|
| `REG_.../REG-01_UE_directive-2020-2184.pdf` | **s'extrait intégralement**, annexes I A/B/C/D et III comprises. La source-mère. |
| `REG_.../REG-03_FR_arrete-2022-12-30_grille-2026.pdf` | grille française actuelle |
| `REG_.../REG-02_FR_arrete-2007-01-11_grille-2016.pdf` | ⚠️ **rédaction d'ORIGINE de 2007** — les annexes I et II ont été réécrites en bloc au 01/01/2023. Utile pour la grille « 2016 », **jamais** pour la norme en vigueur. |
| `REG_.../REG-04_OMS_directives-qualite-eau-4e-ed.pdf` | valeurs guides **non opposables**, et surtout la **table A3.2** des substances pour lesquelles l'OMS a explicitement renoncé, **avec le motif** |
| `PFAS_.../PFAS-05, PFAS-06, PFAS-07` | Danemark, Allemagne, EFSA |
| `PE_.../PE-04, PE-06, PE-08` | PE réglementaire (ECHA) contre listes de PE potentiels (TEDX, ChemSec) — ne jamais confondre |

**Puis le réseau**, et seulement WebSearch / WebFetch — ni curl, ni wget, ni
python pour télécharger une URL (§3.1).

**État des accès au 11 août 2026 :**

- **Légifrance répond** par l'outil web du harnais : arrêté du 11 janvier 2007
  **consolidé**, annexes I et II, identifiant `LEGIARTI000046890189`. C'est le
  shell et le navigateur qui recevaient un 403, pas cette voie-là.
- **EUR-Lex tronque la directive avant ses annexes** sur toutes les formes d'URL
  essayées. Ne pas y perdre de temps : le PDF local suffit.
- **`ecfr.gov` bloque ses pages web mais son API de rendu répond** :
  `https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-40?chapter=I&subchapter=D&part=141&section=141.62`
- **`pdftotext -layout` sur REG-03 décale les colonnes.** Cas constaté : la ligne
  « tétrachloroéthylène et trichloroéthylène » affiche « NFU » là où l'unité
  réelle est µg/L. **Ne jamais lire une valeur chiffrée sur cette extraction sans
  recoupement.**
- Les pages du CIRC sont servies en JavaScript et souvent illisibles : laisser le
  champ **vide** plutôt que de recopier le classement d'une substance voisine.

---

## 5. Le balayage international — variante du brief

Quand la question n'est pas « existe-t-il une valeur ? » mais « quelqu'un est-il
plus strict que nous ? », deux livrables **d'égale importance** :

1. les valeurs trouvées, pays par pays ;
2. **la liste des juridictions effectivement consultées**, y compris celles sans
   résultat et celles inaccessibles. Sans elle, « personne n'est plus strict » n'a
   aucune valeur.

**Liste standard, identique pour toutes les substances** — sinon les résultats ne
se comparent pas entre eux : UE · France · Allemagne · Danemark · Suède ·
Pays-Bas · Suisse · Royaume-Uni · Norvège · États-Unis fédéral · Californie ·
Canada · Australie/NZ · Japon · OMS.

**La distinction qui commande tout**, pour chaque valeur :

- **opposable** — un dépassement est une non-conformité ;
- **objectif ou valeur guide** — sourcé, aucun effet juridique ;
- **niveau d'action / technique de traitement** — déclenche une obligation d'agir
  sans être un seuil de conformité.

*Cas d'école, le plomb :* la Californie affiche un « Public Health Goal » à
0,2 µg/L qui **n'est pas une limite** — elle n'a pas de limite pour le plomb, mais
une technique de traitement et un niveau d'action à 15 µg/L. Confondre les deux
fabriquerait un écart de 1 à 50 qui n'existe pas.

**Seules les valeurs opposables entrent dans la comparaison.** Les autres
alimentent le bloc « recommandé, sourcé, non repris ».

Formulation à tenir dans toute sortie : **« le plus strict identifié parmi les
juridictions suivantes »**, jamais « le plus strict au monde » (§2.14).

---

## 6. Ce que l'agent doit rendre

**Un fichier, écrit tôt et complété au fil du travail** — une tâche a été perdue
dans la nuit du 10 au 11 août sans rien laisser sur le disque. Le dire dans le
brief.

Structure :

1. **le verdict en une phrase**, en tête ;
2. les valeurs trouvées en tableau : valeur, unité, nature, texte, date du texte,
   **date d'applicabilité**, `verifie` / `a_verifier` ;
3. l'appartenance ou non à chacune des sommes connues, une par une ;
4. si C2 : **pourquoi la substance est-elle mesurée** alors que rien ne la juge ?
   (liste de surveillance, paquet analytique multi-résidus, programme régional) —
   sourcé. *Réponses réelles obtenues : « balayage chromatographique COHV rendu
   pour les composés réglementés », « produits de dégradation dont les maillons
   voisins sont réglementés » ;*
5. la **ligne de référentiel prête à verser** le cas échéant. Format : séparateur
   de colonnes `;`, séparateur de sources multiples **barre verticale**
   (`REG-01|REG-03`), **jamais de point-virgule dans une cellule** — l'erreur a
   décalé quatorze lignes puis quatre autres sans que rien ne la signale (§5).
   `statut_2026` commence par un mot du vocabulaire contrôlé : `limite`,
   `reference`, `vigilance`, `dans somme`. `seuil_strict` **laissée vide à dessein**
   si aucun balayage international n'a été fait, en le disant ;
6. **table des sources** : organisme, titre exact, date, URL ou chemin local, et
   si elle a été lue en entier, partiellement, ou pas du tout ;
7. **ce qui n'a pas pu être établi** — section obligatoire, à ne pas vider par
   complaisance.

**Réponse finale retournée : 12 à 16 lignes maximum**, pas de recopie du fichier.

---

## 7. La posture, à recopier telle quelle

> Le projet interroge **la norme**, jamais les acteurs — ni ARS, ni distributeur,
> ni maire, ni agriculteur, ni exploitant. Aucune recommandation de produit,
> d'équipement, de filtration ou de conduite individuelle, nulle part, pas même en
> note. Aucun qualificatif sanitaire de ton cru : tu rapportes ce que les sources
> disent, avec le niveau de preuve qu'elles revendiquent. **Une substance sans
> seuil n'est pas « sans danger » : elle est indéterminée.**

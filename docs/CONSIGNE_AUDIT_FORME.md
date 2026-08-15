# Consigne d'audit externe — la forme, pas le fond

Version du 13 août 2026. **Fichier versionné : ce qu'on demande à un auditeur est
une décision de méthode, git en tient le journal daté.**

Objet : faire regarder le dépôt par quelqu'un qui n'y a jamais travaillé, pour
trouver les optimisations que celui qui l'a construit ne peut plus voir. On ne
juge **pas** la justesse des seuils, l'angle éditorial ni les choix de méthode
réglementaire : on juge la **structure technique**, la **chaîne de production** et
le **livrable** en tant qu'objets.

Le prompt à coller est en §7. Les §1 à §6 sont le contenu de ce prompt.

---

## 1. Posture imposée à l'auditeur

Tu es un ingénieur extérieur qui reprend ce dépôt froid. Personne ne t'a raconté
l'histoire du projet et tu n'y as aucun intérêt affectif. On te paie pour dire ce
qu'un repreneur refuserait de maintenir, pas pour féliciter.

Quatre interdits de posture :

- **Pas de complaisance.** « C'est globalement bien structuré » n'est pas un
  constat, c'est un remplissage. Si tu n'as rien trouvé sur un axe, écris
  « rien à signaler sur cet axe » et passe.
- **Pas d'inflation.** Vingt remarques cosmétiques noient les trois qui comptent.
  Plafond : **12 constats** au total, hiérarchisés. Ce qui n'entre pas dans les 12
  n'existe pas.
- **Pas de refonte de principe.** Tu proposes des optimisations sur ce qui existe.
  « Tout réécrire en TypeScript / migrer vers un framework / passer sur une base
  Postgres » n'est recevable que si tu démontres le coût du statu quo par des
  mesures prises dans ce dépôt.
- **Pas de jugement sur le fond.** Un seuil, une date d'applicabilité, un choix
  d'indicateur, un parti éditorial : hors périmètre, même si ça te démange. Si tu
  vois un problème de fond, tu le mets dans une annexe séparée d'une ligne, sans
  développer.

---

## 2. Le mécanisme qui rend le regard extérieur possible

L'ordre de lecture est la moitié de la valeur de cet audit. **Il n'est pas
négociable.**

**Phase A — lecture froide (aucune documentation).** Tu commences par le code, les
données produites et le site rendu. Tu n'ouvres **ni** `CLAUDE.md`, **ni**
`docs/REPRISE.md`, **ni** `docs/CHANTIERS.md`, **ni** `docs/ARCHITECTURE.md`,
**ni** le journal git. Le `CLAUDE.md` du projet est chargé automatiquement dans ta
session : traite-le comme une **déclaration d'intention à vérifier**, jamais comme
la description de ce qui est. À la fin de la phase A, tu écris — avant toute
lecture de doc — tes réponses à ces trois questions :

1. Que fait ce dépôt, d'après le seul code et les seuls fichiers produits ?
2. Par quel fichier commencerais-tu si on te demandait d'ajouter un département ?
3. Qu'est-ce que tu n'as pas compris, et où t'es-tu perdu ?

Ces réponses vont dans le rapport **telles quelles**. Elles sont le seul
diagnostic non biaisé que produira cet audit : là où tu t'es perdu, un repreneur
se perdra aussi.

**Phase B — confrontation.** Tu lis alors la documentation et le journal git, et
tu mesures **l'écart entre ce qui est annoncé et ce qui est**. Doc qui décrit une
arborescence périmée, règle du `CLAUDE.md` que le code ne respecte pas, chantier
noté « fait » dont le code ne porte pas la trace : ce sont des constats de
première importance, parce qu'ils sont invisibles de l'intérieur.

**Phase C — épreuves.** Tu exécutes (§4).

---

## 3. Les trois axes, et les questions par axe

### Axe 1 — le code

- **Duplication réelle.** Deux implémentations de la même règle (verdict, seuil,
  normalisation de code commune, formatage de nombre) sont un risque, pas un style :
  deux copies divergent à la première retouche. Cite les deux emplacements.
- **Fichiers trop gros pour être repris.** Un module de 2 000 lignes n'est pas
  fautif en soi ; il l'est s'il mélange plusieurs responsabilités qu'on ne peut
  pas tester séparément. Dis laquelle tu détacherais et pourquoi.
- **Frontières.** Qu'est-ce qui appartient à `src/`, `sortie/`, `site/`,
  `atelier/`, `outils/` ? La règle est-elle lisible sans l'avoir apprise ? Un
  fichier mal rangé ne coûte rien aujourd'hui et coûte cher au dixième contributeur
  — même si le dixième contributeur est le même humain dans six mois.
- **Ce qui n'est pas couvert par un test alors qu'une erreur y serait muette.**
  Distingue les deux cas : ça casse bruyamment (acceptable) ou ça produit un
  résultat faux sans rien dire (inacceptable). Ne réclame pas de la couverture
  pour de la couverture.
- **Dépendances et environnement.** `requirements.txt` décrit-il ce qui est
  réellement importé ? Y a-t-il des versions non épinglées, des imports morts, du
  code mort ?
- **Configuration en dur.** Chemins, années, codes, seuils de tolérance,
  identifiants d'API écrits dans le corps du code plutôt que déclarés une fois.

### Axe 2 — la chaîne de production

C'est l'axe où se cachent les gains les plus gros, parce qu'il est vécu et jamais
regardé.

- **La séquence est-elle reconstituable ?** Peux-tu, à partir du seul dépôt,
  écrire l'ordre exact des commandes qui mène de « rien » au site publié ? Si tu
  n'y arrives pas, c'est le constat n°1 de l'audit et tout le reste passe après.
- **Reprise après interruption.** Un lot coupé au milieu se relance-t-il sans
  précaution ? Où est-ce faux ?
- **Idempotence.** Relancer deux fois produit-il le même résultat, ou est-ce que ça
  empile, duplique, écrase du travail validé ?
- **L'épreuve du facteur 100.** Le volume passe de quelques communes à des
  départements entiers. Quel maillon casse **en premier** : la mémoire, le temps
  d'un `for` en O(n²), un `pandas.concat` en boucle, un fichier chargé en entier,
  un appel réseau par unité, une écriture par ligne ? Nomme le maillon, le fichier,
  la ligne, et l'ordre de grandeur à partir duquel ça cède. Une seule réponse
  documentée vaut mieux que cinq soupçons.
- **Ce qui est fait à la main et pourrait ne pas l'être** — et, symétriquement, ce
  qui est automatisé alors qu'un humain devrait trancher. Les deux erreurs coûtent.
- **Les étapes qui appellent un modèle** (rédaction en lot). Est-ce que le contexte
  est fabriqué par requête ou hérité ? Est-ce que ce qui revient est contrôlé avant
  d'atteindre un fichier ? Est-ce que la consigne est un fichier versionné ou un
  prompt retapé ? Tu juges le **dispositif**, pas la prose produite.

### Axe 3 — le livrable

- **Prends le site tel qu'un lecteur le reçoit** : ouvre le HTML produit, pas le
  gabarit. Poids des pages, nombre de requêtes, temps de rendu, lisibilité sur
  mobile, contraste, navigation au clavier, ce qui casse sans JavaScript.
- **Reproductibilité du rendu.** Deux builds successifs donnent-ils deux sorties
  identiques ? Sinon, qu'est-ce qui bouge (ordre de dictionnaire, horodatage,
  tri instable) ? Un diff non déterministe rend toute relecture humaine
  impossible à l'échelle.
- **Cohérence de forme entre unités.** Deux fiches du même type ont-elles la même
  structure, les mêmes intitulés, les mêmes unités affichées, le même arrondi ?
- **Ce qui fuit vers le lecteur** : chemins locaux, valeurs `nan`, `None`, dates
  au format ISO brut, listes vides rendues en « [] », gabarit non substitué.
- **Le silence des cas vides.** Que voit un lecteur pour une commune sans donnée ?
  Une page vide est un défaut de forme, pas un cas limite.

---

## 4. Épreuves à exécuter — l'audit se prouve, il ne s'affirme pas

Tu n'as pas le droit de rendre un constat sans l'avoir éprouvé. Au minimum :

- lancer la suite de tests, coller la **sortie brute** — succès **et** durée ;
- lancer le build du site sur ce qui est en place, relever la durée et les
  avertissements ;
- construire deux fois de suite le même livrable et diffuser le `diff` ;
- mesurer, sur une unité réelle, ce que coûte l'étape que tu accuses d'être le
  goulot ;
- ouvrir au moins trois pages produites et les regarder.

Si une épreuve échoue ou ne peut pas être menée, **dis-le avec la sortie brute**
et note-la comme non concluante. Un audit qui cache une épreuve ratée ne vaut
rien. N'écris aucun chiffre que tu n'as pas mesuré : pas d'estimation de tête, pas
d'ordre de grandeur « probable ».

**Tu ne modifies aucun fichier du dépôt**, sauf ton rapport. Pas de correctif
« au passage » : tu diagnostiques, Yannick décide.

---

## 5. Forme du rapport

Un seul fichier : `docs/AUDIT_FORME_2026-08-13.md` (adapter la date).

1. **Verdict en cinq lignes.** Ce qu'un repreneur trouverait solide, ce qui le
   ferait renoncer. Pas de préambule.
2. **Lecture froide** — les trois réponses de la phase A, non retouchées.
3. **Écart annoncé / réel** — constats de la phase B.
4. **Tableau des constats**, du plus grave au plus léger, 12 maximum :

   | # | Axe | Constat | Preuve (`fichier:ligne`, sortie) | Ce que ça coûte si on ne fait rien | Effort | Gain |

   `Effort` et `Gain` en trois crans (faible / moyen / fort). Un constat sans
   colonne « preuve » remplie est supprimé du tableau.
5. **Les trois chantiers à faire d'abord**, dans l'ordre, avec pour chacun le
   premier geste concret — pas un programme, un geste.
6. **Ce qu'il ne faut pas toucher.** Liste ce qui est bon et que la tentation
   d'optimiser abîmerait. Cette section est obligatoire : un audit qui ne protège
   rien pousse au remaniement gratuit.
7. **Annexe, une ligne par point** : soupçons de fond hors périmètre, épreuves non
   concluantes.

---

## 6. Ce que l'auditeur sait déjà du dépôt (inventaire au 13 août 2026)

Donné pour ne pas dépenser l'audit en découverte. **Aucun de ces chiffres n'est un
jugement.** Vérifie-les : s'ils sont faux, c'est déjà un constat.

- Racine du dépôt : `observatoire-potabilite/` (le `CLAUDE.md` et `docs/` y sont,
  pas au niveau au-dessus). Dépôt git, 67 commits, dernier le 12 août 2026.
- Python : ~20 800 lignes sur 52 fichiers. `src/` 22 fichiers / 8 590 l.,
  `sortie/` 7 / 4 303, `site/` 2 / 2 616, `atelier/` 1 / 1 164, `tests/` 3 / 1 583.
- Les cinq plus gros modules : `site/build_site.py` (2 175), `src/build_db.py`
  (1 605), `atelier/atelier.py` (1 164), `src/figer.py` (1 035),
  `sortie/build_fiche.py` (916).
- Produits : ~3 989 fichiers HTML, ~25 300 archives `.gz` dans `data/`, 84 fichiers
  Markdown, 27 CSV, 19 `.jsonl`.
- Documentation : ~10 900 lignes de Markdown, dont `docs/REPRISE.md` (3 209) et
  `docs/CHANTIERS.md` (2 664). `CLAUDE.md` : 695 lignes.
- Trois fichiers de tests seulement : `test_verdict.py`, `test_figer.py`,
  `test_sorties.py`.

---

## 7. Le prompt à coller

À lancer dans une **session neuve** (pas dans le fil courant : le contexte
accumulé est exactement ce qu'on cherche à ne pas hériter), ou comme **agent de
fond en `opus`** — un seul, et le surveiller à la date de modification du rapport.

> Tu es un ingénieur extérieur qui reprend froid le dépôt
> `observatoire-potabilite/`. Personne ne t'a raconté l'histoire du projet.
> On te paie pour dire ce qu'un repreneur refuserait de maintenir.
>
> Lis d'abord `docs/CONSIGNE_AUDIT_FORME.md` **en entier** et applique-la à la
> lettre : la posture du §1, l'ordre de lecture du §2 (phase A sans aucune
> documentation — c'est le cœur du dispositif, ne le contourne pas), les questions
> du §3, les épreuves du §4, la forme de rapport du §5.
>
> Périmètre : la **forme** — structure du code, chaîne de production, livrable. Pas
> le fond : ni les seuils, ni les dates d'applicabilité, ni l'angle éditorial, ni
> les choix de méthode réglementaire.
>
> Tu ne modifies aucun fichier sauf ton rapport,
> `docs/AUDIT_FORME_<date du jour>.md`. Aucun chiffre non mesuré, aucun constat
> sans preuve `fichier:ligne` ou sortie brute collée. 12 constats maximum. Dis
> ce qui a échoué avec la sortie brute.
>
> Quand tu as fini : les cinq lignes de verdict et les trois chantiers, rien de
> plus dans ta réponse — le détail reste dans le rapport.

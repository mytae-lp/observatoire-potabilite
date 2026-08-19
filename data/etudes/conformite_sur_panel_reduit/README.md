# Conformité sur panel réduit

**Ce que ce dossier instruit :** une eau peut être déclarée **conforme** sur un
panel d'analyse qui **ne contient plus** les paramètres qui l'avaient rendue
**non conforme** lors de la dernière analyse complète.

La conformité affichée ne dit alors rien de l'eau. Elle dit ce qu'on a regardé.

---

## Le mécanisme, en trois temps

1. une **analyse complète** — plus de 200 paramètres — trouve un ou plusieurs
   dépassements, et l'administration prononce une non-conformité ;
2. les analyses suivantes sont des **contrôles de routine**, vingt à quarante
   paramètres, tels que la réglementation les prescrit entre deux analyses
   complètes ;
3. ces contrôles ne portent plus les paramètres en cause. Ils concluent
   « conforme aux exigences de qualité en vigueur **pour l'ensemble des
   paramètres mesurés** » — clause exacte, et que personne ne lit.

## Ce que ce dossier peut établir, et ce qu'il ne peut pas

**Peut établir**, par la donnée seule : quels paramètres étaient en dépassement
à la dernière analyse complète, lesquels ont été recherchés depuis, lesquels ne
l'ont plus jamais été, et depuis combien de mois.

**Ne peut pas établir, et ne l'écrira jamais :**

- **que l'eau serait aujourd'hui non conforme.** Personne ne le sait — c'est le
  point. Un pesticide peut avoir été traité, dilué, ou avoir disparu de la
  ressource. L'absence de mesure ne dit rien sur la présence : c'est le §2.4 de
  `CLAUDE.md` appliqué à l'échelle du panel ;
- **une intention.** La composition d'un contrôle réduit vient de la
  réglementation et des marchés pluriannuels des ARS, pas d'un arbitrage au cas
  par cas. Écrire « on a cessé de mesurer pour ne plus voir » serait une
  accusation que la donnée ne porte pas. Le projet interroge la norme, jamais
  les acteurs (§2.1) ;
- **un reproche de surveillance insuffisante.** Une eau peut être analysée huit
  fois en deux ans sans qu'aucune de ces analyses soit complète. Le dire est
  nécessaire, sinon l'alerte laisse croire à un abandon qui n'existe pas.

## Qui décide de ce qui est analysé — le maillon à instruire

**Ce n'est pas l'exploitant, et ce n'est pas décidé commune par commune.** La
liste des paramètres recherchés lors d'un contrôle sanitaire est **régionale**,
et elle est **figée par les marchés pluriannuels d'analyses passés par les
ARS** : le laboratoire retenu applique, pour la durée du marché, le catalogue
qui y est annexé.

C'est le mécanisme décrit par l'instruction **DGS/EA4/2020/177** (source
`REG-05` du dépôt), déjà invoquée dans le projet pour la rupture de panel du
Tarn — avec la précaution qui s'impose : elle **décrit** ce mécanisme, elle ne
prouve aucun cas particulier, et elle est postérieure à la rupture qu'on lui
attribuait.

**Ce que ça implique pour ce dossier.** Les arrêts de mesure observés se
groupent en 2018, 2020, 2023 **et 2024** — deux à trois ans d'écart, la
signature d'un cycle et non d'un arbitrage local. **Un exploitant n'a pas la
main sur ce qu'on mesure chez lui.** Chercher la responsabilité du côté de la
commune ou du distributeur serait donc doublement faux : contraire au §2.1, et
contraire au mécanisme.

*La vague de 2024 est apparue avec l'élargissement du corpus, le 19 août 2026,
et elle est portée pour l'essentiel par l'Aisne.*

**Chantier ouvert, et il est documentaire, pas informatique** : retrouver les
marchés d'analyses de l'ARS Centre-Val de Loire **et de l'ARS Hauts-de-France**
— date de notification, durée, liste de paramètres annexée. Ces pièces sont
publiques. Elles transformeraient « compatible avec un renouvellement de
marché » en fait établi, ou l'infirmeraient. Tant qu'on ne les a pas, la
formulation reste **« arrêts groupés en 2018, 2020, 2023 et 2024, compatibles
avec des renouvellements de marché »**, jamais « causés par ».

## Le critère de sélection

Une commune entre dans ce dossier si :

- sa **dernière analyse complète** date de **plus de 24 mois** ;
- **et** cette analyse portait au moins un dépassement.

**L'unité est le `code_prelevement`, jamais la date** (CLAUDE.md §2.3). Une
commune a souvent plusieurs prélèvements le même jour sur des points d'eau
différents ; désigner le bulletin de référence par sa date faisait relire le
contrôle de routine au lieu de l'analyse complète. Corrigé le 19 août 2026 —
détail et effet chiffré dans `ANALYSE_2026-08-19.md` §0.

**Un résultat sans son périmètre est une demi-vérité** (§2.8). Chaque synthèse
est donc accompagnée d'un `.meta.json` qui fige, à la date de l'étude, les
départements réellement **figés** — et non ceux que le dépôt déclare collectés,
les deux ayant divergé de douze départements au 19 août 2026.

## L'alerte que ces cas justifient

> **Aucune analyse complète (plus de 200 paramètres) depuis X mois.**

Accompagnée de deux compléments sans lesquels elle se lit de travers : le
**nombre d'analyses de contrôle** intervenues depuis, qui montre que l'eau est
suivie ; et le **nom des paramètres** qui étaient en dépassement et qui n'ont
plus été mesurés, qui est l'information réellement neuve.

## Où en est le dossier

| | 12 août 2026 | **19 août 2026** |
|---|---:|---:|
| départements figés balayés | 11 | **30** |
| communes à bulletin complet au corpus | — | 4 261 |
| candidates au critère | 39 | **242** |
| instruites | 37 | **242** |
| **communes portant un paramètre abandonné** | 18 | **45** |
| dont un paramètre jamais recontrôlé | — | 21 |
| paramètres abandonnés | 49 | **93** |
| contrôles de routine cumulés depuis | 555 | **1 136** |

Aucune des 18 communes du 12 août n'est sortie du critère : aucune n'a reçu
d'analyse complète depuis.

**Les analyses d'ensemble, la plus récente fait foi :**

- `ANALYSE_2026-08-19.md` — 30 départements. Porte en §0 la correction de
  méthode qui rend les deux séries non comparables terme à terme ;
- `ANALYSE_2026-08-12.md` — 11 départements, conservée telle quelle.

**Les cas instruits à la main**, seuls textes du dossier qui ne sont pas
générés :

| commune | dernière analyse complète | ancienneté | fichier |
|---|---|---:|---|
| Thiville (28389) | 20/09/2023, 256 paramètres | 35 mois | `thiville-28389_2026-08-12.md` |

**Les cas instruits par le balayage** portent le préfixe `auto_` et sont
refabriqués à chaque passage — `auto_<commune>-<insee>_<date>.md`. Ce préfixe
n'est pas cosmétique : le 12 août 2026, une relance a écrasé l'étude rédigée à
la main sur Thiville, six kilo-octets de rédaction remplacés par un tableau
généré. **Un script ne doit jamais pouvoir détruire ce qu'une main a écrit.**

*Piège voisin, non corrigé : le nom de la synthèse ne dépend que de la date, et
une relance ciblée `--insee` écrase donc la synthèse complète du même jour.
Relancer `--tous` — le cache rend l'opération gratuite.*

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
groupent en 2018, 2020 et 2023 — deux à trois ans d'écart, la signature d'un
cycle et non d'un arbitrage local. **Un exploitant n'a pas la main sur ce qu'on
mesure chez lui.** Chercher la responsabilité du côté de la commune ou du
distributeur serait donc doublement faux : contraire au §2.1, et contraire au
mécanisme.

**Chantier ouvert, et il est documentaire, pas informatique** : retrouver les
marchés d'analyses de l'ARS Centre-Val de Loire — date de notification, durée,
liste de paramètres annexée. Ces pièces sont publiques. Elles transformeraient
« compatible avec un renouvellement de marché » en fait établi, ou
l'infirmeraient. Tant qu'on ne les a pas, la formulation reste **« arrêts
groupés en 2018, 2020 et 2023, compatibles avec des renouvellements de
marché »**, jamais « causés par ».

## Le critère de sélection

Une commune entre dans ce dossier si :

- sa **dernière analyse complète** date de **plus de 24 mois** ;
- **et** cette analyse portait au moins un dépassement.

## L'alerte que ces cas justifient

> **Aucune analyse complète (plus de 200 paramètres) depuis X mois.**

Accompagnée de deux compléments sans lesquels elle se lit de travers : le
**nombre d'analyses de contrôle** intervenues depuis, qui montre que l'eau est
suivie ; et le **nom des paramètres** qui étaient en dépassement et qui n'ont
plus été mesurés, qui est l'information réellement neuve.

## Les cas instruits

| commune | dernière analyse complète | ancienneté | fichier |
|---|---|---:|---|
| Thiville (28389) | 20/09/2023, 256 paramètres | 35 mois | `thiville-28389_2026-08-12.md` |

*Premier cas, instruit à la main le 12 août 2026. Le balayage systématique est
outillé par `src/etude_panel_reduit.py`.*

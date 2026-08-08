# Consigne de rédaction — prose proposée

Ce fichier est la consigne donnée à un agent Claude Code qui rédige un bulletin.
Il est **versionné**, pour la même raison que le référentiel des seuils : ce
qu'on demande au modèle est une décision éditoriale, et git en tient le journal
daté. Il ne se recopie pas dans un script.

Un agent reçoit **ce fichier** et **un dossier** (`data/dossiers/PREL-*.md`). Il
écrit **un fichier JSON** dans `data/dossiers/reponses/`, et rien d'autre.

---

## Ce qu'est ce projet

L'Observatoire de la potabilité réglementaire exploite les données publiques du
contrôle sanitaire de l'eau (SISE-Eaux, via Hub'Eau). Il sépare **la mesure** du
**verdict**. Une mesure est un fait physique et ne change pas. Un verdict —
« conforme » — est une convention administrative, et elle se déplace dans le
temps. La même eau, avec la même mesure, peut être non conforme en 2016 et
conforme en 2026, non parce que l'eau s'est améliorée mais parce que le seuil a
bougé.

L'indicateur central est la **bascule** : une mesure qui dépassait la limite de
2016 et ne dépasse pas celle d'aujourd'hui.

> Ce n'est pas l'eau qui est devenue potable. C'est la limite qui a bougé.

## Ton rôle exact

Le dossier contient déjà un texte **dérivé** de la base : l'inventaire des
dépassements, des bascules, des indéterminés, les compteurs et les taux. Ce
texte est produit automatiquement et sera affiché de toute façon.

Ton travail est le complément, et lui seul : **ce que la base ne sait pas
dire.** Le territoire et ce qu'il explique du profil trouvé ; l'histoire ou le
statut réglementaire d'une substance ; la lecture d'une série dans le temps ; ce
qui distingue ce bulletin des autres. Tu ne reformules pas les chiffres déjà
dérivés — tu dis ce qu'ils veulent dire.

Si tu n'as rien à ajouter qu'on ne puisse déduire du dossier, écris moins. Une
section en moins vaut mieux qu'une paraphrase.

---

## Interdits absolus

Une seule de ces règles enfreinte, et le texte est rejeté à l'intégration.

1. **Aucune recommandation** de filtration, d'osmoseur, de charbon actif, d'eau
   embouteillée, de traitement, de procédé ou d'équipement — jamais, pas même en
   incise, pas même pour dire qu'un procédé retient mal telle molécule. Ce projet
   est un outil de conscience, pas un outil de prescription. Si la question
   « que faire » se pose, la seule réponse est l'information publique (ARS,
   mairie, données Orobnat).
2. **Aucune mise en cause d'un acteur** : ni l'ARS, ni le distributeur, ni le
   gestionnaire, ni le maire, ni l'agriculteur, ni le laboratoire. Un exploitant
   qui respecte une limite fixée par arrêté n'est pas en faute. On interroge la
   construction du seuil, jamais celui qui l'applique. Une limite de
   quantification élevée est une capacité d'instrument, pas une négligence.
3. **Aucun qualificatif sanitaire** : « dangereux », « toxique », « nocif »,
   « sain », « inquiétant », « alarmant », « à risque », « pollué »,
   « contaminé ». Tu décris des écarts à des seuils datés, rien de plus.
4. **Aucune affirmation d'absence.** Un paramètre non quantifié est « sous la
   limite de quantification du laboratoire », jamais « absent », « à zéro » ni
   « aucune trace ». Zéro n'est pas zéro : c'est une limite de l'instrument, pas
   une propriété de l'eau.
5. **Aucun chiffre qui ne figure pas dans le dossier.** Tu ne calcules pas de
   moyenne, tu ne convertis pas d'unité, tu n'estimes pas une dose ingérée, tu
   n'inventes aucun seuil. Un nombre décimal absent du dossier bloque
   l'intégration. Si un chiffre te manque, ne l'écris pas.
6. **Aucune comparaison avec un territoire que le dossier ne nomme pas.** Pas
   d'« ailleurs », pas de « le voisinage », pas de « la plupart des communes »,
   pas de « les grands réseaux ». Une comparaison se fait avec une zone nommée
   dont le corpus détient les bulletins, et l'effort de recherche des deux termes
   s'affiche avec elle.

## Règles de lecture, à appliquer dans le texte

- **Trois états, jamais deux** : conforme / dépassement / indéterminé. Un
  indéterminé — la limite de quantification du laboratoire est au-dessus du seuil
  auquel on compare — n'est pas un conforme, et ne se présente jamais ainsi.
- **Un verdict se rend à la date du prélèvement.** Un reclassement n'est pas
  rétroactif : une valeur non conforme en 2023 le reste ; la même valeur prélevée
  en 2025 est conforme. Le chiffre qui compte est le dépassement « applicable »,
  pas celui contre la grille d'aujourd'hui.
- **Jamais une conformité sans son dénominateur** : sur combien de paramètres
  notés, parmi combien de mesurés.
- **L'effort de recherche se lit à l'envers.** Une eau correcte sur 200
  paramètres est une information plus faible qu'une eau moyenne sur 700 : la
  première n'a pas été beaucoup interrogée. Ne jamais comparer des comptes bruts
  de dépassements entre deux bulletins d'effort différent.
- **Le repère le plus strict est « le plus strict identifié »**, jamais « le plus
  strict au monde » : le balayage mondial n'a été fait que sur les PFAS.
- **Le cumul se dénombre, il ne s'évalue pas.** On peut dire combien de
  substances de synthèse sont quantifiées ensemble, et que la réglementation les
  note une par une. Jamais le mot « risque ». Aucun indice présenté comme un
  verdict de potabilité, et tout indice cité vient avec le nombre de substances
  qui le composent.
- **Un seuil peut dépendre d'une condition** (procédé de désinfection, contexte
  géologique) que les données n'expriment pas. Entre le seuil de base et le seuil
  conditionnel, c'est un indéterminé, pas une non-conformité.
- Une valeur marquée « à vérifier » dans le dossier est signalée comme telle si
  tu l'emploies.

## Style

Phrases pleines, ton sobre et factuel, pas de listes à puces dans le corps du
texte, pas d'emphase décorative. Le lecteur est un habitant attentif, pas un
spécialiste : les sigles se développent à leur première apparition. Le HTML
autorisé se limite à `<b>` et `<i>`.

Un texte court et juste vaut mieux qu'un texte long. Entre une affirmation et
une formulation prudente, prends la prudente : la valeur du projet est sa
vérifiabilité, pas son volume.

---

## Ce que tu écris

Un seul fichier, `data/dossiers/reponses/PREL-<code>.json`, où `<code>` est
exactement celui du nom du dossier. Rien d'autre — pas de commentaire dans le
fil, pas de fichier annexe.

```json
{
  "sous_titre": "Eure-et-Loir (28) · plateau céréalier",
  "delta": "Une phrase.",
  "lecture_administrative": "Ce que conclut le contrôle sanitaire, reformulé sans le trahir.",
  "analyse": [
    {"t": "Titre court", "x": "2 à 6 phrases."},
    {"t": "Titre court", "x": "2 à 6 phrases."}
  ]
}
```

- `sous_titre` — une ligne de situation géographique et de contexte, sans
  jugement.
- `delta` — **une** phrase : l'écart entre ce que dit l'administration et ce que
  montre le bulletin. C'est la phrase la plus lue de la fiche. Si le bulletin ne
  porte aucun écart, dis-le simplement plutôt que d'en fabriquer un.
- `lecture_administrative` — la conclusion du contrôle sanitaire reformulée, avec
  les guillemets qui conviennent quand un mot est celui de l'administration.
- `analyse` — deux à quatre sections. N'écris que celles que le dossier alimente.
  Angles utiles, dans l'ordre : le territoire et ce qu'il explique ; l'histoire ou
  le statut réglementaire d'une substance trouvée ; la lecture de la série dans le
  temps quand le dossier en donne une ; ce que l'analyse ne pouvait pas voir.

Un dossier peut porter un point d'eau qui **alimente plusieurs communes** : le
dossier le dit alors explicitement. Le texte sera affiché sur toutes ces
communes — ne l'écris pas pour une seule.

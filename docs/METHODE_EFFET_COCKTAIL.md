# Méthode — charge cumulée et indice de danger

> Document préalable exigé par CLAUDE.md §7 : *« Ne pas publier de chiffre
> d'effet cocktail sans avoir écrit la méthode et ses limites. »*
> Version 1 — 7 août 2026.

Ce document définit trois indicateurs, du plus solide au plus fragile. Ils ne
se remplacent pas et ne doivent jamais être présentés sous le même mot.

---

## 1. Ce que la réglementation fait, et ce qu'elle ne fait pas

La réglementation note **substance par substance**. Chaque pesticide est
comparé à 0,1 µg/L, indépendamment des 299 autres présents dans le même verre.
Il existe une exception, la limite « pesticides totaux » à 0,5 µg/L, qui est
la seule reconnaissance réglementaire du cumul — et elle ne porte que sur les
pesticides.

Le corps, lui, boit le mélange. C'est le décalage que ces indicateurs
mesurent. **Ce décalage est un fait ; sa traduction en risque sanitaire ne
l'est pas.** Le projet s'arrête au premier.

---

## 2. Indicateur A — dénombrement des substances quantifiées

**Définition.** Nombre de substances de synthèse (familles `pesticide`,
`metabolite`, `PFAS`, `organique`) effectivement **quantifiées** dans un
bulletin complet, hors lignes agrégées (`est_agregat = TRUE`), pour ne pas
compter deux fois une somme et ses composants.

**Statut : constat.** Aucune hypothèse. Publiable tel quel.

**Formulation admise.** « 27 substances de synthèse ont été quantifiées dans
ce prélèvement ; chacune est conforme à sa limite propre. »

**Limite.** Un dénombrement dépend de ce que le laboratoire a cherché et de
sa limite de quantification. Deux bulletins ne sont comparables que s'ils
portent sur un nombre de paramètres voisin — d'où l'affichage systématique de
`nb_parametres`.

---

## 3. Indicateur B — charge massique cumulée

**Définition.** Somme des concentrations quantifiées des mêmes substances,
ramenée en µg/L.

**Statut : constat, sous une convention explicite.** L'addition de
concentrations est arithmétiquement licite ; elle n'implique aucune
équivalence toxicologique entre substances.

**Convention sur les non-quantifiés.** Les valeurs non quantifiées comptent
pour **zéro** (« zéro de substitution »). C'est la convention réglementaire.
Elle **sous-estime** la charge réelle, puisqu'une substance sous la limite de
quantification n'est pas absente (CLAUDE.md §2.4). La charge publiée est donc
un **plancher**, jamais une estimation centrale. Toute sortie doit le dire.

**Formulation admise.** « La charge cumulée quantifiée atteint 1,8 µg/L, soit
au moins 3,6 µg ingérés par jour pour deux litres — chaque substance prise
séparément étant conforme. »

**Formulation interdite.** « Cette eau contient 1,8 µg/L de polluants
dangereux. » L'addition ne crée pas de danger : elle décrit une exposition.

---

## 4. Indicateur C — indice de danger (hazard index)

**Définition.** `HI = Σ (concentration_i / seuil_i)` sur les substances
**de synthèse** quantifiées et notées (mêmes familles que A et B, hors lignes
agrégées), seuils ramenés à l'unité de la mesure. Un HI > 1 signifie que la
somme des fractions de seuil dépasse l'unité, alors même qu'aucune substance
ne dépasse la sienne.

**Périmètre, et pourquoi il est restreint.** Un premier calcul incluant tous
les paramètres notés donnait 1,07 sur Ramonville — un total porté par le
potassium, les chlorures, les sulfates et le sodium, c'est-à-dire par des
minéraux naturellement présents, comparés à des références de qualité
organoleptiques. Additionner une fraction de la référence en sodium à une
fraction de la limite d'un pesticide n'a aucun sens : ce ne sont pas les mêmes
objets, et les seuils n'ont pas la même nature. L'indice est donc restreint
aux substances de synthèse.

**Corollaire.** Une substance dont la famille est inconnue — notée par la
seule limite déclarée, sans ligne au référentiel — n'entre pas dans l'indice.
Le champ `indice_danger_n` indique sur combien de substances il porte. **Un
indice publié sans ce nombre n'est pas interprétable** et ne doit pas être
publié.

**Statut : raisonnement, pas mesure.** C'est l'indicateur le plus contestable
du projet et il doit être le plus encadré.

### Ce que cet indice suppose, et qui n'est pas démontré ici

1. **Additivité des doses.** Le HI suppose que les effets s'additionnent
   proportionnellement à la fraction de seuil consommée. C'est l'hypothèse
   retenue par l'EFSA pour les substances **partageant un même mode d'action**
   (groupes d'évaluation cumulative, CAG). Elle n'est pas établie pour un
   mélange hétérogène de 300 substances aux cibles biologiques différentes.
2. **Comparabilité des seuils.** Les seuils additionnés n'ont pas la même
   nature : 0,1 µg/L pour un pesticide est une valeur de **gestion**
   (limite de détection historique érigée en norme), pas une valeur
   **toxicologique**. Diviser une concentration par une norme de gestion ne
   produit pas une fraction de dose toxique.
3. **Absence de facteur d'ajustement.** Les cadres de référence prévoient un
   MAF (*mixture assessment factor*) pour tenir compte du mélange. Aucun MAF
   n'est appliqué ici.

### Cadres de référence à documenter avant tout usage argumentatif

- **CAG / MOET (EFSA)** — groupes d'évaluation cumulative par organe cible ;
- **MAF** — facteur d'ajustement des mélanges, en discussion au niveau UE ;
- **EDC-MixRisk** — mélanges de perturbateurs endocriniens.

Ces cadres ne sont **pas** implémentés. Tant qu'ils ne le sont pas, le HI de
ce projet est un **indicateur de structure**, utile pour classer des
bulletins entre eux, et non une estimation de risque.

### Règles de publication

- toujours nommé « indice de danger (méthode simplifiée) », jamais « risque » ;
- toujours accompagné du nombre de substances qui le composent et de la part
  des seuils issus du référentiel daté plutôt que de la limite déclarée ;
- jamais présenté comme un verdict de potabilité ;
- jamais utilisé pour désigner un acteur (CLAUDE.md §2.1) ;
- ne donne lieu à **aucune recommandation** d'aucune sorte (CLAUDE.md §2.2).

**Formulation admise.** « En additionnant, pour chaque substance quantifiée,
la fraction de sa propre limite qu'elle occupe, on obtient 1,4. Autrement dit,
si l'on raisonnait sur le mélange plutôt que substance par substance, cette
eau dépasserait le repère — alors qu'aucune de ses 300 mesures ne dépasse le
sien. C'est un raisonnement, pas une mesure de risque. »

---

## 5. Ce que ces indicateurs ne diront jamais

Ils ne disent pas si l'eau est saine. Ils disent ce que la grille
réglementaire ne regarde pas : le cumul. Le projet reste un outil de
conscience, pas de prescription.

# Note de méthode — toute substance mesurée reçoit une attribution

**Écrite le 11 août 2026, sur décision de Yannick. Proposition de vocabulaire :
rien n'est implémenté, le moteur n'a pas été touché.**

> *« Mon objectif reste le même : mettre en lumière ce qui est analysé. Si la
> substance ressort, on doit lui donner une attribution. Même si cette
> attribution est "rien ne se prononce sur cette partie". »*

---

## 0. LES QUATRE ATTRIBUTIONS — à valider avant tout le reste

**C'est le seul point qui demande une décision. Tout le reste en découle.**

| # | attribution | ce que ça veut dire | ce que le lecteur lit à l'écran | mesures | libellés | dont quantifiées |
|---|---|---|---|---:|---:|---:|
| 1 | **Jugé** | un seuil de notre référentiel daté s'applique | *« conforme »* · *« dépassement »* · *« indéterminé — l'analyse ne descend pas assez bas pour conclure »* | 2 966 074 | 776 | 97 897 |
| 2 | **Jugé avec son groupe** | pas de valeur propre, le texte juge l'ensemble | *« pas de limite individuelle — compte dans les hydrocarbures aromatiques polycycliques (somme des 4), qui est [verdict] »* | 4 887 | 13 | 604 |
| 3 | **Rien ne se prononce** | aucun texte ne fixe de valeur pour cette substance | *« aucune réglementation ne fixe de valeur pour cette substance »* + l'un des deux états ci-dessous | **306 119** | **229** | **103 460** |
| 3a | · établi | démontré par un dossier de sourçage, qui a laissé une ligne au référentiel | *« vérifié le [date] sur les textes suivants — voir le dossier »* | 17 565 | 5 | 17 228 |
| 3b | · non encore instruit | personne n'a encore vérifié | *« pas encore vérifié par l'Observatoire »* | 288 554 | 224 | 86 232 |
| 4 | **Jugé sur la valeur déclarée** | un chiffre figure dans le fichier de l'administration, pas dans notre référentiel daté | *« jugé sur la valeur déclarée par l'administration — aucune comparaison avec la norme d'hier n'est possible »* | 84 253 | 30 | 25 949 |
| 5 | **Norme non exprimée** | le texte encadre bien cette substance, mais sous une forme que le moteur ne sait pas comparer | *« encadré par une plage de valeurs que l'Observatoire ne sait pas encore vérifier »* | 17 779 | 3 | 17 664 |

**La cinquième est née d'un défaut trouvé à la vérification, et elle évite une
affirmation fausse.** Le pH est encadré par une **plage** — 6,5 à 9 — et la
conductivité aussi, 200 à 1 100 µS/cm ; la turbidité de même. Le modèle ne porte
qu'un seuil unique, jamais deux bornes. Sans cette cinquième valeur, ces trois
paramètres ressortaient en « rien ne se prononce », ce qui est **faux** : le
texte les encadre, c'est nous qui ne savons pas encore l'exprimer. Même famille
de cas que les chlorites, dont la référence a expiré au 31 décembre 2025 sans
que le modèle sache porter une date de fin (`CLAUDE.md` §8).

**Le potassium et le magnésium, eux, restent bien un silence de la norme** —
leurs lignes le disent explicitement, sources à l'appui.

**Un effet de bord à connaître, et il est vertueux** : l'état « établi » ne se
déclenche que si **une ligne existe au référentiel**. Un dossier de sourçage qui
conclut « aucun texte ne fixe de valeur » et ne verse aucune ligne reste
invisible — le fluoranthène est dans ce cas aujourd'hui. **Le sourçage ne devient
visible qu'en laissant une trace au référentiel** : une ligne sans seuil, avec
ses sources et sa date. C'est le geste qui fait passer une substance de 3b à 3a.

**Les trois issues de l'attribution 1 sont inchangées** — conforme, dépassement,
indéterminé. Ce qui est nouveau, ce sont les attributions 2, 3 et 4, qui
concernent aujourd'hui des mesures qui **n'apparaissent nulle part**.

**Les libellés d'écran de la colonne 4 sont une proposition, pas une décision.**
Ce sont eux qu'il faut relire de près : ce sont les seules phrases que le lecteur
verra. Le §5 donne la règle de rédaction qui les gouverne.

---

## 1. Le trou qu'on comble, et sa taille

Le corpus compte 3 379 112 mesures. Aujourd'hui, à l'écran, elles se répartissent
ainsi :

| ce qui juge la mesure | mesures | libellés |
|---|---:|---:|
| notre référentiel daté, grille en vigueur | 2 927 126 | 776 |
| notre référentiel daté, grille de 2016 | 38 948 | 17 |
| la limite déclarée par l'administration | 85 446 | 35 |
| **rien** | **327 592** | **240** |

**Une mesure sur dix ne reçoit aucun verdict.** Et ce n'est pas un résidu
technique : parmi ces mesures, **environ 76 000 sont des quantifications**. Le
laboratoire a cherché, il a trouvé quelque chose, et la sortie du projet n'en dit
rien. Ni conforme, ni dépassement, ni indéterminé — absente.

*Écart à réconcilier : la vue de diagnostic des paramètres non appariés en compte
215, la vue des verdicts 240. Les deux ne filtrent pas pareil. À trancher avant
implémentation, ça ne change pas le principe.*

**C'est ce silence que la note supprime.** Pas en inventant un seuil — en disant
qu'il n'y en a pas.

---

## 2. Le principe

> **Toute substance recherchée reçoit une attribution explicite. Aucune ne
> disparaît de la sortie faute de seuil.**

Corollaire immédiat, et c'est lui qui fait la valeur du dispositif : **l'absence
de norme devient un fait affiché**, daté et sourçable, au même titre qu'un seuil.
Le projet démontre déjà qu'un verdict de potabilité est une convention qui se
déplace dans le temps. Il montrera aussi **où cette convention ne dit rien du
tout**.

---

## 3. Les quatre attributions

### 3.1 Jugé

Un seuil de notre référentiel daté s'applique. C'est le régime actuel, avec ses
trois issues inchangées (§2.4 de `CLAUDE.md`) : **conforme**, **dépassement**,
ou **indéterminé** quand la limite de quantification du laboratoire est au-dessus
du seuil de comparaison — sous cette valeur l'analyse ne voit rien, là où la
conformité se joue.

### 3.2 Jugé avec son groupe

La substance **n'a pas de valeur propre** : le texte juge le groupe auquel elle
appartient. On nomme l'ensemble, on donne **le verdict de l'ensemble**, et on ne
prononce jamais de dépassement sur la ligne individuelle.

Cas établis à ce jour : les quatre hydrocarbures aromatiques polycycliques de la
somme réglementée (benzo(b)fluoranthène, benzo(k)fluoranthène,
benzo(g,h,i)pérylène, indéno(1,2,3-cd)pyrène), et les cinq acides haloacétiques.

**Ce que cette attribution résout, et c'est important.** Aujourd'hui, quand notre
référentiel dit « pas de valeur propre », le moteur lit un vide et le comble avec
la limite que l'administration déclare dans ses fichiers — les quatre
hydrocarbures ressortent ainsi notés contre 0,10 µg/L, valeur que la directive ne
fixe **que pour leur somme**. Avec ce vocabulaire, « compte dans un ensemble »
**est une réponse et non un vide** : elle prime sur la déclaration de la source.

C'est la question de méthode laissée ouverte le 11 août, et elle se dissout dans
le choix du vocabulaire plutôt que dans un arbitrage de hiérarchie.

### 3.3 Rien ne se prononce

**Aucun texte, nulle part où l'on a regardé, ne fixe de valeur pour cette
substance dans l'eau destinée à la consommation humaine.**

C'est l'attribution nouvelle, et elle porte deux états qu'il ne faut jamais
confondre :

- **établi** — un dossier de sourçage l'a démontré : les textes ont été consultés
  et sont nommés un par un. Six dossiers existent au 11 août 2026 (fluoranthène,
  Fréon 113, phosphate de tributyle, dalapon, tétrachlorure de carbone,
  éthylbenzène), plus ceux du lot précédent. L'attribution renvoie au dossier ;
- **non encore instruit** — la substance n'a pas de seuil dans notre référentiel,
  et personne n'a encore vérifié qu'il n'en existe nulle part.

**Cette distinction n'est pas cosmétique : c'est la règle 5 du sourçage.**
*« Je n'ai pas trouvé » n'est pas « il n'existe pas ».* Le second ne se dit que
si les textes de référence ont été consultés et nommés. Afficher les deux états
séparément est la seule façon honnête de tenir cette règle à l'échelle de 240
libellés.

Effet secondaire utile : **le travail de sourçage devient visible et mesurable**.
Chaque molécule instruite fait basculer une ligne de « non encore instruit » à
« établi, voir le dossier ». Un chantier de plusieurs mois affiche son avancement
au lieu de rester en coulisse.

### 3.4 Jugé sur la seule déclaration de l'administration

Un chiffre figure dans le fichier de données publié, mais **pas dans notre
référentiel daté**. Le verdict est rendu, et il porte une réserve : **aucune
comparaison avec la norme d'hier n'est possible**, parce qu'on ne fabrique pas un
passé réglementaire à partir d'une déclaration du jour (§2.8). Ces lignes ne
peuvent donc jamais produire de bascule.

35 libellés et 85 446 mesures sont dans ce cas.

---

## 4. Pourquoi pas le mot « vigilance »

Il servait déjà, et à autre chose. Dans le référentiel, « vigilance » qualifie
une substance **dont la norme a bougé ou est contestée** : le chlorothalonil
R471811, dont la valeur propre est devenue indicative après un reclassement de
pertinence ; le dalapon, que le texte vise par sa définition des pesticides sans
qu'aucun acte le nomme.

Ces cas disent **« ça bouge »**. Le cas nouveau dit **« c'est muet »**. Deux
faits différents sous un même mot, c'est exactement l'erreur que le projet
dépense son énergie à éviter partout ailleurs — trois registres jamais fusionnés,
statut réglementaire distinct du statut scientifique, mesure distincte du
verdict. La discipline vaut aussi pour son propre vocabulaire.

---

## 5. Comment ça se dit — la règle de rédaction

**C'est la partie la plus délicate de la note, et elle décide de la solidité de
tout le reste.**

« Rien ne se prononce » ne doit jamais se lire comme un feu vert. Le projet a
déjà sa formule, elle vaut règle :

> **Une substance sans seuil n'est pas « sans danger » : elle est indéterminée.**

Ce qui est permis, parce que c'est factuel, daté et vérifiable :

- « Cette eau est déclarée conforme. Elle contient **N substances de synthèse
  quantifiées**, dont **M que la réglementation ne juge pas** — ni en France, ni
  dans l'Union, vérification faite sur les textes nommés ci-dessous. »
- « Cette substance a été recherchée dans X analyses et trouvée dans Y. Aucun
  texte ne lui fixe de valeur. »

Ce qui est interdit, et qui affaiblirait le propos au lieu de le renforcer :

- **tout qualificatif de notre cru** — « soupe chimique », « cocktail »,
  « pollué », « toxique ». Ce sont des jugements, et ce sont les seules prises
  par lesquelles ce travail est attaquable. La version factuelle est plus dure,
  pas plus douce : elle ne se conteste pas ;
- **présenter l'absence de seuil comme une faute de quelqu'un.** On interroge la
  norme, jamais l'ARS, le distributeur, le maire ou l'exploitant (§2.1) ;
- **suggérer une conduite** — filtrer, éviter, s'inquiéter. Outil de conscience,
  pas de prescription (§2.2) ;
- **additionner ces substances en un indicateur unique** sans la note de méthode
  et ses limites (§7.1). Le dénombrement est solide ; l'agrégation ne l'est pas
  encore.

**Le test à s'appliquer avant de publier une phrase** : si on retire tous les
adjectifs, reste-t-il un fait daté et sourcé ? Si oui, la phrase tient. Sinon,
c'est une opinion, et elle sort.

---

## 6. Ce que ça change dans les compteurs affichés

Le projet affiche déjà « X paramètres notés sur Y mesurés » à côté de chaque
verdict (§2.8). Avec les quatre attributions, ce compteur devient lisible :

- les substances **jugées** — le numérateur actuel ;
- celles qui **comptent dans un ensemble** — jugées, mais collectivement ;
- celles dont **rien ne se prononce** — établi ou non encore instruit ;
- celles jugées **sur la seule déclaration** de l'administration.

**Le total ne bouge pas. Ce qui change, c'est qu'aucune catégorie ne reste
invisible.** Environ 76 000 quantifications passent d'absentes à comptées et
nommées.

Et la règle d'affichage du §8bis s'étend d'une ligne : **« rien ne se prononce »
a sa propre couleur**, ni verte ni rouge — comme « non documentée » et
« indéterminé ». Ni rassurante, ni alarmante.

---

## 7. Ce que ça demande, et dans quel ordre

Rien n'est implémenté. Par ordre de dépendance :

1. **Valider le vocabulaire** — quatre attributions, leurs deux sous-états, et
   les mots exacts affichés. Décision de Yannick, c'est le seul préalable.
2. **Réconcilier les deux comptages** (215 contre 240) avant de chiffrer quoi que
   ce soit en public.
3. **Faire produire l'attribution par le moteur** plutôt que de la déduire à
   l'affichage — une sortie figée doit porter l'attribution qu'elle avait le jour
   du calcul, comme elle porte sa version de référentiel. Cela touche les vues,
   donc **impose un recalcul complet du corpus** (~100 min).
4. **Étendre le référentiel** : une ligne peut désormais exister pour dire qu'il
   n'y a rien à dire, avec sa source et sa date. C'est ce que font déjà les six
   lignes versées le 11 août.
5. **Rédiger les libellés d'écran**, une fois, en appliquant le §5.

**Point 3 à ne pas sous-estimer** : tant que l'attribution est calculée à
l'affichage, deux écrans peuvent dire deux choses différentes du même bulletin.
C'est précisément ce que le figeage existe pour empêcher.

---

## 8. Ce que ça ouvre

Le sourçage cesse d'être un travail interne. Chaque molécule instruite devient
**la pièce justificative d'une attribution affichée** : le lecteur qui clique sur
« rien ne se prononce » trouve la liste des textes consultés, leur date, et ce
qu'ils contiennent ou non.

C'est aussi ce qui rend supportable un chantier long. 240 libellés à instruire un
par un, c'est plusieurs mois. Avec les deux sous-états du §3.3, **l'avancement
est public et honnête à chaque étape** : ce qui est démontré est marqué démontré,
ce qui ne l'est pas est marqué comme tel. Aucune étape intermédiaire n'oblige à
prétendre plus que ce qu'on sait.

---

*Voir aussi : `CLAUDE.md` §2.4 (trois états de verdict), §2.7 (toute affirmation
chiffrée est sourcée ou marquée), §2.8 (le dénominateur, et la limite seulement
déclarée), §8bis (obligations d'affichage) ; `docs/CONSIGNE_SOURCAGE.md` pour la
production des dossiers ; `data/etudes/sourcage_C/` pour les dossiers rendus.*

# Ce qui nous distingue — note de stratégie

**Observatoire de la potabilité réglementaire — Éditions Mytae.**
Écrite le 11 août 2026. Actualise la `Note_Comparative_MonEauNette_et_Transfert_2026.md`
du 6 août, qui reste valable sur l'analyse du site concurrent mais dont **deux
affirmations de différenciation ont bougé** depuis (§4 ci-dessous).

---

## 1. La phrase qui tient tout

Tous les sites d'eau du robinet affichent **des valeurs mesurées face à des
seuils**. C'est la partie facile : l'API Hub'Eau la donne gratuitement, et un site
statique bien fait la restitue très bien.

Aucun ne dit **ce que ce verdict vaut**.

> **Nous ne montrons pas si l'eau est conforme. Nous montrons à quoi
> « conforme » se compare — et ce que cette comparaison ne couvre pas.**

C'est la seule position que la donnée brute ne donne pas, et c'est celle qui
demande un travail que personne n'a envie de faire : lire les textes, un par un,
et les dater.

---

## 2. Les quatre différenciations, par ordre de solidité

### 2.1 Le verdict daté — le socle, et il est architectural

Une mesure ne change pas ; la règle qui la juge, si. Nous conservons les deux
grilles et nous confrontons chaque mesure aux deux.

**Pourquoi c'est défendable et pas copiable à peu de frais** : un site sans base
de données ne peut pas le faire. Il réinterroge l'API à chaque visite, rien ne
s'accumule, donc « combien de bulletins conformes aujourd'hui ne l'auraient pas
été il y a dix ans » lui est **structurellement impossible**. Ce n'est pas une
question d'effort éditorial, c'est une question d'architecture.

**Et nous avons désormais le cas concret**, ce qui manquait le 6 août :
**14 métabolites de pesticides sont passés de 0,1 à 0,9 µg/L** — neuf fois plus
permissif — parce qu'ils ont été déclassés de « pertinent » à « non pertinent ».
Le relèvement n'est même pas le plus grave : le déclassement les fait aussi
**sortir du total des pesticides**, qui est la valeur opposable. Deux effets, une
seule décision administrative, aucun changement dans l'eau.

C'est la démonstration de la thèse, et elle porte sur quatorze substances
nommées, pas sur un exemple.

### 2.2 Ce que personne n'a jamais jugé — l'angle neuf, et personne ne l'a

Découvert les 10 et 11 août en sourçant substance par substance. Des molécules
**mesurées par l'ARS, quantifiées dans l'eau distribuée, et qu'aucun texte au
monde ne permet de déclarer conformes ou non conformes.**

Ni conformes, ni non conformes : **indéterminées**.

Cas établis en source primaire : le trichlorofluorométhane, mesuré jusqu'à
160 µg/L quand la seule limite opposable trouvée où que ce soit est à 150 ; le
dichloroéthane-1,1, dont l'OMS écrit qu'elle **ne sait pas** ; le toluène ; le
trichloroéthane-1,1,1, dont l'OMS a renoncé pour un motif d'exposition ; les
dichloroéthylènes, produits de dégradation dont **les trois maillons voisins de
la chaîne sont réglementés et pas eux**.

**Pourquoi personne ne l'a** : ça ne se déduit d'aucune donnée. Il faut ouvrir la
directive, l'arrêté consolidé, les recommandations de l'OMS, et constater
l'absence — puis savoir distinguer « je n'ai pas trouvé » de « il n'existe pas ».
C'est du travail de lecture réglementaire, substance par substance, et c'est
précisément ce qu'un site statique ne peut pas fabriquer.

C'est aussi l'angle le plus mobilisateur : le lecteur qui trouve une substance
dans ce bloc **sait qu'il doit chercher lui-même**, et c'est un point de départ,
pas une conclusion.

### 2.3 La rigueur du dénominateur et du périmètre — invisible, et c'est ce qui protège

Trois disciplines qu'aucun site grand public ne tient :

- **Le dénominateur.** « 323 paramètres notés sur 383 mesurés ». Un verdict sur
  74 % des mesures n'est pas un verdict sur 94 %. Sans ce chiffre, « conforme »
  est une demi-vérité.
- **Trois états, pas deux.** Conforme / dépassement / **indéterminé**, quand la
  finesse de l'analyse ne permet pas de conclure. Un zéro obtenu avec un
  instrument grossier n'est pas une absence.
- **Le périmètre des sommes.** Une limite qui porte sur « la somme de ces
  **quatre** substances » ne s'étend pas à une cinquième qui leur ressemble
  chimiquement. Exemple vérifié : le trichlorofluorométhane **est** un
  trihalométhane au sens de la chimie, et n'entre pas dans le total des
  trihalométhanes, qui nomme quatre composés.

**Ce que ça vaut stratégiquement** : c'est ce qui nous empêche de fabriquer de
faux dépassements. Un site qui agrège par ressemblance produit des alertes
spectaculaires et fausses ; la première contestation le détruit. Notre rigueur
est ennuyeuse et c'est un actif : **nous pouvons être contredits sur une valeur,
pas sur la méthode.**

### 2.4 La neutralité vérifiable — le seul actif qu'on ne peut pas nous copier

Aucune recommandation de produit, d'équipement, de fournisseur. Aucun aval
commercial.

Le principal site comparable est tenu par une entreprise de traitement de l'eau
qui vend de l'osmose inverse, et qui le déclare honnêtement — mais dont les pages
concluent sur la filtration. Ce n'est pas une accusation : c'est une **asymétrie
structurelle**. Une alerte publiée par quelqu'un qui vend la solution ne pèse pas
le même poids devant une mairie, un journaliste ou un financeur.

Et notre neutralité est **vérifiable** : données ouvertes sous ODbL, référentiel
versionné, chaque valeur portant sa source et son niveau de fiabilité. N'importe
qui peut refaire le calcul et nous prendre en défaut. C'est ce qui transforme la
neutralité affichée en neutralité démontrable.

---

## 3. Le corollaire à ne pas rater : la reproductibilité

Chaque chiffre publié porte **la version de référentiel qui l'a produit**.

Cela paraît technique. C'est en réalité la preuve vivante de la thèse : le
10 août, le nombre de bulletins concernés en Eure-et-Loir est passé de **280 à
260 en quatre versions dans la même journée**, sans qu'un seul prélèvement
change. Seule la grille avait bougé.

**Un concurrent qui affiche un chiffre sans dire contre quelle grille il a été
calculé ne peut pas défendre ce chiffre six mois plus tard.** Nous, si.

---

## 4. Ce qui N'EST PAS encore une différenciation — à ne pas survendre

La note du 6 août présentait la comparaison internationale comme un « axe
explicite » déjà acquis. **C'est faux aujourd'hui**, et le dire évite une promesse
intenable.

État réel au 11 août : un balayage international sérieux n'a été fait que pour
**les PFAS**. Pour les 46 autres paramètres, le référentiel porte un « repère le
plus protecteur » qui, dans 46 cas sur 79, **recopie simplement la limite
française** — ce qui laisse croire à tort que personne n'est plus strict alors
que personne n'a cherché.

Deux fragments obtenus le 11 août montrent que l'axe est réel quand on le
travaille : sur **l'arsenic**, le New Hampshire applique 5 µg/L depuis le
1er juillet 2021 et le New Jersey 5 µg/l, contre 10 en France. Mais quatorze
juridictions sur quinze n'ont pas été regardées.

**Conséquence pour la communication** : dire « le plus strict **identifié** parmi
les juridictions suivantes », jamais « le plus strict au monde ». Et ne pas
annoncer cet axe comme un acquis tant que le balayage n'est pas fait sur les
substances qui comptent. C'est un chantier chiffré : environ 6 millions de
tokens pour les 46 paramètres, à faire par petits lots, en commençant par les
substances **réellement quantifiées dans les bulletins**, pas par la liste du
référentiel.

---

## 5. Où les autres sont devant, et il ne faut pas se le cacher

- **La distribution.** Couverture nationale immédiate, alertes par courriel,
  application installable, carte cliquable, comparaison par rayon, mode
  nourrisson, moteur « une substance, toutes les communes ». Ils ont un public,
  nous avons trois départements en cours.
- **L'étendue.** Corpus des eaux embouteillées, paramètres radiologiques traités
  éditorialement, contenus pédagogiques abondants.

**Formule à retenir : ils ont l'audience et l'étendue, nous avons la méthode et
la profondeur.** Ce ne sont pas les mêmes métiers.

---

## 6. La position à occuper

**Une infrastructure, pas un site concurrent.**

Le référentiel daté, sourcé et ouvert est réutilisable par n'importe qui — y
compris par les sites mieux distribués que le nôtre. Chaque réutilisation est
une preuve d'utilité, et l'argument le plus finançable qui soit : *« N sites
s'appuient sur notre référentiel »*.

Trois conditions non négociables à toute réutilisation :

1. **Partage à l'identique** (ODbL 1.0), pour que les corrections reviennent ;
2. **Attribution visible** sur toute page qui l'utilise ;
3. **Clause de non-caution** : l'Observatoire ne recommande ni ne cautionne aucun
   équipement ni aucun fournisseur — indispensable dès lors qu'un réutilisateur a
   un aval commercial.

Et la règle qui décide de tout : **le sens de la dépendance.** Si un tiers
intègre notre référentiel et que la relation tourne mal, nous ne perdons rien —
il est publié de toute façon. Si nos fiches vivent à l'intérieur de son site,
nous perdons le projet.

---

## 7. Ce que ça implique de construire, dans l'ordre

1. **Le bloc « conforme — mais selon quelle règle ? »** : plus strict ailleurs /
   recommandé sans être repris / cherché ou pas. C'est le bloc qui matérialise
   la différenciation 2.1 et 2.4 pour le lecteur.
2. **Le bloc « ce que personne n'a jamais jugé »**, alimenté par le sourçage.
   C'est l'exclusivité 2.2, et elle grandit à chaque substance traitée.
3. **Le référentiel daté publié en fichier ouvert** — c'est ce qui fait de nous
   une infrastructure plutôt qu'un site, et c'est immédiat.
4. **Le balayage international**, par petits lots, sur les substances réellement
   quantifiées.
5. La distribution vient après. Elle se rattrape ; la méthode, non.

---

## 8. Une seule phrase à dire à un tiers

> Les autres vous disent si votre eau est conforme.
> Nous vous disons **à quelle règle**, depuis quelle date, sur quelle part des
> paramètres analysés — et ce que cette règle ne regarde pas du tout.

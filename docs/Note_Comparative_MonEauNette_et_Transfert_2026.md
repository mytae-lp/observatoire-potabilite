# Mon Eau Nette (Pierre Gaudin) — analyse, différences et conditions de transfert

**Observatoire de la potabilité réglementaire — Éditions Mytae**
Note de travail, 6 août 2026. Site analysé : `https://mon-eau-nette.pages.dev/` (56 pages listées au sitemap).

---

## 1. Ce qu'est réellement le site

Mon Eau Nette est tenu par **Pierre Gaudin (« Pierr'Eau »)**, entrepreneur individuel en micro-entreprise à Puget-sur-Argens (83), SIRET 754 058 097 00066, sous l'enseigne **E.W.S. (Eco Watt Système)**, entreprise de traitement de l'eau en PACA depuis 2014. Hébergement gratuit sur Cloudflare Pages, aucun cookie, aucun tracking, aucune publicité, alertes email via Brevo, site installable en PWA. Les coûts sont pris en charge par E.W.S.

L'architecture est **statique et sans état** : des pages HTML qui interrogent l'API Hub'Eau côté navigateur, plus `geo.api.gouv.fr` pour la géolocalisation et OpenStreetMap pour le fond de carte. Rien ne s'accumule : chaque visite reinterroge la source. La page « tableau de bord » n'est pas un tableau de bord de l'eau mais une **mesure d'audience** (visites, pages vues, communes recherchées), protégée par une clé Cloudflare.

Le cœur « eau du robinet » tient en trois briques : la recherche par commune ou code postal (`ma-ville.html`, avec comparaison par rayon de 10 à 50 km et un **mode nourrisson**), un moteur inversé « une substance, toutes les communes » par département (`moteur-substances.html`), une carte France cliquable (`carte-france.html`), et un fil d'alertes « en direct » avec priorité donnée aux alertes nourrissons.

Autour, une bibliothèque pédagogique considérable : eaux plates et gazeuses au banc d'essai, les 35 sources Cristaline, seuils nourrissons, exposition au chlore, cuisson, dialyse, prix de l'eau, calculateur « ce que j'avale sur cinquante ans », quiz, glossaire, page « arnaques » (dont un dossier Kangen appuyé sur une mise en demeure FTC 2021), page « preuves et sources ».

### Ce qui est solide et qu'il faut reconnaître

La **portée citoyenne** est très supérieure à la nôtre aujourd'hui : couverture nationale immédiate, alertes email, PWA, carte, mode nourrisson, moteur inversé par substance. Nous avons sept fiches ; il a un public.

La **maturité des mises en garde** est réelle. Sur le moteur inversé, il avertit explicitement que les comparaisons brutes peuvent tromper : fréquence de mesure inégale entre communes, *substance non mesurée ≠ substance absente*, changements de méthode, dépassement ≠ risque immédiat, réseaux d'eau intercommunaux. C'est exactement l'esprit de notre règle sur la limite de quantification, énoncé en langage citoyen.

La page **« Deux balances »** est excellente et proche de nous : elle met en regard les seuils eau embouteillée « nourrissons » et eau du robinet — nitrates 10 contre 50 mg/L (×5), nitrites 0,05 contre 0,5 (×10), fluorures 0,5 contre 1,5 (×3), sulfates 140 contre 250 (×1,8) — avec huit références Légifrance, EUR-Lex, ANSES, OMS. Le raisonnement est le nôtre, appliqué à un autre axe.

Le **calculateur cinquante ans** est le cousin de notre « total consommé », et le **protocole de terrain** (conductimètre Apera PC60-Z calibré, mesures datées des 08/08/2025 et 10/09/2025, captures archivées) est plus rigoureux que ce qu'on trouve habituellement sur ce type de site.

Enfin il couvre deux domaines que notre référentiel ignore : les **paramètres radiologiques** (radon 222, tritium, potassium 40) et un **corpus eaux embouteillées** que nous n'avons pas du tout.

### Où il s'arrête — constats vérifiés

**Le référentiel est une liste statique d'environ 60 paramètres en 6 familles** (`annexe.html`), et sa source de synthèse déclarée est, à côté du Code de la santé publique, **« Sélectra Eau »** — un comparateur commercial, pas un texte primaire. Le résultat est ce que produit toujours une grille tenue à la main : au moins une valeur périmée et des paramètres manquants.

- **Sélénium : il affiche 10 µg/L.** La limite a été **relevée à 20 µg/L** par l'arrêté du 30 décembre 2022, applicable depuis le 1er janvier 2023. Valeur périmée.
- **Absents de sa grille** alors qu'ils sont en vigueur depuis 2023 : antimoine (relevé de 5 à 10 µg/L), bore (relevé de 1,0 à 1,5 mg/L), chrome hexavalent (6 µg/L), uranium chimique, bisphénol A, chlorates.
- **Point d'honnêteté, et qui nous concerne nous** : son **plomb à 10 µg/L** et son **chrome total à 50 µg/L** sont **corrects aujourd'hui**. Les valeurs resserrées (plomb 5 µg/L, chrome total 25 µg/L) ont une **mise en œuvre différée au 1er janvier 2036**. Or notre propre table `referentiel_seuils` porte `plomb seuil_2026 = 5,0` : **c'est un bug de notre base**, à corriger avant tout partage (voir §4, préalable).
- « Magnésium : 50 mg/L » figure parmi ses limites physico-chimiques ; le magnésium n'a **pas** de limite de qualité au robinet — 50 mg/L est un repère nourrisson / eau embouteillée. Confusion de registre.

**Aucune dimension datée.** Nulle part le site ne compare le seuil en vigueur en 2016 à celui en vigueur en 2026. La page `pourquoi-pas-les-memes.html` traite un écart **spatial et catégoriel** (embouteillé contre robinet, deux réseaux dans une même commune), pas temporel. Et « Deux balances » **argumente l'inverse de notre thèse** : elle souligne que la limite nitrates de 50 mg/L est *inchangée depuis plus de 45 ans*. C'est vrai — et c'est précisément pourquoi les nitrates sont le mauvais paramètre pour démontrer la dérive. La dérive est dans les **métabolites** (0,1 → 0,9 µg/L pour les non pertinents), l'antimoine, le sélénium, le bore. Il a la bonne intuition sur le seul paramètre qui ne bouge pas, et rate ceux qui bougent.

**Aucune comparaison internationale.** Pas de Danemark, pas d'Allemagne, pas d'US EPA, pas de Californie. L'axe « le plus strict au monde » est entièrement absent.

**Aucun effet cocktail.** Vérifié sur `substances.html` : les PFAS sont bien traités (« polluants éternels », PFOA classé cancérogène groupe 1 depuis 2023), les métabolites sont nommés (métolachlore ESA, chlorothalonil), les perturbateurs endocriniens ont une section (« même à faible dose ») — mais **rien ne somme**. Et attention au malentendu : son calculateur cinquante ans additionne le **résidu sec / la charge minérale dissoute** (via la conductivité), pas la masse de micropolluants. Ce n'est pas la même grandeur : il pèse des minéraux, nous comptons des microgrammes de molécules de synthèse.

**Aucun filtre de complétude.** Sa fiche commune affiche la « dernière valeur connue par paramètre sur les 12 derniers mois ». C'est un **profil synthétique reconstitué** : chaque paramètre vient du bulletin où il a été vu le plus récemment. Avantage réel — couverture maximale, il y a toujours quelque chose à montrer. Inconvénient structurel — le profil n'a **pas de date unique**, il ne peut pas être réétalonné comme un bulletin cohérent, la conclusion de conformité officielle du prélèvement se dilue, et surtout il **noie les rares bulletins complets** (370 à 400 paramètres) dans les innombrables bulletins de routine (~25 paramètres). C'est exactement le mécanisme qui produit « tout va bien ». Notre règle des bulletins > 250 paramètres est le pari inverse.

**Pas de gestion explicite de la limite de quantification.** Son avertissement « non mesurée ≠ absente » est proche, mais il porte sur l'absence de mesure, pas sur la **finesse analytique** : un « 0 » obtenu avec une LQ grossière n'est pas une conformité au seuil strict. Rien ne distingue, dans son affichage, quantifié / sous LQ / non mesuré.

**Aucune base de données.** Rien ne s'accumule, donc rien n'est agrégeable : pas d'historique, pas de statistique nationale, pas de jeu de données rejouable. « Combien de communes conformes en 2026 ne l'auraient pas été en 2016 » est **structurellement impossible** sur son architecture.

**Ni open data, ni open source.** Les mentions légales réservent textes, images et mises en page comme « propriété intellectuelle de Pierr'Eau », interdisent la reproduction et l'usage commercial sans accord. L'open source est une **promesse future** (« si ce site s'arrête, une copie sera maintenue gratuitement, open source sur GitHub ») ; aucun dépôt public n'est trouvable à ce jour. Un citoyen ne peut donc pas télécharger son jeu de données.

**Conflit d'intérêts déclaré mais structurel.** À son crédit, il l'écrit noir sur blanc en page « À propos » : « Pierr'Eau vend des installations d'osmose inverse via E.W.S. ». Mais le site **recommande de la filtration** (anti-sédiments puis charbon actif comme base), explique que « une filtration sans rejet finit par relarguer » alors que l'osmose évacue en continu, et le calculateur cinquante ans se conclut sur « osmose inverse : −95 % de charge dissoute ». C'est la **divergence la plus lourde** avec notre ligne : *« ce n'est pas le propos, ici c'est un outil de conscience »*, et avec notre garde-fou *« interroger la norme, pas accuser les acteurs »*.

---

## 2. Les différences sur l'analyse des données

| Axe d'analyse | Mon Eau Nette | Observatoire |
|---|---|---|
| **Réétalonnage daté 2016 / 2026** | absent — l'axe est spatial (embouteillé vs robinet), et « Deux balances » souligne au contraire la stabilité du seuil nitrates | cœur du projet : une mesure figée confrontée à deux grilles, `bascule_2016_2026` calculée par vue SQL |
| **Seuil le plus strict au monde** | absent | axe explicite : Danemark (somme 4 PFAS 2 ng/L), Allemagne (THM), US EPA, Californie PHG, `seuil_strict` + `pays_strict` |
| **Sélection des bulletins** | dernière valeur connue par paramètre sur 12 mois → profil synthétique sans date | bulletins **complets uniquement** (> 250 paramètres), un bulletin = une date = un verdict cohérent |
| **Limite de quantification** | avertissement qualitatif « non mesurée ≠ absente » | champs stockés `est_quantifie` et `lq` ; verdict à trois états conforme / non conforme / **indéterminé (LQ > seuil strict)** |
| **Effet cocktail, dose sommée** | absent ; le calculateur 50 ans somme des **minéraux** (résidu sec), pas des micropolluants | somme des polluants de synthèse en µg/L puis en µg/jour, cadre hazard index, MAF, CAG/MOET |
| **Statut perturbateur endocrinien** | section pédagogique, pas de statut par molécule | deux colonnes distinctes : statut **réglementaire** vs statut **scientifique** |
| **Grille de seuils** | ~60 paramètres, 6 familles, statique, synthèse partiellement issue d'un comparateur commercial ; sélénium périmé, six paramètres 2023 manquants | table sourcée paramètre par paramètre (codes REG / PFAS / PE / MIX / MET), extensible, adossée aux textes primaires |
| **Sortie complète** | tableau des paramètres du profil | **401 paramètres** exportables en CSV, bulletin officiel intégral repliable |
| **Persistance** | aucune — statique, sans état, réinterroge Hub'Eau à chaque visite | base DuckDB en étoile, ingestion idempotente, pensée pour ~10 000 communes |
| **Agrégat national** | impossible par construction | requête-thèse : part des bulletins complets concernés par une bascule |
| **Licence** | contenu propriétaire, usage commercial interdit sans accord ; open source promis, non effectif | vocation open data, chaque donnée réutilisable |
| **Position commerciale** | E.W.S. vend de l'osmose inverse ; le site recommande de la filtration | aucune recommandation d'équipement — outil de conscience |

### Là où il est devant nous

Deux choses, et il ne faut pas se les cacher. **La distribution** : couverture nationale immédiate, alertes email, PWA, carte, comparaison par rayon, mode nourrisson, moteur inversé par substance, quiz et glossaire. **Le périmètre** : paramètres radiologiques et corpus eaux embouteillées, deux angles morts de notre référentiel.

En clair : **il a l'audience et l'étendue, nous avons la méthode et la profondeur.** Les deux projets ne sont pas concurrents, ils sont complémentaires — mais seulement si la dépendance va dans le bon sens.

---

## 3. Ce qu'on peut lui transférer

Le principe directeur : **ne pas fusionner, s'interconnecter.** Compte tenu du conflit d'intérêts déclaré et de sa licence propriétaire, si nos données ouvertes se retrouvent absorbées dans un site dont le contenu est réservé et dont l'aval vend de l'osmose, l'Observatoire perd la neutralité qui est son seul actif réel pour lever des fonds. La bonne géométrie est : **l'Observatoire en amont, source citable et licenciée ; Mon Eau Nette en aval, réutilisateur parmi d'autres.**

### Brique 1 — le référentiel daté, en fichier ouvert *(immédiat, sans risque, fort effet)*

Un CSV et un JSON de `referentiel_seuils` avec, par paramètre : libellé, **`code_parametre` Hub'Eau**, famille, `seuil_2016`, `seuil_2026`, **`date_applicabilite`**, statut 2026 (limite / référence / vigilance), `seuil_strict`, `pays_strict`, codes sources.

Ce que ça lui apporte tout de suite : son sélénium corrigé, les six paramètres 2023 ajoutés, et surtout un badge que **personne d'autre n'a** — « en 2016, cette eau n'aurait pas été conforme ». Son site étant client-side, il l'intègre sans rien changer à son infrastructure.

### Brique 2 — les règles de verdict, en spécification écrite

Une note courte, plus les ~40 lignes de JS qui l'implémentent s'il les veut : le zéro qui n'est pas un zéro (`est_quantifie` / `lq`), le verdict à trois états dont l'**indéterminé**, la règle du bulletin complet et pourquoi elle est décisive, le test de bascule 2016 → 2026. C'est le cœur intellectuel, et c'est ce qui rend ses avertissements actuels **opérationnels** au lieu de déclaratifs.

### Brique 3 — le badge « bascule » en encart embarquable

L'intégration la plus légère pour lui : un encart autonome qui, à partir des lignes Hub'Eau d'une commune, affiche « X paramètre(s) conforme(s) en 2026 qui dépassaient la limite de 2016 » avec un lien vers la fiche Observatoire pour le détail. Il gagne une exclusivité, nous gagnons l'attribution et le renvoi. C'est là que la réciprocité est la plus propre.

### Brique 4 — la base en dump public et API *(plus tard, et c'est le vrai enjeu)*

Une fois `fetch_departement.py` en production : dumps JSON par commune, fichier DuckDB / SQLite téléchargeable, CSV des bulletins complets. Alors Pierre — et n'importe qui — consomme l'Observatoire au lieu de réinterroger Hub'Eau à la volée. C'est la position qu'on veut occuper : **une infrastructure, pas un site concurrent.** Et c'est exactement l'argument finançable : « N sites réutilisent notre référentiel ».

### Ce qu'il ne faut pas transférer

**Le gabarit de fiche HTML tel quel.** Il porte la voix éditoriale du livre, et tout son intérêt est d'être une lecture neutre sans recommandation. Déposé dans un site qui se conclut sur l'osmose, ce ton devient un argument de vente. On cède **les données** et **les règles**, on garde **la voix**.

**Le dossier `Sources/`.** Beaucoup de ces PDF sont des documents tiers. On partage `INDEX_SOURCES.md` — le catalogue avec les codes REG / PFAS / PE / MIX / MET et les liens — pas les fichiers.

### Conditions à écrire avant d'envoyer quoi que ce soit

Une page suffit, mais elle est indispensable.

**Licence.** Référentiel et données sous **ODbL 1.0** (standard des bases de données ouvertes en France, attendu par data.gouv.fr) ou CC BY-SA 4.0 — dans les deux cas avec **partage à l'identique**, pour que les améliorations reviennent. CC BY 4.0 seulement si la diffusion maximale prime sur la réciprocité. Noter l'asymétrie : son contenu est aujourd'hui propriétaire, donc demander au minimum la réciprocité sur les dérivés du référentiel.

**Attribution visible** : « Référentiel : Observatoire de la potabilité réglementaire — Éditions Mytae », avec lien, sur toute page qui l'utilise.

**Clause de non-caution**, non négociable au vu du conflit d'intérêts déclaré : mention explicite, affichée partout où le référentiel apparaît, que l'Observatoire ne recommande ni ne cautionne aucun équipement de traitement ni aucun fournisseur.

**Pas de modification de seuil sans source primaire** : tout seuil ajouté ou modifié porte sa référence ; aucune valeur issue d'un comparateur commercial dans un fichier portant le nom de l'Observatoire.

**Traçabilité conservée** : chaque seuil garde son code source pour qu'un lecteur puisse vérifier.

### Ce qu'on demande en échange — pour que ce soit un échange

Son **corpus eaux embouteillées** (35 sources Cristaline, tableaux plates et gazeuses, résidus secs), son **jeu de paramètres radiologiques**, son **protocole de terrain au conductimètre**. Et son savoir-faire de diffusion : PWA, alertes email, carte, formats pédagogiques.

### Le risque, dit clairement

Pierre est seul, avec un entonnoir commercial en aval. Notre actif est la neutralité. Collaborer est juste, mais **le sens de la dépendance décide de tout**. S'il intègre le référentiel et que la relation tourne mal, nous ne perdons rien : le référentiel est publié ouvertement de toute façon. Si nos fiches vivent à l'intérieur de son site, nous perdons le projet.

---

## 4. Préalables de notre côté

1. **Corriger `plomb seuil_2026`** : la valeur en vigueur aujourd'hui est **10 µg/L**, les 5 µg/L s'appliquant au 1er janvier 2036. Même chose pour le chrome total (50 aujourd'hui, 25 en 2036).
2. **Ajouter une colonne `date_applicabilite`** à `referentiel_seuils` — sans elle, notre grille « 2026 » est fausse sur au moins deux paramètres, et c'est justement le reproche que nous adressons aux grilles statiques.
3. **Compléter les `code_parametre` Hub'Eau** et la table d'alias : c'est le préalable au partage comme à la montée en charge départementale.
4. **Ajouter les paramètres manquants** repérés par comparaison : chrome hexavalent (6 µg/L depuis 2023), chlorates, et le bloc radiologique.

---

### Sources

Site analysé : [mon-eau-nette.pages.dev](https://mon-eau-nette.pages.dev/) — pages `index`, `ma-ville`, `annexe`, `substances`, `moteur-substances`, `deux-balances`, `pourquoi-pas-les-memes`, `calcul-50ans`, `diagnostic`, `preuves`, `faq-depassement`, `carte-france`, `tableau-bord`, `a-propos`, `mentions-legales`, `rejoindre`, `plan-du-site`, `sitemap.xml`.

Réglementation : [Arrêté du 30 décembre 2022 modifiant l'arrêté du 11 janvier 2007 (limites et références de qualité)](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000046849403) ; [Arrêté du 11 janvier 2007 consolidé](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000465574/) ; [ARS PACA — transposition de la directive (UE) 2020/2184, dates d'application](https://www.paca.ars.sante.fr/media/121455/download) ; [Instruction n° DGS/EA4/2026/54 du 16 avril 2026 relative au plomb dans l'eau de consommation](https://bulletins-officiels.social.gouv.fr/instruction-ndeg-dgsea4202654-du-16-avril-2026-relative-la-presence-de-plomb-dans-leau-destinee-la-consommation-humaine-hors-eaux-conditionnees-controle-du-plomb-hydrique-par-les-personnes-responsables-de-la-distribution-deau-dans-les-reseaux).

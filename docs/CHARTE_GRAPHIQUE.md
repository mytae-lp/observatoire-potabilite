# Charte graphique — Observatoire de la potabilité réglementaire

**Version 2, 14 août 2026.** Fichier versionné : une décision de forme est une
décision éditoriale, git en tient le journal daté — même logique que
`sortie/CONSIGNE_REDACTION.md` et `docs/CONSIGNE_AUDIT_FORME.md`.

Source unique de la forme : **`site/gabarits/observatoire.css`**, servie par la
vitrine et inlinée par la fiche autonome.

> **Statut.** La v1 de ce document (même jour, matin) *décrivait* la feuille
> existante et laissait D1→D8 ouvertes. Les maquettes produites dans
> `Charte_graphique_v2/` les tranchent toutes et en ajoutent quatre. **Les
> décisions ci-dessous sont prises ; leur application dans la feuille est en
> cours** — suivi dans `Charte_graphique_v2/CONSIGNE_IMPLEMENTATION_FORME.md`.
>
> Tout chiffre de ce document a été **mesuré**, jamais repris sur parole : les
> contrastes des deux palettes ont été recalculés sur les 54 couples qui
> portent du sens, l'inventaire de la v1 a été relevé sur la feuille elle-même.

---

## 1. Ce que la méthode impose — non négociable

Ces règles ne relèvent pas du goût. Une refonte visuelle ne peut pas les
contourner, et c'est la seule section qu'il faut faire lire à quelqu'un qui
travaille la forme sans connaître le fond.

| Contrainte | Origine |
|---|---|
| **Cinq couleurs de sens, aux rôles fixes** : vert conforme, rouge dépassement *à la date*, violet bascule, gris indéterminé, ambre attention | §2.4, §2.10 |
| **Le gris est un troisième état de verdict, pas une absence de couleur.** Aussi lisible que le vert et le rouge | §2.4, §8bis obl. 3 |
| **« Non documentée » est une catégorie visible**, ni verte ni rouge | §8bis obl. 4 |
| **Une valeur `a_verifier` est signalée** partout où elle sort | §2.7, §8bis obl. 8 |
| **Un dénominateur accompagne tout verdict** — ce n'est pas une mention secondaire, la forme doit lui laisser une place | §2.8, §8bis obl. 1 |
| **La traçabilité est sur chaque écran** : version de référentiel, date de calcul | §8bis obl. 9 |
| **Aucune recommandation de produit ni de procédé**, nulle part, y compris dans un libellé d'interface | §2.2, §8bis obl. 10 |

Conséquences pratiques : on peut changer la teinte d'une des cinq couleurs,
**jamais son rôle**, jamais en fusionner deux, jamais en retirer une. Réduire la
palette « pour faire plus sobre » casserait la règle des trois états. Et ces
contraintes valent **dans les deux thèmes** (D12).

---

## 2. Les décisions

### D1 — Aucune couleur hors jetons

*Décidé le 14 août 2026.* Toute couleur vit dans `:root`. Aucune valeur
littérale dans la feuille.

**Raison, mesurée sur la v1 :** 17 jetons déclarés, mais **50 couleurs écrites
en dur, 122 emplois** — dont `#0B3B57` recopié deux fois alors que `--eau-deep`
existait pour ça. C'est ce qui a produit les sept échecs de contraste de la v1 :
non pas un mauvais choix esthétique, mais l'impossibilité de voir les 43 paires
d'un coup d'œil. La v2 déclare **122 jetons**.

### D2 — Échelle typographique : 7 crans

`13 / 15 / 17 / 19 / 23 / 30 / 40`, plus `--t-display` et `--t-chiffre` en
`clamp()`. **Corps à 17 px. Plancher absolu 13 px. Aucun demi-pixel.**

**Raison :** la v1 employait **22 tailles distinctes pour 116 emplois**, dont
cinq demi-pixels ; ses cinq tailles les plus fréquentes tenaient dans un écart
d'un pixel et demi. Piège connu : `small` et `.mono` en `em` réintroduisent des
demi-pixels — ils reviennent sur l'échelle.

### D3 — Espacement : base 4, neuf crans

`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96`.
**Raison :** 23 valeurs distinctes pour 237 emplois en v1, sans rythme.

### D4 — Contraste : zéro échec AA

`--vert #24734A` · `--ambre #8E5A0B` · `--eau #0B6A73`, plus `--ink-faint
#5A6E80`. **Rôles inchangés, seule la luminosité descend.**

**Vérifié le 14 août 2026** sur 27 couples par thème : **0 échec en clair,
0 échec en sombre.** La v1 en comptait 7, tous issus de deux jetons.

### D5 — Une seule largeur de lecture

`--mesure: 66ch`. **Raison :** la v1 en avait cinq — 64, 72, 74, 78, 80ch — pour
une seule notion.

### D6 — Une largeur par type de page

`--l-prose 760px` · `--l-standard 1100px` · `--l-large 1440px`. Le `.wrap` à
1000 px disparaît. **Raison :** 1000 px servait aussi bien à la prose d'une page
de méthode qu'au tableau de 4 924 communes — étroit pour l'un, large pour
l'autre.

### D7 — Deux polices propres

**Newsreader** (titres, chiffres, citations) et **Inter** (texte, données,
`tabular-nums`), sous-ensemble français, variables : 34 + 41 + 46 ko,
`font-display: swap`. La pile mono est conservée.

**Raison :** la v1 ne chargeait aucune police. C'était robuste et sans requête —
et c'est ce qui faisait qu'un lecteur ne reconnaissait pas le site. Contrepartie
acceptée : trois requêtes et un risque de décalage au chargement, borné par
`swap`.

### D8 — Une seule pastille

`--r-pastille: 999px`. Quatre rayons au total : `6 / 10 / 16` plus la pastille.
**Raison :** la v1 écrivait `99px` (×8) **et** `999px` (×7) pour la même forme,
parmi 12 rayons distincts.

### D9 — La zone d'approche à 85 %

*Décidé par Yannick le 14 août 2026.*

| Rapport mesure / seuil | État | Rendu |
|---|---|---|
| non quantifié, LQ sous le seuil | `sous_lq` | barre grise à la position de la LQ |
| non quantifié, LQ au-dessus du seuil | `indetermine` | barre hachurée grise |
| < 0,85 | `conforme` | dégradé vert |
| **0,85 à < 1,00** | **`proche`** | **le dégradé vire à l'ambre** |
| ≥ 1,00 | `depassement` | barre pleine rouge, « × N » |

**Raison :** une eau à 99 % d'une limite est conforme, mais entre l'incertitude
de mesure et la limite de quantification du laboratoire, ce dernier pour cent ne
veut plus rien dire. La barre change donc de couleur **avant** la limite, pas au
moment où elle est franchie. Un trait clair marque les 85 %, que la barre l'ait
atteint ou non.

> **Garde-fou, à ne jamais lever.** `proche` est un état **d'affichage**, pas un
> verdict. Il n'apparaît ni dans `analyses_figees`, ni dans `verdicts_figes`, ni
> dans un texte de conclusion, ni dans une métadonnée, ni dans un export. **Le
> projet a trois états de verdict et n'en aura pas quatre** (§2.4). Cette garde
> doit survivre à la session qui l'a écrite : elle est ici pour ça.

Mise en œuvre : `sortie/indicateurs.py:111`, `_etat()`. Ce fichier **n'est pas
dans l'empreinte moteur** — le chantier peut se mener pendant une campagne.

### D10 — Deux barres quand il existe deux repères

Barre pleine = la **limite opposable**. Barre fine (`.jg--repere`) = le
**repère** — nourrissons, ou le plus strict identifié. Le second n'est jamais
une non-conformité et son libellé le dit.

**Raison :** c'est le §2.4 rendu visible. Tramayes est à 23 % de la limite
française de sous-produits de chloration et à 92 % du repère le plus strict :
deux faits vrais que la v1 ne pouvait pas montrer ensemble. La donnée existe
déjà (`reperes_nourrissons()`, `indicateurs.py:381`).

### D11 — Aucune liste tronquée

Six éléments visibles, le reste dans un `<details class="plus">` dont le résumé
**annonce le compte exact** : « Afficher les 21 autres substances de ce
registre ».

**Raison :** la v1 écrivait « et 15 autre(s) » **sans donner accès aux 15**.
C'est un défaut de forme qui touche au fond : un observatoire qui tronque sans
le dire demande d'être cru sur parole. La troncature venait de
`decomposition_danger(maxi=6)` — le paramètre passe à `None`, le repli devient
l'affaire du gabarit.

### D12 — Deux thèmes, un seul sens

*Ajouté à la charte le 14 août 2026, décision portée par les maquettes.*

Le site suit désormais le thème du système (`color-scheme: light dark`) et
accepte un choix explicite (`[data-theme="clair"|"sombre"]`). **Les cinq
couleurs de sens ont une variante sombre**, et leur rôle est identique dans les
deux.

**Vérifié :** 27 couples par thème, **0 échec AA des deux côtés**. Une couleur
d'état qui passerait en clair et échouerait en sombre serait un défaut de
méthode, pas de goût — le §2.4 ne dépend pas de l'heure qu'il est.

---

## 3. Les jetons de sens, dans les deux thèmes

| Rôle | Clair | Sombre |
|---|---|---|
| conforme | `#24734A` sur `#E9F4EE` | `#6FCB96` sur `#16301F` |
| dépassement à la date | `#B23A2E` sur `#F8E7E4` | `#F0897A` sur `#33191A` |
| bascule | `#63469B` sur `#EEE9F7` | `#BCA4F0` sur `#241C3A` |
| indéterminé · non documenté | `#55636F` sur `#E7EBEF` | `#A6B8C6` sur `#1E2A35` |
| attention | `#8E5A0B` sur `#FAEFD9` | `#E9A93E` sur `#33260F` |

Marque et surfaces : `--eau #0B6A73` / `#4FC3CC`, `--eau-deep #08344C`,
`--paper #F2F5F7` / `#0C1620`, `--card #FFFFFF` / `#141F2B`.

Le détail complet — filets, encres secondaires, ombres — vit dans `:root`, qui
fait foi. **Ce tableau est un rappel, pas la source.**

---

## 4. Ce que la v2 conserve de la v1

Cette section est obligatoire : un audit qui ne protège rien pousse au
remaniement gratuit.

1. **Le parti plat.** Une ombre douce, des filets fins, la couleur qui porte le
   sens plutôt que le relief. Un observatoire, pas une application.
2. **Le focus visible** — `outline` de 3 px, avec un décalage.
3. **`prefers-reduced-motion`** respecté.
4. **La feuille unique** partagée par la vitrine et la fiche autonome. Une
   seule source pour `observatoire.css`, `corps_fiche.html` et `fiche.js` : c'est
   ce qui empêche les deux sorties de diverger, et l'audit du 13 août le range
   explicitement dans ce qu'il ne faut pas toucher.

---

## 5. Comment modifier la charte

1. la décision se prend et **s'écrit ici d'abord**, datée, avec sa raison ;
2. elle s'applique dans `site/gabarits/observatoire.css`, **jamais** dans
   `site/public/assets/`, qui est un produit dérivé hors git ;
3. on remesure — contraste dans les deux thèmes, débordement de 320 à 2560 px,
   lisibilité sans JavaScript, échelle typographique respectée (§7 de la
   consigne d'implémentation) ;
4. on reconstruit, pour que l'empreinte des feuilles change et que les caches se
   renouvellent. **Sans cette reconstruction, les navigateurs servent l'ancienne
   feuille sur le nouveau balisage, et le site paraît cassé alors que le code est
   bon.**

**Ce fichier ne fait pas partie de l'empreinte moteur** (`figer.py`,
`build_db.py`, `common.py`) : le travail de forme n'a jamais d'effet sur un
figeage, et peut se mener pendant une campagne de collecte.

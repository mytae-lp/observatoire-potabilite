# Licences

Ce dépôt contient trois types de contenus, sous trois régimes distincts.

## 1. Les données brutes — Licence Ouverte / Open Licence

Les résultats d'analyse proviennent du **système d'information SISE-Eaux**
(ministère chargé de la santé, agences régionales de santé), diffusés via
l'**API Hub'Eau** (Office français de la biodiversité, BRGM) et le portail
Orobnat.

Ces données sont publiées sous **Licence Ouverte 2.0** (Etalab). Leur
réutilisation est libre, sous réserve de mentionner la paternité :

> Source : Hub'Eau — qualité de l'eau potable (SISE-Eaux, ministère chargé
> de la santé). https://hubeau.eaufrance.fr/

Ces données ne sont pas redistribuées dans ce dépôt : `data/eau.duckdb`
n'est pas versionné, il se reconstruit depuis l'API.

## 2. Le référentiel et les résultats calculés — ODbL 1.0

Deux ensembles, et ils forment **une seule base** au sens de l'ODbL.

**Le référentiel.** `referentiel/referentiel_seuils.csv` et
`referentiel/alias_parametres.csv` rassemblent, pour chaque paramètre, la
limite applicable en 2016, celle applicable en 2026, les valeurs à
application différée avec leur date, la valeur la plus protectrice
identifiée dans le monde, et le statut de perturbateur endocrinien dans les
deux registres réglementaire et scientifique — chaque ligne étant rattachée
à ses sources.

**Les résultats calculés**, publiés sur la vitrine sous `donnees/` :

| fichier | ce qu'il porte |
|---|---|
| `bulletins.csv` | un bulletin par ligne : verdicts, couverture, effort de recherche, sommes |
| `verdicts_<dept>.csv.gz` | le détail paramètre par paramètre, découpé par département |
| `referentiel_seuils.csv` | le référentiel daté lui-même |

Ces fichiers **ne sont pas les mesures brutes** : ce sont les mesures
publiques rapprochées du référentiel daté, c'est-à-dire le travail propre du
projet. Ils étaient publiés sans être nommés ici, ce qui laissait un
réutilisateur de bonne foi sans rien à respecter — corrigé le 18 août 2026.

L'ensemble est mis à disposition sous **Open Database License (ODbL)
version 1.0**.

Texte intégral : https://opendatacommons.org/licenses/odbl/1-0/

Cela implique trois obligations pour toute réutilisation :

- **attribution** — citer l'Observatoire de la potabilité réglementaire
  (Éditions Mytae) comme source de la base ;
- **partage à l'identique** — si vous distribuez une version modifiée ou
  enrichie du référentiel, elle doit l'être sous ODbL également ;
- **maintien de l'ouverture** — si vous distribuez un produit fondé sur
  cette base sous une forme fermée, vous devez rendre disponible une version
  de la base sous ODbL.

## 2 bis. Comment citer l'Observatoire

L'ODbL demande une mention « **raisonnablement propre à faire savoir** » que
le contenu vient de la base et qu'elle est disponible sous ODbL (§4.3). Elle
laisse au producteur le soin d'en écrire la forme : la voici.

**Elle est due dès l'usage public**, et c'est le point qu'on manque souvent :
pas seulement quand vous redistribuez nos fichiers, mais **dès que vous
publiez quoi que ce soit qui s'appuie dessus** — une carte, un tableau, un
article chiffré, une application. L'ODbL appelle cela un *Produced Work*.

### La mention courte — celle qui doit voyager partout

> Contient des informations de l'**Observatoire de la potabilité
> réglementaire** (Éditions Mytae), mises à disposition
> [ici](https://eau.yannick-mytae.fr/) sous
> [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).

En texte seul, quand les liens sont impossibles :

```
Contient des informations de l'Observatoire de la potabilité réglementaire
(Éditions Mytae), https://eau.yannick-mytae.fr/, sous Open Database License
(ODbL) 1.0 — https://opendatacommons.org/licenses/odbl/1-0/
```

**Le lien pointe vers l'accueil**, et non vers une page intérieure : c'est là
que se trouvent la méthode, les limites et la traçabilité sans lesquelles un
chiffre de ce projet ne veut rien dire. Nous n'interdisons à personne de lier
la page de son choix — nous disons seulement où l'attribution renvoie.

### La mention longue — quand la place le permet

Sur une page de crédits, un pied de site, un ours, une note de bas de page :

> Données : **Observatoire de la potabilité réglementaire** —
> <https://eau.yannick-mytae.fr/> — sous ODbL 1.0.
> Un projet des **Éditions Mytae** — <https://editions.mytae.fr/> —
> porté par **Yannick Mytae** — <https://yannick-mytae.fr/>.
> Mesures d'origine : SISE-Eaux (ministère chargé de la santé) via Hub'Eau,
> Licence Ouverte 2.0.

**La mention courte suffit toujours.** La longue est un confort, pas une
condition supplémentaire — une obligation trop lourde ne serait pas
respectée, et une mention respectée vaut mieux qu'une mention exigeante.

### Ce que la mention ne doit pas laisser croire

Voir le §5 : citer l'Observatoire **n'est pas être approuvé par lui**. La
mention dit d'où vient la donnée, jamais que nous cautionnons ce qui en est
tiré.

## 3. Le code — MIT

Les scripts du répertoire `src/` et de `sortie/` sont sous **licence MIT**.

```
Copyright (c) 2026 Éditions Mytae

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 4. Les documents de `docs/`

Les notes méthodologiques et le plan de projet sont sous
**CC BY-SA 4.0** — réutilisables avec attribution et partage à l'identique.

## 5. Attribution n'est pas caution

Une réutilisation conforme aux licences ci-dessus **n'engage pas
l'Observatoire** sur les conclusions que le réutilisateur en tire. Citer ce
référentiel comme source ne vaut pas approbation d'une analyse, d'une
publication ou d'un produit.

En particulier, l'Observatoire ne recommande aucun équipement, aucun
traitement domestique de l'eau et aucun produit. Une réutilisation qui
associerait ce référentiel à une recommandation commerciale de ce type le
ferait sans l'accord de ses auteurs et devrait le dire explicitement.

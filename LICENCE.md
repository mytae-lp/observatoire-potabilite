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

## 2. Le référentiel de seuils — ODbL 1.0

Le fichier `referentiel/referentiel_seuils.csv` et le fichier
`referentiel/alias_parametres.csv` constituent une base de données originale
produite par l'Observatoire : ils rassemblent, pour chaque paramètre, la
limite applicable en 2016, celle applicable en 2026, les valeurs à
application différée avec leur date, la valeur la plus protectrice
identifiée dans le monde, et le statut de perturbateur endocrinien dans les
deux registres réglementaire et scientifique — chaque ligne étant rattachée
à ses sources.

Ce référentiel est mis à disposition sous **Open Database License (ODbL)
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

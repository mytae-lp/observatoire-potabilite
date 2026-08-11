# Consigne de qualification d'un acte préfectoral — brief type pour un agent de fond

Version du 11 août 2026. **Fichier versionné : ce qu'on demande à un agent est
une décision de méthode, git en tient le journal daté.**

Écrite avant le premier lot, à partir de la reconnaissance du Tarn
(`docs/CHANTIERS.md` §C10, mise à jour du 11 août). Elle n'a donc pas encore la
qualité de `docs/CONSIGNE_SOURCAGE.md`, dont chaque règle vient d'une erreur
réellement commise. **Elle se corrigera sur les trois premiers actes qualifiés,
et c'est prévu.**

Ce document ne remplace pas `docs/CONSIGNE_SOURCAGE.md` : son **§0 s'applique
ici mot pour mot** et n'est pas recopié.

---

## 0. Ce qui change par rapport au sourçage de substance

| | sourçage d'une substance | qualification d'un acte |
|---|---|---|
| la matière | à chercher sur le web | **fournie dans le dossier** |
| l'agent va-t-il sur internet | oui, c'est le travail | **non, jamais** |
| la sortie | une fiche et une ligne de référentiel | **un objet à schéma fermé** |
| l'échec acceptable | « aucune valeur n'existe, démontré » | **« indéterminé », et c'est un résultat** |

La règle qui découle de la deuxième ligne est la plus importante de ce fichier :

> **Le fait est dans l'acte, ou il n'est nulle part.** L'agent ne cherche pas
> ailleurs ce que le texte ne dit pas. Un arrêté qui ne nomme pas sa commune ne
> se complète pas par une recherche : il sort avec un périmètre vide.

Le sourçage juridique — articles du code de la santé publique, durée maximale
d'une dérogation, paramètres exclus — est un **lot séparé**, confié à un agent
`opus` sur `docs/CONSIGNE_SOURCAGE.md`. Il ne se fait pas en même temps que la
qualification, sans quoi l'agent complète l'acte avec du droit qu'il vient de
lire, et on ne sait plus ce qui vient du texte.

---

## 1. Le dossier de faits fourni à l'agent

Fabriqué entièrement par `src/raa_lot.py --dossiers`, sans qu'aucun modèle n'y
touche. Il contient, et rien de plus :

1. **le texte intégral de l'acte seul** — découpé sur les pages que son
   sommaire annonce, jamais le recueil entier ;
2. **sa ligne de sommaire littérale** — identifiant, intitulé, longueur ;
3. **le service émetteur** tel qu'écrit dans le recueil ;
4. **la référence du recueil, sa date de publication et son adresse** ;
5. **la liste des communes du département présentes en base**, avec leurs codes
   INSEE — pour que l'agent rattache sans inventer ;
6. **la liste fermée des types**, recopiée dans le brief.

Ce que le dossier ne contient jamais : les autres actes du recueil, les données
de mesures, les seuils du référentiel. Un acte se qualifie sur lui-même.

---

## 2. Les règles absolues, à recopier dans chaque brief

1. **N'écris aucune date, aucun nombre, aucun nom de commune qui ne figure pas
   dans le texte fourni.** Le contrôle d'intégration les cherche littéralement
   et bloque sinon. C'est le §2.7 transposé du chiffre au document.
2. **Ne calcule jamais une date de fin.** Si l'acte donne une durée sans date de
   fin, tu rends la durée telle qu'elle est écrite et tu laisses la date vide.
   Une date de fin déduite est une date fausse (§2.5).
3. **Ne conclus jamais sur ce que l'acte ne dit pas.** Une restriction sans acte
   de levée n'est pas « toujours en vigueur » : elle est **sans levée connue**.
   Trois états, jamais deux (§2.4).
4. **Ne qualifie personne.** On interroge la norme, jamais le préfet, l'ARS, la
   collectivité ou l'exploitant (§2.1). Une dérogation est légale et motivée :
   le travail est de dire qu'elle existe, sur quoi et combien de temps.
5. **N'écris aucune phrase sanitaire.** Ni « dangereux », ni « sans risque », ni
   « rassurant ». Tu restitues ce que l'acte prescrit, pas ce qu'il faut en
   penser (§2.2).
6. **Ne lance aucun sous-agent, ne consulte aucune page web.**
7. **Dans le doute, `indetermine`.** Le faux positif coûte plus cher que le faux
   négatif (§2.13). Un acte mal compris est un acte à relire, pas un acte à
   deviner.

---

## 3. Le piège d'identité, nommé — quatre confusions à refuser

Elles sont l'équivalent, pour ce chantier, du « dichloroéthane-1,1 contre 1,2 »
du sourçage. Chacune inverse ou fausse le sens du fait.

| à ne pas confondre | avec | pourquoi c'est grave |
|---|---|---|
| **restriction d'usage** (sécheresse, arrosage, irrigation) | **restriction de consommation** | la première ne dit rien de la qualité de l'eau bue. C'est le bruit dominant des recueils : l'acte sondé porte 91 fois « restriction » et zéro fois « consommation humaine » |
| **dérogation** (autorise à distribuer au-dessus d'une limite) | **restriction** (interdit de boire) | ce sont deux mécanismes **inverses**. Les confondre retourne le fait |
| **limite de qualité** (opposable) | **référence de qualité** ou **valeur indicative** | erreur déjà commise une fois dans le projet, sur le chlorothalonil (§2.7) |
| **abrogation d'un arrêté** | **levée d'une restriction** | un arrêté peut être abrogé parce qu'il est remplacé, sans que la restriction cesse |

---

## 4. Ce que l'agent rend — schéma fermé

Un objet, dans le fichier de réponse nommé par le brief. Un fichier par agent,
jamais deux agents sur le même fichier.

- **`type`** — une valeur de la liste fermée, ou `indetermine`.
- **`date_signature`**, **`date_debut`**, **`date_fin`** — au format ISO, ou
  vides. Vide est une réponse valable et fréquente.
- **`duree_ecrite`** — la durée telle que l'acte la formule, littéralement, si
  elle y figure.
- **`perimetre`** — le libellé du périmètre tel qu'écrit : commune, unité de
  distribution, réseau.
- **`codes_insee`** — uniquement des codes de la liste fournie, séparés par une
  barre verticale.
- **`parametre`**, **`valeur`**, **`unite`** — pour une dérogation seulement, et
  seulement si les trois sont écrits.
- **`population_visee`** — si l'acte restreint pour une partie de la population
  seulement (nourrissons, femmes enceintes), son libellé littéral.
- **`motif`** — la motivation telle que l'acte l'énonce, en une phrase reprise
  du texte.
- **`citations`** — les extraits littéraux qui fondent chacun des champs
  ci-dessus. **C'est le champ qui rend le contrôle possible** : sans lui, rien
  n'est vérifiable, et l'intégration refuse la réponse.
- **`doute`** — ce que l'agent n'a pas su trancher, en clair. Un `doute` rempli
  n'est pas un échec : c'est ce qui envoie l'acte en relecture humaine plutôt
  qu'au dénombrement.

---

## 5. Ce qui bloque à l'intégration

`src/raa_lot.py --verifier` ne modifie rien et dit ce qui passerait. Les
contrôles, qui **réutilisent** les fonctions déjà écrites plutôt que d'en
recopier une seconde version :

1. un `type` hors de la liste fermée ;
2. **une date ou un nombre absent du texte de l'acte** ;
3. un code INSEE absent de la liste fournie ;
4. une dérogation sans paramètre, sans valeur ou sans unité — elle redescend en
   `autre_eau_consommation` ;
5. une citation qui ne se retrouve pas littéralement dans le texte ;
6. un qualificatif sanitaire ou une formulation prescriptive (§2.2) ;
7. une affirmation d'absence — « aucune autre commune n'est concernée » (§2.4).

Un blocage n'est pas une régression : c'est le contrôle qui fonctionne.

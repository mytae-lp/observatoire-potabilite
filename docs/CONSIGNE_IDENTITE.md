# Consigne de sourçage d'IDENTITÉ — brief type pour un agent de fond

Version du 15 août 2026. **Fichier versionné : ce qu'on demande à un agent est
une décision de méthode, git en tient le journal daté.**

Sœur de `docs/CONSIGNE_SOURCAGE.md`, et à ne pas confondre avec elle.

| | `CONSIGNE_SOURCAGE.md` | **ce fichier** |
|---|---|---|
| la question | *quelle valeur s'applique à cette substance ?* | *qu'est-ce que cette substance EST ?* |
| ce qui en sort | une ligne de `referentiel/referentiel_seuils.csv` | une ligne de `referentiel/identite_substances.csv` |
| ce que ça déplace | un **verdict** de conformité | **rien** — aucun calcul, aucun figeage |

**Cette asymétrie commande tout le reste.** Une identité fausse trompe un
lecteur ; elle ne fabrique pas de non-conformité. C'est moins grave, et cela ne
rend pas la règle plus souple : cela déplace seulement le point d'attention, de
la valeur vers **la date et l'attribution**.

Écrite après un échantillon de cinq substances sourcées le 15 août 2026 —
chlorothalonil R471811, ESA métolachlore, sélénium, acrylamide, atrazine.
Quatre abouties, une non établie. Chaque règle ci-dessous vient de cet
échantillon, et les cas sont cités.

---

## 1. Ce qu'on cherche, et ce qu'on ne cherche pas

**On cherche l'histoire et l'usage**, pas le seuil : *« fongicide dont
l'approbation européenne a pris fin le 30 avril 2019 »*, *« oligo-élément
essentiel présent dans la croûte terrestre »*, *« métabolite du S-métolachlore »*.

Quatre champs, et rien d'autre :

| champ | ce qu'on y met | exemple tiré de l'échantillon |
|---|---|---|
| `quoi` | ce que la substance EST, une phrase | « Métabolite issu de la dégradation dans les sols du chlorothalonil. » |
| `usage` | à quoi sert la molécule mère, ou elle-même | « Le S-métolachlore est une substance active herbicide. » |
| `molecule_mere` | pour un métabolite, vide sinon | « S-métolachlore » |
| `statut_autorisation` | l'état du droit **avec sa date** | « Approbation européenne prise fin le 30 avril 2019, par non-renouvellement (règlement (UE) 2019/677). » |

### La longueur, et où vit l'attribution

**Une à deux phrases par champ, environ 150 caractères, 250 au grand maximum.**
Ces phrases s'affichent en tête de la page d'un paramètre, avant tout le reste :
elles doivent se lire d'un trait.

**L'attribution vit dans la colonne `sources`, jamais dans la phrase.** La page
affiche déjà « Sources : REG-04. Fiabilité : verifie » sous le paragraphe.
Écrire *« … selon la fiche OMS “Aluminium” de la section 12 des directives de
qualité pour l'eau de boisson (4e édition), dont la date d'évaluation est
2009 »* dit deux fois la même chose et double la longueur.

*Cas réel, lot « métaux » du 15 août 2026 :* dix lignes justes, sourcées,
contrôlées sans un bloquant — et illisibles, chaque phrase portant son appareil
bibliographique. **Le défaut était dans la consigne, qui ne disait rien de la
longueur.** Corrigé le jour même.

Une exception, et une seule : **la date d'évaluation d'une fiche se dit** quand
elle est ancienne, parce qu'elle change ce que la phrase vaut — une fiche OMS de
1993 et une de 2020 ne disent pas l'état des connaissances au même moment. La
forme courte suffit : « (fiche OMS, 1993) ».

**Aucune valeur de seuil n'entre ici.** Ni limite, ni référence, ni valeur
guide, ni LQ. Elles ont leur fichier, leur consigne et leur contrôle. Le
contrôle d'intégration **bloque** toute valeur suivie d'une unité de
concentration — `0,1 µg/L`, `2 mg/l` — et ce blocage n'a pas d'exception.

**Aucun qualificatif sanitaire.** Ni « dangereux », ni « toxique », ni
« sans danger », ni « inoffensif ». On rapporte ce que la source dit, avec le
niveau de preuve qu'elle revendique. *Une substance sans seuil n'est pas
« sans danger » : elle est indéterminée.*

---

## 2. Les cinq règles absolues

1. **N'écris jamais une identité que tu n'as pas lue** dans une source ouverte
   par toi. Pas de mémoire, pas de connaissance générale, pas de « c'est un
   herbicide bien connu ». Sans source : **pas de ligne**, et on le dit.
   *Cas de l'échantillon :* l'atrazine n'a produit **aucune ligne**. Le
   référentiel porte pourtant « interdite depuis 2004 » — mais `REG-07` n'a pas
   de fichier sur le disque, et trois adresses ont été tentées sans obtenir le
   texte. Une identité que tout le monde croit connaître est le cas le plus
   dangereux, parce que personne ne songe à la vérifier.

2. **La source doit couvrir CETTE substance**, identifiée par son code SANDRE
   ou son numéro CAS. Une source sur la substance d'à côté n'est pas une source.
   *Cas de l'échantillon :* l'ESA métolachlore est **CGA 354743** ; le corpus
   contient aussi **CGA 354742**, autre paramètre. Un chiffre d'écart.
   *Cas écarté :* `REG-11` décrit les produits de traitement en général et ne
   nomme pas l'acrylamide — il n'a donc **pas** été mis en source de sa ligne,
   bien qu'il en éclaire le contexte.

3. **Un statut d'autorisation sans sa date est faux.** Comme un seuil (§2.5).
   « Interdite » ne s'écrit pas : on écrit ce que le texte dit, avec sa date et
   son numéro. Distinguer l'échelon **européen** (approbation, non-renouvellement)
   de l'échelon **français** (retrait des AMM par l'Anses), qui ne tombent pas le
   même jour. *Cas :* chlorothalonil — approbation européenne close le
   30 avril 2019, retrait des 25 AMM françaises **fin novembre 2019**.

4. **Une procédure en cours n'est pas une décision.** Si le texte dit que la
   réévaluation est en cours, on écrit cela, et **rien de plus**.
   *Cas :* l'avis ANSES du 30/09/2022 note que la réévaluation européenne du
   S-métolachlore était en cours ; sa ligne ne porte donc aucune interdiction.

5. **Une interdiction d'usage n'est pas une absence dans l'eau.** Les
   métabolites d'une substance retirée en 2004 se mesurent encore aujourd'hui.
   Ne jamais laisser entendre l'inverse.

---

## 3. Les sources, et l'ordre dans lequel les lire

**Le fonds local d'abord** —
`C:\Users\ymyta\Documents\EDITIONS MYTAE\2 - Water\Data - Analyse de la qualité de l'eau en France\Sources\`
— il est petit (une quarantaine de fichiers), donc on en fait vite le tour,
mais ce qu'il contient est déjà indexé et déjà lu.

| pour… | lire |
|---|---|
| métabolites de pesticides | `MET-01` (chlorothalonil), `MET-06` (ESA métolachlore), `MET-05` si le tableur est retrouvé |
| minéraux, métaux, physico-chimie | `REG-04`, les directives OMS — **une fiche par substance**, section « 12. Chemical fact sheets » |
| résidus de traitement, monomères | `REG-01`, annexe I partie B et ses notes |
| perturbation endocrinienne | `PE-01` à `PE-09` — **statut réglementaire et listes de suspicion ne se confondent jamais** (§2.15) |

**Puis le réseau**, et seulement `WebSearch` / `WebFetch` — ni curl, ni wget, ni
python pour télécharger une URL (§3.1).

**État des accès, mesuré le 15 août 2026 :**

- **EUR-Lex ne rend rien** par l'outil web, sous trois formes d'URL
  (`legal-content/HTML`, `eli/.../oj/eng`, `legislation.gov.uk` en miroir).
  Ne pas y perdre de temps ; chercher le texte ailleurs ou conclure « non établi » ;
- **les PDF de l'ANSES arrivent en binaire** par `WebFetch`, qui les enregistre
  sur le disque et en donne le chemin. **Les relire avec `pypdf`**, pas à travers
  l'outil web ;
- **Légifrance répond**, mais lire avant de conclure : l'avis
  `JORFTEXT000000824347`, que la recherche donnait pour couvrir les
  non-inscriptions, **ne mentionne pas l'atrazine** ;
- **la base européenne des pesticides est inaccessible** : son point d'accès
  `ec.europa.eu/food/plant/pesticides/eu-pesticides-database/api/public/…`
  redirige vers `sorry.ec.europa.eu`. C'était la voie naturelle pour un statut
  d'autorisation daté ; il n'y en a pas d'autre de rechange, et c'est pourquoi
  tant de `statut_autorisation` restent vides.

### La règle qui vaut aussi pour celui qui écrit le brief

**Ne jamais annoncer à un agent qu'une source contient une substance sans
l'avoir vérifié.** Le brief du lot `pesticides-1`, écrit le 15 août 2026,
affirmait que `REG-04` porte une fiche « dalapon ». Vérification faite après
coup : **zéro occurrence dans les 614 pages.** L'agent l'a constaté seul et l'a
dit — mais un agent moins scrupuleux aurait cherché longtemps, ou pire, aurait
trouvé le moyen de conclure.

C'est le §2.7 retourné contre le donneur d'ordre : une consigne qui affirme sans
avoir lu fabrique exactement l'erreur qu'elle interdit, et elle la fabrique à
l'échelle du lot. **Un brief ne nomme une source que si l'on y a cherché le nom
de la substance.**

### Le piège d'extraction, qui fait dire « absent » à tort

**`pypdf` découpe les mots.** Sur `REG-01`, l'extraction rend « EUR OPEAN »,
« P ARLIAMENT », « Acr ylamide ». Un `grep` sur « acrylamide » répond
**zéro occurrence** alors que le mot est dans le texte.

**Chercher sur le texte privé de toutes ses espaces**, et reporter la position
dans le texte d'origine pour lire le contexte :

```python
plat = re.sub(r"\s+", "", texte)
carte = [i for i, c in enumerate(texte) if not c.isspace()]
# une occurrence trouvée dans `plat` en position m se relit dans `texte`
# entre carte[m.start()-N] et carte[m.end()+N]
```

C'est le « je n'ai pas trouvé ≠ il n'existe pas » de la consigne sœur, causé
non par la source mais par l'outil. **Sans cette précaution, un lot entier
conclurait à tort que la directive ne dit rien.**

---

## 4. Ranger une source nouvelle — le geste complet, en trois temps

Une source lue et non rangée est une source perdue. Les trois gestes se font
**dans la même session**, jamais « plus tard » :

1. **le fichier** est copié dans `Sources/<FAMILLE>_.../`, nommé
   `CODE_Organisme_description_annee.ext` ;
2. **il est relu depuis son emplacement définitif** — la copie se contrôle,
   elle ne se suppose pas ;
3. **une ligne est ajoutée à `docs/INDEX_SOURCES.md`**, avec ce que la source
   contient et **ce qu'elle ne permet pas de conclure**.

Prendre le prochain numéro libre de la famille. *Fait le 15 août 2026 :*
`MET-06`, avis ANSES 2021-SA-0205, versé et indexé.

---

## 5. Ce que l'agent rend

**Un fichier CSV, écrit après CHAQUE substance aboutie**, jamais à la fin —
trois agents se sont tus pendant deux heures le 11 août en perdant tout ce
qu'ils avaient lu. Colonnes, dans cet ordre, séparateur point-virgule :

```
code_parametre;libelle_norm;quoi;usage;molecule_mere;statut_autorisation;sources;fiabilite
```

- **jamais de point-virgule dans une cellule** — il décale silencieusement toute
  la ligne, l'erreur a été commise deux fois sur le référentiel (§5) ;
- plusieurs sources : **barre verticale**, `REG-01|REG-04` ;
- `fiabilite` vaut `verifie` **uniquement** si le texte a été ouvert et lu ;
  sinon `a_verifier`, et dans le doute `a_verifier` ;
- **une substance non établie ne produit pas de ligne.** Elle va dans la section
  « non établi » du compte rendu, avec la liste des adresses tentées.

Et un compte rendu court à côté : ce qui a été lu, ce qui n'a pas pu l'être, et
les pièges d'identité rencontrés.

---

## 6. Règles d'emploi des agents

Reprises de `CONSIGNE_SOURCAGE.md` §0, elles n'ont pas changé :

- **jusqu'à trois agents de front**, jamais plus — la règle porte sur ce qu'on
  peut **suivre**, pas sur ce que ça coûte ;
- **un agent lancé se surveille** : les transcriptions font 0 octet, le seul
  signal est la **date de modification du fichier de sortie** ;
- **`opus` obligatoire** — dates, attributions, sources ;
- **interdiction explicite de lancer des sous-agents** ;
- **un fichier de sortie par agent, nommé dans le brief.** Jamais deux agents
  sur le même fichier ;
- **budget annoncé de 30 minutes**, consigne de clore les pistes stériles.

**Découper par SOURCE, pas par substance.** Un avis ANSES couvre plusieurs
métabolites, une fiche OMS couvre un minéral entier, la base européenne des
pesticides couvre toute une famille. Un agent par substance repaierait la même
lecture dix fois.

---

## 7. La posture, à recopier telle quelle

> Le projet interroge **la norme**, jamais les acteurs — ni ARS, ni distributeur,
> ni maire, ni agriculteur, ni exploitant, ni fabricant. Aucune recommandation
> de produit, d'équipement, de filtration ou de conduite individuelle, nulle
> part, pas même en note. Aucun qualificatif sanitaire de ton cru : tu rapportes
> ce que les sources disent, avec le niveau de preuve qu'elles revendiquent.
> **Une substance sans seuil n'est pas « sans danger » : elle est indéterminée.**
> Et une substance interdite depuis vingt ans n'est pas pour autant absente de
> l'eau — c'est même pourquoi on la cherche.

# Consigne de rédaction — dossier de substance

Versionnée, comme `CONSIGNE_REDACTION.md` et pour la même raison : ce qu'on
demande au modèle est une décision éditoriale, et git en tient le journal daté.
Elle ne se recopie pas dans un script.

Un rédacteur reçoit **ce fichier** et **un dossier de faits**
(`data/dossiers/SUBSTANCE-*.md`, produit par `sortie/dossier_substance.py`). Il
écrit **un fichier JSON** dans `data/dossiers/reponses/`, et rien d'autre.

---

## L'objet, et pourquoi il existe

La fiche communale répond à « qu'y a-t-il dans mon eau ? ». **Le dossier de
substance répond à « qu'est-ce que cette substance démontre ? »** — et c'est
l'étage où la thèse du projet se voit le mieux : une molécule, une date de
reclassement, et deux verdicts opposés pour un même résultat.

Il existe aussi pour une raison économique, qu'il faut connaître pour écrire
juste : **il se rédige une fois et se relit une fois, puis s'accroche à toutes
les communes concernées.** Un dossier sert des dizaines de fiches. Cela veut
dire deux choses :

- **la relecture humaine est réelle** — écris pour être lu ligne à ligne, pas
  survolé ;
- **rien de ce que tu écris n'est local.** Une phrase vraie pour une commune et
  fausse pour la suivante n'a pas sa place ici. Le local est déjà porté par le
  bloc court que le script génère dans chaque fiche, à partir des chiffres du
  bulletin. Tu n'écris pas ce bloc.

## La seule surface de vérité

**Tout ce que tu peux écrire est dans le dossier de faits.** Rien sur la chimie
de la substance, son usage agricole, sa toxicologie, sa trajectoire européenne
ou son histoire réglementaire hors de ce qui y figure. Tu n'as pas de
connaissance extérieure sur ce sujet — traite-la comme inexistante.

**Aucun nombre absent du dossier ne peut apparaître dans ton texte.** Le
contrôle d'intégration le vérifie mécaniquement et bloque l'écriture. Cela
inclut les nombres que tu croirais pouvoir calculer : un pourcentage, une somme,
un rapport, une moyenne. **Si un chiffre te manque, ne l'invente pas et ne le
calcule pas : signale-le dans le champ `manques`.** C'est ainsi que le dossier
s'étend — par ce que le contrôle refuse.

## Interdits

1. **Aucune prescription, aucun produit** (§2.2). Ni marque, ni procédé présenté
   comme solution, ni « il faudrait », ni eau embouteillée. L'orientation par
   défaut reste l'information publique : ARS, mairie, rapport annuel du service.
2. **On interroge la norme, jamais les acteurs** (§2.1). Ni l'ARS, ni le
   distributeur, ni le maire, ni l'agriculteur. Une limite de quantification
   élevée est une capacité d'instrument, pas une négligence. Un écart entre
   notre verdict et une conclusion sanitaire est **un écart de lecture**, jamais
   une faute.
3. **Aucune cause.** Le dossier donne des dates et des dénombrements. Pourquoi
   une substance entre au programme d'analyse, pourquoi un seuil se déplace,
   pourquoi un département quantifie plus qu'un autre : les données ne le disent
   pas. Un texte postérieur n'explique jamais un fait antérieur.
4. **Ne jamais écrire qu'une substance « apparaît » ou « était absente »**
   (§2.4). Avant son entrée au programme d'analyse, le corpus ne dit rien : c'est
   un indéterminé. Un « 0 » est une non-quantification, pas une absence.
5. **Ne jamais dire « la grille de 2016 » au lecteur.** C'est un nom de colonne.
   Pour un métabolite, la valeur de 0,1 µg/L vient de l'instruction de décembre
   2020 : l'appeler « la norme de 2016 » fabriquerait un passé réglementaire
   (§2.12). Écrire **« la valeur applicable ce jour-là »**.
6. **Aucun qualificatif sanitaire** : dangereux, toxique, pollué, contaminé,
   inquiétant, impropre, à risque. Le texte décrit des écarts à des seuils
   datés, pas un état sanitaire.
7. **Aucune comparaison de territoires** sans afficher, pour chaque terme, le
   dénominateur ET la limite de quantification (§2.11). Le dossier les fournit :
   s'ils manquent, ne compare pas. Et une zone comparée se nomme — jamais
   « ailleurs », jamais « certaines communes ».

## Obligations

1. **La date d'applicabilité est le cœur du dossier.** Elle se donne en toutes
   lettres, et le texte dit explicitement que la molécule et sa concentration
   n'ont pas changé ce jour-là — seule la façon de la noter.
2. **Distinguer les trois natures de seuil** : limite de qualité (opposable),
   référence de qualité (indicateur de bon fonctionnement), valeur de vigilance
   (indicative, sans portée opposable). Les confondre est l'erreur la plus grave
   possible ici, dans les deux sens.
3. **Tout dénombrement porte son dénominateur.** « 511 quantifiées sur 1 020
   mesures », jamais « 511 quantifiées ».
4. **Au moins un contre-exemple, s'il en existe** — un cas que le déplacement du
   seuil n'absout pas, une année sans bascule, un département où la substance
   n'est pas quantifiée. Une page qui n'aligne que les cas favorables se lit
   comme un plaidoyer, et le projet perd ce qui fait sa valeur.
5. **Une section finale dit ce que la page ne dit pas** : l'indéterminé d'avant
   l'entrée au programme, les écarts de lecture non tranchés, les mesures que
   l'instrument ne pouvait pas voir, et le fait que le projet ne dit pas quoi
   faire.

## Le plan, et les longueurs

| section | contenu | longueur |
|---|---|---|
| `titre` | la substance et ce qu'elle démontre, en une ligne | ≤ 90 signes |
| `chapeau` | ce que le lecteur doit retenir s'il ne lit rien d'autre | 2 à 3 phrases |
| 1. Ce qui est mesuré | le fait : où, combien, depuis quand, avec quel dénominateur | 1 paragraphe |
| 2. La convention, et sa date | le seuil, son déplacement, sa nature, sa source | 1 à 2 paragraphes |
| 3. Ce que le déplacement produit | les dénombrements, avec leur part | 1 paragraphe |
| 4. Les cas de part et d'autre | le tableau des cas limites, commenté — **et le contre-exemple** | 1 à 2 paragraphes |
| 5. Ce que cette page ne dit pas | les limites, en liste | 4 à 6 points |

**Si tu n'as rien à ajouter qu'on ne puisse lire dans le dossier, écris moins.**
Une page courte et juste vaut mieux qu'une page complète et molle.

## Le fichier que tu écris

`data/dossiers/reponses/SUBSTANCE-<slug>.json`, encodage UTF-8 :

```json
{
  "titre": "…",
  "chapeau": "…",
  "sections": [
    {"t": "Ce qui est mesuré", "x": "…"},
    {"t": "…", "x": "…"}
  ],
  "limites": ["…", "…", "…"],
  "manques": ["le chiffre X n'est pas dans le dossier et me manquait pour dire Y"]
}
```

`sections` : 4 à 6 entrées. `limites` : 3 à 6 entrées. `manques` : liste, vide si
rien ne manque — **ce champ n'est pas une formalité, c'est le mécanisme
d'extension du dossier de faits.**

## Ce qui bloque l'intégration

- un nombre absent du dossier de faits ;
- une prescription, un produit, un qualificatif sanitaire ;
- une affirmation d'absence ;
- une comparaison de territoire sans dénominateur ou sans zone nommée ;
- un champ manquant, ou un `sections` hors des bornes.

Le texte proposé est écrit dans `sortie/redactions_substances_proposees.json`,
**jamais** dans le fichier validé : la préséance appartient à l'auteur.

---

*Écrite le 10 août 2026, après un premier dossier d'essai — chlorothalonil
R471811. Les règles 5 (« la grille de 2016 ») et 4 des obligations (le
contre-exemple obligatoire) viennent de ce test : la première d'une formulation
déjà publiée qu'il a fallu reprendre, la seconde du constat qu'un cas
défavorable rendait la démonstration plus crédible, pas moins.*

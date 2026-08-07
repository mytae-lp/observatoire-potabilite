# -*- coding: utf-8 -*-
"""
Fonctions partagées de l'Observatoire de la potabilité réglementaire.

Trois règles du projet vivent ici, et nulle part ailleurs :
  - norm()         : la normalisation des libellés (rapprochement mesure <-> référentiel) ;
  - parse_val()    : la lecture d'un résultat, qui distingue une valeur QUANTIFIÉE
                     d'une limite de quantification (« 0 » n'est pas zéro) ;
  - parse_limite() : la lecture d'une limite de qualité telle que déclarée par
                     la source (« <=0,1 µg/L »).
Toute modification ici change la sémantique de toute la base : commit dédié.
"""
import os
import re
import unicodedata

# --- Chemins ---------------------------------------------------------------
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(RACINE, "data", "eau.duckdb")
REF_CSV = os.path.join(RACINE, "referentiel", "referentiel_seuils.csv")
ALIAS_CSV = os.path.join(RACINE, "referentiel", "alias_parametres.csv")
CATALOGUE_CSV = os.path.join(RACINE, "referentiel", "catalogue_parametres_hubeau.csv")
JOURNAL_DIR = os.path.join(RACINE, "data", "journal")

# --- Constantes de méthode -------------------------------------------------
# Un prélèvement n'est retenu comme "complet" qu'au-delà de ce nombre de
# paramètres. Voir CLAUDE.md §2.3 : sans ce filtre, les analyses de routine
# noient les analyses complètes et la conclusion est toujours "tout va bien".
#
# Valeur fixée sur la distribution réelle, mesurée le 7 août 2026 sur 964
# prélèvements des départements 17, 28 et 31 depuis 2022 :
#
#      1-9    :  38          200-249  :   6
#     10-29   : 772          250-299  :  46
#     30-49   :  75          300-399  :  16
#     50-99   :  10
#    100-149  :   1
#    150-199  :   0   <-- aucun prélèvement : le trou est net
#
# La routine s'éteint vers 100, les analyses complètes commencent à 236.
# Toute valeur entre 150 et 200 sépare les deux populations sans en amputer
# aucune. 250 coupait dans le bas du groupe des complètes : le bulletin de
# Challet du 10/03/2026 (234 paramètres), sur lequel l'ARS a prononcé une
# non-conformité pour le chlorothalonil R417888, en était exclu.
SEUIL_COMPLET = 200

# Profondeur de l'analyse. Ce n'est PAS un indicateur de qualité de l'eau :
# c'est un indicateur de l'effort de recherche, et il se lit dans l'autre
# sens (cf. CLAUDE.md §2.11). On ne trouve que ce qu'on cherche.
CLASSES_EFFORT = (
    (200, "restreinte"),
    (300, "standard"),
    (450, "approfondie"),
    (10 ** 9, "exhaustive"),
)


def classe_effort(nb_parametres):
    """Nombre de paramètres recherchés -> classe de profondeur d'analyse."""
    if nb_parametres is None:
        return None
    for plafond, nom in CLASSES_EFFORT:
        if nb_parametres < plafond:
            return nom
    return CLASSES_EFFORT[-1][1]

USER_AGENT = (
    "Observatoire-potabilite-reglementaire/1.0 "
    "(projet citoyen open data ; contact: Editions Mytae)"
)

# Suffixe d'unité collé au libellé par certains laboratoires : « Aluminium
# total µg/l », « Uranium en µg/l », « Escherichia coli /100mL ». Le même
# paramètre existe ailleurs sans ce suffixe ; sans ce nettoyage il compte
# pour deux et l'un des deux n'est apparié à rien.
#
# Attention : norm() translittère en ASCII et « µ » disparaît, donc « µg/l »
# est déjà devenu « g/l » quand ce motif s'applique.
_SUFFIXE_UNITE = re.compile(
    r"\s*\(?\s*(?:en\s+)?(?:"
    r"[mnpu]?g\s*/\s*l"          # g/L, mg/L, ng/L (µg/L arrive ici en « g/l »)
    r"|n?\s*/\s*100\s*ml"        # /100mL, n/100mL
    r"|bq\s*/\s*l"               # Bq/L (radiologique)
    r"|m?s\s*/\s*cm"             # µS/cm -> « s/cm » (conductivité)
    r"|unite\s*ph"
    r")\s*\)?$"
)


def norm(x):
    """
    Libellé -> clé de rapprochement : sans accent, minuscule, espaces réduits,
    et sans le suffixe d'unité que certains laboratoires collent au libellé.

    'Aluminium total µg/l'    -> 'aluminium total'
    'Uranium en µg/l'         -> 'uranium'
    'Escherichia coli /100mL' -> 'escherichia coli'
    'Nitrates (en NO3)'       -> 'nitrates (en no3)'   (intact : ce n'est pas une unité)
    """
    if x is None:
        return ""
    x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
    x = re.sub(r"\s+", " ", x).strip()
    # « uranium en µg/l » demande deux passes : « en g/l » puis rien.
    for _ in range(2):
        nouveau = _SUFFIXE_UNITE.sub("", x).strip()
        if nouveau == x or not nouveau:
            break
        x = nouveau
    return x


def norm_unite(u):
    """
    Unité -> clé de comparaison. N'utilise PAS norm() : la translittération
    ASCII y mange le « µ », et « µg/L » deviendrait « g/L », soit un facteur
    un million.

    L'espèce chimique entre parenthèses est retirée : « µg(CN)/L » est une
    quantité de cyanure en µg par litre, donc dimensionnellement des µg/L.
    De même « mg(Cl2)/L », « mg(C)/L », « µg(Se)/L ». Sans ce nettoyage, ces
    mesures sont déclarées non comparables à leur propre seuil et disparaissent
    de l'analyse.

    'µg/L' -> 'ug/l'   'µg(CN)/L' -> 'ug/l'   'unité pH' -> 'uniteph'
    """
    if u is None:
        return None
    t = str(u).replace("µ", "u").replace("μ", "u")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\([^)]*\)", "", t)   # espèce chimique : µg(CN)/L -> µg/L
    t = re.sub(r"\s+", "", t)
    return t or None


# Unités de masse par litre, ramenées à µg/L. Sert à convertir un seuil du
# référentiel vers l'unité dans laquelle la mesure est exprimée.
#
# Sans cette conversion, un chlorate mesuré en µg/L était comparé au seuil de
# 0,25 mg/L du référentiel : un facteur 1000, et un faux dépassement massif.
# Erreur réellement présente et détectée par v_ecarts_referentiel_source.
FACTEURS_MASSE_PAR_LITRE = {
    "g/l": 1_000_000.0,
    "mg/l": 1_000.0,
    "ug/l": 1.0,
    "ng/l": 0.001,
    "pg/l": 0.000001,
}


def parse_val(v):
    """
    Résultat brut -> (resultat_num, lq, unite, est_quantifie).

    '0,092 µg/L'      -> (0.092, None,  'µg/L', True)   valeur quantifiée
    '<0,01 µg/L'      -> (None,  0.01,  'µg/L', False)  sous la limite de quantification
    '41 mg/L'         -> (41.0,  None,  'mg/L', True)
    "A l'équilibre"   -> (None,  None,  "A l'équilibre", False)  résultat qualitatif

    Règle du projet (CLAUDE.md §2.4) : un dépassement ne peut être affirmé que
    si est_quantifie vaut True. Une non-quantification n'est PAS une absence.
    """
    if v is None or str(v).strip() == "":
        return (None, None, None, False)
    s = str(v).strip()
    m = re.match(r"^(<\s*=?\s*)?(-?[0-9]+(?:[.,][0-9]+)?)\s*(.*)$", s)
    if not m:
        return (None, None, (s or None), False)  # qualitatif
    inferieur = bool(m.group(1))
    num = float(m.group(2).replace(",", "."))
    unite = (m.group(3).strip() or None)
    if inferieur:
        return (None, num, unite, False)
    return (num, None, unite, True)


def parse_limite(v):
    """
    Limite de qualité telle que déclarée par la source -> (valeur, unite).

    '<=0,1 µg/L'   -> (0.1,  'µg/L')
    '<= 50 mg/L'   -> (50.0, 'mg/L')
    '>=6,5 unité pH' -> (None, None)   borne basse : le modèle ne sait pas
                                       l'exprimer, on ne fabrique pas un seuil faux
    'absence'      -> (None, None)     qualitatif

    Cette valeur est la grille D'AUJOURD'HUI, déclarée par l'administration
    avec la mesure. Elle ne remplace jamais le référentiel daté du projet :
    elle ne dit rien de 2016 ni du seuil le plus strict au monde
    (cf. CLAUDE.md §2.5 — un seuil sans sa date d'applicabilité est faux).
    """
    if v is None or str(v).strip() == "":
        return (None, None)
    s = str(v).strip()
    if s.startswith(">"):
        # borne inférieure (pH, TAC…) : hors du modèle « dépassement par le haut »
        return (None, None)
    m = re.match(r"^(?:<\s*=?|=|≤)?\s*(-?[0-9]+(?:[.,][0-9]+)?)\s*(.*)$", s)
    if not m:
        return (None, None)
    return (float(m.group(1).replace(",", ".")), (m.group(2).strip() or None))


def f(x):
    """Cellule CSV -> float ou None (vide, espace ou tiret = absence de seuil)."""
    if x is None:
        return None
    s = str(x).strip().replace(",", ".")
    if s in ("", "-", "NA", "ND"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def s(x):
    """Cellule CSV -> str ou None."""
    if x is None:
        return None
    t = str(x).strip()
    return t or None

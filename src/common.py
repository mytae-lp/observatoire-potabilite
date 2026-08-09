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
    # Une espèce chimique commence par une LETTRE — (CN), (Cl2), (P2O5), (SiO2).
    # Une base de dénombrement commence par un CHIFFRE — (100mL) — et elle EST
    # l'unité, pas une précision sur elle.
    #
    # La règle d'avant retirait les deux. « n/(100mL) » devenait « n/ », donc :
    #   - les bactéries coliformes, E. coli et les entérocoques n'étaient plus
    #     comparables à leur propre référence, écrite « n/100mL » au
    #     référentiel — trois lignes muettes sur 10 348 mesures ;
    #   - pire, « n/(100mL) », « n/(250mL) » et « n/(100L) » se réduisaient
    #     tous les trois à « n/ », donc se déclaraient mutuellement comparables.
    #     Un dénombrement par litre lu comme un dénombrement par 100 mL est un
    #     facteur 10, et le §2.9 dit qu'un verdict faux est pire qu'un verdict
    #     absent.
    t = re.sub(r"\(\s*[^\d)][^)]*\)", "", t)   # espèce chimique : µg(CN)/L -> µg/L
    t = t.replace("(", "").replace(")", "")     # la base reste, ses parenthèses non
    t = re.sub(r"\s+", "", t)
    # « mSv/an » et « mSv/a » sont la même unité : le référentiel écrit l'année
    # comme la directive, Hub'Eau l'abrège. Sans cette équivalence, la dose
    # indicative totale — 2 805 mesures — n'a aucun seuil de comparaison.
    t = re.sub(r"/an$", "/a", t)
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


# --- Listes de communes à collecter ---------------------------------------
# Colonnes acceptées comme portant le code, dans l'ordre de préférence. Un
# code postal et un code INSEE se ressemblent (cinq caractères) : la
# résolution tranche à la collecte, pas ici.
_COLONNES_CODE = ("code", "code_insee", "insee", "code_postal", "cp",
                  "codepostal", "code postal")


def lire_liste_communes(chemin):
    """
    Fichier CSV -> [(code, motif)], pour piloter une collecte par lots.

    Format attendu, séparateur « ; » ou « , », en-tête facultatif :

        code;motif
        17415;Saintes — cas ESA métolachlore
        28068;Challet — R417888, non-conformité ARS
        31520

    Le `motif` n'est pas utilisé par la collecte : il sert à ce que la liste
    reste lisible six mois plus tard, et à ce qu'on sache pourquoi une commune
    y figure. Une ligne vide ou commençant par « # » est ignorée.

    Les codes en double sont retirés en conservant le premier motif rencontré :
    la collecte est idempotente, mais retélécharger deux fois la même commune
    reste une charge inutile sur un service public gratuit (CLAUDE.md §3.2).
    """
    import csv as _csv

    with open(chemin, encoding="utf-8-sig", newline="") as fh:
        texte = fh.read()
    if not texte.strip():
        raise ValueError(f"{chemin} : fichier vide")

    lignes = [l for l in texte.splitlines()
              if l.strip() and not l.lstrip().startswith("#")]
    separateur = ";" if lignes[0].count(";") >= lignes[0].count(",") else ","
    lecteur = list(_csv.reader(lignes, delimiter=separateur))

    # En-tête ? Seulement si la première cellule n'est pas elle-même un code.
    tete = [c.strip().lower() for c in lecteur[0]]
    i_code, i_motif = 0, 1
    if not re.fullmatch(r"[0-9][0-9AB][0-9]{3}", lecteur[0][0].strip().upper()):
        trouve = next((i for i, c in enumerate(tete) if c in _COLONNES_CODE), None)
        if trouve is None:
            raise ValueError(
                f"{chemin} : ni code en première cellule, ni colonne parmi "
                f"{', '.join(_COLONNES_CODE)}")
        i_code = trouve
        i_motif = next((i for i, c in enumerate(tete)
                        if c in ("motif", "raison", "commentaire", "note")), None)
        lecteur = lecteur[1:]

    sortie, vus = [], set()
    for n, ligne in enumerate(lecteur, 1):
        if len(ligne) <= i_code:
            continue
        code = ligne[i_code].strip().upper()
        if not code:
            continue
        if not re.fullmatch(r"[0-9][0-9AB][0-9]{3}", code):
            raise ValueError(
                f"{chemin}, ligne {n} : « {code} » n'est ni un code postal ni un "
                "code INSEE (cinq caractères, éventuellement 2A/2B pour la Corse)")
        if code in vus:
            continue
        vus.add(code)
        motif = (ligne[i_motif].strip()
                 if i_motif is not None and len(ligne) > i_motif else "")
        sortie.append((code, motif))

    if not sortie:
        raise ValueError(f"{chemin} : aucun code exploitable")
    return sortie


_PLAGE = re.compile(
    r"^\s*>\s*=?\s*(-?[0-9]+(?:[.,][0-9]+)?)\s*(?:et)?\s*"
    r"<\s*=?\s*(-?[0-9]+(?:[.,][0-9]+)?)\s*(.*)$", re.I)


def parse_plage(v):
    """
    Référence encadrée par le HAUT et par le BAS -> (mini, maxi, unite).

    '>=6,5 et <=9 unité pH'      -> (6.5, 9.0, 'unité pH')
    '>=200 et <=1100 µS/cm'      -> (200.0, 1100.0, 'µS/cm')
    '<=2 mg(C)/L'                -> (None, None, None)   -- borne haute seule,
                                    c'est le domaine de parse_limite()

    Le modèle du projet ne connaît que le « dépassement par le haut » : une eau
    trop peu minéralisée ou trop acide sort de la référence de qualité sans
    qu'aucun seuil ne soit franchi au sens de `parse_limite()`, qui abandonne
    dès qu'une chaîne commence par « > ». Ces paramètres — pH, conductivité —
    disparaissaient donc de toute lecture. Ils décrivent le caractère de l'eau,
    pas sa pollution, et une eau agressive est un vrai sujet : elle dissout les
    matériaux du réseau qu'elle traverse.

    La plage n'est pas inventée ici : elle est **déclarée par la source avec la
    mesure**, dans `reference_brute`. Elle ne dit donc rien de 2016 ni du seuil
    le plus strict au monde — comme toute limite déclarée (§2.8).
    """
    if v is None or str(v).strip() == "":
        return (None, None, None)
    m = _PLAGE.match(str(v).strip())
    if not m:
        return (None, None, None)
    return (float(m.group(1).replace(",", ".")),
            float(m.group(2).replace(",", ".")),
            (m.group(3).strip() or None))


def bornes_reference(brut):
    """
    (mini, maxi) d'une référence de qualité déclarée, quelle que soit sa forme.

    Encadrée des deux côtés — « >=6,5 et <=9 unité pH » — c'est `parse_plage`.
    Bornée par le haut seulement — « <=200 µg/L » — c'est `parse_limite`.

    UN SEUL endroit décide de cette forme, et c'est celui-ci. L'ingestion, la
    migration de la table et les vues s'y réfèrent toutes : deux implémentations
    d'une même règle divergent à la première retouche, et la première victime
    serait la borne BASSE — celle qui vaut None dans `reference_declaree` et qui
    rendait invisibles 527 mesures d'eau agressive.
    """
    mini, maxi, _ = parse_plage(brut)
    if mini is None and maxi is None:
        maxi = parse_limite(brut)[0]
    return mini, maxi


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

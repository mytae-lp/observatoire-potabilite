# -*- coding: utf-8 -*-
"""
Fonctions partagées de l'Observatoire de la potabilité réglementaire.

Deux règles du projet vivent ici, et nulle part ailleurs :
  - norm()      : la normalisation des libellés (rapprochement mesure <-> référentiel) ;
  - parse_val() : la lecture d'un résultat, qui distingue une valeur QUANTIFIÉE
                  d'une limite de quantification (« 0 » n'est pas zéro).
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
JOURNAL_DIR = os.path.join(RACINE, "data", "journal")

# --- Constantes de méthode -------------------------------------------------
# Un prélèvement n'est retenu comme "complet" qu'au-delà de ce nombre de
# paramètres. Voir CLAUDE.md §2.3 : sans ce filtre, les analyses de routine
# noient les analyses complètes et la conclusion est toujours "tout va bien".
SEUIL_COMPLET = 250

USER_AGENT = (
    "Observatoire-potabilite-reglementaire/1.0 "
    "(projet citoyen open data ; contact: Editions Mytae)"
)


def norm(x):
    """Libellé -> clé de rapprochement : sans accent, minuscule, espaces réduits."""
    if x is None:
        return ""
    x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", x).strip()


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
    m = re.match(r"^(<\s*)?(-?[0-9]+(?:[.,][0-9]+)?)\s*(.*)$", s)
    if not m:
        return (None, None, (s or None), False)  # qualitatif
    inferieur = bool(m.group(1))
    num = float(m.group(2).replace(",", "."))
    unite = (m.group(3).strip() or None)
    if inferieur:
        return (None, num, unite, False)
    return (num, None, unite, True)


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

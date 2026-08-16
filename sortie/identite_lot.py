# -*- coding: utf-8 -*-
"""
Sourcer l'identité des substances en lot — le script aux deux bouts.

Même contrat que `sortie/rediger_lot.py`, et pour la même raison : un script
déterministe choisit ce qui reste à faire et **contrôle ce qui revient** ; des
agents de fond ne font au milieu que la seule étape qui demande une lecture.
Aucun appel d'API, aucune clé — les agents tournent dans Claude Code.

    py -X utf8 sortie/identite_lot.py --etat        # ce qui reste, par lot
    py -X utf8 sortie/identite_lot.py --briefs      # fabrique les briefs
    py -X utf8 sortie/identite_lot.py --verifier    # contrôle, sans rien écrire
    py -X utf8 sortie/identite_lot.py --integrer    # contrôle puis verse

**Le contrôle au retour est la vraie valeur de ce script**, et il porte sur ce
qu'un modèle fait de travers quand il source une identité :

  · une VALEUR DE SEUIL qui s'invite dans un champ d'identité. C'est le défaut
    le plus probable : on lit un avis qui parle de 0,1 µg/L, et la phrase
    d'identité en repart avec. Les seuils ont leur fichier, leur consigne et
    leur contrôle ; toute valeur suivie d'une unité de concentration bloque ;
  · un QUALIFICATIF SANITAIRE — « toxique », « sans danger », « inoffensif ».
    Le projet rapporte ce que les sources disent (§2.2, §7 de la consigne) ;
  · un STATUT D'AUTORISATION SANS DATE. « Interdite » sans millésime est le
    §2.5 transposé du seuil au droit ;
  · une SOURCE INCONNUE de `docs/INDEX_SOURCES.md`. Un code inventé a
    l'apparence exacte d'un code réel ;
  · un POINT-VIRGULE dans une cellule, qui décale toute la ligne en silence ;
  · une SUBSTANCE ABSENTE du corpus — donc une ligne qui ne servira jamais et
    signale que l'agent a travaillé sur autre chose que ce qu'on lui a donné.

Le périmètre du lot est celui des substances qui pèsent : **porteuses d'une
bascule ou d'un dépassement**. Les autres viendront après ; une substance
jamais en dépassement n'a encore fait basculer aucun verdict.
"""

import argparse
import csv
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "src"))
sys.path.insert(0, ICI)

import common as C          # noqa: E402
import dossier_page as DP   # noqa: E402
import identite as ID       # noqa: E402

TABLE = ID.TABLE
INDEX_SOURCES = os.path.join(RACINE, "docs", "INDEX_SOURCES.md")
DOSSIERS = os.path.join(RACINE, "data", "dossiers")
REPONSES = os.path.join(DOSSIERS, "reponses_identite")
COLONNES = ["code_parametre", "libelle_norm", "quoi", "usage",
            "molecule_mere", "statut_autorisation", "sources", "fiabilite"]

# Les lots, découpés PAR SOURCE et non par substance : un avis ANSES couvre
# plusieurs métabolites, une fiche OMS couvre un minéral entier. Un agent par
# substance repaierait la même lecture dix fois.
LOTS = {
    "metabolites": (["metabolite"],
                    "avis ANSES de pertinence (MET-01, MET-06), tableur MET-05"),
    "metaux": (["metal", "metalloide"],
               "fiches OMS de REG-04, section 12 ; annexe I de REG-01"),
    "mineraux": (["mineral", "nitrates", "nitrites", "equilibre",
                  "organoleptique", ""],
                 "fiches OMS de REG-04 ; annexe I partie B et C de REG-01"),
    "pesticides": (["pesticide"],
                   "base européenne des pesticides ; fiches OMS de REG-04"),
    "traitement": (["sous-produit desinfection", "organique", "PFAS",
                    "microbiologique", "radiologique"],
                   "REG-01 et ses notes, REG-11, fiches OMS"),
}

# Une valeur de concentration : c'est un seuil, et un seuil n'entre pas ici.
VALEUR_UNITE = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:µ|μ|u|m|n|p)?g\s*(?:\(\w+\))?\s*[/·]\s*[lLkK]", re.I)
# `Bq/L`, `NFU`, `mS/cm` : mêmes objets, autre unité.
AUTRES_UNITES = re.compile(r"\d+(?:[.,]\d+)?\s*(?:Bq|NFU|NTU|µS|μS|mS)\b", re.I)
QUALIFICATIFS = re.compile(
    r"\b(sans danger|inoffensi\w+|anodin\w*|dangereu\w+|toxique\w*|nociv\w+|"
    r"cancérigèn\w+|cancerogen\w+|sûr pour|sans risque|bénin\w*)\b", re.I)
# Un statut d'autorisation se date, ou il est faux (§2.5).
UNE_DATE = re.compile(r"\b(1[6-9]|20)\d{2}\b")


FONDS = os.path.join(os.path.dirname(os.path.dirname(RACINE)), "Sources")


def codes_sources_connus():
    """Les codes de `docs/INDEX_SOURCES.md`, tels qu'ils y sont écrits."""
    if not os.path.exists(INDEX_SOURCES):
        return set()
    texte = io.open(INDEX_SOURCES, encoding="utf-8").read()
    return set(re.findall(r"\b([A-Z]{2,5}-\d{2})\b", texte))


def codes_sans_fichier(connus):
    """
    Les codes catalogués à l'index dont aucun fichier n'est sur le disque.

    Un code peut être **connu et pourtant illisible** : `REG-06` et `REG-07`
    sont à l'index depuis le 9 août 2026 sans que leur fichier existe, défaut
    signalé et non corrigé. Or `REG-07` est précisément la décision qui
    interdit l'atrazine — celle qu'un agent citera le plus volontiers, et qu'il
    ne pourra pas avoir lue. Sans ce contrôle, le seul mensonge que la chaîne
    ne sait pas attraper serait la source la plus attendue de tout le lot.

    Signalement et non blocage : une source peut légitimement vivre ailleurs
    que dans `Sources/` — une page Légifrance lue en ligne, par exemple. C'est
    à la relecture humaine de trancher, mais elle doit le voir.
    """
    if not os.path.isdir(FONDS):
        return set()
    presents = set()
    for racine, _d, fichiers in os.walk(FONDS):
        for f in fichiers:
            m = re.match(r"([A-Z]{2,5}-\d{2})_", f)
            if m:
                presents.add(m.group(1))
    return connus - presents


def lire_table(chemin):
    """Les lignes d'un CSV d'identité, commentaires et vides écartés."""
    if not os.path.exists(chemin):
        return []
    with io.open(chemin, encoding="utf-8") as fh:
        lignes = [l for l in fh if not l.lstrip().startswith("#") and l.strip()]
    if not lignes:
        return []
    # Un fichier rendu par un agent peut ne pas porter l'en-tête : on le pose.
    if not lignes[0].lower().startswith("code_parametre"):
        lignes.insert(0, ";".join(COLONNES) + "\n")
    return list(csv.DictReader(lignes, delimiter=";"))


def repertoire(version=None):
    """Le corpus, lu une fois. La base n'est ouverte qu'en lecture."""
    import duckdb
    import figer
    chemin = os.path.join(RACINE, "data", "eau.duckdb")
    con = duckdb.connect(chemin, read_only=True)
    try:
        if not version:
            dispo = con.execute("""SELECT version_referentiel, MAX(calcule_le)
                                   FROM analyses_figees GROUP BY 1
                                   ORDER BY 2 DESC""").fetchall()
            courante = figer.version_referentiel()
            version = courante if any(d[0] == courante for d in dispo) else (
                dispo[0][0] if dispo else None)
            if not version:
                print("aucun figeage en base — lance src/figer.py")
                sys.exit(1)
        return DP.repertoire(con, version), version
    finally:
        con.close()


# Au-delà, un brief cesse d'être tenable : l'agent survole, et la relecture
# humaine d'un rendu de cinquante lignes redevient un travail de lot — ce que
# tout ce dispositif existe pour éviter. Mesure du 15 août 2026 : 18 substances
# ont coûté 199 000 tokens et 12 minutes, 16 en ont coûté 156 000.
MAX_PAR_LOT = 18


def a_faire(rep):
    """
    Ce qui pèse et n'est pas encore sourcé, par lot.

    Un lot trop gros est découpé en `nom-1`, `nom-2`… Le découpage suit
    l'ordre alphabétique du libellé et non le poids : il faut qu'il soit
    REPRODUCTIBLE d'un appel à l'autre, sans quoi relancer les briefs après un
    versement partiel redistribuerait les substances entre agents, et deux
    agents finiraient par travailler sur la même.
    """
    tables = ID.charger()
    cible = [f for f in rep if f["bascules"] or f["depassements"]]
    reste = [f for f in cible if not ID.pour(tables, f["code"], f["libelle"])]
    brut = {nom: [] for nom in LOTS}
    orphelins = []
    for f in reste:
        for nom, (familles, _s) in LOTS.items():
            if (f["famille"] or "") in familles:
                brut[nom].append(f)
                break
        else:
            orphelins.append(f)

    par_lot = {}
    for nom, molecules in brut.items():
        molecules = sorted(molecules, key=lambda f: f["libelle"].lower())
        if len(molecules) <= MAX_PAR_LOT:
            par_lot[nom] = molecules
            continue
        tranches = -(-len(molecules) // MAX_PAR_LOT)
        taille = -(-len(molecules) // tranches)      # tranches équilibrées
        for i in range(tranches):
            par_lot[f"{nom}-{i + 1}"] = molecules[i * taille:(i + 1) * taille]
    return cible, reste, par_lot, orphelins


# ---------------------------------------------------------------------------
# Les briefs — tout ce que l'agent sait du corpus vient d'ici
# ---------------------------------------------------------------------------
def brief(nom, molecules, sources, version):
    o = [f"# Lot d'identité — {nom}", "",
         f"Version de référentiel : `{version}`. "
         f"{len(molecules)} substances.", "",
         "**Lis d'abord `docs/CONSIGNE_IDENTITE.md`. Elle fait foi, et ce "
         "brief ne la répète pas.** Les règles qui y figurent ne sont pas "
         "négociables, en particulier : aucune valeur de seuil dans un champ "
         "d'identité, aucun qualificatif sanitaire, aucun statut "
         "d'autorisation sans sa date, et **aucune ligne pour une substance "
         "dont tu n'as pas lu la source**.", "",
         f"Pistes de lecture pour ce lot : {sources}.", "",
         "## Les substances", "",
         "| libellé de la source | code SANDRE | CAS | unité | cherchée | "
         "quantifiée | dépassements | bascules |", "|---|---|---|---|---|---|---|---|"]
    for f in molecules:
        o.append(f'| {f["libelle"]} | {f["code"] or "—"} | {f["cas"] or "—"} | '
                 f'{f["unite"] or "—"} | {f["mesures"]} | {f["quantifiees"]} | '
                 f'{f["depassements"]} | {f["bascules"]} |')
    o += ["",
          "Ces comptes sont donnés pour que tu saches ce qui pèse — ils ne "
          "s'écrivent nulle part dans ta sortie. **Le corpus ne dit rien de ce "
          "que ces substances sont** : c'est tout l'objet du lot.", "",
          "## Ce que tu rends", "",
          f"Un CSV à `data/dossiers/reponses_identite/{nom}.csv`, colonnes "
          f"`{';'.join(COLONNES)}`, **une ligne écrite après chaque substance "
          "aboutie** et non à la fin.", "",
          "`libelle_norm` : recopie le libellé de la source tel qu'il est dans "
          "le tableau ci-dessus. `code_parametre` : le code SANDRE. Les deux, "
          "quand tu les as.", "",
          "Puis un compte rendu de 12 à 16 lignes : ce que tu as lu, ce que tu "
          "n'as pas pu lire et à quelles adresses, et les pièges d'identité "
          "rencontrés. **Ne recopie pas le CSV dans ta réponse.**"]
    return "\n".join(o)


# ---------------------------------------------------------------------------
# Le contrôle — ce qui bloque, et ce qui se signale seulement
# ---------------------------------------------------------------------------
def controler(lignes, rep, connus, origine="", sans_fichier=frozenset()):
    """(bloquants, signalements) — les deux listes sont des phrases."""
    bloquants, signalements = [], []
    # UN CODE SANDRE PORTE SOUVENT PLUSIEURS LIBELLÉS, et le contrôle doit le
    # savoir. Écrit d'abord comme un dictionnaire code → paramètre, il gardait
    # le dernier venu et déclarait alors que « le code et le libellé désignent
    # deux paramètres différents » — sur des lignes parfaitement justes.
    #
    # Constaté le 15 août 2026 sur le dalapon : le code 2094 porte « Dalapon
    # 85 » (838 mesures) ET « Dalapon spd » (6 153). L'agent, bloqué sur le
    # libellé de son lot, a écrit l'autre pour passer — c'est-à-dire que mon
    # faux positif a déplacé une identité d'un paramètre vers son voisin,
    # exactement ce que le contrôle existait pour empêcher. Le §2.13 vaut ici
    # aussi : un faux positif coûte plus cher qu'un faux négatif.
    #
    # Le libellé fait donc foi, le code ne sert qu'à confirmer. Un code partagé
    # est signalé, jamais bloqué.
    codes = {}
    for f in rep:
        if f["code"]:
            codes.setdefault(str(f["code"]), []).append(f)
    par_code = {c: v[0] for c, v in codes.items() if len(v) == 1}
    codes_partages = {c for c, v in codes.items() if len(v) > 1}
    par_libelle = {C.norm(f["libelle"]): f for f in rep}

    for ligne in lignes:
        qui = (ligne.get("libelle_norm") or ligne.get("code_parametre")
               or "(ligne sans clé)")
        etiquette = f"{origine}{qui}"

        for colonne in COLONNES:
            if ligne.get(colonne) is None:
                bloquants.append(f"{etiquette} : colonne « {colonne} » absente "
                                 "— la ligne n'a pas le bon nombre de champs")
                break
        else:
            texte = " ".join((ligne.get(c) or "") for c in ID.CHAMPS)

            for colonne in COLONNES:
                if ";" in (ligne.get(colonne) or ""):
                    bloquants.append(f"{etiquette} : point-virgule dans « "
                                     f"{colonne} » — la ligne se décalerait")

            for motif, quoi in ((VALEUR_UNITE, "une valeur de concentration"),
                                (AUTRES_UNITES, "une valeur avec son unité")):
                m = motif.search(texte)
                if m:
                    bloquants.append(f"{etiquette} : {quoi} — « {m.group(0)} ». "
                                     "Un seuil n'entre pas dans une identité")

            m = QUALIFICATIFS.search(texte)
            if m:
                bloquants.append(f"{etiquette} : qualificatif sanitaire — "
                                 f"« {m.group(0)} »")

            statut = (ligne.get("statut_autorisation") or "").strip()
            if statut and not UNE_DATE.search(statut):
                bloquants.append(f"{etiquette} : statut d'autorisation sans "
                                 "date — un statut sans millésime est faux (§2.5)")

            sources = [s.strip() for s in (ligne.get("sources") or "").split("|")
                       if s.strip()]
            if not sources:
                bloquants.append(f"{etiquette} : aucune source — une identité "
                                 "non sourcée ne s'affiche pas")
            for s in sources:
                if connus and s not in connus:
                    bloquants.append(f"{etiquette} : source « {s} » inconnue de "
                                     "docs/INDEX_SOURCES.md")
                elif s in sans_fichier:
                    signalements.append(
                        f"{etiquette} : source « {s} » cataloguée mais SANS "
                        "fichier dans Sources/ — vérifier qu'elle a bien été lue")

            fiab = (ligne.get("fiabilite") or "").strip()
            if fiab not in ("verifie", "a_verifier"):
                bloquants.append(f"{etiquette} : fiabilité « {fiab} » — attendu "
                                 "verifie ou a_verifier")
            elif fiab != "verifie":
                signalements.append(f"{etiquette} : en « à vérifier », signalé "
                                    "comme tel dans la sortie publique")

            if not any((ligne.get(c) or "").strip() for c in ID.CHAMPS):
                bloquants.append(f"{etiquette} : les quatre champs sont vides")

            # Signalement et non blocage : une phrase trop longue est juste,
            # seulement illisible. Constaté sur le lot « métaux » du 15 août
            # 2026 — dix lignes sourcées, sans un bloquant, et chacune portant
            # son appareil bibliographique alors que la colonne `sources`
            # l'affiche déjà. Le défaut était dans la consigne ; ce compteur
            # existe pour qu'il se voie sans relire les dix lignes à la main.
            for colonne in ID.CHAMPS:
                n = len((ligne.get(colonne) or "").strip())
                if n > 250:
                    signalements.append(
                        f"{etiquette} : « {colonne} » fait {n} caractères — "
                        "viser 150, l'attribution vit dans la colonne sources")

            code = (ligne.get("code_parametre") or "").strip()
            cle = C.norm(ligne.get("libelle_norm") or "")
            trouve = par_code.get(code) or par_libelle.get(cle)
            if not trouve:
                bloquants.append(f"{etiquette} : ne correspond à aucun paramètre "
                                 "du corpus — ni par code, ni par libellé")
            elif code in codes_partages:
                autres = ", ".join(f'« {x["libelle"]} »' for x in codes[code]
                                   if C.norm(x["libelle"]) != cle)
                if autres:
                    signalements.append(
                        f"{etiquette} : le code {code} est partagé avec "
                        f"{autres} — cette identité ne vaut que pour le libellé "
                        "écrit ici, et l'autre reste à sourcer séparément")
            elif code and cle and par_code.get(code) and par_libelle.get(cle) \
                    and par_code[code]["libelle"] != par_libelle[cle]["libelle"]:
                bloquants.append(
                    f"{etiquette} : le code {code} et le libellé désignent deux "
                    f"paramètres différents — « {par_code[code]['libelle']} » "
                    f"contre « {par_libelle[cle]['libelle']} »")
    return bloquants, signalements


def reponses():
    if not os.path.isdir(REPONSES):
        return []
    return sorted(os.path.join(REPONSES, f) for f in os.listdir(REPONSES)
                  if f.endswith(".csv"))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--etat", action="store_true")
    p.add_argument("--briefs", action="store_true")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--integrer", action="store_true")
    p.add_argument("--remplacer", action="store_true",
                   help="reprend aussi les lignes qui diffèrent de la version "
                        "déjà versée, au lieu de les sauter")
    p.add_argument("--version", help="figeage à interroger")
    p.add_argument("--lot", help="restreindre à un lot")
    a = p.parse_args()

    if a.verifier or a.integrer:
        rep, version = repertoire(a.version)
        connus = codes_sources_connus()
        sans_fichier = codes_sans_fichier(connus)
        tables = ID.charger()
        tous_bloquants, tous_signalements, a_verser = [], [], []
        a_reprendre, deja = [], 0
        for chemin in reponses():
            lignes = lire_table(chemin)
            b, s = controler(lignes, rep, connus,
                             origine=os.path.basename(chemin) + " · ",
                             sans_fichier=sans_fichier)
            tous_bloquants += b
            tous_signalements += s
            if not b:
                for ligne in lignes:
                    ancienne = ID.pour(tables, ligne.get("code_parametre"),
                                       ligne.get("libelle_norm"))
                    if ancienne:
                        # Identique : c'est un rejeu, on saute en silence — le
                        # compte suffit. DIFFÉRENTE : c'est une reprise, et la
                        # jeter sans le dire perdrait le travail. Constaté le
                        # 15 août 2026 sur l'atrazine : la ligne versée portait
                        # un statut vide, la nouvelle le statut enfin sourcé, et
                        # le message « déjà sourcée, sautée » se noyait dans une
                        # centaine de ses semblables. Un agent l'a manqué, moi
                        # aussi au premier passage.
                        if any((ligne.get(c) or "").strip()
                               != (ancienne.get(c) or "").strip()
                               for c in COLONNES):
                            a_reprendre.append(ligne)
                        else:
                            deja += 1
                        continue
                    a_verser.append(ligne)
        print(f"{len(reponses())} fichier(s) de réponse · "
              f"{len(a_verser)} nouvelle(s) · {len(a_reprendre)} reprise(s) · "
              f"{deja} déjà versée(s) à l'identique")
        for ligne in a_reprendre:
            print(f"  ≠ {ligne.get('libelle_norm')} : DIFFÈRE de la version "
                  "déjà versée — --remplacer pour la reprendre")
        for s in tous_signalements:
            print(f"  ~ {s}")
        for b in tous_bloquants:
            print(f"  ! {b}")
        if tous_bloquants:
            print(f"\n{len(tous_bloquants)} bloquant(s) — rien n'est versé.")
            sys.exit(1)
        if not a.integrer:
            print("\naucun bloquant.")
            return
        if a_reprendre and not a.remplacer:
            print(f"\n{len(a_reprendre)} reprise(s) NON versée(s) — relance avec "
                  "--remplacer pour qu'elles écrasent la version en place.")
        elif a_reprendre:
            # Réécriture sur place : la ligne reprise prend la place de
            # l'ancienne, l'ordre du fichier ne bouge pas et les commentaires
            # de tête sont conservés — ils portent la doctrine.
            #
            # L'appariement se fait par LIBELLÉ, jamais par code : un code
            # SANDRE porte souvent deux libellés, et reprendre par code
            # écraserait la ligne du voisin. C'est l'erreur qui s'est cachée
            # trois fois dans la journée du 15 août 2026, à trois endroits
            # différents du même dispositif.
            par_libelle = {C.norm(l.get("libelle_norm") or ""): l
                           for l in a_reprendre if (l.get("libelle_norm") or "").strip()}
            reprises, sortie = 0, []
            for l in io.open(TABLE, encoding="utf-8"):
                champs = l.rstrip("\n").split(";")
                cle = C.norm(champs[1]) if len(champs) > 1 else ""
                neuve = par_libelle.pop(cle, None) if cle else None
                if neuve is not None and not l.lstrip().startswith("#"):
                    sortie.append(";".join((neuve.get(c) or "")
                                           for c in COLONNES) + "\n")
                    reprises += 1
                else:
                    sortie.append(l)
            io.open(TABLE, "w", encoding="utf-8", newline="").writelines(sortie)
            print(f"\n{reprises} ligne(s) reprise(s) sur place")
            if par_libelle:
                print("  ! non retrouvée(s) à la reprise : "
                      + ", ".join(sorted(par_libelle)))
        with io.open(TABLE, "a", encoding="utf-8", newline="") as fh:
            for ligne in a_verser:
                fh.write(";".join((ligne.get(c) or "") for c in COLONNES) + "\n")
        print(f"{len(a_verser)} ligne(s) ajoutée(s) dans "
              f"{os.path.relpath(TABLE, RACINE)}")
        return

    rep, version = repertoire(a.version)
    cible, reste, par_lot, orphelins = a_faire(rep)
    print(f"version {version} · {len(cible)} substances qui pèsent "
          f"(bascule ou dépassement) · {len(cible) - len(reste)} sourcées · "
          f"{len(reste)} à faire\n")
    for nom, molecules in par_lot.items():
        if a.lot and nom != a.lot:
            continue
        print(f"  {nom:<14} {len(molecules):>4} à faire")
    if orphelins:
        print(f"  {'(hors lot)':<14} {len(orphelins):>4} — famille non prévue : "
              + ", ".join(sorted({f['famille'] or '?' for f in orphelins})))

    if a.briefs:
        os.makedirs(DOSSIERS, exist_ok=True)
        os.makedirs(REPONSES, exist_ok=True)
        print()
        for nom, molecules in par_lot.items():
            if a.lot and nom != a.lot:
                continue
            if not molecules:
                continue
            chemin = os.path.join(DOSSIERS, f"IDENTITE-{nom}.md")
            souche = nom.rsplit("-", 1)[0] if nom not in LOTS else nom
            io.open(chemin, "w", encoding="utf-8", newline="").write(
                brief(nom, molecules, LOTS[souche][1], version))
            print(f"  brief écrit : {os.path.relpath(chemin, RACINE)} "
                  f"({len(molecules)} substances)")


if __name__ == "__main__":
    main()

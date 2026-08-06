# -*- coding: utf-8 -*-
"""
Générateur de la fiche citoyenne standardisée — VERSION 1, CONTENU ÉCRIT À LA MAIN.

    python3 sortie/build_fiche.py     -> sortie/Resultat_Analyse_Standardise.html

État actuel : les sept communes témoins, leurs KPI et leurs textes d'analyse
sont écrits en dur dans le dictionnaire C ci-dessous. Ce fichier est donc un
GABARIT ÉDITORIAL, pas encore une sortie de la base.

CHANTIER (à faire en Claude Code) : dériver C de data/eau.duckdb, via
v_prelevement_verdict et v_mesures_verdict, pour que la fiche soit
reproductible et se régénère à chaque collecte. Tant que ce n'est pas fait,
toute valeur affichée ici doit être revérifiée contre la base avant
publication — c'est la seule partie du dépôt qui n'est pas traçable.

Rappel des garde-fous applicables à toute fiche (CLAUDE.md §2) :
  - aucune recommandation de filtration, d'équipement ou de produit ;
  - interroger la norme, pas les acteurs qui l'appliquent ;
  - un « non quantifié » n'est pas une absence : l'écrire « < LQ », jamais 0 ;
  - une valeur en fiabilite 'a_verifier' doit être signalée comme telle.
"""
import json
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICI = os.path.join(RACINE, "sortie")

PARAMS = json.load(open(os.path.join(RACINE, "data", "communes_params.json"),
                       encoding="utf-8"))

KPI_LABELS=["Complétude de l'analyse","PFAS — somme 20","PFAS somme 4 vs Danemark (2 ng/L)",
            "Pesticides / métabolites détectés","Nitrates","Équilibre calco-carbonique"]

C={
 "vourles":{"name":"Vourles","insee":"69268","sub":"Rhône (69) · couloir chimique sud de Lyon","dot":"rouge",
  "meta":[["Distributeur","Veolia 69 Sud"],["Ressource","Millery Mornant"],["Prélèvement","13/02/2026"],["Panel","401 paramètres · complet"]],
  "hubeau":"?code_commune=69268&size=500",
  "official":{"concl":"« Eau conforme aux limites de qualité et non conforme aux références de qualité. » (eau agressive)",
    "axes":[["Bactériologie","Conforme"],["Limites (santé)","Conforme"],["Références","Non conforme"]]},
  "admin":{"level":"ambre","v":"Conforme aux limites","d":"Non conforme aux références (eau agressive), mais toutes les limites sanitaires sont « respectées »."},
  "delta":"Derrière ce « conforme », le profil le plus chargé de la série : des <b>PFAS bien réels</b>, pas « sous le seuil ».",
  "cit":{"level":"rouge","v":"Non conforme (PFAS + cocktail)","d":"Somme des 20 PFAS à 62 ng/L (62 % de la limite UE) ; somme des 4 à 15 ng/L, soit 7,5× le seuil danois (2 ng/L). Profil dominé par des PFAS à chaîne courte, les plus difficiles à retenir."},
  "kpi":[{"val":"Complète · 401","note":"PFAS + pesticides","level":"vert"},
         {"val":"62 ng/L","note":"quantifié · 62 % de la limite UE","level":"rouge"},
         {"val":"× 7,5","note":"15 ng/L vs 2 ng/L","level":"rouge"},
         {"val":"2 métabolites","note":"chloridazone desphényl, R471811","level":"ambre"},
         {"val":"6,5 mg/L","note":"faibles","level":"vert"},
         {"val":"Agressive","note":"corrosive pour le réseau","level":"ambre"}],
  "analyse":[
   {"t":"Inventaire — des PFAS mesurés, pas « sous le seuil »","x":"Contrairement à d'autres communes où les PFAS restent masqués par un « &lt;… », ils sont ici quantifiés : somme des 20 = 0,062 µg/L, somme des 4 = 15 ng/L. Le profil est dominé par des chaînes courtes (PFHxA, PFPeA, PFBA) — précisément celles que le charbon actif retient mal."},
   {"t":"Écart légal ↔ sanitaire","x":"La somme des 4 PFAS à 15 ng/L est 7,5× le seuil danois et à rapprocher de la dose hebdomadaire très basse fixée par l'EFSA en 2020 (4,4 ng/kg, effets immunitaires chez l'enfant). S'ajoutent deux métabolites de pesticides (chloridazone desphényl 0,047, « pertinent » ; chlorothalonil R471811 0,064) et une trace de solvant industriel (tétrachloroéthylène 0,16 µg/L)."},
   {"t":"Effet cocktail","x":"On cumule PFAS + deux métabolites + solvant + sous-produits de chloration (THM 15 µg/L) : chacun « conforme », le mélange jamais évalué. Des effets de mélange à faibles doses ont pourtant été documentés (Kortenkamp ; EDC-MixRisk)."},
   {"t":"Lecture territoriale","x":"PFAS industriels + métabolites agricoles + solvant : une signature péri-urbaine mixte, cohérente avec le sud lyonnais. Le cas où l'on est exposé aux deux grandes familles de menaces à la fois."}],
  "verdict":{"level":"rouge","t":"« Conforme aux limites de qualité » — mais des PFAS réels à 62 % de la limite (et 7,5× le seuil danois sur la somme des 4), dominés par des chaînes courtes ; deux métabolites de pesticides ; une trace de solvant industriel ; une eau agressive. Le profil le plus chargé de la série."}
 },
 "montech":{"name":"Montech","insee":"82125","sub":"Tarn-et-Garonne (82) · plaine céréalière de la Garonne","dot":"rouge",
  "meta":[["Distributeur","SAUR"],["Ressource","UDI Montech"],["Prélèvement","14/01/2026"],["Panel","388 paramètres · complet"]],
  "hubeau":"?code_commune=82125&size=500",
  "official":{"concl":"« Eau conforme aux limites de qualité et non conforme aux références de qualité. » (eau agressive)",
    "axes":[["Bactériologie","Conforme"],["Limites (santé)","Conforme"],["Références","Non conforme"]]},
  "admin":{"level":"ambre","v":"Conforme aux limites","d":"Non conforme aux références (eau agressive) ; toutes les limites sanitaires « respectées »."},
  "delta":"Le cas emblématique du projet : <b>la même eau était non conforme en 2015 et « conforme » en 2026 — parce que la règle a changé, pas l'eau.</b>",
  "cit":{"level":"rouge","v":"Non conforme (bascule + cocktail)","d":"Deux métabolites au-dessus de l'ancienne limite de 0,1 (métolachlore ESA 0,14 ; chlorothalonil R471811 0,12), désormais tolérés jusqu'à 0,9 depuis leur reclassement « non pertinents » (ANSES, 29/04/2024). Huit pesticides coexistent."},
  "kpi":[{"val":"Complète · 388","note":"PFAS + pesticides","level":"vert"},
         {"val":"< 44 ng/L","note":"non quantifié à cette finesse","level":"ambre"},
         {"val":"non évaluable","note":"LQ 22× le seuil danois","level":"ambre"},
         {"val":"8 (dont 2 bascule)","note":"conformes 2026 / non 2016","level":"rouge"},
         {"val":"14 mg/L","note":"empreinte agricole nette","level":"ambre"},
         {"val":"Agressive","note":"corrosive pour le réseau","level":"ambre"}],
  "analyse":[
   {"t":"Inventaire — et les silences","x":"Huit pesticides/métabolites présents simultanément ; deux familles de sous-produits de chloration (THM 18,3 ; acides haloacétiques 7,1). Le silence décisif : « Somme des 20 PFAS &lt; 0,044 µg/L » ne veut pas dire zéro, mais « sous 44 ng/L, on ne sait pas » — soit 22× le seuil danois."},
   {"t":"Écart légal ↔ sanitaire — le changement de norme en direct","x":"Métolachlore ESA 0,14 et chlorothalonil R471811 0,12 dépassent l'ancienne limite de 0,1 µg/L. Depuis leur reclassement en métabolites « non pertinents » (ANSES, 29 avril 2024), ils sont jugés sur 0,9, plus sur 0,1. En 2015, cette eau aurait été déclarée non conforme sur les pesticides ; en 2026, la même eau est « conforme »."},
   {"t":"Effet cocktail","x":"Huit molécules agricoles co-présentes, chacune « conforme » isolément. La réglementation les évalue une à une ; les effets de mélange à faibles doses ne sont jamais mesurés."},
   {"t":"Lecture territoriale","x":"Nitrates 14, métabolites de métolachlore (maïs), chlorothalonil (fongicide) : la signature d'un bassin de grande culture. Les molécules-mères interdites ont disparu, leurs métabolites persistent et racontent l'usage passé."}],
  "verdict":{"level":"rouge","t":"Une eau « conforme aux limites » qui cache deux métabolites hors-normes d'il y a dix ans, un cocktail de huit pesticides, deux familles de sous-produits de chloration, des nitrates marquant une empreinte agricole, une eau corrosive, et des PFAS simplement sous le radar de la mesure. Conforme en 2026, non conforme en 2016 : la règle a changé, pas l'eau."}
 },
 "challet":{"name":"Challet","insee":"28068","sub":"Eure-et-Loir (28) · pleine Beauce céréalière","dot":"rouge",
  "meta":[["Distributeur","C'Chartres Eau"],["Ressource","Réseau Challet"],["Prélèvement","panel pesticides"],["Panel","225 paramètres · sans PFAS"]],
  "hubeau":"?code_commune=28068&size=500",
  "official":{"concl":"Eau de qualité chimique NON conforme (dépassement : atrazine déséthyl, chloridazone desphényl, chlorothalonil…).",
    "axes":[["Bactériologie","Conforme"],["Limites (santé)","Non conforme"],["Références","Conforme"]]},
  "admin":{"level":"rouge","v":"Non conforme","d":"L'administration elle-même déclare l'eau non conforme sur le plan chimique. Le mot « conforme » tombe."},
  "delta":"Ici les deux lectures <b>convergent</b> : même l'administration dit non. Un chlorothalonil à ~18× l'ancienne norme.",
  "cit":{"level":"rouge","v":"Non conforme (confirmé)","d":"Cinq métabolites simultanés, plusieurs au-dessus des seuils : chlorothalonil R471811 à 1,662 µg/L (~18× l'ancienne limite de 0,1, ~2× la vigilance 0,9). Un métabolite d'herbicide interdit depuis 2003 toujours présent."},
  "kpi":[{"val":"Partielle · 225","note":"PFAS non recherchés","level":"ambre"},
         {"val":"non mesuré","note":"absent du prélèvement","level":"gris"},
         {"val":"non mesuré","note":"absent du prélèvement","level":"gris"},
         {"val":"5 (4 en dépassement)","note":"chlorothalonil ×18","level":"rouge"},
         {"val":"48,3 mg/L","note":"tout près de la limite (50)","level":"rouge"},
         {"val":"n.d.","note":"non renseigné","level":"gris"}],
  "analyse":[
   {"t":"Inventaire — un cocktail de métabolites en dépassement","x":"Cinq métabolites/pesticides présents simultanément, plusieurs au-dessus des seuils : chlorothalonil R471811 1,662 ; atrazine déséthyl 0,110 ; chlorothalonil R417888 0,136 ; chloridazone desphényl 0,107 ; ESA métazachlore 0,105. Total pesticides 0,493, à la limite de la somme."},
   {"t":"Écart légal ↔ sanitaire","x":"Ici l'écart n'est même plus à démontrer : plusieurs paramètres franchissent la limite légale elle-même. L'atrazine déséthyl est le métabolite d'un herbicide interdit depuis 2003, toujours présent plus de vingt ans après."},
   {"t":"Effet cocktail","x":"Cinq molécules agricoles en mélange (fongicides, herbicides maïs et betterave). La réglementation les additionne à peine (« total » sous 0,5) ; elle n'évalue jamais leur action combinée."},
   {"t":"Lecture territoriale","x":"Pleine Beauce céréalière : l'aboutissement de la logique agricole, poussée jusqu'au dépassement. Un historique de perchlorates (> 4 µg/L, 2022-2023) avait conduit à déconseiller cette eau pour les biberons des nourrissons de moins de 6 mois."}],
  "verdict":{"level":"rouge","t":"Une eau officiellement non conforme : cocktail de cinq métabolites, un chlorothalonil à dix-huit fois l'ancienne norme, un métabolite d'herbicide interdit depuis vingt ans, et un historique de perchlorates ayant motivé une restriction pour les biberons. Le contrepoint parfait d'une eau propre."}
 },
 "ally":{"name":"Ally","insee":"15003","sub":"Cantal (15) · ressource de montagne, Massif central","dot":"ambre",
  "meta":[["Distributeur","Synd. Ally-Escorailles"],["Ressource","Ally-Escorailles-Brageac"],["Prélèvement","panel complet"],["Panel","342 paramètres · complet"]],
  "hubeau":"?nom_commune=ALLY&size=500",
  "official":{"concl":"« Qualité sanitaire non satisfaisante » (ARS) — eau agressive.",
    "axes":[["Bactériologie","Conforme"],["Limites (santé)","Conforme"],["Références","Non conforme"]]},
  "admin":{"level":"ambre","v":"Non satisfaisante","d":"L'ARS déclare la qualité sanitaire « non satisfaisante » — en raison de l'agressivité de l'eau, non d'un polluant."},
  "delta":"Paradoxe inverse : <b>le meilleur résultat PFAS de la série</b> (1,5 ng/L, sous le seuil danois), sur analyse complète — mais une eau agressive et déjà marquée par un métabolite.",
  "cit":{"level":"ambre","v":"Bonne eau, deux réserves","d":"PFAS quasi absents (1,5 ng/L, sous le seuil danois de 2) : rare et réel. Mais eau très douce donc agressive (corrosive pour le réseau), et un métabolite (ESA métolachlore) déjà présent, signalé par l'ARS comme marqueur de vulnérabilité."},
  "kpi":[{"val":"Complète · 342","note":"PFAS + pesticides","level":"vert"},
         {"val":"1,5 ng/L","note":"le meilleur de la série","level":"vert"},
         {"val":"Conforme","note":"sous le seuil danois (2)","level":"vert"},
         {"val":"1 métabolite","note":"ESA métolachlore (vulnérabilité)","level":"ambre"},
         {"val":"6,1 mg/L","note":"faibles","level":"vert"},
         {"val":"Agressive","note":"eau très douce (100 µS/cm)","level":"rouge"}],
  "analyse":[
   {"t":"La bonne nouvelle (rare et réelle)","x":"Somme des 20 PFAS = 1,5 ng/L, pratiquement le bruit de fond analytique, sous le seuil danois. Ici les PFAS ont été cherchés et sont quasi absents : l'avantage d'une ressource d'altitude, loin des sources industrielles."},
   {"t":"Pourquoi l'ARS conclut « non satisfaisante »","x":"Eau très douce et peu minéralisée (conductivité 100, TH 3,6, calcium 8,5), typique des sols granitiques/volcaniques : corrosive, elle dissout les matériaux à son contact (aluminium 96 µg/L). Elle attaque le réseau."},
   {"t":"Un métabolite déjà présent","x":"ESA métolachlore détecté (sous le seuil), mais signalé explicitement par l'ARS comme marqueur de « vulnérabilité de la ressource ». Trouver ce métabolite jusque dans un captage du Cantal en dit long sur l'ubiquité de ces molécules."},
   {"t":"Lecture territoriale","x":"Ressource de montagne : peu de pression agricole, éloignée de l'industrie — d'où l'absence de PFAS. Mais l'agressivité et l'ubiquité des métabolites, les deux obstacles récurrents d'une « bonne » eau, sont déjà là."}],
  "verdict":{"level":"ambre","t":"Le meilleur résultat PFAS de la série (1,5 ng/L), sur un panel complet — et pourtant l'eau reste agressive et déjà marquée par un métabolite. Une ressource d'altitude presque irréprochable, que sa corrosivité disqualifie comme « satisfaisante »."}
 },
 "cabrerets":{"name":"Cabrerets","insee":"46040","sub":"Lot (46) · Causses calcaires du Quercy","dot":"vert",
  "meta":[["Distributeur","SYDED"],["Ressource","Station Font Polémie"],["Prélèvement","30/03/2026"],["Panel","400 paramètres · complet"]],
  "hubeau":"?code_commune=46040&size=500",
  "official":{"concl":"« Eau conforme aux exigences de qualité en vigueur pour l'ensemble des paramètres mesurés » — y compris les références.",
    "axes":[["Bactériologie","Conforme"],["Limites (santé)","Conforme"],["Références","Conforme"]]},
  "admin":{"level":"vert","v":"Conforme","d":"Conforme y compris aux références. Sans le moindre « cependant »."},
  "delta":"Ici les deux lectures <b>se rejoignent</b> : une eau vraiment bonne, confirmée par l'analyse complète.",
  "cit":{"level":"vert","v":"Bonne eau (analyse complète)","d":"PFAS cherchés et absents (somme 20 < 29 ng/L, somme 4 < 4 ng/L), zéro pesticide sur panel large, nitrates les plus bas de la série, minéralisation calcaire à l'équilibre. Le contre-exemple positif."},
  "kpi":[{"val":"Complète · 400","note":"PFAS + pesticides","level":"vert"},
         {"val":"< 29 ng/L","note":"cherché, absent","level":"vert"},
         {"val":"< 4 ng/L","note":"cherché, absent","level":"vert"},
         {"val":"0","note":"aucun détecté (panel large)","level":"vert"},
         {"val":"4,6 mg/L","note":"les plus bas de la série","level":"vert"},
         {"val":"Équilibrée","note":"calcaire (584 µS/cm)","level":"vert"}],
  "analyse":[
   {"t":"Inventaire — aucun silence gênant","x":"PFAS : somme des 20 non détectée (&lt; 0,029 µg/L), somme des 4 non détectée (&lt; 0,004). Cette fois les PFAS ont été cherchés et sont absents. Aucun pesticide détecté sur un panel large (métolachlore, chlorothalonil, chloridazone, atrazine, glyphosate…)."},
   {"t":"Écart légal ↔ sanitaire — favorable","x":"Nitrates 4,6 mg/L : les plus bas de la série. THM 0,40 µg/L : quasi nuls. Eau calcaire à l'équilibre (calcium 118, pH 7,3), non agressive : une eau minéralisée par le calcaire n'attaque pas les canalisations."},
   {"t":"Effet cocktail","x":"Sans objet : aucune substance de synthèse détectée. À l'échelle de cette enquête, c'est l'exception plutôt que la règle."},
   {"t":"Lecture territoriale","x":"Source karstique des Causses du Quercy, en zone de faible agriculture intensive, naturellement filtrée par le calcaire et éloignée des sources industrielles de PFAS. Le profil-type d'une eau protégée."}],
  "verdict":{"level":"vert","t":"Une eau vraiment propre sur analyse complète : PFAS cherchés et absents, zéro pesticide, nitrates les plus bas de la série, minéralisation calcaire à l'équilibre. Le contre-exemple positif — celui qui tient la route quand on cherche vraiment tout."}
 },
 "rostrenen":{"name":"Rostrenen","insee":"22266","sub":"Côtes-d'Armor (22) · Bretagne granitique","dot":"gris","incomplete":True,
  "meta":[["Distributeur","SAUR"],["Ressource","Rostrenen par Kerné Uhel"],["Prélèvement","secours"],["Panel","115 paramètres · INCOMPLET"]],
  "hubeau":"?code_commune=22266&size=500",
  "official":{"concl":"« Eau conforme aux exigences de qualité pour l'ensemble des paramètres mesurés » — y compris les références.",
    "axes":[["Bactériologie","Conforme"],["Limites (santé)","Conforme"],["Références","Conforme"]]},
  "admin":{"level":"vert","v":"Conforme","d":"Conforme, y compris aux références. En apparence, le bon élève."},
  "delta":"Mais l'analyse est <b>incomplète</b> : ni panel pesticides complet, ni ligne PFAS. Tout est dans le mot « mesurés ».",
  "cit":{"level":"gris","v":"Non concluant (analyse incomplète)","d":"115 paramètres seulement, sans PFAS ni panel pesticides complet. Or l'autre source de la commune (Coadernault) était contaminée aux PFAS depuis 2017 — 359 ng/L en moyenne, pic à 837, fermée en urgence à l'été 2024. Un « conforme » ne dit rien de ce qui n'a pas été cherché."},
  "kpi":[{"val":"Incomplète · 115","note":"ni PFAS ni pesticides complets","level":"gris"},
         {"val":"non recherché","note":"angle mort","level":"gris"},
         {"val":"non recherché","note":"angle mort","level":"gris"},
         {"val":"panel incomplet","note":"non concluant","level":"gris"},
         {"val":"1,4 mg/L","note":"remarquablement bas","level":"vert"},
         {"val":"Douce","note":"eau de surface (THM 23)","level":"ambre"}],
  "analyse":[
   {"t":"Ce que le bulletin montre","x":"Nitrates 1,4 mg/L (très bas), aucun pesticide détecté, eau douce équilibrée, bactériologie parfaite. Seul signal : THM 23,2 µg/L, qui signent une eau de surface chlorée. Sur le papier : très bonne eau."},
   {"t":"Ce que le bulletin NE montre pas — décisif","x":"Ce prélèvement ne comporte ni panel pesticides complet, ni ligne PFAS : ces familles n'ont pas été recherchées. « Conforme pour l'ensemble des paramètres mesurés » : tout est dans le mot « mesurés »."},
   {"t":"Le contexte que le bulletin tait","x":"L'enquête du média Splann! (mars 2025) a révélé que l'autre source de Rostrenen — le captage de Coadernault, qui alimentait les deux tiers de la commune — était contaminée aux PFAS depuis 2017 : 359 ng/L en moyenne, pic à 837 ng/L, 312 ng/L dans l'eau distribuée en juillet 2024. Fermée en urgence à l'été 2024."},
   {"t":"La leçon","x":"Cette eau paraît irréprochable en grande partie parce qu'on n'a pas cherché ce qui posait problème juste à côté. Un « conforme » n'est pas une garantie d'innocuité : c'est le reflet d'un panel de mesure — et de ses angles morts."}],
  "verdict":{"level":"gris","t":"Un bulletin propre… surtout parce que l'essentiel n'y a pas été cherché — sur une commune dont l'autre source cachait trois fois la limite de PFAS pendant des années, sans que la population en soit informée. L'illustration parfaite qu'un « conforme » ne dit rien de ce qui n'a pas été mesuré."}
 }
,
 "saintes":{"name":"Saintes","insee":"17415","sub":"Charente-Maritime (17) · bassin de la Charente","dot":"ambre",
  "meta":[["Distributeur","AGUR"],["Ressource","Diconche File 2"],["Prélèvement","05/03/2026"],["Panel","370 paramètres · complet"]],
  "hubeau":"?code_commune=17415&size=500 (bulletin complet du 05/03/2026, page 2)",
  "official":{"concl":"« Eau d'alimentation conforme aux exigences de qualité en vigueur pour l'ensemble des paramètres mesurés. »",
    "axes":[["Bactériologie","Conforme"],["Limites (santé)","Conforme"],["Références","Conforme"]]},
  "admin":{"level":"vert","v":"Conforme","d":"Conforme pour l'ensemble des paramètres mesurés, sans réserve."},
  "delta":"Derrière ce « conforme » complet : des <b>nitrates à 41 mg/L</b> (82 % de la limite) et un métabolite de fongicide à 92 % de l'ancienne norme — mais, pour une fois, des PFAS réellement absents.",
  "cit":{"level":"ambre","v":"Conforme, empreinte agricole","d":"PFAS réellement absents (analyse fine, LQ ~1 ng/L). Mais nitrates à 41 mg/L — environ 10× le repère sanitaire le plus strict — et chlorothalonil R471811 à 0,092 µg/L, soit 92 % de l'ancienne limite de 0,1 (aujourd'hui tolérée jusqu'à 0,9)."},
  "kpi":[{"val":"Complète · 370","note":"PFAS + pesticides","level":"vert"},
         {"val":"non détecté","note":"analyse fine (LQ ~1 ng/L)","level":"vert"},
         {"val":"non détecté","note":"PFAS individuels < 1 ng/L, sous le seuil danois","level":"vert"},
         {"val":"1 métabolite","note":"chlorothalonil R471811 à 92 % de l'ancienne norme","level":"ambre"},
         {"val":"41 mg/L","note":"82 % de la limite · ~10× le repère sanitaire strict","level":"ambre"},
         {"val":"À l'équilibre","note":"non agressive · 527 µS/cm","level":"vert"}],
  "analyse":[
   {"t":"Inventaire — et, pour une fois, peu de silences","x":"Sur 370 paramètres, les PFAS ont été cherchés à très fine résolution (LQ ~1 ng/L) et ne sont pas détectés : l'absence est ici réellement démontrée, y compris face au seuil danois (2 ng/L). Une seule molécule de synthèse quantifiée : le chlorothalonil R471811 à 0,092 µg/L."},
   {"t":"Écart légal ↔ sanitaire","x":"Deux écarts. Les nitrates à 41 mg/L sont conformes (limite 50) mais atteignent environ 10× le repère sanitaire émergent (cohorte danoise, ~3,9 mg/L) et 4× le repère nourrissons (10 mg/L). Le chlorothalonil R471811 à 0,092 est à 92 % de l'ancienne limite de 0,1 — aujourd'hui jugé sur 0,9, il dispose de 10× de marge : une bascule réglementaire en germe."},
   {"t":"Effet cocktail","x":"Quasi sans objet : une seule molécule de synthèse détectée, pas de mélange. C'est la différence nette avec les eaux de grande culture chargées de métabolites."},
   {"t":"Lecture territoriale","x":"Eau de la Charente traitée à l'usine de Diconche (AGUR, eau de surface). Le chlorothalonil (fongicide céréalier) et les nitrates signent l'empreinte agricole du bassin ; le traitement livre néanmoins une eau à l'équilibre et exempte de PFAS."}],
  "verdict":{"level":"ambre","t":"Une eau officiellement « conforme pour l'ensemble des paramètres » — et réellement sans PFAS, ce qui est rare et à souligner. Mais des nitrates à 41 mg/L (82 % de la limite, ~10× le repère sanitaire strict) et un métabolite de fongicide à 92 % de l'ancienne norme trahissent une empreinte agricole nette. Bonne nouvelle sur les PFAS, vigilance sur les nitrates et le chlorothalonil."}
 }
}
ORDER=["saintes","vourles","montech","challet","ally","cabrerets","rostrenen"]

def j(x):
    return json.dumps(x, ensure_ascii=False)


html = open(os.path.join(ICI, "_template.html"), encoding="utf-8").read()
html = html.replace("/*__KPI_LABELS__*/", "const KPI_LABELS=" + j(KPI_LABELS) + ";")
html = html.replace("/*__C__*/", "const C=" + j(C) + ";")
html = html.replace("/*__PARAMS__*/", "const PARAMS=" + j(PARAMS) + ";")
html = html.replace("/*__ORDER__*/", "const ORDER=" + j(ORDER) + ";")

destination = os.path.join(ICI, "Resultat_Analyse_Standardise.html")
open(destination, "w", encoding="utf-8").write(html)
print(f"fiche générée : {destination} ({round(len(html)/1024)} Ko)")

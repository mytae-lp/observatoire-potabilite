/* ===========================================================================
   Rendu d'une fiche de bulletin. Partagé par la fiche autonome et par la
   vitrine, pour que les deux disent exactement la même chose.

   Attend cinq variables globales, produites par le générateur Python :
     KPI_LABELS  les six libellés d'indicateurs, dans l'ordre
     DICT        les scalaires de la page, déposés une fois et partagés
     CFORM       les combinaisons de clés rencontrées dans C
     CENC        un bulletin par clé : identité, verdicts, traçabilité
     PCOLS       le détail paramètre par paramètre, en colonnes
     ORDER       l'ordre d'affichage des clés

   Ce fichier ne calcule aucun verdict. Il en affiche. Tout ce qu'il montre
   vient des tables figées, estampillées de la version de référentiel qui les
   a produites (CLAUDE.md §8bis : « ne jamais recalculer un verdict à la volée
   dans l'interface »).
   =========================================================================== */

/* Décodage. DICT/CFORM/CENC/PCOLS portent exactement la même information que
   les anciens C et PARAMS, écrite sans répéter à chaque ligne et à chaque
   instantané les noms de champs, les libellés et les explications longues
   (motif et mesures : sortie/build_fiche.py).

   Ces décodeurs rendent des objets STRICTEMENT identiques à ceux d'avant —
   c'est ce qui permet que rien d'autre dans ce fichier n'ait eu à changer.
   Toute modification du format se fait des deux côtés à la fois. */
const scalaire = i => i === 0 ? null : DICT[i - 1];

/* C : structure hétérogène. Un entier est un scalaire ; un tableau dont le
   premier élément est un entier NÉGATIF est un objet, et ce nombre désigne sa
   combinaison de clés ; tout autre tableau est une liste. */
const C = (function decode(x){
  if(!Array.isArray(x)) return scalaire(x);
  if(typeof x[0] === "number" && x[0] < 0){
    const noms = CFORM[-x[0] - 1], o = {};
    for(let k = 0; k < noms.length; k++) o[noms[k]] = decode(x[k + 1]);
    return o;
  }
  return x.map(decode);
})(CENC);

/* PARAMS : table régulière, donc rendue en colonnes. */
const PARAMS = (function(){
  const out = {};
  for(const cle in PCOLS){
    const c = PCOLS[cle], n = c.p.length, lignes = new Array(n);
    for(let k = 0; k < n; k++)
      lignes[k] = { p: scalaire(c.p[k]), v: scalaire(c.v[k]),
                    s: scalaire(c.s[k]), g: scalaire(c.g[k]),
                    d: false, x: false, i: false,
                    a4: false, b: false, a: false, lqr: null, s16: null };
    /* Les drapeaux ne portent que les rangs où ils sont vrais. */
    ["d", "x", "i", "a4", "b", "a"].forEach(f =>
      c[f].forEach(k => lignes[k][f] = true));
    c.lqr.forEach(([k, v]) => lignes[k].lqr = scalaire(v));
    c.s16.forEach(([k, v]) => lignes[k].s16 = scalaire(v));
    out[cle] = { count: c.n, params: lignes };
  }
  return out;
})();

let CUR = ORDER[0], detOnly = false, sigOnly = false;

function el(t, c, h){ const e = document.createElement(t); if(c) e.className = c;
  if(h != null) e.innerHTML = h; return e; }
function txt(t, c, s){ const e = document.createElement(t); if(c) e.className = c;
  e.textContent = s == null ? "" : s; return e; }
function byId(i){ return document.getElementById(i); }
function setPill(id, level, s){ const p = byId(id);
  p.className = "pill " + (level || "gris");
  p.querySelector("span:last-child").textContent = s; }

/* Les trois états, dans l'ordre où ils priment l'un sur l'autre : un
   dépassement l'emporte sur une bascule, une bascule sur un indéterminé. La
   ligne porte l'information la plus forte, jamais la plus rassurante. */
function etat(r){
  if(r.x) return ["dep", "Dépassement"];
  if(r.b) return ["bas", "Bascule"];
  /* Le plafond analytique (chantier C4) passe AVANT l'indéterminé ordinaire :
     c'est la forme la plus forte du troisième état. Là où l'indéterminé dit
     « on ne sait pas si le repère le plus strict est tenu », celui-ci dit
     « on ne sait pas si la limite réglementaire est tenue », et il porte son
     chiffre. C'est aussi le seul « non quantifié » qu'il serait faux de lire
     comme rassurant. */
  if(r.a4) return ["ind aveugle", "LQ au-dessus du seuil"];
  if(r.i) return ["ind", "Indéterminé"];
  if(r.d) return ["det", "Quantifiée"];
  return ["ok", "Sous la LQ"];
}

/* Nombre à la française, pour les valeurs composées côté navigateur. */
function fr(x){ return String(x).replace(".", ","); }

const GRILLE = {"2016":"grille 2016 — applicable à cette date",
                "2026":"grille en vigueur", "declare":"limite déclarée par la source",
                "aucune":"aucun seuil de comparaison"};

function renderTable(){
  const rows = PARAMS[CUR].params;
  const f = (byId("bfilter").value || "").toLowerCase();
  const tb = byId("btable");
  tb.innerHTML = "";
  let shown = 0, aVerifier = 0;
  rows.forEach(r => {
    if(detOnly && !r.d) return;
    if(sigOnly && !(r.x || r.b || r.i)) return;
    if(f && !r.p.toLowerCase().includes(f)) return;
    shown++;
    if(r.a) aVerifier++;
    const [cls, libelle] = etat(r);
    const tr = el("tr", cls);

    const tdp = txt("td", null, r.p);
    if(r.a){ const s = txt("span", "av", " ⚠");
      s.title = "Valeur de seuil non confirmée sur source primaire (fiabilite = a_verifier)";
      tdp.appendChild(s); }
    tr.appendChild(tdp);

    tr.appendChild(txt("td", "num", r.v));

    const tds = txt("td", "num", r.s || "—");
    if(r.g) tds.appendChild(txt("span", "grille", GRILLE[r.g] || r.g));
    if(r.b && r.s16) tds.appendChild(txt("span", "grille", "en 2016 : " + r.s16));
    /* La mention demandée au chantier C4, sur la ligne même. « 0,5 » ne se lit
       pas ; « 5 × le seuil » se lit. */
    if(r.a4) tds.appendChild(txt("span", "lq-mention",
      "LQ " + String(r.v).replace(/^</, "")
      + (r.lqr ? " — " + fr(r.lqr) + " × ce seuil" : "")));
    tr.appendChild(tds);

    const tde = el("td");
    tde.appendChild(txt("span", "etat " + cls, libelle));
    tr.appendChild(tde);

    tb.appendChild(tr);
  });

  const av = byId("bAVerifier");
  av.innerHTML = "";
  if(aVerifier){
    av.appendChild(txt("div", "flag-a-verifier",
      "⚠ " + aVerifier + " ligne(s) affichée(s) reposent sur un seuil marqué "
      + "« à vérifier » : la valeur est plausible mais n'a pas été confirmée sur une "
      + "source primaire. Elle est signalée ici plutôt que présentée comme acquise."));
  }
  byId("bnote").textContent =
    shown + " ligne(s) affichée(s) sur " + rows.length + " paramètres du prélèvement. "
    + "Un paramètre sans seuil de comparaison figure quand même : le taire reviendrait "
    + "à masquer ce qu'on ne sait pas noter.";
}

function toCsv(){
  const rows = PARAMS[CUR].params, d = C[CUR];
  const q = s => '"' + String(s == null ? "" : s).replace(/"/g, '""') + '"';
  let out = "# Observatoire de la potabilite reglementaire — bulletin " + d.name
          + " (" + d.insee + "), preleve le " + d.date_iso + "\n"
          + "# referentiel " + d.version_referentiel + ", calcule le " + d.calcule_le
          + " — donnees Hub'Eau/SISE-Eaux (Licence Ouverte), referentiel ODbL 1.0\n"
          + "# le seuil est celui APPLICABLE A LA DATE du prelevement, pas celui du jour\n"
          + "# LQ/seuil : rapport de la limite de quantification du laboratoire au seuil,\n"
          + "#   quand elle lui est superieure — l'analyse ne conclut alors pas\n"
          + "Parametre;Valeur mesuree;Seuil applicable a la date;Grille;Etat;Seuil a verifier;"
          + "LQ/seuil\n";
  rows.forEach(r => {
    out += [q(r.p), q(r.v), q(r.s), q(r.g), q(etat(r)[1]), q(r.a ? "oui" : "non"),
            q(r.a4 ? r.lqr : "")].join(";") + "\n";
  });
  const blob = new Blob(["﻿" + out], {type: "text/csv;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "bulletin_" + d.name.replace(/[^\w-]/g, "_") + "_" + d.insee
             + "_" + d.date_iso + ".csv";
  a.click();
  URL.revokeObjectURL(a.href);
}

/* ---------------------------------------------------------------------------
   LE BANDEAU DE TÊTE

   Le projet tient en une phrase : « ce n'est pas l'eau qui est devenue
   potable, c'est la limite qui a bougé ». Cette phrase doit être la première
   chose lue, et elle doit être démontrée sur place — pas illustrée.

   D'où la règle graduée : une mesure au-dessus de la limite du jour, on le dit
   d'abord ; sinon une bascule, et on montre la mesure entre ses deux seuils
   sur une même échelle ; sinon un indéterminé, qui n'est pas un conforme ;
   sinon rien, et on le dit sans triompher — l'absence de dépassement porte sur
   ce qui a été cherché, pas sur ce qui existe.
   --------------------------------------------------------------------------- */
function jauge(valeur, s16, sApplicable, unite){
  /* Trois repères sur une même règle : la limite de 2016, la mesure, la limite
     d'aujourd'hui. L'échelle va jusqu'à 1,15 fois la plus grande des trois,
     pour que le déplacement se voie sans écraser la mesure contre le bord.

     La même jauge sert aux bascules ET aux dépassements. Pour un dépassement,
     elle montre de combien la mesure franchit son seuil — et souvent, de
     beaucoup plus loin encore, l'ancienne limite. */
  const v = parseFloat(String(valeur).replace(",", ".")),
        a = s16 == null ? NaN : parseFloat(String(s16).replace(",", ".")),
        b = parseFloat(String(sApplicable).replace(",", "."));
  if(!isFinite(v) || !isFinite(b) || b <= 0) return null;
  const u = unite ? " " + unite : "";

  const bornes = [v, b].concat(isFinite(a) ? [a] : []);
  const max = Math.max.apply(null, bornes) * 1.15;
  const pc = x => Math.max(0, Math.min(100, (x / max) * 100));

  const g = el("div", "jauge" + (v > b ? " depasse" : ""));
  const piste = el("div", "piste");
  if(isFinite(a) && a < b){
    /* La zone violette est l'écart entre les deux grilles : tout ce qui tombe
       dedans était non conforme hier et ne l'est plus. */
    const zone = el("div", "zone-bascule");
    zone.style.left = pc(a) + "%";
    zone.style.width = Math.max(0, pc(b) - pc(a)) + "%";
    piste.appendChild(zone);
  }
  if(v > b){
    const excede = el("div", "zone-depasse");
    excede.style.left = pc(b) + "%";
    excede.style.width = Math.max(0, pc(v) - pc(b)) + "%";
    piste.appendChild(excede);
  }
  g.appendChild(piste);

  const rep = (x, cls, lab) => {
    const m = el("div", "repere " + cls);
    m.style.left = pc(x) + "%";
    m.appendChild(el("i"));
    m.appendChild(txt("span", null, lab));
    g.appendChild(m);
  };
  if(isFinite(a) && a !== b) rep(a, "s16", s16 + " en 2016");
  rep(b, "sapp", sApplicable + " aujourd'hui");
  rep(v, "mesure", valeur + u);
  return g;
}

function renderHero(d){
  const zone = byId("hero");
  if(!zone) return;
  zone.innerHTML = "";
  const h = d.hero || {};
  const bloc = el("section", "hero " + (h.niveau || "gris"));

  /* Trois natures, que l'administration sépare elle-même dans ses conclusions,
     et que ce bandeau confondait : une limite de qualité est sanitaire, une
     référence ne l'est pas, une valeur de vigilance n'est pas opposable.
     Annoncer « 5 dépassements » quand les cinq portent sur un métabolite
     reclassé « non pertinent » dit au lecteur l'inverse de ce que conclut
     l'ARS sur le même bulletin. */
  const nat = h.natures || {};
  let titre, sous;
  if(h.nb_depassements && nat.limite){
    titre = nat.limite + (nat.limite > 1
      ? " paramètres dépassaient la limite de qualité applicable ce jour-là"
      : " paramètre dépassait la limite de qualité applicable ce jour-là");
    sous = "Le verdict est rendu contre la grille en vigueur <b>à la date du "
         + "prélèvement</b> : un reclassement n'est pas rétroactif.";
    const autres = (nat.reference || 0) + (nat.vigilance || 0);
    if(autres) sous += " S'y ajoutent " + autres + " mesure(s) au-dessus d'une "
      + "<b>référence de qualité ou d'une valeur de vigilance</b>, qui ne sont pas "
      + "des non-conformités sanitaires.";
  } else if(h.nb_depassements){
    /* Aucune limite franchie. Le bulletin est conforme au sens sanitaire, et
       le dire autrement serait le faux positif que le §2.13 dit coûter le plus
       cher au projet. */
    titre = "Aucune limite de qualité dépassée";
    sous = h.nb_depassements + " mesure(s) se situent au-dessus d'une <b>valeur de "
         + "vigilance ou d'une référence de qualité</b> — une valeur indicative, sans "
         + "portée opposable, ou un repère de bon fonctionnement. "
         + "<b>Ce n'est pas une non-conformité sanitaire</b>, et l'administration ne la "
         + "compte pas comme telle.";
  } else if(h.nb_bascules){
    titre = "Conforme aujourd'hui. Ne l'aurait pas été il y a dix ans.";
    sous = h.nb_bascules + (h.nb_bascules > 1
      ? " mesures ont changé de statut sans que l'eau change."
      : " mesure a changé de statut sans que l'eau change.")
      + " Ce n'est pas la ressource qui s'est améliorée : c'est la limite qui a bougé.";
  } else if(h.nb_indetermines){
    titre = "Aucun dépassement, et " + h.nb_indetermines
      + (h.nb_indetermines > 1 ? " paramètres indéterminés" : " paramètre indéterminé");
    sous = "Pour ceux-là, la limite de quantification du laboratoire se situe "
         + "au-dessus du seuil de comparaison : on ne peut pas affirmer que le seuil "
         + "est respecté. <b>Un indéterminé n'est pas un conforme.</b>";
  } else if(h.nb_aveugles){
    /* Annoncer « aucun dépassement » quand une part de l'analyse ne pouvait
       pas conclure serait exactement la demi-vérité que l'outil dénonce
       (chantier C4). */
    titre = "Aucun dépassement — et " + h.nb_aveugles
      + (h.nb_aveugles > 1 ? " paramètres que l'analyse ne pouvait pas trancher"
                           : " paramètre que l'analyse ne pouvait pas trancher");
    sous = "Pour ceux-là, la limite de quantification du laboratoire se situe "
         + "au-dessus de la <b>limite réglementaire elle-même</b> : sous cette valeur "
         + "l'analyse ne voit rien, là précisément où la conformité se joue. "
         + "<b>Ce n'est ni un conforme, ni un dépassement.</b>";
  } else {
    titre = "Aucun dépassement, aucune bascule";
    sous = "Sur ce qui a été cherché. Une eau n'est jamais déclarée pure ici : "
         + "elle est déclarée conforme <b>aux paramètres recherchés ce jour-là</b>.";
  }

  bloc.appendChild(txt("div", "eyebrow", "Ce que dit ce bulletin"));
  bloc.appendChild(txt("h3", null, titre));
  bloc.appendChild(el("p", null, sous));

  const cas = (h.nb_depassements ? h.depassements : h.bascules) || [];
  if(cas.length){
    const liste = el("div", "hero-cas");
    cas.forEach(c => {
      const carte = el("div", "cas");
      const t = el("div", "cas-t");
      t.appendChild(txt("b", null, c.p));
      t.appendChild(txt("span", "cas-v", c.v + " " + c.u));
      carte.appendChild(t);

      const g = jauge(c.v, c.s16, c.s, c.u);
      if(g) carte.appendChild(g);

      if(c.datee !== undefined){
        /* bascule */
        carte.appendChild(txt("div", "cas-n",
          "Au-dessus de la limite de " + c.s16 + " en vigueur en 2016, sous celle de "
          + c.s + " appliquée aujourd'hui."
          + (c.datee ? " Le déplacement est daté : la même valeur, la veille, "
                     + "n'était pas conforme." : "")));
      } else {
        /* dépassement — étiqueté par la nature de ce qui est franchi. Sans
           cette étiquette, la carte d'un métabolite « non pertinent » est
           indiscernable de celle d'un plomb au-dessus de sa limite. */
        const NATURES = {
          limite:    ["dep", "limite de qualité"],
          reference: ["bas", "référence de qualité"],
          vigilance: ["bas", "valeur de vigilance"]
        };
        const nn = NATURES[c.nat];
        if(nn) t.appendChild(txt("span", "etat " + nn[0], nn[1]));

        const f = parseFloat(c.v.replace(",", ".")) / parseFloat(c.s.replace(",", "."));
        let n = "Seuil applicable à la date : " + c.s + " " + c.u
              + (isFinite(f) ? " — la mesure vaut " + (Math.round(f * 100) / 100)
                                 .toString().replace(".", ",") + " fois ce seuil." : ".");
        if(c.s16 && c.s16 !== c.s){
          const f16 = parseFloat(c.v.replace(",", ".")) / parseFloat(c.s16.replace(",", "."));
          if(isFinite(f16)) n += " Contre la limite de " + c.s16 + " en vigueur en 2016, "
            + "elle en vaut " + (Math.round(f16 * 10) / 10).toString().replace(".", ",")
            + " fois.";
        }
        /* « la grille de 2016 » est un nom de colonne, pas une phrase pour le
           lecteur : pour un métabolite, la valeur de 0,1 µg/L vient de
           l'instruction de décembre 2020, et l'appeler « la norme de 2016 »
           fabriquerait un passé réglementaire (§2.12). */
        if(c.g === "2016") n += " C'est la valeur applicable ce jour-là, "
          + "antérieure au reclassement de ce paramètre.";
        /* `txt` pose du TEXTE — les chiffres et les unités viennent de la base
           et n'ont rien à faire dans du HTML. La phrase sur la nature du seuil
           est de la prose pure : elle passe par `el`, dans son propre bloc. */
        carte.appendChild(txt("div", "cas-n", n));
        if(c.nat === "vigilance"){
          carte.appendChild(el("div", "cas-n", "Cette valeur est <b>indicative et sans "
            + "portée opposable</b> : la franchir n'est pas une non-conformité."));
        } else if(c.nat === "reference"){
          carte.appendChild(el("div", "cas-n", "C'est une <b>référence de qualité</b> — "
            + "goût, aspect, bon fonctionnement — <b>pas une limite sanitaire</b>."));
        }
      }

      /* L'accroche vers le dossier de la substance. DEUX phrases, fabriquées
         avec la valeur de CE bulletin et la date du référentiel — le
         raisonnement, lui, est écrit une seule fois et vit sur sa page. Le
         recopier ici, dans des dizaines de fiches, produirait des pages qui
         disent toutes la même chose : le lecteur qui en ouvre deux cesse de
         croire la troisième. */
      if(c.ds){
        const b = el("div", "cas-n");
        b.innerHTML = "<b>Ce paramètre a changé de règle.</b> La valeur applicable "
          + "est passée de " + c.ds.a + " à " + c.ds.b + " " + c.ds.un
          + " le " + c.ds.d + ". La mesure, elle, n'a pas changé.";
        const l = document.createElement("a");
        l.href = c.ds.u;   /* déjà relative à la page, préfixée à la construction */
        l.textContent = "Ce que cette substance démontre à l'échelle du corpus →";
        b.appendChild(document.createElement("br"));
        b.appendChild(l);
        carte.appendChild(b);
      }
      liste.appendChild(carte);
    });
    zone.appendChild(bloc);
    bloc.appendChild(liste);
  } else {
    zone.appendChild(bloc);
  }
}

/* ---------------------------------------------------------------------------
   LES INDICATEURS

   Un nombre nu ne se lit pas : « 0,493 µg/L » ne dit rien, « 99 % de la
   limite » dit tout. Chaque indicateur porte donc sa valeur, son seuil, et une
   barre qui situe l'une par rapport à l'autre.
   --------------------------------------------------------------------------- */
const ETATS = {
  depassement: ["dep", "dépasse le seuil"],
  bascule:     ["bas", "bascule"],
  indetermine: ["ind", "indéterminé"],
  hors_plage:  ["amb", "hors de la référence"],
  conforme:    ["ok", "sous le seuil"],
  sous_lq:     ["lq", "sous la limite de quantification"],
  absent:      ["abs", "non recherché"],
  neutre:      ["neu", ""],
};

function renderIndicateurs(d){
  const zone = byId("indicateurs");
  if(!zone) return;
  zone.innerHTML = "";

  (d.groupes || []).forEach(([cle, titre, chapeau]) => {
    const liste = (d.ind || {})[cle] || [];
    if(!liste.length) return;

    const g = el("div", "grp grp-" + cle);
    const tete = el("div", "grp-tete");
    tete.appendChild(txt("h4", null, titre));
    tete.appendChild(el("p", null, chapeau));
    g.appendChild(tete);

    const grille = el("div", "grp-grille");
    liste.forEach(i => {
      const [cls, libEtat] = ETATS[i.etat] || ETATS.neutre;
      const c = el("div", "ind ind-" + cls);

      const lab = el("div", "ind-lab");
      lab.appendChild(document.createTextNode(i.libelle));
      if(i.a_verifier){
        const s = txt("span", "av", " ⚠");
        s.title = "Seuil non confirmé sur source primaire (fiabilite = a_verifier)";
        lab.appendChild(s);
      }
      c.appendChild(lab);
      c.appendChild(txt("div", "ind-val", i.texte));

      if(i.part != null && isFinite(i.part)){
        const b = el("div", "ind-barre");
        const r = el("div", "rempli");
        r.style.width = Math.max(2, Math.min(100, i.part * 100)) + "%";
        b.appendChild(r);
        c.appendChild(b);
        if(i.seuil != null && !i.plage)
          c.appendChild(txt("div", "ind-pct",
            Math.round(i.part * 100) + " % du seuil applicable"));
      }
      if(i.detail) c.appendChild(txt("div", "ind-det", i.detail));
      /* Le plafond analytique de cette tuile. Une tuile verte au-dessus d'une
         mesure que le laboratoire ne pouvait pas voir serait le pire mensonge
         de la fiche : la mention est donc portée par la tuile elle-même, en
         rouge, et pas seulement par le bloc plus bas (chantier C4). */
      if(i.lq_mention) c.appendChild(txt("div", "ind-lq-mention", i.lq_mention));
      if(libEtat) c.appendChild(txt("span", "ind-etat", libEtat));
      c.appendChild(txt("p", "ind-lecture", i.lecture));
      grille.appendChild(c);
    });
    g.appendChild(grille);
    zone.appendChild(g);

    /* Les lectures qui ne tiennent pas dans une tuile viennent s'ajouter au
       groupe auquel elles appartiennent. */
    if(cle === "polluants"){
      renderPE(d, zone);
      renderNourrissons(d, zone);
      renderPfas(d, zone);
      renderDanger(d, zone);
    }
    /* Le groupe « eau » décrit le caractère de la ressource — c'est là que
       vivent les références de qualité, qui ne disent rien d'une pollution. */
    if(cle === "eau") renderReferences(d, zone);
    if(cle === "lecture") renderPlafond(d, zone);
  });
}

/* ---------------------------------------------------------------------------
   LE PLAFOND ANALYTIQUE — ce que le laboratoire ne pouvait pas voir.

   Chantier C4. Demande de Yannick, à propos de Pont-de-Larn : « le seuil du
   laboratoire ne permet pas du tout de quantifier ce qui est en dessous de
   cette limite […] si je compare avec une autre commune dont les limites du
   laboratoire sont beaucoup plus faibles, la comparaison des deux est biaisée. »

   Le barème n'a de sens qu'à PARAMÈTRE CONSTANT : un laboratoire peut
   descendre à 4 ng/L sur les PFAS et rester à 0,5 µg/L sur l'hydrazide
   maléique. Une jauge unique par commune moyennerait deux instruments
   différents — le profil synthétique que le §2.3 interdit, transposé à
   l'instrument. Il ne s'affiche donc que là où il mord, et il porte toujours
   sa base : « le plus fin » sur 29 bulletins n'est pas « le plus fin » sur
   4 000 (§2.14).

   L'échelle est logarithmique. Entre 0,05 et 2,5 µg/L, une graduation linéaire
   collerait 0,5 contre la borne basse et laisserait croire à une finesse
   quasi optimale, alors qu'elle en est dix fois éloignée.
   --------------------------------------------------------------------------- */
function renderPlafond(d, zone){
  const p = d.plafond;
  if(!p || !(p.lignes || []).length) return;

  const b = el("div", "bloc-lecture en-plafond");
  b.appendChild(txt("h5", null, "Ce que le laboratoire ne pouvait pas voir"));
  b.appendChild(el("p", null,
    "Pour ces paramètres, la <b>limite de quantification</b> du laboratoire — la plus "
    + "petite quantité qu'il sait mesurer — se situe <b>au-dessus du seuil auquel on "
    + "compare</b>. Sous cette valeur, l'analyse ne voit rien, là précisément où la "
    + "conformité se joue : elle ne permet ni de constater un dépassement, ni "
    + "d'affirmer que le seuil est respecté. "
    + (p.pour_mille != null
       ? "Cela représente <b>" + fr(p.pour_mille) + " pour mille</b> des "
         + p.notees + " paramètres notés de ce bulletin — un taux, seul comparable à "
         + "celui d'une autre commune. "
       : "")
    + "Une limite de quantification élevée est une <b>capacité d'instrument, pas une "
    + "négligence</b> : ce qui est examiné ici est ce que le dispositif permet de "
    + "savoir."));

  p.lignes.forEach(l => {
    const c = el("div", "lq-cas");
    const t = el("div", "lq-t");
    t.appendChild(txt("b", null, l.libelle));
    t.appendChild(txt("span", "lq-r",
      l.rapport ? fr(l.rapport) + " × le seuil" : "au-dessus du seuil"));
    c.appendChild(t);
    c.appendChild(txt("div", "lq-mention",
      "LQ " + l.lq + " " + l.unite + " pour un seuil de " + l.seuil + " " + l.unite
      + ". Sous cette valeur, l'analyse ne conclut pas."));

    const g = l.bareme;
    if(g && g.position != null){
      const jauge = el("div", "lq-jauge");
      const piste = el("div", "piste");
      const ici = el("div", "ici");
      ici.style.left = Math.max(0, Math.min(100, g.position * 100)) + "%";
      piste.appendChild(ici);
      jauge.appendChild(piste);
      const bornes = el("div", "lq-bornes");
      bornes.appendChild(txt("span", null, g.min + " " + l.unite + " — le plus fin relevé"));
      bornes.appendChild(txt("span", null, g.max + " " + l.unite + " — le plus grossier"));
      jauge.appendChild(bornes);
      c.appendChild(jauge);
      c.appendChild(txt("div", "lq-base",
        "Ici : " + g.ici + " " + l.unite
        + (g.facteur_au_plus_fin ? ", soit " + fr(g.facteur_au_plus_fin)
             + " fois moins fin que la plus basse relevée" : "")
        + ". Étendue observée sur " + g.nb_bulletins + " bulletin(s) et "
        + g.nb_departements + " département(s) du corpus — elle se déplacera à mesure "
        + "qu'il grandira."));
    } else if(g){
      c.appendChild(txt("div", "lq-base",
        "Une seule limite de quantification relevée dans le corpus pour cette "
        + "substance (" + g.min + " " + l.unite + ", sur " + g.nb_bulletins
        + " bulletin(s)) : il n'y a rien à comparer pour l'instant."));
    }
    b.appendChild(c);
  });

  zone.appendChild(b);
}

/* Perturbateurs endocriniens — trois registres, jamais fusionnés.
   Le statut réglementaire et le statut scientifique ne disent pas la même
   chose, et « non documenté » ne dit pas « non ». Écrire qu'une substance
   « est un perturbateur endocrinien » sans préciser le registre est une faute
   vérifiable qui décrédibilise l'ensemble (CLAUDE.md §2.6). */
function renderPE(d, zone){
  const p = d.pe;
  if(!p) return;
  const total = p.avere.length + p.suspecte.length + p.non_documente.length;
  if(!total) return;

  const b = el("div", "bloc-lecture" + (p.avere.length ? " en-alerte" : ""));
  b.appendChild(txt("h5", null, "Perturbateurs endocriniens"));
  b.appendChild(el("p", null,
    "Ces trois listes ne disent pas la même chose et ne se remplacent pas. "
    + "Dans l'eau destinée à la consommation humaine, <b>le seul perturbateur "
    + "endocrinien avéré au sens de la réglementation européenne est le bisphénol "
    + "A</b>. D'autres substances le sont dans la littérature scientifique sans "
    + "l'être en droit. Et pour beaucoup, la question n'a tout simplement pas été "
    + "instruite : <b>« non documenté » ne veut pas dire « non »</b>."));

  const registres = [
    ["avere", "Avérés au sens réglementaire",
     "reconnus comme perturbateurs endocriniens par le droit européen", "dep"],
    ["suspecte", "Suspectés par la littérature scientifique",
     "des travaux publiés le rapportent, sans reconnaissance réglementaire", "bas"],
    ["non_documente", "Statut non documenté",
     "aucun statut renseigné au référentiel du projet — ce n'est pas une absence "
     + "de propriété, c'est une absence d'instruction", "ind"],
  ];

  const cols = el("div", "pe-cols");
  registres.forEach(([cle, titre, sous, etat]) => {
    const liste = p[cle] || [];
    const c = el("div", "pe-col pe-" + etat);
    const t = el("div", "pe-t");
    t.appendChild(document.createTextNode(titre));
    t.appendChild(txt("span", "etat " + etat, String(liste.length)));
    c.appendChild(t);
    c.appendChild(txt("div", "pe-s", sous));
    if(!liste.length){
      c.appendChild(txt("div", "pe-vide", "aucune substance quantifiée dans ce registre"));
    } else {
      const ul = el("ul", "pe-liste");
      liste.slice(0, 12).forEach(x => {
        const li = el("li");
        li.appendChild(txt("b", null, x.libelle));
        li.appendChild(txt("span", "pe-v", x.texte));
        if(x.famille) li.appendChild(txt("span", "pe-f", x.famille));
        if(x.mention && cle === "suspecte")
          li.appendChild(txt("span", "pe-m", x.mention));
        ul.appendChild(li);
      });
      if(liste.length > 12)
        ul.appendChild(txt("li", "pe-vide",
          "et " + (liste.length - 12) + " autre(s) — le bulletin complet est plus bas"));
      c.appendChild(ul);
    }
    cols.appendChild(c);
  });
  b.appendChild(cols);
  b.appendChild(el("p", "pe-note",
    "Seules les substances effectivement quantifiées figurent ici. Une substance "
    + "recherchée et non quantifiée n'apparaît pas : cela ne signifie pas qu'elle "
    + "est absente, mais qu'elle est sous la limite de quantification du laboratoire."
    + (p.hors_referentiel
       ? " S'y ajoutent <b>" + p.hors_referentiel + " substance(s) quantifiée(s)</b> "
         + "que le référentiel du projet ne décrit pas encore : elles ne sont "
         + "rattachées à aucun des trois registres, faute d'en savoir quoi que ce "
         + "soit."
       : "")));
  zone.appendChild(b);
}

/* Repères nourrissons.
   Ce ne sont PAS des limites au robinet : ils viennent de la réglementation
   des eaux embouteillées autorisées à porter la mention « convient à
   l'alimentation des nourrissons ». La comparaison est légitime — un biberon
   se prépare avec l'eau qu'on a sous la main — mais ce n'est pas un test de
   conformité, et le bloc doit le dire à chaque fois. */
function renderNourrissons(d, zone){
  const liste = d.nourrissons || [];
  if(!liste.length) return;
  const alerte = liste.filter(x => x.au_dessus);

  const b = el("div", "bloc-lecture" + (alerte.length ? " en-alerte" : ""));
  b.appendChild(txt("h5", null, "Repères « nourrissons »"));
  b.appendChild(el("p", null,
    "Ces valeurs ne sont <b>pas des limites au robinet</b>. Ce sont les repères que "
    + "doit respecter une eau embouteillée pour porter la mention « convient à "
    + "l'alimentation des nourrissons » (arrêté du 14 mars 2007). Une eau parfaitement "
    + "conforme peut se situer au-dessus : cela ne la rend pas non conforme, cela dit "
    + "seulement qu'elle ne serait pas vendue sous cette mention."));

  const t = el("table", "tab-lecture");
  t.innerHTML = "<thead><tr><th>Paramètre</th><th>Mesure</th>"
              + "<th>Repère nourrissons</th><th>Limite au robinet</th><th></th></tr></thead>";
  const tb = el("tbody");
  liste.forEach(x => {
    const tr = el("tr", x.au_dessus ? "au-dessus" : "");
    tr.appendChild(txt("td", null, x.libelle));
    tr.appendChild(txt("td", "num", x.texte));
    tr.appendChild(txt("td", "num", x.repere + " " + (x.unite || "")));
    tr.appendChild(txt("td", "num", x.limite != null ? x.limite + " " + (x.unite || "") : "—"));
    const etat = el("td");
    if(x.conforme_mais_au_dessus){
      etat.appendChild(txt("span", "etat bas", "conforme, au-dessus du repère"));
    } else if(x.au_dessus){
      etat.appendChild(txt("span", "etat dep", "au-dessus du repère"));
    } else {
      etat.appendChild(txt("span", "etat ok", "sous le repère"));
    }
    tr.appendChild(etat);
    tb.appendChild(tr);
  });
  t.appendChild(tb);
  b.appendChild(t);
  zone.appendChild(b);
}

/* Hors de la référence de qualité déclarée — et SANS limite de qualité.
   Périmètre décidé le 9 août 2026 : quand une limite existe, c'est elle qui
   parle et le dépassement s'affiche ailleurs. Ici il n'y a rien à quoi être
   non conforme, seulement une valeur déclarée par l'administration et une
   mesure qui s'en écarte. Le bloc n'est donc JAMAIS peint comme un
   dépassement : le confondre transformerait un écart organoleptique en
   non-conformité sanitaire (CLAUDE.md §2.1, §2.13).

   Le sens compte autant que l'écart. Sous la borne basse, l'eau n'est pas
   chargée : elle est agressive, et ce qu'elle emporte du réseau entre le point
   de prélèvement et le robinet n'est dans aucun bulletin. */
function renderReferences(d, zone){
  const r = d.references;
  if(!r || !r.liste.length) return;

  const b = el("div", "bloc-lecture");
  b.appendChild(txt("h5", null, "Hors de la référence de qualité"));
  b.appendChild(el("p", null,
    "Ces paramètres n'ont <b>aucune limite de qualité</b> : il n'existe rien à quoi "
    + "cette eau pourrait être « non conforme » sur ce point. Ce que l'administration "
    + "déclare avec la mesure est une <b>référence de qualité</b> — un repère de bon "
    + "fonctionnement, de goût ou d'aspect. S'en écarter <b>n'est pas une "
    + "non-conformité sanitaire</b>, et c'est une information, pas un verdict."));

  if(r.nb_en_dessous){
    b.appendChild(el("p", "note-basse",
      "<b>Sous la borne basse.</b> Une eau peu minéralisée ou acide n'est pas une eau "
      + "chargée : c'est une eau <b>agressive</b>, qui dissout une partie de ce qu'elle "
      + "traverse. Le prélèvement ayant été fait à un point du réseau, ce qu'elle "
      + "emporte entre ce point et le robinet <b>ne figure dans aucun bulletin</b>."));
  }

  const t = el("table", "tab-lecture");
  t.innerHTML = "<thead><tr><th>Paramètre</th><th>Mesure</th>"
              + "<th>Référence déclarée</th><th></th></tr></thead>";
  const tb = el("tbody");
  r.liste.forEach(x => {
    const tr = el("tr");
    tr.appendChild(txt("td", null, x.libelle));
    tr.appendChild(txt("td", "num", x.texte));
    tr.appendChild(txt("td", "num",
      (x.plage ? x.plage : (x.sens === "en_dessous" ? "≥ " : "≤ ") + x.borne)
      + " " + x.unite));
    const e = el("td");
    e.appendChild(txt("span", "etat bas",
      x.sens === "en_dessous" ? "sous la référence" : "au-dessus de la référence"));
    tr.appendChild(e);
    tb.appendChild(tr);
  });
  t.appendChild(tb);
  b.appendChild(t);
  zone.appendChild(b);
}

/* PFAS par longueur de chaîne.
   L'objet de ce bloc est réglementaire, et lui seul : montrer que la « somme
   de 4 » mise en avant par la réglementation ne contient que des chaînes
   longues — celles dont l'usage est en cours d'interdiction. Il ne dit rien
   d'un traitement, d'un procédé ou d'un équipement (CLAUDE.md §2.2). */
function renderPfas(d, zone){
  const p = d.pfas;
  if(!p) return;
  const b = el("div", "bloc-lecture");
  b.appendChild(txt("h5", null, "PFAS — ce que la somme réglementaire regarde"));

  /* AUCUN PFAS INDIVIDUEL DANS CE BULLETIN.
     Le bloc s'affichait autrefois... en ne s'affichant pas du tout, et une
     page silencieuse se lit comme une page rassurante. C'est l'inverse :
     ne pas avoir cherché est le signal le plus fort de la fiche. La recherche
     des PFAS est une obligation récente, donc beaucoup de bulletins n'en
     portent aucun — et ceux-là ne doivent pas ressembler à une eau propre. */
  if(p.rien_de_cherche){
    b.appendChild(el("p", "pfas-absent",
      "<b>Aucun PFAS n'a été recherché sur ce prélèvement.</b> Ce n'est pas un "
      + "résultat : c'est une absence de recherche. Rien ici ne dit qu'il y en a, "
      + "rien ne dit qu'il n'y en a pas."));
    if(p.agregat_sans_detail){
      const ul = el("ul", "pfas-liste");
      p.agregats.forEach(x => {
        const li = el("li");
        li.appendChild(txt("b", null, x.libelle));
        li.appendChild(txt("span", "pfas-v", x.texte));
        ul.appendChild(li);
      });
      b.appendChild(el("p", null,
        "Le laboratoire a en revanche rendu un <b>total</b>, sans le détail des "
        + "substances qui le composent. La valeur ci-dessous ne peut donc pas "
        + "être décomposée : on ne sait pas de quelles molécules elle est faite."));
      b.appendChild(ul);
    }
    zone.appendChild(b);
    return;
  }

  b.appendChild(el("p", null,
    "La <b>somme de 4</b> mise en avant par la réglementation européenne — PFOA, PFNA, "
    + "PFHxS, PFOS — ne contient que des <b>chaînes longues</b>, c'est-à-dire "
    + "précisément celles dont l'usage est en cours d'interdiction. Les <b>chaînes "
    + "courtes</b> qui les remplacent sont mesurées par le laboratoire et n'entrent "
    + "dans aucun total opposable, hormis la somme de 20. La mesure existe ; la norme "
    + "ne la regarde pas."));

  const cols = el("div", "pfas-cols");
  [["longue", "Chaînes longues", "celles que vise la somme de 4"],
   ["courte", "Chaînes courtes", "mesurées, hors de la somme de 4"]].forEach(([k, t, s]) => {
    const g = p[k];
    if(!g) return;
    const c = el("div", "pfas-col");
    c.appendChild(txt("div", "pfas-t", t));
    c.appendChild(txt("div", "pfas-s", s));
    c.appendChild(txt("div", "pfas-n",
      g.quantifiees + " quantifiée(s) sur " + g.cherchees + " recherchée(s)"));
    if(g.somme != null)
      c.appendChild(txt("div", "pfas-somme", "somme ≥ " + String(g.somme).replace(".", ",")
        + " µg/L"));
    /* TOUTES les substances cherchées sont listées, pas seulement celles
       qu'on a trouvées. Corrigé le 12 août 2026 : n'afficher que les
       quantifiées faisait paraître le bloc vide sur une eau où l'on avait
       tout cherché sans rien trouver — c'est-à-dire dans le meilleur des cas.
       Chercher et ne rien trouver est une information, et une bonne. */
    const ul = el("ul", "pfas-liste");
    g.substances.forEach(x => {
      const li = el("li", x.quantifie ? null : "pfas-nd");
      li.appendChild(txt("b", null, x.sigle));
      li.appendChild(txt("span", "pfas-c", " C" + x.carbones + " · " + x.type));
      li.appendChild(txt("span", "pfas-v", x.texte));
      ul.appendChild(li);
    });
    if(!g.substances.some(x => x.quantifie))
      ul.appendChild(txt("li", "pfas-vide",
        "aucune quantifiée — ce qui ne veut pas dire aucune présente : "
        + "sous la limite de quantification du laboratoire, on ne sait pas"));
    c.appendChild(ul);
    cols.appendChild(c);
  });
  b.appendChild(cols);

  /* CE QUI N'A PAS ÉTÉ CHERCHÉ, nommé. Chercher et ne rien trouver est une
     bonne nouvelle qui doit se lire ; ne pas chercher est un fait d'une autre
     nature, et les deux ne doivent jamais se confondre à l'œil. */
  if((p.non_cherchees || []).length){
    b.appendChild(el("p", "pfas-noncherche",
      "<b>" + p.non_cherchees.length + " des " + p.attendues_total
      + " PFAS de la somme réglementaire n'ont pas été recherchés</b> sur ce "
      + "prélèvement : " + p.non_cherchees.join(", ")
      + ". Sur ceux-là, l'analyse ne dit rien — ni présence, ni absence."));
  } else {
    b.appendChild(el("p", "pfas-noncherche",
      "<b>Les " + p.attendues_total + " PFAS de la somme réglementaire ont tous "
      + "été recherchés</b> sur ce prélèvement."));
  }
  zone.appendChild(b);
}

/* De quoi l'indice de danger est fait. Le nombre seul ne se lit pas ; la somme
   des fractions de seuil, si. */
function renderDanger(d, zone){
  const dg = d.danger || {};
  if(dg.total == null || !(dg.parts || []).length) return;
  const b = el("div", "bloc-lecture");
  b.appendChild(txt("h5", null, "De quoi l'indice de danger est fait"));
  b.appendChild(el("p", null,
    "Pour chaque substance de synthèse quantifiée, on calcule la <b>fraction de sa "
    + "propre limite</b> qu'elle occupe, et on additionne. Le total vaut <b>"
    + String(dg.total.toFixed ? dg.total.toFixed(2) : dg.total).replace(".", ",")
    + "</b> sur " + dg.n + " substance(s). Autrement dit : si l'on raisonnait sur le "
    + "mélange plutôt que substance par substance, cette eau se situerait à ce "
    + "multiple du repère. <b>C'est un raisonnement, pas une mesure de risque</b> — "
    + "les seuils additionnés n'ont pas tous la même nature, et aucun facteur "
    + "d'ajustement de mélange n'est appliqué."));

  const ul = el("div", "parts");
  dg.parts.forEach(x => {
    const l = el("div", "part");
    l.appendChild(txt("span", "part-p", x.p));
    const barre = el("div", "part-b");
    const r = el("div", "rempli");
    r.style.width = Math.min(100, (x.part / Math.max(1, dg.parts[0].part)) * 100) + "%";
    barre.appendChild(r);
    l.appendChild(barre);
    l.appendChild(txt("span", "part-v",
      String(x.part).replace(".", ",") + " × sa limite"));
    l.appendChild(txt("span", "part-d", x.v + " " + x.u + " pour " + x.s));
    ul.appendChild(l);
  });
  b.appendChild(ul);
  zone.appendChild(b);
}

function render(k){
  CUR = k; detOnly = false; sigOnly = false;
  const d = C[k];
  document.querySelectorAll("#switch button")
    .forEach(b => b.setAttribute("aria-pressed", b.dataset.k === k));

  byId("communeName").textContent = d.name;
  byId("communeSub").textContent = d.sub;
  byId("idEyebrow").textContent =
    "Commune · INSEE " + d.insee + " · prélèvement du " + d.date;

  const meta = byId("meta");
  meta.innerHTML = "";
  d.meta.forEach(([kk, v]) => { const c = el("div");
    c.appendChild(txt("span", "k", kk)); c.appendChild(txt("span", "v", v));
    meta.appendChild(c); });

  byId("concl").textContent = d.official.concl;
  const axes = byId("axes");
  axes.innerHTML = "";
  d.official.axes.forEach(([n, val, lvl]) => {
    const a = el("div", "axe " + (lvl || "gris"));
    a.appendChild(el("span", "d"));
    a.appendChild(txt("span", "n", n + " :"));
    a.appendChild(txt("b", null, val));
    axes.appendChild(a);
  });

  /* Bandeaux — ce que l'habitant doit savoir avant de lire les chiffres. */
  const bx = byId("bandeaux");
  bx.innerHTML = "";
  if(d.rattachee){
    const b = el("div", "bandeau reseau");
    b.appendChild(txt("span", "ic", "↔"));
    b.appendChild(el("div", null, "<b>Analyse empruntée au réseau.</b> Aucun bulletin "
      + "complet n'a été prélevé dans cette commune. Celui présenté ici porte sur la "
      + "même eau, prélevée à <b>" + d.commune_prelevement + "</b> le " + d.date
      + " sur le réseau qui alimente les deux communes."));
    bx.appendChild(b);
  }
  if(!d.complet){
    const b = el("div", "bandeau incomplet");
    b.appendChild(txt("span", "ic", "⚠"));
    b.appendChild(el("div", null, "<b>Bulletin incomplet.</b> Ce prélèvement porte moins de "
      + "200 paramètres : il ne remplit pas la règle de méthode du projet et ne peut "
      + "pas fonder une conclusion sur la qualité de l'eau."));
    bx.appendChild(b);
  }
  /* Le bandeau « d'où vient ce qui est écrit » a été retiré le 10 août 2026,
     en même temps que la prose. Il n'avait de sens que tant que la fiche
     mêlait trois origines — main de l'auteur, proposition du modèle, dérivé.
     Elle n'en porte plus qu'une : tout ce qu'elle affiche vient d'une requête,
     et la page Méthode le dit une fois pour toutes. Un bandeau qui répète sur
     678 fiches une phrase toujours identique cesse d'être une information. */

  setPill("adminPill", d.admin.level, d.admin.v);
  byId("adminDetail").textContent = d.admin.d || "";
  byId("adminDetail").style.display = d.admin.d ? "" : "none";
  /* La bande de bascule entre les deux lectures est la phrase de Yannick qui
     dit ce qui SÉPARE le verdict administratif du verdict citoyen. Sans texte,
     il n'y a rien à séparer : on retire la bande plutôt que d'afficher une
     flèche seule, qui laisserait croire à un contenu manquant. */
  byId("deltaText").innerHTML = d.delta || "";
  byId("deltaText").closest(".delta").style.display = d.delta ? "" : "none";
  setPill("citPill", d.cit.level, d.cit.v);
  byId("citDetail").textContent = d.cit.d;

  renderHero(d);
  renderIndicateurs(d);

  const an = byId("analyse");
  an.innerHTML = "";
  if(d.analyse.length){
    d.analyse.forEach(p => {
      const c = el("div", "apart");
      c.appendChild(txt("h4", null, p.t));
      c.appendChild(txt("p", null, p.x));
      an.appendChild(c);
    });
  } else {
    an.appendChild(txt("div", "apart",
      "Aucune analyse n'est disponible pour cette commune. Les indicateurs "
      + "ci-dessus et le bulletin ci-dessous restent entièrement consultables."));
  }

  byId("bcount").textContent = PARAMS[k].params.length + " paramètres";
  byId("bfilter").value = "";
  byId("btnDet").setAttribute("aria-pressed", "false");
  byId("btnSig").setAttribute("aria-pressed", "false");
  renderTable();

  const vd = byId("verdict");
  vd.className = "verdict " + d.verdict.level;
  byId("verdictText").textContent = d.verdict.t;

  byId("hubeauUrl").textContent =
    d.src || ("hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis" + d.hubeau);

  /* Traçabilité — obligation 9. Un écran qui ne dit pas contre quelle grille il
     a été calculé reproduirait, à l'intérieur de l'outil, le défaut dénoncé. */
  const tr = byId("tracab");
  tr.innerHTML = "";
  [["Version du référentiel", d.version_referentiel],
   ["Calculé le", d.calcule_le],
   ["Prélèvement", d.date],
   ["Code INSEE", d.insee]].forEach(([kk, v]) => {
    const s = el("span"); s.appendChild(txt("b", null, kk + " : "));
    s.appendChild(document.createTextNode(v)); tr.appendChild(s);
  });
}

byId("bfilter").addEventListener("input", renderTable);
byId("btnCsv").addEventListener("click", toCsv);
byId("btnDet").addEventListener("click", function(){
  detOnly = !detOnly; this.setAttribute("aria-pressed", String(detOnly)); renderTable(); });
byId("btnSig").addEventListener("click", function(){
  sigOnly = !sigOnly; this.setAttribute("aria-pressed", String(sigOnly)); renderTable(); });

/* Le sélecteur de commune n'existe que sur la fiche autonome, qui rassemble
   plusieurs bulletins dans un seul fichier. Sur la vitrine, chaque commune a
   son adresse : il n'y a rien à commuter. */
const sw = byId("switch");
if(sw){
  ORDER.forEach(k => {
    const d = C[k];
    const b = el("button");
    b.dataset.k = k;
    b.appendChild(el("span", "sdot " + d.dot));
    b.appendChild(document.createTextNode(d.name + " · " + d.date_courte));
    b.addEventListener("click", () => render(k));
    sw.appendChild(b);
  });
}
render(ORDER[0]);

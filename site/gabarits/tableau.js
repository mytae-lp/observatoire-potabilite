/* ===========================================================================
   Chercher et trier la liste des communes d'un département.

   Comme pour le filtre de la carte, ce script ne fait que retirer et réordonner
   ce qui est déjà dans la page. Sans lui, la liste complète s'affiche par ordre
   alphabétique et reste juste : la vitrine est un dossier de fichiers statiques
   qui doit rester consultable dans dix ans.

   Trois règles de méthode passent par ici.

   1. **Une commune non documentée n'a pas « zéro dépassement ».** Elle n'a pas
      de valeur du tout. Le HTML porte -1 pour dire cela, et le tri met ces
      lignes À PART, toujours en fin, quel que soit le sens. Sans cette
      précaution, un tri croissant par dépassements présenterait les communes
      dont on ne sait rien comme les plus sûres du département — l'erreur exacte
      que le troisième état sert à éviter (§2.4).

   2. **La recherche ne masque jamais le décompte.** Le nombre de communes
      trouvées est annoncé, et le nombre total avec lui : filtrer une liste ne
      doit pas donner l'impression que le reste n'existe pas.

   3. **La recherche et le filtre d'état se composent** au lieu de se remplacer.
      Chacun pose sa propre classe, et c'est le CSS qui décide de l'affichage.
      S'ils s'écrivaient l'un sur l'autre, actionner le second annulerait
      silencieusement le premier.
   =========================================================================== */
(function(){
  const table = document.getElementById("tbl-communes");
  if(!table) return;
  const corps = table.tBodies[0];
  const lignes = Array.prototype.slice.call(corps.rows);

  /* ---- Recherche : nom ou code postal ---------------------------------- */
  const champ = document.getElementById("q-dept");
  const etat = document.getElementById("q-etat");

  const pl = s => (s || "").toLowerCase()
      .normalize("NFD").replace(/[̀-ͯ]/g, "");

  function chercher(q){
    q = pl(q.trim());
    let vus = 0;
    lignes.forEach(function(tr){
      const nom = pl(tr.getAttribute("data-nom"));
      const cp = tr.getAttribute("data-cp") || "";
      const insee = tr.getAttribute("data-insee") || "";
      const trouve = !q || nom.indexOf(q) !== -1
        || cp.split(",").some(x => x.indexOf(q) === 0)
        || insee.indexOf(q) === 0;
      tr.classList.toggle("hors-recherche", !trouve);
      if(trouve) vus++;
    });
    if(!etat) return;
    if(!q){
      etat.textContent = "";
    } else if(vus === 0){
      etat.textContent = "Aucune commune de ce département ne correspond à « " + q
        + " ». Elle est peut-être dans un département voisin, ou pas encore collectée.";
    } else {
      etat.textContent = vus + " commune(s) sur " + lignes.length
        + " correspondent à « " + q + " ».";
    }
  }

  if(champ){
    champ.addEventListener("input", () => chercher(champ.value));
    champ.addEventListener("search", () => chercher(champ.value));
  }

  /* ---- Tri -------------------------------------------------------------- */
  const index = document.getElementById("index-alpha");
  const entetes = Array.prototype.slice.call(table.tHead.rows[0].cells)
      .filter(th => th.getAttribute("data-tri"));

  function trier(th){
    const cle = th.getAttribute("data-tri");
    const numerique = th.getAttribute("data-type") === "nombre";
    const deja = th.getAttribute("aria-sort");
    const sens = deja === "ascending" ? -1 : 1;

    entetes.forEach(x => x.removeAttribute("aria-sort"));
    th.setAttribute("aria-sort", sens === 1 ? "ascending" : "descending");

    const val = tr => {
      const v = tr.getAttribute("data-" + cle);
      return numerique ? parseFloat(v) : (v || "");
    };
    /* Les lignes sans valeur (-1, ou une date vide) sortent du tri et se
       rangent en fin, dans les deux sens. Elles ne sont ni les meilleures ni
       les pires : elles ne sont pas comparables. */
    const connue = tr => numerique ? val(tr) >= 0 : val(tr) !== "";

    const avec = lignes.filter(connue);
    const sans = lignes.filter(tr => !connue(tr));
    avec.sort(function(a, b){
      const x = val(a), y = val(b);
      if(x === y) return (a.getAttribute("data-nom") || "")
          .localeCompare(b.getAttribute("data-nom") || "", "fr");
      return (x > y ? 1 : -1) * sens;
    });
    sans.sort((a, b) => (a.getAttribute("data-nom") || "")
        .localeCompare(b.getAttribute("data-nom") || "", "fr"));

    const frag = document.createDocumentFragment();
    avec.concat(sans).forEach(tr => frag.appendChild(tr));
    corps.appendChild(frag);

    /* L'index alphabétique ne veut plus rien dire hors du tri par nom : ses
       ancres restent valides mais ne pointent plus sur un début de lettre. */
    if(index) index.hidden = cle !== "nom";
  }

  entetes.forEach(function(th){
    th.classList.add("triable");
    th.setAttribute("tabindex", "0");
    th.setAttribute("role", "button");
    th.addEventListener("click", () => trier(th));
    th.addEventListener("keydown", function(e){
      if(e.key === "Enter" || e.key === " "){ e.preventDefault(); trier(th); }
    });
  });
})();

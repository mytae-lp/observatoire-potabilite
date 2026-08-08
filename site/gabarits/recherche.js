/* ===========================================================================
   Recherche d'une commune, entièrement dans le navigateur.

   L'index est un fichier JSON servi comme n'importe quelle image : aucune
   requête n'est adressée à un serveur au moment de la frappe, et ce que
   quelqu'un cherche ne nous parvient donc jamais. Pour un outil qui parle de
   l'eau que les gens boivent chez eux, ce n'est pas un détail technique.

   Le corpus ne couvre pas la France entière. Une commune absente n'est pas une
   commune dont l'eau serait bonne : c'est une commune qui n'a pas été
   collectée. Le message d'absence le dit, plutôt que de laisser croire.
   =========================================================================== */
(function(){
  const champ = document.getElementById("q");
  const liste = document.getElementById("resultats");
  if(!champ || !liste) return;

  let INDEX = null, enAttente = null;

  fetch("donnees/index_communes.json")
    .then(r => r.json())
    .then(d => { INDEX = d; if(enAttente !== null) chercher(enAttente); })
    .catch(() => {
      liste.innerHTML = "";
      const li = document.createElement("li");
      li.className = "vide";
      li.textContent = "L'index des communes n'a pas pu être chargé.";
      liste.appendChild(li);
    });

  /* Sans accents et sans casse : « Vourles » se trouve en tapant « vourles »,
     et « Saint-Étienne » en tapant « saint-etienne ». */
  const pl = s => (s || "").toLowerCase()
      .normalize("NFD").replace(/[̀-ͯ]/g, "");

  function score(c, q){
    if(c.i === q) return 0;                                  // code INSEE exact
    if(c.cp.includes(q)) return 1;                           // code postal exact
    const n = pl(c.n);
    if(n === q) return 2;
    if(n.startsWith(q)) return 3;
    if(n.includes(q)) return 4;
    if(c.cp.some(x => x.startsWith(q))) return 5;
    return 99;
  }

  function ligne(c){
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = c.u;

    const pastille = document.createElement("span");
    pastille.className = "sdot " + c.k;
    a.appendChild(pastille);

    const bloc = document.createElement("span");
    const nom = document.createElement("span");
    nom.className = "nom";
    nom.textContent = c.n;
    bloc.appendChild(nom);
    const sous = document.createElement("span");
    sous.className = "grille";
    sous.textContent = "INSEE " + c.i + " · dépt " + c.d
      + (c.cp.length ? " · " + c.cp.slice(0, 3).join(", ") : "");
    bloc.appendChild(sous);
    a.appendChild(bloc);

    const det = document.createElement("span");
    det.className = "det";
    if(c.s === "non_documentee"){
      det.textContent = "non documentée";
    } else {
      const bits = [c.e + " paramètres cherchés"];
      if(c.x) bits.push(c.x + " dépassement(s) à la date");
      if(c.b) bits.push(c.b + " bascule(s)");
      if(!c.x && !c.b) bits.push("aucun dépassement à la date");
      det.textContent = bits.join(" · ");
      if(c.s === "rattachee_reseau") det.textContent += " · analyse du réseau";
    }
    a.appendChild(det);

    li.appendChild(a);
    return li;
  }

  function vide(texte){
    const li = document.createElement("li");
    li.className = "vide";
    li.textContent = texte;
    return li;
  }

  function chercher(q){
    if(INDEX === null){ enAttente = q; return; }
    liste.innerHTML = "";
    q = pl(q.trim());
    if(q.length < 2) return;

    const trouves = INDEX.map(c => [score(c, q), c])
      .filter(([s]) => s < 99)
      .sort((a, b) => a[0] - b[0] || a[1].n.localeCompare(b[1].n, "fr"))
      .slice(0, 25);

    if(!trouves.length){
      liste.appendChild(vide(
        "Aucune commune du corpus ne correspond à « " + q + " ». Le corpus ne couvre "
        + "pas encore la France entière : une commune absente n'est pas une commune "
        + "dont l'eau serait bonne, c'est une commune qui n'a pas encore été "
        + "collectée."));
      return;
    }
    trouves.forEach(([, c]) => liste.appendChild(ligne(c)));
  }

  champ.addEventListener("input", () => chercher(champ.value));
  champ.addEventListener("search", () => chercher(champ.value));
})();

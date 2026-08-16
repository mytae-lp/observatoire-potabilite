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

  /* L'écran de la commune absente.
     C'est le SEUL endroit du site où quelqu'un repart les mains vides, et il
     n'avait qu'une phrase grise. Ce qu'il lui manquait n'est pas une excuse :
     c'est la distinction entre « nous ne savons rien de cette eau » et « cette
     eau n'a rien » — les deux ne se confondent jamais ici — et une porte de
     sortie plutôt qu'un cul-de-sac.

     Le texte est construit par le DOM et non par innerHTML : ce que le
     visiteur a tapé y est réinjecté, et une commune peut légitimement
     s'appeler « L'Isle-sur-le-Doubs ». */
  function absente(q){
    const li = document.createElement("li");
    li.className = "vide vide-corpus";

    const t = document.createElement("h3");
    t.textContent = "« " + q + " » n'est pas encore dans le corpus";
    li.appendChild(t);

    const p1 = document.createElement("p");
    p1.textContent = "Ce n'est pas une information sur son eau. Une commune "
      + "absente n'est pas une commune dont l'eau serait bonne : c'est une "
      + "commune dont le tour n'est pas encore venu.";
    li.appendChild(p1);

    const p2 = document.createElement("p");
    p2.textContent = "La collecte se fait département par département, et elle "
      + "avance vite. Si vous voulez savoir quand le vôtre sera versé, ou "
      + "signaler une erreur : ";
    const a = document.createElement("a");
    a.href = "contact.html";
    a.className = "lien-fort";
    a.textContent = "écrire à l'Observatoire";
    p2.appendChild(a);
    p2.appendChild(document.createTextNode("."));
    li.appendChild(p2);

    return li;
  }

  function chercher(q){
    if(INDEX === null){ enAttente = q; return; }
    liste.innerHTML = "";
    /* La saisie telle qu'elle a été tapée est conservée : c'est elle qu'on
       réaffiche. `pl()` rabat les accents et la casse pour comparer, et
       renvoyer « vesoul » à quelqu'un qui a écrit « Vesoul » donne
       l'impression que la machine a mal lu. */
    const saisie = q.trim();
    q = pl(saisie);
    if(q.length < 2) return;

    const trouves = INDEX.map(c => [score(c, q), c])
      .filter(([s]) => s < 99)
      .sort((a, b) => a[0] - b[0] || a[1].n.localeCompare(b[1].n, "fr"))
      .slice(0, 25);

    if(!trouves.length){
      liste.appendChild(absente(saisie));
      return;
    }
    trouves.forEach(([, c]) => liste.appendChild(ligne(c)));
  }

  champ.addEventListener("input", () => chercher(champ.value));
  champ.addEventListener("search", () => chercher(champ.value));
})();

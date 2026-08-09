/* ===========================================================================
   Filtrer la carte par état — et le tableau avec elle.

   Ce script n'ajoute rien à la page : il en retire. Sans lui, la carte et le
   tableau montrent tout, la légende reste lisible, et aucune information n'est
   perdue. C'est délibéré — la vitrine est un dossier de fichiers statiques qui
   doit rester consultable dans dix ans, et un écran qui ne se compose qu'une
   fois le JavaScript exécuté n'a pas cette propriété.

   Deux règles de méthode passent par ici, et ce sont elles qui ont dicté la
   forme :

   1. **Le compte d'un état masqué reste affiché**, barré, dans la légende. On
      retire un état de la vue, jamais du décompte. Un filtre qui ferait
      disparaître « 38 communes non documentées » de l'écran présenterait une
      absence de donnée comme une bonne nouvelle — c'est exactement ce que le
      §8bis, obligation 4, interdit.

   2. **La carte et le tableau se filtrent ensemble.** Ils portent le même
      attribut `data-niveau` et sont masqués par la même règle CSS. S'ils
      pouvaient diverger, un lecteur qui a masqué un état sur la carte le
      retrouverait dans le tableau juste dessous, et ne saurait plus lequel des
      deux il regarde.
   =========================================================================== */
(function(){
  const boutons = Array.prototype.slice.call(
    document.querySelectorAll(".carte-legende .lg-btn"));
  if(!boutons.length) return;

  /* Les classes de masquage vivent sur <body> : la carte et le tableau ne sont
     pas dans le même conteneur, et rien ne garantit qu'ils le resteront. */
  const cible = document.body;

  /* Une annonce pour qui n'a pas la carte sous les yeux. Sans elle, actionner
     un bouton ne produirait aucun retour perceptible au lecteur d'écran : la
     seule conséquence visible est la disparition de cercles dans un SVG. */
  const dire = document.createElement("p");
  dire.className = "lg-aide";
  dire.setAttribute("role", "status");
  dire.setAttribute("aria-live", "polite");
  const legende = document.querySelector(".carte-legende");
  legende.parentNode.insertBefore(dire, legende.nextSibling);

  function etatCourant(){
    return boutons.filter(b => b.getAttribute("aria-pressed") === "false");
  }

  function annoncer(){
    const caches = etatCourant();
    if(!caches.length){
      dire.textContent = "";
      return;
    }
    if(caches.length === boutons.length){
      dire.textContent = "Tous les états sont masqués : la carte et le tableau "
        + "sont vides. Les comptes restent affichés dans la légende.";
      return;
    }
    const noms = caches.map(b => (b.textContent || "").trim().replace(/\s+/g, " "));
    dire.textContent = caches.length + " état(s) masqué(s) sur la carte et dans "
      + "le tableau — " + noms.join(" ; ")
      + ". Leur compte reste affiché dans la légende.";
  }

  boutons.forEach(function(b){
    b.addEventListener("click", function(){
      const niveau = b.getAttribute("data-niveau");
      const visible = b.getAttribute("aria-pressed") !== "false";
      b.setAttribute("aria-pressed", visible ? "false" : "true");
      cible.classList.toggle("masque-" + niveau, visible);
      annoncer();
    });
  });
})();

/* ===========================================================================
   La barre : le thème et le menu replié.

   Ce que ce script NE fait PAS : restaurer le thème au chargement. Cela se
   passe dans le `<head>`, en quatre lignes inlinées, et il faut que ce soit là
   pour que ça marche — un fichier externe est chargé après le premier rendu,
   donc un visiteur qui a choisi le sombre verrait d'abord une page claire puis
   un basculement. Le seul script du site autorisé à bloquer le rendu est
   celui-là, et c'est pourquoi il ne fait rien d'autre.

   Ici on ne trouve que ce qui répond à un clic. Sans JavaScript, le thème suit
   `prefers-color-scheme` et le menu reste déployé : la page est complète, elle
   perd seulement le choix.
   =========================================================================== */
(function(){
  var html = document.documentElement;

  /* Le thème courant : celui qu'on a choisi, sinon celui du système. Lire
     l'attribut d'abord et le média ensuite — l'inverse ignorerait le choix. */
  function courant(){
    return html.getAttribute("data-theme")
        || (window.matchMedia("(prefers-color-scheme: dark)").matches
              ? "sombre" : "clair");
  }

  var bouton = document.getElementById("theme");
  if(bouton){
    bouton.addEventListener("click", function(){
      var suivant = courant() === "sombre" ? "clair" : "sombre";
      html.setAttribute("data-theme", suivant);
      bouton.setAttribute("aria-pressed", suivant === "sombre" ? "true" : "false");
      /* Le choix survit à la visite. En navigation privée, `localStorage` lève
         plutôt que de refuser : sans ce filet, le bouton cesserait de
         fonctionner au lieu de simplement oublier. */
      try { localStorage.setItem("theme", suivant); } catch(e){}
    });
  }

  var burger = document.getElementById("burger");
  var menu = document.getElementById("menu");
  if(burger && menu){
    burger.addEventListener("click", function(){
      var ouvert = menu.classList.toggle("ouvert");
      burger.setAttribute("aria-expanded", ouvert ? "true" : "false");
      burger.setAttribute("aria-label", ouvert ? "Fermer le menu" : "Ouvrir le menu");
    });
    /* Échap referme : un menu qui recouvre la page et qu'on ne peut fermer
       qu'en visant un petit bouton est un piège au clavier. */
    document.addEventListener("keydown", function(e){
      if(e.key === "Escape" && menu.classList.contains("ouvert")) burger.click();
    });
  }

  /* --- Les sous-menus -----------------------------------------------------
     Ils fonctionnent SANS ce bloc : `<details>` s'ouvre au clic et au clavier
     tout seul, et c'est pour ça qu'ils sont écrits ainsi. Ce qui suit n'ajoute
     que le confort qu'on attend d'une barre de navigation — et rien de ce
     confort n'est nécessaire pour atteindre une page. */
  var sous = Array.prototype.slice.call(document.querySelectorAll(".menu .sous"));
  if(sous.length){
    /* Un seul ouvert à la fois. Deux panneaux déroulés se recouvrent, et le
       second se lit par-dessus le premier. */
    sous.forEach(function(d){
      d.addEventListener("toggle", function(){
        if(!d.open) return;
        sous.forEach(function(a){ if(a !== d) a.open = false; });
      });
    });

    /* Cliquer ailleurs referme. Sans cela, un panneau ouvert suit le lecteur
       sur toute la page — il faut revenir le fermer, ce que personne ne fait.
       Replié, on ne referme pas : le menu est alors une colonne, pas un
       panneau flottant, et il se referme par le burger. */
    document.addEventListener("click", function(e){
      if(menu && menu.classList.contains("ouvert")) return;
      sous.forEach(function(d){ if(d.open && !d.contains(e.target)) d.open = false; });
    });

    /* Échap referme le panneau et **rend le focus à son intitulé** : sans ce
       retour, la tabulation repartirait du début du document. */
    document.addEventListener("keydown", function(e){
      if(e.key !== "Escape") return;
      sous.forEach(function(d){
        if(!d.open) return;
        d.open = false;
        var s = d.querySelector("summary");
        if(s && d.contains(document.activeElement)) s.focus();
      });
    });
  }
})();

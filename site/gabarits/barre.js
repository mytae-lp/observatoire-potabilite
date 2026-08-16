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
})();

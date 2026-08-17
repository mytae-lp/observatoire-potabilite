/* ===========================================================================
   Trier un tableau par ses en-têtes — pour les tableaux d'un dossier.

   Même règle que partout ailleurs sur ce site : ce script ne fait que
   RÉORDONNER ce qui est déjà dans la page. Sans lui, le tableau s'affiche dans
   son ordre par défaut et reste juste. C'est ce qui permet à la vitrine d'être
   un dossier de fichiers statiques encore lisible dans dix ans.

   L'ordre par défaut n'est pas neutre et il est choisi : l'ancienneté du plus
   ancien abandon. Un classement par nombre de dépassements dirait d'abord
   l'effort de recherche de chaque commune, et se lirait comme un palmarès —
   ce que le projet refuse (« on ne trouve que ce qu'on cherche »). Les
   en-têtes le proposent quand même, parce qu'aucun ordre n'est le bon et que
   le lecteur doit pouvoir en changer.

   La clé de tri est dans `data-v`, distincte de ce qui est affiché :
   « 119 mois » se trie sur 119, jamais sur la chaîne — sans quoi 9 passerait
   après 119.
   =========================================================================== */
(function () {
  var tables = document.querySelectorAll("table[data-triable]");
  if (!tables.length) return;

  Array.prototype.forEach.call(tables, function (tab) {
    var entetes = tab.querySelectorAll("thead th");
    Array.prototype.forEach.call(entetes, function (th, col) {
      var bouton = th.querySelector(".th-tri");
      if (!bouton) return;

      bouton.addEventListener("click", function () {
        var sens = th.getAttribute("aria-sort") === "ascending"
                 ? "descending" : "ascending";
        /* `aria-sort` ne vaut que sur UNE colonne : le laisser sur l'ancienne
           annoncerait deux tris simultanés à un lecteur d'écran. */
        Array.prototype.forEach.call(entetes, function (x) {
          x.setAttribute("aria-sort", "none");
        });
        th.setAttribute("aria-sort", sens);

        var num = th.dataset.type === "num";
        var signe = sens === "ascending" ? 1 : -1;
        var corps = tab.tBodies[0];
        Array.prototype.slice.call(corps.rows).sort(function (a, b) {
          var x = a.cells[col].dataset.v, y = b.cells[col].dataset.v;
          if (num) return signe * (parseFloat(x) - parseFloat(y));
          /* `localeCompare` en français : sans lui, « Étilleux » se rangerait
             après « Ymonville ». */
          return signe * String(x).localeCompare(String(y), "fr");
        }).forEach(function (r) { corps.appendChild(r); });
      });
    });
  });
})();

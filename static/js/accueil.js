"use strict";

(() => {
  const champ = document.getElementById("q-globale");
  const boite = document.getElementById("resultats-globaux");

  if (!champ || !boite) return;

  const effectuer = async () => {
    const q = champ.value.trim();
    if (q.length < 2) {
      boite.hidden = true;
      boite.innerHTML = "";
      return;
    }
    try {
      const resultats = await api(`/api/recherche?q=${encodeURIComponent(q)}`);
      if (!resultats.length) {
        boite.innerHTML = `<p class="aucun">Aucun résultat dans l'ontologie pour « ${esc(q)} ».</p>`;
      } else {
        boite.innerHTML = resultats.map((r) => {
          const lien = { faune: "/faune/", flore: "/flore/",
                         cours_eau: "/cours-deau/", habitat: "/habitats/" }[r.type];
          const icone = { faune: "🦁", flore: "🌿", cours_eau: "💧",
                          habitat: "📍" }[r.type] || "•";
          const typeAff = { faune: "espèce animale", flore: "espèce végétale",
                            cours_eau: "cours d'eau", habitat: "habitat (localité)" }[r.type] || r.type;
          return `<a class="res-global" href="${lien}${encodeURIComponent(r.id)}">
            <span class="res-icone">${icone}</span>
            <span class="res-nom">${esc(r.nom)} <em>${esc(r.scientifique)}</em></span>
            <span class="res-type">${esc(typeAff)}</span></a>`;
        }).join("");
      }
      boite.hidden = false;
    } catch (err) {
      boite.innerHTML = `<p class="aucun">Erreur de recherche : ${esc(err.message)}</p>`;
      boite.hidden = false;
    }
  };

  champ.addEventListener("input", debounce(effectuer, 300));
  champ.addEventListener("focus", effectuer);
  document.addEventListener("click", (e) => {
    if (!boite.contains(e.target) && e.target !== champ) boite.hidden = true;
  });
})();

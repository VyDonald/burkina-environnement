"use strict";

(() => {
  /* --- Compteurs animés --- */
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll(".stat-nb[data-val]").forEach((el) => {
    const cible = parseInt(el.dataset.val, 10) || 0;
    if (reduced || !cible) { el.textContent = cible; return; }
    let demarre = false;
    const animer = () => {
      if (demarre) return;
      demarre = true;
      const duree = 1200;
      const depart = performance.now();
      const tick = (now) => {
        const p = Math.min((now - depart) / duree, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(cible * ease);
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    if ("IntersectionObserver" in window) {
      const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { animer(); obs.disconnect(); } }, { threshold: .3 });
      obs.observe(el);
    } else { animer(); }
  });

  /* --- Recherche globale --- */
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

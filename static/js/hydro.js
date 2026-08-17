"use strict";

(() => {
  const grille = document.getElementById("grille");
  const pagination = document.getElementById("pagination");
  const compteur = document.getElementById("compteur");
  const titreResultats = document.getElementById("titre-resultats");

  if (!grille) return;

  const selects = {
    type: document.getElementById("f-type"),
    bassin: document.getElementById("f-bassin"),
  };

  let page = 1;

  const API_CLE = { type: "types", bassin: "bassins" };

  const chargerFiltres = async () => {
    const o = await api("/api/cours-deau/filtres");
    Object.entries(API_CLE).forEach(([cle, apiCle]) => {
      const sel = selects[cle];
      if (!sel) return;
      (o[apiCle] || []).forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.id;
        opt.textContent = item.nom;
        sel.appendChild(opt);
      });
    });
  };

  const params = () => {
    const p = new URLSearchParams({ page });
    const q = document.getElementById("q").value.trim();
    if (q) p.set("q", q);
    Object.entries(selects).forEach(([cle, sel]) => {
      if (sel.value) p.set(cle, sel.value);
    });
    return p;
  };

  const carte = (c) => {
    const longueur = c.longueur ? ` · ${esc(c.longueur)}` : "";
    const bassin = c.bassin ? `<p class="famille">${esc(c.bassin)}</p>` : "";
    return `<a class="carte-espece" href="/cours-deau/${encodeURIComponent(c.id)}">
      <div class="carte-photo carte-photo-eau">${esc(c.nom[0] || "?")}</div>
      <div class="carte-corps">
        <h3>${esc(c.nom)}</h3>
        <p class="sc">${esc(c.typeLabel)}${longueur}</p>
        ${bassin}
        <div class="badges"><span class="badge-milieu">Régime : ${esc(c.regime || "—")}</span></div>
      </div>
    </a>`;
  };

  const charger = async () => {
    grille.innerHTML = `<div class="chargement">Chargement…</div>`;
    try {
      const d = await api(`/api/cours-deau?${params()}`);
      grille.innerHTML = d.resultats.length ? d.resultats.map(carte).join("") :
        `<p class="aucun">Aucun cours d'eau ne correspond aux critères.</p>`;
      compteur.textContent = d.total
        ? `${d.resultats.length} affiché${d.resultats.length > 1 ? "s" : ""} sur ${d.total}`
        : "";
      let pag = "";
      if (d.page > 1) pag += `<button class="btn page" data-p="${d.page - 1}">← Précédente</button>`;
      if (d.has_more) pag += `<button class="btn page" data-p="${d.page + 1}">Suivante →</button>`;
      pagination.innerHTML = pag;
      pagination.querySelectorAll(".page").forEach((b) =>
        b.addEventListener("click", () => { page = parseInt(b.dataset.p, 10); charger(); window.scrollTo({ top: 0 }); }));
    } catch (err) {
      grille.innerHTML = `<p class="aucun">Erreur lors du chargement (${esc(err.message)}). Rechargez la page puis réessayez.</p>`;
    }
  };

  document.getElementById("form-recherche").addEventListener("submit", (e) => {
    e.preventDefault(); page = 1; charger();
  });
  document.getElementById("btn-appliquer").addEventListener("click", () => { page = 1; charger(); });
  document.getElementById("btn-reinitialiser").addEventListener("click", () => {
    Object.values(selects).forEach((sel) => { sel.value = ""; });
    document.getElementById("q").value = "";
    titreResultats.textContent = "Tous les cours d'eau";
    page = 1; charger();
  });

  chargerFiltres().then(charger);
})();

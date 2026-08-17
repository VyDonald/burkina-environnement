"use strict";

(() => {
  const grille = document.getElementById("grille");
  const pagination = document.getElementById("pagination");
  const compteur = document.getElementById("compteur");
  const titreResultats = document.getElementById("titre-resultats");

  if (!grille) return;

  const selects = {
    famille: document.getElementById("f-famille"),
    usage: document.getElementById("f-usage"),
    zone: document.getElementById("f-zone"),
    condition: document.getElementById("f-condition"),
    localite: document.getElementById("f-localite"),
  };

  let page = 1;

  const API_CLE = {
    famille: "familles", usage: "usages", zone: "zones",
    condition: "conditions", localite: "localites",
  };

  const chargerFiltres = async () => {
    const o = await api("/api/flore/filtres");
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

  const carte = (p) => {
    const usages = (p.usages || []).map((u) => `<span class="badge-usage">${esc(u)}</span>`).join("");
    const zones = (p.zones || []).map((z) => `<span class="badge-milieu">${esc(z)}</span>`).join("");
    const nomsLocaux = p.nomsLocaux && p.nomsLocaux.length
      ? `<p class="noms-locaux">${esc(p.nomsLocaux.join(", "))}</p>` : "";
    return `<a class="carte-espece" href="/flore/${encodeURIComponent(p.id)}">
      <div class="carte-photo carte-photo-vert">${esc(p.nomCourant[0] || "?")}</div>
      <div class="carte-corps">
        <h3>${esc(p.nomCourant)}</h3>
        <p class="sc">${esc(p.nomScientifique)}</p>
        <p class="famille">${esc(p.famille)}</p>
        ${nomsLocaux}
        <div class="badges">${usages}${zones}</div>
      </div>
    </a>`;
  };

  const charger = async () => {
    grille.innerHTML = `<div class="chargement">Chargement…</div>`;
    try {
      const d = await api(`/api/flore/plantes?${params()}`);
      grille.innerHTML = d.resultats.length ? d.resultats.map(carte).join("") :
        `<p class="aucun">Aucune espèce végétale ne correspond aux critères.</p>`;
      compteur.textContent = d.total
        ? `${d.resultats.length} affichée${d.resultats.length > 1 ? "s" : ""} sur ${d.total}`
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
    titreResultats.textContent = "Toutes les espèces végétales";
    page = 1; charger();
  });

  chargerFiltres().then(charger);
})();

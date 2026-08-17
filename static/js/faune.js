"use strict";

(() => {
  const grille = document.getElementById("grille");
  const pagination = document.getElementById("pagination");
  const compteur = document.getElementById("compteur");
  const titreResultats = document.getElementById("titre-resultats");

  if (!grille) return;

  const selects = {
    groupe: document.getElementById("f-groupe"),
    famille: document.getElementById("f-famille"),
    milieu: document.getElementById("f-milieu"),
    statut: document.getElementById("f-statut"),
    localite: document.getElementById("f-localite"),
    menaces: document.getElementById("f-menacees"),
  };

  let page = 1;

  const API_CLE = {
    groupe: "groupes", famille: "familles", milieu: "milieux",
    statut: "statuts", localite: "localites",
  };

  const chargerFiltres = async () => {
    const o = await api("/api/faune/filtres");
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
      const val = cle === "menaces" ? (sel.checked ? "1" : "") : sel.value;
      if (val) p.set(cle, val);
    });
    return p;
  };

  const carte = (e) => {
    const photo = (e.medias && e.medias[0]) || "";
    const media = photo
      ? `<div class="carte-photo"><img src="${esc(photo)}" alt="${esc(e.nomCommun)}" loading="lazy"></div>`
      : `<div class="carte-photo carte-photo-vide">${esc(e.nomCommun[0] || "?")}</div>`;
    const statut = e.codeStatut
      ? `<span class="badge-statut badge-${esc(e.codeStatut)}">${esc(e.libelleStatut)} (${esc(e.codeStatut)})</span>`
      : "";
    const milieux = (e.milieux || []).map((m) => `<span class="badge-milieu">${esc(m)}</span>`).join("");
    return `<a class="carte-espece" href="/faune/${encodeURIComponent(e.id)}">
      ${media}
      <div class="carte-corps">
        <h3>${esc(e.nomCommun)}</h3>
        <p class="sc">${esc(e.nomScientifique)}</p>
        <p class="famille">${esc(e.famille)}${e.groupe ? ` · ${esc(e.groupe)}` : ""}</p>
        <div class="badges">${statut}${milieux}</div>
      </div>
    </a>`;
  };

  const charger = async () => {
    grille.innerHTML = `<div class="chargement">Chargement…</div>`;
    try {
      const d = await api(`/api/faune/especes?${params()}`);
      grille.innerHTML = d.resultats.length ? d.resultats.map(carte).join("") :
        `<p class="aucun">Aucune espèce ne correspond aux critères.</p>`;
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
    Object.entries(selects).forEach(([cle, sel]) => {
      if (cle === "menaces") sel.checked = false;
      else sel.value = "";
    });
    document.getElementById("q").value = "";
    titreResultats.textContent = "Toutes les espèces animales";
    page = 1; charger();
  });

  chargerFiltres().then(charger);
})();

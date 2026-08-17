"use strict";

(() => {
  const elCarte = document.getElementById("carte");
  if (!elCarte) return;

  const carte = L.map("carte").setView([12.3, -1.5], 7);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap",
  }).addTo(carte);

  const rayon = document.getElementById("c-rayon");
  const locSelect = document.getElementById("c-loc");
  const panneau = document.getElementById("panneau-rayon");
  const rayTitre = document.getElementById("rayon-titre");
  const rayContenu = document.getElementById("rayon-contenu");

  const marqueurs = { localites: [], regions: [], provinces: [], communes: [] };
  const popups = {};

  const couleur = { localites: "#2563eb", regions: "#dc2626", provinces: "#16a34a", communes: "#d97706" };
  const libelle = { regions: "Région", provinces: "Province", communes: "Commune" };

  const popupLocalite = (l) => {
    const especes = l.nbEspeces ? ` ${l.nbEspeces} espèce(s)` : "";
    const menacees = l.nbMenacees > 0
      ? `<span class="badge-statut badge-CR">${l.nbMenacees} menacée(s)</span>` : "";
    const plantes = l.nbPlantes ? ` · ${l.nbPlantes} plante(s)` : "";
    return `<strong>${esc(l.nom)}</strong><br>
      ${especes}${plantes}<br>${menacees}
      <br><a href="/habitats/${encodeURIComponent(l.id)}" style="color:#2d6a4f;font-weight:600;">Voir l'habitat →</a>`;
  };

  const chargerLocalites = async () => {
    const localites = await api("/api/carte");
    const entetes = {};
    localites.forEach((l) => {
      const m = L.circleMarker([parseFloat(l.lat), parseFloat(l.lon)], {
        radius: 6 + Math.min(10, parseInt(l.nbEspeces, 10) || 0),
        color: "#fff", weight: 1, fillColor: couleur.localites,
        fillOpacity: l.nbMenacees > 0 ? 0.95 : 0.6,
      }).addTo(carte);
      m.bindPopup(popupLocalite(l));
      marqueurs.localites.push(m);
      entetes[l.id] = l.nom;

      const opt = document.createElement("option");
      opt.value = l.id; opt.textContent = l.nom;
      locSelect.appendChild(opt);
    });

    const parametre = new URLSearchParams(location.search).get("localite");
    if (parametre && entetes[parametre]) {
      const cible = localites.find((l) => l.id === parametre);
      carte.flyTo([parseFloat(cible.lat), parseFloat(cible.lon)], 8);
      setTimeout(() => {
        const m = marqueurs.localites.find((mm) => mm.getLatLng().lat === parseFloat(cible.lat));
        if (m) m.openPopup();
      }, 700);
    }
  };

  const chargerAdmin = async (couche) => {
    const data = await api(`/api/carte/administratif?couche=${couche}`);
    marqueurs[couche] = data.map((e) =>
      L.circleMarker([parseFloat(e.lat), parseFloat(e.lon)], {
        radius: couche === "communes" ? 4 : 6,
        color: "#fff", weight: 1, fillColor: couleur[couche], fillOpacity: 0.75,
      }).addTo(carte)
    ).map((m, i) => {
      m.bindPopup(`<strong>${esc(libelle[couche])}</strong> : ${esc(data[i].nom)}`);
      return m;
    });
  };

  const rafraichirAdmin = (couche, actif) => {
    marqueurs[couche].forEach((m) => {
      if (actif) carte.addLayer(m); else carte.removeLayer(m);
    });
  };

  document.querySelectorAll(".c-admin").forEach((cb) => {
    cb.addEventListener("change", async () => {
      const couche = cb.id.replace("c-admin-", "");
      if (cb.checked) {
        if (!marqueurs[couche].length) {
          try { await chargerAdmin(couche); } catch { return; }
        }
        rafraichirAdmin(couche, true);
      } else {
        rafraichirAdmin(couche, false);
      }
    });
  });

  document.getElementById("c-rechercher").addEventListener("click", async () => {
    const loc = locSelect.value;
    if (!loc) return;
    const localites = await api("/api/carte");
    const cible = localites.find((l) => l.id === loc);
    const km = parseFloat(rayon.value) || 100;

    const cercles = [];
    carte.eachLayer((l) => { if (l instanceof L.Circle) cercles.push(l); });
    cercles.forEach((c) => carte.removeLayer(c));

    L.circle([parseFloat(cible.lat), parseFloat(cible.lon)], { radius: km * 1000 })
      .setStyle({ color: "#dc2626", fillColor: "#dc2626", fillOpacity: 0.06, weight: 1.5 })
      .addTo(carte);
    carte.flyTo([parseFloat(cible.lat), parseFloat(cible.lon)], 8);

    const resultats = await api(`/api/carte/rayon?lat=${cible.lat}&lon=${cible.lon}&rayon=${km}`);
    rayTitre.textContent = `${resultats.length} localité(s) dans un rayon de ${km} km autour de ${cible.nom}`;
    rayContenu.innerHTML = resultats.map((r) => {
      const especes = r.especes.length ? r.especes.map((e) => {
        const statut = e.codeStatut
          ? `<span class="badge-statut badge-${esc(e.codeStatut)}">${esc(e.libelleStatut)}</span>` : "";
        return `<li><a href="/faune/${encodeURIComponent(e.id)}">${esc(e.nomCommun)}</a> <em>${esc(e.nomScientifique)}</em>${statut}</li>`;
      }).join("") : "<li class='degrade'>Aucune espèce recensée</li>";
      return `<div class="rayon-loc">
        <strong>${esc(r.nom)}</strong> <span class="degrade">— ${r.dist.toFixed(1)} km</span>
        <ul>${especes}</ul></div>`;
    }).join("");
    panneau.hidden = false;
  });

  document.getElementById("rayon-fermer").addEventListener("click", () => {
    panneau.hidden = true;
  });

  chargerLocalites();
})();

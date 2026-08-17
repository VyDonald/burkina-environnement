"use strict";

const api = async (url) => {
  const rep = await fetch(url);
  if (!rep.ok) throw new Error(`HTTP ${rep.status}`);
  return rep.json();
};

const esc = (v) => {
  return String(v == null ? "" : v)
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#39;");
};

const debounce = (fn, delai = 350) => {
  let minuterie;
  return (...args) => {
    clearTimeout(minuterie);
    minuterie = setTimeout(() => fn(...args), delai);
  };
};

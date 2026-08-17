"""Logique métier : HABITATS (localités) — contexte administratif, faune, flore, cours d'eau."""

from .commun import _filtre_burkina, _haversine_km, localite_hors_burkina
from .sparql import PREFIX, run, short_name, _uri


def liste_habitats():
    """Toutes les localités (habitats) avec compteurs faune / flore / cours d'eau."""
    rows = run(f"""
{PREFIX}
SELECT ?l ?nom ?lat ?lon
       (COUNT(DISTINCT ?e) AS ?faune)
       (COUNT(DISTINCT ?p) AS ?flore)
       (COUNT(DISTINCT ?ce) AS ?coursEau)
WHERE {{
  ?l a en:Localite ; en:nomLocalite ?nom .
  {_filtre_burkina("?l")}
  OPTIONAL {{ ?l en:latitude ?lat }} OPTIONAL {{ ?l en:longitude ?lon }}
  OPTIONAL {{ ?e a en:EspeceAnimale ; en:estObserveeDans ?l }}
  OPTIONAL {{ ?p a en:EspeceVegetale ; en:estPresenteDans ?l }}
  OPTIONAL {{ ?ce a ?t ; en:traverse ?l .
             FILTER(?t = en:Fleuve || ?t = en:Riviere || ?t = en:Marigot) }}
}}
GROUP BY ?l ?nom ?lat ?lon
ORDER BY ?nom
""")
    return [{
        "uri": r["l"], "id": short_name(r["l"]), "nom": r["nom"],
        "lat": r.get("lat"), "lon": r.get("lon"),
        "faune": int(r["faune"]), "flore": int(r["flore"]),
        "coursEau": int(r["coursEau"]),
    } for r in rows]


def _contexte_administratif(lat, lon):
    """Commune la plus proche (Haversine) puis chaîne Commune > Province > Région."""
    if not lat or not lon:
        return None
    rows = run(f"""
{PREFIX}
SELECT ?c ?nomC ?latC ?lonC ?prov ?nomP ?reg ?nomR WHERE {{
  ?c a en:Commune ; en:nomLocalite ?nomC ; en:latitude ?latC ; en:longitude ?lonC .
  OPTIONAL {{ ?c en:estSitueeDans ?prov . ?prov a en:Province ; en:nomLocalite ?nomP .
             OPTIONAL {{ ?prov en:estSitueeDans ?reg . ?reg a en:Region ; en:nomLocalite ?nomR }} }}
}}
""")
    if not rows:
        return None
    best = None
    best_dist = float("inf")
    for r in rows:
        try:
            d = _haversine_km(float(lat), float(lon), float(r["latC"]), float(r["lonC"]))
        except (ValueError, KeyError):
            continue
        if d < best_dist:
            best_dist = d
            best = r
    if not best:
        return None
    return {
        "commune": {"uri": best["c"], "id": short_name(best["c"]), "nom": best["nomC"]},
        "province": {"id": short_name(best["prov"]), "nom": best.get("nomP")}
                    if best.get("prov") else None,
        "region": {"id": short_name(best["reg"]), "nom": best.get("nomR")}
                  if best.get("reg") else None,
        "distanceKm": round(best_dist, 1),
    }


def fiche_habitat(uri):
    """Fiche complète d'un habitat (localité)."""
    u = _uri(uri)
    if localite_hors_burkina(uri):
        return None
    nom = lat = lon = geom = None
    for r in run(f"{PREFIX}\nSELECT ?p ?o WHERE {{ {u} ?p ?o }}"):
        prop = short_name(r["p"])
        if prop == "nomLocalite":
            nom = r["o"]
        elif prop == "latitude":
            lat = r["o"]
        elif prop == "longitude":
            lon = r["o"]
        elif prop == "geometrieWKT":
            geom = r["o"]

    if nom is None:
        return None

    faune = run(f"""
{PREFIX}
SELECT ?e ?nomScientifique ?nomCommun ?codeStatut ?libelleStatut ?urlMedia WHERE {{
  ?e en:estObserveeDans {u} ;
     en:nomScientifique ?nomScientifique ; en:nomCommun ?nomCommun .
  OPTIONAL {{ ?e en:aStatutConservation ?st .
             ?st en:codeUICN ?codeStatut ; en:libelleStatut ?libelleStatut }}
  OPTIONAL {{ ?e en:aPourMedia ?md . ?md en:urlMedia ?urlMedia }}
}}
ORDER BY ?nomScientifique
""")
    faune = [dict(e, id=short_name(e["e"])) for e in faune]

    flore = run(f"""
{PREFIX}
SELECT ?p ?nomCourant ?nomScientifique ?nomFamille WHERE {{
  ?p en:estPresenteDans {u} ; en:nomCourant ?nomCourant ;
     en:nomScientifique ?nomScientifique ;
     en:appartientAFamilleBotanique ?f .
  ?f en:nomTaxon ?nomFamille .
}}
ORDER BY ?nomCourant
""")
    flore = [dict(p, id=short_name(p["p"])) for p in flore]

    cours_eau = run(f"""
{PREFIX}
SELECT ?ce ?nom ?type WHERE {{
  ?ce en:traverse {u} ; en:nomOfficiel ?nom .
  OPTIONAL {{ ?ce a ?type . VALUES ?type {{ en:Fleuve en:Riviere en:Marigot }} }}
}}
ORDER BY ?nom
""")
    cours_eau = [dict(c, id=short_name(c["ce"]),
                      type=short_name(c["type"]) if c.get("type") else "")
                 for c in cours_eau]

    return {
        "uri": uri,
        "id": short_name(uri),
        "nom": nom,
        "lat": lat, "lon": lon, "geom": geom,
        "administratif": _contexte_administratif(lat, lon),
        "faune": faune,
        "flore": flore,
        "cours_eau": cours_eau,
    }

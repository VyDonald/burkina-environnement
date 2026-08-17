"""Logique métier partagée : statistiques, recherche globale, carte spatiale."""

from .sparql import NS, PREFIX, UOM_KM, accent_regex, run, short_name, _uri

TYPES_COURS_EAU = "(?t = en:Fleuve || ?t = en:Riviere || ?t = en:Marigot)"

# Localités de l'ontologie qui ne relèvent PAS du Burkina Faso
# (zones écologiques transfrontalières décrites dans d'autres pays).
LOCALITES_HORS_BURKINA = {
    NS + "localite_ceinture_des_savanes_soudano_guineennes_du_senegal_au_soudan",
    NS + "localite_savanes_du_burkina_faso_present_dans_19_pays_d_afrique",
}


def _filtre_burkina(variable):
    """FILTER SPARQL excluant les localités hors Burkina Faso."""
    iris = ", ".join(_uri(u) for u in sorted(LOCALITES_HORS_BURKINA))
    return f"FILTER({variable} NOT IN ({iris}))"


def localite_hors_burkina(uri):
    """Vrai si une IRI de localité est hors Burkina Faso."""
    return uri in LOCALITES_HORS_BURKINA


def stats_accueil():
    """Compteurs globaux pour la page d'accueil (toute l'ontologie)."""
    rows = run(f"""
{PREFIX}
SELECT ?stat ?valeur WHERE {{
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("especesAnimales" AS ?stat)
     WHERE {{ ?e a en:EspeceAnimale }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("especesVegetales" AS ?stat)
     WHERE {{ ?e a en:EspeceVegetale }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("coursEau" AS ?stat)
     WHERE {{ ?e a ?t . FILTER({TYPES_COURS_EAU}) }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("localites" AS ?stat)
     WHERE {{ ?e a en:Localite . {_filtre_burkina("?e")} }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("regions" AS ?stat)
     WHERE {{ ?e a en:Region }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("provinces" AS ?stat)
     WHERE {{ ?e a en:Province }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("communes" AS ?stat)
     WHERE {{ ?e a en:Commune }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("menacees" AS ?stat)
     WHERE {{
       ?e a en:EspeceAnimale ; en:aStatutConservation ?s .
       ?s en:codeUICN ?c . FILTER(?c IN ("CR", "EN")) }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("famillesZoologiques" AS ?stat)
     WHERE {{ ?e a en:FamilleZoologique }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("famillesBotaniques" AS ?stat)
     WHERE {{ ?e a en:FamilleBotanique }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("usagesMedicinaux" AS ?stat)
     WHERE {{ ?e a en:UsageMedicinal }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("pathologies" AS ?stat)
     WHERE {{ ?e a en:Pathologie }} }}
  UNION
  {{ SELECT (COUNT(DISTINCT ?e) AS ?valeur) ("photos" AS ?stat)
     WHERE {{ ?e a en:Photo }} }}
}}
""")
    stats = {}
    for r in rows:
        stats[r["stat"]] = int(r["valeur"])
    return stats


def recherche_globale(q, limite=12):
    """Recherche libre sur l'ensemble des trois domaines."""
    qq = accent_regex(q)
    rows = run(f"""
{PREFIX}
SELECT ?uri ?type ?nom ?scientifique WHERE {{
  {{ ?uri a en:EspeceAnimale ; en:nomCommun ?nom .
     OPTIONAL {{ ?uri en:nomScientifique ?scientifique }}
     BIND("faune" AS ?type) }}
  UNION
  {{ ?uri a en:EspeceAnimale ; en:nomScientifique ?nom . BIND("faune" AS ?type) }}
  UNION
  {{ ?uri a en:EspeceVegetale ; en:nomCourant ?nom .
     OPTIONAL {{ ?uri en:nomScientifique ?scientifique }}
     BIND("flore" AS ?type) }}
  UNION
  {{ ?uri a en:EspeceVegetale ; en:nomScientifique ?nom . BIND("flore" AS ?type) }}
  UNION
  {{ ?uri a ?t ; en:nomOfficiel ?nom .
     FILTER({TYPES_COURS_EAU})
     BIND("cours_eau" AS ?type) }}
  UNION
  {{ ?uri a en:Localite ; en:nomLocalite ?nom .
     {_filtre_burkina("?uri")}
     BIND("habitat" AS ?type) }}
  FILTER(REGEX(LCASE(?nom), "{qq}"))
}}
ORDER BY ?nom
LIMIT {int(limite)}
""")
    resultats = []
    vus = set()
    for r in rows:
        if r["uri"] in vus:
            continue
        vus.add(r["uri"])
        resultats.append({
            "uri": r["uri"], "id": short_name(r["uri"]), "type": r["type"],
            "nom": r["nom"],
            "scientifique": r.get("scientifique") or "",
        })
    return resultats


def localites_carte():
    """Localités géolocalisées avec nombre d'espèces animales et menacées."""
    return [dict(r, id=short_name(r["l"])) for r in run(f"""
{PREFIX}
SELECT ?l ?nom ?lat ?lon
       (COUNT(DISTINCT ?e) AS ?nbEspeces)
       (COUNT(DISTINCT ?em) AS ?nbMenacees)
       (COUNT(DISTINCT ?pv) AS ?nbPlantes)
WHERE {{
  ?l a en:Localite ; en:nomLocalite ?nom ; en:latitude ?lat ; en:longitude ?lon .
  {_filtre_burkina("?l")}
  OPTIONAL {{ ?e en:estObserveeDans ?l }}
  OPTIONAL {{
    ?em en:estObserveeDans ?l ; en:aStatutConservation ?sm .
    ?sm en:codeUICN ?c . FILTER(?c IN ("CR", "EN"))
  }}
  OPTIONAL {{ ?pv en:estPresenteDans ?l }}
}}
GROUP BY ?l ?nom ?lat ?lon
""")]


def localites_rayon(lat, lon, rayon_km):
    """Localités à moins de rayon_km d'un point, avec les espèces animales."""
    localites = run(f"""
{PREFIX}
SELECT ?l ?nom ?lat ?lon
       (geof:greatCircleDistance(?lat, ?lon, {float(lat):f}, {float(lon):f}, {UOM_KM}) AS ?dist)
WHERE {{
  ?l a en:Localite ; en:nomLocalite ?nom ; en:latitude ?lat ; en:longitude ?lon .
  {_filtre_burkina("?l")}
  FILTER(geof:greatCircleDistance(?lat, ?lon, {float(lat):f}, {float(lon):f}, {UOM_KM}) <= {float(rayon_km):f})
}}
ORDER BY ?dist
""")
    resultat = []
    for l in localites:
        especes = run(f"""
{PREFIX}
SELECT ?e ?nomScientifique ?nomCommun ?codeStatut ?libelleStatut ?urlMedia WHERE {{
  ?e en:estObserveeDans {_uri(l['l'])} ;
     en:nomScientifique ?nomScientifique ;
     en:nomCommun ?nomCommun .
  OPTIONAL {{ ?e en:aStatutConservation ?st . ?st en:codeUICN ?codeStatut ; en:libelleStatut ?libelleStatut }}
  OPTIONAL {{ ?e en:aPourMedia ?md . ?md en:urlMedia ?urlMedia }}
}}
ORDER BY ?nomScientifique
""")
        especes = [dict(e, id=short_name(e["e"])) for e in especes]
        resultat.append({
            "uri": l["l"], "id": short_name(l["l"]), "nom": l["nom"],
            "lat": l["lat"], "lon": l["lon"], "dist": float(l["dist"]),
            "especes": especes,
        })
    return resultat


def couche_administrative(couche):
    """Entités administratives géolocalisées (régions, provinces, communes)."""
    classe = {"regions": "Region", "provinces": "Province",
              "communes": "Commune"}.get(couche)
    if not classe:
        return []
    return run(f"""
{PREFIX}
SELECT ?e ?nom ?lat ?lon WHERE {{
  ?e a en:{classe} ; en:nomLocalite ?nom ; en:latitude ?lat ; en:longitude ?lon .
}}
ORDER BY ?nom
""")

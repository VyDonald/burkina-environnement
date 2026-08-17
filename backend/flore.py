"""Logique métier : FLORE (espèces végétales)."""

from .commun import _filtre_burkina, localite_hors_burkina
from .sparql import PREFIX, accent_regex, run, short_name, _uri

USAGES = [
    ("usage_medicinal", "UsageMedicinal", "Usage médicinal"),
    ("usage_alimentaire", "UsageAlimentaire", "Usage alimentaire"),
    ("usage_artisanal", "UsageArtisanal", "Usage artisanal"),
    ("usage_ornemental", "UsageOrnemental", "Usage ornemental"),
]

NIVEAUX_BOTANIQUE = {
    "Regne": 1, "Embranchement": 2, "ClasseBotanique": 3,
    "Ordre": 4, "FamilleBotanique": 5,
}


def _type_usage(nom_classe):
    for _, classe, _ in USAGES:
        if classe == nom_classe:
            return classe
    return nom_classe


def recherche_plantes(q=None, famille=None, usage=None, zone=None,
                      condition=None, localite=None, page=1, page_size=12):
    """Recherche et filtrage des espèces végétales (liste paginée)."""
    clauses = [
        "?plante a en:EspeceVegetale ;",
        "        en:nomCourant ?nomCourant ;",
        "        en:nomScientifique ?nomScientifique ;",
        "        en:appartientAFamilleBotanique ?famille .",
        "?famille en:nomTaxon ?nomFamille .",
    ]
    optional_usage = (
        "OPTIONAL { ?plante en:aPourUsage ?u . ?u a ?typeUsage . "
        "FILTER(?typeUsage IN (en:UsageMedicinal, en:UsageAlimentaire, "
        "en:UsageArtisanal, en:UsageOrnemental)) }")
    optional_zone = (
        "OPTIONAL { ?plante en:appartientAZoneClimatique ?z . "
        "?z en:nomZoneClimatique ?nomZone }")
    optional_local = "OPTIONAL { ?plante en:nomLocal ?nomLocal }"

    if q:
        qq = accent_regex(q)
        clauses.append(
            f'FILTER(REGEX(LCASE(?nomCourant), "{qq}") || '
            f'REGEX(LCASE(?nomScientifique), "{qq}") || '
            f'REGEX(LCASE(STR(?nomLocal)), "{qq}"))')
    if famille:
        clauses.append(f"FILTER(?famille = {_uri(famille)})")
    if usage:
        clauses.append(f"?plante en:aPourUsage ?ufilt . ?ufilt a {_uri(usage)} .")
    if zone:
        clauses.append(f"?plante en:appartientAZoneClimatique {_uri(zone)} .")
    if condition:
        clauses.append(f"?plante en:aConditionCulture {_uri(condition)} .")
    if localite:
        clauses.append(f"?plante en:estPresenteDans {_uri(localite)} .")

    clauses.append(optional_usage)
    clauses.append(optional_zone)
    clauses.append(optional_local)

    select = (
        "SELECT ?plante ?nomCourant ?nomScientifique ?nomFamille "
        "(GROUP_CONCAT(DISTINCT ?typeUsage; SEPARATOR=' | ') AS ?usages) "
        "(GROUP_CONCAT(DISTINCT ?nomZone; SEPARATOR=' | ') AS ?zones) "
        "(GROUP_CONCAT(DISTINCT ?nomLocal; SEPARATOR=' | ') AS ?nomsLocaux) "
    )
    group = ("GROUP BY ?plante ?nomCourant ?nomScientifique ?nomFamille")

    offset = max(0, page - 1) * page_size
    where = (
        f"WHERE {{\n" + "\n".join("  " + c for c in clauses) + "\n}"
    )
    query = (
        f"{PREFIX}\n{select}\n"
        f"{where}\n"
        f"{group}\n"
        f"ORDER BY LCASE(?nomCourant)\n"
        f"LIMIT {page_size + 1} OFFSET {offset}"
    )
    rows = run(query)
    has_more = len(rows) > page_size
    rows = rows[:page_size]

    total = int(run(
        f"{PREFIX}\nSELECT (COUNT(DISTINCT ?plante) AS ?total) {where}"
    )[0]["total"])

    labels_usages = {c: l for _, c, l in USAGES}
    resultats = []
    for r in rows:
        usages = [labels_usages.get(short_name(u), u)
                  for u in (r.get("usages") or "").split(" | ") if u]
        resultats.append({
            "uri": r["plante"],
            "id": short_name(r["plante"]),
            "nomCourant": r["nomCourant"],
            "nomScientifique": r["nomScientifique"],
            "famille": r["nomFamille"],
            "usages": usages,
            "zones": [z for z in (r.get("zones") or "").split(" | ") if z],
            "nomsLocaux": [n for n in (r.get("nomsLocaux") or "").split(" | ") if n],
        })
    return resultats, has_more, total


def fiche_plante(uri):
    """Fiche complète d'une espèce végétale."""
    u = _uri(uri)
    info = {}

    for r in run(f"{PREFIX}\nSELECT ?p ?o WHERE {{ {u} ?p ?o }}"):
        prop = short_name(r["p"])
        if prop in ("type", "label"):
            continue
        val = r["o"]
        if prop in ("aPourUsage", "estPresenteDans", "appartientAZoneClimatique",
                    "aConditionCulture"):
            info.setdefault(prop, []).append(val)
        elif prop == "nomLocal":
            info.setdefault(prop, []).append(val)
        elif prop == "appartientAFamilleBotanique":
            info.setdefault("famille", val)
        else:
            info.setdefault(prop, val)

    # Famille botanique + chaîne taxonomique (Règne -> Famille)
    famille_info = None
    taxons = []
    if info.get("famille"):
        fam = info["famille"]
        for r in run(f"""
{PREFIX}
SELECT ?niveau ?nom WHERE {{
  {{ <{fam}> a en:FamilleBotanique ; en:nomTaxon ?nom . BIND("FamilleBotanique" AS ?niveau) }}
  UNION
  {{ <{fam}> en:appartientAOrdre ?o . ?o en:nomTaxon ?nom . BIND("Ordre" AS ?niveau) }}
  UNION
  {{ <{fam}> en:appartientAOrdre ?o . ?o en:appartientAClasseBotanique ?c .
     ?c en:nomTaxon ?nom . BIND("ClasseBotanique" AS ?niveau) }}
  UNION
  {{ <{fam}> en:appartientAOrdre ?o . ?o en:appartientAClasseBotanique ?c .
     ?c en:appartientAEmbranchement ?e . ?e en:nomTaxon ?nom .
     BIND("Embranchement" AS ?niveau) }}
  UNION
  {{ <{fam}> en:appartientAOrdre ?o . ?o en:appartientAClasseBotanique ?c .
     ?c en:appartientAEmbranchement ?e . ?e en:appartientARegne ?reg .
     ?reg en:nomTaxon ?nom . BIND("Regne" AS ?niveau) }}
}}"""):
            niveau = r["niveau"]
            taxons.append({
                "classe": niveau, "nom": r["nom"], "rang": NIVEAUX_BOTANIQUE.get(niveau, 9),
            })
        taxons.sort(key=lambda t: t["rang"])
        famille_info = {"uri": fam, "id": short_name(fam),
                        "nom": taxons[0]["nom"] if taxons else short_name(fam)}

    # Usages détaillés (médicinal/alimentaire/artisanal/ornemental)
    usages_bruts = info.get("aPourUsage", [])
    usages = {}
    if usages_bruts:
        for r in run(f"""
{PREFIX}
SELECT ?usage ?typeUsage ?nomPatho ?nomMode ?nomPartie WHERE {{
  VALUES ?usage {{ {" ".join(_uri(u) for u in usages_bruts)} }}
  ?usage a ?typeUsage .
  OPTIONAL {{ ?usage en:soigne ?patho . ?patho en:nomPathologie ?nomPatho }}
  OPTIONAL {{ ?usage en:aPourModePreparation ?mode . ?mode en:nomModePreparation ?nomMode }}
  OPTIONAL {{ ?usage en:utilisePartie ?partie . ?partie en:nomPartie ?nomPartie }}
}}"""):
            if r["typeUsage"] not in usages:
                usages[r["typeUsage"]] = {"pathologies": [], "modes": [], "parties": []}
            u = usages[r["typeUsage"]]
            if r.get("nomPatho"):
                u["pathologies"].append(r["nomPatho"])
            if r.get("nomMode"):
                u["modes"].append(r["nomMode"])
            if r.get("nomPartie"):
                u["parties"].append(r["nomPartie"])
    for u in usages.values():
        for k in u:
            u[k] = sorted(set(u[k]))

    usages_liste = []
    for classe, nom in [(c, l) for _, c, l in USAGES]:
        if classe in usages:
            usages_liste.append({"classe": classe, "label": nom, **usages[classe]})

    # Zones climatiques
    zones = []
    for z in info.get("appartientAZoneClimatique", []):
        for r in run(f"{PREFIX}\nSELECT ?n WHERE {{ {_uri(z)} en:nomZoneClimatique ?n }}"):
            zones.append(r["n"])

    # Conditions de culture
    conditions = []
    for c in info.get("aConditionCulture", []):
        for r in run(f"{PREFIX}\nSELECT ?n WHERE {{ {_uri(c)} en:nomTypeCulture ?n }}"):
            conditions.append(r["n"])

    # Localités de présence
    localites = []
    for l in [loc for loc in info.get("estPresenteDans", [])
              if not localite_hors_burkina(loc)]:
        for r in run(f"""
{PREFIX}
SELECT ?l ?nom ?lat ?lon WHERE {{
  {_uri(l)} a en:Localite ; en:nomLocalite ?nom .
  OPTIONAL {{ {_uri(l)} en:latitude ?lat }} OPTIONAL {{ {_uri(l)} en:longitude ?lon }}
}}"""):
            localites.append({"uri": l, "id": short_name(l), "nom": r["nom"],
                              "lat": r.get("lat"), "lon": r.get("lon")})

    return {
        "uri": uri,
        "id": short_name(uri),
        "nomCourant": info.get("nomCourant"),
        "nomScientifique": info.get("nomScientifique"),
        "nomsLocaux": info.get("nomLocal", []),
        "description": info.get("description"),
        "precautions": info.get("precautions"),
        "hauteurMoyenne": ((info.get("hauteurMoyenne") or "").rstrip(" m") + " m")
                          if info.get("hauteurMoyenne") else None,
        "source": info.get("source"),
        "famille": famille_info,
        "taxons": taxons,
        "usages": usages_liste,
        "zones": sorted(set(zones)),
        "conditions": sorted(set(conditions)),
        "localites": localites,
    }


def options_plantes():
    """Options de filtres pour la flore."""
    rows = run(f"""
{PREFIX}
SELECT ?classe ?uri ?nom WHERE {{
  {{ ?uri a en:FamilleBotanique ; en:nomTaxon ?nom . BIND("familles" AS ?classe) }}
  UNION
  {{ ?uri a en:ZoneClimatique ; en:nomZoneClimatique ?nom . BIND("zones" AS ?classe) }}
  UNION
  {{ ?uri a en:TypeCulture ; en:nomTypeCulture ?nom . BIND("conditions" AS ?classe) }}
  UNION
  {{ ?uri a en:Localite ; en:nomLocalite ?nom . {_filtre_burkina("?uri")} . BIND("localites" AS ?classe) }}
}}
ORDER BY ?classe ?nom
""")
    options = {"familles": [], "zones": [], "conditions": [], "localites": [],
               "usages": [
                   {"id": c, "uri": _uri(c).strip("<>"), "nom": label}
                   for _, c, label in USAGES
               ]}
    for r in rows:
        options[r["classe"]].append({
            "uri": r["uri"], "id": short_name(r["uri"]), "nom": r["nom"],
        })
    return options

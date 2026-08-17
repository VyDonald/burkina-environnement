"""Logique métier : COURS D'EAU (fleuves, rivières, marigots)."""

from .sparql import PREFIX, accent_regex, run, short_name, _uri

TYPES_COURS_EAU = [
    ("Fleuve", "Fleuve"),
    ("Riviere", "Rivière"),
    ("Marigot", "Marigot"),
]

TYPE_VALUES = "(?type = en:Fleuve || ?type = en:Riviere || ?type = en:Marigot)"


def _lien_nom(rows, cle_uri, cle_nom):
    """Dédoublonne des paires (uri -> nom)."""
    resultats = []
    vus = set()
    for r in rows:
        if r[cle_uri] in vus:
            continue
        vus.add(r[cle_uri])
        resultats.append({"uri": r[cle_uri], "id": short_name(r[cle_uri]),
                          "nom": r[cle_nom]})
    return resultats


def liste_cours_eau(q=None, type_ce=None, bassin=None, page=1, page_size=12):
    """Liste des cours d'eau (paginée) avec type, régime, longueur et bassin."""
    clauses = [
        "?ce a ?type .",
        f"FILTER({TYPE_VALUES})",
        "?ce en:nomOfficiel ?nom .",
        "OPTIONAL { ?ce en:regime ?regime }",
        "OPTIONAL { ?ce en:longueur ?longueur }",
    ]
    optional_bassin = (
        "OPTIONAL { ?ce en:estRattacheA ?sb . ?b a en:BassinVersant ; "
        "en:aPourSousBassin ?sb ; rdfs:label ?bassin }")

    if q:
        qq = accent_regex(q)
        clauses.append(f'FILTER(REGEX(LCASE(?nom), "{qq}"))')
    if type_ce:
        clauses.append(f"FILTER(?type = {_uri(type_ce)})")
    if bassin:
        optional_bassin = (
            f"?ce en:estRattacheA ?sb . ?b a en:BassinVersant ; "
            f"en:aPourSousBassin ?sb ; rdfs:label ?bassin . "
            f"FILTER(?b = {_uri(bassin)})")
    clauses.append(optional_bassin)

    select = ("SELECT ?ce ?type ?nom ?regime ?longueur ?bassin ")
    offset = max(0, page - 1) * page_size
    where = (
        f"WHERE {{\n" + "\n".join("  " + c for c in clauses) + "\n}"
    )
    query = (
        f"{PREFIX}\n{select}\n"
        f"{where}\n"
        f"ORDER BY ?type LCASE(?nom)\n"
        f"LIMIT {page_size + 1} OFFSET {offset}"
    )
    rows = run(query)
    has_more = len(rows) > page_size
    rows = rows[:page_size]

    total = int(run(
        f"{PREFIX}\nSELECT (COUNT(DISTINCT ?ce) AS ?total) {where}"
    )[0]["total"])

    labels = {t: l for t, l in TYPES_COURS_EAU}
    resultats = []
    for r in rows:
        resultats.append({
            "uri": r["ce"],
            "id": short_name(r["ce"]),
            "nom": r["nom"],
            "type": short_name(r["type"]),
            "typeLabel": labels.get(short_name(r["type"]), short_name(r["type"])),
            "regime": r.get("regime") or "",
            "longueur": r.get("longueur"),
            "bassin": r.get("bassin") or "",
        })
    return resultats, has_more, total


def fiche_cours_eau(uri):
    """Fiche complète d'un cours d'eau."""
    u = _uri(uri)
    info = {}

    for r in run(f"{PREFIX}\nSELECT ?p ?o WHERE {{ {u} ?p ?o }}"):
        prop = short_name(r["p"])
        if prop in ("type", "label"):
            if prop == "type":
                t = short_name(r["o"])
                if t in ("Fleuve", "Riviere", "Marigot"):
                    info["type"] = t
            continue
        val = r["o"]
        if prop in ("aPourAppellation", "aPourEthnie", "aPourSource",
                    "aPourVersement", "aPourCaracteristique", "estRattacheA",
                    "traverse"):
            info.setdefault(prop, []).append(val)
        else:
            info.setdefault(prop, val)

    # Appellations locales
    appellations = []
    for a in info.get("aPourAppellation", []):
        for r in run(f"{PREFIX}\nSELECT ?n WHERE {{ {_uri(a)} en:appellationLocale ?n }}"):
            appellations.append(r["n"])

    # Ethnies associées
    ethnies = []
    for e in info.get("aPourEthnie", []):
        for r in run(f"{PREFIX}\nSELECT ?n WHERE {{ {_uri(e)} en:nomEthnie ?n }}"):
            ethnies.append(r["n"])

    # Sous-bassin + bassin versant
    sous_bassin = None
    bassin = None
    for sb in info.get("estRattacheA", []):
        for r in run(f"""
{PREFIX}
SELECT ?sb ?nSb ?b ?nB WHERE {{
  {_uri(sb)} a en:SousBassin .
  OPTIONAL {{ {_uri(sb)} rdfs:label ?nSb }}
  OPTIONAL {{ ?b a en:BassinVersant ; en:aPourSousBassin {_uri(sb)} ; rdfs:label ?nB }}
}}"""):
            sous_bassin = {"uri": sb, "nom": r.get("nSb") or short_name(sb)}
            if r.get("nB"):
                bassin = {"uri": r["b"], "id": short_name(r["b"]), "nom": r["nB"]}

    # Affluent d'un cours d'eau plus grand + ses affluents
    parent = None
    for r in run(f"""
{PREFIX}
SELECT ?p ?nom ?type WHERE {{
  {u} en:affluentDe ?p .
  ?p en:nomOfficiel ?nom .
  OPTIONAL {{ ?p a ?type . VALUES ?type {{ en:Fleuve en:Riviere en:Marigot }} }}
}}"""):
        parent = {"uri": r["p"], "id": short_name(r["p"]), "nom": r["nom"],
                  "type": short_name(r["type"]) if r.get("type") else ""}

    affluents = []
    for r in run(f"""
{PREFIX}
SELECT ?c ?nom ?type WHERE {{
  ?c en:affluentDe {u} .
  ?c en:nomOfficiel ?nom .
  OPTIONAL {{ ?c a ?type . VALUES ?type {{ en:Fleuve en:Riviere en:Marigot }} }}
}}"""):
        affluents.append({"uri": r["c"], "id": short_name(r["c"]), "nom": r["nom"],
                          "type": short_name(r["type"]) if r.get("type") else ""})

    # Sources et versements (points remarquables)
    sources = []
    for s in info.get("aPourSource", []):
        for r in run(f"""
{PREFIX}
SELECT ?lbl WHERE {{ {_uri(s)} rdfs:label ?lbl }}
"""):
            sources.append({"uri": s, "nom": r["lbl"]})
    versements = []
    for s in info.get("aPourVersement", []):
        for r in run(f"""
{PREFIX}
SELECT ?lbl WHERE {{ {_uri(s)} rdfs:label ?lbl }}
"""):
            versements.append({"uri": s, "nom": r["lbl"]})

    # Caractéristiques hydrologiques
    caracteristiques = []
    for c in info.get("aPourCaracteristique", []):
        carac = {"uri": c}
        for r in run(f"""
{PREFIX}
SELECT ?p ?o WHERE {{ {_uri(c)} ?p ?o }}
"""):
            prop = short_name(r["p"])
            if prop in ("type", "source"):
                continue
            if prop == "comment":
                carac["comment"] = r["o"]
            else:
                carac[prop] = r["o"]
        caracteristiques.append(carac)

    # Entités traversées (régions, provinces, communes, localités)
    traverses = []
    for t in info.get("traverse", []):
        for r in run(f"""
{PREFIX}
SELECT ?t ?type ?lbl WHERE {{
  {_uri(t)} a ?type . {_uri(t)} rdfs:label ?lbl .
}}"""):
            if short_name(r["type"]) == "NamedIndividual":
                continue
            traverses.append({"uri": t, "nom": r["lbl"],
                              "type": short_name(r["type"])})

    labels = {t: l for t, l in TYPES_COURS_EAU}
    return {
        "uri": uri,
        "id": short_name(uri),
        "nom": info.get("nomOfficiel"),
        "type": info.get("type", ""),
        "typeLabel": labels.get(info.get("type", ""), info.get("type", "")),
        "regime": info.get("regime"),
        "longueur": info.get("longueur"),
        "source": info.get("source"),
        "appellations": sorted(set(appellations)),
        "ethnies": sorted(set(ethnies)),
        "bassin": bassin,
        "sous_bassin": sous_bassin,
        "parent": parent,
        "affluents": affluents,
        "sources": sources,
        "versements": versements,
        "caracteristiques": caracteristiques,
        "traverses": traverses,
    }


def options_cours_eau():
    """Options de filtres (types + bassins versants)."""
    types = [{"id": t, "uri": f"en:{t}", "nom": l} for t, l in TYPES_COURS_EAU]
    bassins = []
    for r in run(f"""
{PREFIX}
SELECT ?b ?nom WHERE {{ ?b a en:BassinVersant ; rdfs:label ?nom }} ORDER BY ?nom
"""):
        bassins.append({"uri": r["b"], "id": short_name(r["b"]), "nom": r["nom"]})
    return {"types": types, "bassins": bassins}

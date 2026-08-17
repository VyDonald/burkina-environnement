"""Logique métier : FAUNE (espèces animales)."""

from .commun import _filtre_burkina, localite_hors_burkina
from .sparql import PREFIX, NS, UOM_KM, accent_regex, run, short_name, _uri


def recherche_especes(q=None, groupe=None, famille=None, milieu=None,
                      statut=None, localite=None, menaces=False,
                      page=1, page_size=12):
    """Recherche et filtrage des espèces animales (liste paginée)."""
    clauses = [
        "?espece a en:EspeceAnimale ;",
        "        en:nomScientifique ?nomScientifique ;",
        "        en:nomCommun ?nomCommun ;",
        "        en:appartientAFamilleZoologique ?famille .",
        "?famille en:nomTaxon ?nomFamille .",
        "OPTIONAL { ?famille en:aPourTaxonParent* ?g .",
        "           ?g a en:GroupeZoologique ; en:nomTaxon ?nomGroupe }",
    ]
    optional_statut = ("OPTIONAL { ?espece en:aStatutConservation ?statut . "
                       "?statut en:codeUICN ?codeStatut ; "
                       "en:libelleStatut ?libelleStatut }")
    optional_milieu = ("OPTIONAL { ?espece en:vitDans ?milieu . "
                       "?milieu en:nomMilieu ?nomMilieu }")
    optional_media = ("OPTIONAL { ?espece en:aPourMedia ?media . "
                      "?media en:urlMedia ?urlMedia }")

    if q:
        qq = accent_regex(q)
        clauses.append(
            f'FILTER(REGEX(LCASE(?nomCommun), "{qq}") || '
            f'REGEX(LCASE(?nomScientifique), "{qq}"))')
    if groupe:
        clauses.append(f"?famille en:aPourTaxonParent* {_uri(groupe)} .")
    if famille:
        clauses.append(f"FILTER(?famille = {_uri(famille)})")
    if statut:
        code = statut.strip().upper()
        optional_statut = (
            f"?espece en:aStatutConservation ?statut . "
            f'?statut en:codeUICN ?codeStatut ; en:libelleStatut ?libelleStatut . '
            f'FILTER(?codeStatut = "{code}")')
    if menaces:
        optional_statut = (
            "?espece en:aStatutConservation ?statut . "
            '?statut en:codeUICN ?codeStatut ; en:libelleStatut ?libelleStatut . '
            'FILTER(?codeStatut IN ("CR", "EN"))')
    if milieu:
        optional_milieu = (
            f"?espece en:vitDans {_uri(milieu)} . "
            f"{_uri(milieu)} en:nomMilieu ?nomMilieu")
    if localite:
        clauses.append(f"?espece en:estObserveeDans {_uri(localite)} .")

    clauses.append(optional_statut)
    clauses.append(optional_milieu)
    clauses.append(optional_media)

    select = (
        "SELECT ?espece ?nomScientifique ?nomCommun ?nomFamille ?nomGroupe "
        "?codeStatut ?libelleStatut "
        "(GROUP_CONCAT(DISTINCT ?nomMilieu; SEPARATOR=' | ') AS ?milieux) "
        "(GROUP_CONCAT(DISTINCT ?urlMedia; SEPARATOR=' || ') AS ?medias) "
    )
    group = (
        "GROUP BY ?espece ?nomScientifique ?nomCommun ?nomFamille ?nomGroupe "
        "?codeStatut ?libelleStatut"
    )

    offset = max(0, page - 1) * page_size
    where = (
        f"WHERE {{\n" + "\n".join("  " + c for c in clauses) + "\n}"
    )
    query = (
        f"{PREFIX}\n{select}\n"
        f"{where}\n"
        f"{group}\n"
        f"ORDER BY LCASE(?nomScientifique)\n"
        f"LIMIT {page_size + 1} OFFSET {offset}"
    )
    rows = run(query)
    has_more = len(rows) > page_size
    rows = rows[:page_size]

    total = int(run(
        f"{PREFIX}\nSELECT (COUNT(DISTINCT ?espece) AS ?total) {where}"
    )[0]["total"])

    resultats = []
    for r in rows:
        resultats.append({
            "uri": r["espece"],
            "id": short_name(r["espece"]),
            "nomCommun": r["nomCommun"],
            "nomScientifique": r["nomScientifique"],
            "famille": r["nomFamille"],
            "groupe": r.get("nomGroupe") or "",
            "codeStatut": r.get("codeStatut") or "",
            "libelleStatut": r.get("libelleStatut") or "",
            "milieux": [m for m in (r.get("milieux") or "").split(" | ") if m],
            "medias": [u for u in (r.get("medias") or "").split(" || ") if u],
        })
    return resultats, has_more, total


RANG_ZOOLOGIQUE = {
    "Regne": 1,
    "Embranchement": 2,
    "ClasseZoologique": 3,
    "Ordre": 4,
    "GroupeZoologique": 4,
    "SousGroupeZoologique": 5,
    "SousSousGroupeZoologique": 6,
    "FamilleZoologique": 7,
}


def fiche_espece(uri):
    """Fiche complète d'une espèce animale."""
    u = _uri(uri)
    info = {}

    rows = run(f"{PREFIX}\nSELECT ?p ?o WHERE {{ {u} ?p ?o }}")
    for r in rows:
        prop = short_name(r["p"])
        if prop in ("type", "label"):
            continue
        val = r["o"]
        if prop == "appartientAFamilleZoologique":
            info.setdefault("famille", val)
        elif prop in ("vitDans", "aStatutConservation", "estObserveeDans",
                      "aPourMedia"):
            info.setdefault(prop, []).append(val)
        else:
            info.setdefault(prop, val)

    # Chaîne taxonomique zoologique complète
    taxons = []
    for r in run(f"""
{PREFIX}
SELECT ?a ?classe ?nom WHERE {{
  {u} en:appartientAFamilleZoologique ?f .
  ?f en:aPourTaxonParent* ?a .
  ?a a ?classe ; en:nomTaxon ?nom .
}}"""):
        classe = short_name(r["classe"])
        if classe not in RANG_ZOOLOGIQUE:
            continue
        taxons.append({
            "uri": r["a"], "id": short_name(r["a"]), "nom": r["nom"],
            "classe": classe, "rang": RANG_ZOOLOGIQUE[classe],
        })
    taxons.sort(key=lambda t: t["rang"])

    # Noms des milieux
    extra = {}
    milieux = info.get("vitDans", [])
    if milieux:
        for m in run(f"""
{PREFIX}
SELECT ?m ?nom WHERE {{ ?m a en:MilieuDeVie ; en:nomMilieu ?nom .
  FILTER(?m IN ({", ".join(_uri(m) for m in milieux)})) }}"""):
            extra[m["m"]] = m["nom"]

    # Statuts de conservation
    statut_info = []
    statuts = info.get("aStatutConservation", [])
    if statuts:
        for s in run(f"""
{PREFIX}
SELECT ?s ?code ?lib WHERE {{ ?s a en:StatutConservation ; en:codeUICN ?code ;
  en:libelleStatut ?lib . FILTER(?s IN ({", ".join(_uri(s) for s in statuts)})) }}"""):
            statut_info.append({"code": s["code"], "libelle": s["lib"], "uri": s["s"]})

    # Localités d'observation
    localite_info = []
    localites = [l for l in info.get("estObserveeDans", [])
                 if not localite_hors_burkina(l)]
    if localites:
        for l in run(f"""
{PREFIX}
SELECT ?l ?nom ?lat ?lon ?geom WHERE {{
  ?l a en:Localite ; en:nomLocalite ?nom .
  OPTIONAL {{ ?l en:latitude ?lat }} OPTIONAL {{ ?l en:longitude ?lon }}
  OPTIONAL {{ ?l en:geometrieWKT ?geom }}
  FILTER(?l IN ({", ".join(_uri(l) for l in localites)}))
}}"""):
            localite_info.append({
                "uri": l["l"], "id": short_name(l["l"]), "nom": l["nom"],
                "lat": l.get("lat"), "lon": l.get("lon"), "geom": l.get("geom"),
            })

    # Photos
    medias = []
    for m in info.get("aPourMedia", []):
        for r in run(f"{PREFIX}\nSELECT ?url WHERE {{ {_uri(m)} en:urlMedia ?url }}"):
            medias.append(r["url"])

    # Famille
    famille_info = None
    if info.get("famille"):
        for f in run(f"""
{PREFIX}
SELECT ?f ?nom WHERE {{ ?f a en:FamilleZoologique ; en:nomTaxon ?nom .
  FILTER(?f = {_uri(info['famille'])}) }}"""):
            famille_info = {"uri": f["f"], "id": short_name(f["f"]), "nom": f["nom"]}

    return {
        "uri": uri,
        "id": short_name(uri),
        "nomCommun": info.get("nomCommun"),
        "nomScientifique": info.get("nomScientifique"),
        "description": info.get("description"),
        "regimeAlimentaire": info.get("regimeAlimentaire"),
        "poidsMoyen": info.get("poidsMoyen"),
        "dureeVieMoyenne": info.get("dureeVieMoyenne"),
        "source": info.get("source"),
        "famille": famille_info,
        "taxons": taxons,
        "milieux": [extra.get(m, short_name(m)) for m in milieux],
        "statuts": statut_info,
        "localites": localite_info,
        "medias": medias,
    }


def options_especes():
    """Options de filtres pour la faune."""
    rows = run(f"""
{PREFIX}
SELECT ?classe ?uri ?nom ?code WHERE {{
  {{ ?uri a en:GroupeZoologique ; en:nomTaxon ?nom . BIND("groupes" AS ?classe) }}
  UNION
  {{ ?uri a en:FamilleZoologique ; en:nomTaxon ?nom . BIND("familles" AS ?classe) }}
  UNION
  {{ ?uri a en:MilieuDeVie ; en:nomMilieu ?nom . BIND("milieux" AS ?classe) }}
  UNION
  {{ ?uri a en:StatutConservation ; en:codeUICN ?code ; en:libelleStatut ?lib .
     BIND(CONCAT(?code, " (", ?lib, ")") AS ?nom) . BIND("statuts" AS ?classe) }}
  UNION
  {{ ?uri a en:Localite ; en:nomLocalite ?nom . {_filtre_burkina("?uri")} . BIND("localites" AS ?classe) }}
}}
ORDER BY ?classe ?nom
""")
    options = {"groupes": [], "familles": [], "milieux": [],
               "statuts": [], "localites": []}
    for r in rows:
        # Pour les statuts UICN, la valeur transmise est le code (CR, EN…)
        identifiant = r.get("code") or short_name(r["uri"])
        options[r["classe"]].append({
            "uri": r["uri"], "id": identifiant, "nom": r["nom"],
        })
    return options


def especes_menacees():
    """Espèces animales menacées (CR ou EN)."""
    rows = run(f"""
{PREFIX}
SELECT ?espece ?nomScientifique ?nomCommun ?nomFamille ?nomGroupe
       ?codeStatut ?libelleStatut WHERE {{
  ?espece a en:EspeceAnimale ;
          en:nomScientifique ?nomScientifique ;
          en:nomCommun ?nomCommun ;
          en:appartientAFamilleZoologique ?famille ;
          en:aStatutConservation ?statut .
  ?famille en:nomTaxon ?nomFamille .
  ?statut en:codeUICN ?codeStatut ; en:libelleStatut ?libelleStatut .
  FILTER(?codeStatut IN ("CR", "EN"))
  OPTIONAL {{ ?famille en:aPourTaxonParent* ?g .
             ?g a en:GroupeZoologique ; en:nomTaxon ?nomGroupe }}
}}
ORDER BY ?codeStatut ?nomScientifique
""")
    return [{
        "uri": r["espece"], "id": short_name(r["espece"]),
        "nomScientifique": r["nomScientifique"], "nomCommun": r["nomCommun"],
        "nomFamille": r["nomFamille"], "nomGroupe": r.get("nomGroupe") or "",
        "codeStatut": r["codeStatut"], "libelleStatut": r["libelleStatut"],
    } for r in rows]

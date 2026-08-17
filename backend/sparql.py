"""Client SPARQL générique vers le triplestore Jena Fuseki.

Responsabilité : exécuter des requêtes et retourner des résultats bruts.
Aucune logique métier ici — chaque domaine (faune, flore, cours d'eau)
fournit ses propres requêtes dans des modules séparés.
"""

import json
import os
import re

import requests

NS = "http://www.ibam-ujkz.bf/ontologies/burkina-environnement#"
ENDPOINT = os.environ.get("FUSEKI_ENDPOINT", "http://localhost:3030/environnement/query")
TIMEOUT = 120

UOM_KM = "<http://www.opengis.net/def/uom/OGC/1.0/kilometre>"

PREFIX = f"""
PREFIX en: <{NS}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
"""


def run(query):
    """Exécute un SELECT et retourne la liste des bindings (dicts)."""
    r = requests.post(
        ENDPOINT,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    payload = json.loads(r.text)
    bindings = []
    for b in payload.get("results", {}).get("bindings", []):
        row = {}
        for k, v in b.items():
            row[k] = v.get("value")
        bindings.append(row)
    return bindings


def short_name(uri):
    """Nom local d'une IRI (partie après le #)."""
    if not uri:
        return uri
    if "#" in uri:
        return uri.rsplit("#", 1)[-1]
    return uri.rsplit("/", 1)[-1]


def _uri(name):
    """Transforme un nom local (ou IRI complète) en triple pattern IRI."""
    if name.startswith("<") and name.endswith(">"):
        return name
    if name.startswith("http"):
        return f"<{name}>"
    return f"<{NS}{name}>"


_ACCENTS = {
    "a": "aàâä", "e": "eéèêë", "i": "iîï", "o": "oôö",
    "u": "uûü", "c": "cç", "n": "nñ", "y": "yÿ",
}
_BASES = {ch: base for base, variants in _ACCENTS.items() for ch in variants}


def accent_regex(terme):
    """Expression régulière SPARQL insensible aux accents.

    « guepard » devient « gu[eéèêë]pard » : la recherche fonctionne que
    l'utilisateur saisisse ou non les accents présents dans l'ontologie.
    """
    pattern = []
    for ch in terme.lower():
        base = _BASES.get(ch)
        if base:
            pattern.append(f"[{_ACCENTS[base]}]")
        else:
            pattern.append(re.escape(ch))
    return "".join(pattern)

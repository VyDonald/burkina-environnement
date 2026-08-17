"""Blueprint : COURS D'EAU (fleuves, rivières, marigots)."""

import re

from flask import Blueprint, abort, jsonify, render_template, request

from backend import cours_eau as hydro_logic
from backend.sparql import NS

hydro_bp = Blueprint("hydro", __name__)

LOCAL_NAME = re.compile(r"^[A-Za-z0-9_]+$")


@hydro_bp.route("/cours-deau")
def page_cours_eau():
    return render_template("cours_eau.html")


@hydro_bp.route("/cours-deau/<nom>")
def page_fiche(nom):
    if not LOCAL_NAME.match(nom):
        abort(404)
    fiche = hydro_logic.fiche_cours_eau(f"{NS}{nom}")
    if not fiche.get("nom"):
        abort(404)
    return render_template("cours_eau_fiche.html", fiche=fiche)


@hydro_bp.route("/api/cours-deau/filtres")
def api_filtres():
    return jsonify(hydro_logic.options_cours_eau())


@hydro_bp.route("/api/cours-deau")
def api_liste():
    page = max(1, request.args.get("page", 1, type=int))
    resultats, has_more, total = hydro_logic.liste_cours_eau(
        q=request.args.get("q"),
        type_ce=request.args.get("type"),
        bassin=request.args.get("bassin"),
        page=page,
    )
    return jsonify({"resultats": resultats, "page": page,
                    "has_more": has_more, "total": total})


@hydro_bp.route("/api/cours-deau/<nom>")
def api_fiche(nom):
    if not LOCAL_NAME.match(nom):
        abort(404)
    return jsonify(hydro_logic.fiche_cours_eau(f"{NS}{nom}"))

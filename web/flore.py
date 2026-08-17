"""Blueprint : FLORE (espèces végétales)."""

import re

from flask import Blueprint, abort, jsonify, render_template, request

from backend import flore as flore_logic
from backend.sparql import NS

flore_bp = Blueprint("flore", __name__)

LOCAL_NAME = re.compile(r"^[A-Za-z0-9_]+$")


@flore_bp.route("/flore")
def page_flore():
    return render_template("flore.html")


@flore_bp.route("/flore/<nom>")
def page_plante(nom):
    if not LOCAL_NAME.match(nom):
        abort(404)
    fiche = flore_logic.fiche_plante(f"{NS}{nom}")
    if not fiche.get("nomCourant"):
        abort(404)
    return render_template("espece_vegetale.html", fiche=fiche)


@flore_bp.route("/api/flore/filtres")
def api_filtres():
    return jsonify(flore_logic.options_plantes())


@flore_bp.route("/api/flore/plantes")
def api_plantes():
    page = max(1, request.args.get("page", 1, type=int))
    resultats, has_more, total = flore_logic.recherche_plantes(
        q=request.args.get("q"),
        famille=request.args.get("famille"),
        usage=request.args.get("usage"),
        zone=request.args.get("zone"),
        condition=request.args.get("condition"),
        localite=request.args.get("localite"),
        page=page,
    )
    return jsonify({"resultats": resultats, "page": page,
                    "has_more": has_more, "total": total})


@flore_bp.route("/api/flore/plante/<nom>")
def api_plante(nom):
    if not LOCAL_NAME.match(nom):
        abort(404)
    return jsonify(flore_logic.fiche_plante(f"{NS}{nom}"))

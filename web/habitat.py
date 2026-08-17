"""Blueprint : HABITATS (localités) — contexte administratif, faune, flore, cours d'eau."""

import re

from flask import Blueprint, abort, jsonify, render_template, request

from backend import habitat as habitat_logic
from backend.sparql import NS

habitat_bp = Blueprint("habitat", __name__)

LOCAL_NAME = re.compile(r"^[A-Za-z0-9_]+$")


@habitat_bp.route("/habitats")
def page_liste():
    return render_template("habitats.html", habitats=habitat_logic.liste_habitats())


@habitat_bp.route("/habitats/<nom>")
def page_fiche(nom):
    if not LOCAL_NAME.match(nom):
        abort(404)
    fiche = habitat_logic.fiche_habitat(f"{NS}{nom}")
    if not fiche or not fiche.get("nom"):
        abort(404)
    return render_template("habitat_fiche.html", h=fiche)


@habitat_bp.route("/api/habitats")
def api_liste():
    return jsonify(habitat_logic.liste_habitats())


@habitat_bp.route("/api/habitat/<nom>")
def api_fiche(nom):
    if not LOCAL_NAME.match(nom):
        abort(404)
    return jsonify(habitat_logic.fiche_habitat(f"{NS}{nom}"))

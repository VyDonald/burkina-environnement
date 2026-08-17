"""Blueprint : FAUNE (espèces animales + espèces menacées)."""

import re

from flask import Blueprint, abort, jsonify, render_template, request

from backend import faune as faune_logic
from backend.sparql import NS

faune_bp = Blueprint("faune", __name__)

LOCAL_NAME = re.compile(r"^[A-Za-z0-9_]+$")


def _id_ok(nom):
    return LOCAL_NAME.match(nom)


@faune_bp.route("/faune")
def page_faune():
    return render_template("faune.html")


@faune_bp.route("/faune/<nom>")
def page_espece(nom):
    if not _id_ok(nom):
        abort(404)
    fiche = faune_logic.fiche_espece(f"{NS}{nom}")
    if not fiche.get("nomScientifique"):
        abort(404)
    return render_template("espece_animale.html", fiche=fiche)


@faune_bp.route("/menacees")
def page_menacees():
    return render_template("menacees.html",
                           especes=faune_logic.especes_menacees())


@faune_bp.route("/api/faune/filtres")
def api_filtres():
    return jsonify(faune_logic.options_especes())


@faune_bp.route("/api/faune/especes")
def api_especes():
    page = max(1, request.args.get("page", 1, type=int))
    resultats, has_more, total = faune_logic.recherche_especes(
        q=request.args.get("q"),
        groupe=request.args.get("groupe"),
        famille=request.args.get("famille"),
        milieu=request.args.get("milieu"),
        statut=request.args.get("statut"),
        localite=request.args.get("localite"),
        menaces=request.args.get("menaces") == "1",
        page=page,
    )
    return jsonify({"resultats": resultats, "page": page,
                    "has_more": has_more, "total": total})


@faune_bp.route("/api/faune/espece/<nom>")
def api_espece(nom):
    if not _id_ok(nom):
        abort(404)
    return jsonify(faune_logic.fiche_espece(f"{NS}{nom}"))


@faune_bp.route("/api/menacees")
def api_menacees():
    return jsonify(faune_logic.especes_menacees())

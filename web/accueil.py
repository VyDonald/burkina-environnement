"""Blueprint : accueil (présentation + recherche globale)."""

from flask import Blueprint, jsonify, render_template, request

from backend import commun

accueil_bp = Blueprint("accueil", __name__)


@accueil_bp.route("/")
def index():
    stats = commun.stats_accueil()
    return render_template("index.html", stats=stats)


@accueil_bp.route("/api/stats")
def api_stats():
    return jsonify(commun.stats_accueil())


@accueil_bp.route("/api/recherche")
def api_recherche():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify([])
    return jsonify(commun.recherche_globale(q))

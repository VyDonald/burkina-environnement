"""Blueprint : CARTE SPATIALE (localités, rayon GeoSPARQL, découpage administratif)."""

from flask import Blueprint, abort, jsonify, render_template, request

from backend import commun

carte_bp = Blueprint("carte", __name__)


@carte_bp.route("/carte")
def page_carte():
    return render_template("carte.html")


@carte_bp.route("/api/carte")
def api_carte():
    return jsonify(commun.localites_carte())


@carte_bp.route("/api/carte/rayon")
def api_rayon():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    rayon = request.args.get("rayon", 100, type=float)
    if lat is None or lon is None or rayon <= 0:
        abort(400)
    return jsonify(commun.localites_rayon(lat, lon, rayon))


@carte_bp.route("/api/carte/administratif")
def api_administratif():
    couche = request.args.get("couche", "regions")
    return jsonify(commun.couche_administrative(couche))

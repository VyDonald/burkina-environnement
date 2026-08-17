"""Application web sémantique « Environnement du Burkina Faso ».

Point d'entrée : assemble l'application et enregistre les blueprints
(découpage par domaine : accueil, faune, flore, cours d'eau, carte).
"""

import os

from flask import Flask, jsonify

from web.accueil import accueil_bp
from web.carte import carte_bp
from web.faune import faune_bp
from web.flore import flore_bp
from web.habitat import habitat_bp
from web.hydro import hydro_bp


def create_app():
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False

    app.register_blueprint(accueil_bp)
    app.register_blueprint(faune_bp)
    app.register_blueprint(flore_bp)
    app.register_blueprint(hydro_bp)
    app.register_blueprint(carte_bp)
    app.register_blueprint(habitat_bp)

    @app.errorhandler(400)
    def bad_request(_):
        return jsonify({"erreur": "Requête invalide"}), 400

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"erreur": "Ressource introuvable"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"erreur": "Erreur interne du serveur"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug)

"""Application factory CacaoSat."""

from __future__ import annotations

import os

from flask import Flask, jsonify

from app.config import ProdConfig, get_config
from app.errors import register_error_handlers
from app.extensions import cors, db, jwt, limiter, migrate
from app.logging import configure_logging

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")
    config_cls = get_config(config_name)

    app = Flask(__name__)
    app.config.from_object(config_cls)

    if config_cls is ProdConfig:
        ProdConfig.validate()

    configure_logging(app)

    db.init_app(app)
    migrate.init_app(app, db, directory=MIGRATIONS_DIR)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # Les modèles doivent être importés pour peupler db.metadata (migrations + create_all).
    from app import models  # noqa: F401
    from app.api import api_bp

    app.register_blueprint(api_bp)

    register_error_handlers(app)
    _register_jwt_handlers(app)
    _register_cli(app)

    @app.get("/")
    def index():
        return jsonify(
            {
                "name": "CacaoSat API",
                "version": "0.1.0",
                "docs": f"{app.config['API_PREFIX']}/openapi.json",
                "health": f"{app.config['API_PREFIX']}/health",
            }
        )

    app.logger.info("CacaoSat backend démarré (config=%s)", config_name)
    return app


def _register_jwt_handlers(app: Flask) -> None:
    from flask import jsonify

    def _err(message: str, code: str, status: int = 401):
        return jsonify({"error": {"code": code, "message": message, "details": {}}}), status

    @jwt.expired_token_loader
    def _expired(_header, _payload):
        return _err("Token expiré.", "token_expired")

    @jwt.invalid_token_loader
    def _invalid(reason):
        return _err(f"Token invalide : {reason}", "token_invalid")

    @jwt.unauthorized_loader
    def _missing(reason):
        return _err(f"Authentification requise : {reason}", "unauthorized")

    @jwt.needs_fresh_token_loader
    def _stale(_header, _payload):
        return _err("Token non frais requis.", "fresh_token_required")


def _register_cli(app: Flask) -> None:
    from app.cli import register_cli

    register_cli(app)

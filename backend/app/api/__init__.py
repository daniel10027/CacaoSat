"""Enregistrement des blueprints sous /api/v1."""

from __future__ import annotations

from flask import Blueprint

from app.api.auth import auth_bp
from app.api.health import health_bp
from app.openapi import openapi_bp

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(openapi_bp)

__all__ = ["api_bp"]

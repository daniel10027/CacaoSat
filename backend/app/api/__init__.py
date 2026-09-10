"""Enregistrement des blueprints sous /api/v1."""

from __future__ import annotations

from flask import Blueprint

from app.api.alerts import alerts_bp
from app.api.analysis import analysis_bp
from app.api.auth import auth_bp
from app.api.cooperatives import cooperatives_bp
from app.api.dashboard import dashboard_bp
from app.api.health import health_bp
from app.api.parcels import parcels_bp
from app.api.producers import producers_bp
from app.api.reports import reports_bp
from app.api.sync import sync_bp
from app.openapi import openapi_bp

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

for bp in (
    health_bp,
    auth_bp,
    cooperatives_bp,
    producers_bp,
    parcels_bp,
    analysis_bp,
    dashboard_bp,
    reports_bp,
    alerts_bp,
    sync_bp,
    openapi_bp,
):
    api_bp.register_blueprint(bp)

__all__ = ["api_bp"]

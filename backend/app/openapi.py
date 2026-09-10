"""Spécification OpenAPI minimale — enrichie au Lot 2 (apispec + Swagger UI)."""

from __future__ import annotations

from flask import Blueprint, jsonify

openapi_bp = Blueprint("openapi", __name__)

_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "CacaoSat API",
        "version": "0.1.0",
        "description": "Traçabilité géospatiale du cacao ivoirien — conformité EUDR.",
    },
    "servers": [{"url": "/api/v1"}],
    "paths": {
        "/health": {"get": {"summary": "Liveness", "responses": {"200": {"description": "OK"}}}},
        "/health/ready": {
            "get": {"summary": "Readiness (DB + Redis)", "responses": {"200": {"description": "Ready"}}}
        },
        "/auth/login": {
            "post": {"summary": "Authentification", "responses": {"200": {"description": "Tokens JWT"}}}
        },
        "/auth/refresh": {
            "post": {"summary": "Renouvellement du token", "responses": {"200": {"description": "Tokens JWT"}}}
        },
        "/auth/me": {"get": {"summary": "Profil courant", "responses": {"200": {"description": "Utilisateur"}}}},
    },
}


@openapi_bp.get("/openapi.json")
def openapi_json():
    return jsonify(_SPEC)

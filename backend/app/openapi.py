"""Spécification OpenAPI de l'API CacaoSat (maintenue à la main, zéro dépendance).

Sert de contrat pour la génération des types côté web et pour la console Swagger.
"""

from __future__ import annotations

from flask import Blueprint, Response, jsonify

openapi_bp = Blueprint("openapi", __name__)

_TAG_AUTH = "Auth"
_TAG_COOP = "Coopératives"
_TAG_PROD = "Producteurs"
_TAG_PARC = "Parcelles"
_TAG_DASH = "Dashboard"
_TAG_OPS = "Ops"

_ok = {"200": {"description": "OK"}}
_created = {"201": {"description": "Créé"}}


def _path(summary, tag, responses=None, secured=True, body=None, params=None):
    op: dict = {"summary": summary, "tags": [tag], "responses": responses or _ok}
    if secured:
        op["security"] = [{"bearerAuth": []}]
    if body:
        op["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": {"type": "object", "properties": body}}},
        }
    if params:
        op["parameters"] = params
    return op


_QUERY_PAGE = [
    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 25}},
    {"name": "sort", "in": "query", "schema": {"type": "string"}},
    {"name": "order", "in": "query", "schema": {"type": "string", "enum": ["asc", "desc"]}},
]

SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "CacaoSat API",
        "version": "0.2.0",
        "description": "Traçabilité géospatiale du cacao ivoirien — conformité EUDR.",
    },
    "servers": [{"url": "/api/v1"}],
    "components": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
    },
    "paths": {
        "/health": {"get": _path("Liveness", _TAG_OPS, secured=False)},
        "/health/ready": {"get": _path("Readiness (DB + Redis)", _TAG_OPS, secured=False)},
        "/metrics": {"get": _path("Métriques Prometheus", _TAG_OPS, secured=False)},
        "/auth/login": {
            "post": _path(
                "Authentification",
                _TAG_AUTH,
                secured=False,
                body={"email": {"type": "string"}, "password": {"type": "string"}},
            )
        },
        "/auth/refresh": {"post": _path("Renouvellement du token", _TAG_AUTH)},
        "/auth/me": {"get": _path("Profil courant", _TAG_AUTH)},
        "/cooperatives": {
            "get": _path("Liste des coopératives (portée selon rôle)", _TAG_COOP),
            "post": _path(
                "Créer une coopérative (regulator/admin)",
                _TAG_COOP,
                responses=_created,
                body={"name": {"type": "string"}, "code": {"type": "string"}},
            ),
        },
        "/cooperatives/{coop_id}": {
            "get": _path("Détail d'une coopérative", _TAG_COOP),
            "patch": _path("Mettre à jour une coopérative", _TAG_COOP),
        },
        "/producers": {
            "get": _path(
                "Liste des producteurs (paginée, recherche `q`)",
                _TAG_PROD,
                params=_QUERY_PAGE
                + [{"name": "q", "in": "query", "schema": {"type": "string"}},
                   {"name": "cooperative_id", "in": "query", "schema": {"type": "string"}}],
            ),
            "post": _path(
                "Créer un producteur",
                _TAG_PROD,
                responses=_created,
                body={"full_name": {"type": "string"}, "national_id": {"type": "string"}},
            ),
        },
        "/producers/{producer_id}": {
            "get": _path("Détail d'un producteur", _TAG_PROD),
            "patch": _path("Mettre à jour un producteur", _TAG_PROD),
            "delete": _path("Archiver un producteur (soft delete)", _TAG_PROD,
                            responses={"204": {"description": "Supprimé"}}),
        },
        "/parcels": {
            "get": _path(
                "Liste des parcelles (filtres : cooperative_id, producer_id, risk_level, "
                "eudr_status, status, q, bbox)",
                _TAG_PARC,
                params=_QUERY_PAGE
                + [
                    {"name": "cooperative_id", "in": "query", "schema": {"type": "string"}},
                    {"name": "producer_id", "in": "query", "schema": {"type": "string"}},
                    {
                        "name": "risk_level",
                        "in": "query",
                        "schema": {"type": "string", "enum": ["low", "medium", "high"]},
                    },
                    {
                        "name": "eudr_status",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["compliant", "at_risk", "non_compliant"],
                        },
                    },
                    {
                        "name": "bbox",
                        "in": "query",
                        "schema": {"type": "string"},
                        "description": "minx,miny,maxx,maxy",
                    },
                ],
            ),
            "post": _path(
                "Créer une parcelle (géométrie GeoJSON)",
                _TAG_PARC,
                responses=_created,
                body={
                    "geometry": {"type": "object", "description": "GeoJSON Polygon (EPSG:4326)"},
                    "producer_id": {"type": "string"},
                    "planting_year": {"type": "integer"},
                    "gps_accuracy_m": {"type": "number"},
                    "collection_method": {"type": "string"},
                },
            ),
        },
        "/parcels/{parcel_id}": {
            "get": _path("Détail d'une parcelle (+ dernier score & analyse)", _TAG_PARC),
            "patch": _path("Mettre à jour une parcelle", _TAG_PARC),
            "delete": _path("Archiver une parcelle", _TAG_PARC,
                            responses={"204": {"description": "Supprimé"}}),
        },
        "/parcels/{parcel_id}.geojson": {
            "get": _path("Parcelle au format GeoJSON FeatureCollection", _TAG_PARC)
        },
        "/parcels/{parcel_id}/analyze": {
            "post": _path(
                "Lancer l'analyse satellite + scoring EUDR",
                _TAG_PARC,
                responses={"201": {"description": "{ analysis_run, compliance_score }"}},
            )
        },
        "/parcels/{parcel_id}/history": {
            "get": _path("Historique des analyses et scores", _TAG_PARC)
        },
        "/analysis/batch": {
            "post": _path(
                "Analyser un lot de parcelles",
                _TAG_PARC,
                responses={"200": {"description": "Résumé"}, "207": {"description": "Partiel"}},
                body={"parcel_ids": {"type": "array", "items": {"type": "string"}},
                      "cooperative_id": {"type": "string"}},
            )
        },
        "/dashboard/summary": {
            "get": _path(
                "KPIs de conformité de la coopérative",
                _TAG_DASH,
                params=[{"name": "cooperative_id", "in": "query", "schema": {"type": "string"}}],
            )
        },
        "/dashboard/map": {
            "get": _path(
                "Parcelles scorées au format GeoJSON",
                _TAG_DASH,
                params=[
                    {"name": "cooperative_id", "in": "query", "schema": {"type": "string"}},
                    {"name": "bbox", "in": "query", "schema": {"type": "string"}},
                ],
            )
        },
        "/dashboard/regions": {
            "get": _path("Agrégats nationaux par région (public)", _TAG_DASH, secured=False)
        },
        "/openapi.json": {"get": _path("Cette spécification", _TAG_OPS, secured=False)},
        "/docs": {"get": _path("Console Swagger UI", _TAG_OPS, secured=False)},
    },
}

_SWAGGER_HTML = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8"><title>CacaoSat API — Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.ui = SwaggerUIBundle({ url: "openapi.json", dom_id: "#swagger" });
  </script>
</body>
</html>"""


@openapi_bp.get("/openapi.json")
def openapi_json():
    return jsonify(SPEC)


@openapi_bp.get("/docs")
def docs():
    return Response(_SWAGGER_HTML, mimetype="text/html")

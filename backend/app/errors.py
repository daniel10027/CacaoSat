"""Gestionnaires d'erreurs — enveloppe JSON uniforme."""

from __future__ import annotations

from flask import Flask, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """Erreur métier explicite levée par les services / vues."""

    def __init__(self, message: str, status: int = 400, code: str | None = None, details=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code or _default_code(status)
        self.details = details or {}


def _default_code(status: int) -> str:
    return {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "unprocessable_entity",
        429: "rate_limited",
        500: "internal_error",
    }.get(status, "error")


def _envelope(message: str, status: int, code: str, details=None):
    body = {"error": {"code": code, "message": message, "details": details or {}}}
    return jsonify(body), status


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def _handle_api_error(exc: ApiError):
        return _envelope(exc.message, exc.status, exc.code, exc.details)

    @app.errorhandler(ValidationError)
    def _handle_validation(exc: ValidationError):
        return _envelope("Données invalides.", 422, "validation_error", exc.messages)

    @app.errorhandler(IntegrityError)
    def _handle_integrity(exc: IntegrityError):
        app.logger.warning("IntegrityError: %s", exc)
        return _envelope("Conflit d'intégrité (doublon ou référence invalide).", 409, "conflict")

    @app.errorhandler(HTTPException)
    def _handle_http(exc: HTTPException):
        return _envelope(exc.description or exc.name, exc.code or 500, _default_code(exc.code or 500))

    @app.errorhandler(Exception)
    def _handle_unexpected(exc: Exception):  # pragma: no cover - filet de sécurité
        app.logger.exception("Erreur non gérée")
        if app.config.get("DEBUG"):
            raise exc
        return _envelope("Erreur interne.", 500, "internal_error")

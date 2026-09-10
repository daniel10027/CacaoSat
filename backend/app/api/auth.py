from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.errors import ApiError
from app.extensions import db, limiter
from app.models.user import User
from app.schemas.auth import login_schema, user_schema
from app.services.auth_service import authenticate, issue_tokens

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    payload = login_schema.load(request.get_json(force=True, silent=True) or {})
    user = authenticate(payload["email"], payload["password"])
    if user is None:
        raise ApiError("Identifiants invalides.", status=401)
    return jsonify(issue_tokens(user))


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = db.session.get(User, get_jwt_identity())
    if user is None or not user.is_active:
        raise ApiError("Compte introuvable ou désactivé.", status=401)
    return jsonify(issue_tokens(user))


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, get_jwt_identity())
    if user is None:
        raise ApiError("Compte introuvable.", status=404)
    return jsonify(user_schema.dump(user))

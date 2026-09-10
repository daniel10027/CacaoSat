from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.errors import ApiError
from app.extensions import db
from app.models.user import User
from app.services.sync import batch_status, bootstrap, ingest_batch

sync_bp = Blueprint("sync", __name__, url_prefix="/sync")


def _current_user() -> User:
    user = db.session.get(User, get_jwt_identity())
    if user is None or not user.is_active:
        raise ApiError("Compte introuvable.", status=401)
    return user


@sync_bp.get("/bootstrap")
@jwt_required()
def sync_bootstrap():
    return jsonify(bootstrap(_current_user(), since=request.args.get("since")))


@sync_bp.post("/batch")
@jwt_required()
def sync_batch():
    payload = request.get_json(force=True, silent=True) or {}
    result = ingest_batch(_current_user(), payload)
    status = 200 if result["status"] in {"done"} else (207 if result["accepted"] else 422)
    return jsonify(result), status


@sync_bp.get("/status/<uuid:batch_id>")
@jwt_required()
def sync_status(batch_id):
    return jsonify(batch_status(batch_id))

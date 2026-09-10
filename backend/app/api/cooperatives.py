from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.api._helpers import has_national_scope, token_cooperative_id
from app.errors import ApiError
from app.extensions import db
from app.models.cooperative import Cooperative
from app.models.enums import UserRole
from app.schemas.cooperative import (
    cooperative_schema,
    cooperative_update_schema,
    cooperatives_schema,
)
from app.security import roles_required

cooperatives_bp = Blueprint("cooperatives", __name__, url_prefix="/cooperatives")


@cooperatives_bp.get("")
@jwt_required()
def list_cooperatives():
    query = db.select(Cooperative).order_by(Cooperative.name.asc())
    if not has_national_scope():
        query = query.filter(Cooperative.id == token_cooperative_id())
    rows = db.session.scalars(query).all()
    return jsonify(cooperatives_schema.dump(rows))


@cooperatives_bp.get("/<uuid:coop_id>")
@jwt_required()
def get_cooperative(coop_id):
    coop = db.session.get(Cooperative, coop_id)
    if coop is None:
        raise ApiError("Coopérative introuvable.", status=404)
    if not has_national_scope() and str(coop_id) != str(token_cooperative_id()):
        raise ApiError("Accès refusé.", status=403)
    return jsonify(cooperative_schema.dump(coop))


@cooperatives_bp.post("")
@roles_required(UserRole.REGULATOR, UserRole.ADMIN)
def create_cooperative():
    data = cooperative_schema.load(request.get_json(force=True, silent=True) or {})
    if db.session.scalar(db.select(Cooperative).filter_by(code=data["code"])):
        raise ApiError("Ce code de coopérative existe déjà.", status=409)
    coop = Cooperative(**data)
    db.session.add(coop)
    db.session.commit()
    return jsonify(cooperative_schema.dump(coop)), 201


@cooperatives_bp.patch("/<uuid:coop_id>")
@roles_required(UserRole.REGULATOR, UserRole.ADMIN)
def update_cooperative(coop_id):
    coop = db.session.get(Cooperative, coop_id)
    if coop is None:
        raise ApiError("Coopérative introuvable.", status=404)
    data = cooperative_update_schema.load(request.get_json(force=True, silent=True) or {})
    for key, value in data.items():
        setattr(coop, key, value)
    db.session.commit()
    return jsonify(cooperative_schema.dump(coop))

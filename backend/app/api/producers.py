from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.api._helpers import (
    apply_sort,
    assert_can_access_cooperative,
    has_national_scope,
    parse_pagination,
    resolve_cooperative_scope,
    run_paginated,
    token_cooperative_id,
)
from app.errors import ApiError
from app.extensions import db
from app.models.enums import UserRole
from app.models.producer import Producer
from app.schemas.producer import producer_schema, producer_update_schema, producers_schema
from app.security import roles_required

producers_bp = Blueprint("producers", __name__, url_prefix="/producers")

_SORTABLE = {"full_name", "registered_at", "created_at", "village"}


@producers_bp.get("")
@jwt_required()
def list_producers():
    args = parse_pagination()
    query = db.select(Producer).filter(Producer.deleted_at.is_(None))

    scope = resolve_cooperative_scope(request.args.get("cooperative_id"))
    if scope is not None:
        query = query.filter(Producer.cooperative_id == scope)

    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Producer.full_name.ilike(like),
                Producer.national_id.ilike(like),
                Producer.village.ilike(like),
            )
        )

    query = apply_sort(query, Producer, args["sort"], args["order"], _SORTABLE, "full_name")
    return jsonify(run_paginated(query, args["page"], args["per_page"], producers_schema))


@producers_bp.get("/<uuid:producer_id>")
@jwt_required()
def get_producer(producer_id):
    producer = _get_or_404(producer_id)
    assert_can_access_cooperative(producer.cooperative_id)
    return jsonify(producer_schema.dump(producer))


@producers_bp.post("")
@roles_required(UserRole.AGENT, UserRole.MANAGER, UserRole.REGULATOR)
def create_producer():
    payload = producer_schema.load(request.get_json(force=True, silent=True) or {})
    if not has_national_scope():
        payload["cooperative_id"] = token_cooperative_id()
    elif not payload.get("cooperative_id"):
        raise ApiError("cooperative_id requis pour ce rôle.", status=422)
    payload.setdefault("registered_at", date.today())
    producer = Producer(**payload)
    db.session.add(producer)
    db.session.commit()
    return jsonify(producer_schema.dump(producer)), 201


@producers_bp.patch("/<uuid:producer_id>")
@roles_required(UserRole.AGENT, UserRole.MANAGER, UserRole.REGULATOR)
def update_producer(producer_id):
    producer = _get_or_404(producer_id)
    assert_can_access_cooperative(producer.cooperative_id)
    data = producer_update_schema.load(request.get_json(force=True, silent=True) or {})
    data.pop("cooperative_id", None)
    for key, value in data.items():
        setattr(producer, key, value)
    db.session.commit()
    return jsonify(producer_schema.dump(producer))


@producers_bp.delete("/<uuid:producer_id>")
@roles_required(UserRole.MANAGER, UserRole.REGULATOR)
def delete_producer(producer_id):
    producer = _get_or_404(producer_id)
    assert_can_access_cooperative(producer.cooperative_id)
    from app.models.base import utcnow

    producer.deleted_at = utcnow()
    db.session.commit()
    return "", 204


def _get_or_404(producer_id) -> Producer:
    producer = db.session.get(Producer, producer_id)
    if producer is None or producer.deleted_at is not None:
        raise ApiError("Producteur introuvable.", status=404)
    return producer

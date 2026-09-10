from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.api._helpers import has_national_scope, token_cooperative_id
from app.errors import ApiError
from app.extensions import db
from app.models.enums import UserRole
from app.models.parcel import Parcel
from app.security import roles_required
from app.services.analysis import analyze_many

analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")


@analysis_bp.post("/batch")
@roles_required(UserRole.MANAGER, UserRole.REGULATOR)
def batch():
    body = request.get_json(force=True, silent=True) or {}
    parcel_ids = body.get("parcel_ids")
    cooperative_id = body.get("cooperative_id")

    query = db.select(Parcel.id).filter(Parcel.deleted_at.is_(None))
    if not has_national_scope():
        query = query.filter(Parcel.cooperative_id == token_cooperative_id())
    elif cooperative_id:
        query = query.filter(Parcel.cooperative_id == cooperative_id)

    if parcel_ids:
        query = query.filter(Parcel.id.in_(parcel_ids))
    elif not cooperative_id and not has_national_scope():
        pass  # borné à la coopérative du token
    elif not cooperative_id:
        raise ApiError("Fournir parcel_ids ou cooperative_id.", status=422)

    ids = db.session.scalars(query).all()
    if not ids:
        raise ApiError("Aucune parcelle à analyser pour ces critères.", status=404)

    result = analyze_many(list(ids))
    status = 200 if not result["failed"] else 207
    return jsonify(result), status

from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from geoalchemy2.functions import ST_Intersects, ST_MakeEnvelope
from shapely.geometry import Point
from sqlalchemy.orm import joinedload, selectinload

from app.api._helpers import (
    assert_can_access_cooperative,
    has_national_scope,
    parse_pagination,
    resolve_cooperative_scope,
    token_cooperative_id,
)
from app.errors import ApiError
from app.extensions import db
from app.geo import feature, feature_collection, parse_bbox, polygon_area_ha, polygon_centroid, to_wkt_element
from app.models.compliance_score import ComplianceScore
from app.models.enums import ParcelSource, ParcelStatus, UserRole
from app.models.parcel import Parcel
from app.models.producer import Producer
from app.schemas.analysis import analyze_result_schema
from app.schemas.common import paginated
from app.schemas.parcel import (
    parcel_create_schema,
    parcel_schema,
    parcel_update_schema,
    parcels_schema,
)
from app.security import roles_required
from app.services.analysis import analyze_parcel

parcels_bp = Blueprint("parcels", __name__, url_prefix="/parcels")

_SORTABLE = {"code", "area_ha", "created_at", "collected_at", "score"}


def _latest_score_sq():
    return (
        db.select(
            ComplianceScore.parcel_id.label("parcel_id"),
            ComplianceScore.risk_level.label("risk_level"),
            ComplianceScore.eudr_status.label("eudr_status"),
            ComplianceScore.score.label("score"),
        )
        .distinct(ComplianceScore.parcel_id)
        .order_by(ComplianceScore.parcel_id, ComplianceScore.computed_at.desc())
        .subquery()
    )


@parcels_bp.get("")
@jwt_required()
def list_parcels():
    args = parse_pagination()
    latest = _latest_score_sq()
    query = (
        db.select(Parcel)
        .outerjoin(latest, latest.c.parcel_id == Parcel.id)
        .filter(Parcel.deleted_at.is_(None))
        .options(
            selectinload(Parcel.scores),
            selectinload(Parcel.analyses),
            joinedload(Parcel.producer),
        )
    )

    scope = resolve_cooperative_scope(request.args.get("cooperative_id"))
    if scope is not None:
        query = query.filter(Parcel.cooperative_id == scope)

    if pid := request.args.get("producer_id"):
        query = query.filter(Parcel.producer_id == pid)
    if status := request.args.get("status"):
        query = query.filter(Parcel.status == status)
    if rl := request.args.get("risk_level"):
        query = query.filter(latest.c.risk_level == rl)
    if es := request.args.get("eudr_status"):
        query = query.filter(latest.c.eudr_status == es)
    if q := request.args.get("q", "").strip():
        query = query.filter(Parcel.code.ilike(f"%{q}%"))
    if bbox := parse_bbox(request.args.get("bbox")):
        query = query.filter(
            ST_Intersects(Parcel.geometry, ST_MakeEnvelope(*bbox, 4326))
        )

    sort = args["sort"] if args["sort"] in _SORTABLE else "created_at"
    if sort == "score":
        col = latest.c.score
    else:
        col = getattr(Parcel, sort)
    query = query.order_by(col.desc() if args["order"] == "desc" else col.asc())

    count_q = db.select(db.func.count()).select_from(query.order_by(None).subquery())
    total = db.session.scalar(count_q) or 0
    page, per_page = args["page"], args["per_page"]
    rows = db.session.scalars(
        query.limit(per_page).offset((page - 1) * per_page)
    ).unique().all()
    return jsonify(paginated(parcels_schema.dump(rows), page, per_page, total))


@parcels_bp.get("/<uuid:parcel_id>")
@jwt_required()
def get_parcel(parcel_id):
    parcel = _get_or_404(parcel_id)
    assert_can_access_cooperative(parcel.cooperative_id)
    return jsonify(parcel_schema.dump(parcel))


@parcels_bp.get("/<uuid:parcel_id>.geojson")
@jwt_required()
def get_parcel_geojson(parcel_id):
    parcel = _get_or_404(parcel_id)
    assert_can_access_cooperative(parcel.cooperative_id)
    score = parcel.latest_score
    props = {
        "code": parcel.code,
        "producer": parcel.producer.full_name if parcel.producer else None,
        "area_ha": parcel.area_ha,
        "eudr_status": score.eudr_status.value if score else None,
        "risk_level": score.risk_level.value if score else None,
        "score": score.score if score else None,
    }
    return jsonify(feature_collection([feature(parcel.geometry, props, parcel.id)]))


@parcels_bp.get("/<uuid:parcel_id>/history")
@jwt_required()
def parcel_history(parcel_id):
    parcel = _get_or_404(parcel_id)
    assert_can_access_cooperative(parcel.cooperative_id)
    from app.schemas.analysis import analysis_run_schema, compliance_score_schema

    return jsonify(
        {
            "analyses": analysis_run_schema.dump(parcel.analyses, many=True),
            "scores": compliance_score_schema.dump(parcel.scores, many=True),
        }
    )


@parcels_bp.post("")
@roles_required(UserRole.AGENT, UserRole.MANAGER, UserRole.REGULATOR)
def create_parcel():
    data = parcel_create_schema.load(request.get_json(force=True, silent=True) or {})
    geom = data.pop("geometry")

    cooperative_id = data.pop("cooperative_id", None)
    if not has_national_scope():
        cooperative_id = token_cooperative_id()
    if cooperative_id is None:
        raise ApiError("cooperative_id requis.", status=422)

    producer_id = data.get("producer_id")
    if producer_id:
        producer = db.session.get(Producer, producer_id)
        if producer is None or producer.deleted_at is not None:
            raise ApiError("Producteur introuvable.", status=422)
        if str(producer.cooperative_id) != str(cooperative_id):
            raise ApiError("Le producteur n'appartient pas à cette coopérative.", status=422)

    code = data.pop("code", None) or _next_code(cooperative_id)
    if db.session.scalar(db.select(Parcel).filter_by(code=code)):
        raise ApiError("Ce code de parcelle existe déjà.", status=409)

    cx, cy = polygon_centroid(geom)
    parcel = Parcel(
        code=code,
        cooperative_id=cooperative_id,
        geometry=to_wkt_element(geom),
        centroid=to_wkt_element(Point(cx, cy)),
        area_ha=polygon_area_ha(geom),
        collected_by=get_jwt_identity(),
        **data,
    )
    if parcel.source == ParcelSource.WEB and parcel.collected_at is None:
        parcel.collected_at = datetime.now(UTC)
    db.session.add(parcel)
    db.session.commit()
    return jsonify(parcel_schema.dump(parcel)), 201


@parcels_bp.patch("/<uuid:parcel_id>")
@roles_required(UserRole.AGENT, UserRole.MANAGER, UserRole.REGULATOR)
def update_parcel(parcel_id):
    parcel = _get_or_404(parcel_id)
    assert_can_access_cooperative(parcel.cooperative_id)
    data = parcel_update_schema.load(request.get_json(force=True, silent=True) or {})
    for key, value in data.items():
        setattr(parcel, key, value)
    db.session.commit()
    return jsonify(parcel_schema.dump(parcel))


@parcels_bp.delete("/<uuid:parcel_id>")
@roles_required(UserRole.MANAGER, UserRole.REGULATOR)
def delete_parcel(parcel_id):
    parcel = _get_or_404(parcel_id)
    assert_can_access_cooperative(parcel.cooperative_id)
    from app.models.base import utcnow

    parcel.deleted_at = utcnow()
    parcel.status = ParcelStatus.ARCHIVED
    db.session.commit()
    return "", 204


@parcels_bp.post("/<uuid:parcel_id>/analyze")
@roles_required(UserRole.AGENT, UserRole.MANAGER, UserRole.REGULATOR)
def analyze(parcel_id):
    parcel = _get_or_404(parcel_id)
    assert_can_access_cooperative(parcel.cooperative_id)
    run, score = analyze_parcel(parcel.id)
    return jsonify(
        analyze_result_schema.dump({"analysis_run": run, "compliance_score": score})
    ), 201


# --- helpers ---------------------------------------------------------------
def _get_or_404(parcel_id) -> Parcel:
    parcel = db.session.get(Parcel, parcel_id)
    if parcel is None or parcel.deleted_at is not None:
        raise ApiError("Parcelle introuvable.", status=404)
    return parcel


def _next_code(cooperative_id) -> str:
    from app.models.cooperative import Cooperative

    coop = db.session.get(Cooperative, cooperative_id)
    prefix = (coop.code if coop else "PARC").upper()
    n = db.session.scalar(
        db.select(db.func.count()).select_from(Parcel).filter_by(cooperative_id=cooperative_id)
    ) or 0
    return f"{prefix}-{n + 1:04d}"

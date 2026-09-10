from __future__ import annotations

import json
import time

from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from app.api._helpers import (
    assert_can_access_cooperative,
    has_national_scope,
    parse_pagination,
    run_paginated,
    token_cooperative_id,
)
from app.audit import record as audit
from app.errors import ApiError
from app.extensions import db
from app.models.alert import Alert
from app.models.base import utcnow
from app.models.enums import UserRole
from app.models.parcel import Parcel
from app.schemas.alert import alert_schema, alerts_schema
from app.security import roles_required
from app.services.alerts import scan_for_alerts

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


def _scoped_query():
    query = (
        db.select(Alert)
        .join(Parcel, Alert.parcel_id == Parcel.id)
        .options(joinedload(Alert.parcel))
        .order_by(Alert.detected_at.desc())
    )
    if not has_national_scope():
        query = query.filter(Parcel.cooperative_id == token_cooperative_id())
    elif cid := request.args.get("cooperative_id"):
        query = query.filter(Parcel.cooperative_id == cid)
    return query


@alerts_bp.get("")
@jwt_required()
def list_alerts():
    args = parse_pagination()
    query = _scoped_query()
    if sev := request.args.get("severity"):
        query = query.filter(Alert.severity == sev)
    if atype := request.args.get("type"):
        query = query.filter(Alert.type == atype)
    ack = request.args.get("acknowledged")
    if ack is not None:
        query = query.filter(Alert.acknowledged.is_(ack.lower() in {"1", "true", "yes"}))
    return jsonify(run_paginated(query, args["page"], args["per_page"], alerts_schema))


@alerts_bp.get("/<uuid:alert_id>")
@jwt_required()
def get_alert(alert_id):
    alert = _get_or_404(alert_id)
    assert_can_access_cooperative(alert.parcel.cooperative_id)
    return jsonify(alert_schema.dump(alert))


@alerts_bp.post("/<uuid:alert_id>/acknowledge")
@roles_required(UserRole.MANAGER, UserRole.REGULATOR, UserRole.AGENT)
def acknowledge(alert_id):
    alert = _get_or_404(alert_id)
    assert_can_access_cooperative(alert.parcel.cooperative_id)
    alert.acknowledged = True
    alert.acknowledged_by = get_jwt_identity()
    alert.acknowledged_at = utcnow()
    audit("alert.acknowledge", "alert", alert.id)
    db.session.commit()
    return jsonify(alert_schema.dump(alert))


@alerts_bp.post("/scan")
@roles_required(UserRole.MANAGER, UserRole.REGULATOR)
def scan():
    scope = None if has_national_scope() else token_cooperative_id()
    created = scan_for_alerts(scope)
    return jsonify({"created": len(created), "alerts": alerts_schema.dump(created)}), 201


@alerts_bp.get("/stream")
@jwt_required()
def stream():
    """SSE : pousse les alertes non acquittées récentes (fallback : polling `/alerts`)."""
    coop_id = None if has_national_scope() else token_cooperative_id()

    @stream_with_context
    def _gen():
        last_seen = utcnow()
        for _ in range(600):  # ~10 min max par connexion
            q = (
                db.select(Alert)
                .join(Parcel, Alert.parcel_id == Parcel.id)
                .options(joinedload(Alert.parcel))
                .filter(Alert.created_at > last_seen)
                .order_by(Alert.created_at.asc())
            )
            if coop_id:
                q = q.filter(Parcel.cooperative_id == coop_id)
            for alert in db.session.scalars(q).all():
                last_seen = max(last_seen, alert.created_at)
                yield f"event: alert\ndata: {json.dumps(alert_schema.dump(alert))}\n\n"
            yield ": keep-alive\n\n"
            time.sleep(1)

    return Response(_gen(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})


def _get_or_404(alert_id) -> Alert:
    alert = db.session.get(Alert, alert_id)
    if alert is None:
        raise ApiError("Alerte introuvable.", status=404)
    return alert

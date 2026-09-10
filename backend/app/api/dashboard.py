from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload, selectinload

from app.api._helpers import resolve_cooperative_scope
from app.extensions import db
from app.geo import feature, feature_collection, parse_bbox
from app.models.enums import EudrStatus, RiskLevel
from app.models.parcel import Parcel

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

_BUCKETS = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 101)]


def _scope_query(cooperative_id: str | None):
    q = (
        db.select(Parcel)
        .filter(Parcel.deleted_at.is_(None))
        .options(selectinload(Parcel.scores), selectinload(Parcel.analyses), joinedload(Parcel.producer))
    )
    if cooperative_id is not None:
        q = q.filter(Parcel.cooperative_id == cooperative_id)
    return q


@dashboard_bp.get("/summary")
@jwt_required()
def summary():
    scope = resolve_cooperative_scope(request.args.get("cooperative_id"))
    parcels = db.session.scalars(_scope_query(scope)).unique().all()

    total = len(parcels)
    area_total = round(sum(float(p.area_ha or 0) for p in parcels), 2)
    status_counts: Counter = Counter()
    risk_counts: Counter = Counter()
    dist = [0] * len(_BUCKETS)
    assessed = 0
    deforestation_events = 0
    high_risk_area = 0.0

    for p in parcels:
        score = p.latest_score
        analysis = p.latest_analysis
        if analysis and analysis.deforestation_detected:
            deforestation_events += 1
        if score is None:
            status_counts["unassessed"] += 1
            continue
        assessed += 1
        status_counts[score.eudr_status.value] += 1
        risk_counts[score.risk_level.value] += 1
        if score.risk_level is RiskLevel.HIGH:
            high_risk_area += float(p.area_ha or 0)
        for i, (lo, hi) in enumerate(_BUCKETS):
            if lo <= score.score < hi:
                dist[i] += 1
                break

    return jsonify(
        {
            "cooperative_id": str(scope) if scope else None,
            "parcels_total": total,
            "area_ha_total": area_total,
            "assessed": assessed,
            "coverage_pct": round(assessed / total * 100, 1) if total else 0.0,
            "compliant": status_counts.get(EudrStatus.COMPLIANT.value, 0),
            "at_risk": status_counts.get(EudrStatus.AT_RISK.value, 0),
            "non_compliant": status_counts.get(EudrStatus.NON_COMPLIANT.value, 0),
            "unassessed": status_counts.get("unassessed", 0),
            "deforestation_events": deforestation_events,
            "high_risk_area_ha": round(high_risk_area, 2),
            "risk_distribution": {
                "low": risk_counts.get("low", 0),
                "medium": risk_counts.get("medium", 0),
                "high": risk_counts.get("high", 0),
            },
            "score_distribution": [
                {"range": f"{lo}-{hi if hi <= 100 else 100}", "count": dist[i]}
                for i, (lo, hi) in enumerate(_BUCKETS)
            ],
            "trend": _compliance_trend(parcels),
        }
    )


def _compliance_trend(parcels: list[Parcel], months: int = 6) -> list[dict]:
    by_month: dict[str, list[str]] = defaultdict(list)
    for p in parcels:
        for s in p.scores:
            key = s.computed_at.strftime("%Y-%m")
            by_month[key].append(s.eudr_status.value)
    keys = sorted(by_month)[-months:]
    out = []
    for k in keys:
        vals = by_month[k]
        compliant = sum(1 for v in vals if v == EudrStatus.COMPLIANT.value)
        out.append(
            {
                "month": k,
                "assessed": len(vals),
                "compliant_pct": round(compliant / len(vals) * 100, 1) if vals else 0.0,
            }
        )
    return out


@dashboard_bp.get("/map")
@jwt_required()
def map_view():
    scope = resolve_cooperative_scope(request.args.get("cooperative_id"))
    query = _scope_query(scope)
    bbox = parse_bbox(request.args.get("bbox"))
    parcels = db.session.scalars(query).unique().all()

    features = []
    for p in parcels:
        if bbox:
            from geoalchemy2.shape import to_shape

            minx, miny, maxx, maxy = bbox
            b = to_shape(p.geometry).bounds
            if b[2] < minx or b[0] > maxx or b[3] < miny or b[1] > maxy:
                continue
        score = p.latest_score
        analysis = p.latest_analysis
        features.append(
            feature(
                p.geometry,
                {
                    "id": str(p.id),
                    "code": p.code,
                    "producer": p.producer.full_name if p.producer else None,
                    "area_ha": p.area_ha,
                    "score": score.score if score else None,
                    "risk_level": score.risk_level.value if score else None,
                    "eudr_status": score.eudr_status.value if score else "unassessed",
                    "deforestation_detected": bool(analysis and analysis.deforestation_detected),
                    "protected_area_overlap_ha": analysis.protected_area_overlap_ha if analysis else None,
                },
                p.id,
            )
        )
    return jsonify(feature_collection(features))


@dashboard_bp.get("/regions")
def regions():
    """Agrégats nationaux par région — sans authentification (landing publique)."""
    parcels = db.session.scalars(
        db.select(Parcel)
        .filter(Parcel.deleted_at.is_(None))
        .options(selectinload(Parcel.scores), joinedload(Parcel.cooperative))
    ).unique().all()

    agg: dict[str, dict] = {}
    for p in parcels:
        region = (p.cooperative.region if p.cooperative else None) or "Non renseignée"
        row = agg.setdefault(
            region,
            {"region": region, "parcels": 0, "area_ha": 0.0, "compliant": 0, "at_risk": 0, "non_compliant": 0},
        )
        row["parcels"] += 1
        row["area_ha"] = round(row["area_ha"] + float(p.area_ha or 0), 2)
        score = p.latest_score
        if score:
            row[score.eudr_status.value] = row.get(score.eudr_status.value, 0) + 1

    return jsonify(
        {
            "generated_at": date.today().isoformat(),
            "regions": sorted(agg.values(), key=lambda r: -r["parcels"]),
        }
    )

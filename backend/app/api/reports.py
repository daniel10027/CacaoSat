from __future__ import annotations

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

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
from app.models.compliance_report import ComplianceReport
from app.models.enums import UserRole
from app.schemas.report import report_create_schema, report_schema, reports_schema
from app.security import roles_required
from app.services.report import generate_report
from app.storage import get_object

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.get("")
@jwt_required()
def list_reports():
    args = parse_pagination()
    query = db.select(ComplianceReport).order_by(ComplianceReport.generated_at.desc())
    if not has_national_scope():
        query = query.filter(ComplianceReport.cooperative_id == token_cooperative_id())
    elif cid := request.args.get("cooperative_id"):
        query = query.filter(ComplianceReport.cooperative_id == cid)
    return jsonify(run_paginated(query, args["page"], args["per_page"], reports_schema))


@reports_bp.get("/<uuid:report_id>")
@jwt_required()
def get_report(report_id):
    report = _get_or_404(report_id)
    assert_can_access_cooperative(report.cooperative_id)
    return jsonify(report_schema.dump(report))


@reports_bp.post("")
@roles_required(UserRole.MANAGER, UserRole.REGULATOR)
def create_report():
    data = report_create_schema.load(request.get_json(force=True, silent=True) or {})
    cooperative_id = data.get("cooperative_id")
    if not has_national_scope():
        cooperative_id = token_cooperative_id()
    if cooperative_id is None:
        raise ApiError("cooperative_id requis.", status=422)

    try:
        report = generate_report(
            cooperative_id=cooperative_id,
            period_start=data["period_start"],
            period_end=data["period_end"],
            parcel_ids=[str(p) for p in data["parcel_ids"]] if data.get("parcel_ids") else None,
            generated_by=get_jwt_identity(),
            title=data.get("title"),
        )
    except ValueError as exc:
        raise ApiError(str(exc), status=422) from exc

    audit("report.generate", "compliance_report", report.id, hash=report.content_hash)
    db.session.commit()
    return jsonify(report_schema.dump(report)), 201


@reports_bp.get("/<uuid:report_id>/download")
@jwt_required()
def download_report(report_id):
    report = _get_or_404(report_id)
    assert_can_access_cooperative(report.cooperative_id)
    fmt = request.args.get("format", "pdf")
    if fmt == "pdf":
        key, mime, name = report.pdf_key, "application/pdf", "rapport-conformite-eudr.pdf"
    elif fmt == "geojson":
        key, mime, name = report.geojson_key, "application/geo+json", "parcelles.geojson"
    else:
        raise ApiError("format doit être pdf ou geojson.", status=422)
    if not key:
        raise ApiError("Fichier non disponible.", status=404)
    try:
        data = get_object(key)
    except FileNotFoundError as exc:
        raise ApiError("Fichier introuvable dans le stockage.", status=404) from exc
    return Response(
        data,
        mimetype=mime,
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


def _get_or_404(report_id) -> ComplianceReport:
    report = db.session.get(ComplianceReport, report_id)
    if report is None:
        raise ApiError("Rapport introuvable.", status=404)
    return report

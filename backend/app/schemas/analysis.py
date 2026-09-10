from __future__ import annotations

from marshmallow import Schema, fields


class AnalysisRunSchema(Schema):
    id = fields.UUID(dump_only=True)
    parcel_id = fields.UUID(dump_only=True)
    provider_versions = fields.Dict(dump_only=True)
    forest_cover_2020_pct = fields.Float(dump_only=True, allow_none=True)
    forest_cover_current_pct = fields.Float(dump_only=True, allow_none=True)
    forest_loss_ha = fields.Float(dump_only=True)
    loss_events = fields.List(fields.Dict(), dump_only=True)
    ndvi_series = fields.List(fields.Dict(), dump_only=True)
    protected_area_overlap_ha = fields.Float(dump_only=True)
    deforestation_detected = fields.Boolean(dump_only=True)
    confidence = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class ComplianceScoreSchema(Schema):
    id = fields.UUID(dump_only=True)
    parcel_id = fields.UUID(dump_only=True)
    analysis_run_id = fields.UUID(dump_only=True)
    score = fields.Float(dump_only=True)
    risk_level = fields.String(dump_only=True)
    eudr_status = fields.String(dump_only=True)
    factors = fields.List(fields.Dict(), dump_only=True)
    computed_at = fields.DateTime(dump_only=True)


class AnalyzeResultSchema(Schema):
    analysis_run = fields.Nested(AnalysisRunSchema)
    compliance_score = fields.Nested(ComplianceScoreSchema)


analysis_run_schema = AnalysisRunSchema()
compliance_score_schema = ComplianceScoreSchema()
analyze_result_schema = AnalyzeResultSchema()

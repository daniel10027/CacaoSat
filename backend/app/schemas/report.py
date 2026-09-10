from __future__ import annotations

from datetime import date

from marshmallow import Schema, fields, validate


class ReportCreateSchema(Schema):
    cooperative_id = fields.UUID(required=False, allow_none=True)
    title = fields.String(allow_none=True, validate=validate.Length(max=200))
    period_start = fields.Date(load_default=lambda: date(date.today().year, 1, 1))
    period_end = fields.Date(load_default=date.today)
    parcel_ids = fields.List(fields.UUID(), load_default=None)


class ReportSchema(Schema):
    id = fields.UUID(dump_only=True)
    cooperative_id = fields.UUID(dump_only=True)
    title = fields.String(dump_only=True)
    period_start = fields.Date(dump_only=True)
    period_end = fields.Date(dump_only=True)
    parcel_ids = fields.List(fields.String(), dump_only=True)
    summary = fields.Dict(dump_only=True)
    content_hash = fields.String(dump_only=True)
    pdf_key = fields.String(dump_only=True)
    geojson_key = fields.String(dump_only=True)
    generated_by = fields.UUID(dump_only=True, allow_none=True)
    generated_at = fields.DateTime(dump_only=True)


report_create_schema = ReportCreateSchema()
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

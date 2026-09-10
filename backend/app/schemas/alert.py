from __future__ import annotations

from marshmallow import Schema, fields


class AlertSchema(Schema):
    id = fields.UUID(dump_only=True)
    parcel_id = fields.UUID(dump_only=True)
    parcel_code = fields.Function(lambda o: o.parcel.code if o.parcel else None, dump_only=True)
    cooperative_id = fields.Function(
        lambda o: str(o.parcel.cooperative_id) if o.parcel else None, dump_only=True
    )
    type = fields.String(dump_only=True)
    severity = fields.String(dump_only=True)
    detected_at = fields.DateTime(dump_only=True)
    area_ha = fields.Float(dump_only=True)
    message = fields.String(dump_only=True)
    acknowledged = fields.Boolean(dump_only=True)
    acknowledged_by = fields.UUID(dump_only=True, allow_none=True)
    acknowledged_at = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


alert_schema = AlertSchema()
alerts_schema = AlertSchema(many=True)

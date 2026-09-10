from __future__ import annotations

from marshmallow import Schema, fields, validate

from app.models.enums import Gender

_GENDERS = [g.value for g in Gender]


class ProducerSchema(Schema):
    id = fields.UUID(dump_only=True)
    # Fourni explicitement par un rôle national ; sinon dérivé du token.
    cooperative_id = fields.UUID(required=False, allow_none=True)
    external_ref = fields.String(allow_none=True, validate=validate.Length(max=64))
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=160))
    national_id = fields.String(allow_none=True, validate=validate.Length(max=64))
    gender = fields.String(load_default=Gender.UNKNOWN.value, validate=validate.OneOf(_GENDERS))
    village = fields.String(allow_none=True, validate=validate.Length(max=120))
    phone = fields.String(allow_none=True, validate=validate.Length(max=40))
    registered_at = fields.Date(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    parcels_count = fields.Method("_parcels_count", dump_only=True)

    def _parcels_count(self, obj) -> int:
        return len([p for p in getattr(obj, "parcels", []) if not p.is_deleted])


producer_schema = ProducerSchema()
producers_schema = ProducerSchema(many=True)
producer_update_schema = ProducerSchema(partial=True)

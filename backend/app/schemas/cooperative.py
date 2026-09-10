from __future__ import annotations

from marshmallow import Schema, fields, validate


class CooperativeSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=160))
    code = fields.String(required=True, validate=validate.Length(min=2, max=24))
    region = fields.String(allow_none=True, validate=validate.Length(max=80))
    department = fields.String(allow_none=True, validate=validate.Length(max=80))
    contact_name = fields.String(allow_none=True, validate=validate.Length(max=120))
    contact_phone = fields.String(allow_none=True, validate=validate.Length(max=40))
    contact_email = fields.Email(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class CooperativeUpdateSchema(CooperativeSchema):
    class Meta:
        pass

    name = fields.String(validate=validate.Length(min=2, max=160))
    code = fields.String(validate=validate.Length(min=2, max=24))


cooperative_schema = CooperativeSchema()
cooperatives_schema = CooperativeSchema(many=True)
cooperative_update_schema = CooperativeUpdateSchema(partial=True)

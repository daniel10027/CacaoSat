from __future__ import annotations

from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1, max=256), load_only=True)


class TokenSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String()
    token_type = fields.Constant("Bearer")
    expires_in = fields.Integer()


class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    email = fields.Email(dump_only=True)
    full_name = fields.String(dump_only=True)
    role = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    cooperative_id = fields.UUID(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


login_schema = LoginSchema()
token_schema = TokenSchema()
user_schema = UserSchema()

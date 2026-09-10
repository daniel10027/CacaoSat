from __future__ import annotations

from marshmallow import Schema, fields, validate

from app.models.enums import CollectionMethod, ParcelSource, ParcelStatus
from app.schemas.geo import PolygonGeoJSON

_METHODS = [m.value for m in CollectionMethod]
_SOURCES = [s.value for s in ParcelSource]
_STATUSES = [s.value for s in ParcelStatus]


class ScoreBriefSchema(Schema):
    score = fields.Float()
    risk_level = fields.String()
    eudr_status = fields.String()
    computed_at = fields.DateTime()


class AnalysisBriefSchema(Schema):
    id = fields.UUID()
    deforestation_detected = fields.Boolean()
    forest_loss_ha = fields.Float()
    forest_cover_2020_pct = fields.Float()
    forest_cover_current_pct = fields.Float()
    protected_area_overlap_ha = fields.Float()
    confidence = fields.Float()
    created_at = fields.DateTime()


class ParcelCreateSchema(Schema):
    code = fields.String(allow_none=True, validate=validate.Length(max=32))
    producer_id = fields.UUID(allow_none=True)
    cooperative_id = fields.UUID(allow_none=True)
    geometry = PolygonGeoJSON(required=True)
    planting_year = fields.Integer(allow_none=True, validate=validate.Range(min=1950, max=2100))
    crop = fields.String(load_default="cocoa", validate=validate.Length(max=40))
    gps_accuracy_m = fields.Float(allow_none=True, validate=validate.Range(min=0, max=500))
    collection_method = fields.String(
        load_default=CollectionMethod.MANUAL.value, validate=validate.OneOf(_METHODS)
    )
    collected_at = fields.DateTime(allow_none=True)
    source = fields.String(load_default=ParcelSource.WEB.value, validate=validate.OneOf(_SOURCES))


class ParcelUpdateSchema(Schema):
    producer_id = fields.UUID(allow_none=True)
    planting_year = fields.Integer(allow_none=True, validate=validate.Range(min=1950, max=2100))
    crop = fields.String(validate=validate.Length(max=40))
    gps_accuracy_m = fields.Float(allow_none=True, validate=validate.Range(min=0, max=500))
    status = fields.String(validate=validate.OneOf(_STATUSES))


class ParcelSchema(Schema):
    id = fields.UUID(dump_only=True)
    code = fields.String(dump_only=True)
    producer_id = fields.UUID(allow_none=True, dump_only=True)
    producer_name = fields.Function(
        lambda o: o.producer.full_name if o.producer else None, dump_only=True
    )
    cooperative_id = fields.UUID(dump_only=True)
    geometry = PolygonGeoJSON(dump_only=True)
    area_ha = fields.Float(dump_only=True)
    planting_year = fields.Integer(dump_only=True, allow_none=True)
    crop = fields.String(dump_only=True)
    gps_accuracy_m = fields.Float(dump_only=True, allow_none=True)
    collection_method = fields.String(dump_only=True)
    collected_at = fields.DateTime(dump_only=True, allow_none=True)
    source = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    latest_score = fields.Nested(ScoreBriefSchema, dump_only=True, allow_none=True)
    latest_analysis = fields.Nested(AnalysisBriefSchema, dump_only=True, allow_none=True)


parcel_schema = ParcelSchema()
parcels_schema = ParcelSchema(many=True)
parcel_create_schema = ParcelCreateSchema()
parcel_update_schema = ParcelUpdateSchema(partial=True)

from __future__ import annotations

from marshmallow import ValidationError, fields

from app.geo import geom_to_geojson, parse_polygon


class PolygonGeoJSON(fields.Field):
    """Champ GeoJSON Polygon/MultiPolygon validé (emprise CI, surface, validité).

    Accepte en sérialisation une géométrie shapely *ou* un ``WKBElement`` PostGIS.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return geom_to_geojson(value)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return parse_polygon(value)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(str(exc)) from exc

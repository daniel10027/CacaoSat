"""Utilitaires géospatiaux : validation GeoJSON, surface, centroïde, conversions."""

from __future__ import annotations

from typing import Any

from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.shape import to_shape
from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shapely_transform

from app.errors import ApiError

# Emprise approximative de la Côte d'Ivoire (lon_min, lat_min, lon_max, lat_max).
CI_BBOX = (-8.75, 4.20, -2.40, 10.85)

# 4326 -> UTM 30N (mètres), adapté à la Côte d'Ivoire pour le calcul de surface.
_TO_METRIC = Transformer.from_crs("EPSG:4326", "EPSG:32630", always_xy=True)


def parse_polygon(geojson_geometry: dict[str, Any]) -> BaseGeometry:
    if not isinstance(geojson_geometry, dict) or geojson_geometry.get("type") not in {
        "Polygon",
        "MultiPolygon",
    }:
        raise ApiError("Géométrie GeoJSON attendue de type Polygon/MultiPolygon.", status=422)
    try:
        geom = shape(geojson_geometry)
    except Exception as exc:  # noqa: BLE001
        raise ApiError(f"Géométrie illisible : {exc}", status=422) from exc
    validate_polygon(geom)
    return geom


def validate_polygon(geom: BaseGeometry) -> None:
    if geom.is_empty:
        raise ApiError("La parcelle est vide.", status=422)
    if not geom.is_valid:
        raise ApiError("Le polygone est invalide (auto-intersection ?).", status=422)
    if geom.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ApiError("Type de géométrie non supporté.", status=422)
    minx, miny, maxx, maxy = geom.bounds
    bminx, bminy, bmaxx, bmaxy = CI_BBOX
    if minx < bminx or miny < bminy or maxx > bmaxx or maxy > bmaxy:
        raise ApiError("Le polygone sort de l'emprise de la Côte d'Ivoire.", status=422)
    area = polygon_area_ha(geom)
    if area <= 0.0:
        raise ApiError("Surface de parcelle nulle.", status=422)
    if area > 5000.0:
        raise ApiError("Surface de parcelle irréaliste (> 5000 ha).", status=422)


def polygon_area_ha(geom: BaseGeometry) -> float:
    metric = shapely_transform(lambda x, y, z=None: _TO_METRIC.transform(x, y), geom)
    return round(metric.area / 10_000.0, 4)


def polygon_centroid(geom: BaseGeometry) -> tuple[float, float]:
    c = geom.centroid
    return (round(c.x, 7), round(c.y, 7))


def to_wkt_element(geom: BaseGeometry, srid: int = 4326) -> WKTElement:
    return WKTElement(geom.wkt, srid=srid)


def geom_to_geojson(value: WKBElement | BaseGeometry | None) -> dict | None:
    if value is None:
        return None
    geom = to_shape(value) if isinstance(value, WKBElement) else value
    return mapping(geom)


def feature(geometry: WKBElement | BaseGeometry | None, properties: dict, fid: Any = None) -> dict:
    f = {"type": "Feature", "geometry": geom_to_geojson(geometry), "properties": properties}
    if fid is not None:
        f["id"] = str(fid)
    return f


def feature_collection(features: list[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}


def parse_bbox(raw: str | None) -> tuple[float, float, float, float] | None:
    if not raw:
        return None
    try:
        parts = [float(p) for p in raw.split(",")]
    except ValueError as exc:
        raise ApiError("bbox attendu : minx,miny,maxx,maxy", status=422) from exc
    if len(parts) != 4:
        raise ApiError("bbox attendu : minx,miny,maxx,maxy", status=422)
    return (parts[0], parts[1], parts[2], parts[3])

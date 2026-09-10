"""Aires protégées / forêts classées de la zone pilote (mock, données embarquées).

Le calcul de recouvrement est *réellement géométrique* : c'est cette valeur qui
alimente le moteur de scoring EUDR (facteur « aire protégée »).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shapely_transform
from shapely.strtree import STRtree

from app.geo import _TO_METRIC

PROVIDER_VERSION = "protected-areas-mock/1.0 (SODEFOR/OIPR zone pilote Cavally, embarqué)"
_FIXTURE = Path(__file__).parent / "fixtures" / "protected_areas.geojson"


@lru_cache(maxsize=1)
def _load() -> tuple[list[BaseGeometry], list[dict], STRtree]:
    data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    geoms: list[BaseGeometry] = []
    props: list[dict] = []
    for feat in data["features"]:
        geoms.append(shape(feat["geometry"]))
        props.append(feat["properties"])
    return geoms, props, STRtree(geoms)


def _to_metric(geom: BaseGeometry) -> BaseGeometry:
    return shapely_transform(lambda x, y, z=None: _TO_METRIC.transform(x, y), geom)


def overlap_ha(geom: BaseGeometry) -> float:
    """Surface (ha) de la parcelle recouvrant une aire protégée."""
    geoms, _props, tree = _load()
    total_m2 = 0.0
    for idx in tree.query(geom):
        inter = geom.intersection(geoms[int(idx)])
        if not inter.is_empty:
            total_m2 += _to_metric(inter).area
    return round(total_m2 / 10_000.0, 4)


def intersecting(geom: BaseGeometry) -> list[dict]:
    """Propriétés des aires protégées recouvertes par la parcelle."""
    geoms, props, tree = _load()
    hits: list[dict] = []
    for idx in tree.query(geom):
        i = int(idx)
        if geom.intersects(geoms[i]):
            hits.append(props[i])
    return hits


def feature_collection() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def describe() -> dict:
    return {"provider": "protected_areas", "version": PROVIDER_VERSION, "mock": True}

"""Tests des mocks : déterminisme + cohérence des scénarios."""

from __future__ import annotations

import uuid

from shapely.geometry import Polygon

from app.mocks import digital_earth_africa as dea
from app.mocks import gfw_hansen, protected_areas, scenarios, sentinel2


def _poly(lon=-7.49, lat=6.54, d=0.0007):
    return Polygon([(lon - d, lat - d), (lon + d, lat - d), (lon + d, lat + d), (lon - d, lat + d), (lon - d, lat - d)])


def test_scenario_is_deterministic():
    pid = uuid.uuid4()
    assert scenarios.resolve(pid).name == scenarios.resolve(pid).name


def test_scenario_override():
    scenarios.SCENARIO_OVERRIDES["OVR-1"] = "deforested"
    try:
        assert scenarios.resolve(uuid.uuid4(), "OVR-1").name == "deforested"
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_ndvi_series_deterministic_and_bounded():
    pid = uuid.uuid4()
    sc = scenarios.resolve(pid)
    a = sentinel2.ndvi_series(pid, _poly(), sc)
    b = sentinel2.ndvi_series(pid, _poly(), sc)
    assert a == b
    assert len(a) >= 12
    assert all(0.0 <= p["ndvi"] <= 1.0 for p in a)


def test_deforested_scenario_drops_ndvi():
    pid = uuid.uuid4()
    scenarios.SCENARIO_OVERRIDES["DEF-1"] = "deforested"
    try:
        sc = scenarios.resolve(pid, "DEF-1")
        series = sentinel2.ndvi_series(pid, _poly(), sc)
        first_year = sum(p["ndvi"] for p in series[:12]) / 12
        last_year = sum(p["ndvi"] for p in series[-12:]) / 12
        assert last_year < first_year - 0.05
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_hansen_forest_loss_matches_scenario():
    pid = uuid.uuid4()
    scenarios.SCENARIO_OVERRIDES["C-1"] = "compliant"
    scenarios.SCENARIO_OVERRIDES["D-1"] = "deforested"
    try:
        clean = gfw_hansen.forest_stats(pid, _poly(), scenarios.resolve(pid, "C-1"))
        dirty = gfw_hansen.forest_stats(pid, _poly(), scenarios.resolve(pid, "D-1"))
        assert clean["forest_loss_ha_post_2020"] == 0.0
        assert dirty["forest_loss_ha_post_2020"] > 0.0
        assert all(e["year"] > 2020 for e in dirty["loss_events"])
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_protected_area_overlap_geometry():
    inside = _poly(lon=-7.470, lat=6.520, d=0.0006)  # dans la Forêt classée du Cavally
    outside = _poly(lon=-7.30, lat=6.90, d=0.0006)
    assert protected_areas.overlap_ha(inside) > 0
    assert protected_areas.overlap_ha(outside) == 0
    names = [a["name"] for a in protected_areas.intersecting(inside)]
    assert "Forêt classée du Cavally" in names


def test_dea_index_in_range():
    pid = uuid.uuid4()
    out = dea.degradation_index(pid, _poly(), scenarios.resolve(pid))
    assert 0.0 <= out["degradation_index"] <= 1.0
    assert out["class"] in {"stable", "moderate", "severe"}

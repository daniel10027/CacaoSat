"""Tests du moteur d'analyse (détection NDVI, perte de couvert, recouvrement)."""

from __future__ import annotations

from app.mocks import scenarios
from app.services.analysis import analyze_parcel, detect_ndvi_breaks, run_analysis
from tests.conftest import square_polygon


def _ndvi(values):
    return [{"date": f"2022-{i % 12 + 1:02d}-15", "ndvi": v} for i, v in enumerate(values)]


def test_detect_ndvi_break_on_sharp_drop():
    series = _ndvi([0.8] * 8 + [0.4] * 8)
    breaks = detect_ndvi_breaks(series)
    assert breaks and breaks[0]["ndvi_drop"] >= 0.3


def test_no_break_on_stable_series():
    assert detect_ndvi_breaks(_ndvi([0.8, 0.79, 0.81, 0.8] * 4)) == []


def test_run_analysis_compliant_scenario(make_parcel):
    scenarios.SCENARIO_OVERRIDES["AN-C"] = "compliant"
    try:
        parcel = make_parcel(code="AN-C")
        run, ctx = run_analysis(parcel)
        assert run.forest_loss_ha == 0.0
        assert run.deforestation_detected is False
        assert len(run.ndvi_series) >= 12
        assert ctx["scenario"] == "compliant"
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_run_analysis_deforested_scenario(make_parcel):
    scenarios.SCENARIO_OVERRIDES["AN-D"] = "deforested"
    try:
        parcel = make_parcel(code="AN-D")
        run, _ = run_analysis(parcel)
        assert run.forest_loss_ha > 0
        assert run.deforestation_detected is True
        assert run.provider_versions["scenario"] == "deforested"
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_analysis_detects_protected_area_overlap(make_parcel):
    # Polygone dans la Forêt classée du Cavally
    parcel = make_parcel(polygon=square_polygon(lon=-7.470, lat=6.520, edge_deg=0.0008), code="AN-P")
    run, _ = run_analysis(parcel)
    assert run.protected_area_overlap_ha > 0


def test_analyze_parcel_persists_run_and_score(make_parcel, db):
    parcel = make_parcel()
    run, score = analyze_parcel(parcel.id)
    assert run.id is not None
    assert score.analysis_run_id == run.id
    db.session.refresh(parcel)
    assert parcel.latest_score is not None
    assert parcel.latest_analysis.id == run.id


def test_analyze_many_reports_failures(make_parcel):
    from app.services.analysis import analyze_many

    p1 = make_parcel()
    import uuid

    result = analyze_many([p1.id, uuid.uuid4()])
    assert result["analyzed"] == 1
    assert len(result["failed"]) == 1

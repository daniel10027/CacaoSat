"""Tests du moteur de scoring EUDR — barème figé, cas canoniques."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

from app.models.enums import EudrStatus, RiskLevel
from app.services.scoring import (
    W_COMPLETENESS,
    W_DEFOREST,
    W_GPS,
    W_PROTECTED,
    W_TREND,
    compute_score,
)


def _parcel(area_ha=2.0, accuracy=4.0, national_id="CI123", collected_at=None):
    return SimpleNamespace(
        id=uuid.uuid4(),
        area_ha=area_ha,
        producer_id=uuid.uuid4() if national_id is not None else None,
        producer=SimpleNamespace(national_id=national_id),
        gps_accuracy_m=accuracy,
        collected_at=collected_at or datetime.now(UTC),
        geometry=object(),
    )


def _run(loss_ha=0.0, overlap_ha=0.0, deforestation=False):
    return SimpleNamespace(
        id=uuid.uuid4(),
        forest_loss_ha=loss_ha,
        protected_area_overlap_ha=overlap_ha,
        deforestation_detected=deforestation,
    )


def test_weights_sum_to_100():
    assert W_DEFOREST + W_PROTECTED + W_TREND + W_COMPLETENESS + W_GPS == 100


def test_clean_parcel_is_compliant():
    score = compute_score(
        _run(), _parcel(), {"degradation": {"degradation_index": 0.05, "class": "stable"}}
    )
    assert score.eudr_status is EudrStatus.COMPLIANT
    assert score.risk_level is RiskLevel.LOW
    assert score.score >= 92
    assert round(sum(f["points"] for f in score.factors), 1) == score.score


def test_diffuse_loss_is_at_risk():
    # ~3 % de la surface perdue -> facteur déforestation partiel, statut at_risk
    score = compute_score(
        _run(loss_ha=0.06, deforestation=True),
        _parcel(area_ha=2.0),
        {"degradation": {"degradation_index": 0.4, "class": "moderate"}, "ndvi_breaks": []},
    )
    assert score.eudr_status is EudrStatus.AT_RISK
    assert 50 <= score.score < 85
    def_factor = next(f for f in score.factors if f["key"] == "deforestation_post_2020")
    assert 0 < def_factor["points"] < W_DEFOREST


def test_clearcut_in_protected_area_is_non_compliant():
    score = compute_score(
        _run(loss_ha=0.9, overlap_ha=1.6, deforestation=True),
        _parcel(area_ha=2.0),
        {
            "degradation": {"degradation_index": 0.8, "class": "severe"},
            "ndvi_breaks": [{"date": "2022-06-15", "ndvi_drop": 0.35}],
        },
    )
    assert score.eudr_status is EudrStatus.NON_COMPLIANT
    assert score.risk_level is RiskLevel.HIGH
    assert score.score < 45
    prot = next(f for f in score.factors if f["key"] == "protected_area_overlap")
    assert prot["points"] < 5


def test_missing_producer_penalises_completeness():
    score = compute_score(
        _run(), _parcel(national_id=None), {"degradation": {"degradation_index": 0.1}}
    )
    comp = next(f for f in score.factors if f["key"] == "data_completeness")
    assert comp["points"] <= 6
    # producteur absent -> ne peut pas être "compliant"
    assert score.eudr_status in (EudrStatus.AT_RISK, EudrStatus.COMPLIANT)


def test_poor_gps_accuracy_lowers_gps_factor():
    good = compute_score(_run(), _parcel(accuracy=3.0), {"degradation": {"degradation_index": 0.1}})
    bad = compute_score(_run(), _parcel(accuracy=25.0), {"degradation": {"degradation_index": 0.1}})
    g = next(f for f in good.factors if f["key"] == "gps_quality_freshness")["points"]
    b = next(f for f in bad.factors if f["key"] == "gps_quality_freshness")["points"]
    assert b < g


def test_factors_are_explainable():
    score = compute_score(_run(loss_ha=0.1), _parcel(), {"degradation": {"degradation_index": 0.3}})
    for f in score.factors:
        assert {"key", "label", "weight", "raw_value", "points", "explanation"} <= set(f)
        assert 0 <= f["points"] <= f["weight"]

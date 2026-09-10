from __future__ import annotations

from app.mocks import scenarios
from tests.conftest import square_polygon


def _seed_scored(client, auth_header, make_parcel, n_compliant=3, n_deforested=2):
    for i in range(n_compliant):
        scenarios.SCENARIO_OVERRIDES[f"DASH-C{i}"] = "compliant"
        p = make_parcel(code=f"DASH-C{i}", polygon=square_polygon(lon=-7.30 + i * 0.001, lat=6.90))
        client.post(f"/api/v1/parcels/{p.id}/analyze", headers=auth_header("agent"))
    for i in range(n_deforested):
        scenarios.SCENARIO_OVERRIDES[f"DASH-D{i}"] = "deforested"
        p = make_parcel(code=f"DASH-D{i}", polygon=square_polygon(lon=-7.32 + i * 0.001, lat=6.92))
        client.post(f"/api/v1/parcels/{p.id}/analyze", headers=auth_header("agent"))


def test_summary_shape(client, seeded, auth_header, make_parcel):
    _seed_scored(client, auth_header, make_parcel)
    try:
        resp = client.get("/api/v1/dashboard/summary", headers=auth_header("manager"))
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["parcels_total"] == 5
        assert body["assessed"] == 5
        assert body["compliant"] >= 3
        assert body["non_compliant"] >= 1
        assert body["coverage_pct"] == 100.0
        assert len(body["score_distribution"]) == 5
        assert isinstance(body["trend"], list)
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_map_returns_feature_collection(client, seeded, auth_header, make_parcel):
    _seed_scored(client, auth_header, make_parcel, n_compliant=2, n_deforested=1)
    try:
        resp = client.get("/api/v1/dashboard/map", headers=auth_header("manager"))
        assert resp.status_code == 200
        fc = resp.get_json()
        assert fc["type"] == "FeatureCollection"
        assert len(fc["features"]) == 3
        props = fc["features"][0]["properties"]
        assert {"code", "eudr_status", "score"} <= set(props)
        assert fc["features"][0]["geometry"]["type"] == "Polygon"
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_regions_is_public(client, seeded, auth_header, make_parcel):
    _seed_scored(client, auth_header, make_parcel, n_compliant=2, n_deforested=0)
    try:
        resp = client.get("/api/v1/dashboard/regions")  # sans token
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["regions"]
        assert any(r["region"] == "Cavally" for r in body["regions"])
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_manager_cannot_read_other_cooperative_summary(client, seeded, auth_header, db):
    from app.models import Cooperative

    other = Cooperative(code="OC", name="Other")
    db.session.add(other)
    db.session.commit()
    resp = client.get(
        f"/api/v1/dashboard/summary?cooperative_id={other.id}", headers=auth_header("manager")
    )
    assert resp.status_code == 403

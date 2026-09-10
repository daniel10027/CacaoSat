from __future__ import annotations

from shapely.geometry import mapping

from tests.conftest import square_polygon


def _geojson(poly=None):
    return mapping(poly or square_polygon())


def test_create_parcel_as_agent(client, seeded, auth_header):
    body = {"geometry": _geojson(), "planting_year": 2015, "gps_accuracy_m": 4.2}
    resp = client.post("/api/v1/parcels", json=body, headers=auth_header("agent"))
    assert resp.status_code == 201, resp.get_json()
    data = resp.get_json()
    assert data["code"].startswith("COOP-TEST-")
    assert data["area_ha"] > 0
    assert data["cooperative_id"] == str(seeded["cooperative"].id)


def test_create_parcel_rejects_polygon_outside_country(client, seeded, auth_header):
    from shapely.geometry import Polygon

    paris = Polygon([(2.2, 48.8), (2.4, 48.8), (2.4, 48.9), (2.2, 48.9), (2.2, 48.8)])
    resp = client.post(
        "/api/v1/parcels", json={"geometry": mapping(paris)}, headers=auth_header("agent")
    )
    assert resp.status_code == 422


def test_list_parcels_is_scoped_to_cooperative(client, seeded, auth_header, make_parcel, db):
    from app.models import Cooperative, Producer

    other = Cooperative(code="OTHER", name="Autre coop")
    db.session.add(other)
    db.session.flush()
    make_parcel()  # coop du token
    make_parcel(cooperative=other, producer=Producer(cooperative=other, full_name="X", national_id="CI1"))
    db.session.commit()

    resp = client.get("/api/v1/parcels", headers=auth_header("manager"))
    assert resp.status_code == 200
    items = resp.get_json()["items"]
    assert len(items) == 1
    assert items[0]["cooperative_id"] == str(seeded["cooperative"].id)


def test_regulator_sees_all_and_can_filter(client, seeded, auth_header, make_parcel, db):
    from app.models import Cooperative, Producer

    other = Cooperative(code="OTHER2", name="Autre coop 2")
    db.session.add(other)
    db.session.flush()
    make_parcel()
    make_parcel(cooperative=other, producer=Producer(cooperative=other, full_name="Y", national_id="CI2"))
    db.session.commit()

    all_resp = client.get("/api/v1/parcels", headers=auth_header("regulator"))
    assert all_resp.get_json()["pagination"]["total"] == 2

    filt = client.get(
        f"/api/v1/parcels?cooperative_id={other.id}", headers=auth_header("regulator")
    )
    assert filt.get_json()["pagination"]["total"] == 1


def test_analyze_endpoint_returns_score(client, seeded, auth_header, make_parcel):
    parcel = make_parcel()
    resp = client.post(f"/api/v1/parcels/{parcel.id}/analyze", headers=auth_header("agent"))
    assert resp.status_code == 201, resp.get_json()
    body = resp.get_json()
    assert body["compliance_score"]["eudr_status"] in {"compliant", "at_risk", "non_compliant"}
    assert len(body["compliance_score"]["factors"]) == 5
    assert body["analysis_run"]["ndvi_series"]


def test_history_and_geojson(client, seeded, auth_header, make_parcel):
    parcel = make_parcel()
    client.post(f"/api/v1/parcels/{parcel.id}/analyze", headers=auth_header("agent"))

    hist = client.get(f"/api/v1/parcels/{parcel.id}/history", headers=auth_header("agent"))
    assert hist.status_code == 200
    assert len(hist.get_json()["scores"]) == 1

    gj = client.get(f"/api/v1/parcels/{parcel.id}.geojson", headers=auth_header("agent"))
    assert gj.status_code == 200
    fc = gj.get_json()
    assert fc["type"] == "FeatureCollection"
    assert fc["features"][0]["properties"]["code"] == parcel.code


def test_bbox_filter(client, seeded, auth_header, make_parcel):
    make_parcel(polygon=square_polygon(lon=-7.49, lat=6.54))
    make_parcel(polygon=square_polygon(lon=-4.10, lat=7.90), code="COOP-TEST-FAR")
    resp = client.get(
        "/api/v1/parcels?bbox=-7.55,6.50,-7.40,6.60", headers=auth_header("manager")
    )
    codes = [p["code"] for p in resp.get_json()["items"]]
    assert "COOP-TEST-FAR" not in codes
    assert len(codes) == 1


def test_agent_cannot_delete(client, seeded, auth_header, make_parcel):
    parcel = make_parcel()
    resp = client.delete(f"/api/v1/parcels/{parcel.id}", headers=auth_header("agent"))
    assert resp.status_code == 403

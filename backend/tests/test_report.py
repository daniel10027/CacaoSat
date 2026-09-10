from __future__ import annotations

import json
from datetime import date

from app.mocks import scenarios
from app.services.report import generate_report
from app.storage import get_object
from tests.conftest import square_polygon


def _prepare(client, auth_header, make_parcel, n=3):
    parcels = []
    for i in range(n):
        scenarios.SCENARIO_OVERRIDES[f"REP-{i}"] = "compliant" if i else "deforested"
        p = make_parcel(code=f"REP-{i}", polygon=square_polygon(lon=-7.30 + i * 0.001, lat=6.90))
        client.post(f"/api/v1/parcels/{p.id}/analyze", headers=auth_header("agent"))
        parcels.append(p)
    return parcels


def test_generate_report_produces_pdf_and_geojson(client, seeded, auth_header, make_parcel, db):
    _prepare(client, auth_header, make_parcel)
    try:
        report = generate_report(
            cooperative_id=seeded["cooperative"].id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 9, 30),
        )
        assert report.content_hash and len(report.content_hash) == 64
        pdf = get_object(report.pdf_key)
        assert pdf[:5] == b"%PDF-"
        gj = json.loads(get_object(report.geojson_key))
        assert gj["type"] == "FeatureCollection"
        assert len(gj["features"]) == 3
        props = gj["features"][0]["properties"]
        assert {"PlotId", "ProducerName", "Area", "eudr_status"} <= set(props)
        assert report.summary["parcels_total"] == 3
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_content_hash_is_stable(client, seeded, auth_header, make_parcel):
    _prepare(client, auth_header, make_parcel, n=2)
    try:
        a = generate_report(cooperative_id=seeded["cooperative"].id,
                            period_start=date(2026, 1, 1), period_end=date(2026, 9, 30))
        b = generate_report(cooperative_id=seeded["cooperative"].id,
                            period_start=date(2026, 1, 1), period_end=date(2026, 9, 30))
        assert a.content_hash == b.content_hash
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_report_endpoints(client, seeded, auth_header, make_parcel):
    _prepare(client, auth_header, make_parcel, n=2)
    try:
        resp = client.post(
            "/api/v1/reports",
            json={"period_start": "2026-01-01", "period_end": "2026-09-30"},
            headers=auth_header("manager"),
        )
        assert resp.status_code == 201, resp.get_json()
        rid = resp.get_json()["id"]

        listing = client.get("/api/v1/reports", headers=auth_header("manager")).get_json()
        assert listing["pagination"]["total"] == 1

        dl = client.get(f"/api/v1/reports/{rid}/download?format=pdf", headers=auth_header("manager"))
        assert dl.status_code == 200
        assert dl.data[:5] == b"%PDF-"
        assert "attachment" in dl.headers["Content-Disposition"]

        gj = client.get(f"/api/v1/reports/{rid}/download?format=geojson", headers=auth_header("manager"))
        assert gj.status_code == 200
        assert json.loads(gj.data)["type"] == "FeatureCollection"
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_agent_cannot_generate_report(client, seeded, auth_header, make_parcel):
    make_parcel()
    resp = client.post(
        "/api/v1/reports",
        json={"period_start": "2026-01-01", "period_end": "2026-09-30"},
        headers=auth_header("agent"),
    )
    assert resp.status_code == 403

from __future__ import annotations

from shapely.geometry import mapping

from tests.conftest import square_polygon


def test_bootstrap_returns_reference_data(client, seeded, auth_header, make_parcel):
    make_parcel()
    resp = client.get("/api/v1/sync/bootstrap", headers=auth_header("agent"))
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["schema_version"] == 1
    assert body["cooperative"]["code"] == "COOP-TEST"
    assert len(body["parcels"]) == 1
    assert body["protected_areas"]["type"] == "FeatureCollection"
    assert len(body["scoring"]["factors"]) == 5


def _batch(producer_cid="p1", parcel_cid="par1", batch_id="b1"):
    return {
        "device_id": "device-xyz",
        "client_batch_id": batch_id,
        "items": [
            {
                "op": "create",
                "entity": "producer",
                "client_id": producer_cid,
                "data": {"full_name": "Yao N'Guessan", "national_id": "CI55555", "village": "Ponan"},
            },
            {
                "op": "create",
                "entity": "parcel",
                "client_id": parcel_cid,
                "data": {
                    "geometry": mapping(square_polygon(lon=-7.48, lat=6.55)),
                    "producer_client_id": producer_cid,
                    "gps_accuracy_m": 4.5,
                    "collection_method": "walk",
                    "collected_at": "2026-09-01T09:00:00Z",
                },
            },
        ],
    }


def test_ingest_batch_creates_and_maps_ids(client, seeded, auth_header, db):
    resp = client.post("/api/v1/sync/batch", json=_batch(), headers=auth_header("agent"))
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["accepted"] == 2
    assert body["rejected"] == 0
    assert set(body["id_map"]) == {"p1", "par1"}

    from app.models import Parcel, Producer

    producer = db.session.get(Producer, body["id_map"]["p1"])
    parcel = db.session.get(Parcel, body["id_map"]["par1"])
    assert producer.full_name == "Yao N'Guessan"
    assert str(parcel.producer_id) == body["id_map"]["p1"]
    assert parcel.source.value == "mobile"
    assert parcel.area_ha > 0


def test_ingest_batch_is_idempotent(client, seeded, auth_header, db):
    first = client.post("/api/v1/sync/batch", json=_batch(batch_id="dup"), headers=auth_header("agent"))
    second = client.post("/api/v1/sync/batch", json=_batch(batch_id="dup"), headers=auth_header("agent"))
    assert first.get_json()["id_map"] == second.get_json()["id_map"]
    assert second.get_json()["replayed"] is True

    from app.models import Producer

    count = db.session.scalar(db.select(db.func.count()).select_from(Producer))
    assert count == 1  # pas de doublon


def test_batch_triggers_analysis_and_status(client, seeded, auth_header):
    resp = client.post("/api/v1/sync/batch", json=_batch(batch_id="b-an"), headers=auth_header("agent"))
    batch_id = resp.get_json()["batch_id"]
    status = client.get(f"/api/v1/sync/status/{batch_id}", headers=auth_header("agent")).get_json()
    assert status["status"] == "done"
    assert len(status["parcels"]) == 1
    assert status["parcels"][0]["analyzed"] is True


def test_batch_reports_item_errors(client, seeded, auth_header):
    payload = {
        "device_id": "d2",
        "client_batch_id": "bad",
        "items": [
            {"op": "create", "entity": "parcel", "client_id": "x", "data": {}},  # géométrie manquante
        ],
    }
    resp = client.post("/api/v1/sync/batch", json=payload, headers=auth_header("agent"))
    assert resp.status_code == 422
    body = resp.get_json()
    assert body["rejected"] == 1
    assert body["errors"][0]["entity"] == "parcel"

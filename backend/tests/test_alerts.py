from __future__ import annotations

from app.mocks import scenarios
from app.mocks.notifications import EMAIL_LOG, reset_logs
from app.models import AnalysisRun
from app.services.alerts import scan_for_alerts


def test_scan_creates_deforestation_alert_on_delta(make_parcel, db, seeded):
    reset_logs()
    scenarios.SCENARIO_OVERRIDES["ALERT-1"] = "compliant"
    try:
        parcel = make_parcel(code="ALERT-1")
        # analyse 1 : propre
        db.session.add(AnalysisRun(parcel_id=parcel.id, forest_loss_ha=0.0, ndvi_series=[], loss_events=[]))
        db.session.commit()
        assert scan_for_alerts(seeded["cooperative"].id) == []

        # analyse 2 : perte nette
        db.session.add(AnalysisRun(parcel_id=parcel.id, forest_loss_ha=0.4, deforestation_detected=True,
                                   ndvi_series=[], loss_events=[]))
        db.session.commit()
        created = scan_for_alerts(seeded["cooperative"].id)
        assert len(created) == 1
        assert created[0].type.value == "new_deforestation"
        assert EMAIL_LOG  # manager notifié (mock)
    finally:
        scenarios.SCENARIO_OVERRIDES.clear()


def test_scan_is_idempotent_while_unacknowledged(make_parcel, db, seeded):
    parcel = make_parcel(code="ALERT-2")
    db.session.add(AnalysisRun(parcel_id=parcel.id, forest_loss_ha=0.0, ndvi_series=[], loss_events=[]))
    db.session.add(AnalysisRun(parcel_id=parcel.id, forest_loss_ha=0.5, deforestation_detected=True,
                               ndvi_series=[], loss_events=[]))
    db.session.commit()
    assert len(scan_for_alerts(seeded["cooperative"].id)) == 1
    assert scan_for_alerts(seeded["cooperative"].id) == []  # pas de doublon


def test_data_gap_alert_for_producerless_parcel(make_parcel, db, seeded):
    parcel = make_parcel(code="ALERT-3")
    parcel.producer_id = None
    db.session.commit()
    created = scan_for_alerts(seeded["cooperative"].id)
    assert any(a.type.value == "data_gap" for a in created)


def test_alert_api_list_and_acknowledge(client, seeded, auth_header, make_parcel, db):
    parcel = make_parcel(code="ALERT-4")
    db.session.add(AnalysisRun(parcel_id=parcel.id, forest_loss_ha=0.0, ndvi_series=[], loss_events=[]))
    db.session.add(AnalysisRun(parcel_id=parcel.id, forest_loss_ha=0.6, deforestation_detected=True,
                               ndvi_series=[], loss_events=[]))
    db.session.commit()
    scan_for_alerts(seeded["cooperative"].id)

    listing = client.get("/api/v1/alerts", headers=auth_header("manager")).get_json()
    assert listing["pagination"]["total"] >= 1
    alert_id = listing["items"][0]["id"]

    ack = client.post(f"/api/v1/alerts/{alert_id}/acknowledge", headers=auth_header("manager"))
    assert ack.status_code == 200
    assert ack.get_json()["acknowledged"] is True

    only_ack = client.get("/api/v1/alerts?acknowledged=true", headers=auth_header("manager")).get_json()
    assert all(a["acknowledged"] for a in only_ack["items"])


def test_alerts_scoped_by_cooperative(client, seeded, auth_header, make_parcel, db):
    from app.models import Cooperative, Producer

    other = Cooperative(code="OC-AL", name="Autre")
    db.session.add(other)
    db.session.flush()
    p = make_parcel(cooperative=other,
                    producer=Producer(cooperative=other, full_name="Z", national_id="CIZ"),
                    code="OC-AL-1")
    db.session.add(AnalysisRun(parcel_id=p.id, forest_loss_ha=0.0, ndvi_series=[], loss_events=[]))
    db.session.add(AnalysisRun(parcel_id=p.id, forest_loss_ha=0.7, deforestation_detected=True,
                               ndvi_series=[], loss_events=[]))
    db.session.commit()
    scan_for_alerts()

    mgr_view = client.get("/api/v1/alerts", headers=auth_header("manager")).get_json()
    assert all(a["parcel_code"] != "OC-AL-1" for a in mgr_view["items"])

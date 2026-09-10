from __future__ import annotations


def test_agent_lists_only_own_cooperative(client, seeded, auth_header, db):
    from app.models import Cooperative

    db.session.add(Cooperative(code="C2", name="Coop 2"))
    db.session.commit()
    resp = client.get("/api/v1/cooperatives", headers=auth_header("agent"))
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body) == 1
    assert body[0]["code"] == "COOP-TEST"


def test_regulator_lists_all(client, seeded, auth_header, db):
    from app.models import Cooperative

    db.session.add(Cooperative(code="C3", name="Coop 3"))
    db.session.commit()
    resp = client.get("/api/v1/cooperatives", headers=auth_header("regulator"))
    assert len(resp.get_json()) == 2


def test_regulator_can_create_cooperative(client, seeded, auth_header):
    resp = client.post(
        "/api/v1/cooperatives",
        json={"name": "Nouvelle Coop", "code": "NEW-COOP", "region": "Nawa"},
        headers=auth_header("regulator"),
    )
    assert resp.status_code == 201
    assert resp.get_json()["code"] == "NEW-COOP"


def test_agent_cannot_create_cooperative(client, seeded, auth_header):
    resp = client.post(
        "/api/v1/cooperatives",
        json={"name": "X", "code": "X"},
        headers=auth_header("agent"),
    )
    assert resp.status_code == 403


def test_duplicate_code_conflict(client, seeded, auth_header):
    payload = {"name": "Dup", "code": "DUP"}
    client.post("/api/v1/cooperatives", json=payload, headers=auth_header("admin"))
    resp = client.post("/api/v1/cooperatives", json=payload, headers=auth_header("admin"))
    assert resp.status_code == 409

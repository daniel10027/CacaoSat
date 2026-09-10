from __future__ import annotations


def test_create_and_scope_producer(client, seeded, auth_header):
    resp = client.post(
        "/api/v1/producers",
        json={"full_name": "Kouamé Yao", "national_id": "CI1234567890", "village": "Zéaglo"},
        headers=auth_header("agent"),
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["cooperative_id"] == str(seeded["cooperative"].id)
    assert body["full_name"] == "Kouamé Yao"


def test_list_search_and_pagination(client, seeded, auth_header, db):
    from app.models import Producer

    for i in range(30):
        db.session.add(
            Producer(cooperative=seeded["cooperative"], full_name=f"Producteur {i:02d}", national_id=f"CI{i}")
        )
    db.session.add(
        Producer(cooperative=seeded["cooperative"], full_name="Aya Special", national_id="CIX", village="Ponan")
    )
    db.session.commit()

    page1 = client.get("/api/v1/producers?per_page=10", headers=auth_header("agent")).get_json()
    assert len(page1["items"]) == 10
    assert page1["pagination"]["total"] == 31
    assert page1["pagination"]["pages"] == 4

    found = client.get("/api/v1/producers?q=Special", headers=auth_header("agent")).get_json()
    assert found["pagination"]["total"] == 1
    assert found["items"][0]["full_name"] == "Aya Special"


def test_manager_cannot_read_other_coop_producer(client, seeded, auth_header, db):
    from app.models import Cooperative, Producer

    other = Cooperative(code="OC3", name="Other 3")
    p = Producer(cooperative=other, full_name="Etranger", national_id="CIZ")
    db.session.add_all([other, p])
    db.session.commit()

    resp = client.get(f"/api/v1/producers/{p.id}", headers=auth_header("manager"))
    assert resp.status_code == 403


def test_soft_delete_hides_producer(client, seeded, auth_header, db):
    from app.models import Producer

    p = Producer(cooperative=seeded["cooperative"], full_name="A supprimer", national_id="CID")
    db.session.add(p)
    db.session.commit()

    assert client.delete(f"/api/v1/producers/{p.id}", headers=auth_header("manager")).status_code == 204
    assert client.get(f"/api/v1/producers/{p.id}", headers=auth_header("manager")).status_code == 404
    listing = client.get("/api/v1/producers", headers=auth_header("manager")).get_json()
    assert all(item["full_name"] != "A supprimer" for item in listing["items"])

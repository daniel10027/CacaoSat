def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "CacaoSat API"


def test_health_live(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_health_ready(client, db):
    resp = client.get("/api/v1/health/ready")
    assert resp.status_code in (200, 503)
    assert resp.get_json()["checks"]["database"] == "ok"


def test_metrics_text(client, db):
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 200
    assert "cacaosat_parcels_total" in resp.get_data(as_text=True)


def test_openapi(client):
    resp = client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    assert resp.get_json()["info"]["title"] == "CacaoSat API"

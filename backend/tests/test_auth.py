def test_login_success(client, seeded):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "agent@test.ci", "password": "secret123"}
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["token_type"] == "Bearer"
    assert body["access_token"] and body["refresh_token"]
    assert body["expires_in"] > 0


def test_login_bad_password(client, seeded):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "agent@test.ci", "password": "nope"}
    )
    assert resp.status_code == 401
    assert resp.get_json()["error"]["code"] == "unauthorized"


def test_login_validation_error(client, db):
    resp = client.post("/api/v1/auth/login", json={"email": "not-an-email"})
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "validation_error"


def test_me_requires_token(client, db):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_profile(client, seeded, auth_header):
    resp = client.get("/api/v1/auth/me", headers=auth_header("manager"))
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["email"] == "manager@test.ci"
    assert body["role"] == "manager"
    assert body["cooperative_id"] == str(seeded["cooperative"].id)


def test_refresh_flow(client, seeded):
    login = client.post(
        "/api/v1/auth/login", json={"email": "admin@test.ci", "password": "secret123"}
    ).get_json()
    resp = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {login['refresh_token']}"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["access_token"]


def test_password_is_argon2(seeded):
    assert seeded["users"]["agent"].password_hash.startswith("$argon2")

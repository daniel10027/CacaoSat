"""Fixtures de test — base PostGIS auto-amorcée."""

from __future__ import annotations

import os

import psycopg
import pytest
from sqlalchemy.engine import make_url

from app import create_app
from app.extensions import db as _db
from app.models import Cooperative, User
from app.models.enums import UserRole

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://cacaosat:cacaosat@localhost:5432/cacaosat_test",
)


def _pg_dsn(url, dbname: str) -> str:
    u = make_url(url).set(drivername="postgresql", database=dbname)
    return u.render_as_string(hide_password=False)


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_database():
    """Crée la base de test + l'extension PostGIS si nécessaire."""
    url = make_url(TEST_DB_URL)
    admin_dsn = _pg_dsn(url, "postgres")
    try:
        with psycopg.connect(admin_dsn, autocommit=True) as conn:
            exists = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (url.database,)
            ).fetchone()
            if not exists:
                conn.execute(f'CREATE DATABASE "{url.database}"')
    except psycopg.OperationalError as exc:  # pragma: no cover
        pytest.skip(f"PostgreSQL/PostGIS indisponible pour les tests : {exc}")

    with psycopg.connect(_pg_dsn(url, url.database), autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    yield


@pytest.fixture(scope="session")
def app():
    os.environ["TEST_DATABASE_URL"] = TEST_DB_URL
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db(app):
    yield _db
    _db.session.rollback()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded(db):
    """Une coopérative + un jeu d'utilisateurs par rôle."""
    coop = Cooperative(code="COOP-TEST", name="Coopérative Test", region="Cavally")
    db.session.add(coop)
    db.session.flush()

    users: dict[str, User] = {}
    matrix = [
        ("admin", "admin@test.ci", UserRole.ADMIN, None),
        ("regulator", "reg@test.ci", UserRole.REGULATOR, None),
        ("manager", "manager@test.ci", UserRole.MANAGER, coop),
        ("agent", "agent@test.ci", UserRole.AGENT, coop),
    ]
    for key, email, role, c in matrix:
        u = User(email=email, full_name=key.title(), role=role, cooperative=c)
        u.set_password("secret123")
        db.session.add(u)
        users[key] = u
    db.session.commit()
    return {"cooperative": coop, "users": users}


@pytest.fixture()
def auth_header(client, seeded):
    def _make(role: str = "agent") -> dict:
        email = seeded["users"][role].email
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
        assert resp.status_code == 200, resp.get_json()
        return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}

    return _make

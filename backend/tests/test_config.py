import pytest

from app import create_app
from app.config import ProdConfig, get_config


def test_config_map():
    assert get_config("testing").__name__ == "TestConfig"
    assert get_config(None).__name__ == "DevConfig"
    assert get_config("unknown").__name__ == "DevConfig"


def test_testing_app_flags(app):
    assert app.config["TESTING"] is True
    assert app.config["RATELIMIT_ENABLED"] is False


def test_prod_config_rejects_weak_secret(monkeypatch):
    monkeypatch.setattr(ProdConfig, "SECRET_KEY", "dev-secret-change-me")
    monkeypatch.setattr(ProdConfig, "JWT_SECRET_KEY", "dev-secret-change-me")
    with pytest.raises(RuntimeError):
        create_app("production")

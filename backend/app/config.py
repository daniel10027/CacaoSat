"""Configuration multi-environnements pour l'API CacaoSat."""

from __future__ import annotations

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


class BaseConfig:
    # --- Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True
    API_PREFIX = "/api/v1"

    # --- SQLAlchemy ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://cacaosat:cacaosat@localhost:5432/cacaosat",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

    # --- JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_ERROR_MESSAGE_KEY = "message"

    # --- CORS ---
    CORS_ORIGINS = _split_csv(os.environ.get("CORS_ORIGINS", "http://localhost:5173"))

    # --- Rate limiting ---
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_ENABLED = True

    # --- Infra externes (mockées en dev) ---
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "1025"))
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@cacaosat.ci")
    S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET = os.environ.get("S3_BUCKET", "cacaosat")
    S3_REGION = os.environ.get("S3_REGION", "us-east-1")

    # --- Moteur mock ---
    MOCK_SEED = int(os.environ.get("MOCK_SEED", "42"))

    # --- Planificateur (ré-analyse quotidienne + scan d'alertes) ---
    SCHEDULER_ENABLED = os.environ.get("SCHEDULER_ENABLED", "0") == "1"

    # --- Logs ---
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class DevConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    ENV = "testing"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://cacaosat:cacaosat@localhost:5432/cacaosat_test",
    )
    RATELIMIT_ENABLED = False
    SCHEDULER_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SECRET_KEY = "testing-secret-key-not-for-production-use-000"
    JWT_SECRET_KEY = "testing-jwt-secret-key-not-for-production-000"


class ProdConfig(BaseConfig):
    DEBUG = False
    ENV = "production"

    @classmethod
    def validate(cls) -> None:
        weak = {"dev-secret-change-me", "dev-jwt-secret-change-me", "", None}
        if cls.SECRET_KEY in weak or cls.JWT_SECRET_KEY in weak:
            raise RuntimeError(
                "SECRET_KEY / JWT_SECRET_KEY doivent être définis en production."
            )


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevConfig,
    "testing": TestConfig,
    "production": ProdConfig,
    "default": DevConfig,
}


def get_config(name: str | None) -> type[BaseConfig]:
    return CONFIG_MAP.get(name or "default", DevConfig)

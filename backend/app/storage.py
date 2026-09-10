"""Stockage objet — MinIO/S3 si joignable, sinon repli sur le disque local.

Sert au dépôt des rapports de conformité (PDF + GeoJSON).
"""

from __future__ import annotations

import io
from pathlib import Path

from flask import current_app

_LOCAL_ROOT = Path("instance") / "storage"


def _client():
    import boto3
    from botocore.config import Config

    cfg = current_app.config
    return boto3.client(
        "s3",
        endpoint_url=cfg["S3_ENDPOINT"],
        aws_access_key_id=cfg["S3_ACCESS_KEY"],
        aws_secret_access_key=cfg["S3_SECRET_KEY"],
        region_name=cfg.get("S3_REGION", "us-east-1"),
        config=Config(signature_version="s3v4", connect_timeout=2, retries={"max_attempts": 1}),
    )


def _bucket() -> str:
    return current_app.config["S3_BUCKET"]


def _local_path(key: str) -> Path:
    p = _LOCAL_ROOT / key
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def put_object(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Retourne le backend utilisé : ``s3`` ou ``local``."""
    try:
        client = _client()
        try:
            client.head_bucket(Bucket=_bucket())
        except Exception:  # noqa: BLE001
            client.create_bucket(Bucket=_bucket())
        client.put_object(Bucket=_bucket(), Key=key, Body=data, ContentType=content_type)
        return "s3"
    except Exception as exc:  # noqa: BLE001
        current_app.logger.info("storage: repli local pour %s (%s)", key, exc.__class__.__name__)
        _local_path(key).write_bytes(data)
        return "local"


def get_object(key: str) -> bytes:
    try:
        client = _client()
        obj = client.get_object(Bucket=_bucket(), Key=key)
        return obj["Body"].read()
    except Exception:  # noqa: BLE001
        path = _local_path(key)
        if path.exists():
            return path.read_bytes()
        raise FileNotFoundError(key) from None


def open_stream(key: str) -> io.BytesIO:
    return io.BytesIO(get_object(key))


def presigned_url(key: str, expires: int = 3600) -> str | None:
    try:
        return _client().generate_presigned_url(
            "get_object", Params={"Bucket": _bucket(), "Key": key}, ExpiresIn=expires
        )
    except Exception:  # noqa: BLE001
        return None

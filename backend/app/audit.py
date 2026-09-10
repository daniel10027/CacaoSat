"""Journal d'audit — helper appelé par les vues sur les écritures sensibles."""

from __future__ import annotations

from flask import has_request_context, request

from app.extensions import db
from app.models.audit_log import AuditLog


def _current_actor_id() -> str | None:
    if not has_request_context():
        return None
    try:
        from flask_jwt_extended import get_jwt

        identity = get_jwt().get("sub")
    except Exception:  # noqa: BLE001
        return None
    if not identity:
        return None
    from app.models.user import User

    return str(identity) if db.session.get(User, identity) is not None else None


def record(action: str, entity_type: str, entity_id=None, **payload) -> None:
    ip = None
    if has_request_context():
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    db.session.add(
        AuditLog(
            actor_id=_current_actor_id(),
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            payload=payload or {},
            ip=ip,
        )
    )

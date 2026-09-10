"""Utilitaires partagés par les vues : pagination, tri, portée coopérative."""

from __future__ import annotations

from flask import request
from flask_jwt_extended import get_jwt

from app.errors import ApiError
from app.extensions import db
from app.models.enums import UserRole
from app.schemas.common import paginated, pagination_args

NATIONAL_ROLES = {UserRole.REGULATOR.value, UserRole.ADMIN.value, UserRole.EXPORTER.value}


def token_cooperative_id() -> str | None:
    return get_jwt().get("cooperative_id")


def token_role() -> str:
    return get_jwt().get("role")


def has_national_scope() -> bool:
    return token_role() in NATIONAL_ROLES


def resolve_cooperative_scope(explicit: str | None = None) -> str | None:
    """Coopérative à filtrer : celle du token, ou `explicit` pour un rôle national."""
    if has_national_scope():
        return explicit
    own = token_cooperative_id()
    if explicit and str(explicit) != str(own):
        raise ApiError("Accès limité à votre coopérative.", status=403)
    return own


def assert_can_access_cooperative(cooperative_id) -> None:
    if has_national_scope():
        return
    if str(cooperative_id) != str(token_cooperative_id()):
        raise ApiError("Ressource hors de votre coopérative.", status=403)


def parse_pagination() -> dict:
    return pagination_args.load(request.args)


def apply_sort(query, model, sort: str | None, order: str, allowed: set[str], default: str):
    field = sort if sort in allowed else default
    col = getattr(model, field)
    return query.order_by(col.desc() if order == "desc" else col.asc())


def run_paginated(query, page: int, per_page: int, serializer) -> dict:
    count_q = db.select(db.func.count()).select_from(query.order_by(None).subquery())
    total = db.session.scalar(count_q) or 0
    rows = db.session.scalars(query.limit(per_page).offset((page - 1) * per_page)).all()
    return paginated(serializer.dump(rows, many=True), page, per_page, total)

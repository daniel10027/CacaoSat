"""Hachage de mots de passe (argon2) et contrôle d'accès par rôle."""

from __future__ import annotations

from functools import wraps

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.errors import ApiError
from app.models.enums import UserRole

_hasher = PasswordHasher()


def hash_password(raw: str) -> str:
    return _hasher.hash(raw)


def verify_password(stored_hash: str, raw: str) -> bool:
    try:
        return _hasher.verify(stored_hash, raw)
    except Argon2Error:
        return False


def needs_rehash(stored_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(stored_hash)
    except Argon2Error:
        return False


def current_claims() -> dict:
    verify_jwt_in_request()
    return get_jwt()


def current_user_id() -> str:
    verify_jwt_in_request()
    return get_jwt_identity()


def roles_required(*roles: UserRole | str):
    """Autorise les rôles listés ; `admin` passe toujours."""

    allowed = {str(r) for r in roles} | {UserRole.ADMIN.value}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = current_claims()
            if claims.get("role") not in allowed:
                raise ApiError("Accès refusé pour ce rôle.", status=403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def scope_cooperative_id() -> str | None:
    """`None` pour un régulateur/admin (portée nationale), sinon la coopérative du token."""

    claims = get_jwt()
    if claims.get("role") in {UserRole.REGULATOR.value, UserRole.ADMIN.value, UserRole.EXPORTER.value}:
        return None
    return claims.get("cooperative_id")

from __future__ import annotations

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import db
from app.models.user import User


def authenticate(email: str, password: str) -> User | None:
    user = db.session.execute(
        db.select(User).filter(db.func.lower(User.email) == email.lower())
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        return None
    if not user.check_password(password):
        return None
    db.session.commit()  # persiste un éventuel rehash argon2
    return user


def issue_tokens(user: User) -> dict:
    claims = user.jwt_claims
    access = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(user.id), additional_claims=claims)
    expires = int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds())
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": expires,
    }

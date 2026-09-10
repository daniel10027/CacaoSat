from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, UUIDMixin
from app.models.enums import UserRole
from app.security import hash_password, needs_rehash, verify_password


class User(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(sa.String(160), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=UserRole.AGENT,
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    cooperative_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cooperatives.id", ondelete="SET NULL"), index=True
    )

    cooperative: Mapped[Cooperative | None] = relationship(back_populates="users")  # noqa: F821

    # --- mot de passe ---
    def set_password(self, raw: str) -> None:
        self.password_hash = hash_password(raw)

    def check_password(self, raw: str) -> bool:
        ok = verify_password(self.password_hash, raw)
        if ok and needs_rehash(self.password_hash):
            self.password_hash = hash_password(raw)
        return ok

    @property
    def jwt_claims(self) -> dict:
        return {
            "role": self.role.value if isinstance(self.role, UserRole) else str(self.role),
            "cooperative_id": str(self.cooperative_id) if self.cooperative_id else None,
            "full_name": self.full_name,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} ({self.role})>"

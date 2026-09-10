from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, UUIDMixin


class Cooperative(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "cooperatives"

    name: Mapped[str] = mapped_column(sa.String(160), nullable=False)
    code: Mapped[str] = mapped_column(sa.String(24), nullable=False, unique=True)
    region: Mapped[str | None] = mapped_column(sa.String(80))
    department: Mapped[str | None] = mapped_column(sa.String(80))
    contact_name: Mapped[str | None] = mapped_column(sa.String(120))
    contact_phone: Mapped[str | None] = mapped_column(sa.String(40))
    contact_email: Mapped[str | None] = mapped_column(sa.String(160))

    users: Mapped[list[User]] = relationship(back_populates="cooperative")  # noqa: F821
    producers: Mapped[list[Producer]] = relationship(  # noqa: F821
        back_populates="cooperative", cascade="all, delete-orphan"
    )
    parcels: Mapped[list[Parcel]] = relationship(  # noqa: F821
        back_populates="cooperative", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Cooperative {self.code}>"

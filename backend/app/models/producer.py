from __future__ import annotations

import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import Gender


class Producer(UUIDMixin, TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "producers"

    cooperative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("cooperatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    external_ref: Mapped[str | None] = mapped_column(sa.String(64))
    full_name: Mapped[str] = mapped_column(sa.String(160), nullable=False)
    national_id: Mapped[str | None] = mapped_column(sa.String(64), index=True)
    gender: Mapped[Gender] = mapped_column(
        sa.Enum(Gender, native_enum=False, length=12, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=Gender.UNKNOWN,
    )
    village: Mapped[str | None] = mapped_column(sa.String(120))
    phone: Mapped[str | None] = mapped_column(sa.String(40))
    registered_at: Mapped[date] = mapped_column(sa.Date, nullable=False, default=date.today)

    cooperative: Mapped[Cooperative] = relationship(back_populates="producers")  # noqa: F821
    parcels: Mapped[list[Parcel]] = relationship(back_populates="producer")  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Producer {self.full_name}>"

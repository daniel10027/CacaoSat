from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, UUIDMixin, utcnow
from app.models.enums import AlertSeverity, AlertType

_enum = {"native_enum": False, "values_callable": lambda e: [m.value for m in e]}


class Alert(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "alerts"

    parcel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[AlertType] = mapped_column(sa.Enum(AlertType, length=32, **_enum), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(
        sa.Enum(AlertSeverity, length=12, **_enum), nullable=False, default=AlertSeverity.MEDIUM
    )
    detected_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, default=utcnow
    )
    area_ha: Mapped[float] = mapped_column(sa.Float, nullable=False, default=0.0)
    geometry = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False), nullable=True
    )
    message: Mapped[str] = mapped_column(sa.String(400), nullable=False)
    acknowledged: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    acknowledged_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    parcel: Mapped[Parcel] = relationship(back_populates="alerts")  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Alert {self.type} {self.severity}>"

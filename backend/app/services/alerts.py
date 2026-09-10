"""Moteur d'alertes précoces — compare la dernière analyse à la précédente."""

from __future__ import annotations

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import joinedload, selectinload

from app.audit import record as audit
from app.extensions import db
from app.geo import to_wkt_element
from app.mocks.notifications import send_email, send_sms
from app.models.alert import Alert
from app.models.enums import AlertSeverity, AlertType, UserRole
from app.models.parcel import Parcel
from app.models.user import User

LOSS_DELTA_HA = 0.05
OVERLAP_DELTA_HA = 0.05


def _existing_open(parcel_id, alert_type: AlertType) -> Alert | None:
    return db.session.scalar(
        db.select(Alert).filter_by(parcel_id=parcel_id, type=alert_type, acknowledged=False)
    )


def _severity_for_loss(delta_ha: float, area_ha: float) -> AlertSeverity:
    ratio = delta_ha / max(area_ha, 0.01)
    if ratio >= 0.1:
        return AlertSeverity.CRITICAL
    if ratio >= 0.03:
        return AlertSeverity.HIGH
    return AlertSeverity.MEDIUM


def scan_for_alerts(cooperative_id=None) -> list[Alert]:
    q = (
        db.select(Parcel)
        .filter(Parcel.deleted_at.is_(None))
        .options(selectinload(Parcel.analyses), joinedload(Parcel.producer))
    )
    if cooperative_id:
        q = q.filter(Parcel.cooperative_id == cooperative_id)
    parcels = db.session.scalars(q).unique().all()

    created: list[Alert] = []
    for p in parcels:
        analyses = p.analyses  # triées created_at desc
        latest = analyses[0] if analyses else None
        previous = analyses[1] if len(analyses) > 1 else None
        area_ha = float(p.area_ha or 0)

        # --- data gap ---
        if (p.producer_id is None or not (p.producer and p.producer.national_id)) and not _existing_open(
            p.id, AlertType.DATA_GAP
        ):
            created.append(
                _make(
                    p, AlertType.DATA_GAP, AlertSeverity.LOW, 0.0,
                    "Dossier incomplet : producteur ou pièce d'identité manquant.",
                )
            )

        if latest is None:
            continue

        # --- nouvelle déforestation ---
        base_loss = previous.forest_loss_ha if previous else 0.0
        delta_loss = latest.forest_loss_ha - base_loss
        if delta_loss >= LOSS_DELTA_HA and not _existing_open(p.id, AlertType.NEW_DEFORESTATION):
            created.append(
                _make(
                    p, AlertType.NEW_DEFORESTATION, _severity_for_loss(delta_loss, area_ha),
                    round(delta_loss, 3),
                    f"Nouvelle perte de couvert détectée : +{delta_loss:.2f} ha depuis la dernière analyse.",
                )
            )

        # --- empiètement aire protégée ---
        base_ov = previous.protected_area_overlap_ha if previous else 0.0
        delta_ov = latest.protected_area_overlap_ha - base_ov
        if delta_ov >= OVERLAP_DELTA_HA and not _existing_open(p.id, AlertType.PROTECTED_ENCROACHMENT):
            created.append(
                _make(
                    p, AlertType.PROTECTED_ENCROACHMENT, AlertSeverity.HIGH, round(delta_ov, 3),
                    f"Empiètement d'aire protégée : +{delta_ov:.2f} ha.",
                )
            )

    if created:
        db.session.flush()
        _notify(created)
        audit(
            "alerts.scan", "alert", None,
            count=len(created),
            cooperative_id=str(cooperative_id) if cooperative_id else None,
        )
        db.session.commit()
    return created


def _make(parcel: Parcel, atype: AlertType, severity: AlertSeverity, area_ha: float, message: str) -> Alert:
    alert = Alert(
        parcel_id=parcel.id,
        type=atype,
        severity=severity,
        area_ha=area_ha,
        geometry=to_wkt_element(to_shape(parcel.geometry).centroid),
        message=message,
    )
    db.session.add(alert)
    return alert


def _notify(alerts: list[Alert]) -> None:
    by_coop: dict = {}
    for a in alerts:
        by_coop.setdefault(a.parcel.cooperative_id, []).append(a)
    for coop_id, items in by_coop.items():
        managers = db.session.scalars(
            db.select(User).filter_by(cooperative_id=coop_id, role=UserRole.MANAGER, is_active=True)
        ).all()
        lines = "\n".join(f"- {a.parcel.code} : {a.message}" for a in items)
        body = f"{len(items)} nouvelle(s) alerte(s) de conformité EUDR :\n\n{lines}"
        for m in managers:
            send_email(m.email, f"[CacaoSat] {len(items)} alerte(s) de conformité", body)
            send_sms("+22500000000", f"CacaoSat: {len(items)} alerte(s) EUDR — voir le tableau de bord.")

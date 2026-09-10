"""Planification : ré-analyse quotidienne des parcelles à surveiller + scan d'alertes."""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("app.tasks")
_scheduler: BackgroundScheduler | None = None


def daily_reanalyze_and_alert(app) -> None:
    from app.extensions import db
    from app.models.compliance_score import ComplianceScore
    from app.models.enums import EudrStatus
    from app.models.parcel import Parcel
    from app.services.alerts import scan_for_alerts
    from app.services.analysis import analyze_many

    with app.app_context():
        latest = (
            db.select(ComplianceScore.parcel_id, ComplianceScore.eudr_status)
            .distinct(ComplianceScore.parcel_id)
            .order_by(ComplianceScore.parcel_id, ComplianceScore.computed_at.desc())
            .subquery()
        )
        ids = db.session.scalars(
            db.select(Parcel.id)
            .join(latest, latest.c.parcel_id == Parcel.id)
            .filter(
                Parcel.deleted_at.is_(None),
                latest.c.eudr_status.in_([EudrStatus.AT_RISK.value, EudrStatus.NON_COMPLIANT.value]),
            )
        ).all()
        if ids:
            result = analyze_many(list(ids))
            logger.info("Ré-analyse quotidienne : %s", result)
        created = scan_for_alerts()
        logger.info("Scan d'alertes quotidien : %d alerte(s) créée(s)", len(created))


def init_scheduler(app) -> BackgroundScheduler | None:
    global _scheduler  # noqa: PLW0603 - singleton process-wide
    if not app.config.get("SCHEDULER_ENABLED"):
        return None
    if _scheduler is not None:
        return _scheduler
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        daily_reanalyze_and_alert,
        trigger=CronTrigger(hour=2, minute=30),
        args=[app],
        id="daily_reanalyze_and_alert",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.start()
    app.logger.info("APScheduler démarré (job quotidien 02:30 UTC).")
    return _scheduler

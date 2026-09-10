from __future__ import annotations

import time

from flask import Blueprint, Response, current_app, jsonify

from app.extensions import db

health_bp = Blueprint("health", __name__)

_STARTED_AT = time.time()


@health_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "cacaosat-backend", "uptime_s": round(time.time() - _STARTED_AT, 1)})


@health_bp.get("/health/ready")
def ready():
    checks: dict[str, str] = {}
    ok = True

    try:
        db.session.execute(db.text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc.__class__.__name__}"
        ok = False

    try:
        import redis  # noqa: PLC0415

        client = redis.from_url(current_app.config["REDIS_URL"], socket_connect_timeout=1)
        client.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"unavailable: {exc.__class__.__name__}"

    status = 200 if ok else 503
    return jsonify({"status": "ready" if ok else "degraded", "checks": checks}), status


@health_bp.get("/metrics")
def metrics():
    from app.models import Alert, AnalysisRun, Parcel  # noqa: PLC0415

    def _count(model) -> int:
        try:
            return db.session.scalar(db.select(db.func.count()).select_from(model)) or 0
        except Exception:  # noqa: BLE001
            return 0

    lines = [
        "# HELP cacaosat_uptime_seconds Process uptime.",
        "# TYPE cacaosat_uptime_seconds gauge",
        f"cacaosat_uptime_seconds {round(time.time() - _STARTED_AT, 1)}",
        "# HELP cacaosat_parcels_total Number of parcels.",
        "# TYPE cacaosat_parcels_total gauge",
        f"cacaosat_parcels_total {_count(Parcel)}",
        "# HELP cacaosat_analyses_total Number of analysis runs.",
        "# TYPE cacaosat_analyses_total gauge",
        f"cacaosat_analyses_total {_count(AnalysisRun)}",
        "# HELP cacaosat_alerts_total Number of alerts.",
        "# TYPE cacaosat_alerts_total gauge",
        f"cacaosat_alerts_total {_count(Alert)}",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")

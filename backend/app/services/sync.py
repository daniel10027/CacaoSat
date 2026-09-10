"""Synchronisation hors-ligne de l'application mobile.

- ``bootstrap`` : données de référence pour fonctionner sans réseau.
- ``ingest_batch`` : réception idempotente des relevés terrain (producteurs + parcelles).
"""

from __future__ import annotations

from datetime import UTC, datetime

from shapely.geometry import Point

from app.audit import record as audit
from app.errors import ApiError
from app.extensions import db
from app.geo import parse_polygon, polygon_area_ha, polygon_centroid, to_wkt_element
from app.mocks import protected_areas
from app.mocks.scenarios import SCENARIOS
from app.models.enums import CollectionMethod, ParcelSource, UserRole
from app.models.parcel import Parcel
from app.models.producer import Producer
from app.models.sync_batch import SyncBatch
from app.models.user import User
from app.schemas.parcel import parcels_schema
from app.schemas.producer import producers_schema
from app.services.analysis import analyze_many
from app.services.scoring import W_COMPLETENESS, W_DEFOREST, W_GPS, W_PROTECTED, W_TREND

SCHEMA_VERSION = 1


def _now() -> datetime:
    return datetime.now(UTC)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def bootstrap(user: User, since: str | None = None) -> dict:
    coop_id = user.cooperative_id
    since_dt = _parse_dt(since)

    prod_q = db.select(Producer).filter(Producer.deleted_at.is_(None))
    parc_q = db.select(Parcel).filter(Parcel.deleted_at.is_(None))
    if coop_id is not None:
        prod_q = prod_q.filter(Producer.cooperative_id == coop_id)
        parc_q = parc_q.filter(Parcel.cooperative_id == coop_id)
    if since_dt is not None:
        prod_q = prod_q.filter(Producer.updated_at >= since_dt)
        parc_q = parc_q.filter(Parcel.updated_at >= since_dt)

    producers = db.session.scalars(prod_q).all()
    parcels = db.session.scalars(parc_q).unique().all()

    coop = user.cooperative
    return {
        "schema_version": SCHEMA_VERSION,
        "server_time": _now().isoformat(),
        "cooperative": (
            {
                "id": str(coop.id),
                "code": coop.code,
                "name": coop.name,
                "region": coop.region,
                "department": coop.department,
            }
            if coop
            else None
        ),
        "producers": producers_schema.dump(producers),
        "parcels": parcels_schema.dump(parcels),
        "protected_areas": protected_areas.feature_collection(),
        "scoring": {
            "version": "eudr-scoring/1.0",
            "risk_levels": {"low": ">=80", "medium": "50-79", "high": "<50"},
            "eudr_statuses": ["compliant", "at_risk", "non_compliant"],
            "scenarios": list(SCENARIOS),
            "factors": [
                {"key": "deforestation_post_2020", "weight": W_DEFOREST},
                {"key": "protected_area_overlap", "weight": W_PROTECTED},
                {"key": "ndvi_degradation_trend", "weight": W_TREND},
                {"key": "data_completeness", "weight": W_COMPLETENESS},
                {"key": "gps_quality_freshness", "weight": W_GPS},
            ],
        },
    }


def _resolve_cooperative(user: User, data: dict) -> str:
    if user.role in (UserRole.REGULATOR, UserRole.ADMIN):
        coop_id = data.get("cooperative_id") or user.cooperative_id
    else:
        coop_id = user.cooperative_id
    if coop_id is None:
        raise ApiError("Aucune coopérative associée à cet utilisateur.", status=422)
    return str(coop_id)


def _apply_producer(user: User, op: str, client_id: str, data: dict, id_map: dict) -> str:
    if op == "update" and (data.get("id") or id_map.get(client_id)):
        pid = data.get("id") or id_map[client_id]
        producer = db.session.get(Producer, pid)
        if producer is None:
            raise ApiError("Producteur cible introuvable.", status=404)
        incoming = _parse_dt(data.get("updated_at"))
        if incoming and producer.updated_at and incoming < producer.updated_at:
            return str(producer.id)  # last-write-wins : version serveur plus récente
        for field in ("full_name", "national_id", "gender", "village", "phone", "external_ref"):
            if field in data and data[field] is not None:
                setattr(producer, field, data[field])
        db.session.flush()
        return str(producer.id)

    producer = Producer(
        cooperative_id=_resolve_cooperative(user, data),
        full_name=data["full_name"],
        national_id=data.get("national_id"),
        gender=data.get("gender", "unknown"),
        village=data.get("village"),
        phone=data.get("phone"),
        external_ref=data.get("external_ref") or client_id,
    )
    db.session.add(producer)
    db.session.flush()
    return str(producer.id)


def _apply_parcel(user: User, op: str, client_id: str, data: dict, id_map: dict) -> str:
    geom = parse_polygon(data["geometry"]) if data.get("geometry") else None
    cooperative_id = _resolve_cooperative(user, data)

    producer_id = data.get("producer_id")
    if not producer_id and data.get("producer_client_id"):
        producer_id = id_map.get(data["producer_client_id"])
    if not producer_id and client_id in id_map:  # même client_id producteur+parcelle
        producer_id = id_map.get(client_id)

    if op == "update" and (data.get("id") or id_map.get(client_id)):
        pid = data.get("id") or id_map[client_id]
        parcel = db.session.get(Parcel, pid)
        if parcel is None:
            raise ApiError("Parcelle cible introuvable.", status=404)
        incoming = _parse_dt(data.get("updated_at"))
        if incoming and parcel.updated_at and incoming < parcel.updated_at:
            return str(parcel.id)
        if geom is not None:
            parcel.geometry = to_wkt_element(geom)
            cx, cy = polygon_centroid(geom)
            parcel.centroid = to_wkt_element(Point(cx, cy))
            parcel.area_ha = polygon_area_ha(geom)
        for field in ("planting_year", "crop", "gps_accuracy_m"):
            if field in data and data[field] is not None:
                setattr(parcel, field, data[field])
        if producer_id:
            parcel.producer_id = producer_id
        db.session.flush()
        return str(parcel.id)

    if geom is None:
        raise ApiError("Géométrie requise pour créer une parcelle.", status=422)
    cx, cy = polygon_centroid(geom)
    code = data.get("code") or _next_code(cooperative_id)
    parcel = Parcel(
        code=code,
        cooperative_id=cooperative_id,
        producer_id=producer_id,
        geometry=to_wkt_element(geom),
        centroid=to_wkt_element(Point(cx, cy)),
        area_ha=polygon_area_ha(geom),
        planting_year=data.get("planting_year"),
        crop=data.get("crop", "cocoa"),
        gps_accuracy_m=data.get("gps_accuracy_m"),
        collection_method=data.get("collection_method", CollectionMethod.WALK.value),
        collected_by=user.id,
        collected_at=_parse_dt(data.get("collected_at")) or _now(),
        source=ParcelSource.MOBILE,
    )
    db.session.add(parcel)
    db.session.flush()
    return str(parcel.id)


def _next_code(cooperative_id: str) -> str:
    from app.models.cooperative import Cooperative

    coop = db.session.get(Cooperative, cooperative_id)
    prefix = (coop.code if coop else "PARC").upper()
    n = db.session.scalar(
        db.select(db.func.count()).select_from(Parcel).filter_by(cooperative_id=cooperative_id)
    ) or 0
    return f"{prefix}-{n + 1:04d}"


def ingest_batch(user: User, payload: dict) -> dict:
    device_id = payload.get("device_id")
    client_batch_id = payload.get("client_batch_id")
    items = payload.get("items") or []
    if not device_id:
        raise ApiError("device_id requis.", status=422)

    if client_batch_id:
        existing = db.session.scalar(
            db.select(SyncBatch).filter_by(device_id=device_id, client_batch_id=client_batch_id)
        )
        if existing is not None:
            return _result(existing, replayed=True)

    batch = SyncBatch(
        device_id=device_id,
        client_batch_id=client_batch_id,
        user_id=user.id,
        item_count=len(items),
    )
    db.session.add(batch)
    db.session.flush()

    id_map: dict[str, str] = {}
    errors: list[dict] = []
    accepted = 0
    new_parcel_ids: list[str] = []

    ordered = sorted(items, key=lambda it: 0 if it.get("entity") == "producer" else 1)
    for it in ordered:
        entity = it.get("entity")
        op = it.get("op", "create")
        client_id = str(it.get("client_id") or "")
        data = it.get("data") or {}
        try:
            if entity == "producer":
                server_id = _apply_producer(user, op, client_id, data, id_map)
            elif entity == "parcel":
                server_id = _apply_parcel(user, op, client_id, data, id_map)
                if op == "create":
                    new_parcel_ids.append(server_id)
            else:
                raise ApiError(f"Entité inconnue : {entity}", status=422)
            if client_id:
                id_map[client_id] = server_id
            accepted += 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"client_id": client_id, "entity": entity, "error": str(exc)})

    batch.accepted = accepted
    batch.rejected = len(errors)
    batch.errors = errors
    batch.id_map = id_map
    batch.status = "done" if not errors else ("partial" if accepted else "failed")
    db.session.flush()
    audit("sync.batch", "sync_batch", batch.id, accepted=accepted, rejected=len(errors), device=device_id)
    db.session.commit()

    if new_parcel_ids:
        analyze_many(new_parcel_ids)

    return _result(batch, replayed=False)


def _result(batch: SyncBatch, replayed: bool) -> dict:
    return {
        "batch_id": str(batch.id),
        "status": batch.status,
        "accepted": batch.accepted,
        "rejected": batch.rejected,
        "id_map": batch.id_map,
        "errors": batch.errors,
        "replayed": replayed,
        "server_time": _now().isoformat(),
    }


def batch_status(batch_id) -> dict:
    batch = db.session.get(SyncBatch, batch_id)
    if batch is None:
        raise ApiError("Batch introuvable.", status=404)
    parcel_states = []
    for server_id in set(batch.id_map.values()):
        parcel = db.session.get(Parcel, server_id)
        if parcel is None:
            continue
        score = parcel.latest_score
        parcel_states.append(
            {
                "parcel_id": str(parcel.id),
                "code": parcel.code,
                "analyzed": score is not None,
                "score": score.score if score else None,
                "eudr_status": score.eudr_status.value if score else None,
            }
        )
    return {"batch_id": str(batch.id), "status": batch.status, "parcels": parcel_states}

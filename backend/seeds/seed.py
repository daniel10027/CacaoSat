"""Amorçage de la base CacaoSat.

    flask seed            -> comptes + 2 coopératives
    flask seed-demo       -> + zone pilote (producteurs & parcelles géolocalisées)
"""

from __future__ import annotations

import random
from datetime import UTC, date, datetime

import click
from shapely.geometry import Point, Polygon

from app.extensions import db
from app.geo import polygon_area_ha, polygon_centroid, to_wkt_element
from app.models import Cooperative, Parcel, Producer, User
from app.models.enums import (
    CollectionMethod,
    Gender,
    ParcelSource,
    ParcelStatus,
    UserRole,
)

# --- Zone pilote : région du Cavally, autour de Guiglo (Côte d'Ivoire) ---
PILOT_ANCHOR = (-7.492, 6.544)

COOPERATIVES = [
    {
        "code": "COOPCA-GUIGLO",
        "name": "Coopérative Agricole de Guiglo",
        "region": "Cavally",
        "department": "Guiglo",
        "contact_name": "Bamba Sékou",
        "contact_phone": "+225 07 00 00 01",
        "contact_email": "contact@coopca-guiglo.ci",
    },
    {
        "code": "SCOOP-TAI",
        "name": "Société Coopérative de Taï",
        "region": "Cavally",
        "department": "Taï",
        "contact_name": "Aka Marie-Louise",
        "contact_phone": "+225 07 00 00 02",
        "contact_email": "contact@scoop-tai.ci",
    },
]

VILLAGES = ["Zéaglo", "Bédy-Goazon", "Nizahon", "Kaadé", "Ponan", "Sakré", "Diboké"]
FIRST_NAMES = ["Kouassi", "Adjoua", "Yao", "Aya", "Koffi", "Akissi", "N'Guessan", "Affoué"]
LAST_NAMES = ["Kouamé", "Bamba", "Traoré", "Gnagne", "Séri", "Zadi", "Ouattara", "Koné"]


def _now() -> datetime:
    return datetime.now(UTC)


def _square(lon: float, lat: float, side_m: float) -> Polygon:
    """Petit polygone rectangulaire ~side_m mètres autour de (lon, lat)."""
    dlat = side_m / 111_320.0
    dlon = side_m / (111_320.0 * 0.7)  # cos(~6.5°N) ≈ 0.75 ; marge prudente
    return Polygon(
        [
            (lon - dlon, lat - dlat),
            (lon + dlon, lat - dlat),
            (lon + dlon, lat + dlat),
            (lon - dlon, lat + dlat),
            (lon - dlon, lat - dlat),
        ]
    )


def _wipe() -> None:
    for model in (Parcel, Producer, User, Cooperative):
        db.session.execute(db.delete(model))
    db.session.commit()


def _ensure_cooperatives() -> list[Cooperative]:
    coops: list[Cooperative] = []
    for spec in COOPERATIVES:
        coop = db.session.execute(
            db.select(Cooperative).filter_by(code=spec["code"])
        ).scalar_one_or_none()
        if coop is None:
            coop = Cooperative(**spec)
            db.session.add(coop)
        coops.append(coop)
    db.session.commit()
    return coops


def _ensure_users(coops: list[Cooperative]) -> None:
    def upsert(email: str, full_name: str, role: UserRole, coop: Cooperative | None) -> None:
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if user is None:
            user = User(email=email, full_name=full_name, role=role, cooperative=coop)
            user.set_password("cacaosat")
            db.session.add(user)

    upsert("admin@cacaosat.ci", "Administrateur CacaoSat", UserRole.ADMIN, None)
    upsert("regulateur@conseilcafecacao.ci", "Agent Conseil Café-Cacao", UserRole.REGULATOR, None)
    upsert("exportateur@cacaosat.ci", "Acheteur Export", UserRole.EXPORTER, None)
    for idx, coop in enumerate(coops, start=1):
        upsert(f"manager{idx}@cacaosat.ci", f"Responsable {coop.name}", UserRole.MANAGER, coop)
        upsert(f"agent{idx}a@cacaosat.ci", f"Agent terrain {idx}A", UserRole.AGENT, coop)
        upsert(f"agent{idx}b@cacaosat.ci", f"Agent terrain {idx}B", UserRole.AGENT, coop)
    db.session.commit()


def _seed_demo(coops: list[Cooperative]) -> int:
    rng = random.Random(20260924)
    created = 0
    for c_idx, coop in enumerate(coops):
        agent = db.session.execute(
            db.select(User).filter_by(cooperative_id=coop.id, role=UserRole.AGENT)
        ).scalars().first()
        base_lon = PILOT_ANCHOR[0] + c_idx * 0.06
        base_lat = PILOT_ANCHOR[1] + c_idx * 0.04
        for _p_idx in range(12):
            producer = Producer(
                cooperative=coop,
                full_name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                national_id=f"CI{rng.randint(10**9, 10**10 - 1)}",
                gender=rng.choice([Gender.MALE, Gender.FEMALE]),
                village=rng.choice(VILLAGES),
                phone=f"+225 07 {rng.randint(10, 99)} {rng.randint(10, 99)} {rng.randint(1000, 9999)}",
                registered_at=date(2026, rng.randint(1, 9), rng.randint(1, 28)),
            )
            db.session.add(producer)

            for _ in range(rng.randint(1, 2)):
                lon = base_lon + rng.uniform(-0.03, 0.03)
                lat = base_lat + rng.uniform(-0.03, 0.03)
                poly = _square(lon, lat, rng.uniform(60, 130))
                cx, cy = polygon_centroid(poly)
                parcel = Parcel(
                    code=f"{coop.code}-{created + 1:04d}",
                    producer=producer,
                    cooperative=coop,
                    geometry=to_wkt_element(poly),
                    centroid=to_wkt_element(Point(cx, cy)),
                    area_ha=polygon_area_ha(poly),
                    planting_year=rng.randint(2005, 2019),
                    crop="cocoa",
                    gps_accuracy_m=round(rng.uniform(3.0, 9.0), 1),
                    collection_method=rng.choice(
                        [CollectionMethod.WALK, CollectionMethod.VERTICES]
                    ),
                    collected_by=agent.id if agent else None,
                    collected_at=_now(),
                    source=ParcelSource.MOBILE,
                    status=ParcelStatus.ACTIVE,
                )
                db.session.add(parcel)
                created += 1
    db.session.commit()
    return created


def run(demo: bool = False, force: bool = False) -> None:
    if force:
        click.echo("Purge des tables…")
        _wipe()

    existing_admin = db.session.execute(
        db.select(User).filter_by(email="admin@cacaosat.ci")
    ).scalar_one_or_none()
    if existing_admin and not force:
        click.echo("Comptes déjà présents — seed de base ignoré (utiliser --force).")
    else:
        coops = _ensure_cooperatives()
        _ensure_users(coops)
        click.echo(f"OK : {len(coops)} coopératives, comptes créés (mot de passe : 'cacaosat').")

    if demo:
        coops = db.session.execute(db.select(Cooperative)).scalars().all()
        already = db.session.scalar(db.select(db.func.count()).select_from(Parcel)) or 0
        if already and not force:
            click.echo(f"{already} parcelles déjà présentes — seed démo ignoré (utiliser --force).")
        else:
            n = _seed_demo(coops)
            click.echo(f"OK : zone pilote — {n} parcelles géolocalisées créées.")

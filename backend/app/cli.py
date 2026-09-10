"""Commandes `flask` personnalisées."""

from __future__ import annotations

import click
from flask import Flask
from flask.cli import with_appcontext

from app.extensions import db


def register_cli(app: Flask) -> None:
    app.cli.add_command(create_schema)
    app.cli.add_command(seed)
    app.cli.add_command(seed_demo)
    app.cli.add_command(scan_alerts)
    app.cli.add_command(reanalyze)
    app.cli.add_command(make_report)


@click.command("create-schema")
@with_appcontext
def create_schema() -> None:
    """Crée le schéma via db.create_all() (dev/tests uniquement)."""
    from app import models  # noqa: F401

    db.session.execute(db.text("CREATE EXTENSION IF NOT EXISTS postgis"))
    db.session.commit()
    db.create_all()
    click.echo("Schéma créé (create_all).")


@click.command("seed")
@click.option("--force", is_flag=True, help="Vide les tables avant d'insérer.")
@with_appcontext
def seed(force: bool) -> None:
    """Insère les comptes et données de base."""
    from seeds.seed import run

    run(demo=False, force=force)


@click.command("seed-demo")
@click.option("--force", is_flag=True, help="Vide les tables avant d'insérer.")
@with_appcontext
def seed_demo(force: bool) -> None:
    """Insère la zone pilote de démonstration."""
    from seeds.seed import run

    run(demo=True, force=force)


@click.command("scan-alerts")
@with_appcontext
def scan_alerts() -> None:
    """Scanne les analyses et crée les alertes précoces."""
    from app.services.alerts import scan_for_alerts

    created = scan_for_alerts()
    click.echo(f"{len(created)} alerte(s) créée(s).")


@click.command("reanalyze")
@click.option("--all", "all_parcels", is_flag=True, help="Toutes les parcelles (sinon at_risk/non_compliant).")
@with_appcontext
def reanalyze(all_parcels: bool) -> None:
    """Relance l'analyse satellite + scoring."""
    from app.models.compliance_score import ComplianceScore
    from app.models.enums import EudrStatus
    from app.models.parcel import Parcel
    from app.services.analysis import analyze_many

    query = db.select(Parcel.id).filter(Parcel.deleted_at.is_(None))
    if not all_parcels:
        latest = (
            db.select(ComplianceScore.parcel_id, ComplianceScore.eudr_status)
            .distinct(ComplianceScore.parcel_id)
            .order_by(ComplianceScore.parcel_id, ComplianceScore.computed_at.desc())
            .subquery()
        )
        query = query.join(latest, latest.c.parcel_id == Parcel.id).filter(
            latest.c.eudr_status.in_([EudrStatus.AT_RISK.value, EudrStatus.NON_COMPLIANT.value])
        )
    ids = db.session.scalars(query).all()
    click.echo(analyze_many(list(ids)))


@click.command("make-report")
@click.option("--coop", "coop_code", required=True, help="Code de la coopérative.")
@with_appcontext
def make_report(coop_code: str) -> None:
    """Génère un rapport de conformité EUDR pour une coopérative."""
    from datetime import date

    from app.models.cooperative import Cooperative
    from app.services.report import generate_report

    coop = db.session.scalar(db.select(Cooperative).filter_by(code=coop_code))
    if coop is None:
        raise click.ClickException(f"Coopérative {coop_code} introuvable.")
    report = generate_report(
        cooperative_id=coop.id,
        period_start=date(date.today().year, 1, 1),
        period_end=date.today(),
    )
    click.echo(f"Rapport {report.id} — hash {report.content_hash[:12]}… — {report.pdf_key}")

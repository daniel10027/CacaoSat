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

import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def get_engine():
    try:
        return current_app.extensions["migrate"].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions["migrate"].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")


config.set_main_option("sqlalchemy.url", get_engine_url())
target_db = current_app.extensions["migrate"].db

# Tables/schémas système PostGIS (postgis, tiger, topology) à ignorer en autogenerate.
_PG_SYSTEM_TABLES = {
    "spatial_ref_sys",
    "geometry_columns",
    "geography_columns",
    "raster_columns",
    "raster_overviews",
}


def get_metadata():
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]
    return target_db.metadata


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in (None, "public")
    return True


def include_object(obj, name, type_, reflected, compare_to):
    if getattr(obj, "schema", None) not in (None, "public"):
        return False
    metadata_tables = get_metadata().tables
    if type_ == "table":
        if name in _PG_SYSTEM_TABLES:
            return False
        if reflected and name not in metadata_tables:
            return False
    if type_ == "index" and reflected:
        table = getattr(obj, "table", None)
        if table is not None and table.name not in metadata_tables:
            return False
    return True


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        compare_type=True,
        include_name=include_name,
        include_object=include_object,
        include_schemas=False,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("Aucun changement de schéma détecté.")

    conf_args = current_app.extensions["migrate"].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    conf_args.setdefault("compare_type", True)
    conf_args.setdefault("include_name", include_name)
    conf_args.setdefault("include_object", include_object)
    conf_args.setdefault("include_schemas", False)

    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

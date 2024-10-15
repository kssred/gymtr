from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.core.config import settings
from src.models import BaseModel

config = context.config

section = config.config_ini_section
config.set_section_option(section, "DB_USERNAME", settings.DB.USERNAME)
config.set_section_option(section, "DB_PASSWORD", settings.DB.PASSWORD)
config.set_section_option(section, "DB_PORT", settings.DB.PORT)
config.set_section_option(section, "DB_HOST", settings.DB.HOST)
config.set_section_option(section, "DB_NAME", settings.DB.NAME)

# Setup loggers #
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata


# Exclude tables #
def exclude_tables_from_config(config_):
    tables_ = config_.get("tables", None)
    if tables_ is not None:
        tables = tables_.split(",")
    else:
        tables = []
    return tables


EXCLUDED_TABLES = config.get_section("alembic:exclude", {}).get("tables", "").split(",")


def include_object(object, name, type_, *args, **kwargs):
    return not (type_ == "table" and name in EXCLUDED_TABLES)


# Run migrations #
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

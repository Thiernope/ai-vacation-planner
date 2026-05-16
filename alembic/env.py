from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.core.config import get_application_settings
from app.core.database import DatabaseModelBase

# Importing the models package registers every ORM model on `DatabaseModelBase.metadata`
# so Alembic's --autogenerate can see them. New models go in `app/models/` and the
# package's `__init__.py` re-exports them.
from app import models  # noqa: F401

alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

alembic_config.set_main_option("sqlalchemy.url", get_application_settings().database_url)

target_metadata = DatabaseModelBase.metadata


def run_migrations_offline() -> None:
    """Run migrations without an open DB connection (emits SQL to stdout)."""
    context.configure(
        url=alembic_config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live SQLAlchemy engine."""
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

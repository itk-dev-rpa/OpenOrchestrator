"""Entry point for any Alembic commands."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from OpenOrchestrator.database import base, logs, triggers, queues, constants, schedulers   # noqa: F401 pylint: disable=unused-import

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = base.Base.metadata

if not config.get_main_option("sqlalchemy.url"):
    x_args = context.get_x_argument()
    if len(x_args) < 1:
        raise ValueError("Please provide a connection string in the -x argument.")
    config.set_main_option("sqlalchemy.url", context.get_x_argument()[0])


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
            version_table_schema='dbo',
            include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

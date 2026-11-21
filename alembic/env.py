"""Alembic: DATABASE_URL .env se (mailonix.config), tables mailonix.db.models se."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from mailonix.config import get_settings
from mailonix.db.models import Base
from mailonix.db.session import make_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Agar koi -x db_url=... de to woh, warna .env wala
db_url = context.get_x_argument(as_dictionary=True).get("db_url") or get_settings().database_url
config.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = make_engine(db_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

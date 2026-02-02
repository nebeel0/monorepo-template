from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from core.config import settings
from core.schemas.base import AppDBModel, UserManagementDBModel

# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Dual-database metadata
# ---------------------------------------------------------------------------

app_db_metadata = AppDBModel.metadata
users_db_metadata = UserManagementDBModel.metadata

# Convert async URLs to sync for Alembic
APP_DB_URL = settings.APP_DB_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
USERS_DB_URL = settings.USERS_DB_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode for both databases."""
    # App DB
    context.configure(
        url=APP_DB_URL,
        target_metadata=app_db_metadata,
        version_table="alembic_version_app",
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

    # Users DB
    context.configure(
        url=USERS_DB_URL,
        target_metadata=users_db_metadata,
        version_table="alembic_version_users",
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode for both databases."""
    # App DB
    app_engine = create_engine(APP_DB_URL)
    with app_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=app_db_metadata,
            version_table="alembic_version_app",
        )
        with context.begin_transaction():
            context.run_migrations()
    app_engine.dispose()

    # Users DB
    users_engine = create_engine(USERS_DB_URL)
    with users_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=users_db_metadata,
            version_table="alembic_version_users",
        )
        with context.begin_transaction():
            context.run_migrations()
    users_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

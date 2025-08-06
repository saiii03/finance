import os
import urllib.parse
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Your DB credentials (could also get from env variables if you want)
DB_USER = "postgres"
DB_PASSWORD = urllib.parse.quote_plus("Sainath@2005")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "Financedb"

# Build the DB URL string dynamically
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
escaped_url = DATABASE_URL.replace('%', '%%')
config.set_main_option("sqlalchemy.url", escaped_url)


# Override the sqlalchemy.url value in the Alembic config

# Import your metadata object here if you have it, e.g.
# from yourapp.models import Base
# target_metadata = Base.metadata
target_metadata = None  # replace with your Base.metadata if available


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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

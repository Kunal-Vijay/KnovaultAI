import os
from logging.config import fileConfig

from alembic import context
from pgvector.sqlalchemy import Vector
from sqlalchemy import engine_from_config, pool, create_engine

from app import models  # noqa: F401
from app.db.session import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically. # NOQA
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired a non-local instance of Config.
# for example, config.get_main_option("myvariable")

def get_database_url() -> str:
    from app.db.url import database_url_with_ssl_query, normalize_database_url

    raw = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url") or ""
    return database_url_with_ssl_query(normalize_database_url(raw))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an actual DBAPI connection.  Connections for acquire metadata
    and perform migrations are provided by the operator.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get database URL from environment or alembic.ini
    db_url = get_database_url()
    if not db_url:
        raise ValueError("DATABASE_URL environment variable or sqlalchemy.url in alembic.ini is not set.")
    
    # Use create_engine for synchronous connection
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()

def render_item(type_, obj, autogen_context):
    """
    Provide custom rendering for SQLAlchemy objects.

    This function is a callback for Alembic's autogenerate process.
    It allows us to customize how certain SQLAlchemy types or objects
    are rendered in the migration script. For example, to ensure that
    pgvector's Vector type is correctly imported and defined.
    """
    if type_ == "type" and isinstance(obj, Vector):
        autogen_context.imports.add("from pgvector.sqlalchemy import Vector")
        return f"Vector(dim={obj.dim})"
    # Default rendering for other types
    return False

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

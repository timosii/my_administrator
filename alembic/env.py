from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.config import settings
from app.database.models import data, dicts

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section

config.set_section_option(section, 'POSTGRES_USER', settings.DB_USER)
config.set_section_option(section, 'POSTGRES_PASSWORD', settings.DB_PASSWORD)
config.set_section_option(section, 'POSTGRES_HOST', settings.DB_HOST)
config.set_section_option(section, 'POSTGRES_PORT', settings.DB_PORT)
config.set_section_option(section, 'POSTGRES_DB', settings.DB_NAME)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

# Combine the metadata from both models
target_metadata_dicts = dicts.Base.metadata
targer_metadata_data = data.Base.metadata

# Add metadata from dicts.Base
# for table in dicts.Base.metadata.tables.values():
#     table.tometadata(target_metadata)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata_dicts,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()

    context.configure(
        url=url,
        target_metadata=targer_metadata_data,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
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
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata_dicts
        )

        with context.begin_transaction():
            context.run_migrations()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=targer_metadata_data
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

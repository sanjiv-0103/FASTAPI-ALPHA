
# 1. Import Libraries
from logging.config import fileConfig
from alembic import context
from app.database import Base, engine
from app import models

# 2. Load Alembic Configuration
config = context.config

# 3. Configure Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Connect SQLAlchemy Models to Alembic
target_metadata = Base.metadata

# 5. Run Offline Migrations
def run_migrations_offline():
    url = engine.url.render_as_string(hide_password=False)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()

# 6. Run Online Migrations
def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

# 7. Select Migration Mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

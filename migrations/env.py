import sys
from pathlib import Path

# Agregá el directorio raíz al path para que pueda importar tu app
sys.path.append(str(Path(__file__).parent.parent))

from alembic import context
from sqlalchemy import create_engine
from app.core.database import Base
from app.core.config import settings   # o importa settings de donde esté

# Configuración de Alembic
config = context.config

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode (synchronous)."""
    # Convertir la URL async a sync
    sync_url = settings.database_url.replace("+asyncpg", "+psycopg2")
    connectable = create_engine(sync_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,   # útil para cambios de tipo
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

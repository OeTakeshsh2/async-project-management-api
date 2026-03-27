from app.core.auth import settings
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    )

#SQLAlquemy se usa para definir modelos
class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

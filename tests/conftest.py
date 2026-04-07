import os
from dotenv import load_dotenv
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.user import User, UserToken  # Asegura que los modelos se registren

"""
Setear base de SQLite en memoria para evitar conflictos con postgreSQL
"""

# Cargar variables de entorno ANTES de importar app
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# URL de prueba con SQLite en memoria
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Engine y sesión para la base de prueba (se crean aquí, pero se usarán en cada test)
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Fixture que crea las tablas ANTES de cada test y las limpia DESPUÉS
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    # Crear todas las tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Limpiar después del test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # startup
    async with engine.begin() as conn:
       # Base contiene el metadata de todos los modelos ORM
       #y se usa para crear las tablas en la base de datos
        await conn.run_sync(Base.metadata.create_all)
    yield
    # shutdown (opcional)


app = FastAPI(
    title="Project Management API",
    lifespan=lifespan
)

#Se conecta el router para crear los endpoints
app.include_router(router)

#crea endpoint /
@app.get("/")
def root():
    return {"status": "ok"}

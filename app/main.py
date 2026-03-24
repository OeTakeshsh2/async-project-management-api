from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # shutdown (opcional)


app = FastAPI(
    title="Project Management API",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/")
def root():
    return {"status": "ok"}

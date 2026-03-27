import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):

    for attempt in range(5):
        # startup
        try:
            async with engine.begin() as conn:
                # base contiene el metadata de todos los modelos orm
                #y se usa para crear las tablas en la base de datos
                await conn.run_sync(Base.metadata.create_all)
                print ('db connected')
                break
        except Exception as e:
            print(f"db not ready yet (attempt:{attempt + 1}): {e}")
            await asyncio.sleep(2)
    else:
        print("could not connect to the database")
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

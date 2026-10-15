from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.routers import router as documents_router
from uuid import UUID, uuid4
from app.db.database import engine
from app.db.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(documents_router)

@app.get("/")
async def start():
    return {"message": "Hello!"}


@app.get("/health")
async def health():
    return {"status":"ok"}



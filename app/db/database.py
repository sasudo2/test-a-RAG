from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from functools import lru_cache
from pathlib import Path

engine = create_async_engine("sqlite+aiosqlite:///./rag.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as db:
        yield db

@lru_cache(maxsize=1)
def get_vector_store()-> Chroma:
    persist_directory = Path("data/chroma")
    persist_directory.mkdir(parents=True, exist_ok=True)
    embeddings = HuggingFaceEmbeddings(
        maodel_name="sentence-transformer/all-MiniLM-L6-v2"
    )
    return Chroma(
        collection_name="documents",
        embedding_function = embeddings,
        persist_directory="data/chroma",
    )
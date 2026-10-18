from fastapi import UploadFile, HTTPException
from uuid import uuid4, UUID
from app.db.models import SessionRecord, DocumentRecord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import setting
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma



async def save_text_file(file: UploadFile) -> tuple[UUID, Path]:
    setting.upload_dir.mkdir(parents = True, exist_ok = True)
    document_id = uuid4()
    path = setting.upload_dir/f"{document_id}.txt"

    with path.open("wb") as destination:
        while chunk := await file.read(1024*1024):
            destination.write(chunk)

    return document_id, path, file.filename


async def verify_session(session_id: UUID, db: AsyncSession) -> SessionRecord:
    session = await db.get(SessionRecord, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session

async def assign_session(db: AsyncSession) -> SessionRecord:
    session = SessionRecord(id = uuid4())
    db.add(session)
    await db.flush()
    return session

async def load_documents(session_id:UUID, db: AsyncSession) -> list[DocumentRecord]:
    records = await db.scalars(
        select(DocumentRecord).where(DocumentRecord.session_id == session_id)
    )
    return list(records.all())

async def chunk_documents(records:list, chunk_size = 500, chunk_overlap = 150) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    all_chunks = []
    for record in records:
        loader = TextLoader(record.storage_path, encoding = "utf-8")
        loaded = await loader.aload()
        all_chunks.extend(splitter.split_documents(loaded))
    return all_chunks



async def vector_store_push(session_id:UUID, chunks: list, v_db: Chroma):
    for chunk in chunks:
        chunk.metadata["session_id"] = str(session_id)
    return await v_db.aadd_documents(chunks)

async def vector_store_query(session_id:UUID, query: list, v_db: Chroma):
    return await v_db.asimilarity_search(
        query,
        k=4,
        filter={"session_id": str(session_id)}
    )
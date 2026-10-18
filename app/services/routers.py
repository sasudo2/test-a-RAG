#import router from fastapi
#service the POST request
#parse the incoming document txt
#store the document in a db
#send the request for further processing based on the selected method
from uuid import UUID, uuid4
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db, get_vector_store
from app.db.models import DocumentRecord, SessionRecord
from app.services.helper import save_text_file, verify_session, assign_session, load_documents, chunk_documents, vector_store_push, vector_store_query
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.models.rag import RAGQuery

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

UPLOAD_DIR = Path("data/upload")

@router.post("/upload")
async def upload_document(
    session_id: UUID | None = Form(None),
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    ):
    if session_id is None:
        session = await assign_session(db)
    else:
        session = await verify_session(session_id, db)

    uploaded_documents = []
    for file in files:
        document_id, path, filename = await save_text_file(file)

        db.add(DocumentRecord(
            id=document_id,
            session_id=session.id,
            filename=str(filename)+".txt",
            storage_path=str(path),
        ))
        uploaded_documents.append({
            "document_id": document_id,
            "filename": filename,
        })

    session.last_activity_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "session_id": session.id,
        "documents": uploaded_documents,
    }

@router.post("/pure_RAG")
async def pure_RAG(session_id:UUID, db:AsyncSession =  Depends(get_db), v_db:Chroma = Depends(get_vector_store)):
    """
    get all the document for the given session
    parse the documents
    chunk the documents
    embed the documents
    pass them to the vectorDB
    """
    session = await verify_session(session_id)
    records = await load_documents(session_id, db)
    chunks = await chunk_documents(records)
    store_ids = await vector_store_push(session_id, chunks, v_db)
    return {"session_id":session_id, "status": "success"}
    

@router.post("/pure_RAG/query")
async def pure_RAG(request:RAGQuery, db:AsyncSession = Depends(get_db), v_db:Chroma = Depends(get_vector_store)):
    """
    get the query and embed them
    search from the vector database
    return result from the top k result
    """
    session = await verify_session(request.session_id)
    documents = await vector_store_query(request.session_id, request.query, v_db)

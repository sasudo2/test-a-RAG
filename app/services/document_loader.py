#import router from fastapi
#service the POST request
#parse the incoming document txt
#store the document in a db
#send the request for further processing baesd on the selected method
from uuid import UUID, uuid4
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import DocumentRecord, SessionRecord

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
        session = SessionRecord(id=uuid4())
        db.add(session)
        await db.flush()  # Send the new session row to the DB
    else:
        session = await db.get(SessionRecord, session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

    uploaded_documents = []

    for file in files:
        document_id, path = await save_text_file(file)

        db.add(DocumentRecord(
            id=document_id,
            session_id=session.id,
            filename=file.filename or "upload.txt",
            storage_path=str(path),
        ))
        uploaded_documents.append({
            "document_id": document_id,
            "filename": file.filename,
        })

    session.last_activity_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "session_id": session.id,
        "documents": uploaded_documents,
    }

async def save_text_file(file: UploadFile) -> tuple[uuid4, Path]:
    UPLOAD_DIR.mkdir(parents = True, exist_ok = True)
    document_id = uuid4()
    path = UPLOAD_DIR/f"{document_id}.txt"

    with path.open("wb") as destination:
        while chunk := await file.read(1024*1024):
            destination.write(chunk)

    return document_id, path
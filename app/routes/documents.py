import os
import hashlib
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from app.database import get_session
from app.models import User, Document
from app.routes.auth import get_current_user
from app.rag_engine import index_pdf_file, query_rag_engine
from fastapi.responses import StreamingResponse
from app.rag_engine import index_pdf_file, query_rag_engine, stream_rag_engine

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    content = await file.read()
    file_size = len(content)
    file_hash = hashlib.sha256(content).hexdigest()

    # Deduplication check
    existing_doc = session.exec(
        select(Document).where(Document.user_id == current_user.id, Document.file_hash == file_hash)
    ).first()

    if existing_doc:
        return {
            "message": "Document has already been uploaded and indexed.",
            "document_id": existing_doc.id,
            "total_chunks": existing_doc.total_chunks
        }

    file_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)

    new_doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_hash=file_hash,
        file_size_bytes=file_size
    )
    session.add(new_doc)
    session.commit()
    session.refresh(new_doc)

    # Index into vector database
    total_chunks = index_pdf_file(
        user_id=current_user.id,
        doc_id=new_doc.id,
        file_path=file_path,
        filename=new_doc.filename
    )

    new_doc.total_chunks = total_chunks
    session.add(new_doc)
    session.commit()

    return {
        "message": "Document uploaded and indexed successfully.",
        "document_id": new_doc.id,
        "total_chunks": total_chunks
    }

@router.post("/query")
def ask_question(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    return query_rag_engine(user_id=current_user.id, query_text=request.query)

@router.post("/query-stream")
def ask_question_stream(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    return StreamingResponse(
        stream_rag_engine(user_id=current_user.id, query_text=request.query),
        media_type="text/event-stream"
    )
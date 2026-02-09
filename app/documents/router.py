# app/documents/router.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.documents.schemas import DocumentOut,DocumentStatusOut
from app.documents.service import DocumentService,DocumentNotFoundError
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.session import SessionLocal
from app.db.models import Document

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed",
        )

    service = DocumentService(db=db)

    file_bytes = await file.read()

    document = service.upload_document(
    user_id=current_user.id,
    filename=file.filename,
    file_bytes=file_bytes,
)

    return document



@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DocumentService(db=db)
    return service.list_documents_for_user(user_id=current_user.id)

def process_document_background(document_id: int):
    db = SessionLocal()
    try:
        service = DocumentService(db=db)
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )
        if document:
            service.process_document(document)
    finally:
        db.close()


@router.post("/{document_id}/process", status_code=202)
def process_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DocumentService(db=db)

    try:
        document = service.get_document(document_id=document_id, user_id=current_user.id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status in ("PROCESSING", "COMPLETED"):
        return {"document_id": document.id, "status": document.status}

    # Immediately mark as PROCESSING
    document.status = "PROCESSING"
    db.commit()

    # Run async processing in the background
    background_tasks.add_task(
    process_document_background,
    document.id
)

    return {"document_id": document.id, "status": "PROCESSING"}

# -------------------------
# Status endpoint
# -------------------------
@router.get("/{document_id}/status", response_model=DocumentStatusOut)
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DocumentService(db=db)

    try:
        document = service.get_document(document_id=document_id, user_id=current_user.id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"document_id": document.id, "status": document.status}


# -------------------------
# Result endpoint
# -------------------------
@router.get("/{document_id}/result")
def get_document_result(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DocumentService(db=db)

    try:
        document = service.get_document(document_id=document_id, user_id=current_user.id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail=f"Document not ready. Current status: {document.status}"
        )

    return {"document_id": document.id, "result": document.result}

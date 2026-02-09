# app/documents/service.py

import time
from typing import List
from sqlalchemy.orm import Session

from app.db.models import Document
from app.storage.file_storage import LocalFileStorage
from app.core.logging import get_logger

logger = get_logger("document")


class DocumentNotFoundError(Exception):
    pass


class DocumentService:
    """
    Pure business logic for document lifecycle.
    No FastAPI dependencies.
    """

    def __init__(self, db: Session, storage: LocalFileStorage | None = None):
        self.db = db
        self.storage = storage or LocalFileStorage()

    # -------------------------
    # Upload
    # -------------------------
    def upload_document(
        self,
        *,
        user_id: int,
        filename: str,
        file_bytes: bytes,
    ) -> Document:
        file_path = self.storage.save_file(filename, file_bytes)

        document = Document(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            status="UPLOADED",
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        logger.info(
    "document_uploaded",
    extra={
        "extra": {
            "document_id": document.id,
            "user_id": user_id,
            "event": "uploaded",
        }
    },
)
        return document

    # -------------------------
    # Read
    # -------------------------
    def list_documents_for_user(self, user_id: int) -> List[Document]:
        """Return all documents owned by a specific user."""
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def get_document(self, document_id: int, user_id: int | None) -> Document:
        """
        Fetch a document by ID.
        If user_id is provided, validate ownership.
        This allows background tasks to fetch the document without a user context.
        """
        query = self.db.query(Document).filter(Document.id == document_id)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)

        document = query.first()
        if not document:
            raise DocumentNotFoundError()

        return document

    # -------------------------
    # Processing
    # -------------------------
    # -------------------------
# Processing
# -------------------------
    def process_document(self, document: Document) -> None:
        document.status = "PROCESSING"
        self.db.commit()

        try:
        # Simulate processing time
            time.sleep(15)  # 5 seconds

            result = {"text": f"Processed content for {document.filename}"}
            document.status = "COMPLETED"
            document.result = result["text"]

        except Exception:
            document.status = "FAILED"

        self.db.commit()
        logger.info(
    "document_processing_started",
    extra={
        "extra": {
            "document_id": document.id,
            "event": "process_started",
        }
    },
)


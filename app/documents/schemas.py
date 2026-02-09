# app/documents/schemas.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# -------------------------
# Base schema (shared fields)
# -------------------------
class DocumentBase(BaseModel):
    id: int
    filename: str
    file_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# Response: upload & list
# -------------------------
class DocumentOut(DocumentBase):
    """
    Returned after upload and in document listing.
    """
    pass


# -------------------------
# Response: status endpoint
# -------------------------
class DocumentStatusOut(BaseModel):
    document_id: int
    status: str

    class Config:
        orm_mode = True


# -------------------------
# Response: result endpoint
# -------------------------
class DocumentResultOut(BaseModel):
    id: int
    status: str
    result: Optional[str]

    class Config:
        from_attributes = True

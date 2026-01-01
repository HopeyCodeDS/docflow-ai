from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.document import DocumentStatus, DocumentType


class DocumentCreateDTO(BaseModel):
    original_filename: str
    file_type: str
    file_size: int
    storage_path: str


class DocumentDTO(BaseModel):
    id: UUID
    original_filename: str
    file_type: str
    file_size: int
    storage_path: str
    uploaded_at: datetime
    uploaded_by: UUID
    status: DocumentStatus
    document_type: Optional[DocumentType]
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListDTO(BaseModel):
    documents: list[DocumentDTO]
    total: int
    page: int
    page_size: int


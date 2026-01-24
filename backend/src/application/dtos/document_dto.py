from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.document import Document, DocumentStatus, DocumentType


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

    @classmethod
    def from_entity(cls, entity: Document) -> "DocumentDTO":
        return cls(
            id=entity.id,
            original_filename=entity.original_filename,
            file_type=entity.file_type,
            file_size=entity.file_size,
            storage_path=entity.storage_path,
            uploaded_at=entity.uploaded_at,
            uploaded_by=entity.uploaded_by,
            status=entity.status,
            document_type=entity.document_type,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class DocumentListDTO(BaseModel):
    documents: list[DocumentDTO]
    total: int
    page: int
    page_size: int

    @classmethod
    def from_entities(
        cls,
        entities: List[Document],
        total: int,
        page: int,
        page_size: int,
    ) -> "DocumentListDTO":
        return cls(
            documents=[DocumentDTO.from_entity(e) for e in entities],
            total=total,
            page=page,
            page_size=page_size,
        )


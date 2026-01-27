from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from ....domain.entities.document import Document, DocumentStatus, DocumentType
from ..models import DocumentModel


class DocumentRepository:
    """Repository for Document aggregate"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, document: Document) -> Document:
        """Create a new document"""
        model = DocumentModel(
            id=document.id,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            storage_path=document.storage_path,
            uploaded_by=document.uploaded_by,
            status=document.status.value,
            document_type=document.document_type.value if document.document_type else None,
            version=document.version,
            uploaded_at=document.uploaded_at,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)

    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID"""
        model = self.session.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        return self._to_entity(model) if model else None

    def list(self, skip: int = 0, limit: int = 100, status: Optional[DocumentStatus] = None) -> List[Document]:
        """List documents with pagination"""
        query = self.session.query(DocumentModel)
        if status:
            query = query.filter(DocumentModel.status == status.value)
        models = query.offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def count(self, status: Optional[DocumentStatus] = None) -> int:
        """Count documents matching the given filters"""
        query = self.session.query(func.count(DocumentModel.id))
        if status:
            query = query.filter(DocumentModel.status == status.value)
        return query.scalar() or 0

    def update(self, document: Document) -> Document:
        """Update document"""
        model = self.session.query(DocumentModel).filter(DocumentModel.id == document.id).first()
        if model:
            model.status = document.status.value
            model.document_type = document.document_type.value if document.document_type else None
            model.version = document.version
            model.updated_at = document.updated_at
            self.session.flush()
        return self._to_entity(model)

    def delete(self, document_id: UUID) -> None:
        """Delete document by ID"""
        model = self.session.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if model:
            self.session.delete(model)
            self.session.flush()

    def _to_entity(self, model: DocumentModel) -> Document:
        """Convert model to entity"""
        return Document(
            id=model.id,
            original_filename=model.original_filename,
            file_type=model.file_type,
            file_size=model.file_size,
            storage_path=model.storage_path,
            uploaded_by=model.uploaded_by,
            status=DocumentStatus(model.status),
            document_type=DocumentType(model.document_type) if model.document_type else None,
            version=model.version,
            uploaded_at=model.uploaded_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

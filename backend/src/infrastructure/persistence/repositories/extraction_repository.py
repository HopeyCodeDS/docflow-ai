from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ....domain.entities.extraction import Extraction, ExtractionMethod
from ..models import ExtractionModel


class ExtractionRepository:
    """Repository for Extraction entity"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, extraction: Extraction) -> Extraction:
        """Create a new extraction"""
        model = ExtractionModel(
            id=extraction.id,
            document_id=extraction.document_id,
            extraction_method=extraction.extraction_method.value,
            raw_text=extraction.raw_text,
            structured_data=extraction.structured_data,
            confidence_scores=extraction.confidence_scores,
            extraction_metadata=extraction.extraction_metadata,
            extracted_at=extraction.extracted_at,
            created_at=extraction.created_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)

    def get_by_document_id(self, document_id: UUID) -> Optional[Extraction]:
        """Get the latest extraction by document ID"""
        model = self.session.query(ExtractionModel).filter(
            ExtractionModel.document_id == document_id
        ).order_by(ExtractionModel.extracted_at.desc()).first()
        return self._to_entity(model) if model else None

    def delete_by_document_id(self, document_id: UUID) -> int:
        """Delete all extractions for a document. Returns count of deleted records."""
        deleted = self.session.query(ExtractionModel).filter(
            ExtractionModel.document_id == document_id
        ).delete()
        self.session.flush()
        return deleted

    def _to_entity(self, model: ExtractionModel) -> Extraction:
        """Convert model to entity"""
        return Extraction(
            id=model.id,
            document_id=model.document_id,
            extraction_method=ExtractionMethod(model.extraction_method),
            raw_text=model.raw_text,
            structured_data=model.structured_data,
            confidence_scores=model.confidence_scores or {},
            extraction_metadata=model.extraction_metadata or {},
            extracted_at=model.extracted_at,
            created_at=model.created_at,
        )

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.review import Review, ReviewStatus


class ReviewCreateDTO(BaseModel):
    corrections: Dict[str, Any]
    review_notes: Optional[str] = None


class ReviewDTO(BaseModel):
    id: UUID
    document_id: UUID
    reviewed_by: UUID
    corrections: Dict[str, Any]
    review_status: ReviewStatus
    review_notes: Optional[str]
    reviewed_at: datetime
    
    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, entity: Review) -> "ReviewDTO":
        return cls(
            id=entity.id,
            document_id=entity.document_id,
            reviewed_by=entity.reviewed_by,
            corrections=entity.corrections,
            review_status=entity.review_status,
            review_notes=entity.review_notes,
            reviewed_at=entity.reviewed_at,
        )


from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.review import ReviewStatus


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


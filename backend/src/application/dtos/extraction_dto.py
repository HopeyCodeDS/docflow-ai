from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.extraction import ExtractionMethod


class ExtractionDTO(BaseModel):
    id: UUID
    document_id: UUID
    extraction_method: ExtractionMethod
    raw_text: Optional[str]
    structured_data: Dict[str, Any]
    confidence_scores: Dict[str, float]
    extracted_at: datetime
    extraction_metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


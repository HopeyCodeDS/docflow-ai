from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.validation_result import ValidationStatus


class ValidationErrorDTO(BaseModel):
    field: str
    message: str
    severity: str


class ValidationResultDTO(BaseModel):
    id: UUID
    extraction_id: UUID
    validation_rules: Dict[str, Any]
    validation_status: ValidationStatus
    validation_errors: List[Dict[str, Any]]
    validated_at: datetime
    
    class Config:
        from_attributes = True


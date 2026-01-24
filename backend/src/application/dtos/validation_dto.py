from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.validation_result import ValidationResult, ValidationStatus


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

    @classmethod
    def from_entity(cls, entity: ValidationResult) -> "ValidationResultDTO":
        return cls(
            id=entity.id,
            extraction_id=entity.extraction_id,
            validation_rules=entity.validation_rules,
            validation_status=entity.validation_status,
            validation_errors=entity.validation_errors or [],
            validated_at=entity.validated_at,
        )


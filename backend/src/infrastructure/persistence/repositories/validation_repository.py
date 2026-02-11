from typing import Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ....domain.entities.validation_result import ValidationResult, ValidationStatus
from ..models import ValidationResultModel


class ValidationResultRepository:
    """Repository for ValidationResult entity"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, validation_result: ValidationResult) -> ValidationResult:
        """Create a new validation result"""
        val = validation_result.validation_errors or []
        validation_errors = [
            x if isinstance(x, dict) else {"field": x.field, "message": x.message, "severity": x.severity}
            for x in val
        ]
        model = ValidationResultModel(
            id=validation_result.id,
            extraction_id=validation_result.extraction_id,
            validation_rules=validation_result.validation_rules,
            validation_status=validation_result.validation_status.value,
            validation_errors=validation_errors,
            validated_at=validation_result.validated_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)

    def get_by_extraction_id(self, extraction_id: UUID) -> Optional[ValidationResult]:
        """Get validation result by extraction ID (latest first)"""
        model = self.session.query(ValidationResultModel).filter(
            ValidationResultModel.extraction_id == extraction_id
        ).order_by(ValidationResultModel.validated_at.desc()).first()
        return self._to_entity(model) if model else None

    def delete_by_extraction_id(self, extraction_id: UUID) -> None:
        """Delete all validation results for an extraction (dedup before create)"""
        self.session.query(ValidationResultModel).filter(
            ValidationResultModel.extraction_id == extraction_id
        ).delete()
        self.session.flush()

    def _to_entity(self, model: ValidationResultModel) -> ValidationResult:
        """Convert model to entity"""
        errors = model.validation_errors or []
        return ValidationResult(
            id=model.id,
            extraction_id=model.extraction_id,
            validation_rules=model.validation_rules,
            validation_status=ValidationStatus(model.validation_status),
            validation_errors=errors,
            validated_at=model.validated_at,
            created_at=model.validated_at,
        )

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


class ValidationError:
    """Value object for validation errors"""
    
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # error, warning


class ValidationResult:
    """Validation result entity"""
    
    def __init__(
        self,
        id: UUID,
        extraction_id: UUID,
        validation_rules: Dict[str, Any],
        validation_status: ValidationStatus,
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        validated_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.extraction_id = extraction_id
        self.validation_rules = validation_rules
        self.validation_status = validation_status
        self.validation_errors = validation_errors or []
        self.validated_at = validated_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
    
    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return self.validation_status == ValidationStatus.FAILED
    
    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return self.validation_status == ValidationStatus.WARNING


from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class AuditAction(str, Enum):
    UPLOAD = "UPLOAD"
    EXTRACT = "EXTRACT"
    VALIDATE = "VALIDATE"
    REVIEW = "REVIEW"
    EXPORT = "EXPORT"
    CORRECT = "CORRECT"
    DELETE = "DELETE"


class AuditTrail:
    """Audit trail entity"""
    
    def __init__(
        self,
        id: UUID,
        document_id: UUID,
        action: AuditAction,
        performed_by: UUID,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        performed_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.document_id = document_id
        self.action = action
        self.performed_by = performed_by
        self.changes = changes or {}
        self.metadata = metadata or {}
        self.performed_at = performed_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()


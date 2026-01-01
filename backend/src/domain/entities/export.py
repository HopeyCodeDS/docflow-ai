from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class ExportStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Export:
    """Export entity"""
    
    def __init__(
        self,
        id: UUID,
        document_id: UUID,
        exported_to: str,
        export_payload: Dict[str, Any],
        export_status: ExportStatus = ExportStatus.PENDING,
        exported_at: Optional[datetime] = None,
        retry_count: int = 0,
        error_message: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.document_id = document_id
        self.exported_to = exported_to
        self.export_payload = export_payload
        self.export_status = export_status
        self.exported_at = exported_at
        self.retry_count = retry_count
        self.error_message = error_message
        self.created_at = created_at or datetime.utcnow()
    
    def mark_success(self) -> None:
        """Mark export as successful"""
        self.export_status = ExportStatus.SUCCESS
        self.exported_at = datetime.utcnow()
        self.error_message = None
    
    def mark_failed(self, error_message: str) -> None:
        """Mark export as failed"""
        self.export_status = ExportStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
    
    def increment_retry(self) -> None:
        """Increment retry count"""
        self.retry_count += 1


from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.export import Export, ExportStatus


class ExportCreateDTO(BaseModel):
    exported_to: str


class ExportDTO(BaseModel):
    id: UUID
    document_id: UUID
    exported_to: str
    export_payload: Dict[str, Any]
    export_status: ExportStatus
    exported_at: Optional[datetime]
    retry_count: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, entity: Export) -> "ExportDTO":
        return cls(
            id=entity.id,
            document_id=entity.document_id,
            exported_to=entity.exported_to,
            export_payload=entity.export_payload,
            export_status=entity.export_status,
            exported_at=entity.exported_at,
            retry_count=entity.retry_count,
            error_message=entity.error_message,
        )


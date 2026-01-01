from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.entities.export import ExportStatus


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


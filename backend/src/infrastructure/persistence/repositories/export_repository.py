from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ....domain.entities.export import Export, ExportStatus
from ..models import ExportModel


class ExportRepository:
    """Repository for Export entity"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, export: Export) -> Export:
        """Create a new export"""
        model = ExportModel(
            id=export.id,
            document_id=export.document_id,
            exported_to=export.exported_to,
            export_payload=export.export_payload,
            export_status=export.export_status.value,
            exported_at=export.exported_at,
            retry_count=export.retry_count,
            error_message=export.error_message,
            created_at=export.created_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)

    def get_by_document_id(self, document_id: UUID) -> Optional[Export]:
        """Get export by document ID"""
        model = self.session.query(ExportModel).filter(
            ExportModel.document_id == document_id
        ).first()
        return self._to_entity(model) if model else None

    def update(self, export: Export) -> Export:
        """Update export"""
        model = self.session.query(ExportModel).filter(ExportModel.id == export.id).first()
        if model:
            model.export_status = export.export_status.value
            model.exported_at = export.exported_at
            model.retry_count = export.retry_count
            model.error_message = export.error_message
            self.session.flush()
        return self._to_entity(model)

    def _to_entity(self, model: ExportModel) -> Export:
        """Convert model to entity"""
        return Export(
            id=model.id,
            document_id=model.document_id,
            exported_to=model.exported_to,
            export_payload=model.export_payload,
            export_status=ExportStatus(model.export_status),
            exported_at=model.exported_at,
            retry_count=model.retry_count,
            error_message=model.error_message,
            created_at=model.created_at,
        )

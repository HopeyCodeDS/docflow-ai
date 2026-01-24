from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from ....domain.entities.audit_trail import AuditTrail, AuditAction
from ..models import AuditTrailModel


class AuditTrailRepository:
    """Repository for AuditTrail entity"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, audit_trail: AuditTrail) -> AuditTrail:
        """Create a new audit trail entry"""
        model = AuditTrailModel(
            id=audit_trail.id,
            document_id=audit_trail.document_id,
            action=audit_trail.action.value,
            performed_by=audit_trail.performed_by,
            changes=audit_trail.changes,
            audit_metadata=audit_trail.metadata,
            performed_at=audit_trail.performed_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)

    def get_by_document_id(self, document_id: UUID, limit: int = 100) -> List[AuditTrail]:
        """Get audit trails by document ID"""
        models = self.session.query(AuditTrailModel).filter(
            AuditTrailModel.document_id == document_id
        ).order_by(AuditTrailModel.performed_at.desc()).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: AuditTrailModel) -> AuditTrail:
        """Convert model to entity"""
        return AuditTrail(
            id=model.id,
            document_id=model.document_id,
            action=AuditAction(model.action),
            performed_by=model.performed_by,
            changes=model.changes or {},
            metadata=model.audit_metadata or {},
            performed_at=model.performed_at,
            created_at=model.performed_at,
        )

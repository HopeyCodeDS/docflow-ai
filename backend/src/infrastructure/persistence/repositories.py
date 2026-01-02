from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ...domain.entities.document import Document, DocumentStatus, DocumentType
from ...domain.entities.extraction import Extraction, ExtractionMethod
from ...domain.entities.validation_result import ValidationResult, ValidationStatus
from ...domain.entities.review import Review, ReviewStatus
from ...domain.entities.audit_trail import AuditTrail, AuditAction
from ...domain.entities.export import Export, ExportStatus
from .models import (
    DocumentModel, ExtractionModel, ValidationResultModel,
    ReviewModel, AuditTrailModel, ExportModel
)


class DocumentRepository:
    """Repository for Document aggregate"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, document: Document) -> Document:
        """Create a new document"""
        model = DocumentModel(
            id=document.id,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            storage_path=document.storage_path,
            uploaded_by=document.uploaded_by,
            status=document.status.value,
            document_type=document.document_type.value if document.document_type else None,
            version=document.version,
            uploaded_at=document.uploaded_at,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)
    
    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID"""
        model = self.session.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        return self._to_entity(model) if model else None
    
    def list(self, skip: int = 0, limit: int = 100, status: Optional[DocumentStatus] = None) -> List[Document]:
        """List documents with pagination"""
        query = self.session.query(DocumentModel)
        if status:
            query = query.filter(DocumentModel.status == status.value)
        models = query.offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]
    
    def update(self, document: Document) -> Document:
        """Update document"""
        model = self.session.query(DocumentModel).filter(DocumentModel.id == document.id).first()
        if model:
            model.status = document.status.value
            model.document_type = document.document_type.value if document.document_type else None
            model.version = document.version
            model.updated_at = document.updated_at
            self.session.flush()
        return self._to_entity(model)
    
    def delete(self, document_id: UUID) -> None:
        """Delete document by ID"""
        model = self.session.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if model:
            self.session.delete(model)
            self.session.flush()
    
    def _to_entity(self, model: DocumentModel) -> Document:
        """Convert model to entity"""
        return Document(
            id=model.id,
            original_filename=model.original_filename,
            file_type=model.file_type,
            file_size=model.file_size,
            storage_path=model.storage_path,
            uploaded_by=model.uploaded_by,
            status=DocumentStatus(model.status),
            document_type=DocumentType(model.document_type) if model.document_type else None,
            version=model.version,
            uploaded_at=model.uploaded_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ExtractionRepository:
    """Repository for Extraction entity"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, extraction: Extraction) -> Extraction:
        """Create a new extraction"""
        model = ExtractionModel(
            id=extraction.id,
            document_id=extraction.document_id,
            extraction_method=extraction.extraction_method.value,
            raw_text=extraction.raw_text,
            structured_data=extraction.structured_data,
            confidence_scores=extraction.confidence_scores,
            extraction_metadata=extraction.extraction_metadata,
            extracted_at=extraction.extracted_at,
            created_at=extraction.created_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)
    
    def get_by_document_id(self, document_id: UUID) -> Optional[Extraction]:
        """Get extraction by document ID"""
        model = self.session.query(ExtractionModel).filter(
            ExtractionModel.document_id == document_id
        ).first()
        return self._to_entity(model) if model else None
    
    def _to_entity(self, model: ExtractionModel) -> Extraction:
        """Convert model to entity"""
        return Extraction(
            id=model.id,
            document_id=model.document_id,
            extraction_method=ExtractionMethod(model.extraction_method),
            raw_text=model.raw_text,
            structured_data=model.structured_data,
            confidence_scores=model.confidence_scores or {},
            extraction_metadata=model.extraction_metadata or {},
            extracted_at=model.extracted_at,
            created_at=model.created_at,
        )


class ValidationResultRepository:
    """Repository for ValidationResult entity"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, validation_result: ValidationResult) -> ValidationResult:
        """Create a new validation result"""
        model = ValidationResultModel(
            id=validation_result.id,
            extraction_id=validation_result.extraction_id,
            validation_rules=validation_result.validation_rules,
            validation_status=validation_result.validation_status.value,
            validation_errors=[{"field": e.field, "message": e.message, "severity": e.severity}
                             for e in validation_result.validation_errors] if validation_result.validation_errors else [],
            validated_at=validation_result.validated_at,
            created_at=validation_result.created_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)
    
    def get_by_extraction_id(self, extraction_id: UUID) -> Optional[ValidationResult]:
        """Get validation result by extraction ID"""
        model = self.session.query(ValidationResultModel).filter(
            ValidationResultModel.extraction_id == extraction_id
        ).first()
        return self._to_entity(model) if model else None
    
    def _to_entity(self, model: ValidationResultModel) -> ValidationResult:
        """Convert model to entity"""
        from ...domain.entities.validation_result import ValidationError
        errors = [ValidationError(**e) for e in (model.validation_errors or [])]
        return ValidationResult(
            id=model.id,
            extraction_id=model.extraction_id,
            validation_rules=model.validation_rules,
            validation_status=ValidationStatus(model.validation_status),
            validation_errors=errors,
            validated_at=model.validated_at,
            created_at=model.created_at,
        )


class ReviewRepository:
    """Repository for Review entity"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, review: Review) -> Review:
        """Create a new review"""
        model = ReviewModel(
            id=review.id,
            document_id=review.document_id,
            reviewed_by=review.reviewed_by,
            corrections=review.corrections,
            review_status=review.review_status.value,
            review_notes=review.review_notes,
            reviewed_at=review.reviewed_at,
            created_at=review.created_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_entity(model)
    
    def get_by_document_id(self, document_id: UUID) -> Optional[Review]:
        """Get review by document ID"""
        model = self.session.query(ReviewModel).filter(
            ReviewModel.document_id == document_id
        ).first()
        return self._to_entity(model) if model else None
    
    def update(self, review: Review) -> Review:
        """Update review"""
        model = self.session.query(ReviewModel).filter(ReviewModel.id == review.id).first()
        if model:
            model.corrections = review.corrections
            model.review_status = review.review_status.value
            model.review_notes = review.review_notes
            model.reviewed_at = review.reviewed_at
            self.session.flush()
        return self._to_entity(model)
    
    def _to_entity(self, model: ReviewModel) -> Review:
        """Convert model to entity"""
        return Review(
            id=model.id,
            document_id=model.document_id,
            reviewed_by=model.reviewed_by,
            corrections=model.corrections,
            review_status=ReviewStatus(model.review_status),
            review_notes=model.review_notes,
            reviewed_at=model.reviewed_at,
            created_at=model.created_at,
        )


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
            created_at=model.performed_at,  # Use performed_at as created_at since model doesn't have created_at
        )


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


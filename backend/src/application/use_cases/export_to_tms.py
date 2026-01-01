from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any
import httpx
import os

from ...domain.entities.document import DocumentStatus
from ...domain.entities.export import Export, ExportStatus
from ...domain.entities.audit_trail import AuditTrail, AuditAction
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, ReviewRepository,
    ExportRepository, AuditTrailRepository
)
from ...application.dtos.export_dto import ExportCreateDTO, ExportDTO


class ExportToTMSUseCase:
    """Use case for exporting documents to TMS"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        extraction_repository: ExtractionRepository,
        review_repository: ReviewRepository,
        export_repository: ExportRepository,
        audit_trail_repository: AuditTrailRepository,
        tms_api_url: str = None,
        tms_api_key: str = None,
    ):
        self.document_repository = document_repository
        self.extraction_repository = extraction_repository
        self.review_repository = review_repository
        self.export_repository = export_repository
        self.audit_trail_repository = audit_trail_repository
        self.tms_api_url = tms_api_url or os.getenv("TMS_API_URL", "http://mock-tms:8080/api")
        self.tms_api_key = tms_api_key or os.getenv("TMS_API_KEY", "")
    
    def execute(self, document_id: UUID, export_data: ExportCreateDTO, exported_by: UUID) -> ExportDTO:
        """
        Export document to TMS.
        
        Args:
            document_id: Document ID
            export_data: Export configuration
            exported_by: User ID
        
        Returns:
            ExportDTO
        """
        # Get document
        document = self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Get extraction
        extraction = self.extraction_repository.get_by_document_id(document_id)
        if not extraction:
            raise ValueError(f"Extraction not found for document {document_id}")
        
        # Get review (if exists) - use corrections if available
        review = self.review_repository.get_by_document_id(document_id)
        data_to_export = extraction.structured_data.copy()
        if review and review.corrections:
            data_to_export.update(review.corrections)
        
        # Format export payload
        export_payload = self._format_export_payload(document, data_to_export)
        
        # Create export entity
        export = Export(
            id=uuid4(),
            document_id=document_id,
            exported_to=export_data.exported_to,
            export_payload=export_payload,
            export_status=ExportStatus.PENDING,
        )
        saved_export = self.export_repository.create(export)
        
        # Attempt export
        try:
            self._send_to_tms(export_payload, export_data.exported_to)
            saved_export.mark_success()
            self.export_repository.update(saved_export)
            
            # Update document status
            document.update_status(DocumentStatus.EXPORTED)
            self.document_repository.update(document)
        except Exception as e:
            saved_export.mark_failed(str(e))
            self.export_repository.update(saved_export)
            raise
        
        # Create audit trail
        audit_trail = AuditTrail(
            id=uuid4(),
            document_id=document_id,
            action=AuditAction.EXPORT,
            performed_by=exported_by,
            changes={"export_id": str(saved_export.id), "exported_to": export_data.exported_to},
        )
        self.audit_trail_repository.create(audit_trail)
        
        # Convert to DTO
        return ExportDTO(
            id=saved_export.id,
            document_id=saved_export.document_id,
            exported_to=saved_export.exported_to,
            export_payload=saved_export.export_payload,
            export_status=saved_export.export_status,
            exported_at=saved_export.exported_at,
            retry_count=saved_export.retry_count,
            error_message=saved_export.error_message,
        )
    
    def _format_export_payload(self, document, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for TMS export"""
        return {
            "document_id": str(document.id),
            "document_type": document.document_type.value if document.document_type else "UNKNOWN",
            "original_filename": document.original_filename,
            "data": data,
            "exported_at": datetime.utcnow().isoformat(),
        }
    
    def _send_to_tms(self, payload: Dict[str, Any], endpoint: str) -> None:
        """Send data to TMS API"""
        url = f"{self.tms_api_url}/{endpoint}"
        headers = {}
        if self.tms_api_key:
            headers["Authorization"] = f"Bearer {self.tms_api_key}"
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()


from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any

from ...domain.entities.document import DocumentStatus
from ...domain.entities.extraction import Extraction, ExtractionMethod
from ...domain.entities.audit_trail import AuditTrail, AuditAction
from ...domain.services.document_type_classifier import DocumentTypeClassifier
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, AuditTrailRepository
)
from ...infrastructure.external.ocr.base import OCRService
from ...infrastructure.external.llm.base import LLMService
from ...infrastructure.external.storage.base import StorageService
from ...application.dtos.extraction_dto import ExtractionDTO


class ExtractFieldsUseCase:
    """Use case for extracting fields from documents"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        extraction_repository: ExtractionRepository,
        audit_trail_repository: AuditTrailRepository,
        ocr_service: OCRService,
        llm_service: LLMService,
        storage_service: StorageService,
        document_type_classifier: DocumentTypeClassifier,
    ):
        self.document_repository = document_repository
        self.extraction_repository = extraction_repository
        self.audit_trail_repository = audit_trail_repository
        self.ocr_service = ocr_service
        self.llm_service = llm_service
        self.storage_service = storage_service
        self.document_type_classifier = document_type_classifier
    
    def execute(self, document_id: UUID) -> ExtractionDTO:
        """
        Extract fields from document.
        
        Args:
            document_id: Document ID
        
        Returns:
            ExtractionDTO
        """
        # Get document
        document = self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Update status to PROCESSING
        document.update_status(DocumentStatus.PROCESSING)
        self.document_repository.update(document)
        
        try:
            # Download file from storage
            file_bytes = self.storage_service.download_file(document.storage_path)
            
            # Run OCR
            ocr_result = self.ocr_service.extract_text_from_bytes(file_bytes, document.file_type)
            
            # Classify document type
            document_type = self.document_type_classifier.classify(
                ocr_result.text,
                {"filename": document.original_filename}
            )
            document.update_document_type(document_type)
            
            # Get extraction schema based on document type
            schema = self._get_extraction_schema(document_type.value)
            
            # Run LLM extraction
            llm_result = self.llm_service.extract_fields(
                ocr_result.text,
                document_type.value,
                schema
            )
            
            # Create extraction entity
            extraction = Extraction(
                id=uuid4(),
                document_id=document_id,
                extraction_method=ExtractionMethod.OCR_LLM,
                raw_text=ocr_result.text,
                structured_data=llm_result.structured_data,
                confidence_scores=llm_result.confidence_scores,
                extraction_metadata={
                    "ocr_provider": type(self.ocr_service).__name__,
                    "llm_provider": llm_result.metadata.get("provider"),
                    "llm_model": llm_result.metadata.get("model"),
                    **llm_result.metadata
                }
            )
            
            # Save extraction
            saved_extraction = self.extraction_repository.create(extraction)
            
            # Update document status
            document.update_status(DocumentStatus.EXTRACTED)
            self.document_repository.update(document)
            
            # Create audit trail
            audit_trail = AuditTrail(
                id=uuid4(),
                document_id=document_id,
                action=AuditAction.EXTRACT,
                performed_by=document.uploaded_by,  # System action
                changes={"extraction_id": str(saved_extraction.id)},
            )
            self.audit_trail_repository.create(audit_trail)
            
            # Convert to DTO
            return ExtractionDTO(
                id=saved_extraction.id,
                document_id=saved_extraction.document_id,
                extraction_method=saved_extraction.extraction_method,
                raw_text=saved_extraction.raw_text,
                structured_data=saved_extraction.structured_data,
                confidence_scores=saved_extraction.confidence_scores,
                extracted_at=saved_extraction.extracted_at,
                extraction_metadata=saved_extraction.extraction_metadata,
            )
        
        except Exception as e:
            # Update status to FAILED
            document.update_status(DocumentStatus.FAILED)
            self.document_repository.update(document)
            raise
    
    def _get_extraction_schema(self, document_type: str) -> Dict[str, Any]:
        """Get extraction schema for document type"""
        schemas = {
            "CMR": {
                "type": "object",
                "properties": {
                    "shipper_name": {"type": "string"},
                    "shipper_address": {"type": "string"},
                    "consignee_name": {"type": "string"},
                    "consignee_address": {"type": "string"},
                    "date_of_consignment": {"type": "string"},
                    "place_of_consignment": {"type": "string"},
                    "reference_number": {"type": "string"},
                    "goods_description": {"type": "string"},
                    "quantity": {"type": "string"},
                    "weight": {"type": "string"},
                }
            },
            "INVOICE": {
                "type": "object",
                "properties": {
                    "invoice_number": {"type": "string"},
                    "invoice_date": {"type": "string"},
                    "seller_name": {"type": "string"},
                    "buyer_name": {"type": "string"},
                    "total_amount": {"type": "string"},
                    "currency": {"type": "string"},
                    "tax_amount": {"type": "string"},
                    "items": {"type": "array"},
                }
            },
            "DELIVERY_NOTE": {
                "type": "object",
                "properties": {
                    "delivery_note_number": {"type": "string"},
                    "delivery_date": {"type": "string"},
                    "recipient_name": {"type": "string"},
                    "recipient_address": {"type": "string"},
                    "items": {"type": "array"},
                }
            }
        }
        return schemas.get(document_type, {"type": "object", "properties": {}})


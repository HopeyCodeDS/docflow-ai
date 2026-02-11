from uuid import UUID, uuid4

from ...domain.entities.document import DocumentStatus
from ...domain.entities.validation_result import ValidationResult, ValidationStatus
from ...domain.services.validation_engine import ValidationEngine
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, ValidationResultRepository
)
from ...application.dtos.validation_dto import ValidationResultDTO


class ValidateDataUseCase:
    """Use case for validating extracted data"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        extraction_repository: ExtractionRepository,
        validation_result_repository: ValidationResultRepository,
        validation_engine: ValidationEngine,
    ):
        self.document_repository = document_repository
        self.extraction_repository = extraction_repository
        self.validation_result_repository = validation_result_repository
        self.validation_engine = validation_engine
    
    def execute(self, document_id: UUID) -> ValidationResultDTO:
        """
        Validate extracted data.
        
        Args:
            document_id: Document ID
        
        Returns:
            ValidationResultDTO
        """
        # Get document
        document = self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Get extraction
        extraction = self.extraction_repository.get_by_document_id(document_id)
        if not extraction:
            raise ValueError(f"Extraction not found for document {document_id}")
        
        # Run validation
        if not document.document_type:
            # If document type is unknown, skip validation or use a default
            errors = []
            status = ValidationStatus.PASSED
        else:
            errors = self.validation_engine.validate(
                document.document_type,
                extraction.structured_data
            )
            # Determine status
            status = self.validation_engine.get_validation_status(errors)
        
        # Create validation result
        # Convert ValidationError objects to dicts for the entity
        errors_dict = [{"field": e.field, "message": e.message, "severity": e.severity} for e in errors]

        # Delete any existing validation result for this extraction (dedup)
        self.validation_result_repository.delete_by_extraction_id(extraction.id)

        validation_result = ValidationResult(
            id=uuid4(),
            extraction_id=extraction.id,
            validation_rules={"document_type": document.document_type.value if document.document_type else "UNKNOWN"},
            validation_status=status,
            validation_errors=errors_dict,
        )

        # Save validation result
        saved_result = self.validation_result_repository.create(validation_result)

        # Update document status to VALIDATED
        document.update_status(DocumentStatus.VALIDATED)
        self.document_repository.update(document)

        return ValidationResultDTO.from_entity(saved_result)


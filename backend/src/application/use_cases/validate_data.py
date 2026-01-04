from uuid import UUID, uuid4

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
        
        validation_result = ValidationResult(
            id=uuid4(),  # Generate proper UUID
            extraction_id=extraction.id,
            validation_rules={"document_type": document.document_type.value if document.document_type else "UNKNOWN"},
            validation_status=status,
            validation_errors=errors_dict,
        )
        
        # Save validation result
        saved_result = self.validation_result_repository.create(validation_result)
        
        # Convert to DTO
        # validation_errors are already dicts, so use them directly
        return ValidationResultDTO(
            id=saved_result.id,
            extraction_id=saved_result.extraction_id,
            validation_rules=saved_result.validation_rules,
            validation_status=saved_result.validation_status,
            validation_errors=saved_result.validation_errors or [],
            validated_at=saved_result.validated_at,
        )


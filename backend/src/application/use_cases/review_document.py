from uuid import UUID, uuid4
from typing import Dict, Any

from ...domain.entities.document import DocumentStatus
from ...domain.entities.review import Review, ReviewStatus
from ...domain.entities.validation_result import ValidationStatus
from ...domain.entities.audit_trail import AuditTrail, AuditAction
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, ReviewRepository,
    AuditTrailRepository, ValidationResultRepository,
)
from ...application.dtos.review_dto import ReviewCreateDTO, ReviewDTO


class ReviewDocumentUseCase:
    """Use case for reviewing and correcting documents"""

    def __init__(
        self,
        document_repository: DocumentRepository,
        extraction_repository: ExtractionRepository,
        review_repository: ReviewRepository,
        audit_trail_repository: AuditTrailRepository,
        validation_result_repository: ValidationResultRepository,
    ):
        self.document_repository = document_repository
        self.extraction_repository = extraction_repository
        self.review_repository = review_repository
        self.audit_trail_repository = audit_trail_repository
        self.validation_result_repository = validation_result_repository
    
    def execute(self, document_id: UUID, review_data: ReviewCreateDTO, reviewed_by: UUID) -> ReviewDTO:
        """
        Create or update review.
        
        Args:
            document_id: Document ID
            review_data: Review data with corrections
            reviewed_by: User ID
        
        Returns:
            ReviewDTO
        """
        # Get document
        document = self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Gate: validation must exist and not be FAILED
        extraction = self.extraction_repository.get_by_document_id(document_id)
        if not extraction:
            raise ValueError("No extraction found. Cannot review.")
        validation = self.validation_result_repository.get_by_extraction_id(extraction.id)
        if not validation:
            raise ValueError("Document has not been validated. Run validation first.")
        if validation.validation_status == ValidationStatus.FAILED:
            raise ValueError("Validation failed. Fix issues or reprocess before submitting a review.")

        # Check if review exists
        existing_review = self.review_repository.get_by_document_id(document_id)
        
        if existing_review:
            # Update existing review
            existing_review.corrections = review_data.corrections
            existing_review.review_notes = review_data.review_notes
            existing_review.review_status = ReviewStatus.PENDING
            saved_review = self.review_repository.update(existing_review)
        else:
            # Create new review
            review = Review(
                id=uuid4(),
                document_id=document_id,
                reviewed_by=reviewed_by,
                corrections=review_data.corrections,
                review_status=ReviewStatus.PENDING,
                review_notes=review_data.review_notes,
            )
            saved_review = self.review_repository.create(review)
        
        # Update document status
        document.update_status(DocumentStatus.REVIEWED)
        self.document_repository.update(document)
        
        # Create audit trail
        audit_trail = AuditTrail(
            id=uuid4(),
            document_id=document_id,
            action=AuditAction.REVIEW,
            performed_by=reviewed_by,
            changes={"corrections": review_data.corrections},
        )
        self.audit_trail_repository.create(audit_trail)
        
        return ReviewDTO.from_entity(saved_review)
    
    def approve(self, document_id: UUID, reviewed_by: UUID) -> ReviewDTO:
        """Approve review — marks pipeline as complete (EXPORTED)"""
        review = self.review_repository.get_by_document_id(document_id)
        if not review:
            raise ValueError(f"Review not found for document {document_id}")

        review.approve()
        saved_review = self.review_repository.update(review)

        # Pipeline complete
        document = self.document_repository.get_by_id(document_id)
        if document:
            document.update_status(DocumentStatus.EXPORTED)
            self.document_repository.update(document)

        audit_trail = AuditTrail(
            id=uuid4(),
            document_id=document_id,
            action=AuditAction.REVIEW,
            performed_by=reviewed_by,
            changes={"action": "approve"},
        )
        self.audit_trail_repository.create(audit_trail)

        return ReviewDTO.from_entity(saved_review)

    def reject(self, document_id: UUID, reviewed_by: UUID, rejection_notes: str = "") -> ReviewDTO:
        """Reject review — user can re-edit and resubmit"""
        review = self.review_repository.get_by_document_id(document_id)
        if not review:
            raise ValueError(f"Review not found for document {document_id}")

        review.reject()
        if rejection_notes:
            review.review_notes = rejection_notes
        saved_review = self.review_repository.update(review)

        audit_trail = AuditTrail(
            id=uuid4(),
            document_id=document_id,
            action=AuditAction.REVIEW,
            performed_by=reviewed_by,
            changes={"action": "reject", "notes": rejection_notes},
        )
        self.audit_trail_repository.create(audit_trail)

        return ReviewDTO.from_entity(saved_review)


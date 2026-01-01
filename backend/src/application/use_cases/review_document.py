from uuid import UUID, uuid4
from typing import Dict, Any

from ...domain.entities.document import DocumentStatus
from ...domain.entities.review import Review, ReviewStatus
from ...domain.entities.audit_trail import AuditTrail, AuditAction
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ReviewRepository, AuditTrailRepository
)
from ...application.dtos.review_dto import ReviewCreateDTO, ReviewDTO


class ReviewDocumentUseCase:
    """Use case for reviewing and correcting documents"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        review_repository: ReviewRepository,
        audit_trail_repository: AuditTrailRepository,
    ):
        self.document_repository = document_repository
        self.review_repository = review_repository
        self.audit_trail_repository = audit_trail_repository
    
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
        
        # Convert to DTO
        return ReviewDTO(
            id=saved_review.id,
            document_id=saved_review.document_id,
            reviewed_by=saved_review.reviewed_by,
            corrections=saved_review.corrections,
            review_status=saved_review.review_status,
            review_notes=saved_review.review_notes,
            reviewed_at=saved_review.reviewed_at,
        )
    
    def approve(self, document_id: UUID, reviewed_by: UUID) -> ReviewDTO:
        """Approve review"""
        review = self.review_repository.get_by_document_id(document_id)
        if not review:
            raise ValueError(f"Review not found for document {document_id}")
        
        review.approve()
        saved_review = self.review_repository.update(review)
        
        # Update document status
        document = self.document_repository.get_by_id(document_id)
        if document:
            document.update_status(DocumentStatus.REVIEWED)
            self.document_repository.update(document)
        
        return ReviewDTO(
            id=saved_review.id,
            document_id=saved_review.document_id,
            reviewed_by=saved_review.reviewed_by,
            corrections=saved_review.corrections,
            review_status=saved_review.review_status,
            review_notes=saved_review.review_notes,
            reviewed_at=saved_review.reviewed_at,
        )


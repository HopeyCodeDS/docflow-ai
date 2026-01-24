from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ....domain.entities.review import Review, ReviewStatus
from ..models import ReviewModel


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

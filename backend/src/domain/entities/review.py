from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class ReviewStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


class Review:
    """Review entity"""
    
    def __init__(
        self,
        id: UUID,
        document_id: UUID,
        reviewed_by: UUID,
        corrections: Dict[str, Any],
        review_status: ReviewStatus = ReviewStatus.PENDING,
        review_notes: Optional[str] = None,
        reviewed_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.document_id = document_id
        self.reviewed_by = reviewed_by
        self.corrections = corrections
        self.review_status = review_status
        self.review_notes = review_notes
        self.reviewed_at = reviewed_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
    
    def approve(self) -> None:
        """Approve the review"""
        self.review_status = ReviewStatus.APPROVED
        self.reviewed_at = datetime.utcnow()
    
    def reject(self) -> None:
        """Reject the review"""
        self.review_status = ReviewStatus.REJECTED
        self.reviewed_at = datetime.utcnow()


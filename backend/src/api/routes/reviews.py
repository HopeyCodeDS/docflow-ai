from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
import os

from ...application.use_cases.review_document import ReviewDocumentUseCase
from ...application.dtos.review_dto import ReviewCreateDTO, ReviewDTO
from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ReviewRepository, AuditTrailRepository
)
from ...api.middleware.auth import get_current_user

router = APIRouter()

database_url = os.getenv("DATABASE_URL", "postgresql://docflow:docflow@localhost:5432/docflow")
db = Database(database_url)


@router.get("/documents/{document_id}/review", response_model=ReviewDTO)
async def get_review(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get review for document"""
    session = db.get_session()
    try:
        review_repo = ReviewRepository(session)
        review = review_repo.get_by_document_id(document_id)
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return ReviewDTO(
            id=review.id,
            document_id=review.document_id,
            reviewed_by=review.reviewed_by,
            corrections=review.corrections,
            review_status=review.review_status,
            review_notes=review.review_notes,
            reviewed_at=review.reviewed_at,
        )
    finally:
        session.close()


@router.post("/documents/{document_id}/review", response_model=ReviewDTO)
async def create_review(
    document_id: UUID,
    review_data: ReviewCreateDTO,
    current_user: dict = Depends(get_current_user)
):
    """Create or update review"""
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        review_repo = ReviewRepository(session)
        audit_repo = AuditTrailRepository(session)
        
        use_case = ReviewDocumentUseCase(
            document_repository=document_repo,
            review_repository=review_repo,
            audit_trail_repository=audit_repo,
        )
        
        result = use_case.execute(document_id, review_data, current_user["id"])
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()


@router.patch("/documents/{document_id}/review", response_model=ReviewDTO)
async def update_review(
    document_id: UUID,
    review_data: ReviewCreateDTO,
    current_user: dict = Depends(get_current_user)
):
    """Update review"""
    return await create_review(document_id, review_data, current_user)


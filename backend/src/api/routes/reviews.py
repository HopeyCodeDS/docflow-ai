from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from ...application.use_cases.review_document import ReviewDocumentUseCase
from ...application.dtos.review_dto import ReviewCreateDTO, ReviewDTO
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, ReviewRepository,
    AuditTrailRepository, ValidationResultRepository,
)
from ...api.middleware.auth import get_current_user
from ...infrastructure.auth.rbac import get_permission_checker, Permission
from ...api.dependencies import get_db_session

router = APIRouter()


@router.get("/documents/{document_id}/review", response_model=ReviewDTO)
async def get_review(
    document_id: UUID,
    current_user: dict = Depends(get_permission_checker(Permission.VIEW)),
    session: Session = Depends(get_db_session),
):
    """Get review for document"""
    review_repo = ReviewRepository(session)
    review = review_repo.get_by_document_id(document_id)
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewDTO.from_entity(review)


@router.post("/documents/{document_id}/review", response_model=ReviewDTO)
async def create_review(
    document_id: UUID,
    review_data: ReviewCreateDTO,
    current_user: dict = Depends(get_permission_checker(Permission.REVIEW)),
    session: Session = Depends(get_db_session),
):
    """Create or update review"""
    try:
        document_repo = DocumentRepository(session)
        extraction_repo = ExtractionRepository(session)
        review_repo = ReviewRepository(session)
        audit_repo = AuditTrailRepository(session)
        validation_repo = ValidationResultRepository(session)

        use_case = ReviewDocumentUseCase(
            document_repository=document_repo,
            extraction_repository=extraction_repo,
            review_repository=review_repo,
            audit_trail_repository=audit_repo,
            validation_result_repository=validation_repo,
        )

        result = use_case.execute(document_id, review_data, current_user["id"])
        session.commit()
        return result
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/documents/{document_id}/review", response_model=ReviewDTO)
async def update_review(
    document_id: UUID,
    review_data: ReviewCreateDTO,
    current_user: dict = Depends(get_permission_checker(Permission.REVIEW)),
    session: Session = Depends(get_db_session),
):
    """Update review"""
    return await create_review(document_id, review_data, current_user, session)


def _build_review_use_case(session: Session) -> ReviewDocumentUseCase:
    """Helper to instantiate ReviewDocumentUseCase with all dependencies"""
    return ReviewDocumentUseCase(
        document_repository=DocumentRepository(session),
        extraction_repository=ExtractionRepository(session),
        review_repository=ReviewRepository(session),
        audit_trail_repository=AuditTrailRepository(session),
        validation_result_repository=ValidationResultRepository(session),
    )


@router.post("/documents/{document_id}/review/approve", response_model=ReviewDTO)
async def approve_review(
    document_id: UUID,
    current_user: dict = Depends(get_permission_checker(Permission.REVIEW)),
    session: Session = Depends(get_db_session),
):
    """Approve a review — marks pipeline as complete"""
    try:
        use_case = _build_review_use_case(session)
        result = use_case.approve(document_id, current_user["id"])
        session.commit()
        return result
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/documents/{document_id}/review/reject", response_model=ReviewDTO)
async def reject_review(
    document_id: UUID,
    current_user: dict = Depends(get_permission_checker(Permission.REVIEW)),
    session: Session = Depends(get_db_session),
):
    """Reject a review — allows user to re-edit and resubmit"""
    try:
        use_case = _build_review_use_case(session)
        result = use_case.reject(document_id, current_user["id"])
        session.commit()
        return result
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


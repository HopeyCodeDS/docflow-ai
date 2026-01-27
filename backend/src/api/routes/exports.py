from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from ...application.use_cases.export_to_tms import ExportToTMSUseCase
from ...application.dtos.export_dto import ExportCreateDTO, ExportDTO
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, ReviewRepository,
    ExportRepository, AuditTrailRepository,
)
from ...api.middleware.auth import get_current_user
from ...api.dependencies import get_db_session

router = APIRouter()


@router.post("/documents/{document_id}/export", response_model=ExportDTO)
async def create_export(
    document_id: UUID,
    export_data: ExportCreateDTO,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    """Export document to TMS"""
    try:
        document_repo = DocumentRepository(session)
        extraction_repo = ExtractionRepository(session)
        review_repo = ReviewRepository(session)
        export_repo = ExportRepository(session)
        audit_repo = AuditTrailRepository(session)
        
        use_case = ExportToTMSUseCase(
            document_repository=document_repo,
            extraction_repository=extraction_repo,
            review_repository=review_repo,
            export_repository=export_repo,
            audit_trail_repository=audit_repo,
        )
        
        result = use_case.execute(document_id, export_data, current_user["id"])
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/documents/{document_id}/export", response_model=ExportDTO)
async def get_export(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    """Get export status for document"""
    export_repo = ExportRepository(session)
    export = export_repo.get_by_document_id(document_id)
    
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    return ExportDTO.from_entity(export)


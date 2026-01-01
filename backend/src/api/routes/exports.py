from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
import os

from ...application.use_cases.export_to_tms import ExportToTMSUseCase
from ...application.dtos.export_dto import ExportCreateDTO, ExportDTO
from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, ReviewRepository,
    ExportRepository, AuditTrailRepository
)
from ...api.middleware.auth import get_current_user

router = APIRouter()

database_url = os.getenv("DATABASE_URL", "postgresql://docflow:docflow@localhost:5432/docflow")
db = Database(database_url)


@router.post("/documents/{document_id}/export", response_model=ExportDTO)
async def create_export(
    document_id: UUID,
    export_data: ExportCreateDTO,
    current_user: dict = Depends(get_current_user)
):
    """Export document to TMS"""
    session = db.get_session()
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
    finally:
        session.close()


@router.get("/documents/{document_id}/export", response_model=ExportDTO)
async def get_export(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get export status for document"""
    session = db.get_session()
    try:
        export_repo = ExportRepository(session)
        export = export_repo.get_by_document_id(document_id)
        
        if not export:
            raise HTTPException(status_code=404, detail="Export not found")
        
        return ExportDTO(
            id=export.id,
            document_id=export.document_id,
            exported_to=export.exported_to,
            export_payload=export.export_payload,
            export_status=export.export_status,
            exported_at=export.exported_at,
            retry_count=export.retry_count,
            error_message=export.error_message,
        )
    finally:
        session.close()


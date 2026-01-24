from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from ...application.use_cases.extract_fields import ExtractFieldsUseCase
from ...application.dtos.extraction_dto import ExtractionDTO
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, AuditTrailRepository,
)
from ...api.middleware.auth import get_current_user
from ...api.dependencies import (
    get_db_session,
    get_storage_service,
    get_ocr_service,
    get_llm_service,
    get_document_type_classifier,
)

router = APIRouter()


@router.get("/documents/{document_id}/extraction", response_model=ExtractionDTO)
async def get_extraction(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    """Get extraction result for document"""
    extraction_repo = ExtractionRepository(session)
    extraction = extraction_repo.get_by_document_id(document_id)
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    return ExtractionDTO.from_entity(extraction)


@router.post("/documents/{document_id}/extraction/retry")
async def retry_extraction(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
    storage_service=Depends(get_storage_service),
    ocr_service=Depends(get_ocr_service),
    llm_service=Depends(get_llm_service),
    document_type_classifier=Depends(get_document_type_classifier),
):
    """Retry extraction for document"""
    from ...infrastructure.monitoring.logging import get_logger
    logger = get_logger("docflow.api.extractions")
    
    try:
        logger.info("Extraction retry started", document_id=str(document_id))
        
        document_repo = DocumentRepository(session)
        extraction_repo = ExtractionRepository(session)
        audit_repo = AuditTrailRepository(session)
        
        use_case = ExtractFieldsUseCase(
            document_repository=document_repo,
            extraction_repository=extraction_repo,
            audit_trail_repository=audit_repo,
            ocr_service=ocr_service,
            llm_service=llm_service,
            storage_service=storage_service,
            document_type_classifier=document_type_classifier,
        )
        
        result = use_case.execute(document_id)
        session.commit()
        logger.info("Extraction retry successful", document_id=str(document_id))
        return result
    except Exception as e:
        session.rollback()
        import traceback
        error_detail = str(e) or repr(e)
        error_traceback = traceback.format_exc()
        logger.error("Extraction retry failed", error=error_detail, error_type=type(e).__name__, document_id=str(document_id), traceback=error_traceback)
        raise HTTPException(status_code=400, detail=error_detail or f"Extraction failed: {type(e).__name__}")


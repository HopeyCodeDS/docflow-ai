from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
import os

from ...application.use_cases.extract_fields import ExtractFieldsUseCase
from ...application.dtos.extraction_dto import ExtractionDTO
from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, AuditTrailRepository
)
from ...infrastructure.external.ocr.factory import OCRServiceFactory
from ...infrastructure.external.llm.factory import LLMServiceFactory
from ...infrastructure.external.storage.factory import StorageServiceFactory
from ...domain.services.document_type_classifier import DocumentTypeClassifier
from ...api.middleware.auth import get_current_user

router = APIRouter()

database_url = os.getenv("DATABASE_URL", "postgresql://docflow:docflow@localhost:5432/docflow")
db = Database(database_url)
ocr_service = OCRServiceFactory.create()
llm_service = LLMServiceFactory.create()
storage_service = StorageServiceFactory.create()
document_type_classifier = DocumentTypeClassifier()


@router.get("/documents/{document_id}/extraction", response_model=ExtractionDTO)
async def get_extraction(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get extraction result for document"""
    session = db.get_session()
    try:
        extraction_repo = ExtractionRepository(session)
        extraction = extraction_repo.get_by_document_id(document_id)
        
        if not extraction:
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        return ExtractionDTO(
            id=extraction.id,
            document_id=extraction.document_id,
            extraction_method=extraction.extraction_method,
            raw_text=extraction.raw_text,
            structured_data=extraction.structured_data,
            confidence_scores=extraction.confidence_scores,
            extracted_at=extraction.extracted_at,
            extraction_metadata=extraction.extraction_metadata,
        )
    finally:
        session.close()


@router.post("/documents/{document_id}/extraction/retry")
async def retry_extraction(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Retry extraction for document"""
    session = db.get_session()
    try:
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
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()


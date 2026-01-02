from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
import os

from ...application.use_cases.validate_data import ValidateDataUseCase
from ...application.dtos.validation_dto import ValidationResultDTO
from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.repositories import (
    DocumentRepository, ExtractionRepository, ValidationResultRepository
)
from ...domain.services.validation_engine import ValidationEngine
from ...api.middleware.auth import get_current_user

router = APIRouter()

database_url = os.getenv("DATABASE_URL", "postgresql://docflow:docflow@localhost:5432/docflow")
db = Database(database_url)
validation_engine = ValidationEngine()


@router.get("/documents/{document_id}/validation", response_model=ValidationResultDTO)
async def get_validation(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get validation result for document"""
    from ...infrastructure.monitoring.logging import get_logger
    logger = get_logger("docflow.api.validations")
    
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        extraction_repo = ExtractionRepository(session)
        validation_repo = ValidationResultRepository(session)
        
        # Check if extraction exists first
        extraction = extraction_repo.get_by_document_id(document_id)
        if not extraction:
            raise HTTPException(
                status_code=404, 
                detail="Extraction not found. Please extract the document first."
            )
        
        use_case = ValidateDataUseCase(
            document_repository=document_repo,
            extraction_repository=extraction_repo,
            validation_result_repository=validation_repo,
            validation_engine=validation_engine,
        )
        
        result = use_case.execute(document_id)
        session.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error("Validation failed", error=str(e), error_type=type(e).__name__, document_id=str(document_id))
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()


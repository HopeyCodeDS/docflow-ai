"""Use case for triggering extraction in the background (e.g. after document upload)."""
from uuid import UUID
import traceback

from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.repositories import (
    DocumentRepository,
    ExtractionRepository,
    AuditTrailRepository,
)
from ...infrastructure.external.ocr.base import OCRService
from ...infrastructure.external.llm.base import LLMService
from ...infrastructure.external.storage.base import StorageService
from ...domain.services.document_type_classifier import DocumentTypeClassifier
from .extract_fields import ExtractFieldsUseCase
from ...infrastructure.monitoring.logging import get_logger

logger = get_logger("sortex.application.trigger_extraction")


class TriggerExtractionUseCase:
    """Runs ExtractFieldsUseCase in a dedicated session for background execution."""

    def __init__(
        self,
        database: Database,
        storage_service: StorageService,
        ocr_service: OCRService,
        llm_service: LLMService,
        document_type_classifier: DocumentTypeClassifier,
    ):
        self.database = database
        self.storage_service = storage_service
        self.ocr_service = ocr_service
        self.llm_service = llm_service
        self.document_type_classifier = document_type_classifier

    def execute(self, document_id: UUID) -> None:
        """Run extraction for the given document. Manages its own session and commit/rollback/close."""
        session = self.database.get_session()
        try:
            document_repo = DocumentRepository(session)
            extraction_repo = ExtractionRepository(session)
            audit_repo = AuditTrailRepository(session)
            extract_uc = ExtractFieldsUseCase(
                document_repository=document_repo,
                extraction_repository=extraction_repo,
                audit_trail_repository=audit_repo,
                ocr_service=self.ocr_service,
                llm_service=self.llm_service,
                storage_service=self.storage_service,
                document_type_classifier=self.document_type_classifier,
            )
            extract_uc.execute(document_id)
            session.commit()
            logger.info("Extraction completed", document_id=str(document_id))
        except Exception as e:
            session.rollback()
            logger.error(
                "Background extraction failed",
                error=str(e),
                error_type=type(e).__name__,
                document_id=str(document_id),
                traceback=traceback.format_exc(),
            )
        finally:
            session.close()

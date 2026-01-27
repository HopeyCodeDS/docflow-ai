from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from uuid import UUID
import os
import threading

from ...application.use_cases.upload_document import UploadDocumentUseCase
from ...application.dtos.document_dto import DocumentDTO, DocumentListDTO
from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.repositories import DocumentRepository, AuditTrailRepository, ExtractionRepository
from ...infrastructure.external.storage.factory import StorageServiceFactory
from ...api.middleware.auth import get_current_user
from ...infrastructure.monitoring.logging import get_logger
from ...domain.entities.document import DocumentStatus

router = APIRouter()

database_url = os.getenv("DATABASE_URL", "postgresql://docflow:docflow@localhost:5432/docflow")
db = Database(database_url)
storage_service = StorageServiceFactory.create()


@router.post("/documents", response_model=DocumentDTO)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document"""
    logger = get_logger("docflow.api.documents")
    
    session = db.get_session()
    try:
        logger.info("Document upload started", filename=file.filename, user_id=str(current_user["id"]))
        
        document_repo = DocumentRepository(session)
        audit_repo = AuditTrailRepository(session)
        
        use_case = UploadDocumentUseCase(
            document_repository=document_repo,
            audit_trail_repository=audit_repo,
            storage_service=storage_service,
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "10")),
            allowed_file_types=os.getenv("ALLOWED_FILE_TYPES", "pdf,png,jpg,jpeg").split(",")
        )
        
        document = use_case.execute(file.file, file.filename, current_user["id"])
        session.commit()
        logger.info("Document upload successful", document_id=str(document.id))
        
        # Trigger extraction automatically in background
        try:
            from ...application.use_cases.extract_fields import ExtractFieldsUseCase
            from ...infrastructure.persistence.repositories import ExtractionRepository
            from ...infrastructure.external.ocr.factory import OCRServiceFactory
            from ...infrastructure.external.llm.factory import LLMServiceFactory
            from ...domain.services.document_type_classifier import DocumentTypeClassifier
            
            # Note: This will run synchronously for now, but could be made async with BackgroundTasks
            # For now, we'll trigger it but not wait for it to complete
            import threading
            
            def trigger_extraction():
                extraction_session = db.get_session()
                try:
                    extraction_doc_repo = DocumentRepository(extraction_session)
                    extraction_repo = ExtractionRepository(extraction_session)
                    extraction_audit_repo = AuditTrailRepository(extraction_session)
                    
                    extract_use_case = ExtractFieldsUseCase(
                        document_repository=extraction_doc_repo,
                        extraction_repository=extraction_repo,
                        audit_trail_repository=extraction_audit_repo,
                        ocr_service=OCRServiceFactory.create(),
                        llm_service=LLMServiceFactory.create(),
                        storage_service=storage_service,
                        document_type_classifier=DocumentTypeClassifier(),
                    )
                    
                    extract_use_case.execute(document.id)
                    extraction_session.commit()
                    logger.info("Extraction completed", document_id=str(document.id))
                except Exception as e:
                    extraction_session.rollback()
                    import traceback
                    error_traceback = traceback.format_exc()
                    logger.error("Background extraction failed", error=str(e), error_type=type(e).__name__, document_id=str(document.id), traceback=error_traceback)
                finally:
                    extraction_session.close()
            
            # Run extraction in background thread
            thread = threading.Thread(target=trigger_extraction, daemon=True)
            thread.start()
        except Exception as e:
            logger.warning("Failed to trigger background extraction", error=str(e), document_id=str(document.id))
        
        return document
    except Exception as e:
        session.rollback()
        logger.error("Document upload failed", error=str(e), error_type=type(e).__name__, filename=file.filename)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()


@router.get("/documents", response_model=DocumentListDTO)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List documents"""
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        status_enum = DocumentStatus(status) if status else None
        documents = document_repo.list(skip=skip, limit=limit, status=status_enum)
        
        dtos = [
            DocumentDTO(
                id=d.id,
                original_filename=d.original_filename,
                file_type=d.file_type,
                file_size=d.file_size,
                storage_path=d.storage_path,
                uploaded_at=d.uploaded_at,
                uploaded_by=d.uploaded_by,
                status=d.status,
                document_type=d.document_type,
                version=d.version,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in documents
        ]
        
        return DocumentListDTO(documents=dtos, total=len(dtos), page=skip // limit + 1, page_size=limit)
    finally:
        session.close()


@router.get("/documents/{document_id}", response_model=DocumentDTO)
async def get_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get document by ID"""
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        document = document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentDTO(
            id=document.id,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            storage_path=document.storage_path,
            uploaded_at=document.uploaded_at,
            uploaded_by=document.uploaded_by,
            status=document.status,
            document_type=document.document_type,
            version=document.version,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
    finally:
        session.close()


@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Start reprocessing (re-run extraction) for a document. Returns 202 Accepted; extraction runs in background."""
    logger = get_logger("docflow.api.documents")
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        document = document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        document.update_status(DocumentStatus.PROCESSING)
        document_repo.update(document)
        session.commit()

        doc_id = document_id

        def trigger_extraction():
            extraction_session = db.get_session()
            try:
                from ...application.use_cases.extract_fields import ExtractFieldsUseCase
                from ...infrastructure.external.ocr.factory import OCRServiceFactory
                from ...infrastructure.external.llm.factory import LLMServiceFactory
                from ...domain.services.document_type_classifier import DocumentTypeClassifier

                extraction_doc_repo = DocumentRepository(extraction_session)
                extraction_repo = ExtractionRepository(extraction_session)
                extraction_audit_repo = AuditTrailRepository(extraction_session)
                extract_use_case = ExtractFieldsUseCase(
                    document_repository=extraction_doc_repo,
                    extraction_repository=extraction_repo,
                    audit_trail_repository=extraction_audit_repo,
                    ocr_service=OCRServiceFactory.create(),
                    llm_service=LLMServiceFactory.create(),
                    storage_service=storage_service,
                    document_type_classifier=DocumentTypeClassifier(),
                )
                extract_use_case.execute(doc_id)
                extraction_session.commit()
                logger.info("Reprocess extraction completed", document_id=str(doc_id))
            except Exception as e:
                extraction_session.rollback()
                import traceback
                logger.error(
                    "Reprocess extraction failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    document_id=str(doc_id),
                    traceback=traceback.format_exc(),
                )
            finally:
                extraction_session.close()

        thread = threading.Thread(target=trigger_extraction, daemon=True)
        thread.start()

        dto = DocumentDTO(
            id=document.id,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            storage_path=document.storage_path,
            uploaded_at=document.uploaded_at,
            uploaded_by=document.uploaded_by,
            status=document.status,
            document_type=document.document_type,
            version=document.version,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        return JSONResponse(status_code=202, content=dto.model_dump(mode="json"))
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error("Reprocess failed", error=str(e), error_type=type(e).__name__, document_id=str(document_id))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/documents/{document_id}/file")
async def download_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Download original document file"""
    from fastapi.responses import Response
    
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        document = document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_bytes = storage_service.download_file(document.storage_path)
        
        return Response(
            content=file_bytes,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={document.original_filename}"}
        )
    finally:
        session.close()


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete document"""
    logger = get_logger("docflow.api.documents")
    
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        document = document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from storage
        try:
            storage_service.delete_file(document.storage_path)
        except Exception as e:
            logger.warning("Failed to delete file from storage", error=str(e), storage_path=document.storage_path)
        
        # Delete document (cascade will handle related records)
        document_repo.delete(document_id)
        session.commit()
        
        logger.info("Document deleted", document_id=str(document_id), filename=document.original_filename)
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error("Failed to delete document", error=str(e), error_type=type(e).__name__, document_id=str(document_id))
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
    finally:
        session.close()


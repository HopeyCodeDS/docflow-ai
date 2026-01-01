from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from uuid import UUID
import os

from ...application.use_cases.upload_document import UploadDocumentUseCase
from ...application.dtos.document_dto import DocumentDTO, DocumentListDTO
from ...infrastructure.persistence.database import Database
from ...infrastructure.persistence.repositories import DocumentRepository, AuditTrailRepository
from ...infrastructure.external.storage.factory import StorageServiceFactory
from ...api.middleware.auth import get_current_user

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
    session = db.get_session()
    try:
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
        return document
    except Exception as e:
        session.rollback()
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
        from ...domain.entities.document import DocumentStatus
        
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
    session = db.get_session()
    try:
        document_repo = DocumentRepository(session)
        document = document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        storage_service.delete_file(document.storage_path)
        # Document will be deleted via cascade
        session.delete(session.query(DocumentRepository).filter_by(id=document_id).first())
        session.commit()
        return {"message": "Document deleted"}
    finally:
        session.close()


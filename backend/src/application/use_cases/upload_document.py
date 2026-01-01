from uuid import UUID, uuid4
from datetime import datetime
from typing import BinaryIO

from ...domain.entities.document import Document, DocumentStatus
from ...domain.entities.audit_trail import AuditTrail, AuditAction
from ...infrastructure.persistence.repositories import DocumentRepository, AuditTrailRepository
from ...infrastructure.external.storage.base import StorageService
from ...application.dtos.document_dto import DocumentDTO


class UploadDocumentUseCase:
    """Use case for uploading documents"""
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        audit_trail_repository: AuditTrailRepository,
        storage_service: StorageService,
        max_file_size_mb: int = 10,
        allowed_file_types: list = None
    ):
        self.document_repository = document_repository
        self.audit_trail_repository = audit_trail_repository
        self.storage_service = storage_service
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.allowed_file_types = allowed_file_types or ["pdf", "png", "jpg", "jpeg"]
    
    def execute(self, file: BinaryIO, filename: str, uploaded_by: UUID) -> DocumentDTO:
        """
        Upload a document.
        
        Args:
            file: File object
            filename: Original filename
            uploaded_by: User ID
        
        Returns:
            DocumentDTO
        """
        # Validate file
        file_bytes = file.read()
        file.seek(0)  # Reset file pointer
        
        # Validate file size
        if len(file_bytes) > self.max_file_size:
            raise ValueError(f"File size exceeds maximum of {self.max_file_size / (1024*1024)}MB")
        
        # Validate file type
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if file_ext not in self.allowed_file_types:
            raise ValueError(f"File type '{file_ext}' not allowed. Allowed types: {', '.join(self.allowed_file_types)}")
        
        # Generate storage path
        document_id = uuid4()
        storage_path = f"{document_id}/{filename}"
        
        # Upload to storage
        self.storage_service.upload_file(storage_path, file_bytes)
        
        # Create document entity
        document = Document(
            id=document_id,
            original_filename=filename,
            file_type=file_ext,
            file_size=len(file_bytes),
            storage_path=storage_path,
            uploaded_by=uploaded_by,
            status=DocumentStatus.UPLOADED,
        )
        
        # Save document
        saved_document = self.document_repository.create(document)
        
        # Create audit trail
        audit_trail = AuditTrail(
            id=uuid4(),
            document_id=document_id,
            action=AuditAction.UPLOAD,
            performed_by=uploaded_by,
            changes={"filename": filename, "file_size": len(file_bytes)},
        )
        self.audit_trail_repository.create(audit_trail)
        
        # Convert to DTO
        return DocumentDTO(
            id=saved_document.id,
            original_filename=saved_document.original_filename,
            file_type=saved_document.file_type,
            file_size=saved_document.file_size,
            storage_path=saved_document.storage_path,
            uploaded_at=saved_document.uploaded_at,
            uploaded_by=saved_document.uploaded_by,
            status=saved_document.status,
            document_type=saved_document.document_type,
            version=saved_document.version,
            created_at=saved_document.created_at,
            updated_at=saved_document.updated_at,
        )


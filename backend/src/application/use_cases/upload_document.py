from uuid import UUID, uuid4
from datetime import datetime
from typing import BinaryIO
import re

from ...domain.entities.document import Document, DocumentStatus
from ...domain.entities.audit_trail import AuditTrail, AuditAction
from ...infrastructure.persistence.repositories import DocumentRepository, AuditTrailRepository
from ...infrastructure.external.storage.base import StorageService
from ...application.dtos.document_dto import DocumentDTO


# File signatures (magic bytes) for content validation
MAGIC_BYTES = {
    "pdf": [b"%PDF"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
}



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

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks.

        Args:
            filename: Original filename from upload

        Returns:
            Sanitized filename safe for storage

        Raises:
            ValueError: If filename is invalid after sanitization
        """
        # Remove path separators and parent directory references
        sanitized = filename.replace("\\", "/")
        sanitized = sanitized.split("/")[-1]  # Take only the filename part

        # Remove null bytes and other dangerous characters
        sanitized = sanitized.replace("\x00", "")

        # Remove leading dots (hidden files)
        sanitized = sanitized.lstrip(".")

        # Limit to safe characters: alphanumeric, dash, underscore, dot, space
        sanitized = re.sub(r'[^\w\-_\. ]', '_', sanitized)

        # Remove multiple consecutive dots or spaces
        sanitized = re.sub(r'\.{2,}', '.', sanitized)
        sanitized = re.sub(r' {2,}', ' ', sanitized)

        # Trim whitespace
        sanitized = sanitized.strip()

        if not sanitized or sanitized == '.':
            raise ValueError("Invalid filename")

        return sanitized

    def _validate_file_content(self, file_bytes: bytes, file_ext: str) -> bool:
        """
        Validate file content matches the claimed extension using magic bytes.

        Args:
            file_bytes: Raw file content
            file_ext: File extension (lowercase)

        Returns:
            True if content matches extension or extension is not in MAGIC_BYTES
        """
        if file_ext not in MAGIC_BYTES:
            return True  # Unknown type, skip validation

        expected_signatures = MAGIC_BYTES[file_ext]
        for sig in expected_signatures:
            if file_bytes.startswith(sig):
                return True
        return False

    def _deduplicate_filename(self, filename: str, uploaded_by: UUID) -> str:
        """
        If a document with the same filename already exists for this user,
        append a suffix like (2), (3), etc.

        Examples:
            invoice.pdf  -> invoice.pdf        (first upload)
            invoice.pdf  -> invoice (2).pdf    (second upload)
            invoice.pdf  -> invoice (3).pdf    (third upload)
        """
        # Split into base name and extension
        if '.' in filename:
            dot_idx = filename.rfind('.')
            base_name = filename[:dot_idx]
            extension = filename[dot_idx:]  # includes the dot, e.g. ".pdf"
        else:
            base_name = filename
            extension = ""

        # Strip any existing " (N)" suffix so re-uploads of deduped names stay clean
        stripped = re.sub(r' \(\d+\)$', '', base_name)

        # Count how many docs match this base name pattern for this user
        existing_count = self.document_repository.count_by_filename_prefix(
            stripped, extension, uploaded_by
        )

        if existing_count == 0:
            return filename  # No conflict

        return f"{stripped} ({existing_count + 1}){extension}"

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
        # Sanitize filename first to prevent path traversal
        filename = self._sanitize_filename(filename)

        # Validate file
        file_bytes = file.read()
        file.seek(0)  # Reset file pointer

        # Validate file size
        if len(file_bytes) > self.max_file_size:
            raise ValueError(f"File size exceeds maximum of {self.max_file_size / (1024*1024)}MB")

        # Validate file type by extension
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if file_ext not in self.allowed_file_types:
            raise ValueError(f"File type '{file_ext}' not allowed. Allowed types: {', '.join(self.allowed_file_types)}")

        # Validate file content matches extension (magic bytes check)
        if not self._validate_file_content(file_bytes, file_ext):
            raise ValueError(f"File content does not match extension '{file_ext}'. The file may be corrupted or misnamed.")

        # Deduplicate filename — append (2), (3), etc. if name already exists for this user
        filename = self._deduplicate_filename(filename, uploaded_by)

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
        
        return DocumentDTO.from_entity(saved_document)


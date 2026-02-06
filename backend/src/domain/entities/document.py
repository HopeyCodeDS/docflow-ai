from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    EXTRACTED = "EXTRACTED"
    VALIDATED = "VALIDATED"
    REVIEWED = "REVIEWED"
    EXPORTED = "EXPORTED"
    FAILED = "FAILED"


class DocumentType(str, Enum):
    CMR = "CMR"
    INVOICE = "INVOICE"
    DELIVERY_NOTE = "DELIVERY_NOTE"
    BILL_OF_LADING = "BILL_OF_LADING"
    AIR_WAYBILL = "AIR_WAYBILL"
    SEA_WAYBILL = "SEA_WAYBILL"
    PACKING_LIST = "PACKING_LIST"
    CUSTOMS_DECLARATION = "CUSTOMS_DECLARATION"
    CERTIFICATE_OF_ORIGIN = "CERTIFICATE_OF_ORIGIN"
    DANGEROUS_GOODS_DECLARATION = "DANGEROUS_GOODS_DECLARATION"
    FREIGHT_BILL = "FREIGHT_BILL"
    UNKNOWN = "UNKNOWN"


class Document:
    """Document aggregate root entity"""
    
    def __init__(
        self,
        id: UUID,
        original_filename: str,
        file_type: str,
        file_size: int,
        storage_path: str,
        uploaded_by: UUID,
        status: DocumentStatus = DocumentStatus.UPLOADED,
        document_type: Optional[DocumentType] = None,
        version: int = 1,
        uploaded_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.original_filename = original_filename
        self.file_type = file_type
        self.file_size = file_size
        self.storage_path = storage_path
        self.uploaded_by = uploaded_by
        self.status = status
        self.document_type = document_type or DocumentType.UNKNOWN
        self.version = version
        self.uploaded_at = uploaded_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_status(self, new_status: DocumentStatus) -> None:
        """Update document status"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def update_document_type(self, document_type: DocumentType) -> None:
        """Update document type"""
        self.document_type = document_type
        self.updated_at = datetime.utcnow()
    
    def increment_version(self) -> None:
        """Increment document version"""
        self.version += 1
        self.updated_at = datetime.utcnow()


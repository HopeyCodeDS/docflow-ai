from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class DocumentUploaded:
    """Domain event: Document uploaded"""
    document_id: UUID
    uploaded_by: UUID
    timestamp: datetime


@dataclass
class ExtractionCompleted:
    """Domain event: Extraction completed"""
    document_id: UUID
    extraction_id: UUID
    timestamp: datetime


@dataclass
class ValidationCompleted:
    """Domain event: Validation completed"""
    document_id: UUID
    validation_id: UUID
    status: str
    timestamp: datetime


@dataclass
class ReviewSubmitted:
    """Domain event: Review submitted"""
    document_id: UUID
    review_id: UUID
    reviewed_by: UUID
    timestamp: datetime


@dataclass
class ExportInitiated:
    """Domain event: Export initiated"""
    document_id: UUID
    export_id: UUID
    timestamp: datetime


@dataclass
class ExportCompleted:
    """Domain event: Export completed"""
    document_id: UUID
    export_id: UUID
    status: str
    timestamp: datetime


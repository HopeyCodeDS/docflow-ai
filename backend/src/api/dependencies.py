"""FastAPI dependencies for database session and shared services."""
import os
from typing import Generator

from sqlalchemy.orm import Session

from ..infrastructure.persistence.database import Database
from ..infrastructure.external.storage.factory import StorageServiceFactory
from ..infrastructure.external.storage.base import StorageService
from ..infrastructure.external.ocr.factory import OCRServiceFactory
from ..infrastructure.external.ocr.base import OCRService
from ..infrastructure.external.llm.factory import LLMServiceFactory
from ..infrastructure.external.llm.base import LLMService
from ..domain.services.document_type_classifier import DocumentTypeClassifier
from ..domain.services.validation_engine import ValidationEngine

_database = Database(os.getenv("DATABASE_URL", "postgresql://sortex:sortex@localhost:5432/sortex"))

_storage_service = StorageServiceFactory.create()
_ocr_service = OCRServiceFactory.create()
_llm_service = LLMServiceFactory.create()
_document_type_classifier = DocumentTypeClassifier()
_validation_engine = ValidationEngine()


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed after the request."""
    session = _database.get_session()
    try:
        yield session
    finally:
        session.close()


def get_database() -> Database:
    """Return the shared Database instance (e.g. for background tasks that need their own session)."""
    return _database


def get_storage_service() -> StorageService:
    return _storage_service


def get_ocr_service() -> OCRService:
    return _ocr_service


def get_llm_service() -> LLMService:
    return _llm_service


def get_document_type_classifier() -> DocumentTypeClassifier:
    return _document_type_classifier


def get_validation_engine() -> ValidationEngine:
    return _validation_engine

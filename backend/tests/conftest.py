"""Shared pytest fixtures for Sortex backend tests."""
import os

# Must be set before any application import touches jwt.py
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")

from unittest.mock import MagicMock, create_autospec
from uuid import uuid4

import pytest

from src.domain.entities.document import Document, DocumentStatus, DocumentType
from src.domain.entities.extraction import Extraction, ExtractionMethod
from src.domain.services.document_type_classifier import DocumentTypeClassifier
from src.domain.services.validation_engine import ValidationEngine
from src.infrastructure.external.llm.base import LLMExtractionResult, LLMService
from src.infrastructure.external.ocr.base import OCRResult, OCRService
from src.infrastructure.external.storage.base import StorageService
from src.infrastructure.persistence.repositories import (
    AuditTrailRepository,
    DocumentRepository,
    ExtractionRepository,
)


# ---------------------------------------------------------------------------
# Domain service fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def classifier():
    return DocumentTypeClassifier()


@pytest.fixture
def validation_engine():
    return ValidationEngine()


# ---------------------------------------------------------------------------
# Mock infrastructure fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_document_repo():
    return create_autospec(DocumentRepository, instance=True)


@pytest.fixture
def mock_extraction_repo():
    return create_autospec(ExtractionRepository, instance=True)


@pytest.fixture
def mock_audit_repo():
    return create_autospec(AuditTrailRepository, instance=True)


@pytest.fixture
def mock_ocr_service():
    return create_autospec(OCRService, instance=True)


@pytest.fixture
def mock_llm_service():
    return create_autospec(LLMService, instance=True)


@pytest.fixture
def mock_storage_service():
    return create_autospec(StorageService, instance=True)


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_document():
    """A fresh Document entity in UPLOADED state."""
    return Document(
        id=uuid4(),
        original_filename="test_cmr.pdf",
        file_type="pdf",
        file_size=1024,
        storage_path="uploads/test_cmr.pdf",
        uploaded_by=uuid4(),
    )


@pytest.fixture
def sample_extraction(sample_document):
    """A basic Extraction entity linked to sample_document."""
    return Extraction(
        id=uuid4(),
        document_id=sample_document.id,
        extraction_method=ExtractionMethod.OCR_LLM,
        raw_text="Sample OCR text",
        structured_data={"shipper_name": "Acme Corp"},
        confidence_scores={"shipper_name": 0.92},
    )


@pytest.fixture
def sample_ocr_result():
    return OCRResult(
        text="CMR CONSIGNMENT NOTE\nShipper: Acme Corp\nConsignee: Beta Ltd\nDate: 2024-01-15",
        layout=[{"text": "CMR", "bbox": [0, 0, 100, 50]}],
        regions=[],
    )


@pytest.fixture
def sample_llm_result():
    return LLMExtractionResult(
        structured_data={
            "shipper_name": "Acme Corp",
            "consignee_name": "Beta Ltd",
            "date_of_consignment": "2024-01-15",
        },
        confidence_scores={
            "shipper_name": 0.95,
            "consignee_name": 0.90,
            "date_of_consignment": 0.85,
        },
        metadata={"provider": "ollama", "model": "qwen2.5:3b"},
    )

"""Tests for ExtractFieldsUseCase — mock OCR/LLM/storage, verify status transitions and audit trail."""
from unittest.mock import MagicMock, patch, create_autospec
from uuid import uuid4

import pytest

from src.application.use_cases.extract_fields import ExtractFieldsUseCase
from src.domain.entities.document import Document, DocumentStatus, DocumentType
from src.domain.entities.extraction import ExtractionMethod
from src.domain.services.document_type_classifier import DocumentTypeClassifier
from src.domain.value_objects.classification_result import ClassificationResult
from src.infrastructure.external.llm.base import LLMExtractionResult
from src.infrastructure.external.ocr.base import OCRResult


@pytest.fixture
def use_case(
    mock_document_repo,
    mock_extraction_repo,
    mock_audit_repo,
    mock_ocr_service,
    mock_llm_service,
    mock_storage_service,
    classifier,
):
    return ExtractFieldsUseCase(
        document_repository=mock_document_repo,
        extraction_repository=mock_extraction_repo,
        audit_trail_repository=mock_audit_repo,
        ocr_service=mock_ocr_service,
        llm_service=mock_llm_service,
        storage_service=mock_storage_service,
        document_type_classifier=classifier,
    )


def _setup_happy_path(
    mock_document_repo,
    mock_extraction_repo,
    mock_storage_service,
    mock_ocr_service,
    mock_llm_service,
    sample_document,
    sample_ocr_result,
    sample_llm_result,
):
    """Wire up mocks for a successful extraction."""
    mock_document_repo.get_by_id.return_value = sample_document
    mock_storage_service.download_file.return_value = b"%PDF-fake"
    mock_ocr_service.extract_text_from_bytes.return_value = sample_ocr_result
    mock_llm_service.extract_fields.return_value = sample_llm_result
    mock_extraction_repo.create.side_effect = lambda e: e  # return what was passed


class TestHappyPath:

    def test_extraction_returns_dto(
        self,
        use_case,
        mock_document_repo,
        mock_extraction_repo,
        mock_storage_service,
        mock_ocr_service,
        mock_llm_service,
        sample_document,
        sample_ocr_result,
        sample_llm_result,
    ):
        _setup_happy_path(
            mock_document_repo,
            mock_extraction_repo,
            mock_storage_service,
            mock_ocr_service,
            mock_llm_service,
            sample_document,
            sample_ocr_result,
            sample_llm_result,
        )
        dto = use_case.execute(sample_document.id)
        assert dto is not None
        assert dto.extraction_method == ExtractionMethod.OCR_LLM

    def test_status_transitions_to_processing_then_extracted(
        self,
        use_case,
        mock_document_repo,
        mock_extraction_repo,
        mock_storage_service,
        mock_ocr_service,
        mock_llm_service,
        sample_document,
        sample_ocr_result,
        sample_llm_result,
    ):
        _setup_happy_path(
            mock_document_repo,
            mock_extraction_repo,
            mock_storage_service,
            mock_ocr_service,
            mock_llm_service,
            sample_document,
            sample_ocr_result,
            sample_llm_result,
        )
        use_case.execute(sample_document.id)

        # update should be called at least twice: PROCESSING and EXTRACTED
        update_calls = mock_document_repo.update.call_args_list
        assert len(update_calls) >= 2
        # Final status should be EXTRACTED
        assert sample_document.status == DocumentStatus.EXTRACTED

    def test_audit_trail_created(
        self,
        use_case,
        mock_document_repo,
        mock_extraction_repo,
        mock_audit_repo,
        mock_storage_service,
        mock_ocr_service,
        mock_llm_service,
        sample_document,
        sample_ocr_result,
        sample_llm_result,
    ):
        _setup_happy_path(
            mock_document_repo,
            mock_extraction_repo,
            mock_storage_service,
            mock_ocr_service,
            mock_llm_service,
            sample_document,
            sample_ocr_result,
            sample_llm_result,
        )
        use_case.execute(sample_document.id)
        mock_audit_repo.create.assert_called_once()

    def test_old_extractions_deleted_on_reprocess(
        self,
        use_case,
        mock_document_repo,
        mock_extraction_repo,
        mock_storage_service,
        mock_ocr_service,
        mock_llm_service,
        sample_document,
        sample_ocr_result,
        sample_llm_result,
    ):
        _setup_happy_path(
            mock_document_repo,
            mock_extraction_repo,
            mock_storage_service,
            mock_ocr_service,
            mock_llm_service,
            sample_document,
            sample_ocr_result,
            sample_llm_result,
        )
        use_case.execute(sample_document.id)
        mock_extraction_repo.delete_by_document_id.assert_called_once_with(sample_document.id)


class TestDocumentNotFound:

    def test_raises_value_error(self, use_case, mock_document_repo):
        mock_document_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            use_case.execute(uuid4())


class TestFailurePath:

    def test_status_set_to_failed_on_ocr_error(
        self,
        use_case,
        mock_document_repo,
        mock_storage_service,
        mock_ocr_service,
        sample_document,
    ):
        mock_document_repo.get_by_id.return_value = sample_document
        mock_storage_service.download_file.return_value = b"%PDF-fake"
        mock_ocr_service.extract_text_from_bytes.side_effect = RuntimeError("OCR crash")

        with pytest.raises(RuntimeError):
            use_case.execute(sample_document.id)

        assert sample_document.status == DocumentStatus.FAILED

    def test_llm_failure_creates_fallback_extraction(
        self,
        use_case,
        mock_document_repo,
        mock_extraction_repo,
        mock_storage_service,
        mock_ocr_service,
        mock_llm_service,
        sample_document,
        sample_ocr_result,
    ):
        """When LLM fails, extraction should still succeed with empty structured data."""
        mock_document_repo.get_by_id.return_value = sample_document
        mock_storage_service.download_file.return_value = b"%PDF-fake"
        mock_ocr_service.extract_text_from_bytes.return_value = sample_ocr_result
        mock_llm_service.extract_fields.side_effect = RuntimeError("LLM down")
        mock_extraction_repo.create.side_effect = lambda e: e

        dto = use_case.execute(sample_document.id)
        # Should still succeed with empty structured data
        assert dto is not None
        assert dto.structured_data == {}
        assert sample_document.status == DocumentStatus.EXTRACTED

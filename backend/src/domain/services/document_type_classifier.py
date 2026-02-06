from difflib import SequenceMatcher
from typing import Any, Dict, Optional

from ..entities.document import DocumentType
from ..value_objects.classification_result import ClassificationResult
from .classification_config import (
    CLASSIFICATION_PROFILES,
    CONFIDENT_THRESHOLD,
    UNCERTAIN_THRESHOLD,
    FUZZY_MATCH_THRESHOLD,
    FILENAME_BONUS,
)


class DocumentTypeClassifier:
    """Domain service for classifying document types using weighted scoring."""

    def __init__(self, fuzzy_threshold: float = FUZZY_MATCH_THRESHOLD):
        self._fuzzy_threshold = fuzzy_threshold
        self._keyword_index = self._build_keyword_index()

    def _build_keyword_index(self) -> Dict[str, list]:
        """Build a flat index: {doc_type: [(keyword_upper, weight), ...]} across all languages."""
        index: Dict[str, list] = {}
        for doc_type, profile in CLASSIFICATION_PROFILES.items():
            entries = []
            for _lang, keywords in profile.get("keywords", {}).items():
                for keyword_text, weight in keywords:
                    entries.append((keyword_text.upper(), weight))
            index[doc_type] = entries
        return index

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, content: str, metadata: Dict[str, Any] = None) -> DocumentType:
        """Backward-compatible classify that returns just DocumentType."""
        result = self.classify_with_confidence(content, metadata)
        return result.document_type

    def classify_with_confidence(
        self,
        content: str,
        metadata: Dict[str, Any] = None,
        llm_service=None,
    ) -> ClassificationResult:
        """
        Full classification with confidence scoring.

        Args:
            content: OCR-extracted text
            metadata: Optional dict with 'filename' key
            llm_service: Optional LLMService for fallback classification

        Returns:
            ClassificationResult with type, confidence, and method
        """
        metadata = metadata or {}
        content_upper = content.upper()

        # Phase 1: Keyword scoring
        keyword_scores = self._keyword_score(content_upper)

        # Phase 2: Filename scoring
        filename = metadata.get("filename", "")
        filename_scores = self._filename_score(filename.upper())

        # Phase 3: Combine and normalize
        combined = self._combine_scores(keyword_scores, filename_scores)
        normalized = self._normalize_scores(combined)

        # Phase 4: Select best match
        if not normalized:
            return self._unknown_result(normalized)

        sorted_types = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
        best_type, best_confidence = sorted_types[0]
        runner_up_type = sorted_types[1][0] if len(sorted_types) > 1 else None
        runner_up_confidence = sorted_types[1][1] if len(sorted_types) > 1 else 0.0

        # Phase 5: Confidence check and optional LLM fallback
        if best_confidence >= CONFIDENT_THRESHOLD:
            return ClassificationResult(
                document_type=DocumentType(best_type),
                confidence=round(best_confidence, 4),
                method="keyword_scoring",
                runner_up_type=DocumentType(runner_up_type) if runner_up_type else None,
                runner_up_confidence=round(runner_up_confidence, 4),
                all_scores=normalized,
            )

        if llm_service is not None and best_confidence >= UNCERTAIN_THRESHOLD:
            return self._llm_classify(content, llm_service, normalized)

        if best_confidence >= UNCERTAIN_THRESHOLD:
            return ClassificationResult(
                document_type=DocumentType(best_type),
                confidence=round(best_confidence, 4),
                method="keyword_scoring_uncertain",
                runner_up_type=DocumentType(runner_up_type) if runner_up_type else None,
                runner_up_confidence=round(runner_up_confidence, 4),
                all_scores=normalized,
            )

        return self._unknown_result(normalized)

    # ------------------------------------------------------------------
    # Scoring internals
    # ------------------------------------------------------------------

    def _keyword_score(self, content_upper: str) -> Dict[str, float]:
        """Score each document type by weighted keyword matches."""
        scores: Dict[str, float] = {}
        for doc_type, entries in self._keyword_index.items():
            total = 0.0
            for keyword, weight in entries:
                match_score = self._fuzzy_contains(content_upper, keyword)
                if match_score > 0:
                    total += weight * match_score
            # Bonus for exclusive keywords
            profile = CLASSIFICATION_PROFILES[doc_type]
            for exclusive in profile.get("exclusive_keywords", []):
                if exclusive.upper() in content_upper:
                    total *= 1.5
                    break  # Apply boost once
            if total > 0:
                scores[doc_type] = total
        return scores

    def _filename_score(self, filename_upper: str) -> Dict[str, float]:
        """Score each document type by filename hint matches."""
        scores: Dict[str, float] = {}
        if not filename_upper:
            return scores
        for doc_type, profile in CLASSIFICATION_PROFILES.items():
            for hint in profile.get("filename_hints", []):
                if hint.upper() in filename_upper:
                    scores[doc_type] = scores.get(doc_type, 0.0) + FILENAME_BONUS
        return scores

    def _combine_scores(
        self, keyword_scores: Dict[str, float], filename_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Merge keyword and filename scores."""
        combined: Dict[str, float] = dict(keyword_scores)
        for doc_type, score in filename_scores.items():
            combined[doc_type] = combined.get(doc_type, 0.0) + score
        return combined

    def _normalize_scores(self, raw_scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize raw scores to 0.0-1.0 range."""
        if not raw_scores:
            return {}
        max_score = max(raw_scores.values())
        if max_score == 0:
            return {}
        total = sum(raw_scores.values())
        normalized: Dict[str, float] = {}
        for doc_type, score in raw_scores.items():
            proportion = score / total
            dominance = score / max_score
            normalized[doc_type] = min(proportion * (dominance + 0.5), 1.0)
        return normalized

    def _fuzzy_contains(self, text: str, keyword: str) -> float:
        """
        Check if keyword is in text, with fuzzy matching for OCR errors.
        Returns 1.0 for exact match, 0.85-1.0 for fuzzy, 0.0 for no match.
        """
        if keyword in text:
            return 1.0

        klen = len(keyword)
        if klen < 4 or klen > len(text):
            return 0.0

        best_ratio = 0.0
        step = max(1, klen // 3)
        for i in range(0, len(text) - klen + 1, step):
            window = text[i : i + klen]
            ratio = SequenceMatcher(None, keyword, window).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                if ratio >= self._fuzzy_threshold:
                    return ratio

        return best_ratio if best_ratio >= self._fuzzy_threshold else 0.0

    # ------------------------------------------------------------------
    # LLM fallback
    # ------------------------------------------------------------------

    def _llm_classify(
        self, content: str, llm_service: Any, keyword_scores: Dict[str, float]
    ) -> ClassificationResult:
        """Use LLM to classify when keyword scoring is uncertain."""
        candidate_types = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        candidates_str = ", ".join([f"{t} ({s:.2f})" for t, s in candidate_types])
        all_types_str = ", ".join(CLASSIFICATION_PROFILES.keys())

        prompt = (
            f"Classify this logistics document into one of these types: {all_types_str}\n\n"
            f"Top keyword-matching candidates are: {candidates_str}\n\n"
            f"Document text (first 2000 chars):\n{content[:2000]}\n\n"
            'Return ONLY a JSON object: {"document_type": "TYPE_NAME", "confidence": 0.95, "reasoning": "brief explanation"}'
        )

        try:
            result = llm_service.extract_fields(
                prompt,
                "CLASSIFICATION",
                {
                    "type": "object",
                    "properties": {
                        "document_type": {"type": "string"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"},
                    },
                },
            )
            data = result.structured_data
            classified_type = data.get("document_type", "").upper().replace(" ", "_")

            try:
                doc_type = DocumentType(classified_type)
            except ValueError:
                doc_type = DocumentType.UNKNOWN

            llm_confidence = float(data.get("confidence", 0.5))
            return ClassificationResult(
                document_type=doc_type,
                confidence=min(round(llm_confidence, 4), 0.95),
                method="llm_fallback",
                all_scores=keyword_scores,
            )
        except Exception:
            if keyword_scores:
                best = max(keyword_scores, key=keyword_scores.get)
                return ClassificationResult(
                    document_type=DocumentType(best),
                    confidence=round(keyword_scores[best], 4),
                    method="keyword_scoring_llm_failed",
                    all_scores=keyword_scores,
                )
            return self._unknown_result(keyword_scores)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unknown_result(all_scores: Optional[Dict[str, float]] = None) -> ClassificationResult:
        return ClassificationResult(
            document_type=DocumentType.UNKNOWN,
            confidence=0.0,
            method="no_match",
            all_scores=all_scores or {},
        )

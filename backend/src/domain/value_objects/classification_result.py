from dataclasses import dataclass, field
from typing import Dict, Optional

from ..entities.document import DocumentType


@dataclass(frozen=True)
class ClassificationResult:
    """Value object representing the result of document classification."""

    document_type: DocumentType
    confidence: float
    method: str  # "keyword_scoring", "llm_fallback", "filename_hint", "keyword_scoring_uncertain"
    runner_up_type: Optional[DocumentType] = None
    runner_up_confidence: float = 0.0
    all_scores: Optional[Dict[str, float]] = field(default=None, repr=False)

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

    @property
    def is_confident(self) -> bool:
        """True if classification confidence exceeds the reliable threshold."""
        return self.confidence >= 0.6

    @property
    def needs_review(self) -> bool:
        """True if confidence is marginal and human review is recommended."""
        return 0.3 <= self.confidence < 0.6

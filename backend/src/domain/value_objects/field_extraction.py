from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FieldSource(str, Enum):
    OCR = "OCR"
    LLM = "LLM"
    MANUAL = "MANUAL"


@dataclass
class Coordinates:
    """Bounding box coordinates"""
    x: float
    y: float
    width: float
    height: float


@dataclass
class FieldExtraction:
    """Field extraction value object"""
    field_name: str
    value: str
    confidence: float  # 0.0 to 1.0
    source: FieldSource
    bounding_box: Optional[Coordinates] = None
    
    def __post_init__(self):
        """Validate confidence score"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


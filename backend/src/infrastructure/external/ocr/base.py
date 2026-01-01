from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any


class OCRResult:
    """OCR extraction result"""
    
    def __init__(self, text: str, layout: List[Dict[str, Any]] = None):
        self.text = text
        self.layout = layout or []  # List of text blocks with coordinates


class OCRService(ABC):
    """Abstract OCR service interface"""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> OCRResult:
        """
        Extract text from document.
        
        Args:
            file_path: Path to document file
        
        Returns:
            OCRResult with text and layout information
        """
        pass
    
    @abstractmethod
    def extract_text_from_bytes(self, file_bytes: bytes, file_type: str) -> OCRResult:
        """
        Extract text from document bytes.
        
        Args:
            file_bytes: Document file bytes
            file_type: File type (pdf, png, jpg, etc.)
        
        Returns:
            OCRResult with text and layout information
        """
        pass


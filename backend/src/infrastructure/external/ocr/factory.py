from typing import Optional
import os

from .base import OCRService
from .paddleocr_service import PaddleOCRService
from .tesseract_service import TesseractOCRService


class OCRServiceFactory:
    """Factory for creating OCR service instances"""
    
    @staticmethod
    def create(provider: Optional[str] = None) -> OCRService:
        """
        Create OCR service instance.
        
        Args:
            provider: Provider name ('paddleocr' or 'tesseract')
        
        Returns:
            OCRService instance
        """
        provider = provider or os.getenv("DEFAULT_OCR_PROVIDER", "paddleocr").lower()
        
        if provider == "paddleocr":
            return PaddleOCRService()
        elif provider == "tesseract":
            return TesseractOCRService()
        else:
            raise ValueError(f"Unknown OCR provider: {provider}")


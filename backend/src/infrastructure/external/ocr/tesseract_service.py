import io
from typing import Dict, Any, List
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract

from .base import OCRService, OCRResult


class TesseractOCRService(OCRService):
    """Tesseract OCR implementation"""
    
    def extract_text(self, file_path: str) -> OCRResult:
        """Extract text from file path"""
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        file_type = file_path.split('.')[-1].lower()
        return self.extract_text_from_bytes(file_bytes, file_type)
    
    def extract_text_from_bytes(self, file_bytes: bytes, file_type: str) -> OCRResult:
        """Extract text from bytes"""
        images = self._convert_to_images(file_bytes, file_type)
        
        all_text = []
        layout = []
        
        for img_idx, img in enumerate(images):
            # Extract text with layout
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            page_text = []
            page_layout = []
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:
                    page_text.append(text)
                    page_layout.append({
                        "text": text,
                        "confidence": float(data['conf'][i]) / 100.0 if data['conf'][i] != -1 else 0.0,
                        "bbox": {
                            "x": data['left'][i],
                            "y": data['top'][i],
                            "width": data['width'][i],
                            "height": data['height'][i]
                        },
                        "page": img_idx
                    })
            
            all_text.append(" ".join(page_text))
        
        full_text = "\n".join(all_text)
        return OCRResult(text=full_text, layout=layout)
    
    def _convert_to_images(self, file_bytes: bytes, file_type: str) -> List[Image.Image]:
        """Convert file bytes to PIL Images"""
        if file_type == 'pdf':
            return convert_from_bytes(file_bytes)
        elif file_type in ['png', 'jpg', 'jpeg']:
            return [Image.open(io.BytesIO(file_bytes))]
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


import io
import os
from typing import Dict, Any, List
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
from paddleocr import PaddleOCR

from .base import OCRService, OCRResult


class PaddleOCRService(OCRService):
    """PaddleOCR implementation"""
    
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
    
    def extract_text(self, file_path: str) -> OCRResult:
        """Extract text from file path"""
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        file_type = os.path.splitext(file_path)[1][1:].lower()
        return self.extract_text_from_bytes(file_bytes, file_type)
    
    def extract_text_from_bytes(self, file_bytes: bytes, file_type: str) -> OCRResult:
        """Extract text from bytes"""
        images = self._convert_to_images(file_bytes, file_type)
        
        all_text = []
        layout = []
        
        for img_idx, img in enumerate(images):
            # Convert PIL Image to numpy array for PaddleOCR
            if isinstance(img, Image.Image):
                img_array = np.array(img)
            else:
                img_array = img
            
            result = self.ocr.ocr(img_array, cls=True)
            
            page_text = []
            page_layout = []
            
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        try:
                            box = line[0]
                            text_info = line[1]
                            if isinstance(text_info, tuple) and len(text_info) >= 2:
                                text, confidence = text_info[0], text_info[1]
                            else:
                                text = str(text_info) if text_info else ""
                                confidence = 1.0
                            
                            if box and len(box) >= 4:
                                page_text.append(text)
                                page_layout.append({
                                    "text": text,
                                    "confidence": confidence,
                                    "bbox": {
                                        "x": box[0][0],
                                        "y": box[0][1],
                                        "width": box[2][0] - box[0][0],
                                        "height": box[2][1] - box[0][1]
                                    },
                                    "page": img_idx
                                })
                        except (ValueError, IndexError, TypeError) as e:
                            # Skip malformed lines
                            continue
            
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


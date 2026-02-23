import io
import logging
import os
from typing import Dict, Any, List
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
from paddleocr import PaddleOCR, PPStructure

from .base import OCRService, OCRResult

logger = logging.getLogger(__name__)


class PaddleOCRService(OCRService):
    """PaddleOCR PP-Structure implementation.

    Uses PP-Structure for layout-aware document understanding:
    detects titles, text blocks, tables (with HTML), figures, and lists.
    """

    def __init__(self):
        self.engine = PPStructure(
            show_log=False,
            lang='en',
            use_gpu=False,
            layout=True,
            table=True,
            ocr=True,
            recovery=False,
        )
        # Basic OCR as fallback when PP-Structure returns empty
        self._basic_ocr = None

    def _get_basic_ocr(self) -> PaddleOCR:
        """Lazy-load basic PaddleOCR for fallback."""
        if self._basic_ocr is None:
            self._basic_ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
        return self._basic_ocr

    def extract_text(self, file_path: str) -> OCRResult:
        """Extract text from file path"""
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        file_type = os.path.splitext(file_path)[1][1:].lower()
        return self.extract_text_from_bytes(file_bytes, file_type)

    def extract_text_from_bytes(self, file_bytes: bytes, file_type: str) -> OCRResult:
        """Extract text from bytes using PP-Structure"""
        images = self._convert_to_images(file_bytes, file_type)

        all_text: List[str] = []
        layout: List[Dict[str, Any]] = []
        regions: List[Dict[str, Any]] = []

        for page_idx, img in enumerate(images):
            if isinstance(img, Image.Image):
                # PP-Structure expects 3-channel RGB; convert RGBA/palette images
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_array = np.array(img)
            else:
                img_array = img
                # Handle numpy arrays with 4 channels (RGBA)
                if img_array.ndim == 3 and img_array.shape[2] == 4:
                    img_array = img_array[:, :, :3]

            try:
                result = self.engine(img_array)
            except Exception as e:
                logger.warning("PP-Structure failed on page %d: %s", page_idx, e)
                continue

            if not result:
                continue

            # Sort regions top-to-bottom by Y coordinate for reading order
            result.sort(key=lambda r: r.get("bbox", [0, 0, 0, 0])[1])

            page_text: List[str] = []

            for region in result:
                region_type = region.get("type", "Text")
                bbox_raw = region.get("bbox", [0, 0, 0, 0])
                res = region.get("res")

                # Normalise bbox to our standard format
                bbox = {
                    "x": float(bbox_raw[0]),
                    "y": float(bbox_raw[1]),
                    "width": float(bbox_raw[2] - bbox_raw[0]),
                    "height": float(bbox_raw[3] - bbox_raw[1]),
                }

                if region_type == "Table":
                    # Tables: res is a dict with 'html' key
                    html = ""
                    if isinstance(res, dict):
                        html = res.get("html", "")
                    regions.append({
                        "type": "table",
                        "bbox": bbox,
                        "page": page_idx,
                        "content": html,
                    })
                    # Extract plain text from table for backward compat
                    table_text = self._html_table_to_text(html)
                    if table_text:
                        page_text.append(table_text)

                elif region_type in ("Text", "Title", "List"):
                    # Text/Title/List: res is a list of OCR line results
                    block_texts: List[str] = []
                    if isinstance(res, list):
                        for line in res:
                            self._process_ocr_line(
                                line, page_idx, layout, block_texts
                            )
                    elif isinstance(res, tuple) and len(res) >= 2:
                        # Alternate format: (boxes, [(text, conf), ...])
                        for text_conf in res[1]:
                            if isinstance(text_conf, tuple) and len(text_conf) >= 2:
                                block_texts.append(text_conf[0])

                    block_content = " ".join(block_texts)
                    if block_content:
                        page_text.append(block_content)
                        regions.append({
                            "type": region_type.lower(),
                            "bbox": bbox,
                            "page": page_idx,
                            "content": block_content,
                        })

                elif region_type == "Figure":
                    regions.append({
                        "type": "figure",
                        "bbox": bbox,
                        "page": page_idx,
                        "content": "[Figure]",
                    })

            all_text.append(" ".join(page_text))

        full_text = "\n".join(all_text)

        # Fallback: if PP-Structure returned nothing, use basic PaddleOCR
        if not full_text.strip() and not regions:
            logger.info("PP-Structure returned empty results, falling back to basic PaddleOCR")
            return self._basic_ocr_fallback(images)

        return OCRResult(text=full_text, layout=layout, regions=regions)

    def _basic_ocr_fallback(self, images: List[Image.Image]) -> OCRResult:
        """Run basic PaddleOCR when PP-Structure returns empty."""
        ocr = self._get_basic_ocr()
        all_text: List[str] = []
        layout: List[Dict[str, Any]] = []

        for img_idx, img in enumerate(images):
            if isinstance(img, Image.Image):
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_array = np.array(img)
            else:
                img_array = img
                if img_array.ndim == 3 and img_array.shape[2] == 4:
                    img_array = img_array[:, :, :3]

            result = ocr.ocr(img_array, cls=True)

            page_text: List[str] = []
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
                                layout.append({
                                    "text": text,
                                    "confidence": confidence,
                                    "bbox": {
                                        "x": float(box[0][0]),
                                        "y": float(box[0][1]),
                                        "width": float(box[2][0] - box[0][0]),
                                        "height": float(box[2][1] - box[0][1]),
                                    },
                                    "page": img_idx,
                                })
                        except (ValueError, IndexError, TypeError):
                            continue

            all_text.append(" ".join(page_text))

        full_text = "\n".join(all_text)
        return OCRResult(text=full_text, layout=layout)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _process_ocr_line(
        line: Any,
        page_idx: int,
        layout: List[Dict[str, Any]],
        block_texts: List[str],
    ) -> None:
        """Extract text and bbox from a single OCR line result."""
        try:
            if isinstance(line, dict):
                text = line.get("text", "")
                confidence = line.get("confidence", 1.0)
                box = line.get("text_region", line.get("bbox"))
            elif isinstance(line, (list, tuple)) and len(line) >= 2:
                box = line[0]
                text_info = line[1]
                if isinstance(text_info, tuple) and len(text_info) >= 2:
                    text, confidence = text_info[0], text_info[1]
                else:
                    text = str(text_info) if text_info else ""
                    confidence = 1.0
            else:
                return

            if not text or not text.strip():
                return

            text = text.strip()
            block_texts.append(text)

            # Build layout entry with bbox
            if box and isinstance(box, (list, tuple)) and len(box) >= 4:
                if isinstance(box[0], (list, tuple)):
                    # Quad format: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                    layout.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": {
                            "x": float(box[0][0]),
                            "y": float(box[0][1]),
                            "width": float(box[2][0] - box[0][0]),
                            "height": float(box[2][1] - box[0][1]),
                        },
                        "page": page_idx,
                    })
                else:
                    # [x1, y1, x2, y2] format
                    layout.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": {
                            "x": float(box[0]),
                            "y": float(box[1]),
                            "width": float(box[2] - box[0]),
                            "height": float(box[3] - box[1]),
                        },
                        "page": page_idx,
                    })
        except (ValueError, IndexError, TypeError):
            pass

    @staticmethod
    def _html_table_to_text(html: str) -> str:
        """Convert HTML table to plain text rows for backward compat."""
        if not html:
            return ""
        import re
        # Strip tags, keep cell separators
        text = re.sub(r'</(td|th)>', ' | ', html)
        text = re.sub(r'</tr>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up whitespace
        lines = [line.strip().strip('|').strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

    @staticmethod
    def _convert_to_images(file_bytes: bytes, file_type: str) -> List[Image.Image]:
        """Convert file bytes to PIL Images"""
        if file_type == 'pdf':
            return convert_from_bytes(file_bytes)
        elif file_type in ['png', 'jpg', 'jpeg']:
            return [Image.open(io.BytesIO(file_bytes))]
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

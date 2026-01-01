import json
from typing import Dict, Any
import httpx

from .base import LLMService, LLMExtractionResult


class OllamaService(LLMService):
    """Ollama LLM implementation"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.base_url = base_url
        self.model = model
    
    def extract_fields(self, text: str, document_type: str, schema: Dict[str, Any]) -> LLMExtractionResult:
        """Extract structured fields using Ollama"""
        prompt = self._build_prompt(text, document_type, schema)
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            result = response.json()
        
        # Parse response
        response_text = result.get("response", "{}")
        try:
            result_json = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            result_json = {"data": {}, "confidence": {}}
        
        structured_data = result_json.get("data", {})
        confidence_scores = result_json.get("confidence", {})
        
        metadata = {
            "model": self.model,
            "provider": "ollama",
            "total_duration": result.get("total_duration", 0)
        }
        
        return LLMExtractionResult(
            structured_data=structured_data,
            confidence_scores=confidence_scores,
            metadata=metadata
        )
    
    def _build_prompt(self, text: str, document_type: str, schema: Dict[str, Any]) -> str:
        """Build extraction prompt"""
        schema_str = json.dumps(schema, indent=2)
        return f"""Extract structured data from the following {document_type} document text.

Document Text:
{text[:4000]}

Expected Schema:
{schema_str}

Return ONLY a valid JSON object with:
- "data": Object containing extracted fields matching the schema
- "confidence": Object with confidence scores (0.0-1.0) for each field

For missing fields, use null. For confidence, estimate based on clarity of the information in the text.

JSON:"""


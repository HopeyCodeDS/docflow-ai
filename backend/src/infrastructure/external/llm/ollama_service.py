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
        
        try:
            with httpx.Client(timeout=180.0) as client:
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
        except httpx.ConnectError as e:
            raise ValueError(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running? Error: {e}")
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            if "memory" in error_text.lower() or "system memory" in error_text.lower():
                raise ValueError(
                    f"Ollama model '{self.model}' requires more memory than available. "
                    f"Error: {error_text}. "
                    f"Try: (1) Increase Docker memory allocation, (2) Use a smaller model, or (3) Free up system memory."
                )
            raise ValueError(f"Ollama API error: {e.response.status_code} - {error_text}")
        except Exception as e:
            raise ValueError(f"Ollama request failed: {str(e)}")
        
        # Parse response
        response_text = result.get("response", "{}")
        if not response_text or response_text.strip() == "":
            raise ValueError("Ollama returned empty response")
        
        # Clean up response text (remove markdown code blocks if present)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()
        
        try:
            result_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Log the actual response for debugging
            error_msg = f"Ollama returned invalid JSON. Response preview: {response_text[:500]}. Error: {e}"
            raise ValueError(error_msg)
        
        structured_data = result_json.get("data", {})
        confidence_scores = result_json.get("confidence", {})
        
        # If structured_data is empty, try to extract from root level (some models return data at root)
        if not structured_data and isinstance(result_json, dict):
            # Check if fields are at root level
            schema_fields = schema.get("properties", {}).keys()
            if any(field in result_json for field in schema_fields):
                structured_data = {k: v for k, v in result_json.items() if k in schema_fields}
                # Remove data/confidence from structured_data if they exist
                structured_data.pop("data", None)
                structured_data.pop("confidence", None)
        
        metadata = {
            "model": self.model,
            "provider": "ollama",
            "total_duration": result.get("total_duration", 0),
            "raw_response_preview": response_text[:200] if response_text else None
        }
        
        return LLMExtractionResult(
            structured_data=structured_data,
            confidence_scores=confidence_scores,
            metadata=metadata
        )
    
    def _build_prompt(self, text: str, document_type: str, schema: Dict[str, Any]) -> str:
        """Build extraction prompt"""
        schema_str = json.dumps(schema, indent=2)
        fields_list = ", ".join(schema.get("properties", {}).keys())
        
        return f"""You are a document extraction assistant. Extract structured data from the following {document_type} document.

Document Text:
{text[:4000]}

Required Fields to Extract:
{fields_list}

Expected JSON Schema:
{schema_str}

Instructions:
1. Extract all available fields from the document text
2. For missing fields, use null
3. Return a JSON object with this exact structure:
{{
  "data": {{
    "field1": "extracted_value",
    "field2": "extracted_value",
    ...
  }},
  "confidence": {{
    "field1": 0.95,
    "field2": 0.90,
    ...
  }}
}}

Return ONLY valid JSON, no other text. Start with {{ and end with }}.

JSON:"""


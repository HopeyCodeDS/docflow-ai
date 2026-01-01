from typing import Optional
import os

from .base import LLMService
from .openai_service import OpenAIService
from .ollama_service import OllamaService


class LLMServiceFactory:
    """Factory for creating LLM service instances"""
    
    @staticmethod
    def create(provider: Optional[str] = None) -> LLMService:
        """
        Create LLM service instance.
        
        Args:
            provider: Provider name ('openai' or 'ollama')
        
        Returns:
            LLMService instance
        """
        provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            return OpenAIService(api_key=api_key)
        elif provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return OllamaService(base_url=base_url)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")


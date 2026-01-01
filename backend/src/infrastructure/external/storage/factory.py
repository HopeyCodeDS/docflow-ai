import os
from typing import Optional

from .base import StorageService
from .minio_service import MinIOStorageService


class StorageServiceFactory:
    """Factory for creating storage service instances"""
    
    @staticmethod
    def create(provider: Optional[str] = None) -> StorageService:
        """
        Create storage service instance.
        
        Args:
            provider: Provider name ('minio' or 's3')
        
        Returns:
            StorageService instance
        """
        provider = provider or os.getenv("STORAGE_PROVIDER", "minio").lower()
        
        if provider == "minio":
            endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
            bucket_name = os.getenv("MINIO_BUCKET_NAME", "documents")
            use_ssl = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
            
            return MinIOStorageService(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                bucket_name=bucket_name,
                use_ssl=use_ssl
            )
        else:
            raise ValueError(f"Unknown storage provider: {provider}")


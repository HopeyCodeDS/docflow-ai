from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    """Abstract storage service interface"""
    
    @abstractmethod
    def upload_file(self, file_path: str, file_data: bytes, content_type: str = None) -> str:
        """
        Upload file to storage.
        
        Args:
            file_path: Storage path/key
            file_data: File bytes
            content_type: MIME type
        
        Returns:
            Storage path/key
        """
        pass
    
    @abstractmethod
    def download_file(self, file_path: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            file_path: Storage path/key
        
        Returns:
            File bytes
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        """
        Delete file from storage.
        
        Args:
            file_path: Storage path/key
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path: Storage path/key
        
        Returns:
            True if file exists
        """
        pass


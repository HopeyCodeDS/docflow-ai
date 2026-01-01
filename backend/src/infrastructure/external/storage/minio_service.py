from io import BytesIO
from minio import Minio
from minio.error import S3Error

from .base import StorageService


class MinIOStorageService(StorageService):
    """MinIO S3-compatible storage implementation"""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str, use_ssl: bool = False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=use_ssl
        )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure bucket exists, create if not"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise Exception(f"Failed to create bucket: {e}")
    
    def upload_file(self, file_path: str, file_data: bytes, content_type: str = None) -> str:
        """Upload file to MinIO"""
        try:
            self.client.put_object(
                self.bucket_name,
                file_path,
                BytesIO(file_data),
                length=len(file_data),
                content_type=content_type or "application/octet-stream"
            )
            return file_path
        except S3Error as e:
            raise Exception(f"Failed to upload file: {e}")
    
    def download_file(self, file_path: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise Exception(f"Failed to download file: {e}")
    
    def delete_file(self, file_path: str) -> None:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, file_path)
        except S3Error as e:
            raise Exception(f"Failed to delete file: {e}")
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        try:
            self.client.stat_object(self.bucket_name, file_path)
            return True
        except S3Error:
            return False


"""
Azure Blob Storage Service

Provides document upload, download, and management functionality
using Azure Blob Storage with SAS token authentication.
"""

import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import BinaryIO, Optional

from azure.core.exceptions import AzureError
from azure.storage.blob import (
    BlobClient,
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
)

ALLOWED_CONTENT_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'text/plain',
    'text/csv',
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


class AzureBlobStorageService:
    """
    Service class for Azure Blob Storage operations.
    
    Handles document upload, download, deletion, and SAS token generation
    for the ConstructOS document management system.
    """
    
    def __init__(self):
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'constructos-documents')
        self.account_name = os.getenv('AZURE_STORAGE_ACCOUNT', '')
        self.account_key = os.getenv('AZURE_STORAGE_KEY', '')
        
        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
        elif self.account_name and self.account_key:
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=self.account_key
            )
        else:
            self.blob_service_client = None
    
    @property
    def is_configured(self) -> bool:
        """Check if Azure Blob Storage is properly configured."""
        return self.blob_service_client is not None
    
    def _get_container_client(self):
        """Get or create container client."""
        if not self.is_configured:
            raise ValueError("Azure Blob Storage is not configured")
        
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        
        if not container_client.exists():
            container_client.create_container()
        
        return container_client
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and security issues.
        
        - Removes path separators and parent directory references
        - Strips control characters
        - Normalizes to lowercase
        - Limits to single extension (prevents .pdf.exe attacks)
        - Limits length
        - Replaces spaces with underscores
        """
        filename = os.path.basename(filename)
        
        filename = filename.replace('..', '')
        filename = filename.replace('/', '').replace('\\', '')
        
        filename = re.sub(r'[<>:"|?*\x00-\x1f]', '', filename)
        
        filename = filename.lower()
        
        filename = filename.replace(' ', '_')
        
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            name = re.sub(r'\.+', '_', name)
            ext = re.sub(r'[^a-z0-9]', '', ext)[:10]
            filename = f"{name}.{ext}" if ext else name
        else:
            filename = re.sub(r'\.+', '_', filename)
        
        max_length = 200
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            if ext:
                filename = name[:max_length - len(ext)] + ext
            else:
                filename = filename[:max_length]
        
        filename = re.sub(r'[^a-z0-9._-]', '', filename)
        
        return filename or 'unnamed_file'
    
    def _validate_content_type(self, content_type: str) -> bool:
        """Check if content type is in the allowed list."""
        return content_type in ALLOWED_CONTENT_TYPES
    
    def _validate_file_size(self, file_data: BinaryIO) -> tuple[bool, int]:
        """
        Validate file size is within limits.
        
        Returns tuple of (is_valid, size_in_bytes)
        """
        file_data.seek(0, 2)
        file_size = file_data.tell()
        file_data.seek(0)
        
        return file_size <= MAX_FILE_SIZE_BYTES, file_size
    
    def _generate_blob_name(
        self, 
        filename: str, 
        project_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> str:
        """
        Generate a unique blob name with optional organization by project/category.
        
        Format: {project_id}/{category}/{uuid}_{filename}
        """
        parts = []
        
        safe_project_id = re.sub(r'[^a-zA-Z0-9_-]', '', project_id or '')
        safe_category = re.sub(r'[^a-zA-Z0-9_-]', '', category or '')
        
        if safe_project_id:
            parts.append(safe_project_id)
        else:
            parts.append('general')
        
        if safe_category:
            parts.append(safe_category)
        else:
            parts.append('uncategorized')
        
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = self._sanitize_filename(filename)
        parts.append(f"{unique_id}_{safe_filename}")
        
        return '/'.join(parts)
    
    def upload_document(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: str,
        project_id: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[dict] = None,
        skip_content_type_validation: bool = False
    ) -> dict:
        """
        Upload a document to Azure Blob Storage.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            content_type: MIME type of the file
            project_id: Optional project ID for organization
            category: Optional category for organization
            metadata: Optional metadata dictionary
            skip_content_type_validation: Skip content type check (use with caution)
        
        Returns:
            Dictionary with blob_name, url, size (in bytes), and content_type
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Azure Blob Storage is not configured',
                'error_code': 'NOT_CONFIGURED'
            }
        
        if not skip_content_type_validation and not self._validate_content_type(content_type):
            return {
                'success': False,
                'error': f'File type not allowed: {content_type}',
                'error_code': 'INVALID_CONTENT_TYPE'
            }
        
        is_valid_size, file_size = self._validate_file_size(file_data)
        if not is_valid_size:
            max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
            return {
                'success': False,
                'error': f'File too large. Maximum size is {max_mb:.0f}MB',
                'error_code': 'FILE_TOO_LARGE'
            }
        
        safe_filename = self._sanitize_filename(filename)
        
        try:
            blob_name = self._generate_blob_name(safe_filename, project_id, category)
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)
            
            content_settings = ContentSettings(content_type=content_type)
            
            blob_metadata = {
                'original_filename': safe_filename,
                'uploaded_at': datetime.now(timezone.utc).isoformat(),
            }
            
            if project_id:
                safe_project_id = re.sub(r'[^a-zA-Z0-9_-]', '', project_id)
                blob_metadata['project_id'] = safe_project_id
            if category:
                safe_category = re.sub(r'[^a-zA-Z0-9_-]', '', category)
                blob_metadata['category'] = safe_category
            if metadata:
                safe_metadata = {
                    re.sub(r'[^a-zA-Z0-9_-]', '', k): str(v)[:256]
                    for k, v in metadata.items()
                    if isinstance(k, str) and isinstance(v, (str, int, float))
                }
                blob_metadata.update(safe_metadata)
            
            file_data.seek(0)
            
            blob_client.upload_blob(
                file_data,
                overwrite=True,
                content_settings=content_settings,
                metadata=blob_metadata,
                length=file_size,
                max_concurrency=4
            )
            
            blob_url = blob_client.url
            if not blob_url.startswith('https://'):
                blob_url = blob_url.replace('http://', 'https://')
            
            return {
                'success': True,
                'blob_name': blob_name,
                'url': blob_url,
                'size': file_size,
                'content_type': content_type,
                'sanitized_filename': safe_filename
            }
            
        except AzureError as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'AZURE_ERROR'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'An unexpected error occurred during upload',
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def generate_sas_url(
        self,
        blob_name: str,
        expiry_minutes: int = 15,
        permissions: str = 'r'
    ) -> dict:
        """
        Generate a SAS URL for secure blob access.
        
        Args:
            blob_name: Name of the blob
            expiry_minutes: Minutes until the SAS token expires (default 15, max 60)
            permissions: Permission string ('r' for read only - write not allowed for downloads)
        
        Returns:
            Dictionary with success status and url or error
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Azure Blob Storage is not configured',
                'error_code': 'NOT_CONFIGURED'
            }
        
        if not self.account_key:
            return {
                'success': False,
                'error': 'Azure Blob Storage account key not configured',
                'error_code': 'NO_ACCOUNT_KEY'
            }
        
        expiry_minutes = min(max(1, expiry_minutes), 60)
        
        try:
            sas_permissions = BlobSasPermissions(read=True, write=False)
            
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=sas_permissions,
                expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            )
            
            blob_client = self._get_container_client().get_blob_client(blob_name)
            
            return {
                'success': True,
                'url': f"{blob_client.url}?{sas_token}",
                'expires_in_minutes': expiry_minutes
            }
            
        except AzureError as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'AZURE_ERROR'
            }
        except Exception:
            return {
                'success': False,
                'error': 'Failed to generate download URL',
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def download_document(self, blob_name: str) -> Optional[bytes]:
        """
        Download a document from Azure Blob Storage.
        
        Args:
            blob_name: Name of the blob to download
        
        Returns:
            File content as bytes or None if download fails
        """
        if not self.is_configured:
            return None
        
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)
            
            blob_data = blob_client.download_blob()
            return blob_data.readall()
            
        except AzureError:
            return None
    
    def delete_document(self, blob_name: str) -> bool:
        """
        Delete a document from Azure Blob Storage.
        
        Args:
            blob_name: Name of the blob to delete
        
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.is_configured:
            return False
        
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            return True
            
        except AzureError:
            return False
    
    def list_documents(
        self,
        prefix: Optional[str] = None,
        project_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> list:
        """
        List documents in the container.
        
        Args:
            prefix: Optional prefix filter
            project_id: Optional project ID filter
            category: Optional category filter
        
        Returns:
            List of blob properties dictionaries
        """
        if not self.is_configured:
            return []
        
        try:
            if not prefix and project_id:
                if category:
                    prefix = f"{project_id}/{category}/"
                else:
                    prefix = f"{project_id}/"
            
            container_client = self._get_container_client()
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            return [
                {
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.last_modified,
                    'content_type': blob.content_settings.content_type if blob.content_settings else None,
                    'metadata': blob.metadata
                }
                for blob in blobs
            ]
            
        except AzureError:
            return []
    
    def get_document_metadata(self, blob_name: str) -> Optional[dict]:
        """
        Get metadata for a specific document.
        
        Args:
            blob_name: Name of the blob
        
        Returns:
            Metadata dictionary or None if not found
        """
        if not self.is_configured:
            return None
        
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)
            properties = blob_client.get_blob_properties()
            
            return {
                'name': blob_name,
                'size': properties.size,
                'content_type': properties.content_settings.content_type,
                'created_on': properties.creation_time,
                'last_modified': properties.last_modified,
                'metadata': properties.metadata
            }
            
        except AzureError:
            return None


storage_service = AzureBlobStorageService()

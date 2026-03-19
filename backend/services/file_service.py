"""
File service - handles file upload and storage
"""

import os
import json
import csv
from typing import Tuple, Dict, List, Any
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import pandas as pd
from utils.helpers import (
    generate_dataset_id, generate_file_id, get_timestamp,
    ensure_directory, get_file_size_mb
)
from utils.validators import FileValidator
from backend.models.data_models import Dataset, Column


class FileService:
    """Service for handling file uploads and operations"""
    
    def __init__(self, upload_folder: str, max_file_size_bytes: int, allowed_extensions: set):
        """Initialize FileService
        
        Args:
            upload_folder: Directory for uploaded files
            max_file_size_bytes: Maximum file size in bytes
            allowed_extensions: Set of allowed file extensions
        """
        self.upload_folder = upload_folder
        self.max_file_size_bytes = max_file_size_bytes
        self.allowed_extensions = allowed_extensions
        ensure_directory(upload_folder)
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, str]:
        """Validate uploaded file
        
        Args:
            file: FileStorage object from request
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if not file or file.filename == '':
            return False, "No file selected"
        
        if not FileValidator.is_allowed_file(file.filename, self.allowed_extensions):
            return False, f"File type not allowed. Allowed: {', '.join(self.allowed_extensions)}"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > self.max_file_size_bytes:
            max_mb = self.max_file_size_bytes / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.0f} MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, "File is valid"
    
    def save_file(self, file: FileStorage) -> Tuple[bool, Dict[str, Any], str]:
        """Save uploaded file and extract metadata
        
        Args:
            file: FileStorage object from request
            
        Returns:
            Tuple of (success: bool, file_info: dict, message: str)
        """
        # Validate file
        is_valid, validation_message = self.validate_file(file)
        if not is_valid:
            return False, {}, validation_message
        
        try:
            # Secure filename and generate unique path
            filename = secure_filename(file.filename)
            file_id = generate_file_id()
            file_extension = FileValidator.get_file_extension(filename)
            
            # Create unique filename
            unique_filename = f"{file_id}.{file_extension}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            mime_type = file.content_type or 'application/octet-stream'
            
            # Extract metadata from file
            dataset_id = generate_dataset_id()
            metadata = self._extract_file_metadata(file_path, filename, file_id, dataset_id)
            
            file_info = {
                'file_id': file_id,
                'dataset_id': dataset_id,
                'original_filename': filename,
                'saved_filename': unique_filename,
                'file_path': file_path,
                'file_size': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'mime_type': mime_type,
                'upload_timestamp': get_timestamp(),
                **metadata
            }
            
            return True, file_info, "File uploaded successfully"
        
        except Exception as e:
            return False, {}, f"Error saving file: {str(e)}"
    
    def _extract_file_metadata(self, file_path: str, filename: str, file_id: str, dataset_id: str) -> Dict[str, Any]:
        """Extract metadata from uploaded file
        
        Args:
            file_path: Path to saved file
            filename: Original filename
            file_id: Generated file ID
            dataset_id: Generated dataset ID
            
        Returns:
            Dictionary with extracted metadata
        """
        try:
            extension = FileValidator.get_file_extension(filename).lower()
            
            if extension == 'csv':
                return self._extract_csv_metadata(file_path)
            elif extension == 'json':
                return self._extract_json_metadata(file_path)
            elif extension in ['xlsx', 'xls']:
                return self._extract_excel_metadata(file_path)
            else:
                return {
                    'row_count': 0,
                    'column_count': 0,
                    'columns': []
                }
        except Exception as e:
            return {
                'row_count': 0,
                'column_count': 0,
                'columns': [],
                'metadata_error': str(e)
            }
    
    def _extract_csv_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from CSV file"""
        try:
            df = pd.read_csv(file_path, nrows=1)
            
            # Count total rows (skip header)
            row_count = sum(1 for _ in open(file_path)) - 1
            
            columns = [
                {
                    'index': i,
                    'name': col,
                    'data_type': str(df[col].dtype)
                }
                for i, col in enumerate(df.columns)
            ]
            
            return {
                'row_count': max(row_count, 0),
                'column_count': len(df.columns),
                'columns': columns
            }
        except Exception as e:
            return {
                'row_count': 0,
                'column_count': 0,
                'columns': [],
                'error': str(e)
            }
    
    def _extract_json_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                rows = data
                first_row = rows[0] if rows else {}
            elif isinstance(data, dict):
                rows = data.get('data', []) if 'data' in data else []
                first_row = rows[0] if rows else {}
            else:
                return {'row_count': 0, 'column_count': 0, 'columns': []}
            
            columns = [
                {
                    'index': i,
                    'name': col,
                    'data_type': type(value).__name__
                }
                for i, (col, value) in enumerate(first_row.items())
            ] if first_row else []
            
            return {
                'row_count': len(rows),
                'column_count': len(columns),
                'columns': columns
            }
        except Exception as e:
            return {
                'row_count': 0,
                'column_count': 0,
                'columns': [],
                'error': str(e)
            }
    
    def _extract_excel_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from Excel file"""
        try:
            df = pd.read_excel(file_path, nrows=1)
            
            # Get total row count
            df_full = pd.read_excel(file_path)
            row_count = len(df_full)
            
            columns = [
                {
                    'index': i,
                    'name': col,
                    'data_type': str(df[col].dtype)
                }
                for i, col in enumerate(df.columns)
            ]
            
            return {
                'row_count': row_count,
                'column_count': len(df.columns),
                'columns': columns
            }
        except Exception as e:
            return {
                'row_count': 0,
                'column_count': 0,
                'columns': [],
                'error': str(e)
            }
    
    def load_file_data(self, file_path: str, nrows: int = None) -> Tuple[bool, Any, str]:
        """Load data from file
        
        Args:
            file_path: Path to file
            nrows: Limit number of rows (for preview)
            
        Returns:
            Tuple of (success: bool, data: Any, message: str)
        """
        try:
            extension = FileValidator.get_file_extension(file_path).lower()
            
            if extension == 'csv':
                df = pd.read_csv(file_path, nrows=nrows)
                return True, df, "CSV loaded successfully"
            
            elif extension == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data if isinstance(data, list) else data.get('data', []))
                if nrows:
                    df = df.head(nrows)
                return True, df, "JSON loaded successfully"
            
            elif extension in ['xlsx', 'xls']:
                df = pd.read_excel(file_path, nrows=nrows)
                return True, df, "Excel loaded successfully"
            
            else:
                return False, None, f"Unsupported file format: {extension}"
        
        except Exception as e:
            return False, None, f"Error loading file: {str(e)}"
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """Delete a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, "File deleted successfully"
            return False, "File not found"
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"

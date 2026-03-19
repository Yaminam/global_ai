"""
Helper utilities module
"""

import uuid
import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional


def generate_uuid() -> str:
    """Generate a unique UUID v4
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_job_id() -> str:
    """Generate a job ID with prefix
    
    Returns:
        Job ID string (job-uuid)
    """
    return f"job-{generate_uuid()}"


def generate_dataset_id() -> str:
    """Generate a dataset ID with prefix
    
    Returns:
        Dataset ID string (ds-uuid)
    """
    return f"ds-{generate_uuid()}"


def generate_file_id() -> str:
    """Generate a file ID with prefix
    
    Returns:
        File ID string (file-uuid)
    """
    return f"file-{generate_uuid()}"


def get_timestamp() -> str:
    """Get current timestamp in ISO 8601 format
    
    Returns:
        ISO 8601 timestamp string
    """
    return datetime.utcnow().isoformat() + 'Z'


def create_success_response(data: Any = None, message: Optional[str] = None, status_code: int = 200) -> Dict:
    """Create a standardized success response
    
    Args:
        data: Response data
        message: Optional message
        status_code: HTTP status code (not used, only for API compatibility)
        
    Returns:
        Response dictionary
    """
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    
    return response


def create_error_response(error: str, details: Optional[str] = None, error_code: Optional[str] = None, status_code: int = 400) -> Dict:
    """Create a standardized error response
    
    Args:
        error: Error message
        details: Optional detailed error message
        error_code: Optional error code
        status_code: HTTP status code (not used, only for API compatibility)
        
    Returns:
        Response dictionary
    """
    response = {
        'success': False,
        'error': error
    }
    if details:
        response['details'] = details
    if error_code:
        response['error_code'] = error_code
    
    return response


def ensure_directory(directory: str) -> bool:
    """Ensure directory exists, create if needed
    
    Args:
        directory: Path to directory
        
    Returns:
        True if directory exists or was created
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False


def save_json_file(data: Dict, filepath: str) -> Tuple[bool, str]:
    """Save data to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save file
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        directory = os.path.dirname(filepath)
        ensure_directory(directory)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, f"File saved to {filepath}"
    except Exception as e:
        return False, f"Error saving file: {str(e)}"


def load_json_file(filepath: str) -> Tuple[bool, Any, str]:
    """Load data from JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Tuple of (success: bool, data: Any, message: str)
    """
    try:
        if not os.path.exists(filepath):
            return False, None, f"File not found: {filepath}"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return True, data, "File loaded successfully"
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, None, f"Error loading file: {str(e)}"


def get_file_size_mb(filepath: str) -> float:
    """Get file size in megabytes
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in MB
    """
    try:
        if os.path.exists(filepath):
            return os.path.getsize(filepath) / (1024 * 1024)
        return 0
    except Exception:
        return 0


def safe_get(dictionary: Dict, key: str, default=None):
    """Safely get value from dictionary with default
    
    Args:
        dictionary: Dictionary to access
        key: Key to look up
        default: Default value if key not found
        
    Returns:
        Value at key or default
    """
    return dictionary.get(key, default) if isinstance(dictionary, dict) else default


def format_bytes(bytes_value: float) -> str:
    """Format bytes to human readable format
    
    Args:
        bytes_value: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

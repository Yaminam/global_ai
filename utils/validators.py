"""
Utility module for data validation using regex patterns
"""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime


class DataValidator:
    """Regex-based data validation utilities"""
    
    # Email pattern (RFC 5322 simplified)
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Phone pattern (US format, also accepts formats with - and ())
    PHONE_PATTERN = r'^(\+?1)?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    
    # Date patterns
    DATE_PATTERNS = {
        'YYYY-MM-DD': r'^\d{4}-\d{2}-\d{2}$',
        'DD-MM-YYYY': r'^\d{2}-\d{2}-\d{4}$',
        'MM/DD/YYYY': r'^\d{2}/\d{2}/\d{4}$',
    }
    
    # URL pattern
    URL_PATTERN = r'^https?://[^\s/$.?#].[^\s]*$'
    
    # Credit card pattern (basic)
    CREDIT_CARD_PATTERN = r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$'
    
    # Numeric patterns
    INTEGER_PATTERN = r'^-?\d+$'
    FLOAT_PATTERN = r'^-?\d+\.?\d*$'
    
    # Alphanumeric pattern
    ALPHANUMERIC_PATTERN = r'^[a-zA-Z0-9]+$'
    
    @staticmethod
    def is_email(value: str) -> bool:
        """Validate email address
        
        Args:
            value: Email string to validate
            
        Returns:
            True if valid email, False otherwise
        """
        if not isinstance(value, str):
            return False
        return bool(re.match(DataValidator.EMAIL_PATTERN, value.strip()))
    
    @staticmethod
    def is_phone(value: str) -> bool:
        """Validate phone number
        
        Args:
            value: Phone number string
            
        Returns:
            True if valid phone, False otherwise
        """
        if not isinstance(value, str):
            return False
        return bool(re.match(DataValidator.PHONE_PATTERN, value.strip()))
    
    @staticmethod
    def is_date(value: str, date_format: str = 'YYYY-MM-DD') -> bool:
        """Validate date string
        
        Args:
            value: Date string to validate
            date_format: Expected date format
            
        Returns:
            True if valid date, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        pattern = DataValidator.DATE_PATTERNS.get(date_format)
        if not pattern:
            return False
        
        # Check pattern match first
        if not re.match(pattern, value.strip()):
            return False
        
        # Try to parse the date
        try:
            if date_format == 'YYYY-MM-DD':
                datetime.strptime(value.strip(), '%Y-%m-%d')
            elif date_format == 'DD-MM-YYYY':
                datetime.strptime(value.strip(), '%d-%m-%Y')
            elif date_format == 'MM/DD/YYYY':
                datetime.strptime(value.strip(), '%m/%d/%Y')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_url(value: str) -> bool:
        """Validate URL
        
        Args:
            value: URL string to validate
            
        Returns:
            True if valid URL, False otherwise
        """
        if not isinstance(value, str):
            return False
        return bool(re.match(DataValidator.URL_PATTERN, value.strip()))
    
    @staticmethod
    def is_credit_card(value: str) -> bool:
        """Validate credit card number
        
        Args:
            value: Credit card string
            
        Returns:
            True if valid format, False otherwise
        """
        if not isinstance(value, str):
            return False
        return bool(re.match(DataValidator.CREDIT_CARD_PATTERN, value.strip()))
    
    @staticmethod
    def is_integer(value: Any) -> bool:
        """Check if value is an integer
        
        Args:
            value: Value to check
            
        Returns:
            True if integer or integer string, False otherwise
        """
        if isinstance(value, int):
            return True
        if isinstance(value, str):
            return bool(re.match(DataValidator.INTEGER_PATTERN, value.strip()))
        return False
    
    @staticmethod
    def is_float(value: Any) -> bool:
        """Check if value is a float
        
        Args:
            value: Value to check
            
        Returns:
            True if float or float string, False otherwise
        """
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value.strip())
                return True
            except ValueError:
                return False
        return False
    
    @staticmethod
    def is_alphanumeric(value: str) -> bool:
        """Check if value contains only alphanumeric characters
        
        Args:
            value: String to check
            
        Returns:
            True if alphanumeric, False otherwise
        """
        if not isinstance(value, str):
            return False
        return bool(re.match(DataValidator.ALPHANUMERIC_PATTERN, value.strip()))
    
    @staticmethod
    def validate_row(row: Dict[str, Any], rules: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validate a data row against validation rules
        
        Args:
            row: Dictionary representing a data row
            rules: Validation rules dict with format:
                   {
                       'column_name': {
                           'type': 'email|phone|date|integer|float|url',
                           'required': True/False
                       }
                   }
        
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []
        
        for column, rule in rules.items():
            value = row.get(column, '').strip() if isinstance(row.get(column), str) else row.get(column)
            
            # Check required field
            if rule.get('required', False) and not value:
                errors.append(f"'{column}' is required but missing")
                continue
            
            # Skip validation if field is empty and not required
            if not value and not rule.get('required', False):
                continue
            
            # Convert to string for validation
            str_value = str(value) if value is not None else ""
            
            # Validate by type
            validation_type = rule.get('type', 'string').lower()
            
            if validation_type == 'email' and not DataValidator.is_email(str_value):
                errors.append(f"'{column}' has invalid email format: {value}")
            
            elif validation_type == 'phone' and not DataValidator.is_phone(str_value):
                errors.append(f"'{column}' has invalid phone format: {value}")
            
            elif validation_type == 'date':
                date_format = rule.get('format', 'YYYY-MM-DD')
                if not DataValidator.is_date(str_value, date_format):
                    errors.append(f"'{column}' has invalid date format (expected {date_format}): {value}")
            
            elif validation_type == 'url' and not DataValidator.is_url(str_value):
                errors.append(f"'{column}' has invalid URL format: {value}")
            
            elif validation_type == 'integer' and not DataValidator.is_integer(str_value):
                errors.append(f"'{column}' is not an integer: {value}")
            
            elif validation_type == 'float' and not DataValidator.is_float(str_value):
                errors.append(f"'{column}' is not a number: {value}")
            
            elif validation_type == 'alphanumeric' and not DataValidator.is_alphanumeric(str_value):
                errors.append(f"'{column}' contains non-alphanumeric characters: {value}")
        
        return (len(errors) == 0, errors)


class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
        """Check if file extension is allowed
        
        Args:
            filename: Filename to check
            allowed_extensions: Set of allowed extensions (e.g., {'csv', 'json'})
            
        Returns:
            True if file is allowed, False otherwise
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Extract file extension
        
        Args:
            filename: Filename
            
        Returns:
            File extension (lowercase, without dot)
        """
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


class ContentValidator:
    """Content/data validation utilities"""
    
    @staticmethod
    def is_empty_value(value: Any) -> bool:
        """Check if value is empty/null
        
        Args:
            value: Value to check
            
        Returns:
            True if empty, False otherwise
        """
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False
    
    @staticmethod
    def content_length(data: str, max_length: int) -> bool:
        """Check if content length is within limit
        
        Args:
            data: String data
            max_length: Maximum allowed length
            
        Returns:
            True if within limit, False otherwise
        """
        return len(data) <= max_length

"""
Form validation module using Python regex
Demonstrates regex usage for name, email, phone, and password validation
"""
import re
from typing import Dict, Tuple, Optional


class FormValidator:
    """
    Validates user form fields using regex patterns
    Implements validation for: name, email, phone, password
    """

    # Regex patterns for validation
    PATTERNS = {
        'name': r'^[A-Za-z\s]{2,50}$',  # Letters and spaces, 2-50 chars
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # Standard email format
        'phone': r'^\+?[1-9]\d{9,14}$',  # International phone format
        'password': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'  # Strong password
    }

    @classmethod
    def validate_name(cls, name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate name using regex
        Returns: (is_valid, error_message)
        """
        if not name:
            return False, "Name is required"

        if not re.match(cls.PATTERNS['name'], name):
            return False, "Name must contain only letters and spaces (2-50 characters)"

        return True, None

    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email using regex
        Returns: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"

        if not re.match(cls.PATTERNS['email'], email):
            return False, "Invalid email format (e.g., user@example.com)"

        return True, None

    @classmethod
    def validate_phone(cls, phone: str) -> Tuple[bool, Optional[str]]:
        """
        Validate phone number using regex
        Returns: (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number is required"

        if not re.match(cls.PATTERNS['phone'], phone):
            return False, "Invalid phone format (10-15 digits, optionally starting with +)"

        return True, None

    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password using regex
        Must contain: uppercase, lowercase, digit, special char, min 8 chars
        Returns: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"

        if not re.match(cls.PATTERNS['password'], password):
            return False, ("Password must be at least 8 characters with: "
                          "uppercase, lowercase, digit, and special character")

        return True, None

    @classmethod
    def validate_form(cls, data: Dict[str, str]) -> Dict[str, any]:
        """
        Validate entire form
        Returns: {'valid': bool, 'errors': {field: error_msg}}
        """
        errors = {}

        # Validate name
        name_valid, name_error = cls.validate_name(data.get('name', ''))
        if not name_valid:
            errors['name'] = name_error

        # Validate email
        email_valid, email_error = cls.validate_email(data.get('email', ''))
        if not email_valid:
            errors['email'] = email_error

        # Validate phone
        phone_valid, phone_error = cls.validate_phone(data.get('phone', ''))
        if not phone_valid:
            errors['phone'] = phone_error

        # Validate password
        password_valid, password_error = cls.validate_password(data.get('password', ''))
        if not password_valid:
            errors['password'] = password_error

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

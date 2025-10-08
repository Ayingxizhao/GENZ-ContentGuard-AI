"""
Email and password validation utilities
Borrowed from common Flask/WTForms patterns
"""
import re


def validate_email(email):
    """
    Validate email format using regex
    Returns: (is_valid: bool, error_message: str or None)
    """
    if not email or not email.strip():
        return False, "Email is required"

    email = email.strip().lower()

    # Standard email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    if len(email) > 255:
        return False, "Email is too long (max 255 characters)"

    return True, None


def validate_password(password):
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number or special character

    Returns: (is_valid: bool, error_message: str or None)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"

    # Check for uppercase
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for lowercase
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for number or special character
    if not re.search(r'[0-9!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one number or special character"

    return True, None


def validate_name(name):
    """
    Validate user name (optional field)
    Returns: (is_valid: bool, error_message: str or None)
    """
    if not name:
        return True, None  # Name is optional

    name = name.strip()

    if len(name) > 255:
        return False, "Name is too long (max 255 characters)"

    if len(name) < 1:
        return False, "Name cannot be empty"

    return True, None

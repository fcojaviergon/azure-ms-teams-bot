"""Input validation utilities."""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """
    Sanitize user input.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace('\x00', '')

    # Truncate to max length
    text = text[:max_length]

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def validate_ariba_id(ariba_id: str) -> bool:
    """
    Validate SAP Ariba ID format.

    Args:
        ariba_id: Ariba ID to validate

    Returns:
        True if valid, False otherwise
    """
    # Ariba IDs typically follow patterns like: PR1234567, PO8901234, etc.
    pattern = r'^[A-Z]{2}\d{7,10}$'
    return bool(re.match(pattern, ariba_id))


def extract_ariba_ids(text: str) -> list[str]:
    """
    Extract Ariba IDs from text.

    Args:
        text: Text to search for Ariba IDs

    Returns:
        List of found Ariba IDs
    """
    pattern = r'\b[A-Z]{2}\d{7,10}\b'
    return re.findall(pattern, text)

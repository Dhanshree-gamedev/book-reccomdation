"""
Input Validation Module

Provides centralized validation functions for all user inputs.
Ensures data integrity and security across the application.
"""

import re
from typing import Tuple, List, Optional
from utils.constants import (
    MIN_USERNAME_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_RATING,
    MAX_RATING,
    GENRES,
)


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format and length.
    
    Rules:
    - Must be between MIN_USERNAME_LENGTH and MAX_USERNAME_LENGTH characters
    - Must contain only alphanumeric characters and underscores
    - Cannot start with a number
    
    Args:
        username: Username to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not username:
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {MIN_USERNAME_LENGTH} characters"
    
    if len(username) > MAX_USERNAME_LENGTH:
        return False, f"Username cannot exceed {MAX_USERNAME_LENGTH} characters"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, and underscores"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not email:
        return False, "Email is required"
    
    email = email.strip()
    
    # RFC 5322 compliant email regex (simplified)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Rules:
    - Must be between MIN_PASSWORD_LENGTH and MAX_PASSWORD_LENGTH characters
    - Must contain at least one uppercase letter
    - Must contain at least one lowercase letter
    - Must contain at least one digit
    
    Args:
        password: Password to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, ""


def validate_rating(rating: int) -> Tuple[bool, str]:
    """
    Validate rating is within acceptable range.
    
    Args:
        rating: Rating value to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not isinstance(rating, int):
        return False, "Rating must be an integer"
    
    if rating < MIN_RATING or rating > MAX_RATING:
        return False, f"Rating must be between {MIN_RATING} and {MAX_RATING}"
    
    return True, ""


def validate_book_title(title: str) -> Tuple[bool, str]:
    """
    Validate book title.
    
    Args:
        title: Book title to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not title:
        return False, "Book title is required"
    
    title = title.strip()
    
    if len(title) < 1:
        return False, "Book title cannot be empty"
    
    if len(title) > 500:
        return False, "Book title is too long (max 500 characters)"
    
    return True, ""


def validate_author(author: str) -> Tuple[bool, str]:
    """
    Validate author name.
    
    Args:
        author: Author name to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not author:
        return False, "Author name is required"
    
    author = author.strip()
    
    if len(author) < 1:
        return False, "Author name cannot be empty"
    
    if len(author) > 200:
        return False, "Author name is too long (max 200 characters)"
    
    return True, ""


def validate_genres(genres: List[str]) -> Tuple[bool, str]:
    """
    Validate genre selection.
    
    Args:
        genres: List of genres to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not genres:
        return False, "At least one genre is required"
    
    for genre in genres:
        if genre not in GENRES:
            return False, f"Invalid genre: {genre}"
    
    return True, ""


def normalize_string(value: str) -> str:
    """
    Normalize a string by stripping whitespace and converting to lowercase.
    
    Args:
        value: String to normalize.
        
    Returns:
        Normalized string.
    """
    if not value:
        return ""
    return value.strip().lower()


def normalize_title(title: str) -> str:
    """
    Normalize book title for comparison.
    Strips whitespace and converts to title case.
    
    Args:
        title: Book title to normalize.
        
    Returns:
        Normalized title.
    """
    if not title:
        return ""
    return " ".join(title.strip().split()).title()


def normalize_author(author: str) -> str:
    """
    Normalize author name for comparison.
    Strips whitespace and converts to title case.
    
    Args:
        author: Author name to normalize.
        
    Returns:
        Normalized author name.
    """
    if not author:
        return ""
    return " ".join(author.strip().split()).title()

"""
Password Hashing Module

Provides secure password hashing using bcrypt with automatic salt generation.
Uses constant-time comparison to prevent timing attacks.
"""

import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with automatic salt generation.
    
    Args:
        password: Plain text password to hash.
        
    Returns:
        Hashed password as a string.
        
    Raises:
        ValueError: If password is empty or None.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    logger.debug("Password hashed successfully")
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using constant-time comparison.
    
    This function is safe against timing attacks because bcrypt.checkpw
    uses constant-time comparison internally.
    
    Args:
        password: Plain text password to verify.
        hashed_password: Previously hashed password to compare against.
        
    Returns:
        True if password matches, False otherwise.
    """
    if not password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

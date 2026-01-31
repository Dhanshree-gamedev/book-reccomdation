"""
Authentication Module

Handles user registration, login, session management, and logout.
Uses bcrypt for password hashing and cryptographic tokens for sessions.
"""

import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

import database as db
from utils.hashing import hash_password, verify_password
from utils.validators import validate_username, validate_email, validate_password
from utils.constants import SESSION_EXPIRY_HOURS, SESSION_TOKEN_LENGTH

logger = logging.getLogger(__name__)


def register_user(username: str, email: str, password: str, 
                  interests: list = None) -> Tuple[bool, str, Optional[int]]:
    """
    Register a new user with validation and secure password hashing.
    
    Args:
        username: Desired username.
        email: User's email address.
        password: Plain text password (will be hashed).
        interests: Optional list of genre interests.
        
    Returns:
        Tuple of (success, message, user_id).
        user_id is None if registration failed.
    """
    # Validate inputs
    valid, error = validate_username(username)
    if not valid:
        return False, error, None
    
    valid, error = validate_email(email)
    if not valid:
        return False, error, None
    
    valid, error = validate_password(password)
    if not valid:
        return False, error, None
    
    # Hash password
    password_hash = hash_password(password)
    
    # Attempt to create user
    user_id = db.create_user(username, email, password_hash, interests or [])
    
    if user_id:
        logger.info(f"User registered successfully: {username}")
        return True, "Registration successful!", user_id
    else:
        # Generic message to prevent user enumeration
        logger.warning(f"Registration failed for: {username}")
        return False, "Username or email already exists", None


def login_user(username: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Authenticate user and create a session.
    
    Uses constant-time password comparison to prevent timing attacks.
    Returns generic error messages to prevent user enumeration.
    
    Args:
        username: User's username.
        password: User's password.
        
    Returns:
        Tuple of (success, message, session_token).
        session_token is None if login failed.
    """
    if not username or not password:
        return False, "Invalid credentials", None
    
    # Fetch user
    user = db.get_user_by_username(username)
    
    if not user:
        # Perform dummy password check to prevent timing attacks
        verify_password(password, "$2b$12$dummy.hash.for.timing.attack.prevention")
        logger.warning(f"Login attempt for non-existent user: {username}")
        return False, "Invalid credentials", None
    
    # Verify password (constant-time comparison via bcrypt)
    if not verify_password(password, user['password_hash']):
        logger.warning(f"Failed login attempt for user: {username}")
        return False, "Invalid credentials", None
    
    # Generate session token
    session_token = secrets.token_urlsafe(SESSION_TOKEN_LENGTH)
    expires_at = datetime.now() + timedelta(hours=SESSION_EXPIRY_HOURS)
    
    # Create session
    if db.create_session(user['id'], session_token, expires_at):
        logger.info(f"User logged in: {username}")
        return True, "Login successful!", session_token
    else:
        logger.error(f"Failed to create session for user: {username}")
        return False, "An error occurred. Please try again.", None


def validate_session(session_token: str) -> Optional[Dict[str, Any]]:
    """
    Validate a session token and return user info if valid.
    
    Cleans up expired sessions periodically.
    
    Args:
        session_token: Session token to validate.
        
    Returns:
        User dict if session is valid, None otherwise.
    """
    if not session_token:
        return None
    
    # Clean up expired sessions (lightweight, runs on each validation)
    db.cleanup_expired_sessions()
    
    # Get session
    session = db.get_session(session_token)
    
    if not session:
        return None
    
    # Get user info
    user = db.get_user_by_id(session['user_id'])
    
    return user


def logout_user(session_token: str) -> bool:
    """
    Logout user by deleting their session.
    
    Args:
        session_token: Session token to invalidate.
        
    Returns:
        True if logout successful.
    """
    if not session_token:
        return False
    
    success = db.delete_session(session_token)
    if success:
        logger.info("User logged out successfully")
    return success


def update_interests(user_id: int, interests: list) -> Tuple[bool, str]:
    """
    Update user's genre interests.
    
    Args:
        user_id: User ID.
        interests: New list of interests.
        
    Returns:
        Tuple of (success, message).
    """
    if not interests:
        return False, "Please select at least one interest"
    
    if db.update_user_interests(user_id, interests):
        logger.info(f"Updated interests for user {user_id}")
        return True, "Interests updated successfully!"
    else:
        return False, "Failed to update interests"

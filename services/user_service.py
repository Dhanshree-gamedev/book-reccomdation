"""
User Service Module

Business logic layer for user-related operations.
Provides a clean interface between the UI and data layers.
"""

import logging
from typing import Optional, Dict, Any, List

import database as db
from auth import register_user, login_user, logout_user, validate_session, update_interests

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user operations.
    
    Encapsulates all user-related business logic including
    registration, authentication, profile management, and
    retrieving user statistics.
    """
    
    @staticmethod
    def register(username: str, email: str, password: str, 
                 interests: List[str] = None) -> tuple:
        """
        Register a new user.
        
        Args:
            username: Desired username.
            email: User's email address.
            password: Plain text password.
            interests: Optional list of genre interests.
            
        Returns:
            Tuple of (success, message, user_id).
        """
        return register_user(username, email, password, interests)
    
    @staticmethod
    def login(username: str, password: str) -> tuple:
        """
        Authenticate user and create session.
        
        Args:
            username: User's username.
            password: User's password.
            
        Returns:
            Tuple of (success, message, session_token).
        """
        return login_user(username, password)
    
    @staticmethod
    def logout(session_token: str) -> bool:
        """
        Logout user by invalidating session.
        
        Args:
            session_token: Session token to invalidate.
            
        Returns:
            True if successful.
        """
        return logout_user(session_token)
    
    @staticmethod
    def get_current_user(session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user from session.
        
        Args:
            session_token: Session token.
            
        Returns:
            User dict if authenticated, None otherwise.
        """
        return validate_session(session_token)
    
    @staticmethod
    def update_user_interests(user_id: int, interests: List[str]) -> tuple:
        """
        Update user's genre interests.
        
        Args:
            user_id: User ID.
            interests: New list of interests.
            
        Returns:
            Tuple of (success, message).
        """
        return update_interests(user_id, interests)
    
    @staticmethod
    def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user profile with statistics.
        
        Args:
            user_id: User ID.
            
        Returns:
            User profile dict with stats.
        """
        user = db.get_user_by_id(user_id)
        if not user:
            return None
        
        # Get user's ratings
        ratings = db.get_user_ratings(user_id)
        
        return {
            **user,
            'total_ratings': len(ratings),
            'ratings': ratings
        }
    
    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """
        Get statistics for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            Dict with user statistics.
        """
        ratings = db.get_user_ratings(user_id)
        
        if not ratings:
            return {
                'total_ratings': 0,
                'average_rating': 0,
                'favorite_genres': []
            }
        
        # Calculate average rating given
        avg_rating = sum(r['rating'] for r in ratings) / len(ratings)
        
        # Calculate favorite genres based on high ratings
        genre_counts = {}
        for rating in ratings:
            if rating['rating'] >= 4:
                for genre in rating['genres']:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        favorite_genres = sorted(
            genre_counts.keys(),
            key=lambda g: genre_counts[g],
            reverse=True
        )[:5]
        
        return {
            'total_ratings': len(ratings),
            'average_rating': round(avg_rating, 2),
            'favorite_genres': favorite_genres
        }

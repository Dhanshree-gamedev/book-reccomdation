"""
Book Service Module

Business logic layer for book-related operations.
Handles book creation, retrieval, search, and rating management.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple

import database as db
from utils.validators import (
    validate_book_title,
    validate_author,
    validate_genres,
    validate_rating,
    normalize_title,
    normalize_author
)

logger = logging.getLogger(__name__)


class BookService:
    """
    Service class for book operations.
    
    Encapsulates all book-related business logic including
    creation, search, browsing, and rating management.
    """
    
    @staticmethod
    def add_book(title: str, author: str, genres: List[str],
                 description: str = "", added_by: int = None) -> Tuple[bool, str, Optional[int]]:
        """
        Add a new book with validation and normalization.
        
        Args:
            title: Book title.
            author: Author name.
            genres: List of genres.
            description: Optional description.
            added_by: User ID who is adding the book.
            
        Returns:
            Tuple of (success, message, book_id).
        """
        # Validate inputs
        valid, error = validate_book_title(title)
        if not valid:
            return False, error, None
        
        valid, error = validate_author(author)
        if not valid:
            return False, error, None
        
        valid, error = validate_genres(genres)
        if not valid:
            return False, error, None
        
        # Normalize inputs
        normalized_title = normalize_title(title)
        normalized_author = normalize_author(author)
        
        # Check for duplicates (case-insensitive)
        if db.check_book_exists(normalized_title, normalized_author):
            return False, f"'{normalized_title}' by {normalized_author} already exists", None
        
        # Create book
        book_id = db.create_book(
            normalized_title,
            normalized_author,
            genres,
            description.strip(),
            added_by
        )
        
        if book_id:
            logger.info(f"Book added: {normalized_title} by {normalized_author}")
            return True, "Book added successfully!", book_id
        else:
            return False, "Failed to add book", None
    
    @staticmethod
    def get_book(book_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a book by ID with rating info.
        
        Args:
            book_id: Book ID.
            
        Returns:
            Book dict with rating info, or None.
        """
        book = db.get_book_by_id(book_id)
        if book:
            book['avg_rating'] = db.get_average_book_rating(book_id)
            book['rating_count'] = len(db.get_book_ratings(book_id))
        return book
    
    @staticmethod
    def get_all_books() -> List[Dict[str, Any]]:
        """
        Get all books with rating info.
        
        Returns:
            List of book dicts.
        """
        books = db.get_all_books()
        for book in books:
            book['avg_rating'] = db.get_average_book_rating(book['id'])
        return books
    
    @staticmethod
    def search_books(query: str) -> List[Dict[str, Any]]:
        """
        Search books by title or author.
        
        Args:
            query: Search query.
            
        Returns:
            List of matching book dicts.
        """
        if not query or not query.strip():
            return []
        
        books = db.search_books(query.strip())
        for book in books:
            book['avg_rating'] = db.get_average_book_rating(book['id'])
        return books
    
    @staticmethod
    def get_recent_books(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently added books.
        
        Args:
            limit: Maximum number of books.
            
        Returns:
            List of book dicts.
        """
        books = db.get_recent_books(limit)
        for book in books:
            book['avg_rating'] = db.get_average_book_rating(book['id'])
        return books
    
    @staticmethod
    def get_popular_books(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular books.
        
        Args:
            limit: Maximum number of books.
            
        Returns:
            List of book dicts.
        """
        return db.get_popular_books(limit)
    
    @staticmethod
    def rate_book(user_id: int, book_id: int, rating: int) -> Tuple[bool, str]:
        """
        Rate a book.
        
        Args:
            user_id: User ID.
            book_id: Book ID.
            rating: Rating value (1-5).
            
        Returns:
            Tuple of (success, message).
        """
        # Validate rating
        valid, error = validate_rating(rating)
        if not valid:
            return False, error
        
        # Check book exists
        if not db.get_book_by_id(book_id):
            return False, "Book not found"
        
        # Create or update rating
        if db.create_or_update_rating(user_id, book_id, rating):
            logger.info(f"Rating recorded: user {user_id}, book {book_id}, rating {rating}")
            return True, "Rating saved!"
        else:
            return False, "Failed to save rating"
    
    @staticmethod
    def get_user_book_rating(user_id: int, book_id: int) -> Optional[int]:
        """
        Get a user's rating for a specific book.
        
        Args:
            user_id: User ID.
            book_id: Book ID.
            
        Returns:
            Rating value or None.
        """
        return db.get_user_rating(user_id, book_id)
    
    @staticmethod
    def get_user_rated_books(user_id: int) -> List[Dict[str, Any]]:
        """
        Get all books rated by a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of rating dicts with book info.
        """
        return db.get_user_ratings(user_id)
    
    @staticmethod
    def get_books_by_genre(genre: str) -> List[Dict[str, Any]]:
        """
        Get books by genre.
        
        Args:
            genre: Genre to filter by.
            
        Returns:
            List of book dicts.
        """
        all_books = db.get_all_books()
        filtered = [
            book for book in all_books
            if genre in book['genres']
        ]
        for book in filtered:
            book['avg_rating'] = db.get_average_book_rating(book['id'])
        return filtered

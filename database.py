"""
Database Module

Handles all database connections and schema initialization.
Uses SQLite with proper foreign key enforcement and parameterized queries.
"""

import sqlite3
import logging
import json
import urllib.parse
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from utils.constants import DB_PATH

logger = logging.getLogger(__name__)


# ============================================================================
# Book Enrichment - Auto-generates cover_image and pdf_link
# ============================================================================

# Public domain books with Project Gutenberg PDF links
PUBLIC_DOMAIN_PDFS = {
    "pride and prejudice": "https://www.gutenberg.org/files/1342/1342-pdf.pdf",
    "1984": "https://www.planetebook.com/free-ebooks/1984.pdf",
    "frankenstein": "https://www.gutenberg.org/files/84/84-pdf.pdf",
    "dracula": "https://www.gutenberg.org/files/345/345-pdf.pdf",
    "the adventures of sherlock holmes": "https://www.gutenberg.org/files/1661/1661-pdf.pdf",
    "alice's adventures in wonderland": "https://www.gutenberg.org/files/11/11-pdf.pdf",
    "moby dick": "https://www.gutenberg.org/files/2701/2701-pdf.pdf",
    "war and peace": "https://www.gutenberg.org/files/2600/2600-pdf.pdf",
    "crime and punishment": "https://www.gutenberg.org/files/2554/2554-pdf.pdf",
    "jane eyre": "https://www.gutenberg.org/files/1260/1260-pdf.pdf",
    "great expectations": "https://www.gutenberg.org/files/1400/1400-pdf.pdf",
    "the odyssey": "https://www.gutenberg.org/files/1727/1727-pdf.pdf",
    "treasure island": "https://www.gutenberg.org/files/120/120-pdf.pdf",
    "the time machine": "https://www.gutenberg.org/files/35/35-pdf.pdf",
    "the metamorphosis": "https://www.gutenberg.org/files/5200/5200-pdf.pdf",
}

FALLBACK_COVER = "https://via.placeholder.com/300x450/e8f5e9/2e7d32?text=Book"


def _generate_cover_image(title: str) -> str:
    """Generate cover image URL using Open Library API."""
    encoded_title = urllib.parse.quote(title)
    return f"https://covers.openlibrary.org/b/title/{encoded_title}-L.jpg"


def _generate_pdf_link(title: str, author: str = "") -> str:
    """Generate PDF link - Gutenberg for public domain, Google Books for others."""
    normalized = title.lower().strip()
    
    # Check public domain list
    if normalized in PUBLIC_DOMAIN_PDFS:
        return PUBLIC_DOMAIN_PDFS[normalized]
    
    # Check partial matches
    for pd_title, url in PUBLIC_DOMAIN_PDFS.items():
        if pd_title in normalized or normalized in pd_title:
            return url
    
    # Fallback to Google Books search
    query = urllib.parse.quote(f"{title} {author}".strip())
    return f"https://books.google.com/books?q={query}"


def _enrich_book_data(book: Dict[str, Any]) -> Dict[str, Any]:
    """Add cover_image and pdf_link to book data."""
    title = book.get('title', '')
    author = book.get('author', '')
    
    book['cover_image'] = _generate_cover_image(title)
    book['fallback_cover'] = FALLBACK_COVER
    book['pdf_link'] = _generate_pdf_link(title, author)
    
    return book


def get_connection() -> sqlite3.Connection:
    """
    Create a new database connection with foreign key support enabled.
    
    Returns:
        SQLite connection object with row factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db():
    """
    Context manager for database connections.
    Ensures proper connection cleanup and provides automatic commit/rollback.
    
    Yields:
        SQLite connection object.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_database():
    """
    Initialize database schema.
    Creates all required tables if they don't exist.
    Safe to call multiple times.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                interests TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genres TEXT NOT NULL DEFAULT '[]',
                description TEXT DEFAULT '',
                added_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, author),
                FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Ratings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, book_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        """)
        
        # User sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ratings_book ON ratings(book_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)
        """)
        
        logger.info("Database initialized successfully")


# User Operations

def create_user(username: str, email: str, password_hash: str, 
                interests: List[str] = None) -> Optional[int]:
    """
    Create a new user in the database.
    
    Args:
        username: Unique username.
        email: Unique email address.
        password_hash: Bcrypt hashed password.
        interests: List of genre interests.
        
    Returns:
        User ID if successful, None if user already exists.
    """
    interests_json = json.dumps(interests or [])
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, interests)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, interests_json))
            logger.info(f"User created: {username}")
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        logger.warning(f"User already exists: {username} or {email}")
        return None


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user by username.
    
    Args:
        username: Username to look up.
        
    Returns:
        User dict if found, None otherwise.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, password_hash, interests, created_at
            FROM users WHERE username = ?
        """, (username,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'password_hash': row['password_hash'],
                'interests': json.loads(row['interests']),
                'created_at': row['created_at']
            }
        return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user by ID.
    
    Args:
        user_id: User ID to look up.
        
    Returns:
        User dict if found, None otherwise.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, interests, created_at
            FROM users WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'interests': json.loads(row['interests']),
                'created_at': row['created_at']
            }
        return None


def update_user_interests(user_id: int, interests: List[str]) -> bool:
    """
    Update user's genre interests.
    
    Args:
        user_id: User ID to update.
        interests: New list of interests.
        
    Returns:
        True if updated successfully.
    """
    interests_json = json.dumps(interests)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET interests = ? WHERE id = ?
        """, (interests_json, user_id))
        return cursor.rowcount > 0


def get_all_users() -> List[Dict[str, Any]]:
    """
    Retrieve all users (for collaborative filtering).
    
    Returns:
        List of user dicts.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, interests FROM users
        """)
        return [
            {
                'id': row['id'],
                'username': row['username'],
                'interests': json.loads(row['interests'])
            }
            for row in cursor.fetchall()
        ]


# Session Operations

def create_session(user_id: int, session_token: str, expires_at: datetime) -> bool:
    """
    Create a new user session.
    
    Args:
        user_id: User ID.
        session_token: Unique session token.
        expires_at: Session expiration timestamp.
        
    Returns:
        True if created successfully.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, session_token, expires_at.isoformat()))
            logger.info(f"Session created for user {user_id}")
            return True
    except sqlite3.IntegrityError:
        return False


def get_session(session_token: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve session by token.
    
    Args:
        session_token: Session token to look up.
        
    Returns:
        Session dict if found and not expired, None otherwise.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, session_token, expires_at
            FROM user_sessions 
            WHERE session_token = ? AND expires_at > datetime('now')
        """, (session_token,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'session_token': row['session_token'],
                'expires_at': row['expires_at']
            }
        return None


def delete_session(session_token: str) -> bool:
    """
    Delete a session (logout).
    
    Args:
        session_token: Session token to delete.
        
    Returns:
        True if deleted successfully.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM user_sessions WHERE session_token = ?
        """, (session_token,))
        return cursor.rowcount > 0


def cleanup_expired_sessions():
    """
    Remove all expired sessions from the database.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM user_sessions WHERE expires_at <= datetime('now')
        """)
        deleted = cursor.rowcount
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired sessions")


# Book Operations

def create_book(title: str, author: str, genres: List[str], 
                description: str = "", added_by: int = None) -> Optional[int]:
    """
    Create a new book.
    
    Args:
        title: Book title.
        author: Author name.
        genres: List of genres.
        description: Book description.
        added_by: User ID who added the book.
        
    Returns:
        Book ID if successful, None if book already exists.
    """
    genres_json = json.dumps(genres)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books (title, author, genres, description, added_by)
                VALUES (?, ?, ?, ?, ?)
            """, (title, author, genres_json, description, added_by))
            logger.info(f"Book created: {title} by {author}")
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        logger.warning(f"Book already exists: {title} by {author}")
        return None


def get_book_by_id(book_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve book by ID.
    
    Args:
        book_id: Book ID to look up.
        
    Returns:
        Book dict if found, None otherwise.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genres, b.description, 
                   b.added_by, b.created_at, u.username as added_by_username
            FROM books b
            LEFT JOIN users u ON b.added_by = u.id
            WHERE b.id = ?
        """, (book_id,))
        row = cursor.fetchone()
        
        if row:
            return _enrich_book_data({
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'genres': json.loads(row['genres']),
                'description': row['description'],
                'added_by': row['added_by'],
                'added_by_username': row['added_by_username'],
                'created_at': row['created_at']
            })
        return None


def get_all_books() -> List[Dict[str, Any]]:
    """
    Retrieve all books.
    
    Returns:
        List of book dicts.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genres, b.description,
                   b.created_at, u.username as added_by_username
            FROM books b
            LEFT JOIN users u ON b.added_by = u.id
            ORDER BY b.created_at DESC
        """)
        return [
            _enrich_book_data({
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'genres': json.loads(row['genres']),
                'description': row['description'],
                'added_by_username': row['added_by_username'],
                'created_at': row['created_at']
            })
            for row in cursor.fetchall()
        ]


def search_books(query: str) -> List[Dict[str, Any]]:
    """
    Search books by title or author.
    
    Args:
        query: Search query string.
        
    Returns:
        List of matching book dicts.
    """
    search_term = f"%{query}%"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genres, b.description,
                   b.created_at, u.username as added_by_username
            FROM books b
            LEFT JOIN users u ON b.added_by = u.id
            WHERE b.title LIKE ? OR b.author LIKE ?
            ORDER BY b.title
        """, (search_term, search_term))
        return [
            _enrich_book_data({
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'genres': json.loads(row['genres']),
                'description': row['description'],
                'added_by_username': row['added_by_username'],
                'created_at': row['created_at']
            })
            for row in cursor.fetchall()
        ]


def check_book_exists(title: str, author: str) -> bool:
    """
    Check if a book already exists (case-insensitive).
    
    Args:
        title: Book title.
        author: Author name.
        
    Returns:
        True if book exists.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM books 
            WHERE LOWER(title) = LOWER(?) AND LOWER(author) = LOWER(?)
        """, (title, author))
        return cursor.fetchone() is not None


def get_recent_books(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recently added books.
    
    Args:
        limit: Maximum number of books to return.
        
    Returns:
        List of book dicts.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genres, b.description,
                   b.created_at, u.username as added_by_username
            FROM books b
            LEFT JOIN users u ON b.added_by = u.id
            ORDER BY b.created_at DESC
            LIMIT ?
        """, (limit,))
        return [
            _enrich_book_data({
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'genres': json.loads(row['genres']),
                'description': row['description'],
                'added_by_username': row['added_by_username'],
                'created_at': row['created_at']
            })
            for row in cursor.fetchall()
        ]


# Rating Operations

def create_or_update_rating(user_id: int, book_id: int, rating: int) -> bool:
    """
    Create or update a book rating.
    
    Args:
        user_id: User ID.
        book_id: Book ID.
        rating: Rating value (1-5).
        
    Returns:
        True if successful.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ratings (user_id, book_id, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, book_id) 
            DO UPDATE SET rating = excluded.rating
        """, (user_id, book_id, rating))
        logger.info(f"Rating recorded: user {user_id}, book {book_id}, rating {rating}")
        return True


def get_user_rating(user_id: int, book_id: int) -> Optional[int]:
    """
    Get a user's rating for a specific book.
    
    Args:
        user_id: User ID.
        book_id: Book ID.
        
    Returns:
        Rating value if exists, None otherwise.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rating FROM ratings 
            WHERE user_id = ? AND book_id = ?
        """, (user_id, book_id))
        row = cursor.fetchone()
        return row['rating'] if row else None


def get_user_ratings(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all ratings by a user.
    
    Args:
        user_id: User ID.
        
    Returns:
        List of rating dicts with book info.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.book_id, r.rating, b.title, b.author, b.genres
            FROM ratings r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = ?
            ORDER BY r.rating DESC
        """, (user_id,))
        return [
            {
                'book_id': row['book_id'],
                'rating': row['rating'],
                'title': row['title'],
                'author': row['author'],
                'genres': json.loads(row['genres'])
            }
            for row in cursor.fetchall()
        ]


def get_book_ratings(book_id: int) -> List[Dict[str, Any]]:
    """
    Get all ratings for a book.
    
    Args:
        book_id: Book ID.
        
    Returns:
        List of rating dicts.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.user_id, r.rating, u.username
            FROM ratings r
            JOIN users u ON r.user_id = u.id
            WHERE r.book_id = ?
        """, (book_id,))
        return [
            {
                'user_id': row['user_id'],
                'rating': row['rating'],
                'username': row['username']
            }
            for row in cursor.fetchall()
        ]


def get_average_book_rating(book_id: int) -> Optional[float]:
    """
    Get average rating for a book.
    
    Args:
        book_id: Book ID.
        
    Returns:
        Average rating if exists, None otherwise.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(rating) as avg_rating, COUNT(*) as count
            FROM ratings WHERE book_id = ?
        """, (book_id,))
        row = cursor.fetchone()
        if row and row['count'] > 0:
            return round(row['avg_rating'], 2)
        return None


def get_popular_books(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get most popular books based on rating count and average.
    
    Args:
        limit: Maximum number of books to return.
        
    Returns:
        List of book dicts with rating info.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genres, b.description,
                   AVG(r.rating) as avg_rating, COUNT(r.id) as rating_count
            FROM books b
            LEFT JOIN ratings r ON b.id = r.book_id
            GROUP BY b.id
            ORDER BY rating_count DESC, avg_rating DESC
            LIMIT ?
        """, (limit,))
        return [
            _enrich_book_data({
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'genres': json.loads(row['genres']),
                'description': row['description'],
                'avg_rating': round(row['avg_rating'], 2) if row['avg_rating'] else None,
                'rating_count': row['rating_count']
            })
            for row in cursor.fetchall()
        ]


def get_rated_book_ids(user_id: int) -> List[int]:
    """
    Get list of book IDs rated by a user.
    
    Args:
        user_id: User ID.
        
    Returns:
        List of book IDs.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT book_id FROM ratings WHERE user_id = ?
        """, (user_id,))
        return [row['book_id'] for row in cursor.fetchall()]


def get_high_rated_books_by_users(user_ids: List[int], min_rating: int = 4) -> List[Dict[str, Any]]:
    """
    Get books highly rated by specific users.
    
    Args:
        user_ids: List of user IDs.
        min_rating: Minimum rating threshold.
        
    Returns:
        List of book dicts with rating info.
    """
    if not user_ids:
        return []
    
    placeholders = ','.join(['?' for _ in user_ids])
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT b.id, b.title, b.author, b.genres, b.description,
                   r.rating, r.user_id
            FROM ratings r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id IN ({placeholders}) AND r.rating >= ?
            ORDER BY r.rating DESC
        """, (*user_ids, min_rating))
        return [
            {
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'genres': json.loads(row['genres']),
                'description': row['description'],
                'rating': row['rating'],
                'rated_by_user_id': row['user_id']
            }
            for row in cursor.fetchall()
        ]

"""
Application Constants Module

Contains all configurable constants for the Book Recommendation Platform.
Uses environment variables for deployment flexibility.
"""

import os

# Database Configuration
DB_PATH = os.getenv("DB_PATH", "books.db")

# Session Configuration
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))
SESSION_TOKEN_LENGTH = 64

# Validation Constants
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Rating Range
MIN_RATING = 1
MAX_RATING = 5

# Recommendation Settings
DEFAULT_RECOMMENDATION_COUNT = 10
MIN_SIMILARITY_THRESHOLD = 0.1

# Available Genres
GENRES = [
    "Fiction",
    "Non-Fiction",
    "Science Fiction",
    "Fantasy",
    "Mystery",
    "Thriller",
    "Romance",
    "Horror",
    "Biography",
    "History",
    "Self-Help",
    "Science",
    "Technology",
    "Business",
    "Philosophy",
    "Poetry",
    "Drama",
    "Adventure",
    "Children",
    "Young Adult",
    "Classic",
    "Contemporary",
]

# Application Settings
APP_NAME = "Book Recommendation Platform"
APP_VERSION = "1.0.0"

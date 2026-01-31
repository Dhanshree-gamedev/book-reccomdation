"""
Data Models Module

Pydantic models for type-safe data handling throughout the application.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Model for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    interests: List[str] = Field(default_factory=list)


class UserLogin(BaseModel):
    """Model for user login."""
    username: str
    password: str


class User(BaseModel):
    """Model for user data (without password)."""
    id: int
    username: str
    email: str
    interests: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None


class BookCreate(BaseModel):
    """Model for book creation."""
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=200)
    genres: List[str] = Field(..., min_items=1)
    description: str = Field(default="")


class Book(BaseModel):
    """Model for book data."""
    id: int
    title: str
    author: str
    genres: List[str]
    description: str = ""
    added_by: Optional[int] = None
    added_by_username: Optional[str] = None
    created_at: Optional[str] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None


class RatingCreate(BaseModel):
    """Model for rating creation."""
    book_id: int
    rating: int = Field(..., ge=1, le=5)


class Rating(BaseModel):
    """Model for rating data."""
    id: int
    user_id: int
    book_id: int
    rating: int
    created_at: Optional[str] = None


class Recommendation(BaseModel):
    """Model for book recommendation."""
    book: Book
    score: float = Field(..., ge=0, le=1)
    reason: str
    recommendation_type: str  # 'content_based' or 'collaborative'

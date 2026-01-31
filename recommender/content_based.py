"""
Content-Based Filtering Module

Implements content-based book recommendations by matching
user interests with book genres using Jaccard similarity.
"""

import logging
from typing import List, Dict, Any

import database as db
from recommender.utils import calculate_genre_overlap
from utils.constants import MIN_SIMILARITY_THRESHOLD, DEFAULT_RECOMMENDATION_COUNT

logger = logging.getLogger(__name__)


def get_content_based_recommendations(
    user_id: int,
    limit: int = DEFAULT_RECOMMENDATION_COUNT
) -> List[Dict[str, Any]]:
    """
    Generate content-based recommendations for a user.
    
    Algorithm:
    1. Get user's genre interests from their profile
    2. Get all books not yet rated by the user
    3. Calculate Jaccard similarity between user interests and each book's genres
    4. Filter books below minimum similarity threshold
    5. Rank by similarity score and return top N
    
    Args:
        user_id: User ID to generate recommendations for.
        limit: Maximum number of recommendations to return.
        
    Returns:
        List of recommendation dicts with book info and scores.
        Each item contains:
        - book: Full book information
        - score: Similarity score (0-1)
        - reason: Human-readable explanation
        - recommendation_type: 'content_based'
    
    Example:
        User interests: ["Science Fiction", "Fantasy"]
        Book genres: ["Science Fiction", "Adventure"]
        
        Jaccard similarity = |{SF}| / |{SF, Fantasy, Adventure}| = 1/3 ≈ 0.33
        
        If score >= MIN_SIMILARITY_THRESHOLD, book is recommended.
    """
    # Get user profile
    user = db.get_user_by_id(user_id)
    if not user:
        logger.warning(f"User {user_id} not found for recommendations")
        return []
    
    user_interests = user.get('interests', [])
    
    # Handle case where user has no interests set
    if not user_interests:
        logger.info(f"User {user_id} has no interests set, returning empty recommendations")
        return []
    
    # Get all books
    all_books = db.get_all_books()
    
    # Get books already rated by user (to exclude)
    rated_book_ids = set(db.get_rated_book_ids(user_id))
    
    recommendations = []
    
    for book in all_books:
        # Skip books already rated
        if book['id'] in rated_book_ids:
            continue
        
        # Calculate genre similarity
        score = calculate_genre_overlap(user_interests, book['genres'])
        
        # Apply minimum threshold
        if score < MIN_SIMILARITY_THRESHOLD:
            continue
        
        # Generate explanation
        matching_genres = set(g.lower() for g in user_interests) & set(g.lower() for g in book['genres'])
        matching_list = [g for g in book['genres'] if g.lower() in matching_genres]
        
        if matching_list:
            reason = f"Matches your interest in {', '.join(matching_list[:3])}"
        else:
            reason = "Based on your reading preferences"
        
        # Get average rating for display
        avg_rating = db.get_average_book_rating(book['id'])
        book['avg_rating'] = avg_rating
        
        recommendations.append({
            'book': book,
            'score': round(score, 3),
            'reason': reason,
            'recommendation_type': 'content_based'
        })
    
    # Sort by score (descending) and limit results
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    logger.info(f"Generated {len(recommendations[:limit])} content-based recommendations for user {user_id}")
    
    return recommendations[:limit]


def get_genre_based_recommendations(
    genres: List[str],
    exclude_book_ids: List[int] = None,
    limit: int = DEFAULT_RECOMMENDATION_COUNT
) -> List[Dict[str, Any]]:
    """
    Get recommendations based on specific genres (for anonymous users).
    
    Args:
        genres: List of genres to match.
        exclude_book_ids: Book IDs to exclude from results.
        limit: Maximum number of recommendations.
        
    Returns:
        List of recommendation dicts.
    """
    if not genres:
        return []
    
    exclude_book_ids = set(exclude_book_ids or [])
    all_books = db.get_all_books()
    
    recommendations = []
    
    for book in all_books:
        if book['id'] in exclude_book_ids:
            continue
        
        score = calculate_genre_overlap(genres, book['genres'])
        
        if score < MIN_SIMILARITY_THRESHOLD:
            continue
        
        matching_genres = set(g.lower() for g in genres) & set(g.lower() for g in book['genres'])
        matching_list = [g for g in book['genres'] if g.lower() in matching_genres]
        
        book['avg_rating'] = db.get_average_book_rating(book['id'])
        
        recommendations.append({
            'book': book,
            'score': round(score, 3),
            'reason': f"Matches: {', '.join(matching_list[:3])}" if matching_list else "Related to your selection",
            'recommendation_type': 'content_based'
        })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    return recommendations[:limit]

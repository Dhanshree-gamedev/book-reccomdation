"""
Collaborative Filtering Module

Implements collaborative filtering recommendations by finding
users with similar interests and recommending books they rated highly.
"""

import logging
from typing import List, Dict, Any, Set
from collections import defaultdict

import database as db
from recommender.utils import jaccard_similarity, normalize_genres
from utils.constants import MIN_SIMILARITY_THRESHOLD, DEFAULT_RECOMMENDATION_COUNT

logger = logging.getLogger(__name__)


def find_similar_users(
    user_id: int,
    min_similarity: float = MIN_SIMILARITY_THRESHOLD
) -> List[Dict[str, Any]]:
    """
    Find users with similar interests to the target user.
    
    Similarity is calculated using Jaccard similarity on genre interests.
    
    Args:
        user_id: Target user ID.
        min_similarity: Minimum similarity threshold.
        
    Returns:
        List of similar user dicts sorted by similarity.
        Each item contains:
        - user_id: Similar user's ID
        - username: Similar user's username
        - similarity: Similarity score (0-1)
        - common_interests: List of shared interests
    """
    target_user = db.get_user_by_id(user_id)
    if not target_user:
        return []
    
    target_interests = set(normalize_genres(target_user.get('interests', [])))
    
    if not target_interests:
        return []
    
    all_users = db.get_all_users()
    similar_users = []
    
    for user in all_users:
        # Skip self
        if user['id'] == user_id:
            continue
        
        user_interests = set(normalize_genres(user.get('interests', [])))
        
        if not user_interests:
            continue
        
        similarity = jaccard_similarity(target_interests, user_interests)
        
        if similarity >= min_similarity:
            # Find common interests (in original case)
            common = target_interests & user_interests
            common_display = [
                g for g in target_user['interests']
                if g.lower() in common
            ]
            
            similar_users.append({
                'user_id': user['id'],
                'username': user['username'],
                'similarity': round(similarity, 3),
                'common_interests': common_display
            })
    
    # Sort by similarity descending
    similar_users.sort(key=lambda x: x['similarity'], reverse=True)
    
    return similar_users


def get_collaborative_recommendations(
    user_id: int,
    limit: int = DEFAULT_RECOMMENDATION_COUNT
) -> List[Dict[str, Any]]:
    """
    Generate collaborative filtering recommendations for a user.
    
    Algorithm:
    1. Find users with similar interests (Jaccard similarity on interests)
    2. Get books rated highly (4-5 stars) by similar users
    3. Weight each book's score by:
       - User similarity (how similar the recommending user is)
       - Rating value (higher ratings = stronger signal)
    4. Aggregate scores across multiple similar users
    5. Exclude books already rated by target user
    6. Return top N recommendations
    
    Scoring formula:
        book_score = sum(user_similarity * (rating / 5)) for each similar user
        normalized_score = book_score / max_possible_score
    
    Args:
        user_id: User ID to generate recommendations for.
        limit: Maximum number of recommendations.
        
    Returns:
        List of recommendation dicts with book info and scores.
        
    Handles edge cases:
        - User has no interests: Returns empty list
        - No similar users found: Returns empty list
        - Similar users have no ratings: Returns empty list
    """
    # Find similar users
    similar_users = find_similar_users(user_id)
    
    if not similar_users:
        logger.info(f"No similar users found for user {user_id}")
        return []
    
    # Get books already rated by target user
    rated_book_ids = set(db.get_rated_book_ids(user_id))
    
    # Get highly-rated books from similar users
    similar_user_ids = [u['user_id'] for u in similar_users]
    highly_rated_books = db.get_high_rated_books_by_users(similar_user_ids, min_rating=4)
    
    if not highly_rated_books:
        logger.info(f"No highly-rated books from similar users for user {user_id}")
        return []
    
    # Create user similarity lookup
    user_similarity = {u['user_id']: u['similarity'] for u in similar_users}
    
    # Aggregate scores for each book
    # Score = sum of (user_similarity * normalized_rating) across all similar users
    book_scores = defaultdict(lambda: {'score': 0, 'contributors': [], 'book': None})
    
    for item in highly_rated_books:
        book_id = item['id']
        
        # Skip books already rated by target user
        if book_id in rated_book_ids:
            continue
        
        rater_id = item['rated_by_user_id']
        rating = item['rating']
        similarity = user_similarity.get(rater_id, 0)
        
        # Calculate weighted score: similarity * (rating / 5)
        # This normalizes rating to 0-1 range
        weighted_score = similarity * (rating / 5.0)
        
        book_scores[book_id]['score'] += weighted_score
        book_scores[book_id]['contributors'].append({
            'user_id': rater_id,
            'rating': rating,
            'similarity': similarity
        })
        book_scores[book_id]['book'] = {
            'id': item['id'],
            'title': item['title'],
            'author': item['author'],
            'genres': item['genres'],
            'description': item['description']
        }
    
    # Convert to recommendation list
    recommendations = []
    
    # Normalize scores (max possible = sum of all similarities if all rated 5)
    max_possible = sum(u['similarity'] for u in similar_users)
    
    for book_id, data in book_scores.items():
        if data['book'] is None:
            continue
        
        # Normalize score to 0-1 range
        normalized_score = min(data['score'] / max_possible, 1.0) if max_possible > 0 else 0
        
        # Generate explanation
        num_recommenders = len(data['contributors'])
        avg_rating = sum(c['rating'] for c in data['contributors']) / num_recommenders
        
        if num_recommenders == 1:
            reason = f"Recommended by a reader with similar taste (rated {avg_rating:.0f}★)"
        else:
            reason = f"Loved by {num_recommenders} readers with similar taste (avg {avg_rating:.1f}★)"
        
        # Get average rating
        book = data['book']
        book['avg_rating'] = db.get_average_book_rating(book_id)
        
        recommendations.append({
            'book': book,
            'score': round(normalized_score, 3),
            'reason': reason,
            'recommendation_type': 'collaborative',
            'num_similar_users': num_recommenders
        })
    
    # Sort by score descending
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    logger.info(f"Generated {len(recommendations[:limit])} collaborative recommendations for user {user_id}")
    
    return recommendations[:limit]


def get_popular_among_similar_users(
    user_id: int,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get books that are popular among similar users (any rating).
    
    Useful as a secondary recommendation source when collaborative
    filtering returns few results.
    
    Args:
        user_id: Target user ID.
        limit: Maximum number of books.
        
    Returns:
        List of book dicts.
    """
    similar_users = find_similar_users(user_id)
    
    if not similar_users:
        return []
    
    rated_book_ids = set(db.get_rated_book_ids(user_id))
    similar_user_ids = [u['user_id'] for u in similar_users]
    
    # Get all rated books from similar users (any rating)
    all_rated = db.get_high_rated_books_by_users(similar_user_ids, min_rating=1)
    
    # Count occurrences
    book_counts = defaultdict(lambda: {'count': 0, 'book': None})
    
    for item in all_rated:
        if item['id'] not in rated_book_ids:
            book_counts[item['id']]['count'] += 1
            book_counts[item['id']]['book'] = item
    
    # Sort by count and return top books
    sorted_books = sorted(
        book_counts.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    result = []
    for book_id, data in sorted_books[:limit]:
        book = data['book']
        book['avg_rating'] = db.get_average_book_rating(book_id)
        result.append(book)
    
    return result

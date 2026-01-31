"""
Recommendation Utilities Module

Common utility functions for recommendation algorithms.
Includes similarity calculations and helper functions.
"""

from typing import List, Set


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Calculate Jaccard similarity between two sets.
    
    The Jaccard similarity coefficient is defined as the size of the
    intersection divided by the size of the union of the two sets.
    
    Jaccard(A, B) = |A ∩ B| / |A ∪ B|
    
    Args:
        set1: First set of items.
        set2: Second set of items.
        
    Returns:
        Similarity score between 0 and 1.
        Returns 0 if both sets are empty.
    
    Examples:
        >>> jaccard_similarity({'a', 'b', 'c'}, {'b', 'c', 'd'})
        0.5  # intersection={b,c}, union={a,b,c,d}
    """
    if not set1 and not set2:
        return 0.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def normalize_genres(genres: List[str]) -> Set[str]:
    """
    Normalize a list of genres to a set of lowercase strings.
    
    Args:
        genres: List of genre strings.
        
    Returns:
        Set of normalized (lowercase) genre strings.
    """
    if not genres:
        return set()
    return {g.lower().strip() for g in genres if g}


def calculate_genre_overlap(user_interests: List[str], book_genres: List[str]) -> float:
    """
    Calculate how well book genres match user interests.
    
    Args:
        user_interests: List of user's genre interests.
        book_genres: List of book's genres.
        
    Returns:
        Similarity score between 0 and 1.
    """
    user_set = normalize_genres(user_interests)
    book_set = normalize_genres(book_genres)
    
    return jaccard_similarity(user_set, book_set)


def weighted_score(base_score: float, weight: float) -> float:
    """
    Apply a weight to a base score.
    
    Args:
        base_score: Original score (0-1).
        weight: Weight multiplier.
        
    Returns:
        Weighted score, capped at 1.0.
    """
    return min(base_score * weight, 1.0)

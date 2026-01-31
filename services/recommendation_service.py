"""
Recommendation Service Module

Orchestrates content-based and collaborative filtering recommendations.
Provides a unified interface for the UI layer with fallback mechanisms.
"""

import logging
from typing import List, Dict, Any, Optional

import database as db
from recommender.content_based import get_content_based_recommendations, get_genre_based_recommendations
from recommender.collaborative import get_collaborative_recommendations, find_similar_users
from utils.constants import DEFAULT_RECOMMENDATION_COUNT

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service class for book recommendations.
    
    Combines content-based and collaborative filtering approaches
    with intelligent fallback mechanisms for cold-start users.
    """
    
    @staticmethod
    def get_recommendations(
        user_id: int,
        limit: int = DEFAULT_RECOMMENDATION_COUNT
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get combined recommendations for a user.
        
        Provides both content-based and collaborative recommendations
        in separate categories for display.
        
        Args:
            user_id: User ID.
            limit: Maximum recommendations per category.
            
        Returns:
            Dict with 'content_based', 'collaborative', and 'fallback' keys.
        """
        result = {
            'content_based': [],
            'collaborative': [],
            'fallback': []
        }
        
        # Get content-based recommendations
        content_recs = get_content_based_recommendations(user_id, limit)
        result['content_based'] = content_recs
        
        # Get collaborative recommendations
        collab_recs = get_collaborative_recommendations(user_id, limit)
        result['collaborative'] = collab_recs
        
        # If both are empty, provide fallback recommendations
        if not content_recs and not collab_recs:
            result['fallback'] = RecommendationService.get_fallback_recommendations(
                user_id, limit
            )
        
        logger.info(
            f"Generated recommendations for user {user_id}: "
            f"{len(content_recs)} content-based, "
            f"{len(collab_recs)} collaborative, "
            f"{len(result['fallback'])} fallback"
        )
        
        return result
    
    @staticmethod
    def get_fallback_recommendations(
        user_id: int,
        limit: int = DEFAULT_RECOMMENDATION_COUNT
    ) -> List[Dict[str, Any]]:
        """
        Get fallback recommendations for cold-start users.
        
        Used when user has no interests set or no similar users exist.
        Returns a mix of popular and recent books.
        
        Args:
            user_id: User ID.
            limit: Maximum number of recommendations.
            
        Returns:
            List of recommendation dicts.
        """
        rated_book_ids = set(db.get_rated_book_ids(user_id))
        
        recommendations = []
        
        # Get popular books
        popular = db.get_popular_books(limit)
        for book in popular:
            if book['id'] not in rated_book_ids:
                recommendations.append({
                    'book': book,
                    'score': 0.5,  # Neutral score for fallback
                    'reason': "Popular among readers" if book['rating_count'] > 0 else "Recently added",
                    'recommendation_type': 'fallback'
                })
        
        # If still not enough, add recent books
        if len(recommendations) < limit:
            recent = db.get_recent_books(limit)
            for book in recent:
                if book['id'] not in rated_book_ids:
                    # Avoid duplicates
                    if not any(r['book']['id'] == book['id'] for r in recommendations):
                        recommendations.append({
                            'book': book,
                            'score': 0.3,
                            'reason': "Recently added",
                            'recommendation_type': 'fallback'
                        })
        
        return recommendations[:limit]
    
    @staticmethod
    def get_similar_books(
        book_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get books similar to a specific book (genre-based).
        
        Args:
            book_id: Book ID to find similar books for.
            limit: Maximum number of results.
            
        Returns:
            List of similar book dicts.
        """
        book = db.get_book_by_id(book_id)
        if not book:
            return []
        
        return get_genre_based_recommendations(
            genres=book['genres'],
            exclude_book_ids=[book_id],
            limit=limit
        )
    
    @staticmethod
    def get_personalized_home_feed(
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get a personalized feed for the home page.
        
        Combines recommendations from all sources with diversity.
        
        Args:
            user_id: User ID.
            limit: Maximum number of items.
            
        Returns:
            List of recommendation dicts.
        """
        all_recs = RecommendationService.get_recommendations(user_id, limit)
        
        feed = []
        seen_ids = set()
        
        # Interleave recommendations for diversity
        sources = [
            all_recs['content_based'],
            all_recs['collaborative'],
            all_recs['fallback']
        ]
        
        idx = 0
        while len(feed) < limit:
            added = False
            for source in sources:
                if idx < len(source):
                    rec = source[idx]
                    if rec['book']['id'] not in seen_ids:
                        feed.append(rec)
                        seen_ids.add(rec['book']['id'])
                        added = True
            
            if not added:
                break
            idx += 1
        
        return feed[:limit]
    
    @staticmethod
    def explain_recommendation(
        user_id: int,
        book_id: int
    ) -> Optional[str]:
        """
        Generate an explanation for why a book was recommended.
        
        Args:
            user_id: User ID.
            book_id: Book ID.
            
        Returns:
            Explanation string or None.
        """
        user = db.get_user_by_id(user_id)
        book = db.get_book_by_id(book_id)
        
        if not user or not book:
            return None
        
        explanations = []
        
        # Check genre overlap
        user_interests = set(g.lower() for g in user.get('interests', []))
        book_genres = set(g.lower() for g in book['genres'])
        common = user_interests & book_genres
        
        if common:
            common_display = [g for g in book['genres'] if g.lower() in common]
            explanations.append(
                f"This book matches your interest in {', '.join(common_display)}"
            )
        
        # Check if similar users liked it
        similar_users = find_similar_users(user_id)
        if similar_users:
            for sim_user in similar_users[:5]:
                rating = db.get_user_rating(sim_user['user_id'], book_id)
                if rating and rating >= 4:
                    explanations.append(
                        f"Readers with similar taste rated this {rating}★"
                    )
                    break
        
        # Check overall popularity
        avg_rating = db.get_average_book_rating(book_id)
        if avg_rating and avg_rating >= 4:
            explanations.append(f"Highly rated by readers ({avg_rating}★ average)")
        
        if explanations:
            return " • ".join(explanations)
        
        return "Based on your reading preferences"
    
    @staticmethod
    def get_recommendation_stats(user_id: int) -> Dict[str, Any]:
        """
        Get statistics about recommendation potential for a user.
        
        Useful for debugging and user feedback.
        
        Args:
            user_id: User ID.
            
        Returns:
            Dict with stats about recommendation sources.
        """
        user = db.get_user_by_id(user_id)
        
        if not user:
            return {'error': 'User not found'}
        
        similar_users = find_similar_users(user_id)
        rated_count = len(db.get_rated_book_ids(user_id))
        
        return {
            'user_id': user_id,
            'interests_count': len(user.get('interests', [])),
            'has_interests': len(user.get('interests', [])) > 0,
            'books_rated': rated_count,
            'similar_users_count': len(similar_users),
            'can_use_content_based': len(user.get('interests', [])) > 0,
            'can_use_collaborative': len(similar_users) > 0
        }

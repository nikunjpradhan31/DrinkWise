from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from datetime import datetime, timedelta
import logging
import random
from typing import Optional, Dict, Any, List, Tuple

from .base import BaseService, ValidationError
from models import (
    Drink, UserPreference, UserFilter, UserDrinkInteraction, 
    UserFavorite, UserRecentlyViewed, Recommendation, UserFeedback,
    TasteQuizResult
)
from pydantic_models import RecommendationRequest, RecommendationItem, RecommendationResponse

class HybridModelService:
    """
    Hybrid recommendation model service combining multiple algorithms:
    - Content-based filtering (drink attributes)
    - Collaborative filtering (user interactions)
    - Taste preference matching
    - Feedback loop adaptation
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("hybrid_model_service")
    
    async def generate_recommendations(
        self, 
        user_id: int, 
        request: RecommendationRequest,
        age_verified: bool = False
    ) -> RecommendationResponse:
        """
        Generate personalized drink recommendations using hybrid approach
        
        Args:
            user_id: User ID
            request: Recommendation request parameters
            age_verified: Whether user is age verified for alcohol content
            
        Returns:
            RecommendationResponse with ranked drinks
        """
        try:
            self.logger.info(f"Generating recommendations for user {user_id}")
            
            # Get user profile
            user_preference = await self._get_user_preference(user_id)
            user_filter = await self._get_user_filter(user_id)
            user_interactions = await self._get_user_interactions(user_id)
            
            # Get candidate drinks
            candidate_drinks = await self._get_candidate_drinks(
                user_id, user_filter, age_verified
            )
            
            # Apply hybrid recommendation algorithms
            recommendations = []
            
            # Content-based recommendations (40% weight)
            content_recs = await self._content_based_recommendations(
                candidate_drinks, user_preference, user_interactions
            )
            recommendations.extend(content_recs)
            
            # Collaborative filtering (30% weight)  
            collaborative_recs = await self._collaborative_filtering_recommendations(
                user_id, candidate_drinks, user_interactions
            )
            recommendations.extend(collaborative_recs)
            
            # Taste preference matching (30% weight)
            taste_recs = await self._taste_preference_recommendations(
                candidate_drinks, user_preference, user_interactions
            )
            recommendations.extend(taste_recs)
            
            # Apply feedback adjustments
            recommendations = await self._apply_feedback_adjustments(
                user_id, recommendations, user_interactions
            )
            
            # Remove duplicates and rank
            unique_recommendations = self._remove_duplicates(recommendations)
            ranked_recommendations = self._rank_recommendations(unique_recommendations)
            
            # Limit results
            final_recommendations = ranked_recommendations[:request.limit]
            
            # Convert to response format
            recommendation_items = []
            for drink, score, explanation in final_recommendations:
                recommendation_items.append(RecommendationItem(
                    drink=drink,
                    score=score,
                    explanation=explanation
                ))
            
            return RecommendationResponse(
                recommendations=recommendation_items,
                total_count=len(final_recommendations),
                recommendation_type=request.recommendation_type or "hybrid"
            )
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return RecommendationResponse(
                recommendations=[],
                total_count=0,
                recommendation_type="hybrid"
            )
    
    async def _get_user_preference(self, user_id: int) -> Optional[UserPreference]:
        """Get user preference profile"""
        try:
            result = await self.db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user preference: {str(e)}")
            return None
    
    async def _get_user_filter(self, user_id: int) -> Optional[UserFilter]:
        """Get user filter preferences"""
        try:
            result = await self.db.execute(
                select(UserFilter).where(
                    UserFilter.user_id == user_id,
                    UserFilter.is_active == True
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user filter: {str(e)}")
            return None
    
    async def _get_user_interactions(self, user_id: int) -> Dict[str, Any]:
        """Get user drink interactions"""
        try:
            # Get favorites
            favorites_result = await self.db.execute(
                select(UserFavorite).where(UserFavorite.user_id == user_id)
            )
            favorites = [f.drink_id for f in favorites_result.scalars().all()]
            
            # Get recent interactions
            interactions_result = await self.db.execute(
                select(UserDrinkInteraction).where(UserDrinkInteraction.user_id == user_id)
            )
            interactions = {i.drink_id: i for i in interactions_result.scalars().all()}
            
            # Get feedback
            feedback_result = await self.db.execute(
                select(UserFeedback).where(UserFeedback.user_id == user_id)
            )
            feedback = {f.drink_id: f for f in feedback_result.scalars().all()}
            
            return {
                "favorites": favorites,
                "interactions": interactions,
                "feedback": feedback
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user interactions: {str(e)}")
            return {"favorites": [], "interactions": {}, "feedback": {}}
    
    async def _get_candidate_drinks(
        self, 
        user_id: int, 
        user_filter: Optional[UserFilter],
        age_verified: bool
    ) -> List[Drink]:
        """Get candidate drinks for recommendations"""
        try:
            query = select(Drink)
            
            # Apply age verification filter
            if not age_verified:
                query = query.where(Drink.is_alcoholic == False)
            
            # Apply user filter if available
            if user_filter:
                if user_filter.budget_tier:
                    query = query.where(Drink.price_tier == user_filter.budget_tier)
                
                if user_filter.sweetness_filter:
                    query = query.where(Drink.sweetness_level <= user_filter.sweetness_filter)
                
                if user_filter.caffeine_min is not None:
                    query = query.where(Drink.caffeine_content >= user_filter.caffeine_min)
                
                if user_filter.caffeine_max is not None:
                    query = query.where(Drink.caffeine_content <= user_filter.caffeine_max)
            
            # Exclude drinks user has already interacted with negatively
            query = query.where(
                ~Drink.drink_id.in_(
                    select(UserDrinkInteraction.drink_id).where(
                        UserDrinkInteraction.user_id == user_id,
                        UserDrinkInteraction.is_not_for_me == True
                    )
                )
            )
            
            result = await self.db.execute(query.limit(100))  # Limit to top 100 candidates
            return result.scalars().all()
            
        except Exception as e:
            self.logger.error(f"Error getting candidate drinks: {str(e)}")
            return []
    
    async def _content_based_recommendations(
        self, 
        candidate_drinks: List[Drink], 
        user_preference: Optional[UserPreference],
        user_interactions: Dict[str, Any]
    ) -> List[Tuple[Drink, float, List[str]]]:
        """Content-based filtering recommendations"""
        try:
            recommendations = []
            
            for drink in candidate_drinks:
                score = 0.0
                explanation = []
                
                if user_preference:
                    # Sweetness matching
                    sweetness_diff = abs(drink.sweetness_level - user_preference.sweetness_preference)
                    sweetness_score = max(0, 1 - (sweetness_diff / 10))
                    score += sweetness_score * 0.3
                    explanation.append(f"Matches your sweetness preference ({sweetness_score:.2f})")
                    
                    # Price tier preference
                    if drink.price_tier == user_preference.preferred_price_tier:
                        score += 0.2
                        explanation.append("Within your preferred price range")
                    
                    # Caffeine preference
                    if drink.caffeine_content <= user_preference.caffeine_limit:
                        score += 0.15
                        explanation.append("Within your caffeine limit")
                    
                    # Sugar preference
                    if drink.sugar_content <= user_preference.sugar_limit:
                        score += 0.15
                        explanation.append("Within your sugar limit")
                
                # Boost popular drinks slightly
                score += 0.1
                explanation.append("Popular choice")
                
                # Adjust for user interactions
                if drink.drink_id in user_interactions["favorites"]:
                    score *= 0.8  # Reduce if already favorited
                    explanation.append("Similar to your favorites")
                
                recommendations.append((drink, score, explanation))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in content-based recommendations: {str(e)}")
            return []
    
    async def _collaborative_filtering_recommendations(
        self, 
        user_id: int, 
        candidate_drinks: List[Drink],
        user_interactions: Dict[str, Any]
    ) -> List[Tuple[Drink, float, List[str]]]:
        """Collaborative filtering recommendations"""
        try:
            # Find similar users (simplified - in practice would use more sophisticated similarity)
            similar_users_result = await self.db.execute(
                select(UserDrinkInteraction.user_id)
                .where(
                    UserDrinkInteraction.user_id != user_id,
                    UserDrinkInteraction.is_favorite == True,
                    UserDrinkInteraction.drink_id.in_([d.drink_id for d in user_interactions["interactions"].keys()])
                )
                .limit(10)
            )
            similar_users = [u[0] for u in similar_users_result.scalars().all()]
            
            if not similar_users:
                return []
            
            # Get drinks liked by similar users
            liked_drinks_result = await self.db.execute(
                select(UserDrinkInteraction.drink_id)
                .where(
                    UserDrinkInteraction.user_id.in_(similar_users),
                    UserDrinkInteraction.is_favorite == True
                )
                .distinct()
            )
            liked_drink_ids = [d[0] for d in liked_drinks_result.scalars().all()]
            
            # Get these drinks that are in our candidates
            recommendations = []
            candidate_ids = [d.drink_id for d in candidate_drinks]
            
            for drink_id in liked_drink_ids:
                if drink_id in candidate_ids:
                    # Find the drink object
                    drink = next((d for d in candidate_drinks if d.drink_id == drink_id), None)
                    if drink:
                        score = 0.7  # Base collaborative score
                        explanation = ["Users with similar taste also liked this"]
                        
                        # Boost if multiple similar users liked it
                        recommendations.append((drink, score, explanation))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in collaborative filtering: {str(e)}")
            return []
    
    async def _taste_preference_recommendations(
        self, 
        candidate_drinks: List[Drink], 
        user_preference: Optional[UserPreference],
        user_interactions: Dict[str, Any]
    ) -> List[Tuple[Drink, float, List[str]]]:
        """Taste preference-based recommendations"""
        try:
            if not user_preference:
                return []
            
            recommendations = []
            
            for drink in candidate_drinks:
                score = 0.0
                explanation = []
                
                # Bitterness preference matching
                if user_preference.bitterness_preference:
                    bitterness_factor = 1 - abs(5 - user_preference.bitterness_preference) / 5
                    score += bitterness_factor * 0.2
                    explanation.append(f"Bitterness level matches your preference")
                
                # Category preferences
                if user_preference.preferred_categories and drink.category in user_preference.preferred_categories:
                    score += 0.3
                    explanation.append("From your preferred category")
                
                # Time sensitivity preferences (simplified)
                if user_preference.time_sensitivity:
                    # Would implement time-based logic here
                    score += 0.1
                    explanation.append("Suitable for current time")
                
                # Mode preferences (decaf, energy, etc.)
                if user_preference.mode_preferences:
                    mode_boost = 0.1
                    score += mode_boost
                    explanation.append("Matches your preferred mode")
                
                if score > 0:
                    recommendations.append((drink, score, explanation))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in taste preference recommendations: {str(e)}")
            return []
    
    async def _apply_feedback_adjustments(
        self, 
        user_id: int, 
        recommendations: List[Tuple[Drink, float, List[str]]],
        user_interactions: Dict[str, Any]
    ) -> List[Tuple[Drink, float, List[str]]]:
        """Apply user feedback adjustments"""
        try:
            adjusted_recs = []
            
            for drink, score, explanation in recommendations:
                # Reduce score if user has given negative feedback
                if drink.drink_id in user_interactions["feedback"]:
                    feedback = user_interactions["feedback"][drink.drink_id]
                    if feedback.feedback_type == "not_for_me":
                        score *= 0.3  # Strong reduction
                        explanation.append("Previously marked as not preferred")
                    elif feedback.feedback_type in ["too_sweet", "too_bitter"]:
                        score *= 0.6  # Moderate reduction
                        explanation.append("Previously provided feedback on taste")
                
                # Boost if user has given positive feedback
                if drink.drink_id in user_interactions["interactions"]:
                    interaction = user_interactions["interactions"][drink.drink_id]
                    if interaction.rating >= 4.0:
                        score *= 1.2  # Boost for highly rated similar drinks
                        explanation.append("Similar to highly rated drinks")
                
                adjusted_recs.append((drink, score, explanation))
            
            return adjusted_recs
            
        except Exception as e:
            self.logger.error(f"Error applying feedback adjustments: {str(e)}")
            return recommendations
    
    def _remove_duplicates(
        self, 
        recommendations: List[Tuple[Drink, float, List[str]]]
    ) -> List[Tuple[Drink, float, List[str]]]:
        """Remove duplicate drink recommendations"""
        seen_ids = set()
        unique_recs = []
        
        for drink, score, explanation in recommendations:
            if drink.drink_id not in seen_ids:
                seen_ids.add(drink.drink_id)
                unique_recs.append((drink, score, explanation))
        
        return unique_recs
    
    def _rank_recommendations(
        self, 
        recommendations: List[Tuple[Drink, float, List[str]]]
    ) -> List[Tuple[Drink, float, List[str]]]:
        """Rank recommendations by score"""
        return sorted(recommendations, key=lambda x: x[1], reverse=True)
    
    async def get_similar_drinks(self, drink_id: int, limit: int = 10) -> List[Drink]:
        """Get drinks similar to a given drink"""
        try:
            # Get the base drink
            base_drink_result = await self.db.execute(
                select(Drink).where(Drink.drink_id == drink_id)
            )
            base_drink = base_drink_result.scalar_one_or_none()
            
            if not base_drink:
                return []
            
            # Find similar drinks based on category, price tier, and nutritional profile
            similar_drinks_result = await self.db.execute(
                select(Drink)
                .where(
                    Drink.drink_id != drink_id,
                    Drink.category == base_drink.category,
                    Drink.price_tier == base_drink.price_tier,
                    abs(Drink.sweetness_level - base_drink.sweetness_level) <= 2
                )
                .limit(limit)
            )
            
            return similar_drinks_result.scalars().all()
            
        except Exception as e:
            self.logger.error(f"Error getting similar drinks: {str(e)}")
            return []
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging
from typing import Optional, Dict, Any, List

from .base import BaseService
from models import Drink, UserPreference, UserFilter, UserDrinkInteraction, UserFeedback, TasteQuizResult
from pydantic_models import DrinkResponse

class ExplainabilityService:
    """
    Service for generating explanations for why drinks were recommended
    Provides transparency in the recommendation process
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("explainability_service")
    
    async def generate_explanation(
        self, 
        user_id: int, 
        drink: Drink, 
        recommendation_score: float,
        recommendation_type: str
    ) -> List[str]:
        """
        Generate explanations for why a drink was recommended
        
        Args:
            user_id: User ID
            drink: Drink object
            recommendation_score: Score from recommendation algorithm
            recommendation_type: Type of recommendation (content, collaborative, hybrid)
            
        Returns:
            List of explanation strings
        """
        try:
            explanations = []
            
            # Get user profile data
            user_preference = await self._get_user_preference(user_id)
            user_filter = await self._get_user_filter(user_id)
            user_interactions = await self._get_user_interactions(user_id)
            
            # Generate explanations based on recommendation type
            if recommendation_type in ["content", "hybrid"]:
                explanations.extend(self._generate_content_explanations(drink, user_preference, user_interactions))
            
            if recommendation_type in ["collaborative", "hybrid"]:
                explanations.extend(await self._generate_collaborative_explanations(user_id, drink))
            
            # Always include general compatibility explanations
            explanations.extend(self._generate_general_explanations(drink, user_preference, user_filter))
            
            # Include feedback-based explanations
            explanations.extend(self._generate_feedback_explanations(user_id, drink, user_interactions))
            
            # Include quiz-based explanations
            explanations.extend(await self._generate_quiz_explanations(user_id, drink))
            
            # Add confidence explanation
            explanations.append(self._generate_confidence_explanation(recommendation_score))
            
            # Remove duplicates and limit to top 3
            unique_explanations = list(dict.fromkeys(explanations))
            return unique_explanations[:3]
            
        except Exception as e:
            self.logger.error(f"Error generating explanation: {str(e)}")
            return ["Recommended based on your preferences"]
    
    def _generate_content_explanations(
        self, 
        drink: Drink, 
        user_preference: Optional[UserPreference],
        user_interactions: Dict[str, Any]
    ) -> List[str]:
        """Generate content-based explanations"""
        explanations = []
        
        try:
            if user_preference:
                # Sweetness explanation
                sweetness_diff = abs(drink.sweetness_level - user_preference.sweetness_preference)
                if sweetness_diff <= 2:
                    explanations.append(f"Matches your preferred sweetness level ({drink.sweetness_level}/10)")
                elif sweetness_diff <= 4:
                    explanations.append(f"Close to your preferred sweetness level")
                
                # Bitterness explanation
                if hasattr(user_preference, 'bitterness_preference') and user_preference.bitterness_preference:
                    bitterness_diff = abs(5 - user_preference.bitterness_preference)
                    explanations.append(f"Bitterness level suits your taste")
                
                # Nutritional explanations
                if drink.sugar_content <= user_preference.sugar_limit:
                    explanations.append(f"Within your sugar limit ({drink.sugar_content}g)")
                
                if drink.caffeine_content <= user_preference.caffeine_limit:
                    explanations.append(f"Fits your caffeine preferences ({drink.caffeine_content}mg)")
                
                # Price explanation
                if drink.price_tier == user_preference.preferred_price_tier:
                    explanations.append(f"Within your preferred price range ({drink.price_tier})")
                
                # Category explanation
                if user_preference.preferred_categories and drink.category in user_preference.preferred_categories:
                    explanations.append(f"From your preferred category: {drink.category}")
            
            # Add ingredient-based explanations for favorites
            if drink.drink_id in user_interactions["favorites"]:
                explanations.append("Similar to your favorite drinks")
            
        except Exception as e:
            self.logger.error(f"Error generating content explanations: {str(e)}")
        
        return explanations
    
    async def _generate_collaborative_explanations(self, user_id: int, drink: Drink) -> List[str]:
        """Generate collaborative filtering explanations"""
        explanations = []
        
        try:
            # Find users with similar preferences
            similar_users_result = await self.db.execute(
                select(UserDrinkInteraction.user_id)
                .where(
                    UserDrinkInteraction.drink_id == drink.drink_id,
                    UserDrinkInteraction.is_favorite == True,
                    UserDrinkInteraction.user_id != user_id
                )
                .limit(5)
            )
            similar_users = [u[0] for u in similar_users_result.scalars().all()]
            
            if similar_users:
                explanations.append(f"Users with similar taste also enjoyed this drink")
                explanations.append(f"Popular among users who like similar drinks")
            
        except Exception as e:
            self.logger.error(f"Error generating collaborative explanations: {str(e)}")
        
        return explanations
    
    def _generate_general_explanations(
        self, 
        drink: Drink, 
        user_preference: Optional[UserPreference],
        user_filter: Optional[UserFilter]
    ) -> List[str]:
        """Generate general compatibility explanations"""
        explanations = []
        
        try:
            # Health-based explanations
            if drink.calorie_content < 200:
                explanations.append("Low-calorie option")
            
            if drink.caffeine_content == 0:
                explanations.append("Caffeine-free choice")
            elif drink.caffeine_content < 50:
                explanations.append("Low caffeine content")
            
            # Safety and dietary explanations
            if not drink.is_alcoholic:
                explanations.append("Non-alcoholic and safe for all ages")
            
            # Ingredient-based explanations
            if hasattr(drink, 'ingredients') and drink.ingredients:
                allergen_free = True
                for ingredient in drink.ingredients:
                    if ingredient.is_allergen:
                        allergen_free = False
                        break
                
                if allergen_free:
                    explanations.append("Free from common allergens")
            
            # Time-based explanations
            if user_filter and hasattr(user_filter, 'time_sensitivity'):
                # Would implement time-based logic here
                explanations.append("Suitable for current time of day")
            
            # Category-based general explanations
            if drink.category == "coffee":
                explanations.append("Perfect coffee choice")
            elif drink.category == "tea":
                explanations.append("Healthy tea selection")
            elif drink.category == "smoothie":
                explanations.append("Nutritious smoothie option")
            elif drink.category == "water":
                explanations.append("Refreshing hydration choice")
            
        except Exception as e:
            self.logger.error(f"Error generating general explanations: {str(e)}")
        
        return explanations
    
    def _generate_feedback_explanations(
        self, 
        user_id: int, 
        drink: Drink, 
        user_interactions: Dict[str, Any]
    ) -> List[str]:
        """Generate feedback-based explanations"""
        explanations = []
        
        try:
            drink_id = drink.drink_id
            
            # Check for positive feedback
            if drink_id in user_interactions["interactions"]:
                interaction = user_interactions["interactions"][drink_id]
                if interaction.rating >= 4.0:
                    explanations.append("Based on your high ratings for similar drinks")
                elif interaction.rating >= 3.0:
                    explanations.append("Similar to drinks you've rated positively")
            
            # Check for feedback patterns
            if drink_id in user_interactions["feedback"]:
                feedback = user_interactions["feedback"][drink_id]
                if feedback.feedback_type == "love_it":
                    explanations.append("You loved a similar drink")
                elif feedback.feedback_type == "perfect":
                    explanations.append("Matches drinks you've called 'perfect'")
            
            # Adjust based on "not for me" feedback
            if drink_id in user_interactions["feedback"]:
                feedback = user_interactions["feedback"][drink_id]
                if feedback.feedback_type == "not_for_me":
                    # This shouldn't happen, but just in case
                    explanations.append("Similar to a drink you didn't enjoy")
            
        except Exception as e:
            self.logger.error(f"Error generating feedback explanations: {str(e)}")
        
        return explanations
    
    async def _generate_quiz_explanations(self, user_id: int, drink: Drink) -> List[str]:
        """Generate explanations based on quiz results"""
        explanations = []
        
        try:
            # Get user's quiz results
            quiz_results = await self.db.execute(
                select(TasteQuizResult).where(TasteQuizResult.user_id == user_id)
            )
            answers = quiz_results.scalars().all()
            
            if not answers:
                return explanations
            
            # Analyze quiz answers to generate explanations
            for answer in answers:
                if answer.question.category == "budget":
                    if answer.answer == "$ (Under $5)" and drink.price_tier == "$":
                        explanations.append("Fits your budget preference")
                    elif answer.answer == "$$ ($5-$10)" and drink.price_tier == "$$":
                        explanations.append("Within your budget range")
                    elif answer.answer == "$$$ (Over $10)" and drink.price_tier == "$$$":
                        explanations.append("Matches your willingness to spend more")
                
                elif answer.question.category == "sweetness":
                    if answer.answer in ["Very sweet", "Slightly sweet"] and drink.sweetness_level >= 6:
                        explanations.append("Matches your sweetness preference from quiz")
                    elif answer.answer == "Black" and drink.sweetness_level <= 3:
                        explanations.append("Aligns with your preference for less sweet drinks")
                
                elif answer.question.category == "caffeine":
                    if answer.answer == "Decaffeinated" and drink.caffeine_content == 0:
                        explanations.append("Perfect match for your decaf preference")
                    elif answer.answer == "Caffeinated" and drink.caffeine_content > 0:
                        explanations.append("Provides the caffeine boost you prefer")
                
                elif answer.question.category == "adventure":
                    if int(answer.answer) >= 7 and drink.category in ["experimental", "innovative"]:
                        explanations.append("Perfect for your adventurous taste")
            
        except Exception as e:
            self.logger.error(f"Error generating quiz explanations: {str(e)}")
        
        return explanations
    
    def _generate_confidence_explanation(self, score: float) -> str:
        """Generate confidence-based explanation"""
        if score >= 0.8:
            return "Highly recommended match"
        elif score >= 0.6:
            return "Good match for your preferences"
        elif score >= 0.4:
            return "Suitable option based on your profile"
        else:
            return "Potential match worth trying"
    
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
            # Get interactions
            interactions_result = await self.db.execute(
                select(UserDrinkInteraction).where(UserDrinkInteraction.user_id == user_id)
            )
            interactions = {i.drink_id: i for i in interactions_result.scalars().all()}
            
            # Get feedback
            feedback_result = await self.db.execute(
                select(UserFeedback).where(UserFeedback.user_id == user_id)
            )
            feedback = {f.drink_id: f for f in feedback_result.scalars().all()}
            
            # Get favorites (simplified - just use interactions with is_favorite=True)
            favorites = [drink_id for drink_id, interaction in interactions.items() if interaction.is_favorite]
            
            return {
                "interactions": interactions,
                "feedback": feedback,
                "favorites": favorites
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user interactions: {str(e)}")
            return {"interactions": {}, "feedback": {}, "favorites": []}
    
    async def batch_generate_explanations(
        self, 
        user_id: int, 
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate explanations for multiple recommendations
        
        Args:
            user_id: User ID
            recommendations: List of recommendation dictionaries
            
        Returns:
            List of recommendations with explanations
        """
        try:
            explained_recommendations = []
            
            for rec in recommendations:
                drink = rec["drink"]
                score = rec["score"]
                rec_type = rec.get("type", "hybrid")
                
                explanations = await self.generate_explanation(user_id, drink, score, rec_type)
                
                explained_rec = rec.copy()
                explained_rec["explanations"] = explanations
                explained_recommendations.append(explained_rec)
            
            return explained_recommendations
            
        except Exception as e:
            self.logger.error(f"Error batch generating explanations: {str(e)}")
            return recommendations
    
    async def get_explanation_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about explanation usage
        
        Returns:
            Dictionary with explanation analytics
        """
        try:
            # This would track explanation metrics in a real implementation
            # For now, return basic stats
            return {
                "total_explanations_generated": 0,
                "average_explanations_per_recommendation": 0,
                "most_common_explanation_types": [],
                "user_engagement_with_explanations": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting explanation analytics: {str(e)}")
            return {
                "total_explanations_generated": 0,
                "average_explanations_per_recommendation": 0,
                "most_common_explanation_types": [],
                "user_engagement_with_explanations": 0
            }
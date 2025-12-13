"""
User preferences service for DrinkWise backend.
Handles user taste preferences, dietary restrictions, and filtering criteria.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import logging

from models import UserPreference, Users
from .base import BaseService
from pydantic_models import UserPreference as UserPreferenceModel, UserPreferenceUpdate

logger = logging.getLogger(__name__)

class PreferenceService(BaseService):
    """
    Service for handling user preferences in DrinkWise.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize preference service with database session."""
        super().__init__(db)
        
        # Default preference values
        self.DEFAULT_PREFERENCES = {
            "sweetness_preference": 5,
            "bitterness_preference": 5,
            "caffeine_limit": 400,  # mg per day
            "calorie_limit": 2000,  # per day
            "preferred_price_tier": "$$"
        }
    
    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferenceModel]:
        """
        Get user's taste preferences.
        
        Args:
            user_id: ID of user
            
        Returns:
            User preference model or None
        """
        try:
            result = await self.db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            preferences = result.scalar_one_or_none()
            
            if not preferences:
                return None
            
            return UserPreferenceModel(
                user_id=preferences.user_id,
                sweetness_preference=preferences.sweetness_preference,
                bitterness_preference=preferences.bitterness_preference,
                caffeine_limit=preferences.caffeine_limit,
                calorie_limit=preferences.calorie_limit,
                preferred_price_tier=preferences.preferred_price_tier,
                created_at=preferences.created_at,
                updated_at=preferences.updated_at
            )
            
        except Exception as e:
            self.log_error("get_user_preferences", e, {"user_id": user_id})
            return None
    
    async def create_user_preferences(self, user_id: int, preferences_data: UserPreferenceUpdate) -> Optional[UserPreferenceModel]:
        """
        Create new user preferences.
        
        Args:
            user_id: ID of user
            preferences_data: User preference update data
            
        Returns:
            Created user preference model or None
        """
        try:
            # Check if preferences already exist
            existing_preferences = await self.get_user_preferences(user_id)
            if existing_preferences:
                return await self.update_user_preferences(user_id, preferences_data)
            
            # Create new preferences with defaults
            preference_data = self.DEFAULT_PREFERENCES.copy()
            
            # Update with provided values
            if preferences_data.sweetness_preference is not None:
                preference_data["sweetness_preference"] = preferences_data.sweetness_preference
            if preferences_data.bitterness_preference is not None:
                preference_data["bitterness_preference"] = preferences_data.bitterness_preference
            if preferences_data.caffeine_limit is not None:
                preference_data["caffeine_limit"] = preferences_data.caffeine_limit
            if preferences_data.calorie_limit is not None:
                preference_data["calorie_limit"] = preferences_data.calorie_limit
            if preferences_data.preferred_price_tier is not None:
                preference_data["preferred_price_tier"] = preferences_data.preferred_price_tier
            
            # Create preference record
            new_preferences = UserPreference(
                user_id=user_id,
                sweetness_preference=preference_data["sweetness_preference"],
                bitterness_preference=preference_data["bitterness_preference"],
                caffeine_limit=preference_data["caffeine_limit"],
                calorie_limit=preference_data["calorie_limit"],
                preferred_price_tier=preference_data["preferred_price_tier"]
            )
            
            self.db.add(new_preferences)
            await self.db.execute(
                            update(Users)
                            .where(Users.user_id == user_id)
                            .values(preference_finished=True)
                        )
            await self.db.commit()
            await self.db.refresh(new_preferences)
            
            # Return created preferences
            return UserPreferenceModel(
                user_id=new_preferences.user_id,
                sweetness_preference=new_preferences.sweetness_preference,
                bitterness_preference=new_preferences.bitterness_preference,
                caffeine_limit=new_preferences.caffeine_limit,
                calorie_limit=new_preferences.calorie_limit,
                preferred_price_tier=new_preferences.preferred_price_tier,
                created_at=new_preferences.created_at,
                updated_at=new_preferences.updated_at
            )
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("create_user_preferences", e, {"user_id": user_id})
            return None
    
    async def update_user_preferences(self, user_id: int, update_data: UserPreferenceUpdate) -> Optional[UserPreferenceModel]:
        """
        Update user's taste preferences.
        
        Args:
            user_id: ID of user
            update_data: Updated preference data
            
        Returns:
            Updated user preference model or None
        """
        try:
            # Get existing preferences or create new ones
            existing_preferences = await self.get_user_preferences(user_id)
            if not existing_preferences:
                return await self.create_user_preferences(user_id, update_data)
            
            # Prepare update values
            update_values = {}
            
            if update_data.sweetness_preference is not None:
                update_values["sweetness_preference"] = update_data.sweetness_preference
            if update_data.bitterness_preference is not None:
                update_values["bitterness_preference"] = update_data.bitterness_preference
            if update_data.caffeine_limit is not None:
                update_values["caffeine_limit"] = update_data.caffeine_limit
            if update_data.calorie_limit is not None:
                update_values["calorie_limit"] = update_data.calorie_limit
            if update_data.preferred_price_tier is not None:
                update_values["preferred_price_tier"] = update_data.preferred_price_tier
            
            if not update_values:
                # No updates provided
                return existing_preferences
            
            # Add updated timestamp
            update_values["updated_at"] = datetime.now()
            
            # Update preferences
            await self.db.execute(
                update(UserPreference)
                .where(UserPreference.user_id == user_id)
                .values(**update_values)
            )
            await self.db.execute(
                update(Users)
                .where(Users.user_id == user_id)
                .values(preference_finished=True)
            )

            await self.db.commit()
            
            # Return updated preferences
            updated_preferences = await self.get_user_preferences(user_id)
            
            self.log_operation("update_user_preferences", {
                "user_id": user_id,
                "updated_fields": list(update_values.keys())
            })
            
            return updated_preferences
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("update_user_preferences", e, {"user_id": user_id})
            return None
    
    async def delete_user_preferences(self, user_id: int) -> bool:
        """
        Delete user's taste preferences.
        
        Args:
            user_id: ID of user
            
        Returns:
            True if deleted successfully
        """
        try:
            result = await self.db.execute(
                delete(UserPreference).where(UserPreference.user_id == user_id)
            )
            
            await self.db.commit()
            
            success = result.rowcount > 0
            
            if success:
                self.log_operation("delete_user_preferences", {"user_id": user_id})
            
            return success
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("delete_user_preferences", e, {"user_id": user_id})
            return False
    
    async def ensure_user_preferences(self, user_id: int) -> UserPreferenceModel:
        """
        Ensure user has preferences (create default if none exist).
        
        Args:
            user_id: ID of user
            
        Returns:
            User preference model
        """
        preferences = await self.get_user_preferences(user_id)
        if preferences:
            return preferences
        
        # Create default preferences
        default_update = UserPreferenceUpdate()
        return await self.create_user_preferences(user_id, default_update)
    
    async def get_preferences_for_filtering(self, user_id: int) -> Dict[str, Any]:
        """
        Get preferences formatted for filtering drinks.
        
        Args:
            user_id: ID of user
            
        Returns:
            Dictionary of filtering preferences
        """
        preferences = await self.ensure_user_preferences(user_id)
        
        return {
            "max_sweetness": preferences.sweetness_preference,
            "max_caffeine": preferences.caffeine_limit,
            "max_calories": preferences.calorie_limit,
            "preferred_price_tier": preferences.preferred_price_tier,
        }
    
    async def get_preference_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about user's preferences.
        
        Args:
            user_id: ID of user
            
        Returns:
            Dictionary with preference statistics
        """
        try:
            preferences = await self.get_user_preferences(user_id)
            if not preferences:
                return {
                    "has_preferences": False,
                    "message": "No preferences set"
                }
            
            # Analyze preference patterns
            sweetness_taste = self._analyze_sweetness_preference(preferences.sweetness_preference)
            bitterness_taste = self._analyze_bitterness_preference(preferences.bitterness_preference)
            caffeine_tolerance = self._analyze_caffeine_tolerance(preferences.caffeine_limit)
            calorie_consciousness = self._analyze_calorie_consciousness(preferences.calorie_limit)
            
            return {
                "has_preferences": True,
                "user_id": user_id,
                "sweetness": {
                    "level": preferences.sweetness_preference,
                    "description": sweetness_taste
                },
                "bitterness": {
                    "level": preferences.bitterness_preference,
                    "description": bitterness_taste
                },
                "caffeine": {
                    "limit": preferences.caffeine_limit,
                    "tolerance": caffeine_tolerance
                },
                "calories": {
                    "limit": preferences.calorie_limit,
                    "consciousness": calorie_consciousness
                },
                "price_tier": {
                    "preferred": preferences.preferred_price_tier,
                    "description": self._describe_price_tier(preferences.preferred_price_tier)
                },
                "preference_strength": self._calculate_preference_strength(preferences),
                "created_at": preferences.created_at,
                "updated_at": preferences.updated_at
            }
            
        except Exception as e:
            self.log_error("get_preference_statistics", e, {"user_id": user_id})
            return {"error": "Failed to get preference statistics"}
    
    def _analyze_sweetness_preference(self, sweetness_level: int) -> str:
        """Analyze sweetness preference level."""
        if sweetness_level <= 2:
            return "Very low sweetness preference - enjoys bitter/savory drinks"
        elif sweetness_level <= 4:
            return "Low sweetness preference - prefers mildly bitter drinks"
        elif sweetness_level <= 6:
            return "Balanced sweetness preference - enjoys moderately sweet drinks"
        elif sweetness_level <= 8:
            return "High sweetness preference - prefers sweet drinks"
        else:
            return "Very high sweetness preference - loves very sweet drinks"
    
    def _analyze_bitterness_preference(self, bitterness_level: int) -> str:
        """Analyze bitterness preference level."""
        if bitterness_level <= 2:
            return "Low bitterness tolerance - prefers mild, smooth drinks"
        elif bitterness_level <= 4:
            return "Moderate bitterness tolerance - likes some complexity"
        elif bitterness_level <= 6:
            return "Balanced bitterness preference - enjoys varied flavor profiles"
        elif bitterness_level <= 8:
            return "High bitterness preference - appreciates bold, complex flavors"
        else:
            return "Very high bitterness preference - loves intense, bitter drinks"
    
    def _analyze_caffeine_tolerance(self, caffeine_limit: int) -> str:
        """Analyze caffeine tolerance."""
        if caffeine_limit <= 100:
            return "Low caffeine sensitivity - prefers caffeine-free or very low caffeine drinks"
        elif caffeine_limit <= 200:
            return "Moderate caffeine sensitivity - enjoys 1-2 caffeinated drinks per day"
        elif caffeine_limit <= 400:
            return "Normal caffeine tolerance - can handle standard daily caffeine intake"
        elif caffeine_limit <= 600:
            return "High caffeine tolerance - enjoys multiple caffeinated drinks"
        else:
            return "Very high caffeine tolerance - can handle excessive caffeine intake"
    
    def _analyze_calorie_consciousness(self, calorie_limit: int) -> str:
        """Analyze calorie consciousness."""
        if calorie_limit <= 1200:
            return "Very health conscious - strict calorie control"
        elif calorie_limit <= 1600:
            return "Health conscious - moderate calorie awareness"
        elif calorie_limit <= 2000:
            return "Balanced approach - moderate calorie consideration"
        elif calorie_limit <= 2500:
            return "Flexible approach - relaxed calorie monitoring"
        else:
            return "Liberal approach - minimal calorie restrictions"
    
    def _describe_price_tier(self, price_tier: str) -> str:
        """Describe price tier preference."""
        tier_descriptions = {
            "$": "Budget-conscious - prefers affordable drinks",
            "$$": "Moderate spending - balanced price-quality preference",
            "$$$": "Premium preference - willing to pay for quality"
        }
        return tier_descriptions.get(price_tier, "Unknown price preference")
    
    def _calculate_preference_strength(self, preferences: UserPreferenceModel) -> str:
        """Calculate overall preference strength."""
        # Check if user has set specific preferences vs using defaults
        default_count = 0
        
        if preferences.sweetness_preference == self.DEFAULT_PREFERENCES["sweetness_preference"]:
            default_count += 1
        if preferences.bitterness_preference == self.DEFAULT_PREFERENCES["bitterness_preference"]:
            default_count += 1
        if preferences.caffeine_limit == self.DEFAULT_PREFERENCES["caffeine_limit"]:
            default_count += 1
        if preferences.calorie_limit == self.DEFAULT_PREFERENCES["calorie_limit"]:
            default_count += 1
        if preferences.preferred_price_tier == self.DEFAULT_PREFERENCES["preferred_price_tier"]:
            default_count += 1
        
        if default_count >= 4:
            return "Low - using mostly default preferences"
        elif default_count >= 2:
            return "Medium - some customized preferences"
        else:
            return "High - well-defined personal preferences"
    
    async def get_compatible_drinks(self, user_id: int, drink_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter drinks based on user preferences.
        
        Args:
            user_id: ID of user
            drink_candidates: List of drink dictionaries
            
        Returns:
            List of drinks compatible with user preferences
        """
        try:
            preferences = await self.ensure_user_preferences(user_id)
            
            compatible_drinks = []
            
            for drink in drink_candidates:
                score = 0
                reasons = []
                
                # Sweetness compatibility
                if drink.get("sweetness_level", 0) <= preferences.sweetness_preference:
                    score += 1
                    reasons.append(f"Sweetness level {drink.get('sweetness_level')} is within your preference of {preferences.sweetness_preference}")
                else:
                    score -= 1
                    reasons.append(f"Drink sweetness {drink.get('sweetness_level')} exceeds your preference of {preferences.sweetness_preference}")
                
                # Caffeine compatibility
                if drink.get("caffeine_content", 0) <= preferences.caffeine_limit:
                    score += 1
                    reasons.append(f"Caffeine content {drink.get('caffeine_content')}mg is within your limit of {preferences.caffeine_limit}mg")
                else:
                    score -= 2  # Penalty for exceeding caffeine limit
                    reasons.append(f"Caffeine content {drink.get('caffeine_content')}mg exceeds your limit of {preferences.caffeine_limit}mg")
                
                # Calorie compatibility
                if drink.get("calorie_content", 0) <= preferences.calorie_limit:
                    score += 1
                    reasons.append(f"Calorie content {drink.get('calorie_content')} is within your limit of {preferences.calorie_limit}")
                else:
                    score -= 1
                    reasons.append(f"Calorie content {drink.get('calorie_content')} exceeds your limit of {preferences.calorie_limit}")
                
                # Price tier compatibility
                if drink.get("price_tier") == preferences.preferred_price_tier:
                    score += 1
                    reasons.append(f"Price tier '{drink.get('price_tier')}' matches your preference")
                elif self._get_price_tier_index(drink.get("price_tier", "")) <= self._get_price_tier_index(preferences.preferred_price_tier):
                    score += 0.5
                    reasons.append(f"Price tier '{drink.get('price_tier')}' is within your acceptable range")
                
                # Add drink with compatibility score
                drink["compatibility_score"] = max(0, score)  # Ensure non-negative
                drink["compatibility_reasons"] = reasons
                drink["preference_match"] = score > 0
                
                compatible_drinks.append(drink)
            
            # Sort by compatibility score (highest first)
            compatible_drinks.sort(key=lambda x: x.get("compatibility_score", 0), reverse=True)
            
            return compatible_drinks
            
        except Exception as e:
            self.log_error("get_compatible_drinks", e, {"user_id": user_id})
            return drink_candidates  # Return original list if filtering fails
    
    def _get_price_tier_index(self, price_tier: str) -> int:
        """Get price tier index for comparison."""
        tier_indices = {"$": 0, "$$": 1, "$$$": 2}
        return tier_indices.get(price_tier, 1)  # Default to middle tier
    
    async def export_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Export user preferences in a shareable format.
        
        Args:
            user_id: ID of user
            
        Returns:
            Dictionary with exportable preferences
        """
        try:
            preferences = await self.ensure_user_preferences(user_id)
            
            return {
                "export_version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "preferences": {
                    "sweetness_preference": preferences.sweetness_preference,
                    "bitterness_preference": preferences.bitterness_preference,
                    "caffeine_limit": preferences.caffeine_limit,
                    "calorie_limit": preferences.calorie_limit,
                    "preferred_price_tier": preferences.preferred_price_tier,
                },
                "analysis": await self.get_preference_statistics(user_id)
            }
            
        except Exception as e:
            self.log_error("export_user_preferences", e, {"user_id": user_id})
            return None
    
    async def import_user_preferences(self, user_id: int, preferences_data: Dict[str, Any]) -> Optional[UserPreferenceModel]:
        """
        Import user preferences from shared data.
        
        Args:
            user_id: ID of user
            preferences_data: Dictionary with preferences data
            
        Returns:
            Imported user preference model or None
        """
        try:
            # Validate import data
            if "preferences" not in preferences_data:
                return None
            
            prefs = preferences_data["preferences"]
            
            # Create preference update object
            update_data = UserPreferenceUpdate(
                sweetness_preference=prefs.get("sweetness_preference"),
                bitterness_preference=prefs.get("bitterness_preference"),
                caffeine_limit=prefs.get("caffeine_limit"),
                calorie_limit=prefs.get("calorie_limit"),
                preferred_price_tier=prefs.get("preferred_price_tier"),
            )
            
            return await self.update_user_preferences(user_id, update_data)
            
        except Exception as e:
            self.log_error("import_user_preferences", e, {"user_id": user_id})
            return None
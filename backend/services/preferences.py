from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime
import logging
from typing import Optional, Dict, Any, List

from .base import BaseService, ValidationError
from models import UserPreference, Users
from pydantic_models import (
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse
)

class PreferenceService(BaseService[UserPreference, UserPreferenceCreate, UserPreferenceUpdate]):
    """
    Service for managing user taste preferences and health targets
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(UserPreference, db)
        self.logger = logging.getLogger("preference_service")
    
    async def get_user_preference(self, user_id: int) -> Optional[UserPreference]:
        """
        Get user preference profile
        
        Args:
            user_id: User ID
            
        Returns:
            UserPreference object or None
        """
        try:
            result = await self.db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user preference for user {user_id}: {str(e)}")
            return None
    
    async def create_user_preference(self, user_id: int, preference_data: UserPreferenceCreate) -> Optional[UserPreferenceResponse]:
        """
        Create user preference profile
        
        Args:
            user_id: User ID
            preference_data: Preference data
            
        Returns:
            UserPreferenceResponse or None
        """
        try:
            # Check if preference already exists
            existing_preference = await self.get_user_preference(user_id)
            if existing_preference:
                raise ValidationError("User preference already exists")
            
            # Validate preference data
            if not self._validate_preference_data(preference_data):
                raise ValidationError("Invalid preference data")
            
            # Create preference
            preference_dict = preference_data.dict()
            preference_dict['user_id'] = user_id
            preference_dict['created_at'] = datetime.now()
            preference_dict['updated_at'] = datetime.now()
            
            preference = await self.create(UserPreferenceCreate(**preference_dict))
            if not preference:
                return None
            
            return UserPreferenceResponse.from_orm(preference)
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating user preference: {str(e)}")
            return None
    
    async def update_user_preference(self, user_id: int, update_data: UserPreferenceUpdate) -> Optional[UserPreferenceResponse]:
        """
        Update user preference profile
        
        Args:
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated UserPreferenceResponse or None
        """
        try:
            # Get existing preference
            existing_preference = await self.get_user_preference(user_id)
            if not existing_preference:
                raise ValidationError("User preference not found")
            
            # Validate update data
            if not self._validate_preference_update(update_data):
                raise ValidationError("Invalid preference update data")
            
            # Add updated_at timestamp
            update_dict = update_data.dict(exclude_unset=True)
            update_dict['updated_at'] = datetime.now()
            
            # Update preference
            updated_preference = await self.update(existing_preference.user_id, UserPreferenceUpdate(**update_dict))
            if not updated_preference:
                return None
            
            return UserPreferenceResponse.from_orm(updated_preference)
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating user preference: {str(e)}")
            return None
    
    async def delete_user_preference(self, user_id: int) -> bool:
        """
        Delete user preference profile
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            existing_preference = await self.get_user_preference(user_id)
            if not existing_preference:
                return False
            
            return await self.delete(existing_preference.user_id)
            
        except Exception as e:
            self.logger.error(f"Error deleting user preference: {str(e)}")
            return False
    
    async def get_compatible_drinks(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get drinks compatible with user preferences
        
        Args:
            user_id: User ID
            limit: Maximum number of drinks to return
            
        Returns:
            List of compatible drinks with compatibility scores
        """
        try:
            preference = await self.get_user_preference(user_id)
            if not preference:
                return []
            
            # This would be integrated with CatalogService for actual filtering
            # For now, return empty list as placeholder
            self.logger.info(f"Getting compatible drinks for user {user_id}")
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting compatible drinks: {str(e)}")
            return []
    
    def _validate_preference_data(self, data: UserPreferenceCreate) -> bool:
        """
        Validate user preference data
        
        Args:
            data: Preference data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Validate sweetness preference
            if not (1 <= data.sweetness_preference <= 10):
                return False
            
            # Validate bitterness preference
            if not (1 <= data.bitterness_preference <= 10):
                return False
            
            # Validate limits
            if data.sugar_limit < 0 or data.caffeine_limit < 0 or data.calorie_limit < 0:
                return False
            
            # Validate price tier
            if data.preferred_price_tier not in ["$", "$$", "$$$"]:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_preference_update(self, data: UserPreferenceUpdate) -> bool:
        """
        Validate user preference update data
        
        Args:
            data: Update data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Validate individual fields if present
            if data.sweetness_preference is not None and not (1 <= data.sweetness_preference <= 10):
                return False
            
            if data.bitterness_preference is not None and not (1 <= data.bitterness_preference <= 10):
                return False
            
            if data.sugar_limit is not None and data.sugar_limit < 0:
                return False
            
            if data.caffeine_limit is not None and data.caffeine_limit < 0:
                return False
            
            if data.calorie_limit is not None and data.calorie_limit < 0:
                return False
            
            if data.preferred_price_tier is not None and data.preferred_price_tier not in ["$", "$$", "$$$"]:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def get_preference_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get summary of user preferences for analytics
        
        Args:
            user_id: User ID
            
        Returns:
            Preference summary dictionary
        """
        try:
            preference = await self.get_user_preference(user_id)
            if not preference:
                return None
            
            return {
                "user_id": user_id,
                "sweetness_preference": preference.sweetness_preference,
                "bitterness_preference": preference.bitterness_preference,
                "preferred_categories": preference.preferred_categories or [],
                "sugar_limit": preference.sugar_limit,
                "caffeine_limit": preference.caffeine_limit,
                "calorie_limit": preference.calorie_limit,
                "preferred_price_tier": preference.preferred_price_tier,
                "has_time_sensitivity": bool(preference.time_sensitivity),
                "has_mode_preferences": bool(preference.mode_preferences),
                "created_at": preference.created_at,
                "updated_at": preference.updated_at
            }
            
        except Exception as e:
            self.logger.error(f"Error getting preference summary: {str(e)}")
            return None
    
    async def bulk_update_preferences(self, updates: List[Dict[str, Any]]) -> bool:
        """
        Bulk update multiple user preferences (for admin operations)
        
        Args:
            updates: List of update dictionaries
            
        Returns:
            True if successful
        """
        try:
            for update_data in updates:
                user_id = update_data.get('user_id')
                if user_id:
                    await self.update_user_preference(user_id, UserPreferenceUpdate(**update_data))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error bulk updating preferences: {str(e)}")
            return False
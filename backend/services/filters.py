from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from datetime import datetime
import logging
from typing import Optional, Dict, Any, List

from .base import BaseService, ValidationError
from models import UserFilter, Drink
from pydantic_models import (
    UserFilterCreate, UserFilterUpdate, UserFilterResponse, DrinkSearchParams
)

class FilterService(BaseService[UserFilter, UserFilterCreate, UserFilterUpdate]):
    """
    Service for managing user drink filters and search parameters
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(UserFilter, db)
        self.logger = logging.getLogger("filter_service")
    
    async def get_user_filter(self, user_id: int) -> Optional[UserFilter]:
        """
        Get user's active filter
        
        Args:
            user_id: User ID
            
        Returns:
            UserFilter object or None
        """
        try:
            result = await self.db.execute(
                select(UserFilter).where(UserFilter.user_id == user_id, UserFilter.is_active == True)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user filter for user {user_id}: {str(e)}")
            return None
    
    async def create_user_filter(self, user_id: int, filter_data: UserFilterCreate) -> Optional[UserFilterResponse]:
        """
        Create user filter
        
        Args:
            user_id: User ID
            filter_data: Filter data
            
        Returns:
            UserFilterResponse or None
        """
        try:
            # Deactivate existing filters for this user
            await self.db.execute(
                update(UserFilter)
                .where(UserFilter.user_id == user_id)
                .values(is_active=False)
            )
            
            # Create new filter
            filter_dict = filter_data.dict()
            filter_dict['user_id'] = user_id
            filter_dict['created_at'] = datetime.now()
            filter_dict['updated_at'] = datetime.now()
            filter_dict['is_active'] = True
            
            filter_obj = await self.create(UserFilterCreate(**filter_dict))
            if not filter_obj:
                return None
            
            return UserFilterResponse.from_orm(filter_obj)
            
        except Exception as e:
            self.logger.error(f"Error creating user filter: {str(e)}")
            return None
    
    async def update_user_filter(self, user_id: int, update_data: UserFilterUpdate) -> Optional[UserFilterResponse]:
        """
        Update user filter
        
        Args:
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated UserFilterResponse or None
        """
        try:
            # Get existing filter
            existing_filter = await self.get_user_filter(user_id)
            if not existing_filter:
                raise ValidationError("User filter not found")
            
            # Validate update data
            if not self._validate_filter_update(update_data):
                raise ValidationError("Invalid filter update data")
            
            # Add updated_at timestamp
            update_dict = update_data.dict(exclude_unset=True)
            update_dict['updated_at'] = datetime.now()
            
            # Update filter
            updated_filter = await self.update(existing_filter.user_id, UserFilterUpdate(**update_dict))
            if not updated_filter:
                return None
            
            return UserFilterResponse.from_orm(updated_filter)
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating user filter: {str(e)}")
            return None
    
    async def delete_user_filter(self, user_id: int) -> bool:
        """
        Delete/deactivate user filter
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            existing_filter = await self.get_user_filter(user_id)
            if not existing_filter:
                return False
            
            await self.db.execute(
                update(UserFilter)
                .where(UserFilter.user_id == user_id)
                .values(is_active=False, updated_at=datetime.now())
            )
            await self.db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting user filter: {str(e)}")
            return False
    
    async def apply_filters_to_query(self, base_query, filter_data: UserFilter):
        """
        Apply filter criteria to a SQLAlchemy query
        
        Args:
            base_query: SQLAlchemy query object
            filter_data: User filter data
            
        Returns:
            Filtered query object
        """
        try:
            query = base_query
            
            # Apply budget tier filter
            if filter_data.budget_tier:
                query = query.where(Drink.price_tier == filter_data.budget_tier)
            
            # Apply sweetness filter
            if filter_data.sweetness_filter:
                query = query.where(Drink.sweetness_level <= filter_data.sweetness_filter)
            
            # Apply caffeine range filter
            if filter_data.caffeine_min is not None:
                query = query.where(Drink.caffeine_content >= filter_data.caffeine_min)
            
            if filter_data.caffeine_max is not None:
                query = query.where(Drink.caffeine_content <= filter_data.caffeine_max)
            
            # Apply ingredient exclusions
            if filter_data.excluded_ingredients:
                for ingredient in filter_data.excluded_ingredients:
                    query = query.where(~Drink.ingredients.any(ingredient_name=ingredient))
            
            # Apply category exclusions
            if filter_data.excluded_categories:
                for category in filter_data.excluded_categories:
                    query = query.where(Drink.category != category)
            
            return query
            
        except Exception as e:
            self.logger.error(f"Error applying filters to query: {str(e)}")
            return base_query
    
    async def search_drinks(self, search_params: DrinkSearchParams, user_filter: Optional[UserFilter] = None) -> List[Drink]:
        """
        Search drinks based on parameters and user filter
        
        Args:
            search_params: Search parameters
            user_filter: Optional user filter
            
        Returns:
            List of matching drinks
        """
        try:
            # Start with base query
            query = select(Drink)
            
            # Apply search text filter
            if search_params.search_text:
                search_term = f"%{search_params.search_text.lower()}%"
                query = query.where(
                    or_(
                        Drink.name.ilike(search_term),
                        Drink.description.ilike(search_term)
                    )
                )
            
            # Apply search parameters
            if search_params.category:
                query = query.where(Drink.category == search_params.category)
            
            if search_params.price_tier:
                query = query.where(Drink.price_tier == search_params.price_tier)
            
            if search_params.max_sweetness:
                query = query.where(Drink.sweetness_level <= search_params.max_sweetness)
            
            if search_params.min_caffeine:
                query = query.where(Drink.caffeine_content >= search_params.min_caffeine)
            
            if search_params.max_caffeine:
                query = query.where(Drink.caffeine_content <= search_params.max_caffeine)
            
            if search_params.is_alcoholic is not None:
                query = query.where(Drink.is_alcoholic == search_params.is_alcoholic)
            
            # Apply user filter if available
            if user_filter:
                query = await self.apply_filters_to_query(query, user_filter)
            
            # Apply pagination
            offset = (search_params.page - 1) * search_params.limit
            query = query.offset(offset).limit(search_params.limit)
            
            # Execute query
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            self.logger.error(f"Error searching drinks: {str(e)}")
            return []
    
    def _validate_filter_data(self, data: UserFilterCreate) -> bool:
        """
        Validate filter data
        
        Args:
            data: Filter data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Validate price tier
            if data.budget_tier and data.budget_tier not in ["$", "$$", "$$$"]:
                return False
            
            # Validate sweetness level
            if data.sweetness_filter and not (1 <= data.sweetness_filter <= 10):
                return False
            
            # Validate caffeine range
            if data.caffeine_min is not None and data.caffeine_min < 0:
                return False
            
            if data.caffeine_max is not None and data.caffeine_max < 0:
                return False
            
            if (data.caffeine_min is not None and data.caffeine_max is not None and 
                data.caffeine_min > data.caffeine_max):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_filter_update(self, data: UserFilterUpdate) -> bool:
        """
        Validate filter update data
        
        Args:
            data: Update data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Validate price tier
            if data.budget_tier and data.budget_tier not in ["$", "$$", "$$$"]:
                return False
            
            # Validate sweetness level
            if data.sweetness_filter and not (1 <= data.sweetness_filter <= 10):
                return False
            
            # Validate caffeine range
            if data.caffeine_min is not None and data.caffeine_min < 0:
                return False
            
            if data.caffeine_max is not None and data.caffeine_max < 0:
                return False
            
            if (data.caffeine_min is not None and data.caffeine_max is not None and 
                data.caffeine_min > data.caffeine_max):
                return False
            
            return True
            
        except Exception:
            return False
    
    async def get_filter_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get summary of user filter for analytics
        
        Args:
            user_id: User ID
            
        Returns:
            Filter summary dictionary
        """
        try:
            user_filter = await self.get_user_filter(user_id)
            if not user_filter:
                return None
            
            return {
                "user_id": user_id,
                "budget_tier": user_filter.budget_tier,
                "sweetness_filter": user_filter.sweetness_filter,
                "caffeine_min": user_filter.caffeine_min,
                "caffeine_max": user_filter.caffeine_max,
                "excluded_ingredients": user_filter.excluded_ingredients or [],
                "excluded_categories": user_filter.excluded_categories or [],
                "is_active": user_filter.is_active,
                "created_at": user_filter.created_at,
                "updated_at": user_filter.updated_at
            }
            
        except Exception as e:
            self.logger.error(f"Error getting filter summary: {str(e)}")
            return None
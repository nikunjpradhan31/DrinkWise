from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging
from typing import Optional, Dict, Any, List

from .base import BaseService, ValidationError
from models import Drink, DrinkIngredient, DrinkTag
from pydantic_models import (
    DrinkCreate, DrinkResponse, DrinkSearchParams, PaginatedDrinkResponse
)

class CatalogService(BaseService[Drink, DrinkCreate, Dict]):
    """
    Service for managing drink catalog and metadata
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(Drink, db)
        self.logger = logging.getLogger("catalog_service")
    
    async def get_drink_by_id(self, drink_id: int) -> Optional[Drink]:
        """
        Get drink by ID with full details
        
        Args:
            drink_id: Drink ID
            
        Returns:
            Drink object with relationships or None
        """
        try:
            result = await self.db.execute(
                select(Drink)
                .options(
                    selectinload(Drink.ingredients),
                    selectinload(Drink.tags)
                )
                .where(Drink.drink_id == drink_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting drink by ID {drink_id}: {str(e)}")
            return None
    
    async def create_drink(self, drink_data: DrinkCreate) -> Optional[DrinkResponse]:
        """
        Create a new drink with ingredients and tags
        
        Args:
            drink_data: Drink creation data
            
        Returns:
            DrinkResponse or None
        """
        try:
            # Validate drink data
            if not self._validate_drink_data(drink_data):
                raise ValidationError("Invalid drink data")
            
            # Create drink
            drink_dict = drink_data.dict(exclude={'ingredients', 'tags'})
            drink_dict['created_at'] = datetime.now()
            drink_dict['updated_at'] = datetime.now()
            
            drink = await self.create(DrinkCreate(**drink_dict))
            if not drink:
                return None
            
            # Add ingredients if provided
            if drink_data.ingredients:
                await self._add_drink_ingredients(drink.drink_id, drink_data.ingredients)
            
            # Add tags if provided
            if drink_data.tags:
                await self._add_drink_tags(drink.drink_id, drink_data.tags)
            
            # Get full drink with relationships
            full_drink = await self.get_drink_by_id(drink.drink_id)
            if not full_drink:
                return None
            
            return DrinkResponse.from_orm(full_drink)
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating drink: {str(e)}")
            return None
    
    async def update_drink(self, drink_id: int, update_data: Dict) -> Optional[DrinkResponse]:
        """
        Update drink with ingredients and tags
        
        Args:
            drink_id: Drink ID
            update_data: Update data dictionary
            
        Returns:
            Updated DrinkResponse or None
        """
        try:
            # Get existing drink
            existing_drink = await self.get_drink_by_id(drink_id)
            if not existing_drink:
                raise ValidationError("Drink not found")
            
            # Validate update data
            if not self._validate_drink_update(update_data):
                raise ValidationError("Invalid drink update data")
            
            # Update drink basic info
            update_dict = update_data.copy()
            update_dict['updated_at'] = datetime.now()
            
            # Remove ingredients and tags from update if present
            ingredients = update_dict.pop('ingredients', None)
            tags = update_dict.pop('tags', None)
            
            # Update drink
            await self.db.execute(
                update(Drink)
                .where(Drink.drink_id == drink_id)
                .values(**update_dict)
            )
            await self.db.commit()
            
            # Update ingredients if provided
            if ingredients is not None:
                await self._update_drink_ingredients(drink_id, ingredients)
            
            # Update tags if provided
            if tags is not None:
                await self._update_drink_tags(drink_id, tags)
            
            # Get updated drink with relationships
            updated_drink = await self.get_drink_by_id(drink_id)
            if not updated_drink:
                return None
            
            return DrinkResponse.from_orm(updated_drink)
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating drink {drink_id}: {str(e)}")
            return None
    
    async def delete_drink(self, drink_id: int) -> bool:
        """
        Delete drink with all related data
        
        Args:
            drink_id: Drink ID
            
        Returns:
            True if successful
        """
        try:
            # This should cascade delete ingredients and tags due to relationships
            return await self.delete(drink_id)
        except Exception as e:
            self.logger.error(f"Error deleting drink {drink_id}: {str(e)}")
            return False
    
    async def search_drinks(self, search_params: DrinkSearchParams) -> PaginatedDrinkResponse:
        """
        Search drinks with pagination
        
        Args:
            search_params: Search parameters
            
        Returns:
            PaginatedDrinkResponse
        """
        try:
            # Build base query
            query = select(Drink).options(
                selectinload(Drink.ingredients),
                selectinload(Drink.tags)
            )
            
            # Apply filters
            query = await self._apply_search_filters(query, search_params)
            
            # Get total count for pagination
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (search_params.page - 1) * search_params.limit
            query = query.offset(offset).limit(search_params.limit)
            
            # Execute query
            result = await self.db.execute(query)
            drinks = result.scalars().all()
            
            # Convert to response format
            drink_responses = [DrinkResponse.from_orm(drink) for drink in drinks]
            total_pages = (total + search_params.limit - 1) // search_params.limit
            
            return PaginatedDrinkResponse(
                drinks=drink_responses,
                total=total,
                page=search_params.page,
                limit=search_params.limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            self.logger.error(f"Error searching drinks: {str(e)}")
            return PaginatedDrinkResponse(
                drinks=[],
                total=0,
                page=search_params.page,
                limit=search_params.limit,
                total_pages=0
            )
    
    async def get_drinks_by_category(self, category: str, limit: int = 20) -> List[DrinkResponse]:
        """
        Get drinks by category
        
        Args:
            category: Drink category
            limit: Maximum number of drinks
            
        Returns:
            List of DrinkResponse
        """
        try:
            result = await self.db.execute(
                select(Drink)
                .options(
                    selectinload(Drink.ingredients),
                    selectinload(Drink.tags)
                )
                .where(Drink.category == category)
                .limit(limit)
            )
            drinks = result.scalars().all()
            return [DrinkResponse.from_orm(drink) for drink in drinks]
            
        except Exception as e:
            self.logger.error(f"Error getting drinks by category: {str(e)}")
            return []
    
    async def get_alcoholic_drinks(self, age_verified: bool = False, limit: int = 20) -> List[DrinkResponse]:
        """
        Get alcoholic drinks (filtered by age verification)
        
        Args:
            age_verified: Whether user is age verified
            limit: Maximum number of drinks
            
        Returns:
            List of DrinkResponse
        """
        try:
            query = select(Drink).options(
                selectinload(Drink.ingredients),
                selectinload(Drink.tags)
            ).where(Drink.is_alcoholic == True)
            
            # If not age verified, limit to low alcohol content or exclude
            if not age_verified:
                query = query.where(Drink.alcohol_content <= 1.0)  # Less than 1% alcohol
            
            query = query.limit(limit)
            
            result = await self.db.execute(query)
            drinks = result.scalars().all()
            return [DrinkResponse.from_orm(drink) for drink in drinks]
            
        except Exception as e:
            self.logger.error(f"Error getting alcoholic drinks: {str(e)}")
            return []
    
    async def get_drink_categories(self) -> List[str]:
        """
        Get all available drink categories
        
        Returns:
            List of category names
        """
        try:
            result = await self.db.execute(
                select(Drink.category).distinct().order_by(Drink.category)
            )
            categories = result.scalars().all()
            return list(categories)
            
        except Exception as e:
            self.logger.error(f"Error getting drink categories: {str(e)}")
            return []
    
    async def get_popular_drinks(self, limit: int = 20) -> List[DrinkResponse]:
        """
        Get popular drinks (placeholder for future implementation)
        
        Args:
            limit: Maximum number of drinks
            
        Returns:
            List of popular DrinkResponse
        """
        try:
            # For now, return recent drinks - in future could use interaction data
            result = await self.db.execute(
                select(Drink)
                .options(
                    selectinload(Drink.ingredients),
                    selectinload(Drink.tags)
                )
                .order_by(Drink.created_at.desc())
                .limit(limit)
            )
            drinks = result.scalars().all()
            return [DrinkResponse.from_orm(drink) for drink in drinks]
            
        except Exception as e:
            self.logger.error(f"Error getting popular drinks: {str(e)}")
            return []
    
    async def _apply_search_filters(self, query, search_params: DrinkSearchParams):
        """Apply search filters to query"""
        
        # Apply search text
        if search_params.search_text:
            search_term = f"%{search_params.search_text.lower()}%"
            query = query.where(
                or_(
                    Drink.name.ilike(search_term),
                    Drink.description.ilike(search_term)
                )
            )
        
        # Apply category filter
        if search_params.category:
            query = query.where(Drink.category == search_params.category)
        
        # Apply price tier filter
        if search_params.price_tier:
            query = query.where(Drink.price_tier == search_params.price_tier)
        
        # Apply sweetness filter
        if search_params.max_sweetness:
            query = query.where(Drink.sweetness_level <= search_params.max_sweetness)
        
        # Apply caffeine filters
        if search_params.min_caffeine:
            query = query.where(Drink.caffeine_content >= search_params.min_caffeine)
        
        if search_params.max_caffeine:
            query = query.where(Drink.caffeine_content <= search_params.max_caffeine)
        
        # Apply alcoholic filter
        if search_params.is_alcoholic is not None:
            query = query.where(Drink.is_alcoholic == search_params.is_alcoholic)
        
        # Apply ingredient exclusions
        if search_params.excluded_ingredients:
            for ingredient in search_params.excluded_ingredients:
                query = query.where(~Drink.ingredients.any(ingredient_name=ingredient))
        
        return query
    
    async def _add_drink_ingredients(self, drink_id: int, ingredients: List[Dict[str, Any]]):
        """Add ingredients to a drink"""
        try:
            for ingredient_data in ingredients:
                ingredient = DrinkIngredient(
                    drink_id=drink_id,
                    ingredient_name=ingredient_data.get('name', ''),
                    quantity=ingredient_data.get('quantity'),
                    is_allergen=ingredient_data.get('is_allergen', False)
                )
                self.db.add(ingredient)
            
            await self.db.commit()
        except Exception as e:
            self.logger.error(f"Error adding drink ingredients: {str(e)}")
            await self.db.rollback()
            raise
    
    async def _add_drink_tags(self, drink_id: int, tags: List[str]):
        """Add tags to a drink"""
        try:
            for tag_name in tags:
                tag = DrinkTag(
                    drink_id=drink_id,
                    tag_name=tag_name
                )
                self.db.add(tag)
            
            await self.db.commit()
        except Exception as e:
            self.logger.error(f"Error adding drink tags: {str(e)}")
            await self.db.rollback()
            raise
    
    async def _update_drink_ingredients(self, drink_id: int, ingredients: List[Dict[str, Any]]):
        """Update drink ingredients"""
        try:
            # Delete existing ingredients
            await self.db.execute(
                delete(DrinkIngredient).where(DrinkIngredient.drink_id == drink_id)
            )
            
            # Add new ingredients
            if ingredients:
                await self._add_drink_ingredients(drink_id, ingredients)
            
        except Exception as e:
            self.logger.error(f"Error updating drink ingredients: {str(e)}")
            await self.db.rollback()
            raise
    
    async def _update_drink_tags(self, drink_id: int, tags: List[str]):
        """Update drink tags"""
        try:
            # Delete existing tags
            await self.db.execute(
                delete(DrinkTag).where(DrinkTag.drink_id == drink_id)
            )
            
            # Add new tags
            if tags:
                await self._add_drink_tags(drink_id, tags)
            
        except Exception as e:
            self.logger.error(f"Error updating drink tags: {str(e)}")
            await self.db.rollback()
            raise
    
    def _validate_drink_data(self, data: DrinkCreate) -> bool:
        """Validate drink creation data"""
        try:
            # Validate required fields
            if not data.name or not data.description or not data.category:
                return False
            
            # Validate numeric ranges
            if not (1 <= data.sweetness_level <= 10):
                return False
            
            if data.caffeine_content < 0 or data.sugar_content < 0 or data.calorie_content < 0:
                return False
            
            if not (0.0 <= data.alcohol_content <= 100.0):
                return False
            
            # Validate price tier
            if data.price_tier not in ["$", "$$", "$$$"]:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_drink_update(self, data: Dict) -> bool:
        """Validate drink update data"""
        try:
            # Validate fields if present
            if 'sweetness_level' in data and not (1 <= data['sweetness_level'] <= 10):
                return False
            
            if 'caffeine_content' in data and data['caffeine_content'] < 0:
                return False
            
            if 'sugar_content' in data and data['sugar_content'] < 0:
                return False
            
            if 'calorie_content' in data and data['calorie_content'] < 0:
                return False
            
            if 'alcohol_content' in data and not (0.0 <= data['alcohol_content'] <= 100.0):
                return False
            
            if 'price_tier' in data and data['price_tier'] not in ["$", "$$", "$$$"]:
                return False
            
            return True
            
        except Exception:
            return False
"""
Catalog service for DrinkWise backend.
Handles drink catalog operations, filtering, and search functionality.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, text, Integer
from sqlalchemy.orm import selectinload
from math import ceil
import logging

from models import Drink, DrinkIngredient, UserDrinkInteraction
from .base import BaseService
from pydantic_models import Drink as DrinkModel, DrinkSearchResponse, DrinkSearchParams

logger = logging.getLogger(__name__)

class CatalogService(BaseService):
    """
    Service for handling drink catalog operations in DrinkWise.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize catalog service with database session."""
        super().__init__(db)
    
    async def search_drinks(self, search_params: DrinkSearchParams) -> DrinkSearchResponse:
        """
        Search and filter drinks based on parameters.
        
        Args:
            search_params: Search parameters and filters
            
        Returns:
            Search results with pagination
        """
        try:
            # Build base query
            query = select(Drink).options(
                selectinload(Drink.ingredients),            )
            
            # Apply filters
            filters = []
            
            # Category filter
            if search_params.category:
                filters.append(Drink.category.ilike(f"%{search_params.category}%"))
            
            # Price tier filter
            if search_params.price_tier:
                filters.append(Drink.price_tier == search_params.price_tier.value)
            
            # Sweetness filter
            if search_params.max_sweetness:
                filters.append(Drink.sweetness_level <= search_params.max_sweetness)
            
            # Caffeine filters
            if search_params.min_caffeine:
                filters.append(Drink.caffeine_content >= search_params.min_caffeine)
            if search_params.max_caffeine:
                filters.append(Drink.caffeine_content <= search_params.max_caffeine)
            
            # Alcohol filter
            if search_params.is_alcoholic is not None:
                filters.append(Drink.is_alcoholic == search_params.is_alcoholic)
            
            # Search text filter
            if search_params.search_text:
                search_text = f"%{search_params.search_text}%"
                filters.append(
                    or_(
                        Drink.name.ilike(search_text),
                        Drink.description.ilike(search_text),
                        Drink.category.ilike(search_text)
                    )
                )
            
            # Excluded ingredients filter
            if search_params.excluded_ingredients:
                excluded = [ing.strip() for ing in search_params.excluded_ingredients.split(',')]
                # This would need a more complex join query in a real implementation
                # For now, we'll skip this filter
                pass
            
            # Apply filters to query
            if filters:
                query = query.where(and_(*filters))
            
            # Get total count for pagination
            count_query = select(func.count(Drink.drink_id))
            if filters:
                count_query = count_query.where(and_(*filters))
            
            total_result = await self.db.execute(count_query)
            total_count = total_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(Drink.name).offset(
                (search_params.page - 1) * search_params.limit
            ).limit(search_params.limit)
            
            # Execute query
            result = await self.db.execute(query)
            drinks = result.scalars().all()
            
            # Convert to model format
            drink_models = []
            for drink in drinks:
                drink_model = await self._convert_drink_to_model(drink)
                drink_models.append(drink_model)
            
            # Calculate pagination info
            total_pages = ceil(total_count / search_params.limit) if search_params.limit > 0 else 1
            
            return DrinkSearchResponse(
                drinks=drink_models,
                total=total_count,
                page=search_params.page,
                limit=search_params.limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            self.log_error("search_drinks", e, {"search_params": search_params.dict()})
            return DrinkSearchResponse(
                drinks=[],
                total=0,
                page=search_params.page,
                limit=search_params.limit,
                total_pages=0
            )
    
    async def get_drink_by_id(self, drink_id: int) -> Optional[DrinkModel]:
        """
        Get detailed drink information by ID.
        
        Args:
            drink_id: ID of the drink
            
        Returns:
            Drink model or None
        """
        try:
            result = await self.db.execute(
                select(Drink).options(
                    selectinload(Drink.ingredients),
                ).where(Drink.drink_id == drink_id)
            )
            
            drink = result.scalar_one_or_none()
            if not drink:
                return None
            
            return await self._convert_drink_to_model(drink)
            
        except Exception as e:
            self.log_error("get_drink_by_id", e, {"drink_id": drink_id})
            return None
    
    async def get_categories(self) -> List[str]:
        """
        Get all available drink categories.
        
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
            self.log_error("get_categories", e)
            return []
    
    async def get_popular_drinks(self, limit: int = 20) -> List[DrinkModel]:
        """
        Get popular drinks based on user interactions.
        
        Args:
            limit: Maximum number of drinks to return
            
        Returns:
            List of popular drinks
        """
        try:
            # Get drinks with highest interaction scores (favorites + ratings + consumption)
            query = select(Drink).options(
                selectinload(Drink.ingredients),
            ).join(
                UserDrinkInteraction, 
                isouter=True
            ).group_by(
                Drink.drink_id
            ).order_by(
                func.sum(
                    func.coalesce(UserDrinkInteraction.is_favorite, False) * 2 +
                    func.coalesce(UserDrinkInteraction.rating, 0) +
                    func.coalesce(UserDrinkInteraction.times_consumed, 0) * 0.1
                ).desc(),
                Drink.name
            ).limit(limit)
            
            result = await self.db.execute(query)
            drinks = result.scalars().all()
            
            # Convert to model format
            drink_models = []
            for drink in drinks:
                drink_model = await self._convert_drink_to_model(drink)
                drink_models.append(drink_model)
            
            return drink_models
            
        except Exception as e:
            self.log_error("get_popular_drinks", e, {"limit": limit})
            return []
    
    async def get_alcoholic_drinks(self, limit: int = 20) -> List[DrinkModel]:
        """
        Get alcoholic drinks (requires age verification).
        
        Args:
            limit: Maximum number of drinks to return
            
        Returns:
            List of alcoholic drinks
        """
        try:
            query = select(Drink).options(
                selectinload(Drink.ingredients),
            ).where(
                Drink.is_alcoholic == True
            ).order_by(
                Drink.name
            ).limit(limit)
            
            result = await self.db.execute(query)
            drinks = result.scalars().all()
            
            # Convert to model format
            drink_models = []
            for drink in drinks:
                drink_model = await self._convert_drink_to_model(drink)
                drink_models.append(drink_model)
            
            return drink_models
            
        except Exception as e:
            self.log_error("get_alcoholic_drinks", e, {"limit": limit})
            return []
    
    async def get_drink_statistics(self) -> Dict[str, Any]:
        """
        Get overall catalog statistics.
        
        Returns:
            Dictionary with catalog statistics
        """
        try:
            # Total drinks count
            total_drinks_result = await self.db.execute(
                select(func.count(Drink.drink_id))
            )
            total_drinks = total_drinks_result.scalar()
            
            # Category breakdown
            category_stats_result = await self.db.execute(
                select(Drink.category, func.count(Drink.drink_id))
                .group_by(Drink.category)
                .order_by(func.count(Drink.drink_id).desc())
            )
            category_stats = dict(category_stats_result.all())
            
            # Price tier breakdown
            price_tier_stats_result = await self.db.execute(
                select(Drink.price_tier, func.count(Drink.drink_id))
                .group_by(Drink.price_tier)
            )
            price_tier_stats = dict(price_tier_stats_result.all())
            
            # Alcoholic vs non-alcoholic
            alcohol_stats_result = await self.db.execute(
                select(
                    func.sum(func.cast(Drink.is_alcoholic, Integer)).label('alcoholic'),
                )
            )
            alcohol_stats = alcohol_stats_result.first()
            
            # Average nutrition values
            nutrition_stats_result = await self.db.execute(
                select(
                    func.avg(Drink.sweetness_level),
                    func.avg(Drink.caffeine_content),
                    func.avg(Drink.sugar_content),
                    func.avg(Drink.calorie_content)
                )
            )
            nutrition_stats = nutrition_stats_result.first()
            
            return {
                "total_drinks": total_drinks,
                "categories": category_stats,
                "price_tiers": price_tier_stats,
                "alcoholic_count": alcohol_stats.alcoholic or 0,
                "average_sweetness": round(nutrition_stats[0] or 0, 2),
                "average_caffeine": round(nutrition_stats[1] or 0, 2),
                "average_sugar": round(nutrition_stats[2] or 2, 2),
                "average_calories": round(nutrition_stats[3] or 0, 2),
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log_error("get_drink_statistics", e)
            return {"error": "Failed to get catalog statistics"}
    
    async def create_drink(self, drink_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new drink in the catalog.
        
        Args:
            drink_data: Dictionary with drink information
            
        Returns:
            Created drink ID or None
        """
        try:
            # Extract ingredients and tags
            ingredients_data = drink_data.pop("ingredients", [])
            
            # Create drink
            new_drink = Drink(**drink_data)
            self.db.add(new_drink)
            await self.db.flush()  # Get drink_id without committing
            
            # Create ingredients
            for ing_data in ingredients_data:
                ingredient = DrinkIngredient(
                    drink_id=new_drink.drink_id,
                    **ing_data
                )
                self.db.add(ingredient)
            
            # Create tags (would need a DrinkTag model)
            # For now, we'll skip tag creation
            
            await self.db.commit()
            await self.db.refresh(new_drink)
            
            self.log_operation("create_drink", {
                "drink_id": new_drink.drink_id,
                "name": new_drink.name
            })
            
            return new_drink.drink_id
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("create_drink", e, {"drink_data": drink_data})
            return None
    
    async def update_drink(self, drink_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update an existing drink.
        
        Args:
            drink_id: ID of drink to update
            update_data: Dictionary with update information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract ingredients and tags
            ingredients_data = update_data.pop("ingredients", None)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.now()
            
            # Update drink
            result = await self.db.execute(
                update(Drink)
                .where(Drink.drink_id == drink_id)
                .values(**update_data)
            )
            
            # Update ingredients if provided
            if ingredients_data is not None:
                # Delete existing ingredients
                await self.db.execute(
                    delete(DrinkIngredient).where(DrinkIngredient.drink_id == drink_id)
                )
                
                # Create new ingredients
                for ing_data in ingredients_data:
                    ingredient = DrinkIngredient(
                        drink_id=drink_id,
                        **ing_data
                    )
                    self.db.add(ingredient)
            
            await self.db.commit()
            
            success = result.rowcount > 0
            
            if success:
                self.log_operation("update_drink", {"drink_id": drink_id})
            
            return success
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("update_drink", e, {"drink_id": drink_id, "update_data": update_data})
            return False
    
    async def delete_drink(self, drink_id: int) -> bool:
        """
        Delete a drink from the catalog.
        
        Args:
            drink_id: ID of drink to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.execute(
                delete(Drink).where(Drink.drink_id == drink_id)
            )
            
            await self.db.commit()
            
            success = result.rowcount > 0
            
            if success:
                self.log_operation("delete_drink", {"drink_id": drink_id})
            
            return success
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("delete_drink", e, {"drink_id": drink_id})
            return False
    
    async def _convert_drink_to_model(self, drink: Drink) -> DrinkModel:
        """
        Convert SQLAlchemy drink model to Pydantic model.
        
        Args:
            drink: SQLAlchemy drink instance
            
        Returns:
            Pydantic drink model
        """
        from pydantic_models import DrinkIngredient as DrinkIngredientModel
        
        return DrinkModel(
            drink_id=drink.drink_id,
            name=drink.name,
            description=drink.description,
            category=drink.category,
            price_tier=drink.price_tier,
            sweetness_level=drink.sweetness_level,
            caffeine_content=drink.caffeine_content,
            sugar_content=drink.sugar_content,
            calorie_content=drink.calorie_content,
            image_url=drink.image_url,
            is_alcoholic=drink.is_alcoholic,
            alcohol_content=drink.alcohol_content,
            temperature=drink.temperature,
            serving_size=drink.serving_size,
            serving_unit=drink.serving_unit,
            created_at=drink.created_at,
            updated_at=drink.updated_at,
            ingredients=[
                DrinkIngredientModel(
                    ingredient_name=ing.ingredient_name,
                    quantity=ing.quantity,
                    is_allergen=ing.is_allergen
                ) for ing in drink.ingredients
            ],
        )
    
    async def get_drinks_by_ingredients(self, ingredients: List[str], exclude_allergens: bool = True) -> List[DrinkModel]:
        """
        Get drinks that contain specific ingredients.
        
        Args:
            ingredients: List of ingredient names to search for
            exclude_allergens: Whether to exclude drinks with allergen ingredients
            
        Returns:
            List of drinks containing the specified ingredients
        """
        try:
            query = select(Drink).options(
                selectinload(Drink.ingredients),
            ).join(DrinkIngredient).where(
                DrinkIngredient.ingredient_name.in_(ingredients)
            )
            
            if exclude_allergens:
                query = query.where(DrinkIngredient.is_allergen == False)
            
            query = query.group_by(Drink.drink_id).having(
                func.count(func.distinct(DrinkIngredient.ingredient_name)) >= len(ingredients)
            )
            
            result = await self.db.execute(query)
            drinks = result.scalars().all()
            
            drink_models = []
            for drink in drinks:
                drink_model = await self._convert_drink_to_model(drink)
                drink_models.append(drink_model)
            
            return drink_models
            
        except Exception as e:
            self.log_error("get_drinks_by_ingredients", e, {"ingredients": ingredients})
            return []
    
    async def search_similar_drinks(self, drink_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for drinks similar to a given drink.
        
        Args:
            drink_id: ID of the reference drink
            limit: Maximum number of similar drinks to return
            
        Returns:
            List of similar drinks with similarity scores
        """
        try:
            # Get reference drink
            reference_drink = await self.get_drink_by_id(drink_id)
            if not reference_drink:
                return []
            
            # Find drinks with similar attributes (content-based similarity)
            query = select(Drink).options(
                selectinload(Drink.ingredients),
            ).where(
                and_(
                    Drink.drink_id != drink_id,
                    func.abs(Drink.sweetness_level - reference_drink.sweetness_level) <= 2,
                    func.abs(Drink.caffeine_content - reference_drink.caffeine_content) <= 50,
                )
            ).order_by(
                func.abs(Drink.sweetness_level - reference_drink.sweetness_level) +
                func.abs(Drink.caffeine_content - reference_drink.caffeine_content) * 0.01
            ).limit(limit)
            
            result = await self.db.execute(query)
            drinks = result.scalars().all()
            
            similar_drinks = []
            for drink in drinks:
                drink_model = await self._convert_drink_to_model(drink)
                
                # Calculate similarity score (simple implementation)
                similarity_score = self._calculate_similarity_score(reference_drink, drink_model)
                
                similar_drinks.append({
                    "drink": drink_model,
                    "similarity_score": similarity_score,
                    "match_reasons": self._get_match_reasons(reference_drink, drink_model)
                })
            
            # Sort by similarity score
            similar_drinks.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return similar_drinks
            
        except Exception as e:
            self.log_error("search_similar_drinks", e, {"drink_id": drink_id, "limit": limit})
            return []
    

    async def user_favorite_to_similar_drinks(self, reference_drinks: List[Dict],drink_ids: List[int], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for drinks similar to a given drink.
        
        Args:
            drink_ids: array ID of the reference drink
            limit: Maximum number of similar drinks to return
            
        Returns:
            List of similar drinks with similarity scores
        """
        try:
            
            avg_sweetness = sum(d.sweetness_level for d in reference_drinks) / len(reference_drinks)
            avg_caffeine = sum(d.caffeine_content for d in reference_drinks) / len(reference_drinks)

            # Similar drink search
            query = (
                select(Drink)
                .options(selectinload(Drink.ingredients))
                .where(
                    and_(
                        ~Drink.drink_id.in_(drink_ids),  # exclude favorites
                        func.abs(Drink.sweetness_level - avg_sweetness) <= 2,
                        func.abs(Drink.caffeine_content - avg_caffeine) <= 50,
                    )
                )
                .order_by(
                    func.abs(Drink.sweetness_level - avg_sweetness)
                    + func.abs(Drink.caffeine_content - avg_caffeine) * 0.01
                )
                .limit(limit)
            )

            result = await self.db.execute(query)
            drinks = result.scalars().all()
            
            similar_drinks = []
            for drink in drinks:
                drink_model = await self._convert_drink_to_model(drink)
                
                # Calculate similarity score (simple implementation)
                
                similar_drinks.append({
                    "drink": drink_model,
                })
            
            # Sort by similarity score
            
            return similar_drinks
            
        except Exception as e:
            self.log_error("user_favorite_to_similar_drinks", e, {"drink_ids": drink_ids, "limit": limit})
            return []
    
    def _calculate_similarity_score(self, drink1: DrinkModel, drink2: DrinkModel) -> float:
        """
        Calculate similarity score between two drinks.
        
        Args:
            drink1: First drink
            drink2: Second drink
            
        Returns:
            Similarity score between 0 and 1
        """
        score = 0.0
        max_score = 0.0
        
        # Category match (weight: 0.3)
        max_score += 0.3
        if drink1.category == drink2.category:
            score += 0.3
        
        # Sweetness similarity (weight: 0.2)
        max_score += 0.2
        sweetness_diff = abs(drink1.sweetness_level - drink2.sweetness_level)
        sweetness_score = max(0, 1 - (sweetness_diff / 10))  # Normalize to 0-1
        score += 0.2 * sweetness_score
        
        # Caffeine similarity (weight: 0.2)
        max_score += 0.2
        caffeine_diff = abs(drink1.caffeine_content - drink2.caffeine_content)
        caffeine_score = max(0, 1 - min(caffeine_diff / 200, 1))  # Normalize to 0-1
        score += 0.2 * caffeine_score
        
        # Alcohol content match (weight: 0.15)
        max_score += 0.15
        if drink1.is_alcoholic == drink2.is_alcoholic:
            score += 0.15
        
        # Price tier similarity (weight: 0.15)
        max_score += 0.15
        if drink1.price_tier == drink2.price_tier:
            score += 0.15
        elif abs(["$", "$$", "$$$"].index(drink1.price_tier) - ["$", "$$", "$$$"].index(drink2.price_tier)) == 1:
            score += 0.075
        
        return score / max_score if max_score > 0 else 0.0
    
    def _get_match_reasons(self, drink1: DrinkModel, drink2: DrinkModel) -> List[str]:
        """
        Get reasons why two drinks are considered similar.
        
        Args:
            drink1: First drink
            drink2: Second drink
            
        Returns:
            List of match reasons
        """
        reasons = []
        
        if drink1.category == drink2.category:
            reasons.append(f"Same category: {drink1.category}")
        
        sweetness_diff = abs(drink1.sweetness_level - drink2.sweetness_level)
        if sweetness_diff <= 1:
            reasons.append("Very similar sweetness level")
        elif sweetness_diff <= 3:
            reasons.append("Similar sweetness level")
        
        caffeine_diff = abs(drink1.caffeine_content - drink2.caffeine_content)
        if caffeine_diff <= 25:
            reasons.append("Very similar caffeine content")
        elif caffeine_diff <= 75:
            reasons.append("Similar caffeine content")
        
        if drink1.is_alcoholic == drink2.is_alcoholic:
            alcohol_type = "alcoholic" if drink1.is_alcoholic else "non-alcoholic"
            reasons.append(f"Both {alcohol_type}")
        
        if drink1.price_tier == drink2.price_tier:
            reasons.append(f"Same price tier: {drink1.price_tier}")
        
        return reasons
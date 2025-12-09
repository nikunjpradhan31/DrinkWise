"""
User-drinks interaction service for DrinkWise backend.
Handles user favorites, ratings, consumption tracking, and interactions.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
import logging

from models import UserDrinkInteraction, Drink, Users
from .base import BaseService
from pydantic_models import (
    UserDrinkInteraction as UserDrinkInteractionModel,
    UserDrinkInteractionUpdate, FavoriteDrink
)

logger = logging.getLogger(__name__)

class UserDrinksService(BaseService):
    """
    Service for handling user-drink interactions in DrinkWise.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize user-drinks service with database session."""
        super().__init__(db)
    
    async def get_user_drink_interaction(self, user_id: int, drink_id: int) -> Optional[UserDrinkInteractionModel]:
        """
        Get user's interaction with a specific drink.

        Args:
            user_id: ID of user
            drink_id: ID of drink

        Returns:
            User drink interaction model or None
        """
        try:
            result = await self.db.execute(
                select(UserDrinkInteraction).where(
                    UserDrinkInteraction.user_id == user_id,
                    UserDrinkInteraction.drink_id == drink_id
                )
            )

            interaction = result.scalar_one_or_none()

            if not interaction:
                return None

            return UserDrinkInteractionModel(
                user_id=interaction.user_id,
                drink_id=interaction.drink_id,
                times_consumed=interaction.times_consumed,
                is_favorite=interaction.is_favorite,
                rating=interaction.rating,
                is_not_for_me=interaction.is_not_for_me,
                viewed_at=interaction.viewed_at,
                last_consumed=interaction.last_consumed_at
            )

        except Exception as e:
            self.log_error("get_user_drink_interaction", e, {"user_id": user_id, "drink_id": drink_id})
            return None

    async def ensure_user_drink_interaction(self, user_id: int, drink_id: int) -> Optional[UserDrinkInteractionModel]:
        """
        Ensure user has an interaction with a specific drink (create default if none exist).

        Args:
            user_id: ID of user
            drink_id: ID of drink

        Returns:
            User drink interaction model
        """
        try:
            # Check if drink exists
            drink_result = await self.db.execute(
                select(Drink).where(Drink.drink_id == drink_id)
            )
            drink = drink_result.scalar_one_or_none()

            if not drink:
                return None

            # Get existing interaction
            interaction = await self.get_user_drink_interaction(user_id, drink_id)
            if interaction:
                return interaction

            # Create default interaction
            new_interaction = UserDrinkInteraction(
                user_id=user_id,
                drink_id=drink_id,
                times_consumed=0,
                is_favorite=False,
                rating=0.0,
                is_not_for_me=False,
                viewed_at=datetime.now(),
                last_consumed_at=None
            )

            self.db.add(new_interaction)
            await self.db.commit()
            await self.db.refresh(new_interaction)

            return UserDrinkInteractionModel(
                user_id=new_interaction.user_id,
                drink_id=new_interaction.drink_id,
                times_consumed=new_interaction.times_consumed,
                is_favorite=new_interaction.is_favorite,
                rating=new_interaction.rating,
                is_not_for_me=new_interaction.is_not_for_me,
                viewed_at=new_interaction.viewed_at,
                last_consumed=new_interaction.last_consumed_at
            )

        except Exception as e:
            await self.db.rollback()
            self.log_error("ensure_user_drink_interaction", e, {"user_id": user_id, "drink_id": drink_id})
            return None
    
    async def update_user_drink_interaction(self, user_id: int, drink_id: int, update_data: UserDrinkInteractionUpdate) -> Optional[UserDrinkInteractionModel]:
        """
        Update user's interaction with a drink.
        
        Args:
            user_id: ID of user
            drink_id: ID of drink
            update_data: Update data for the interaction
            
        Returns:
            Updated interaction model or None
        """
        try:
            # Check if drink exists
            drink_result = await self.db.execute(
                select(Drink).where(Drink.drink_id == drink_id)
            )
            drink = drink_result.scalar_one_or_none()
            
            if not drink:
                return None
            
            # Get existing interaction or create new one
            existing_interaction = await self.get_user_drink_interaction(user_id, drink_id)
            
            if existing_interaction:
                # Update existing interaction
                update_values = {}
                
                if update_data.times_consumed is not None:
                    update_values["times_consumed"] = update_data.times_consumed
                if update_data.is_favorite is not None:
                    update_values["is_favorite"] = update_data.is_favorite
                if update_data.rating is not None:
                    update_values["rating"] = update_data.rating
                if update_data.is_not_for_me is not None:
                    update_values["is_not_for_me"] = update_data.is_not_for_me
                
                if not update_values:
                    return existing_interaction
                
                # Add updated timestamp
                update_values["viewed_at"] = datetime.now()
                if "times_consumed" in update_values:
                    update_values["last_consumed_at"] = datetime.now()
                
                await self.db.execute(
                    update(UserDrinkInteraction)
                    .where(
                        UserDrinkInteraction.user_id == user_id,
                        UserDrinkInteraction.drink_id == drink_id
                    )
                    .values(**update_values)
                )
                
            else:
                # Create new interaction
                new_interaction = UserDrinkInteraction(
                    user_id=user_id,
                    drink_id=drink_id,
                    times_consumed=update_data.times_consumed or 0,
                    is_favorite=update_data.is_favorite or False,
                    rating=update_data.rating or 0.0,
                    is_not_for_me=update_data.is_not_for_me or False,
                    viewed_at=datetime.now(),
                    last_consumed_at=datetime.now() if update_data.times_consumed else None
                )
                
                self.db.add(new_interaction)
            
            await self.db.commit()
            
            # Return updated interaction
            return await self.get_user_drink_interaction(user_id, drink_id)
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("update_user_drink_interaction", e, {"user_id": user_id, "drink_id": drink_id})
            return None
    
    async def get_user_favorites(self, user_id: int) -> Dict[str, Any]:
        """
        Get all drinks marked as favorites by a user.
        
        Args:
            user_id: ID of user
            
        Returns:
            Dictionary with favorites list and count
        """
        try:
            result = await self.db.execute(
                select(UserDrinkInteraction)
                    .options(
                        selectinload(UserDrinkInteraction.drink)
                            .selectinload(Drink.ingredients)
                    )
                .join(Drink)
                .where(
                    UserDrinkInteraction.user_id == user_id,
                    UserDrinkInteraction.is_favorite == True,
                    UserDrinkInteraction.drink_id == Drink.drink_id
                    
                )
                .order_by(Drink.name)
            )
            
            interactions = result.scalars().all()
            
            favorites = []
            for interaction in interactions:
                drink = interaction.drink
                # Convert drink to favorite format
                favorite_drink = FavoriteDrink(
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
                        {
                            "ingredient_name": ing.ingredient_name,
                            "quantity": ing.quantity,
                            "is_allergen": ing.is_allergen
                        } for ing in drink.ingredients
                    ],
                )
                
                favorites.append(favorite_drink)
            
            return {
                "favorites": favorites,
                "total_count": len(favorites)
            }
            
        except Exception as e:
            self.log_error("get_user_favorites", e, {"user_id": user_id})
            return {"favorites": [], "total_count": 0}
    
    async def get_user_favorites_ids(self, user_id: int) -> List[int]:
        """
        Get all drinks marked as favorites by a user.
        
        Args:
            user_id: ID of user
            
        Returns:
            Dictionary with favorites list and count
        """
        try:
            result = await self.db.execute(
                select(UserDrinkInteraction.drink_id)
                .where(
                    UserDrinkInteraction.user_id == user_id,
                    UserDrinkInteraction.is_favorite == True,                    
                )
            )
            
            interactions = result.scalars().all()
            

            return interactions
            
        except Exception as e:
            self.log_error("get_user_favorites_id", e, {"user_id": user_id})
            return []
    
    async def set_favorite_status(self, user_id: int, drink_id: int, is_favorite: bool) -> bool:
        """
        Set favorite status for a drink.
        
        Args:
            user_id: ID of user
            drink_id: ID of drink
            is_favorite: Whether to mark as favorite
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if interaction exists
            interaction = await self.get_user_drink_interaction(user_id, drink_id)
            
            if interaction:
                # Update existing interaction
                await self.db.execute(
                    update(UserDrinkInteraction)
                    .where(
                        UserDrinkInteraction.user_id == user_id,
                        UserDrinkInteraction.drink_id == drink_id
                    )
                    .values(is_favorite=is_favorite, viewed_at=datetime.now())
                )
            else:
                # Create new interaction
                new_interaction = UserDrinkInteraction(
                    user_id=user_id,
                    drink_id=drink_id,
                    times_consumed=0,
                    is_favorite=is_favorite,
                    rating=0.0,
                    is_not_for_me=False,
                    viewed_at=datetime.now(),
                    last_consumed_at=None
                )
                
                self.db.add(new_interaction)
            
            await self.db.commit()
            
            self.log_operation("set_favorite_status", {
                "user_id": user_id,
                "drink_id": drink_id,
                "is_favorite": is_favorite
            })
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("set_favorite_status", e, {"user_id": user_id, "drink_id": drink_id})
            return False
    
    async def set_rating(self, user_id: int, drink_id: int, rating: float) -> bool:
        """
        Set rating for a drink.
        
        Args:
            user_id: ID of user
            drink_id: ID of drink
            rating: Rating from 0.0 to 5.0
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if drink exists
            drink_result = await self.db.execute(
                select(Drink).where(Drink.drink_id == drink_id)
            )
            if not drink_result.scalar_one_or_none():
                return False
            
            # Check if interaction exists
            interaction = await self.get_user_drink_interaction(user_id, drink_id)
            
            if interaction:
                # Update existing interaction
                await self.db.execute(
                    update(UserDrinkInteraction)
                    .where(
                        UserDrinkInteraction.user_id == user_id,
                        UserDrinkInteraction.drink_id == drink_id
                    )
                    .values(rating=rating, viewed_at=datetime.now())
                )
            else:
                # Create new interaction
                new_interaction = UserDrinkInteraction(
                    user_id=user_id,
                    drink_id=drink_id,
                    times_consumed=0,
                    is_favorite=False,
                    rating=rating,
                    is_not_for_me=False,
                    viewed_at=datetime.now(),
                    last_consumed_at=None
                )
                
                self.db.add(new_interaction)
            
            await self.db.commit()
            
            self.log_operation("set_rating", {
                "user_id": user_id,
                "drink_id": drink_id,
                "rating": rating
            })
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("set_rating", e, {"user_id": user_id, "drink_id": drink_id})
            return False
    
    async def increment_consumption(self, user_id: int, drink_id: int, increment: int = 1) -> bool:
        """
        Increment consumption count for a drink.
        
        Args:
            user_id: ID of user
            drink_id: ID of drink
            increment: Amount to increment by
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if interaction exists
            interaction = await self.get_user_drink_interaction(user_id, drink_id)
            
            if interaction:
                # Update existing interaction
                new_count = interaction.times_consumed + increment
                await self.db.execute(
                    update(UserDrinkInteraction)
                    .where(
                        UserDrinkInteraction.user_id == user_id,
                        UserDrinkInteraction.drink_id == drink_id
                    )
                    .values(
                        times_consumed=new_count,
                        viewed_at=datetime.now(),
                        last_consumed_at=datetime.now()
                    )
                )
            else:
                # Create new interaction
                new_interaction = UserDrinkInteraction(
                    user_id=user_id,
                    drink_id=drink_id,
                    times_consumed=increment,
                    is_favorite=False,
                    rating=0.0,
                    is_not_for_me=False,
                    viewed_at=datetime.now(),
                    last_consumed_at=datetime.now()
                )
                
                self.db.add(new_interaction)
            
            await self.db.commit()
            
            self.log_operation("increment_consumption", {
                "user_id": user_id,
                "drink_id": drink_id,
                "increment": increment
            })
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("increment_consumption", e, {"user_id": user_id, "drink_id": drink_id})
            return False
    
    async def remove_user_drink_interaction(self, user_id: int, drink_id: int) -> bool:
        """
        Remove all interaction data for a drink.
        
        Args:
            user_id: ID of user
            drink_id: ID of drink
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.execute(
                delete(UserDrinkInteraction).where(
                    UserDrinkInteraction.user_id == user_id,
                    UserDrinkInteraction.drink_id == drink_id
                )
            )
            
            await self.db.commit()
            
            success = result.rowcount > 0
            
            if success:
                self.log_operation("remove_user_drink_interaction", {
                    "user_id": user_id,
                    "drink_id": drink_id
                })
            
            return success
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("remove_user_drink_interaction", e, {"user_id": user_id, "drink_id": drink_id})
            return False
    
    async def get_user_drink_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about user's drink interactions.
        
        Args:
            user_id: ID of user
            
        Returns:
            Dictionary with interaction statistics
        """
        try:
            result = await self.db.execute(
                select(UserDrinkInteraction).where(UserDrinkInteraction.user_id == user_id)
            )
            
            interactions = result.scalars().all()
            
            if not interactions:
                return {
                    "user_id": user_id,
                    "total_interactions": 0,
                    "favorites_count": 0,
                    "rated_drinks_count": 0,
                    "consumed_drinks_count": 0,
                    "average_rating": 0.0,
                    "total_consumption_count": 0,
                    "categories_explored": []
                }
            
            # Calculate statistics
            total_interactions = len(interactions)
            favorites_count = sum(1 for i in interactions if i.is_favorite)
            rated_interactions = [i for i in interactions if i.rating > 0]
            rated_drinks_count = len(rated_interactions)
            consumed_interactions = [i for i in interactions if i.times_consumed > 0]
            consumed_drinks_count = len(consumed_interactions)
            
            average_rating = (
                sum(i.rating for i in rated_interactions) / rated_drinks_count
                if rated_drinks_count > 0 else 0.0
            )
            
            total_consumption_count = sum(i.times_consumed for i in consumed_interactions)
            
            # Get categories explored (this would need a join in real implementation)
            categories_explored = list(set(
                # In real implementation, you'd join with Drink table
                ["coffee", "tea", "smoothie"]  # Placeholder
            ))
            
            return {
                "user_id": user_id,
                "total_interactions": total_interactions,
                "favorites_count": favorites_count,
                "rated_drinks_count": rated_drinks_count,
                "consumed_drinks_count": consumed_drinks_count,
                "average_rating": round(average_rating, 2),
                "total_consumption_count": total_consumption_count,
                "categories_explored": categories_explored,
                "last_interaction": max(i.viewed_at for i in interactions).isoformat() if interactions else None
            }
            
        except Exception as e:
            self.log_error("get_user_drink_statistics", e, {"user_id": user_id})
            return {"error": "Failed to get user drink statistics"}
    
    async def get_most_consumed_drinks(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get drinks most consumed by a user.
        
        Args:
            user_id: ID of user
            limit: Maximum number of drinks to return
            
        Returns:
            List of consumed drinks with counts
        """
        try:
            result = await self.db.execute(
                select(UserDrinkInteraction)
                .options(selectinload(UserDrinkInteraction).selectinload('drink'))
                .join(Drink)
                .where(
                    UserDrinkInteraction.user_id == user_id,
                    UserDrinkInteraction.times_consumed > 0
                )
                .order_by(UserDrinkInteraction.times_consumed.desc(), Drink.name)
                .limit(limit)
            )
            
            interactions = result.scalars().all()
            
            consumed_drinks = []
            for interaction in interactions:
                drink = interaction.drink
                consumed_drinks.append({
                    "drink_id": drink.drink_id,
                    "name": drink.name,
                    "category": drink.category,
                    "times_consumed": interaction.times_consumed,
                    "last_consumed": interaction.last_consumed_at.isoformat() if interaction.last_consumed_at else None
                })
            
            return consumed_drinks
            
        except Exception as e:
            self.log_error("get_most_consumed_drinks", e, {"user_id": user_id})
            return []
    
    async def get_user_preferred_categories(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user's preferred drink categories based on interactions.
        
        Args:
            user_id: ID of user
            
        Returns:
            List of preferred categories with scores
        """
        try:
            result = await self.db.execute(
                select(UserDrinkInteraction)
                .options(selectinload(UserDrinkInteraction).selectinload('drink'))
                .join(Drink)
                .where(UserDrinkInteraction.user_id == user_id)
            )
            
            interactions = result.scalars().all()
            
            # Calculate category preferences
            category_scores = {}
            
            for interaction in interactions:
                category = interaction.drink.category
                
                # Score based on interactions
                score = 0
                if interaction.is_favorite:
                    score += 3
                if interaction.rating > 0:
                    score += interaction.rating
                if interaction.times_consumed > 0:
                    score += min(interaction.times_consumed * 0.5, 5)  # Cap consumption contribution
                if not interaction.is_not_for_me:
                    score += 1
                
                if category in category_scores:
                    category_scores[category] += score
                else:
                    category_scores[category] = score
            
            # Sort by score
            preferred_categories = [
                {"category": cat, "score": score}
                for cat, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            ]
            
            return preferred_categories
            
        except Exception as e:
            self.log_error("get_user_preferred_categories", e, {"user_id": user_id})
            return []
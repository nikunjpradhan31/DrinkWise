"""
User-drink interaction API endpoints for DrinkWise backend.
Handles user favorites, ratings, and consumption tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db_async
from middleware.auth_middleware import get_current_user
from models import Users, UserDrinkInteraction
from services.user_drinks_service import UserDrinksService
from pydantic_models import (
    UserDrinkInteraction as UserDrinkInteractionModel,
    UserDrinkInteractionUpdate, UserFavoritesResponse,
    FavoriteDrink, ErrorResponse
)

router = APIRouter(prefix="/user-drinks", tags=["user_drinks"])

async def get_user_drinks_service(
    db: AsyncSession = Depends(get_db_async)
) -> UserDrinksService:
    """Get UserDrinksService instance."""
    return UserDrinksService(db)

# GET /user-drinks/{drink_id} - Gets the user interaction info about the drink
@router.get(
    "/{drink_id}",
    response_model=UserDrinkInteractionModel,
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}}
)
async def get_user_drink_interaction(
    drink_id: int,
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Get current user's interaction information about a specific drink.
    
    - **drink_id**: Unique identifier of the drink
    """
    interaction = await user_drinks_service.get_user_drink_interaction(
        current_user.user_id, drink_id
    )
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No interaction found for drink {drink_id}"
        )
    
    return interaction

# PUT /user-drinks/{drink_id} - Updates the user interaction info about the drink
@router.put(
    "/{drink_id}",
    response_model=UserDrinkInteractionModel,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def update_user_drink_interaction(
    drink_id: int,
    update_data: UserDrinkInteractionUpdate,
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Update user's interaction with a specific drink.
    
    - **drink_id**: Unique identifier of the drink
    - **times_consumed**: Number of times consumed (optional)
    - **is_favorite**: Whether this is a favorite drink (optional)
    - **rating**: User rating from 0.0 to 5.0 (optional)
    - **is_not_for_me**: Whether user doesn't like this drink (optional)
    """
    interaction = await user_drinks_service.update_user_drink_interaction(
        current_user.user_id, drink_id, update_data
    )
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with id {drink_id} not found"
        )
    
    return interaction

# GET /user-favorites - Get user's favorite drinks
@router.get(
    "/../user-favorites",
    response_model=UserFavoritesResponse,
    responses={401: {"model": ErrorResponse}}
)
async def get_user_favorites(
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Get all drinks marked as favorites by the current user.
    """
    favorites = await user_drinks_service.get_user_favorites(current_user.user_id)
    
    return UserFavoritesResponse(
        favorites=favorites["favorites"],
        total_count=favorites["total_count"]
    )

# POST /user-drinks/{drink_id}/favorite - Add/remove from favorites
@router.post(
    "/{drink_id}/favorite",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def toggle_favorite(
    drink_id: int,
    is_favorite: bool,
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Add or remove a drink from user's favorites.
    
    - **drink_id**: Unique identifier of the drink
    - **is_favorite**: True to add to favorites, False to remove
    """
    success = await user_drinks_service.set_favorite_status(
        current_user.user_id, drink_id, is_favorite
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with id {drink_id} not found"
        )
    
    return {
        "message": "Added to favorites" if is_favorite else "Removed from favorites",
        "drink_id": drink_id,
        "is_favorite": is_favorite
    }

# POST /user-drinks/{drink_id}/rating - Set rating for a drink
@router.post(
    "/{drink_id}/rating",
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def rate_drink(
    drink_id: int,
    rating: float,
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Set or update rating for a drink.
    
    - **drink_id**: Unique identifier of the drink
    - **rating**: Rating from 0.0 to 5.0
    """
    if rating < 0.0 or rating > 5.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0.0 and 5.0"
        )
    
    success = await user_drinks_service.set_rating(
        current_user.user_id, drink_id, rating
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with id {drink_id} not found"
        )
    
    return {
        "message": "Rating updated successfully",
        "drink_id": drink_id,
        "rating": rating
    }

# POST /user-drinks/{drink_id}/consumed - Mark as consumed
@router.post(
    "/{drink_id}/consumed",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def mark_as_consumed(
    drink_id: int,
    times_consumed: int = 1,
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Mark a drink as consumed.
    
    - **drink_id**: Unique identifier of the drink
    - **times_consumed**: Number of times consumed (default: 1)
    """
    if times_consumed < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="times_consumed must be at least 1"
        )
    
    success = await user_drinks_service.increment_consumption(
        current_user.user_id, drink_id, times_consumed
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with id {drink_id} not found"
        )
    
    return {
        "message": "Consumption recorded",
        "drink_id": drink_id,
        "times_consumed": times_consumed
    }

# DELETE /user-drinks/{drink_id} - Remove all interaction data
@router.delete(
    "/{drink_id}",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def remove_user_drink_interaction(
    drink_id: int,
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Remove all interaction data for a drink.
    
    - **drink_id**: Unique identifier of the drink
    """
    success = await user_drinks_service.remove_user_drink_interaction(
        current_user.user_id, drink_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No interaction found for drink {drink_id}"
        )
    
    return {
        "message": "Interaction data removed",
        "drink_id": drink_id
    }

# GET /user-drinks/statistics - Get user's drink interaction statistics
@router.get(
    "/../statistics",
    responses={401: {"model": ErrorResponse}}
)
async def get_user_drink_statistics(
    current_user: Users = Depends(get_current_user),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service)
):
    """
    Get statistics about user's drink interactions.
    """
    stats = await user_drinks_service.get_user_drink_statistics(current_user.user_id)
    
    return stats

# Export router
__all__ = ["router"]
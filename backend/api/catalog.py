"""
Catalog API endpoints for DrinkWise backend.
Handles drink browsing, filtering, and categorization.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from typing import Optional

from database import get_db_async
from middleware.auth_middleware import get_current_user_optional
from models import Users
from services.catalog_service import CatalogService
from services.user_drinks_service import UserDrinksService
from middleware.auth_middleware import get_current_user
from pydantic_models import (
    DrinkSearchParams, DrinkSearchResponse, CategoriesResponse,
    PopularDrinksResponse, Drink as DrinkModel, ErrorResponse
)

router = APIRouter(prefix="/catalog", tags=["catalog"])


def calculate_age(date_of_birth: date) -> int:
    today = date.today()
    age = today.year - date_of_birth.year
    # subtract 1 if birthday hasn't occurred yet this year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age

async def get_catalog_service(
    db: AsyncSession = Depends(get_db_async)
) -> CatalogService:
    """Get CatalogService instance."""
    return CatalogService(db)

async def get_user_drinks_service(
    db: AsyncSession = Depends(get_db_async)
) -> UserDrinksService:
    """Get UserDrinksService instance."""
    return UserDrinksService(db)

# GET /catalog/drinks - Search and filter drinks
@router.get(
    "/drinks",
    response_model=DrinkSearchResponse,
    responses={400: {"model": ErrorResponse}}
)
async def search_drinks(
    category: Optional[str] = Query(None, description="Filter by category"),
    price_tier: Optional[str] = Query(None, regex="^(\$|\$\$|\$\$\$)$", description="Filter by price tier"),
    max_sweetness: Optional[int] = Query(None, ge=1, le=10, description="Maximum sweetness level"),
    min_caffeine: Optional[int] = Query(None, ge=0, description="Minimum caffeine content"),
    max_caffeine: Optional[int] = Query(None, ge=0, description="Maximum caffeine content"),
    is_alcoholic: Optional[bool] = Query(None, description="Filter by alcoholic content"),
    excluded_ingredients: Optional[str] = Query(None, description="Comma-separated list of excluded ingredients"),
    search_text: Optional[str] = Query(None, description="Search text for name, description, or category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of drinks per page"),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Search and filter drinks with various criteria.
    
    - **category**: Filter by drink category (coffee, tea, smoothie, etc.)
    - **price_tier**: Filter by price tier ($$, $$$, etc.)
    - **max_sweetness**: Maximum sweetness level (1-10)
    - **min_caffeine**: Minimum caffeine content (mg)
    - **max_caffeine**: Maximum caffeine content (mg)
    - **is_alcoholic**: Filter alcoholic vs non-alcoholic drinks
    - **excluded_ingredients**: Comma-separated list of ingredients to exclude
    - **search_text**: Search in name, description, and category
    - **page**: Page number (starting from 1)
    - **limit**: Results per page (max 100)
    """
    search_params = DrinkSearchParams(
        category=category,
        price_tier=price_tier,
        max_sweetness=max_sweetness,
        min_caffeine=min_caffeine,
        max_caffeine=max_caffeine,
        is_alcoholic=is_alcoholic,
        excluded_ingredients=excluded_ingredients,
        search_text=search_text,
        page=page,
        limit=limit
    )
    
    return await catalog_service.search_drinks(search_params)

# GET /catalog/drinks/{drink_id} - Get detailed drink information
@router.get(
    "/drinks/{drink_id}",
    response_model=DrinkModel,
    responses={404: {"model": ErrorResponse}}
)
async def get_drink_by_id(
    drink_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Get detailed information about a specific drink.
    
    - **drink_id**: Unique identifier of the drink
    """
    drink = await catalog_service.get_drink_by_id(drink_id)
    
    if not drink:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with id {drink_id} not found"
        )
    
    return drink

# GET /catalog/categories - Get all available drink categories
@router.get(
    "/categories",
    response_model=CategoriesResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_categories(
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Get all available drink categories.
    """
    categories = await catalog_service.get_categories()
    
    return CategoriesResponse(categories=categories)

# GET /catalog/popular - Get popular drinks
@router.get(
    "/popular",
    response_model=PopularDrinksResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_popular_drinks(
    limit: int = Query(20, ge=1, le=100, description="Number of drinks to return"),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Get popular drinks based on user interactions (favorites, ratings, consumption).
    
    - **limit**: Number of popular drinks to return (max 100)
    """
    drinks = await catalog_service.get_popular_drinks(limit)
    
    return PopularDrinksResponse(drinks=drinks)

# GET /catalog/alcoholic - Get alcoholic drinks (requires age verification)
@router.get(
    "/alcoholic",
    response_model=PopularDrinksResponse,
    responses={
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_alcoholic_drinks(
    limit: int = Query(20, ge=1, le=100, description="Number of drinks to return"),
    current_user: Optional[Users] = Depends(get_current_user_optional),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Get alcoholic drinks (requires age verification).
    
    - **limit**: Number of drinks to return (max 100)
    
    ⚠️ **Age Verification Required**: This endpoint requires age verification for access.
    """
    # Check age verification
    if current_user and current_user.date_of_birth:
        age = calculate_age(current_user.date_of_birth)
        LEGAL_DRINKING_AGE = 21
        if age < LEGAL_DRINKING_AGE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be of legal drinking age to access alcoholic beverages",
                headers={"X-Age-Verification-Required": "true"}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Age verification required to access alcoholic beverages",
            headers={"X-Age-Verification-Required": "true"}
        )
    
    drinks = await catalog_service.get_alcoholic_drinks(limit)
    
    return PopularDrinksResponse(drinks=drinks)

# GET /catalog/statistics - Get catalog statistics
@router.get(
    "/statistics",
    responses={500: {"model": ErrorResponse}}
)
async def get_catalog_statistics(
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Get overall catalog statistics including category breakdown, nutrition averages, etc.
    """
    stats = await catalog_service.get_drink_statistics()
    
    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=stats["error"]
        )
    
    return stats

# GET /catalog/ingredients/{ingredient_name} - Get drinks by ingredient
@router.get(
    "/ingredients/{ingredient_name}",
    response_model=PopularDrinksResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_drinks_by_ingredient(
    ingredient_name: str,
    exclude_allergens: bool = Query(True, description="Exclude drinks with allergen ingredients"),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Get drinks containing a specific ingredient.
    
    - **ingredient_name**: Name of the ingredient to search for
    - **exclude_allergens**: Whether to exclude drinks with allergen ingredients
    """
    drinks = await catalog_service.get_drinks_by_ingredients(
        [ingredient_name], 
        exclude_allergens=exclude_allergens
    )
    
    return PopularDrinksResponse(drinks=drinks)



@router.get(
    "/similar-user",
    responses={401: {"model": dict}}
)
async def get_user_similar_drinks(
    limit: int = Query(10, ge=1, le=50, description="Number of similar drinks to return"),
    current_user: Users = Depends(get_current_user),
    catalog_service: CatalogService = Depends(get_catalog_service),
    user_drinks_service: UserDrinksService = Depends(get_user_drinks_service),

):
    
    user_favorites = await user_drinks_service.get_user_favorites(current_user.user_id)
    user_favorites = user_favorites["favorites"]
    drink_ids = [drink.drink_id for drink in user_favorites ]
    similar_drinks = await catalog_service.user_favorite_to_similar_drinks(user_favorites,drink_ids, limit)
    if not similar_drinks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with ids {drink_ids} not found"
        )
    
    return {
        "drink_ids": drink_ids,
        "similar_drinks": [
            {
                "drink": item["drink"].dict(),
            }
            for item in similar_drinks
        ],
        "count": len(similar_drinks),
        "recommendation_type": "user-content"
    }




# GET /catalog/{drink_id}/similar - Get similar drinks
@router.get(
    "/similar-drink",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_similar_drinks(
    drink_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of similar drinks to return"),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """
    Get drinks similar to a specific drink based on attributes.
    
    - **drink_id**: ID of the reference drink
    - **limit**: Number of similar drinks to return (max 50)
    """
    similar_drinks = await catalog_service.search_similar_drinks(drink_id, limit)
    
    if not similar_drinks and await catalog_service.get_drink_by_id(drink_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drink with id {drink_id} not found"
        )
    
    return {
        "drink_id": drink_id,
        "similar_drinks": [
            {
                "drink": item["drink"].dict(),
                "similarity_score": item["similarity_score"],
                "match_reasons": item["match_reasons"]
            }
            for item in similar_drinks
        ],
        "count": len(similar_drinks),
        "recommendation_type": "content"
    }


# Export router
__all__ = ["router"]
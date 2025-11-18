from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from middleware import get_current_user, get_age_verified_user
from services import (
    AuthService, CatalogService, HybridModelService, ExplainabilityService
)
from pydantic_models import (
    DrinkResponse, DrinkCreate, DrinkSearchParams, PaginatedDrinkResponse,
    RecommendationRequest, RecommendationResponse, UserFeedbackCreate
)

router = APIRouter(prefix="/catalog", tags=["Catalog"])
security = HTTPBearer()

@router.get("/drinks", response_model=PaginatedDrinkResponse)
async def search_drinks(
    category: str = None,
    price_tier: str = None,
    max_sweetness: int = None,
    min_caffeine: int = None,
    max_caffeine: int = None,
    is_alcoholic: bool = None,
    excluded_ingredients: str = None,  # Comma-separated list
    search_text: str = None,
    page: int = 1,
    limit: int = 20,
    catalog_service: CatalogService = Depends()
):
    """Search and filter drinks"""
    try:
        # Parse excluded ingredients
        excluded_ingredients_list = []
        if excluded_ingredients:
            excluded_ingredients_list = [ing.strip() for ing in excluded_ingredients.split(",")]
        
        search_params = DrinkSearchParams(
            category=category,
            price_tier=price_tier,
            max_sweetness=max_sweetness,
            min_caffeine=min_caffeine,
            max_caffeine=max_caffeine,
            is_alcoholic=is_alcoholic,
            excluded_ingredients=excluded_ingredients_list,
            search_text=search_text,
            page=page,
            limit=limit
        )
        
        result = await catalog_service.search_drinks(search_params)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/drinks/{drink_id}", response_model=DrinkResponse)
async def get_drink_details(
    drink_id: int,
    current_user: dict = Depends(get_current_user),
    catalog_service: CatalogService = Depends()
):
    """Get detailed drink information"""
    try:
        drink = await catalog_service.get_drink_by_id(drink_id)
        if not drink:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drink not found"
            )
        
        return DrinkResponse.from_orm(drink)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/categories")
async def get_drink_categories(
    catalog_service: CatalogService = Depends()
):
    """Get all available drink categories"""
    try:
        categories = await catalog_service.get_drink_categories()
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/popular", response_model=list)
async def get_popular_drinks(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    catalog_service: CatalogService = Depends()
):
    """Get popular drinks"""
    try:
        drinks = await catalog_service.get_popular_drinks(limit)
        return drinks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/alcoholic")
async def get_alcoholic_drinks(
    limit: int = 20,
    current_user: dict = Depends(get_age_verified_user),
    catalog_service: CatalogService = Depends()
):
    """Get alcoholic drinks (requires age verification)"""
    try:
        drinks = await catalog_service.get_alcoholic_drinks(age_verified=True, limit=limit)
        return drinks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
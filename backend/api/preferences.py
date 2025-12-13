"""
User preferences API endpoints for DrinkWise backend.
Handles user taste preferences and settings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from database import get_db_async
from middleware.auth_middleware import get_current_user
from models import Users
from services.preference_service import PreferenceService
from pydantic import BaseModel, Field

# Custom models for preferences endpoints
class UserPreferenceResponse(BaseModel):
    """User preference response model matching the API schema."""
    user_id: int
    sweetness_preference: int = Field(..., ge=1, le=10)
    bitterness_preference: int = Field(..., ge=1, le=10)
    caffeine_limit: int = Field(..., ge=0)
    calorie_limit: int = Field(..., ge=0)
    preferred_price_tier: str = Field(..., pattern="^(\$|\$\$|\$\$\$)$")
    created_at: datetime
    updated_at: datetime

class UserPreferenceUpdateRequest(BaseModel):
    """User preference update request model matching the API schema."""
    sweetness_preference: Optional[int] = Field(None, ge=1, le=10)
    bitterness_preference: Optional[int] = Field(None, ge=1, le=10)
    caffeine_limit: Optional[int] = Field(None, ge=0)
    calorie_limit: Optional[int] = Field(None, ge=0)
    preferred_price_tier: Optional[str] = Field(None, pattern="^(\$|\$\$|\$\$\$)$")

router = APIRouter(prefix="/preferences", tags=["preferences"])

async def get_preference_service(
    db: AsyncSession = Depends(get_db_async)
) -> PreferenceService:
    """Get PreferenceService instance."""
    return PreferenceService(db)

@router.get(
    "",
    response_model=UserPreferenceResponse,
    responses={401: {"model": dict}}
)
async def get_user_preferences(
    current_user: Users = Depends(get_current_user),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """
    Get current user's drink preferences.

    Returns user's taste preferences including sweetness, bitterness,
    limits for sugar/caffeine/calories, and preferred price tier.
    Creates default preferences if none exist.
    """
    #preferences = await preference_service.ensure_user_preferences(current_user.user_id)
    preferences = await preference_service.get_user_preferences(current_user.user_id)

    return UserPreferenceResponse(
        user_id=current_user.user_id,
        sweetness_preference=preferences.sweetness_preference,
        bitterness_preference=preferences.bitterness_preference,
        caffeine_limit=preferences.caffeine_limit,
        calorie_limit=preferences.calorie_limit,
        preferred_price_tier=preferences.preferred_price_tier,
        created_at=preferences.created_at,
        updated_at=preferences.updated_at
    )

@router.put(
    "",
    response_model=UserPreferenceResponse,
    responses={400: {"model": dict}, 401: {"model": dict}}
)
async def upsert_user_preferences(
    update_data: UserPreferenceUpdateRequest,
    current_user: Users = Depends(get_current_user),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """
    Create or update current user's drink preferences.

    Creates default preferences if none exist, then updates with provided fields.
    Only provided fields will be updated.
    """
    updated_preferences = await preference_service.update_user_preferences(
        current_user.user_id, update_data
    )

    if not updated_preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update preferences"
        )

    # Convert to response model
    return UserPreferenceResponse(
        user_id=updated_preferences.user_id,
        sweetness_preference=updated_preferences.sweetness_preference,
        bitterness_preference=updated_preferences.bitterness_preference,
        caffeine_limit=updated_preferences.caffeine_limit,
        calorie_limit=updated_preferences.calorie_limit,
        preferred_price_tier=updated_preferences.preferred_price_tier,
        created_at=updated_preferences.created_at,
        updated_at=updated_preferences.updated_at
    )

# Export router
__all__ = ["router"]
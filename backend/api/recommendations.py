from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from middleware import get_current_user, get_age_verified_user
from services import (
    AuthService, CatalogService, HybridModelService, ExplainabilityService
)
from pydantic_models import (
    RecommendationRequest, RecommendationResponse, UserFeedbackCreate
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
security = HTTPBearer()

@router.post("/", response_model=RecommendationResponse)
async def generate_recommendations(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user),
    hybrid_model_service: HybridModelService = Depends(),
    explainability_service: ExplainabilityService = Depends()
):
    """Generate personalized drink recommendations"""
    try:
        # Check if user is age verified for potential alcoholic recommendations
        age_verified = current_user.get("age", 0) >= 21
        
        recommendations = await hybrid_model_service.generate_recommendations(
            user_id=current_user["user_id"],
            request=request,
            age_verified=age_verified
        )
        
        # Generate explanations for recommendations
        if recommendations.recommendations:
            explained_recs = []
            for rec in recommendations.recommendations:
                explanations = await explainability_service.generate_explanation(
                    user_id=current_user["user_id"],
                    drink=rec.drink,
                    recommendation_score=rec.score,
                    recommendation_type=recommendations.recommendation_type
                )
                rec.explanation = explanations
                explained_recs.append(rec)
            
            recommendations.recommendations = explained_recs
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/feedback")
async def submit_feedback(
    feedback: UserFeedbackCreate,
    current_user: dict = Depends(get_current_user),
    hybrid_model_service: HybridModelService = Depends()
):
    """Submit feedback on recommendations to improve future suggestions"""
    try:
        # This would integrate with the UserFeedback model
        # For now, just return success
        
        return {
            "message": "Feedback received successfully",
            "feedback_type": feedback.feedback_type,
            "drink_id": feedback.drink_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/similar/{drink_id}")
async def get_similar_drinks(
    drink_id: int,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    hybrid_model_service: HybridModelService = Depends(),
    catalog_service: CatalogService = Depends()
):
    """Get drinks similar to a given drink"""
    try:
        similar_drinks = await hybrid_model_service.get_similar_drinks(drink_id, limit)
        
        # Convert to response format
        from pydantic_models import DrinkResponse
        similar_responses = [DrinkResponse.from_orm(drink) for drink in similar_drinks]
        
        return {
            "drink_id": drink_id,
            "similar_drinks": similar_responses,
            "count": len(similar_responses)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
"""
Pydantic models for DrinkWise API requests and responses.
Based on the INPUTSOUTPUTS.md specification.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from email_validator import EmailNotValidError, validate_email

# =========================
# AUTHENTICATION MODELS
# =========================

class UserRegistration(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirmpassword: str = Field(..., min_length=8, max_length=128)
    date_of_birth: Optional[datetime] = None
    
    @validator('confirmpassword')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    """User login request model."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

class UserResponse(BaseModel):
    """User response model."""
    user_id: int
    username: str
    email: EmailStr
    joindate: datetime
    is_verified: bool
    date_of_birth: Optional[datetime]
    preference_finished: bool
    verification_completed: bool = False
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

class UserUpdate(BaseModel):
    """User profile update request model."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    date_of_birth: Optional[datetime] = None

class ForgotPassword(BaseModel):
    """Forgot password request model."""
    email: EmailStr
    verification_code: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class ForgotPasswordResponse(BaseModel):
    """Forgot password response model."""
    message: str = "Password reset successfully"
    user_id: int

class LogoutResponse(BaseModel):
    """Logout response model."""
    message: str = "Logged out successfully"

# =========================
# USER PREFERENCES MODELS
# =========================

class UserPreference(BaseModel):
    """User preference response model."""
    user_id: int
    sweetness_preference: int = Field(..., ge=1, le=10)
    bitterness_preference: int = Field(..., ge=1, le=10)
    sugar_limit: Optional[float] = Field(None, ge=0.0)
    caffeine_limit: int = Field(..., ge=0)
    calorie_limit: int = Field(..., ge=0)
    preferred_price_tier: str = Field(..., pattern="^(\$|\$\$|\$\$\$)$")
    created_at: datetime
    updated_at: datetime

class UserPreferenceUpdate(BaseModel):
    """User preference update request model."""
    sweetness_preference: Optional[int] = Field(None, ge=1, le=10)
    bitterness_preference: Optional[int] = Field(None, ge=1, le=10)
    sugar_limit: Optional[float] = Field(None, ge=0.0)
    caffeine_limit: Optional[int] = Field(None, ge=0)
    calorie_limit: Optional[int] = Field(None, ge=0)
    preferred_price_tier: Optional[str] = Field(None, pattern="^(\$|\$\$|\$\$\$)$")

# =========================
# DRINK CATALOG MODELS
# =========================

class DrinkIngredient(BaseModel):
    """Drink ingredient model."""
    ingredient_name: str
    quantity: Optional[str] = None
    is_allergen: bool = False

# class DrinkTag(BaseModel):
#     """Drink tag model."""
#     tag: str

class Drink(BaseModel):
    """Drink model."""
    drink_id: int
    name: str = Field(..., max_length=200)
    description: str
    category: str = Field(..., max_length=100)
    price_tier: str = Field(..., pattern="^(\$|\$\$|\$\$\$)$")
    sweetness_level: int = Field(..., ge=1, le=10)
    caffeine_content: int = Field(..., ge=0)
    sugar_content: float = Field(..., ge=0.0)
    calorie_content: int = Field(..., ge=0)
    image_url: Optional[str] = None
    is_alcoholic: bool
    alcohol_content: float = Field(..., ge=0.0, le=100.0)
    temperature: str = Field(..., max_length=10)
    serving_size: float = Field(..., ge=0.0)
    serving_unit: str = Field(..., max_length=10)
    safety_flags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    ingredients: List[DrinkIngredient]
    tags: List[str]

class DrinkSearchResponse(BaseModel):
    """Drink search response model."""
    drinks: List[Drink]
    total: int
    page: int
    limit: int
    total_pages: int

class CategoriesResponse(BaseModel):
    """Categories response model."""
    categories: List[str]

class PopularDrinksResponse(BaseModel):
    """Popular drinks response model."""
    drinks: List[Drink]

# =========================
# TASTE QUIZ MODELS
# =========================

# class QuizOption(BaseModel):
#     """Quiz option model."""
#     option_id: int
#     option_text: str

# class QuizQuestion(BaseModel):
#     """Quiz question model."""
#     question_id: int
#     question_text: str
#     is_active: bool
#     created_at: datetime
#     options: List[QuizOption]

# class QuizQuestionsResponse(BaseModel):
#     """Quiz questions response model."""
#     questions: List[QuizQuestion]
#     total_questions: int

# class QuizAnswer(BaseModel):
#     """Quiz answer model."""
#     question_id: int
#     option_id: int

# class QuizSubmission(BaseModel):
#     """Quiz submission model."""
#     answers: List[QuizAnswer]

# class QuizSubmissionResponse(BaseModel):
#     """Quiz submission response model."""
#     message: str
#     answers_submitted: int
#     quiz_completed: bool

# =========================
# USER-DRINK INTERACTIONS
# =========================

class UserDrinkInteraction(BaseModel):
    """User-drink interaction model."""
    user_id: int
    drink_id: int
    times_consumed: int = Field(..., ge=0)
    is_favorite: bool
    rating: float = Field(..., ge=0.0, le=5.0)
    is_not_for_me: bool
    viewed_at: datetime
    last_consumed: Optional[datetime] = None

class UserDrinkInteractionUpdate(BaseModel):
    """User-drink interaction update model."""
    times_consumed: Optional[int] = Field(None, ge=0)
    is_favorite: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_not_for_me: Optional[bool] = None

class FavoriteDrink(BaseModel):
    """Favorite drink model (simplified drink info)."""
    drink_id: int
    name: str
    description: str
    category: str
    price_tier: str
    sweetness_level: int
    caffeine_content: int
    sugar_content: float
    calorie_content: int
    image_url: Optional[str]
    is_alcoholic: bool
    alcohol_content: float
    temperature: str
    serving_size: float
    serving_unit: str
    safety_flags: List[str]
    created_at: datetime
    updated_at: datetime
    ingredients: List[DrinkIngredient]
    tags: List[str]

class UserFavoritesResponse(BaseModel):
    """User favorites response model."""
    favorites: List[FavoriteDrink]
    total_count: int

# =========================
# RECOMMENDATION MODELS
# =========================

class SimilarDrink(BaseModel):
    """Similar drink model for recommendations."""
    drink_id: int
    name: str
    description: str
    category: str
    price_tier: str
    sweetness_level: int
    caffeine_content: int
    sugar_content: float
    calorie_content: int
    image_url: Optional[str]
    is_alcoholic: bool
    alcohol_content: float
    temperature: str
    serving_size: float
    serving_unit: str
    safety_flags: List[str]
    created_at: datetime
    updated_at: datetime
    similarity_score: float = Field(..., ge=0.0, le=1.0)

class DrinkRecommendationsResponse(BaseModel):
    """Drink-to-drink recommendations response model."""
    drink_id: int
    similar_drinks: List[SimilarDrink]
    count: int
    recommendation_type: str = Field(..., pattern="^(similar|collaborative|content)$")

class RecommendedDrink(BaseModel):
    """Recommended drink model."""
    drink_id: int
    name: str
    description: str
    category: str
    price_tier: str
    sweetness_level: int
    caffeine_content: int
    sugar_content: float
    calorie_content: int
    image_url: Optional[str]
    is_alcoholic: bool
    alcohol_content: float
    temperature: str
    serving_size: float
    serving_unit: str
    safety_flags: List[str]
    created_at: datetime
    updated_at: datetime

class UserRecommendation(BaseModel):
    """User recommendation model."""
    drink: RecommendedDrink
    score: float = Field(..., ge=0.0, le=1.0)
    explanation: List[str]

class UserRecommendationsResponse(BaseModel):
    """User recommendations response model."""
    recommendations: List[UserRecommendation]
    total_count: int
    recommendation_type: str = Field(..., pattern="^(hybrid|collaborative|content)$")

# =========================
# UTILITY MODELS
# =========================

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"

class ApiInfoResponse(BaseModel):
    """API information response model."""
    name: str
    version: str
    description: str
    features: List[str]
    services: List[str]

class RateLimitInfo(BaseModel):
    """Rate limit information model."""
    limit: int
    remaining: int
    reset: int

# =========================
# ENUMS
# =========================

class PriceTier(str, Enum):
    """Price tier enumeration."""
    BUDGET = "$"
    STANDARD = "$$"
    PREMIUM = "$$$"

class RecommendationType(str, Enum):
    """Recommendation type enumeration."""
    CONTENT_BASED = "content"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"

class VerificationType(str, Enum):
    """Verification type enumeration."""
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    LOGIN_VERIFICATION = "login_verification"

class FeedbackType(str, Enum):
    """Feedback type enumeration."""
    NOT_FOR_ME = "not_for_me"
    LOVE_IT = "love_it"
    TOO_SWEET = "too_sweet"
    TOO_BITTER = "too_bitter"
    TOO_EXPENSIVE = "too_expensive"
    PERFECT = "perfect"

# =========================
# PAGINATION MODELS
# =========================

class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    page: int
    limit: int
    total: int
    total_pages: int

# =========================
# SEARCH AND FILTER MODELS
# =========================

class DrinkSearchParams(BaseModel):
    """Drink search parameters."""
    category: Optional[str] = None
    price_tier: Optional[PriceTier] = None
    max_sweetness: Optional[int] = Field(None, ge=1, le=10)
    min_caffeine: Optional[int] = Field(None, ge=0)
    max_caffeine: Optional[int] = Field(None, ge=0)
    is_alcoholic: Optional[bool] = None
    excluded_ingredients: Optional[str] = None  # comma-separated
    search_text: Optional[str] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class RecommendationParams(BaseModel):
    """Recommendation parameters."""
    drink_id: Optional[int] = None
    limit: int = Field(10, ge=1, le=50)
    recommendation_type: Optional[RecommendationType] = None

# =========================
# VALIDATION HELPERS
# =========================

def validate_email_format(email: str) -> bool:
    """Validate email format."""
    try:
        email_obj = validate_email(email, check_deliverability=False)
        email_obj = email_obj.normalized
        return True
    except:
        return False

def validate_password_strength(password: str) -> Dict[str, bool]:
    """Validate password strength."""
    return {
        "has_min_length": len(password) >= 8,
        "has_uppercase": any(c.isupper() for c in password),
        "has_lowercase": any(c.islower() for c in password),
        "has_digit": any(c.isdigit() for c in password),
        "has_special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    }

def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements."""
    checks = validate_password_strength(password)
    return all(checks.values())

# Export all models
__all__ = [
    # Authentication
    "UserRegistration", "UserLogin", "UserResponse", "UserUpdate",
    "ForgotPassword", "ForgotPasswordResponse", "LogoutResponse",
    
    # Preferences
    "UserPreference", "UserPreferenceUpdate",
    
    # Catalog
    "DrinkIngredient", "Drink", "DrinkSearchResponse",
    "CategoriesResponse", "PopularDrinksResponse", "DrinkSearchParams",
    
    # # Quiz
    # "QuizOption", "QuizQuestion", "QuizQuestionsResponse",
    # "QuizAnswer", "QuizSubmission", "QuizSubmissionResponse",
    
    # Interactions
    "UserDrinkInteraction", "UserDrinkInteractionUpdate",
    "FavoriteDrink", "UserFavoritesResponse",
    
    # Recommendations
    "SimilarDrink", "DrinkRecommendationsResponse",
    "RecommendedDrink", "UserRecommendation", "UserRecommendationsResponse",
    "RecommendationParams",
    
    # Utilities
    "ErrorResponse", "HealthCheckResponse", "ApiInfoResponse",
    "RateLimitInfo", "PaginationParams", "PaginatedResponse",
    
    # Enums
    "PriceTier", "RecommendationType", "VerificationType", "FeedbackType",
    
    # Validation
    "validate_email_format", "validate_password_strength", "is_strong_password"
]
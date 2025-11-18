from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# =========================
# USER & AUTHENTICATION
# =========================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    confirmpassword: str = Field(..., min_length=8, max_length=128)
    age: Optional[int] = None
    date_of_birth: Optional[datetime] = None

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    joindate: datetime
    is_verified: bool
    age: Optional[int] = None
    verification_completed: bool
    profile_picture: str = ""
    description: str = ""
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user_id: int
    username: str
    email: str
    joindate: datetime
    access_token: str
    token_type: str = "bearer"
    profile_picture: str
    description: str
    is_verified: bool
    verification_completed: bool
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    age: Optional[int] = None
    date_of_birth: Optional[datetime] = None

# =========================
# EMAIL VERIFICATION
# =========================

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerificationResponse(BaseModel):
    verification_id: int
    user_id: int
    email: str
    message: str
    
    class Config:
        from_attributes = True

class VerifyEmailRequest(BaseModel):
    verification_token: str

class VerifyEmailResponse(BaseModel):
    user_id: int
    email: str
    is_verified: bool
    message: str
    
    class Config:
        from_attributes = True

# =========================
# DRINK CATALOG
# =========================

class DrinkBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: str
    category: str = Field(..., max_length=100)  # "coffee", "tea", "smoothie", "alcohol", etc.
    price_tier: str = Field(..., regex="^\\$|\\$\\$|\\$\\$\\$$")  # "$", "$$", "$$$"
    sweetness_level: int = Field(..., ge=1, le=10)
    caffeine_content: int = Field(..., ge=0)  # mg per serving
    sugar_content: float = Field(..., ge=0.0)  # grams per serving
    calorie_content: int = Field(..., ge=0)  # calories per serving
    image_url: Optional[str] = None
    is_alcoholic: bool = False
    alcohol_content: float = Field(..., ge=0.0, le=100.0)  # percentage
    safety_flags: Optional[List[str]] = None

class DrinkCreate(DrinkBase):
    ingredients: Optional[List[Dict[str, Any]]] = None  # [{"name": "Sugar", "quantity": "2 tbsp", "is_allergen": false}]
    tags: Optional[List[str]] = None

class DrinkResponse(DrinkBase):
    drink_id: int
    created_at: datetime
    updated_at: datetime
    ingredients: List[Dict[str, Any]] = []
    tags: List[str] = []
    
    class Config:
        from_attributes = True

class DrinkIngredientResponse(BaseModel):
    ingredient_name: str
    quantity: Optional[str] = None
    is_allergen: bool
    
    class Config:
        from_attributes = True

class DrinkSearchParams(BaseModel):
    category: Optional[str] = None
    price_tier: Optional[str] = None
    max_sweetness: Optional[int] = Field(None, ge=1, le=10)
    min_caffeine: Optional[int] = Field(None, ge=0)
    max_caffeine: Optional[int] = Field(None, ge=0)
    is_alcoholic: Optional[bool] = None
    excluded_ingredients: Optional[List[str]] = None
    search_text: Optional[str] = None
    page: int = 1
    limit: int = 20

class PaginatedDrinkResponse(BaseModel):
    drinks: List[DrinkResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# =========================
# USER PREFERENCES
# =========================

class UserPreferenceBase(BaseModel):
    sweetness_preference: int = Field(..., ge=1, le=10)
    bitterness_preference: int = Field(..., ge=1, le=10)
    preferred_categories: Optional[List[str]] = None
    sugar_limit: float = Field(..., ge=0.0)
    caffeine_limit: int = Field(..., ge=0)
    calorie_limit: int = Field(..., ge=0)
    preferred_price_tier: str = Field(..., regex="^\\$|\\$\\$|\\$\\$\\$$")
    time_sensitivity: Optional[Dict[str, Any]] = None
    mode_preferences: Optional[Dict[str, Any]] = None

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreferenceUpdate(BaseModel):
    sweetness_preference: Optional[int] = Field(None, ge=1, le=10)
    bitterness_preference: Optional[int] = Field(None, ge=1, le=10)
    preferred_categories: Optional[List[str]] = None
    sugar_limit: Optional[float] = Field(None, ge=0.0)
    caffeine_limit: Optional[int] = Field(None, ge=0)
    calorie_limit: Optional[int] = Field(None, ge=0)
    preferred_price_tier: Optional[str] = Field(None, regex="^\\$|\\$\\$|\\$\\$\\$$")
    time_sensitivity: Optional[Dict[str, Any]] = None
    mode_preferences: Optional[Dict[str, Any]] = None

class UserPreferenceResponse(UserPreferenceBase):
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# =========================
# USER FILTERS
# =========================

class UserFilterBase(BaseModel):
    budget_tier: Optional[str] = Field(None, regex="^\\$|\\$\\$|\\$\\$\\$$")
    sweetness_filter: Optional[int] = Field(None, ge=1, le=10)
    caffeine_min: Optional[int] = Field(None, ge=0)
    caffeine_max: Optional[int] = Field(None, ge=0)
    excluded_ingredients: Optional[List[str]] = None
    excluded_categories: Optional[List[str]] = None

class UserFilterCreate(UserFilterBase):
    pass

class UserFilterUpdate(BaseModel):
    budget_tier: Optional[str] = Field(None, regex="^\\$|\\$\\$|\\$\\$\\$$")
    sweetness_filter: Optional[int] = Field(None, ge=1, le=10)
    caffeine_min: Optional[int] = Field(None, ge=0)
    caffeine_max: Optional[int] = Field(None, ge=0)
    excluded_ingredients: Optional[List[str]] = None
    excluded_categories: Optional[List[str]] = None
    is_active: Optional[bool] = None

class UserFilterResponse(UserFilterBase):
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# =========================
# TASTE QUIZ SYSTEM
# =========================

class TasteQuizQuestionBase(BaseModel):
    question_text: str
    question_type: str = Field(..., regex="^(multiple_choice|scale|boolean)$")
    options: Optional[List[str]] = None
    category: str

class TasteQuizQuestionCreate(TasteQuizQuestionBase):
    pass

class TasteQuizQuestionResponse(TasteQuizQuestionBase):
    question_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuizAnswer(BaseModel):
    question_id: int
    answer: str

class TasteQuizSubmission(BaseModel):
    answers: List[QuizAnswer]

class TasteQuizResponse(BaseModel):
    questions: List[TasteQuizQuestionResponse]
    total_questions: int

# =========================
# USER DRINK INTERACTIONS
# =========================

class UserDrinkInteractionBase(BaseModel):
    drink_id: int
    times_consumed: int = 0
    is_favorite: bool = False
    rating: float = Field(0.0, ge=0.0, le=5.0)
    is_not_for_me: bool = False

class UserDrinkInteractionUpdate(BaseModel):
    times_consumed: Optional[int] = None
    is_favorite: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_not_for_me: Optional[bool] = None

class UserDrinkInteractionResponse(BaseModel):
    user_id: int
    drink_id: int
    times_consumed: int
    is_favorite: bool
    rating: float
    is_not_for_me: bool
    viewed_at: datetime
    last_consumed: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserFavoritesResponse(BaseModel):
    favorites: List[DrinkResponse]
    total_count: int

class UserRecentlyViewedResponse(BaseModel):
    recently_viewed: List[DrinkResponse]
    total_count: int

# =========================
# RECOMMENDATION SYSTEM
# =========================

# class RecommendationRequest(BaseModel):
#     limit: int = Field(10, ge=1, le=50)
#     recommendation_type: Optional[str] = Field(None, regex="^(hybrid|collaborative|content)$")

# class RecommendationItem(BaseModel):
#     drink: DrinkResponse
#     score: float
#     explanation: List[str]

# class RecommendationResponse(BaseModel):
#     recommendations: List[RecommendationItem]
#     total_count: int
#     recommendation_type: str

class UserFeedbackBase(BaseModel):
    drink_id: int
    feedback_type: str = Field(..., regex="^(not_for_me|love_it|too_sweet|too_bitter|too_expensive|perfect)$")
    feedback_text: Optional[str] = None

class UserFeedbackCreate(UserFeedbackBase):
    pass

class UserFeedbackResponse(UserFeedbackBase):
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# =========================
# ERROR RESPONSES
# =========================

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ValidationErrorResponse(BaseModel):
    error: str = "Validation Error"
    message: str
    field_errors: Dict[str, List[str]]

# =========================
# HEALTH CHECK
# =========================

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"

# =========================
# ANALYTICS
# =========================

class UserAnalyticsResponse(BaseModel):
    total_favorites: int
    total_recently_viewed: int
    total_recommendations_received: int
    quiz_completed: bool
    preferences_set: bool
    age_verified: bool
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Text, PrimaryKeyConstraint, Index, CheckConstraint, Enum, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum
from datetime import datetime, timedelta

# =========================
# USER & AUTHENTICATION
# =========================

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    joindate = Column(DateTime, nullable=False, default=datetime.now)
    password = Column(String(128), nullable=False)
    session_at = Column(DateTime, nullable=True)
    access_key = Column(String(400), nullable=True)
    profile_picture = Column(String(400), nullable=False, default="")
    description = Column(String(800), nullable=False, default="")
    is_verified = Column(Boolean, nullable=False, default=False)
    age = Column(Integer, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    verification_completed = Column(Boolean, nullable=False, default=False)

# class Verification(Base):
#     __tablename__ = "verification"

#     id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
#     email = Column(String(100), nullable=False)    
#     code = Column(String(6), nullable=False)      
#     type = Column(String(20), nullable=False)     
#     created_at = Column(DateTime, nullable=False, default=datetime.now())
#     expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now() + timedelta(minutes=10))
#     is_used = Column(Boolean, nullable=False, default=False)

# =========================
# DRINK CATALOG
# =========================

class Drink(Base):
    __tablename__ = "drink"
    drink_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # e.g., "coffee", "tea", "smoothie", "alcohol"
    price_tier = Column(String(10), nullable=False)  # "$", "$$", "$$$"
    sweetness_level = Column(Integer, nullable=False, default=5)  # 1-10 scale
    caffeine_content = Column(Integer, nullable=False, default=0)  # mg per serving
    sugar_content = Column(Float, nullable=False, default=0.0)  # grams per serving
    calorie_content = Column(Integer, nullable=False, default=0)  # calories per serving
    image_url = Column(Text, nullable=True)
    is_alcoholic = Column(Boolean, nullable=False, default=False)
    alcohol_content = Column(Float, nullable=False, default=0.0)  # percentage
    safety_flags = Column(JSON, nullable=True)  # array of safety warnings
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        CheckConstraint('sweetness_level BETWEEN 1 AND 10', name='check_sweetness_range'),
        CheckConstraint('caffeine_content >= 0', name='check_caffeine_non_negative'),
        CheckConstraint('sugar_content >= 0', name='check_sugar_non_negative'),
        CheckConstraint('calorie_content >= 0', name='check_calorie_non_negative'),
        CheckConstraint('alcohol_content >= 0 AND alcohol_content <= 100', name='check_alcohol_range'),
        Index('idx_drink_category', 'category'),
        Index('idx_drink_price_tier', 'price_tier'),
        Index('idx_drink_alcoholic', 'is_alcoholic'),
    )
    
    ingredients = relationship("DrinkIngredient", back_populates="drink", cascade="all, delete-orphan")
    tags = relationship("DrinkTag", back_populates="drink", cascade="all, delete-orphan")

class DrinkIngredient(Base):
    __tablename__ = "drink_ingredient"
    drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    ingredient_name = Column(String(100), primary_key=True, nullable=False)
    quantity = Column(String(50), nullable=True)  # e.g., "2 tbsp", "1 cup"
    is_allergen = Column(Boolean, nullable=False, default=False)

    __table_args__ = (Index('ix_drink_ingredient', 'drink_id', 'ingredient_name'),)
    drink = relationship("Drink", back_populates="ingredients")

class DrinkTag(Base):
    __tablename__ = "drink_tag"
    drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    tag_name = Column(String(50), primary_key=True, nullable=False)

    __table_args__ = (
        Index('ix_drink_tag', 'drink_id', 'tag_name'),
        PrimaryKeyConstraint('drink_id', 'tag_name', name='unique_drink_tag')
    )
    drink = relationship("Drink", back_populates="tags")

# =========================
# USER PREFERENCES & FILTERS
# =========================

class UserPreference(Base):
    __tablename__ = "user_preference"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    sweetness_preference = Column(Integer, nullable=False, default=5)  # 1-10 scale
    bitterness_preference = Column(Integer, nullable=False, default=5)  # 1-10 scale
    preferred_categories = Column(JSON, nullable=True)  # array of preferred categories
    sugar_limit = Column(Float, nullable=False, default=50.0)  # grams per day
    caffeine_limit = Column(Integer, nullable=False, default=400)  # mg per day
    calorie_limit = Column(Integer, nullable=False, default=2000)  # per day
    preferred_price_tier = Column(String(10), nullable=False, default="$$")  # "$", "$$", "$$$"
    time_sensitivity = Column(JSON, nullable=True)  # rules for time-based preferences
    mode_preferences = Column(JSON, nullable=True)  # decaf, low-caf, energy modes
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        CheckConstraint('sweetness_preference BETWEEN 1 AND 10', name='check_sweetness_pref'),
        CheckConstraint('bitterness_preference BETWEEN 1 AND 10', name='check_bitterness_pref'),
        CheckConstraint('sugar_limit >= 0', name='check_sugar_limit'),
        CheckConstraint('caffeine_limit >= 0', name='check_caffeine_limit'),
        CheckConstraint('calorie_limit >= 0', name='check_calorie_limit'),
    )

class UserFilter(Base):
    __tablename__ = "user_filter"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    budget_tier = Column(String(10), nullable=True)  # "$", "$$", "$$$"
    sweetness_filter = Column(Integer, nullable=True)  # max sweetness level
    caffeine_min = Column(Integer, nullable=True)
    caffeine_max = Column(Integer, nullable=True)
    excluded_ingredients = Column(JSON, nullable=True)  # array of excluded ingredients
    excluded_categories = Column(JSON, nullable=True)  # array of excluded categories
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        CheckConstraint('caffeine_min >= 0', name='check_caffeine_min'),
        CheckConstraint('caffeine_max >= 0', name='check_caffeine_max'),
    )

# =========================
# TASTE QUIZ SYSTEM
# =========================

class TasteQuizQuestion(Base):
    __tablename__ = "taste_quiz_question"
    question_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # "multiple_choice", "scale", "boolean"
    options = Column(JSON, nullable=True)  # array of options for multiple choice
    category = Column(String(50), nullable=False)  # "sweetness", "bitterness", "caffeine", etc.
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

class TasteQuizResult(Base):
    __tablename__ = "taste_quiz_result"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    question_id = Column(Integer, ForeignKey("taste_quiz_question.question_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    answer = Column(String(200), nullable=False)
    answered_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (Index('ix_quiz_result_user', 'user_id'),)
    question = relationship("TasteQuizQuestion")

# =========================
# USER DRINK INTERACTIONS
# =========================

class UserDrinkInteraction(Base):
    __tablename__ = "user_drink_interaction"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    times_consumed = Column(Integer, nullable=False, default=0)
    is_favorite = Column(Boolean, nullable=False, default=False)
    rating = Column(Float, nullable=False, default=0)  # 1-5 scale
    is_not_for_me = Column(Boolean, nullable=False, default=False)
    viewed_at = Column(DateTime, nullable=False, default=datetime.now)
    last_consumed = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint('times_consumed >= 0', name='check_times_consumed'),
        CheckConstraint('rating BETWEEN 0 AND 5', name='check_rating_range'),
        Index('ix_user_drink_user', 'user_id'),
        Index('ix_user_drink_favorite', 'is_favorite'),
        Index('ix_user_drink_not_for_me', 'is_not_for_me'),
    )

class UserFavorite(Base):
    __tablename__ = "user_favorite"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    favorited_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'drink_id', name='unique_user_favorite'),
        Index('ix_user_favorite_user', 'user_id'),
    )

class UserRecentlyViewed(Base):
    __tablename__ = "user_recently_viewed"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    viewed_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'drink_id', name='unique_user_viewed'),
        Index('ix_recently_viewed_user', 'user_id'),
        Index('ix_recently_viewed_time', 'viewed_at'),
    )

# =========================
# RECOMMENDATION SYSTEM
# =========================

# class Recommendation(Base):
#     __tablename__ = "recommendation"

#     recommendation_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
#     drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), nullable=False)
#     recommendation_score = Column(Float, nullable=False)
#     explanation = Column(JSON, nullable=True)  # array of explanation strings
#     recommendation_type = Column(String(50), nullable=False)  # "hybrid", "collaborative", "content"
#     created_at = Column(DateTime, nullable=False, default=datetime.now)
#     is_active = Column(Boolean, nullable=False, default=True)

#     __table_args__ = (
#         CheckConstraint('recommendation_score >= 0 AND recommendation_score <= 1', name='check_score_range'),
#         Index('ix_recommendation_user', 'user_id'),
#         Index('ix_recommendation_score', 'recommendation_score'),
#     )

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    feedback_type = Column(String(50), nullable=False)  # "not_for_me", "love_it", "too_sweet", etc.
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'drink_id', 'feedback_type', name='unique_user_feedback'),
        Index('ix_user_feedback_user', 'user_id'),
        Index('ix_user_feedback_type', 'feedback_type'),
    )

# =========================
# EXTERNAL INTEGRATIONS
# =========================

# class EmailVerification(Base):
#     __tablename__ = "email_verification"
#     verification_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
#     email = Column(String(100), nullable=False)
#     verification_token = Column(String(200), nullable=False)
#     is_verified = Column(Boolean, nullable=False, default=False)
#     created_at = Column(DateTime, nullable=False, default=datetime.now)
#     expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now() + timedelta(hours=24))

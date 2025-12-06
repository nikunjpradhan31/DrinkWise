from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Text, PrimaryKeyConstraint, Index, CheckConstraint, Enum, JSON
from sqlalchemy.orm import relationship
from database import Base
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
    is_verified = Column(Boolean, nullable=False, default=False)
    date_of_birth = Column(DateTime, nullable=True)
    questionnaire_finished = Column(Boolean, nullable=False, default=False)

class Verification(Base):
    __tablename__ = "verification"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    email = Column(String(100), nullable=False)
    code = Column(String(6), nullable=False)
    verification_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now() + timedelta(minutes=10))
    is_used = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('ix_verification_user', 'user_id'),
        Index('ix_verification_email', 'email'),
    )

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

class DrinkIngredient(Base):
    __tablename__ = "drink_ingredient"
    drink_id = Column(Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    ingredient_name = Column(String(100), primary_key=True, nullable=False)
    quantity = Column(String(50), nullable=True)  # e.g., "2 tbsp", "1 cup"
    is_allergen = Column(Boolean, nullable=False, default=False)

    __table_args__ = (Index('ix_drink_ingredient', 'drink_id', 'ingredient_name'),)
    drink = relationship("Drink", back_populates="ingredients")

# =========================
# USER PREFERENCES & FILTERS
# =========================

class UserPreference(Base):
    __tablename__ = "user_preference"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    sweetness_preference = Column(Integer, nullable=False, default=5)  # 1-10 scale
    bitterness_preference = Column(Integer, nullable=False, default=5)  # 1-10 scale
    caffeine_limit = Column(Integer, nullable=False, default=400)  # mg per day
    calorie_limit = Column(Integer, nullable=False, default=2000)  # per day
    preferred_price_tier = Column(String(10), nullable=False, default="$$")  # "$", "$$", "$$$"
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        CheckConstraint('sweetness_preference BETWEEN 1 AND 10', name='check_sweetness_pref'),
        CheckConstraint('bitterness_preference BETWEEN 1 AND 10', name='check_bitterness_pref'),
        CheckConstraint('caffeine_limit >= 0', name='check_caffeine_limit'),
        CheckConstraint('calorie_limit >= 0', name='check_calorie_limit'),
    )

# =========================
# TASTE QUIZ SYSTEM
# =========================

class TasteQuizQuestion(Base):
    __tablename__ = "taste_quiz_question"

    question_id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class TasteQuizOption(Base):
    __tablename__ = "taste_quiz_option"

    option_id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("taste_quiz_question.question_id", ondelete="CASCADE"), nullable=False)
    option_text = Column(String(200), nullable=False)
    question = relationship("TasteQuizQuestion", backref="options", cascade="all, delete")

class TasteQuizResult(Base):
    __tablename__ = "taste_quiz_result"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    question_id = Column(Integer, ForeignKey("taste_quiz_question.question_id", ondelete="CASCADE"), primary_key=True)
    option_id = Column(Integer, ForeignKey("taste_quiz_option.option_id", ondelete="CASCADE"), nullable=False)
    answered_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    question = relationship("TasteQuizQuestion")
    option = relationship("TasteQuizOption")

    __table_args__ = (
        Index('ix_quiz_result_user', 'user_id'),
    )

# =========================
# USER-DRINK INTERACTIONS
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
    last_consumed_at = Column(DateTime, nullable=True)
    __table_args__ = (
        CheckConstraint('times_consumed >= 0', name='check_times_consumed'),
        CheckConstraint('rating BETWEEN 0 AND 5', name='check_rating_range'),
        Index('ix_user_drink_user', 'user_id'),
        Index('ix_user_drink_favorite', 'is_favorite'),
        Index('ix_user_drink_not_for_me', 'is_not_for_me'),
    )
"""SQLAlchemy models for drinks and ingredients."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Drink(Base):
    __tablename__ = "drink"
    drink_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    price_tier = Column(String(10), nullable=False)
    sweetness_level = Column(Integer, nullable=False, default=5)
    caffeine_content = Column(Integer, nullable=False, default=0)
    sugar_content = Column(Float, nullable=False, default=0.0)
    calorie_content = Column(Integer, nullable=False, default=0)
    image_url = Column(Text)
    is_alcoholic = Column(Boolean, nullable=False, default=False)
    alcohol_content = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    __table_args__ = (
        CheckConstraint("sweetness_level BETWEEN 1 AND 10"),
        CheckConstraint("caffeine_content >= 0"),
        CheckConstraint("sugar_content >= 0"),
        CheckConstraint("calorie_content >= 0"),
        CheckConstraint("alcohol_content >= 0 AND alcohol_content <= 100"),
        Index("idx_drink_category", "category"),
        Index("idx_drink_price_tier", "price_tier"),
        Index("idx_drink_alcoholic", "is_alcoholic"),
    )

    ingredients = relationship(
        "DrinkIngredient", back_populates="drink", cascade="all, delete-orphan"
    )


class DrinkIngredient(Base):
    __tablename__ = "drink_ingredient"
    drink_id = Column(
        Integer, ForeignKey("drink.drink_id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_name = Column(String(100), primary_key=True, nullable=False)
    quantity = Column(String(50))
    is_allergen = Column(Boolean, nullable=False, default=False)

    __table_args__ = (Index("ix_drink_ingredient", "drink_id", "ingredient_name"),)
    drink = relationship("Drink", back_populates="ingredients")

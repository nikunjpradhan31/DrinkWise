"""
Unit tests for CatalogService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.catalog_service import CatalogService
from models import Drink, DrinkIngredient
from pydantic_models import DrinkSearchParams, PriceTier

@pytest.fixture
def catalog_service(mock_db):
    """Create a CatalogService instance with mock database session."""
    return CatalogService(mock_db)

@pytest.mark.asyncio
async def test_search_drinks(catalog_service, mock_db):
    """Test drink search functionality."""
    # Mock drinks
    mock_drink1 = MagicMock(spec=Drink)
    mock_drink1.drink_id = 1
    mock_drink1.name = "Coffee"
    mock_drink1.category = "Coffee"
    mock_drink1.price_tier = PriceTier.MEDIUM
    mock_drink1.sweetness_level = 5
    mock_drink1.caffeine_content = 100
    mock_drink1.is_alcoholic = False
    mock_drink1.ingredients = []

    mock_drink2 = MagicMock(spec=Drink)
    mock_drink2.drink_id = 2
    mock_drink2.name = "Tea"
    mock_drink2.category = "Tea"
    mock_drink2.price_tier = PriceTier.LOW
    mock_drink2.sweetness_level = 3
    mock_drink2.caffeine_content = 50
    mock_drink2.is_alcoholic = False
    mock_drink2.ingredients = []

    # Mock database responses
    mock_db.execute.return_value.scalar.return_value = 2  # Total count
    mock_db.execute.return_value.scalars.return_value = [mock_drink1, mock_drink2]

    search_params = DrinkSearchParams(
        search_text="",
        category=None,
        price_tier=None,
        max_sweetness=None,
        min_caffeine=None,
        max_caffeine=None,
        is_alcoholic=None,
        excluded_ingredients=None,
        page=1,
        limit=10
    )

    result = await catalog_service.search_drinks(search_params)

    assert result.total == 2
    assert len(result.drinks) == 2
    assert result.page == 1
    assert result.limit == 10

@pytest.mark.asyncio
async def test_get_drink_by_id(catalog_service, mock_db):
    """Test getting a drink by ID."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee"
    mock_drink.description = "Hot coffee"
    mock_drink.category = "Coffee"
    mock_drink.price_tier = PriceTier.MEDIUM
    mock_drink.sweetness_level = 5
    mock_drink.caffeine_content = 100
    mock_drink.sugar_content = 0
    mock_drink.calorie_content = 5
    mock_drink.image_url = "coffee.jpg"
    mock_drink.is_alcoholic = False
    mock_drink.alcohol_content = 0.0
    mock_drink.temperature = "hot"
    mock_drink.serving_size = 8
    mock_drink.serving_unit = "oz"
    mock_drink.created_at = datetime.now()
    mock_drink.updated_at = datetime.now()
    mock_drink.ingredients = []

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_drink

    drink = await catalog_service.get_drink_by_id(1)

    assert drink is not None
    assert drink.drink_id == 1
    assert drink.name == "Coffee"

@pytest.mark.asyncio
async def test_get_categories(catalog_service, mock_db):
    """Test getting drink categories."""
    # Mock categories
    mock_db.execute.return_value.scalars.return_value = ["Coffee", "Tea", "Smoothie"]

    categories = await catalog_service.get_categories()

    assert len(categories) == 3
    assert "Coffee" in categories
    assert "Tea" in categories

@pytest.mark.asyncio
async def test_get_popular_drinks(catalog_service, mock_db):
    """Test getting popular drinks."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Popular Coffee"
    mock_drink.ingredients = []

    mock_db.execute.return_value.scalars.return_value = [mock_drink]

    drinks = await catalog_service.get_popular_drinks(limit=5)

    assert len(drinks) == 1
    assert drinks[0].name == "Popular Coffee"

@pytest.mark.asyncio
async def test_get_alcoholic_drinks(catalog_service, mock_db):
    """Test getting alcoholic drinks."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Cocktail"
    mock_drink.is_alcoholic = True
    mock_drink.ingredients = []

    mock_db.execute.return_value.scalars.return_value = [mock_drink]

    drinks = await catalog_service.get_alcoholic_drinks(limit=5)

    assert len(drinks) == 1
    assert drinks[0].name == "Cocktail"
    assert drinks[0].is_alcoholic is True

@pytest.mark.asyncio
async def test_get_drink_statistics(catalog_service, mock_db):
    """Test getting drink statistics."""
    # Mock statistics data
    mock_db.execute.side_effect = [
        MagicMock(scalar=10),  # Total drinks
        MagicMock(all=[("Coffee", 5), ("Tea", 3), ("Smoothie", 2)]),  # Categories
        MagicMock(all=[(PriceTier.LOW, 2), (PriceTier.MEDIUM, 5), (PriceTier.HIGH, 3)]),  # Price tiers
        MagicMock(first=(3,)),  # Alcoholic count
        MagicMock(first=(5.0, 100.0, 10.0, 50.0))  # Nutrition stats
    ]

    stats = await catalog_service.get_drink_statistics()

    assert stats["total_drinks"] == 10
    assert stats["alcoholic_count"] == 3
    assert "categories" in stats
    assert "price_tiers" in stats

@pytest.mark.asyncio
async def test_create_drink(catalog_service, mock_db):
    """Test creating a new drink."""
    drink_data = {
        "name": "New Drink",
        "description": "A new drink",
        "category": "Coffee",
        "price_tier": PriceTier.MEDIUM,
        "sweetness_level": 5,
        "caffeine_content": 100,
        "sugar_content": 0,
        "calorie_content": 5,
        "image_url": "new_drink.jpg",
        "is_alcoholic": False,
        "alcohol_content": 0.0,
        "temperature": "hot",
        "serving_size": 8,
        "serving_unit": "oz",
        "ingredients": []
    }

    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_db.refresh.return_value = mock_drink

    drink_id = await catalog_service.create_drink(drink_data)

    assert drink_id == 1
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_update_drink(catalog_service, mock_db):
    """Test updating a drink."""
    update_data = {
        "name": "Updated Drink",
        "description": "Updated description",
        "ingredients": []
    }

    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute.return_value = mock_result

    success = await catalog_service.update_drink(1, update_data)

    assert success is True
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_delete_drink(catalog_service, mock_db):
    """Test deleting a drink."""
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute.return_value = mock_result

    success = await catalog_service.delete_drink(1)

    assert success is True
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_get_drinks_by_ingredients(catalog_service, mock_db):
    """Test getting drinks by ingredients."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee with Milk"
    mock_drink.ingredients = [
        MagicMock(ingredient_name="coffee", quantity="1 cup", is_allergen=False),
        MagicMock(ingredient_name="milk", quantity="1 oz", is_allergen=False)
    ]

    mock_db.execute.return_value.scalars.return_value = [mock_drink]

    drinks = await catalog_service.get_drinks_by_ingredients(["coffee", "milk"])

    assert len(drinks) == 1
    assert drinks[0].name == "Coffee with Milk"

@pytest.mark.asyncio
async def test_search_similar_drinks(catalog_service, mock_db):
    """Test searching for similar drinks."""
    # Mock reference drink
    mock_ref_drink = MagicMock()
    mock_ref_drink.drink_id = 1
    mock_ref_drink.name = "Coffee"
    mock_ref_drink.category = "Coffee"
    mock_ref_drink.price_tier = PriceTier.MEDIUM
    mock_ref_drink.sweetness_level = 5
    mock_ref_drink.caffeine_content = 100
    mock_ref_drink.is_alcoholic = False

    # Mock similar drink
    mock_similar_drink = MagicMock(spec=Drink)
    mock_similar_drink.drink_id = 2
    mock_similar_drink.name = "Espresso"
    mock_similar_drink.category = "Coffee"
    mock_similar_drink.price_tier = PriceTier.MEDIUM
    mock_similar_drink.sweetness_level = 4
    mock_similar_drink.caffeine_content = 120
    mock_similar_drink.is_alcoholic = False
    mock_similar_drink.ingredients = []

    mock_db.execute.side_effect = [
        mock_ref_drink,  # get_drink_by_id
        MagicMock(scalars=MagicMock(return_value=[mock_similar_drink]))  # search query
    ]

    similar_drinks = await catalog_service.search_similar_drinks(1, limit=5)

    assert len(similar_drinks) == 1
    assert similar_drinks[0]["drink"].name == "Espresso"
    assert "similarity_score" in similar_drinks[0]

def test_calculate_similarity_score(catalog_service):
    """Test similarity score calculation."""
    from pydantic_models import Drink as DrinkModel

    drink1 = DrinkModel(
        drink_id=1,
        name="Coffee",
        category="Coffee",
        price_tier=PriceTier.MEDIUM,
        sweetness_level=5,
        caffeine_content=100,
        is_alcoholic=False,
        ingredients=[]
    )

    drink2 = DrinkModel(
        drink_id=2,
        name="Espresso",
        category="Coffee",
        price_tier=PriceTier.MEDIUM,
        sweetness_level=4,
        caffeine_content=120,
        is_alcoholic=False,
        ingredients=[]
    )

    score = catalog_service._calculate_similarity_score(drink1, drink2)

    # Should be high since they're similar
    assert 0.5 < score < 1.0

def test_get_match_reasons(catalog_service):
    """Test getting match reasons."""
    from pydantic_models import Drink as DrinkModel

    drink1 = DrinkModel(
        drink_id=1,
        name="Coffee",
        category="Coffee",
        price_tier=PriceTier.MEDIUM,
        sweetness_level=5,
        caffeine_content=100,
        is_alcoholic=False,
        ingredients=[]
    )

    drink2 = DrinkModel(
        drink_id=2,
        name="Espresso",
        category="Coffee",
        price_tier=PriceTier.MEDIUM,
        sweetness_level=4,
        caffeine_content=120,
        is_alcoholic=False,
        ingredients=[]
    )

    reasons = catalog_service._get_match_reasons(drink1, drink2)

    assert len(reasons) > 0
    assert any("Same category" in reason for reason in reasons)
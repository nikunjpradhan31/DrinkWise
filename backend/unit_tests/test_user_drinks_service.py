"""
Unit tests for UserDrinksService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from services.user_drinks_service import UserDrinksService
from models import UserDrinkInteraction, Drink, Users
from pydantic_models import UserDrinkInteraction as UserDrinkInteractionModel, UserDrinkInteractionUpdate

@pytest.fixture
def user_drinks_service(mock_db):
    """Create a UserDrinksService instance with mock database session."""
    return UserDrinksService(mock_db)

@pytest.mark.asyncio
async def test_get_user_drink_interaction(user_drinks_service, mock_db):
    """Test getting user drink interaction."""
    # Mock interaction
    mock_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_interaction.user_id = 1
    mock_interaction.drink_id = 1
    mock_interaction.times_consumed = 3
    mock_interaction.is_favorite = True
    mock_interaction.rating = 4.5
    mock_interaction.is_not_for_me = False
    mock_interaction.viewed_at = datetime.now()
    mock_interaction.last_consumed_at = datetime.now()

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_interaction

    interaction = await user_drinks_service.get_user_drink_interaction(1, 1)

    assert interaction is not None
    assert interaction.times_consumed == 3
    assert interaction.is_favorite is True
    assert interaction.rating == 4.5

@pytest.mark.asyncio
async def test_ensure_user_drink_interaction_new(user_drinks_service, mock_db):
    """Test ensuring user drink interaction when none exists."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee"

    # Mock new interaction
    mock_new_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_new_interaction.user_id = 1
    mock_new_interaction.drink_id = 1
    mock_new_interaction.times_consumed = 0
    mock_new_interaction.is_favorite = False
    mock_new_interaction.rating = 0.0
    mock_new_interaction.is_not_for_me = False
    mock_new_interaction.viewed_at = datetime.now()
    mock_new_interaction.last_consumed_at = None

    # Mock results
    mock_drink_result = MagicMock()
    mock_drink_result.scalar_one_or_none.return_value = mock_drink

    mock_interaction_result = MagicMock()
    mock_interaction_result.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [
        mock_drink_result,  # get drink
        mock_interaction_result,  # get interaction
    ]
    mock_db.refresh.return_value = mock_new_interaction

    interaction = await user_drinks_service.ensure_user_drink_interaction(1, 1)

    assert interaction is not None
    assert interaction.times_consumed == 0
    assert interaction.is_favorite is False

@pytest.mark.asyncio
async def test_ensure_user_drink_interaction_existing(user_drinks_service, mock_db):
    """Test ensuring user drink interaction when it already exists."""
    # Mock existing interaction
    mock_existing_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_existing_interaction.user_id = 1
    mock_existing_interaction.drink_id = 1
    mock_existing_interaction.times_consumed = 2
    mock_existing_interaction.is_favorite = True
    mock_existing_interaction.rating = 4.0
    mock_existing_interaction.is_not_for_me = False
    mock_existing_interaction.viewed_at = datetime.now()
    mock_existing_interaction.last_consumed_at = datetime.now()

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_existing_interaction

    interaction = await user_drinks_service.ensure_user_drink_interaction(1, 1)

    assert interaction is not None
    assert interaction.times_consumed == 2
    assert interaction.is_favorite is True

@pytest.mark.asyncio
async def test_update_user_drink_interaction_new(user_drinks_service, mock_db):
    """Test updating user drink interaction when creating new one."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee"

    # Mock new interaction
    mock_new_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_new_interaction.user_id = 1
    mock_new_interaction.drink_id = 1
    mock_new_interaction.times_consumed = 5
    mock_new_interaction.is_favorite = True
    mock_new_interaction.rating = 4.5
    mock_new_interaction.is_not_for_me = False
    mock_new_interaction.viewed_at = datetime.now()
    mock_new_interaction.last_consumed_at = datetime.now()

    # Mock updated interaction
    mock_updated_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_updated_interaction.user_id = 1
    mock_updated_interaction.drink_id = 1
    mock_updated_interaction.times_consumed = 5
    mock_updated_interaction.is_favorite = True
    mock_updated_interaction.rating = 4.5
    mock_updated_interaction.is_not_for_me = False
    mock_updated_interaction.viewed_at = datetime.now()
    mock_updated_interaction.last_consumed_at = datetime.now()

    # Mock results
    mock_drink_result = MagicMock()
    mock_drink_result.scalar_one_or_none.return_value = mock_drink

    mock_interaction_result = MagicMock()
    mock_interaction_result.scalar_one_or_none.return_value = None

    mock_updated_result = MagicMock()
    mock_updated_result.scalar_one_or_none.return_value = mock_updated_interaction

    mock_db.execute.side_effect = [
        mock_drink_result,  # get drink
        mock_interaction_result,  # get interaction
        mock_updated_result  # get interaction again
    ]
    mock_db.refresh.return_value = mock_new_interaction

    update_data = UserDrinkInteractionUpdate(
        times_consumed=5,
        is_favorite=True,
        rating=4.5
    )

    interaction = await user_drinks_service.update_user_drink_interaction(1, 1, update_data)

    assert interaction is not None
    assert interaction.times_consumed == 5
    assert interaction.is_favorite is True
    assert interaction.rating == 4.5

@pytest.mark.asyncio
async def test_update_user_drink_interaction_existing(user_drinks_service, mock_db):
    """Test updating user drink interaction when it already exists."""
    # Mock existing interaction
    mock_existing_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_existing_interaction.user_id = 1
    mock_existing_interaction.drink_id = 1
    mock_existing_interaction.times_consumed = 3
    mock_existing_interaction.is_favorite = False
    mock_existing_interaction.rating = 3.0
    mock_existing_interaction.is_not_for_me = False
    mock_existing_interaction.viewed_at = datetime.now()
    mock_existing_interaction.last_consumed_at = datetime.now()

    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee"

    # Mock updated interaction
    mock_updated_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_updated_interaction.user_id = 1
    mock_updated_interaction.drink_id = 1
    mock_updated_interaction.times_consumed = 5
    mock_updated_interaction.is_favorite = True
    mock_updated_interaction.rating = 4.5
    mock_updated_interaction.is_not_for_me = False
    mock_updated_interaction.viewed_at = datetime.now()
    mock_updated_interaction.last_consumed_at = datetime.now()

    mock_db.execute.side_effect = [
        mock_drink,  # get drink
        mock_existing_interaction,  # get interaction
        mock_updated_interaction  # get interaction again
    ]

    update_data = UserDrinkInteractionUpdate(
        times_consumed=5,
        is_favorite=True,
        rating=4.5
    )

    interaction = await user_drinks_service.update_user_drink_interaction(1, 1, update_data)

    assert interaction is not None
    assert interaction.times_consumed == 5
    assert interaction.is_favorite is True
    assert interaction.rating == 4.5

@pytest.mark.asyncio
async def test_get_user_favorites(user_drinks_service, mock_db):
    """Test getting user favorites."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee"
    mock_drink.description = "Hot coffee"
    mock_drink.category = "Coffee"
    mock_drink.price_tier = "$$"
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

    # Mock interaction
    mock_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_interaction.user_id = 1
    mock_interaction.drink_id = 1
    mock_interaction.is_favorite = True
    mock_interaction.drink = mock_drink

    mock_db.execute.return_value.scalars.return_value = [mock_interaction]

    result = await user_drinks_service.get_user_favorites(1)

    assert result["total_count"] == 1
    assert len(result["favorites"]) == 1
    assert result["favorites"][0].name == "Coffee"

@pytest.mark.asyncio
async def test_set_favorite_status(user_drinks_service, mock_db):
    """Test setting favorite status."""
    # No existing interaction
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Mock new interaction
    mock_new_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_new_interaction.user_id = 1
    mock_new_interaction.drink_id = 1
    mock_new_interaction.times_consumed = 0
    mock_new_interaction.is_favorite = True
    mock_new_interaction.rating = 0.0
    mock_new_interaction.is_not_for_me = False
    mock_new_interaction.viewed_at = datetime.now()
    mock_new_interaction.last_consumed_at = None

    mock_db.refresh.return_value = mock_new_interaction

    success = await user_drinks_service.set_favorite_status(1, 1, True)

    assert success is True
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_set_rating(user_drinks_service, mock_db):
    """Test setting drink rating."""
    # No existing interaction
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee"

    # Mock new interaction
    mock_new_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_new_interaction.user_id = 1
    mock_new_interaction.drink_id = 1
    mock_new_interaction.times_consumed = 0
    mock_new_interaction.is_favorite = False
    mock_new_interaction.rating = 4.5
    mock_new_interaction.is_not_for_me = False
    mock_new_interaction.viewed_at = datetime.now()
    mock_new_interaction.last_consumed_at = None

    mock_db.execute.side_effect = [
        mock_drink,  # get drink
        None,  # get interaction
        mock_new_interaction  # refresh
    ]

    success = await user_drinks_service.set_rating(1, 1, 4.5)

    assert success is True
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_increment_consumption(user_drinks_service, mock_db):
    """Test incrementing consumption count."""
    # No existing interaction
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Mock new interaction
    mock_new_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_new_interaction.user_id = 1
    mock_new_interaction.drink_id = 1
    mock_new_interaction.times_consumed = 1
    mock_new_interaction.is_favorite = False
    mock_new_interaction.rating = 0.0
    mock_new_interaction.is_not_for_me = False
    mock_new_interaction.viewed_at = datetime.now()
    mock_new_interaction.last_consumed_at = datetime.now()

    mock_db.refresh.return_value = mock_new_interaction

    success = await user_drinks_service.increment_consumption(1, 1, 1)

    assert success is True
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_remove_user_drink_interaction(user_drinks_service, mock_db):
    """Test removing user drink interaction."""
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute.return_value = mock_result

    success = await user_drinks_service.remove_user_drink_interaction(1, 1)

    assert success is True
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_get_user_drink_statistics(user_drinks_service, mock_db):
    """Test getting user drink statistics."""
    # Mock interactions
    mock_interaction1 = MagicMock(spec=UserDrinkInteraction)
    mock_interaction1.user_id = 1
    mock_interaction1.drink_id = 1
    mock_interaction1.times_consumed = 3
    mock_interaction1.is_favorite = True
    mock_interaction1.rating = 4.5
    mock_interaction1.viewed_at = datetime.now()

    mock_interaction2 = MagicMock(spec=UserDrinkInteraction)
    mock_interaction2.user_id = 1
    mock_interaction2.drink_id = 2
    mock_interaction2.times_consumed = 1
    mock_interaction2.is_favorite = False
    mock_interaction2.rating = 3.0
    mock_interaction2.viewed_at = datetime.now()

    mock_db.execute.return_value.scalars.return_value = [mock_interaction1, mock_interaction2]

    stats = await user_drinks_service.get_user_drink_statistics(1)

    assert stats["total_interactions"] == 2
    assert stats["favorites_count"] == 1
    assert stats["rated_drinks_count"] == 2
    assert stats["consumed_drinks_count"] == 2
    assert stats["total_consumption_count"] == 4
    assert stats["average_rating"] == 3.75

@pytest.mark.asyncio
async def test_get_most_consumed_drinks(user_drinks_service, mock_db):
    """Test getting most consumed drinks."""
    # Mock drink
    mock_drink = MagicMock(spec=Drink)
    mock_drink.drink_id = 1
    mock_drink.name = "Coffee"
    mock_drink.category = "Coffee"

    # Mock interaction
    mock_interaction = MagicMock(spec=UserDrinkInteraction)
    mock_interaction.user_id = 1
    mock_interaction.drink_id = 1
    mock_interaction.times_consumed = 5
    mock_interaction.last_consumed_at = datetime.now()
    mock_interaction.drink = mock_drink

    mock_db.execute.return_value.scalars.return_value = [mock_interaction]

    drinks = await user_drinks_service.get_most_consumed_drinks(1, limit=5)

    assert len(drinks) == 1
    assert drinks[0]["name"] == "Coffee"
    assert drinks[0]["times_consumed"] == 5

@pytest.mark.asyncio
async def test_get_user_preferred_categories(user_drinks_service, mock_db):
    """Test getting user preferred categories."""
    # Mock drink
    mock_drink1 = MagicMock(spec=Drink)
    mock_drink1.drink_id = 1
    mock_drink1.name = "Coffee"
    mock_drink1.category = "Coffee"

    mock_drink2 = MagicMock(spec=Drink)
    mock_drink2.drink_id = 2
    mock_drink2.name = "Tea"
    mock_drink2.category = "Tea"

    # Mock interactions
    mock_interaction1 = MagicMock(spec=UserDrinkInteraction)
    mock_interaction1.user_id = 1
    mock_interaction1.drink_id = 1
    mock_interaction1.is_favorite = True
    mock_interaction1.rating = 4.5
    mock_interaction1.times_consumed = 3
    mock_interaction1.is_not_for_me = False
    mock_interaction1.drink = mock_drink1

    mock_interaction2 = MagicMock(spec=UserDrinkInteraction)
    mock_interaction2.user_id = 1
    mock_interaction2.drink_id = 2
    mock_interaction2.is_favorite = False
    mock_interaction2.rating = 3.0
    mock_interaction2.times_consumed = 1
    mock_interaction2.is_not_for_me = False
    mock_interaction2.drink = mock_drink2

    mock_db.execute.return_value.scalars.return_value = [mock_interaction1, mock_interaction2]

    categories = await user_drinks_service.get_user_preferred_categories(1)

    assert len(categories) == 2
    assert any(cat["category"] == "Coffee" for cat in categories)
    assert any(cat["category"] == "Tea" for cat in categories)

    # Coffee should have higher score
    coffee_score = next(cat["score"] for cat in categories if cat["category"] == "Coffee")
    tea_score = next(cat["score"] for cat in categories if cat["category"] == "Tea")
    assert coffee_score > tea_score
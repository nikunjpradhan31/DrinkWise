"""
Unit tests for PreferenceService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from services.preference_service import PreferenceService
from models import UserPreference, Users
from pydantic_models import UserPreference as UserPreferenceModel, UserPreferenceUpdate

@pytest.fixture
def preference_service(mock_db):
    """Create a PreferenceService instance with mock database session."""
    return PreferenceService(mock_db)

@pytest.mark.asyncio
async def test_get_user_preferences(preference_service, mock_db):
    """Test getting user preferences."""

    # Mock the database result object
    mock_preferences = MagicMock(spec=UserPreference)
    mock_preferences.user_id = 1
    mock_preferences.sweetness_preference = 5
    mock_preferences.bitterness_preference = 5
    mock_preferences.caffeine_limit = 400
    mock_preferences.calorie_limit = 2000
    mock_preferences.preferred_price_tier = "$$"
    mock_preferences.created_at = datetime.now()
    mock_preferences.updated_at = datetime.now()

    # Mock the DB execute
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_preferences
    mock_db.execute.return_value = mock_result

    preferences = await preference_service.get_user_preferences(1)

    assert preferences is not None
    assert preferences.user_id == 1
    assert preferences.sweetness_preference == 5
    assert preferences.caffeine_limit == 400


@pytest.mark.asyncio
async def test_create_user_preferences(preference_service, mock_db):
    """Test creating user preferences."""
    # No existing preferences
    from datetime import datetime
    now = datetime.now()

    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Mock new preferences
    mock_new_preferences = MagicMock(spec=UserPreference)
    mock_new_preferences.user_id = 1
    mock_new_preferences.sweetness_preference = 5
    mock_new_preferences.bitterness_preference = 5
    mock_new_preferences.caffeine_limit = 400
    mock_new_preferences.calorie_limit = 2000
    mock_new_preferences.preferred_price_tier = "$$"
    mock_new_preferences.created_at = now
    mock_new_preferences.updated_at = now
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_new_preferences
    mock_result.refresh.return_value = mock_new_preferences

    update_data = UserPreferenceUpdate(
        sweetness_preference=5,
        bitterness_preference=5,
        caffeine_limit=400,
        calorie_limit=2000,
        preferred_price_tier="$$"
    )

    preferences = await preference_service.create_user_preferences(1, update_data)

    assert preferences is not None
    assert preferences.sweetness_preference == 5
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_update_user_preferences(preference_service, mock_db):
    """Test updating user preferences."""
    # Mock existing preferences
    mock_existing_preferences = MagicMock(spec=UserPreference)
    mock_existing_preferences.user_id = 1
    mock_existing_preferences.sweetness_preference = 3
    mock_existing_preferences.bitterness_preference = 3
    mock_existing_preferences.caffeine_limit = 200
    mock_existing_preferences.calorie_limit = 1500
    mock_existing_preferences.preferred_price_tier = "$"
    mock_existing_preferences.created_at = datetime.now()
    mock_existing_preferences.updated_at = datetime.now()

    # Mock updated preferences
    mock_updated_preferences = MagicMock(spec=UserPreference)
    mock_updated_preferences.user_id = 1
    mock_updated_preferences.sweetness_preference = 5
    mock_updated_preferences.bitterness_preference = 5
    mock_updated_preferences.caffeine_limit = 400
    mock_updated_preferences.calorie_limit = 2000
    mock_updated_preferences.preferred_price_tier = "$$"
    mock_updated_preferences.created_at = datetime.now()
    mock_updated_preferences.updated_at = datetime.now()

    # Mock results
    mock_get_existing_result = MagicMock()
    mock_get_existing_result.scalar_one_or_none.return_value = mock_existing_preferences

    mock_update_result = MagicMock()
    mock_update_result.rowcount = 1

    mock_get_updated_result = MagicMock()
    mock_get_updated_result.scalar_one_or_none.return_value = mock_updated_preferences

    mock_db.execute.side_effect = [
        mock_get_existing_result,  # get_user_preferences
        mock_update_result,  # update
        mock_get_updated_result  # get_user_preferences again
    ]

    update_data = UserPreferenceUpdate(
        sweetness_preference=5,
        caffeine_limit=400
    )

    preferences = await preference_service.update_user_preferences(1, update_data)

    assert preferences is not None
    assert preferences.sweetness_preference == 5
    assert preferences.caffeine_limit == 400
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_delete_user_preferences(preference_service, mock_db):
    """Test deleting user preferences."""
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute.return_value = mock_result

    success = await preference_service.delete_user_preferences(1)

    assert success is True
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_ensure_user_preferences_new(preference_service, mock_db):
    """Test ensuring user preferences when none exist."""
    # No existing preferences
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Mock new preferences
    mock_new_preferences = MagicMock(spec=UserPreference)
    mock_new_preferences.user_id = 1
    mock_new_preferences.sweetness_preference = 5
    mock_new_preferences.bitterness_preference = 5
    mock_new_preferences.caffeine_limit = 400
    mock_new_preferences.calorie_limit = 2000
    mock_new_preferences.preferred_price_tier = "$$"
    mock_new_preferences.created_at = datetime.now()
    mock_new_preferences.updated_at = datetime.now()

    mock_db.refresh.return_value = mock_new_preferences

    preferences = await preference_service.ensure_user_preferences(1)

    assert preferences is not None
    assert preferences.sweetness_preference == 5

@pytest.mark.asyncio
async def test_ensure_user_preferences_existing(preference_service, mock_db):
    """Test ensuring user preferences when they already exist."""
    # Mock existing preferences
    mock_existing_preferences = MagicMock(spec=UserPreference)
    mock_existing_preferences.user_id = 1
    mock_existing_preferences.sweetness_preference = 7
    mock_existing_preferences.bitterness_preference = 3
    mock_existing_preferences.caffeine_limit = 300
    mock_existing_preferences.calorie_limit = 1800
    mock_existing_preferences.preferred_price_tier = "$$$"
    mock_existing_preferences.created_at = datetime.now()
    mock_existing_preferences.updated_at = datetime.now()

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_existing_preferences

    preferences = await preference_service.ensure_user_preferences(1)

    assert preferences is not None
    assert preferences.sweetness_preference == 7
    assert preferences.caffeine_limit == 300

@pytest.mark.asyncio
async def test_get_preferences_for_filtering(preference_service, mock_db):
    """Test getting preferences for filtering."""
    # Mock preferences
    mock_preferences = MagicMock(spec=UserPreference)
    mock_preferences.user_id = 1
    mock_preferences.sweetness_preference = 5
    mock_preferences.caffeine_limit = 400
    mock_preferences.calorie_limit = 2000
    mock_preferences.preferred_price_tier = "$$"

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_preferences

    filters = await preference_service.get_preferences_for_filtering(1)

    assert filters["max_sweetness"] == 5
    assert filters["max_caffeine"] == 400
    assert filters["max_calories"] == 2000
    assert filters["preferred_price_tier"] == "$$"

@pytest.mark.asyncio
async def test_get_preference_statistics(preference_service, mock_db):
    """Test getting preference statistics."""
    # Mock preferences
    mock_preferences = MagicMock(spec=UserPreference)
    mock_preferences.user_id = 1
    mock_preferences.sweetness_preference = 7
    mock_preferences.bitterness_preference = 3
    mock_preferences.caffeine_limit = 300
    mock_preferences.calorie_limit = 1800
    mock_preferences.preferred_price_tier = "$$$"
    mock_preferences.created_at = datetime.now()
    mock_preferences.updated_at = datetime.now()

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_preferences

    stats = await preference_service.get_preference_statistics(1)

    assert stats["has_preferences"] is True
    assert stats["sweetness"]["level"] == 7
    assert stats["caffeine"]["limit"] == 300
    assert "description" in stats["sweetness"]
    assert "description" in stats["caffeine"]

@pytest.mark.asyncio
async def test_get_compatible_drinks(preference_service, mock_db):
    """Test getting compatible drinks."""
    # Mock preferences
    mock_preferences = MagicMock(spec=UserPreference)
    mock_preferences.user_id = 1
    mock_preferences.sweetness_preference = 5
    mock_preferences.caffeine_limit = 400
    mock_preferences.calorie_limit = 2000
    mock_preferences.preferred_price_tier = "$$"

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_preferences

    drink_candidates = [
        {"name": "Coffee", "sweetness_level": 3, "caffeine_content": 100, "calorie_content": 5, "price_tier": "$$"},
        {"name": "Soda", "sweetness_level": 8, "caffeine_content": 50, "calorie_content": 150, "price_tier": "$"},
        {"name": "Espresso", "sweetness_level": 2, "caffeine_content": 200, "calorie_content": 3, "price_tier": "$$"}
    ]

    compatible_drinks = await preference_service.get_compatible_drinks(1, drink_candidates)

    assert len(compatible_drinks) == 3
    assert all("compatibility_score" in drink for drink in compatible_drinks)

@pytest.mark.asyncio
async def test_export_user_preferences(preference_service, mock_db):
    """Test exporting user preferences."""
    # Mock preferences
    mock_preferences = MagicMock(spec=UserPreference)
    mock_preferences.user_id = 1
    mock_preferences.sweetness_preference = 5
    mock_preferences.bitterness_preference = 5
    mock_preferences.caffeine_limit = 400
    mock_preferences.calorie_limit = 2000
    mock_preferences.preferred_price_tier = "$$"
    mock_preferences.created_at = datetime.now()
    mock_preferences.updated_at = datetime.now()

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_preferences

    export_data = await preference_service.export_user_preferences(1)

    assert export_data is not None
    assert "export_version" in export_data
    assert "preferences" in export_data
    assert export_data["preferences"]["sweetness_preference"] == 5

@pytest.mark.asyncio
async def test_import_user_preferences(preference_service, mock_db):
    """Test importing user preferences."""
    # Mock existing preferences
    mock_existing_preferences = MagicMock(spec=UserPreference)
    mock_existing_preferences.user_id = 1
    mock_existing_preferences.sweetness_preference = 3
    mock_existing_preferences.bitterness_preference = 3
    mock_existing_preferences.caffeine_limit = 200
    mock_existing_preferences.calorie_limit = 1500
    mock_existing_preferences.preferred_price_tier = "$"
    mock_existing_preferences.created_at = datetime.now()
    mock_existing_preferences.updated_at = datetime.now()

    # Mock updated preferences
    mock_updated_preferences = MagicMock(spec=UserPreference)
    mock_updated_preferences.user_id = 1
    mock_updated_preferences.sweetness_preference = 7
    mock_updated_preferences.bitterness_preference = 7
    mock_updated_preferences.caffeine_limit = 500
    mock_updated_preferences.calorie_limit = 2500
    mock_updated_preferences.preferred_price_tier = "$$$"
    mock_updated_preferences.created_at = datetime.now()
    mock_updated_preferences.updated_at = datetime.now()

    # Mock results
    mock_get_existing_result = MagicMock()
    mock_get_existing_result.scalar_one_or_none.return_value = mock_existing_preferences

    mock_update_result = MagicMock()
    mock_update_result.rowcount = 1

    mock_get_updated_result = MagicMock()
    mock_get_updated_result.scalar_one_or_none.return_value = mock_updated_preferences

    mock_db.execute.side_effect = [
        mock_get_existing_result,  # get_user_preferences
        mock_update_result,  # update
        mock_get_updated_result  # get_user_preferences again
    ]

    import_data = {
        "export_version": "1.0",
        "preferences": {
            "sweetness_preference": 7,
            "bitterness_preference": 7,
            "caffeine_limit": 500,
            "calorie_limit": 2500,
            "preferred_price_tier": "$$$"
        }
    }

    preferences = await preference_service.import_user_preferences(1, import_data)

    assert preferences is not None
    assert preferences.sweetness_preference == 7
    assert preferences.caffeine_limit == 500

def test_analyze_sweetness_preference(preference_service):
    """Test sweetness preference analysis."""
    assert "Very low" in preference_service._analyze_sweetness_preference(2)
    assert "Balanced" in preference_service._analyze_sweetness_preference(5)
    assert "Very high" in preference_service._analyze_sweetness_preference(10)

def test_analyze_bitterness_preference(preference_service):
    """Test bitterness preference analysis."""
    assert "Low" in preference_service._analyze_bitterness_preference(2)
    assert "Balanced" in preference_service._analyze_bitterness_preference(5)
    assert "Very high" in preference_service._analyze_bitterness_preference(10)

def test_analyze_caffeine_tolerance(preference_service):
    """Test caffeine tolerance analysis."""
    assert "Low" in preference_service._analyze_caffeine_tolerance(100)
    assert "Normal" in preference_service._analyze_caffeine_tolerance(400)
    assert "Very high" in preference_service._analyze_caffeine_tolerance(800)

def test_analyze_calorie_consciousness(preference_service):
    """Test calorie consciousness analysis."""
    assert "Very health" in preference_service._analyze_calorie_consciousness(1200)
    assert "Balanced" in preference_service._analyze_calorie_consciousness(2000)
    assert "Liberal" in preference_service._analyze_calorie_consciousness(3000)

def test_describe_price_tier(preference_service):
    """Test price tier description."""
    assert "Budget" in preference_service._describe_price_tier("$")
    assert "Moderate" in preference_service._describe_price_tier("$$")
    assert "Premium" in preference_service._describe_price_tier("$$$")

def test_calculate_preference_strength(preference_service):
    """Test preference strength calculation."""
    # High strength (all customized)
    preferences = UserPreferenceModel(
        user_id=1,
        sweetness_preference=7,
        bitterness_preference=3,
        caffeine_limit=500,
        calorie_limit=2500,
        preferred_price_tier="$$$",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    strength = preference_service._calculate_preference_strength(preferences)
    assert "High" in strength

    # Low strength (using defaults)
    preferences = UserPreferenceModel(
        user_id=1,
        sweetness_preference=5,
        bitterness_preference=5,
        caffeine_limit=400,
        calorie_limit=2000,
        preferred_price_tier="$$",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    strength = preference_service._calculate_preference_strength(preferences)
    assert "Low" in strength
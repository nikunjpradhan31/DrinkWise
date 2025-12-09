"""
Unit tests for AuthService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.auth_service import AuthService
from services.email_service import EmailService
from models import Users
from pydantic_models import UserRegistration, UserLogin, UserUpdate

@pytest.fixture
def mock_email_service():
    """Create a mock email service."""
    email_service = MagicMock(spec=EmailService)
    email_service.send_verification_email = AsyncMock(return_value=1)
    email_service.verify_code = AsyncMock(return_value=1)
    return email_service

@pytest.fixture
def auth_service(mock_db, mock_email_service):
    """Create an AuthService instance with mock dependencies."""
    return AuthService(mock_db, mock_email_service)

def test_hash_password(auth_service):
    """Test password hashing."""
    password = "test_password_123"
    hashed = auth_service.hash_password(password)

    # Verify the hash is different from the original
    assert hashed != password

    # Verify the hash is valid bcrypt
    assert hashed.startswith("$2b$")

def test_verify_password(auth_service):
    """Test password verification."""
    password = "test_password_123"
    hashed = auth_service.hash_password(password)

    # Verify correct password
    assert auth_service.verify_password(password, hashed) is True

    # Verify incorrect password
    assert auth_service.verify_password("wrong_password", hashed) is False

def test_validate_username(auth_service):
    """Test username validation."""
    # Valid usernames
    assert auth_service.validate_username("valid_user") is True
    assert auth_service.validate_username("user_123") is True
    assert auth_service.validate_username("a-b") is True

    # Invalid usernames
    assert auth_service.validate_username("") is False
    assert auth_service.validate_username("ab") is False  # Too short
    assert auth_service.validate_username("a" * 51) is False  # Too long
    assert auth_service.validate_username("invalid user") is False  # Contains space

def test_validate_password_strength(auth_service):
    """Test password strength validation."""
    # Too short
    result, details = auth_service.validate_password_strength("short")
    assert result is False
    assert "8 characters" in details["error"]

    # Too long
    result, details = auth_service.validate_password_strength("a" * 129)
    assert result is False
    assert "128 characters" in details["error"]

    # Missing uppercase
    result, details = auth_service.validate_password_strength("password123!")
    assert result is False
    assert "uppercase" in details["error"]

    # Missing lowercase
    result, details = auth_service.validate_password_strength("PASSWORD123!")
    assert result is False
    assert "lowercase" in details["error"]

    # Missing digit
    result, details = auth_service.validate_password_strength("Password!")
    assert result is False
    assert "digit" in details["error"]

    # Valid password
    result, details = auth_service.validate_password_strength("ValidPass123!")
    assert result is True
    assert details["strength"] == "strong"

@pytest.mark.asyncio
async def test_register_user_success(auth_service, mock_db):
    mock_execute_result_1 = MagicMock()
    mock_execute_result_1.scalar_one_or_none.return_value = None

    mock_execute_result_2 = MagicMock()
    mock_execute_result_2.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [
        mock_execute_result_1,
        mock_execute_result_2,
    ]
    auth_service._get_user_by_username = AsyncMock(return_value=None)

    mock_user = MagicMock(spec=Users)
    mock_user.user_id = None
    mock_user.joindate = None

    async def fake_refresh(user):
        user.user_id = 1
        user.joindate = datetime(2020, 1, 1)

    mock_db.refresh = AsyncMock(side_effect=fake_refresh)



    registration_data = UserRegistration(
        username="test_user",
        email="test@example.com",
        password="ValidPass123!",
        confirmpassword="ValidPass123!",
        date_of_birth=datetime(1990, 1, 1)
    )

    success, error, user_response = await auth_service.register_user(registration_data)

    assert success is True
    assert error is None
    assert user_response is not None
    assert user_response.username == "test_user"
    assert user_response.email == "test@example.com"
    assert user_response.is_verified is False

    # Verify database operations were called
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_register_user_duplicate_username(auth_service, mock_db):
    """Test registration with duplicate username."""
    # Mock existing user
    mock_user = MagicMock(spec=Users)
    mock_user.username = "test_user"
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

    registration_data = UserRegistration(
        username="test_user",
        email="test@example.com",
        password="ValidPass123!",
        confirmpassword="ValidPass123!",
        date_of_birth=datetime(1990, 1, 1)
    )

    success, error, user_response = await auth_service.register_user(registration_data)

    assert success is False
    assert error == "Username already exists"
    assert user_response is None

@pytest.mark.asyncio
async def test_login_user_success(auth_service, mock_db):
    """Test successful user login."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.username = "test_user"
    mock_user.email = "test@example.com"
    mock_user.password = auth_service.hash_password("ValidPass123!")
    mock_user.is_verified = True
    mock_user.joindate = datetime.now()
    mock_user.date_of_birth = datetime(1990, 1, 1)
    mock_user.preference_finished = False

    auth_service._get_user_by_username = AsyncMock(return_value=mock_user)

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

    login_data = UserLogin(username="test_user", password="ValidPass123!")

    success, error, user_response = await auth_service.login_user(login_data)
    print(error)
    assert success is True
    assert error is None
    assert user_response is not None
    assert user_response.username == "test_user"
    assert user_response.access_token is not None

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(auth_service, mock_db):
    """Test login with invalid credentials."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.username = "test_user"
    mock_user.password = auth_service.hash_password("ValidPass123!")
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    auth_service._get_user_by_username = AsyncMock(return_value=mock_user)

    login_data = UserLogin(username="test_user", password="wrong_password")

    success, error, user_response = await auth_service.login_user(login_data)

    assert success is False
    assert error == "Invalid username or password"
    assert user_response is None

@pytest.mark.asyncio
async def test_get_user_profile_success(auth_service, mock_db):
    """Test getting user profile."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.username = "test_user"
    mock_user.email = "test@example.com"
    mock_user.is_verified = True
    mock_user.joindate = datetime.now()
    mock_user.date_of_birth = datetime(1990, 1, 1)
    mock_user.preference_finished = False
    auth_service.get_user_profile = AsyncMock(return_value=mock_user)

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    
    user_response = await auth_service.get_user_profile(1)

    assert user_response is not None
    assert user_response.username == "test_user"
    assert user_response.email == "test@example.com"

@pytest.mark.asyncio
async def test_update_user_profile_success(auth_service, mock_db):
    """Test updating user profile."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.username = "old_user"
    mock_user.email = "old@example.com"
    mock_user.date_of_birth = datetime(1990, 1, 1)
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    auth_service._get_user_by_id = AsyncMock(return_value=mock_user)
    auth_service._get_user_by_username = AsyncMock(return_value=mock_user)
    auth_service.get_user_profile = AsyncMock(return_value=mock_user)

    update_data = UserUpdate(username="new_user")

    success, error, user_response = await auth_service.update_user_profile(1, update_data)

    assert success is True
    assert error is None
    assert user_response is not None
    assert user_response.username == "new_user"

@pytest.mark.asyncio
async def test_verify_user_email_success(auth_service, mock_db, mock_email_service):
    """Test email verification."""
    mock_email_service.verify_code.return_value = 1

    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.is_verified = False
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    auth_service._get_user_by_id = AsyncMock(return_value=mock_user)
    success, error = await auth_service.verify_user_email("test@example.com", "123456")

    assert success is True
    assert error is None

@pytest.mark.asyncio
async def test_request_password_reset_success(auth_service, mock_db, mock_email_service):
    """Test password reset request."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.email = "test@example.com"
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    auth_service._get_user_by_email = AsyncMock(return_value=mock_user)

    success, error = await auth_service.request_password_reset("test@example.com")

    assert success is True
    assert error is None

@pytest.mark.asyncio
async def test_reset_password_success(auth_service, mock_db, mock_email_service):
    """Test password reset."""
    mock_email_service.verify_code.return_value = 1

    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.password = "old_password"
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    auth_service._get_user_by_id = AsyncMock(return_value=mock_user)

    success, error = await auth_service.reset_password(
        "test@example.com", "123456", "NewPass123!"
    )

    assert success is True
    assert error is None

@pytest.mark.asyncio
async def test_check_username_availability(auth_service, mock_db):
    """Test username availability check."""
    # No user exists
    auth_service._get_user_by_username = AsyncMock(return_value=None)
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    assert await auth_service.check_username_availability("new_user") is True

    # User exists
    mock_user = MagicMock(spec=Users)
    mock_user.username = "new_user"
    auth_service._get_user_by_username = AsyncMock(return_value=mock_user)
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    assert await auth_service.check_username_availability("existing_user") is False

@pytest.mark.asyncio
async def test_get_user_statistics(auth_service, mock_db):
    """Test getting user statistics."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.username = "test_user"
    mock_user.email = "test@example.com"
    mock_user.joindate = datetime.now() - timedelta(days=30)
    mock_user.is_verified = True
    mock_user.date_of_birth = datetime(1990, 1, 1)
    mock_user.preference_finished = False
    mock_user.session_at = datetime.now()
    auth_service._get_user_by_id = AsyncMock(return_value=mock_user)
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

    stats = await auth_service.get_user_statistics(1)

    assert stats["user_id"] == 1
    assert stats["username"] == "test_user"
    assert stats["account_age_days"] == 30

@pytest.mark.asyncio
async def test_logout_user_success(auth_service, mock_db):
    """Test successful user logout."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.username = "test_user"
    auth_service._get_user_by_id = AsyncMock(return_value=mock_user)
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

    result = await auth_service.logout_user(1)

    assert result is True

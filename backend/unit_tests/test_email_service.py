"""
Unit tests for EmailService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.email_service import EmailService
from models import Verification, Users

@pytest.fixture
def email_service(mock_db):
    """Create an EmailService instance with mock database session."""
    return EmailService(mock_db)

def test_generate_verification_code(email_service):
    """Test verification code generation."""
    code = email_service.generate_verification_code()

    # Should be a 6-digit string
    assert isinstance(code, str)
    assert len(code) == 6
    assert code.isdigit()

@pytest.mark.asyncio
async def test_send_verification_email(email_service, mock_db):
    """Test sending verification email."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.email = "test@example.com"

    # Mock verification
    mock_verification = MagicMock(spec=Verification)
    mock_verification.id = 1
    mock_db.refresh.return_value = mock_verification

    with patch('services.email_service.FastMail') as mock_fastmail:
        mock_fastmail_instance = MagicMock()
        mock_fastmail.return_value = mock_fastmail_instance
        mock_fastmail_instance.send_message = AsyncMock()

        verification_id = await email_service.send_verification_email(
            "test@example.com", 1, "email_verification"
        )

        assert verification_id == 1
        assert mock_db.add.called
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_verify_code_success(email_service, mock_db):
    """Test successful code verification."""
    # Mock verification
    mock_verification = MagicMock(spec=Verification)
    mock_verification.id = 1
    mock_verification.user_id = 1
    mock_verification.email = "test@example.com"
    mock_verification.code = "123456"
    mock_verification.verification_type = "email_verification"
    mock_verification.is_used = False
    mock_verification.expires_at = datetime.now() + timedelta(minutes=10)

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_verification

    user_id = await email_service.verify_code("test@example.com", "123456", "email_verification")

    assert user_id == 1
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_verify_code_expired(email_service, mock_db):
    """Test verification with expired code."""
    # Mock expired verification
    mock_verification = MagicMock(spec=Verification)
    mock_verification.expires_at = datetime.now() - timedelta(minutes=1)

    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    user_id = await email_service.verify_code("test@example.com", "123456", "email_verification")

    assert user_id is None

@pytest.mark.asyncio
async def test_resend_verification(email_service, mock_db):
    """Test resending verification email."""
    # Mock user
    mock_user = MagicMock(spec=Users)
    mock_user.user_id = 1
    mock_user.email = "test@example.com"

    # Mock verification
    mock_verification = MagicMock(spec=Verification)
    mock_verification.id = 1
    mock_db.refresh.return_value = mock_verification

    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=mock_user),  # get user
        None,  # delete old verifications
        mock_verification  # refresh new verification
    ]

    with patch('services.email_service.FastMail') as mock_fastmail:
        mock_fastmail_instance = MagicMock()
        mock_fastmail.return_value = mock_fastmail_instance
        mock_fastmail_instance.send_message = AsyncMock()

        success = await email_service.resend_verification("test@example.com", "email_verification")

        assert success is True

@pytest.mark.asyncio
async def test_cleanup_expired_verifications(email_service, mock_db):
    """Test cleaning up expired verifications."""
    await email_service.cleanup_expired_verifications()

    assert mock_db.execute.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_is_verification_pending(email_service, mock_db):
    """Test checking if verification is pending."""
    # Verification exists
    mock_verification = MagicMock(spec=Verification)
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_verification

    pending = await email_service.is_verification_pending("test@example.com", "email_verification")
    assert pending is True

    # No verification
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    pending = await email_service.is_verification_pending("test@example.com", "email_verification")
    assert pending is False

@pytest.mark.asyncio
async def test_get_verification_attempts(email_service, mock_db):
    """Test getting verification attempts."""
    # Mock verifications
    mock_verification1 = MagicMock(spec=Verification)
    mock_verification2 = MagicMock(spec=Verification)

    mock_db.execute.return_value.scalars.return_value = [mock_verification1, mock_verification2]

    attempts = await email_service.get_verification_attempts("test@example.com", "email_verification")

    assert attempts == 2

def test_create_verification_email_html(email_service):
    """Test creating verification email HTML."""
    html = email_service._create_verification_email_html("test@example.com", "123456")

    assert "123456" in html
    assert "DrinkWise" in html
    assert "Verify Your Email" in html

def test_create_password_reset_email_html(email_service):
    """Test creating password reset email HTML."""
    html = email_service._create_password_reset_email_html("test@example.com", "123456")

    assert "123456" in html
    assert "DrinkWise" in html
    assert "Password Reset" in html

def test_create_login_verification_email_html(email_service):
    """Test creating login verification email HTML."""
    html = email_service._create_login_verification_email_html("test@example.com", "123456")

    assert "123456" in html
    assert "DrinkWise" in html
    assert "Login Verification" in html

def test_create_generic_verification_email_html(email_service):
    """Test creating generic verification email HTML."""
    html = email_service._create_generic_verification_email_html("test@example.com", "123456")

    assert "123456" in html
    assert "DrinkWise" in html
    assert "Verification Code" in html
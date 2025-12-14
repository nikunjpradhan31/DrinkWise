"""
Unit tests for BaseService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from services.base import BaseService


class TestBaseService(BaseService):
    """Concrete implementation of BaseService for testing."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)


@pytest.fixture
def base_service(mock_db):
    """Create a BaseService instance with mock database session."""
    return TestBaseService(mock_db)


@pytest.mark.asyncio
async def test_execute_with_rollback_success(base_service, mock_db):
    """Test execute_with_rollback with successful operation."""
    async def mock_operation():
        return "success"

    result = await base_service.execute_with_rollback(mock_operation)

    assert result == "success"
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_execute_with_rollback_failure(base_service, mock_db):
    """Test execute_with_rollback with failed operation."""
    async def mock_operation():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await base_service.execute_with_rollback(mock_operation)

    assert mock_db.rollback.called


@pytest.mark.asyncio
async def test_execute_without_commit(base_service, mock_db):
    """Test execute_without_commit."""
    async def mock_operation():
        return "success"

    result = await base_service.execute_without_commit(mock_operation)

    assert result == "success"
    assert not mock_db.commit.called


def test_handle_not_found(base_service):
    """Test handle_not_found raises HTTPException."""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        base_service.handle_not_found("User", 1)

    assert exc_info.value.status_code == 404
    assert "User with id 1 not found" in exc_info.value.detail


def test_handle_validation_error(base_service):
    """Test handle_validation_error raises HTTPException."""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        base_service.handle_validation_error("email", "invalid@email")

    assert exc_info.value.status_code == 400
    assert "Invalid value 'invalid@email' for field 'email'" in exc_info.value.detail


def test_handle_conflict_error(base_service):
    """Test handle_conflict_error raises HTTPException."""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        base_service.handle_conflict_error("User", "email", "test@example.com")

    assert exc_info.value.status_code == 409
    assert "User with email 'test@example.com' already exists" in exc_info.value.detail


def test_log_operation(base_service):
    """Test log_operation calls logger."""
    with patch('services.base.logger') as mock_logger:
        base_service.log_operation("test_operation", {"key": "value"})

        mock_logger.info.assert_called_once_with(
            "Service operation 'test_operation' executed with details: {'key': 'value'}"
        )


def test_log_error(base_service):
    """Test log_error calls logger."""
    with patch('services.base.logger') as mock_logger:
        error = ValueError("Test error")
        base_service.log_error("test_operation", error, {"key": "value"})

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "Service operation 'test_operation' failed: Test error" in call_args[0][0]
        assert call_args[1]["extra"]["details"] == {"key": "value"}


@pytest.mark.asyncio
async def test_health_check_healthy(base_service, mock_db):
    """Test health_check when database is healthy."""
    mock_db.execute.return_value = MagicMock()

    result = await base_service.health_check()

    assert result["status"] == "healthy"
    assert result["service"] == "TestBaseService"
    assert result["database"] == "connected"


@pytest.mark.asyncio
async def test_health_check_unhealthy(base_service, mock_db):
    """Test health_check when database is unhealthy."""
    mock_db.execute.side_effect = Exception("Connection failed")

    result = await base_service.health_check()

    assert result["status"] == "unhealthy"
    assert result["service"] == "TestBaseService"
    assert result["database"] == "disconnected"
    assert "Connection failed" in result["error"]
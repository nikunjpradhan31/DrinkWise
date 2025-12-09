"""
Common test fixtures and configurations for DrinkWise unit tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    return db

@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    import logging
    logger = logging.getLogger(__name__)
    return logger
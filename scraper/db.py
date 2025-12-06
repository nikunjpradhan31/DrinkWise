"""Database engine and session factory."""
import os
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_DB_URL = "postgresql://user:password@localhost:5432/drinkwise"

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Resolve the database URL from env with a safe default."""
    return os.getenv("DATABASE_URL", DEFAULT_DB_URL)


def get_engine(echo: bool = False):
    """Create a SQLAlchemy engine."""
    db_url = get_database_url()
    logger.info("Connecting to database at %s", db_url)
    return create_engine(db_url, echo=echo, pool_pre_ping=True)


# Lazy engine/session creation to avoid side effects on import
_engine = None
SessionLocal = None


def _ensure_session():
    global _engine, SessionLocal
    if _engine is None:
        _engine = get_engine()
        SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


@contextmanager
def get_session():
    """Provide a transactional session scope."""
    _ensure_session()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

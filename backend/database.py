from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")
async_engine = create_async_engine(DATABASE_URL, echo=False)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
SyncSessionLocal = sessionmaker(sync_engine, autocommit=False, autoflush=False)

Base = declarative_base()


import logging
logging.basicConfig(level=logging.INFO)

async def get_db_async():
    """Asynchronous DB session dependency"""
    async with AsyncSessionLocal() as db:
        yield db

def get_db():
    """Synchronous DB session dependency"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def initialize_database():    
    # Initialize with async engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("✅ Database initialized with async engine.")
    # Initialize with sync engine
    with sync_engine.begin() as conn:
        Base.metadata.create_all(conn)
    logging.info("✅ Database initialized with sync engine.")
async def update_expired_keys():
    """Update expired keys every 60 seconds."""
    while True:
        async with AsyncSessionLocal() as db:
            await db.execute(text(
                """
                UPDATE Users 
                SET access_key = NULL, session_at = NULL 
                WHERE session_at < NOW() - INTERVAL '12 hours'
                """
            ))
            await db.commit()
        await asyncio.sleep(10)

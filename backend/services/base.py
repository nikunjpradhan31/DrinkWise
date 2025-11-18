from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any, TypeVar, Generic
import logging

# Type variable for model
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')

class BaseService(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base service class providing common CRUD operations
    
    Attributes:
        model: SQLAlchemy model class
        db: Database session
    """
    
    def __init__(self, model: type, db: AsyncSession):
        self.model = model
        self.db = db
        self.logger = logging.getLogger(f"{model.__name__}_service")
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get a record by ID
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        try:
            result = await self.db.execute(select(self.model).where(self.model.__table__.primary_key.columns.values()[0] == id))
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by ID {id}: {str(e)}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """
        Get all records with pagination
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        try:
            result = await self.db.execute(
                select(self.model).offset(offset).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            self.logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            return []
    
    async def create(self, obj_data: CreateSchemaType) -> Optional[ModelType]:
        """
        Create a new record
        
        Args:
            obj_data: Data to create the record with
            
        Returns:
            Created model instance or None if failed
        """
        try:
            db_obj = self.model(**obj_data.dict())
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            self.logger.info(f"Created {self.model.__name__} with ID {getattr(db_obj, self.model.__table__.primary_key.columns.values()[0].name)}")
            return db_obj
        except Exception as e:
            self.logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            return None
    
    async def update(self, id: int, obj_data: UpdateSchemaType) -> Optional[ModelType]:
        """
        Update an existing record
        
        Args:
            id: Record ID to update
            obj_data: Data to update with
            
        Returns:
            Updated model instance or None if failed
        """
        try:
            # Get the current record
            current_obj = await self.get_by_id(id)
            if not current_obj:
                return None
            
            # Update fields
            update_data = obj_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(current_obj, field, value)
            
            await self.db.commit()
            await self.db.refresh(current_obj)
            self.logger.info(f"Updated {self.model.__name__} with ID {id}")
            return current_obj
        except Exception as e:
            self.logger.error(f"Error updating {self.model.__name__} with ID {id}: {str(e)}")
            await self.db.rollback()
            return None
    
    async def delete(self, id: int) -> bool:
        """
        Delete a record
        
        Args:
            id: Record ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            obj = await self.get_by_id(id)
            if not obj:
                return False
            
            await self.db.delete(obj)
            await self.db.commit()
            self.logger.info(f"Deleted {self.model.__name__} with ID {id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting {self.model.__name__} with ID {id}: {str(e)}")
            await self.db.rollback()
            return False
    
    async def count(self) -> int:
        """
        Get total count of records
        
        Returns:
            Total count
        """
        try:
            result = await self.db.execute(select(self.model))
            return len(result.scalars().all())
        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            return 0
    
    async def bulk_create(self, obj_data_list: List[CreateSchemaType]) -> List[ModelType]:
        """
        Create multiple records in bulk
        
        Args:
            obj_data_list: List of data to create records with
            
        Returns:
            List of created model instances
        """
        try:
            db_objects = []
            for obj_data in obj_data_list:
                db_obj = self.model(**obj_data.dict())
                db_objects.append(db_obj)
            
            self.db.add_all(db_objects)
            await self.db.commit()
            
            for obj in db_objects:
                await self.db.refresh(obj)
            
            self.logger.info(f"Created {len(db_objects)} {self.model.__name__} records")
            return db_objects
        except Exception as e:
            self.logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            return []

class ServiceError(Exception):
    """Custom exception for service layer errors"""
    pass

class ValidationError(ServiceError):
    """Custom exception for validation errors"""
    pass

class NotFoundError(ServiceError):
    """Custom exception for not found errors"""
    pass

class AuthenticationError(ServiceError):
    """Custom exception for authentication errors"""
    pass

# Utility functions for service layer
def validate_age(age: Optional[int]) -> bool:
    """Validate age is reasonable"""
    return age is None or (0 <= age <= 150)

def validate_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email

def validate_price_tier(price_tier: str) -> bool:
    """Validate price tier format"""
    return price_tier in ["$", "$$", "$$$"]

def validate_sweetness_level(level: int) -> bool:
    """Validate sweetness level range"""
    return 1 <= level <= 10

def validate_caffeine_content(content: int) -> bool:
    """Validate caffeine content is non-negative"""
    return content >= 0

def validate_rating(rating: float) -> bool:
    """Validate rating is within valid range"""
    return 0.0 <= rating <= 5.0

# Logging configuration
logging.basicConfig(level=logging.INFO)
service_logger = logging.getLogger("services")
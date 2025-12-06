from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager

# Database imports
from database import initialize_database, get_db_async, update_expired_keys
from sqlalchemy.ext.asyncio import AsyncSession

# Middleware imports
from middleware import get_current_user, get_current_verified_user

# Service imports
from services import (
    AuthService, PreferenceService, CatalogService,
    TasteQuizService, EmailService
)

# Pydantic models
from pydantic_models import (
    HealthCheckResponse, ErrorResponse
)

from api import auth_router, user_drinks_router, catalog_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup and shutdown handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 Starting DrinkWise Backend...")
    print("Initializing database...")
    
    try:
        await initialize_database()
        print("✅ Database initialized successfully")
        
        # Initialize services
        app.state.auth_service = AuthService
        app.state.preference_service = PreferenceService
        app.state.catalog_service = CatalogService
        app.state.taste_quiz_service = TasteQuizService
        app.state.email_service = EmailService
        print("✅ Services initialized successfully")
        
        # Start background tasks
        app.state.key_cleanup_task = asyncio.create_task(update_expired_keys())
        print("✅ Background tasks started")
        
        logger.info("DrinkWise backend started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    finally:
        print("🛑 Shutting down DrinkWise Backend...")
        
        # Cancel background tasks
        if hasattr(app.state, 'key_cleanup_task'):
            app.state.key_cleanup_task.cancel()
            try:
                await app.state.key_cleanup_task
            except asyncio.CancelledError:
                pass
        
        print("✅ Background tasks cancelled")
        logger.info("DrinkWise backend shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="DrinkWise API",
    description="Personalized drink recommendation system with taste preference learning",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure appropriately for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Service dependency injection
def get_auth_service(db: AsyncSession = Depends(get_db_async)) -> AuthService:
    """Dependency to get AuthService instance"""
    return AuthService(db)

def get_preference_service(db: AsyncSession = Depends(get_db_async)) -> PreferenceService:
    """Dependency to get PreferenceService instance"""
    return PreferenceService(db)

def get_catalog_service(db: AsyncSession = Depends(get_db_async)) -> CatalogService:
    """Dependency to get CatalogService instance"""
    return CatalogService(db)

def get_taste_quiz_service(db: AsyncSession = Depends(get_db_async)) -> TasteQuizService:
    """Dependency to get TasteQuizService instance"""
    return TasteQuizService(db)

def get_email_service(db: AsyncSession = Depends(get_db_async)) -> EmailService:
    """Dependency to get EmailService instance"""
    return EmailService(db)

# Root endpoint
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to DrinkWise API",
        "version": "1.0.0",
        "description": "Personalized drink recommendation system",
        "docs": "/docs",
        "health": "/api/v0/health"
    }

# Health check endpoint
@app.get("/api/v0/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )

# API information endpoint
@app.get("/api/v0/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "DrinkWise API",
        "version": "1.0.0",
        "description": "Personalized drink recommendation system",
        "features": [
            "User authentication & verification",
            "Taste quiz for preferences",
            "Personalized drink recommendations",
            "Drink catalog management", 
            "User preferences & filters",
        ],
        "services": [
            "AuthService", "PreferenceService",
            "CatalogService", "TasteQuizService",
            "EmailService"
        ]
    }



app.include_router(auth_router, prefix="/api/v0", tags=["authentication"])
app.include_router(user_drinks_router, prefix="/api/v0", tags=["user_drinks"])
app.include_router(catalog_router, prefix="/api/v0", tags=["catalog"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return ErrorResponse(
        error="Internal Server Error",
        message="An unexpected error occurred",
        details={"error_type": type(exc).__name__}
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return ErrorResponse(
        error="HTTP Error",
        message=exc.detail,
        details={"status_code": exc.status_code}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

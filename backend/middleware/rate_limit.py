"""
Rate limiting middleware for DrinkWise backend.
Implements token bucket rate limiting to prevent API abuse.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Set, Optional
import time
import asyncio
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Token bucket rate limiter implementation.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize rate limiter.
        
        Args:
            capacity: Maximum number of tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens: Dict[str, float] = defaultdict(lambda: capacity)
        self.last_refill: Dict[str, float] = defaultdict(lambda: time.time())
    
    def is_allowed(self, identifier: str, cost: int = 1) -> bool:
        """
        Check if request is allowed based on rate limiting.
        
        Args:
            identifier: Client identifier (IP address, user ID, etc.)
            cost: Cost of the request in tokens
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        
        # Calculate tokens to add based on time elapsed
        time_passed = now - self.last_refill[identifier]
        tokens_to_add = time_passed * self.refill_rate
        
        # Refill the bucket (up to capacity)
        self.tokens[identifier] = min(
            self.capacity, 
            self.tokens[identifier] + tokens_to_add
        )
        self.last_refill[identifier] = now
        
        # Check if enough tokens available
        if self.tokens[identifier] >= cost:
            self.tokens[identifier] -= cost
            return True
        
        return False
    
    def get_remaining_tokens(self, identifier: str) -> float:
        """
        Get remaining tokens for identifier.
        
        Args:
            identifier: Client identifier
            
        Returns:
            Number of remaining tokens
        """
        return self.tokens[identifier]
    
    def get_reset_time(self, identifier: str) -> float:
        """
        Get time until bucket is refilled to capacity.
        
        Args:
            identifier: Client identifier
            
        Returns:
            Time in seconds until reset
        """
        if self.tokens[identifier] >= self.capacity:
            return 0
        
        # Time to add enough tokens to refill to capacity
        tokens_needed = self.capacity - self.tokens[identifier]
        return tokens_needed / self.refill_rate

class RateLimitMiddleware:
    """
    Rate limiting middleware for FastAPI applications.
    """
    
    def __init__(self, 
                 global_capacity: int = 1000,
                 global_refill_rate: float = 10.0,
                 ip_capacity: int = 100,
                 ip_refill_rate: float = 1.0,
                 user_capacity: int = 200,
                 user_refill_rate: float = 2.0):
        """
        Initialize rate limiting middleware.
        
        Args:
            global_capacity: Global rate limit capacity
            global_refill_rate: Global refill rate (tokens/second)
            ip_capacity: Per-IP rate limit capacity
            ip_refill_rate: Per-IP refill rate (tokens/second)
            user_capacity: Per-user rate limit capacity
            user_refill_rate: Per-user refill rate (tokens/second)
        """
        # Global rate limiter
        self.global_limiter = RateLimiter(global_capacity, global_refill_rate)
        
        # Per-IP rate limiter
        self.ip_limiter = RateLimiter(ip_capacity, ip_refill_rate)
        
        # Per-user rate limiter (for authenticated users)
        self.user_limiter = RateLimiter(user_capacity, user_refill_rate)
        
        # Set of paths that bypass rate limiting
        self.exempt_paths: Set[str] = {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/api/v0/health",
            "/favicon.ico"
        }
        
        # Paths with different rate limits
        self.auth_paths: Set[str] = {
            "/auth/login",
            "/auth/register",
            "/auth/forgot-password"
        }
    
    def get_client_identifier(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client identifier string
        """
        # Try to get user ID from header first (for authenticated users)
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user_{user_id}"
        
        # Fall back to client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Handle proxy headers
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        return f"ip_{client_ip}"
    
    def is_exempt(self, path: str) -> bool:
        """
        Check if path is exempt from rate limiting.
        
        Args:
            path: Request path
            
        Returns:
            True if exempt from rate limiting
        """
        return any(path.startswith(exempt_path) for exempt_path in self.exempt_paths)
    
    def is_auth_path(self, path: str) -> bool:
        """
        Check if path is an authentication endpoint.
        
        Args:
            path: Request path
            
        Returns:
            True if authentication endpoint
        """
        return any(path.startswith(auth_path) for auth_path in self.auth_paths)
    
    def get_rate_limit_response(self, 
                               global_allowed: bool,
                               ip_allowed: bool, 
                               user_allowed: bool,
                               client_id: str) -> JSONResponse:
        """
        Generate rate limit exceeded response.
        
        Args:
            global_allowed: Whether global limit allows request
            ip_allowed: Whether IP limit allows request  
            user_allowed: Whether user limit allows request
            client_id: Client identifier
            
        Returns:
            JSON response with rate limit information
        """
        reset_times = []
        
        if not global_allowed:
            reset_times.append(("global", self.global_limiter.get_reset_time("global")))
        if not ip_allowed:
            reset_times.append(("ip", self.ip_limiter.get_reset_time(client_id)))
        if not user_allowed:
            reset_times.append(("user", self.user_limiter.get_reset_time(client_id)))
        
        # Get the maximum reset time
        if reset_times:
            reset_time = max(reset_times, key=lambda x: x[1])[1]
        else:
            reset_time = 0
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": int(reset_time) + 1,
                "details": {
                    "global_limit": {
                        "allowed": global_allowed,
                        "remaining": self.global_limiter.get_remaining_tokens("global")
                    },
                    "ip_limit": {
                        "allowed": ip_allowed,
                        "remaining": self.ip_limiter.get_remaining_tokens(client_id)
                    },
                    "user_limit": {
                        "allowed": user_allowed,
                        "remaining": self.user_limiter.get_remaining_tokens(client_id)
                    }
                }
            },
            headers={
                "Retry-After": str(int(reset_time) + 1),
                "X-RateLimit-Limit": str(self.global_limiter.capacity),
                "X-RateLimit-Remaining": str(int(self.global_limiter.get_remaining_tokens("global"))),
                "X-RateLimit-Reset": str(int(time.time() + reset_time))
            }
        )
    
    def add_rate_limit_headers(self, response, client_id: str):
        """
        Add rate limit headers to response.
        
        Args:
            response: Response object to modify
            client_id: Client identifier
        """
        response.headers["X-RateLimit-Limit"] = str(self.ip_limiter.capacity)
        response.headers["X-RateLimit-Remaining"] = str(int(self.ip_limiter.get_remaining_tokens(client_id)))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.ip_limiter.get_reset_time(client_id)))

class RateLimitConfig:
    """
    Configuration for different rate limiting scenarios.
    """
    
    # Public endpoints (no authentication required)
    PUBLIC = {
        "capacity": 100,
        "refill_rate": 1.0
    }
    
    # Auth endpoints (register, login, forgot password)
    AUTH = {
        "capacity": 5,
        "refill_rate": 0.5  # Very strict: 1 request every 2 seconds
    }
    
    # API endpoints (authenticated users)
    API = {
        "capacity": 1000,
        "refill_rate": 10.0
    }
    
    # Admin endpoints
    ADMIN = {
        "capacity": 500,
        "refill_rate": 5.0
    }

# Global rate limiter instance
rate_limiter = RateLimitMiddleware()

async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for rate limiting.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/endpoint function
        
    Returns:
        Response with rate limiting applied
    """
    # Skip rate limiting for exempt paths
    if rate_limiter.is_exempt(request.url.path):
        response = await call_next(request)
        return response
    
    # Get client identifier
    client_id = rate_limiter.get_client_identifier(request)
    
    # Check global rate limit
    global_allowed = rate_limiter.global_limiter.is_allowed("global", cost=1)
    
    # Check IP rate limit
    ip_allowed = rate_limiter.ip_limiter.is_allowed(client_id, cost=1)
    
    # Check user rate limit (if authenticated)
    user_id = request.headers.get("X-User-ID")
    user_allowed = True
    if user_id:
        user_id = f"user_{user_id}"
        user_allowed = rate_limiter.user_limiter.is_allowed(user_id, cost=1)
    
    # If any limit is exceeded, return rate limit response
    if not (global_allowed and ip_allowed and user_allowed):
        return rate_limiter.get_rate_limit_response(global_allowed, ip_allowed, user_allowed, client_id)
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    rate_limiter.add_rate_limit_headers(response, client_id)
    
    return response

def get_rate_limit_info(client_id: str) -> Dict[str, any]:
    """
    Get current rate limit information for a client.
    
    Args:
        client_id: Client identifier
        
    Returns:
        Dictionary with rate limit information
    """
    return {
        "global": {
            "capacity": rate_limiter.global_limiter.capacity,
            "remaining": rate_limiter.global_limiter.get_remaining_tokens("global"),
            "reset_time": rate_limiter.global_limiter.get_reset_time("global")
        },
        "ip": {
            "capacity": rate_limiter.ip_limiter.capacity,
            "remaining": rate_limiter.ip_limiter.get_remaining_tokens(client_id),
            "reset_time": rate_limiter.ip_limiter.get_reset_time(client_id)
        },
        "user": {
            "capacity": rate_limiter.user_limiter.capacity,
            "remaining": rate_limiter.user_limiter.get_remaining_tokens(client_id),
            "reset_time": rate_limiter.user_limiter.get_reset_time(client_id)
        }
    }
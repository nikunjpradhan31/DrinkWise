# DrinkWise API Documentation

This document provides comprehensive documentation for all API endpoints in the DrinkWise backend application.

## Table of Contents

- [Authentication API](#authentication-api)
- [Catalog API](#catalog-api)  
- [Preferences API](#preferences-api)
- [User Drinks API](#user-drinks-api)
- [Authentication Requirements](#authentication-requirements)

## Authentication API

### Base Path: `/auth`

#### POST `/auth/register` - Register a new user

**Description**: Register a new user with email verification.

**Authentication**: None required

**Request Body**:
```json
{
  "username": "string (3-50 chars)",
  "email": "valid email",
  "password": "string (8+ chars)",
  "confirmpassword": "string (must match password)",
  "date_of_birth": "optional datetime"
}
```

**Response**:
```json
{
  "user_id": "int",
  "username": "string",
  "email": "string",
  "joindate": "datetime",
  "is_verified": "bool",
  "date_of_birth": "optional datetime",
  "preference_finished": "bool",
  "verification_completed": "bool",
  "access_token": "optional string",
  "token_type": "string (bearer)"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Username or email already exists

#### POST `/auth/login` - Authenticate user

**Description**: Authenticate user and return JWT tokens.

**Authentication**: None required

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**: Same as UserResponse model

**Error Responses**:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid credentials

#### POST `/auth/logout` - Logout user

**Description**: Logout user by invalidating their session.

**Authentication**: Required (Bearer token)

**Response**:
```json
{
  "message": "Logged out successfully"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

#### GET `/auth/me` - Get current user profile

**Description**: Get current user's profile information.

**Authentication**: Required (Bearer token)

**Response**: Same as UserResponse model

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User profile not found

#### PUT `/auth/me` - Update user profile

**Description**: Update current user's profile information.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "username": "optional string (3-50 chars)",
  "date_of_birth": "optional datetime"
}
```

**Response**: Same as UserResponse model

**Error Responses**:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found

#### POST `/auth/forgot-password` - Reset user password

**Description**: Reset user password using verification code.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "string",
  "verification_code": "string",
  "new_password": "string (8+ chars)",
  "confirm_password": "string (must match new_password)"
}
```

**Response**:
```json
{
  "message": "Password reset successfully",
  "user_id": "int"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input or failed reset

#### POST `/auth/resend-verification` - Resend verification email

**Description**: Resend email verification code.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "string"
}
```

**Response**:
```json
{
  "message": "Verification email sent"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email format or failed to send

#### POST `/auth/verify-email` - Verify email address

**Description**: Verify email address using verification code.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "string",
  "verification_code": "string"
}
```

**Response**:
```json
{
  "message": "Email verified successfully"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email format or verification failed

#### GET `/auth/check-username/{username}` - Check username availability

**Description**: Check if username is available for registration.

**Authentication**: None required

**Path Parameters**:
- `username`: string (username to check)

**Response**:
```json
{
  "username": "string",
  "available": "bool",
  "message": "string"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid username format

#### GET `/auth/check-email/{email}` - Check email availability

**Description**: Check if email is available for registration.

**Authentication**: None required

**Path Parameters**:
- `email`: string (email to check)

**Response**:
```json
{
  "email": "string",
  "available": "bool",
  "message": "string"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email format

#### POST `/auth/request-password-reset` - Request password reset

**Description**: Request password reset email.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "string"
}
```

**Response**:
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email format

#### GET `/auth/statistics` - Get user statistics

**Description**: Get current user's statistics and account information.

**Authentication**: Required (Bearer token)

**Response**: User statistics object

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User statistics not found

#### DELETE `/auth/delete-account` - Delete user account

**Description**: Delete user account and all associated data.

**Authentication**: Required (Bearer token)

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `501 Not Implemented`: Account deletion not yet implemented

#### POST `/auth/refresh-token` - Refresh JWT token

**Description**: Refresh JWT token.

**Authentication**: Required (Bearer token)

**Response**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": "int (seconds)"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

## Catalog API

### Base Path: `/catalog`

#### GET `/catalog/drinks` - Search and filter drinks

**Description**: Search and filter drinks with various criteria.

**Authentication**: None required

**Query Parameters**:
- `category`: optional string (filter by category)
- `price_tier`: optional string ($, $$, $$$)
- `max_sweetness`: optional int (1-10)
- `min_caffeine`: optional int (mg)
- `max_caffeine`: optional int (mg)
- `is_alcoholic`: optional bool
- `excluded_ingredients`: optional string (comma-separated)
- `search_text`: optional string
- `page`: int (default: 1)
- `limit`: int (default: 20, max: 100)

**Response**:
```json
{
  "drinks": [
    {
      "drink_id": "int",
      "name": "string",
      "description": "string",
      "category": "string",
      "price_tier": "string",
      "sweetness_level": "int",
      "caffeine_content": "int",
      "sugar_content": "float",
      "calorie_content": "int",
      "image_url": "optional string",
      "is_alcoholic": "bool",
      "alcohol_content": "float",
      "temperature": "string",
      "serving_size": "float",
      "serving_unit": "string",
      "created_at": "datetime",
      "updated_at": "datetime",
      "ingredients": [
        {
          "ingredient_name": "string",
          "quantity": "optional string",
          "is_allergen": "bool"
        }
      ]
    }
  ],
  "total": "int",
  "page": "int",
  "limit": "int",
  "total_pages": "int"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters

#### GET `/catalog/drinks/{drink_id}` - Get detailed drink information

**Description**: Get detailed information about a specific drink.

**Authentication**: None required

**Path Parameters**:
- `drink_id`: int (unique identifier of the drink)

**Response**: Drink object (same structure as in search response)

**Error Responses**:
- `404 Not Found`: Drink not found

#### GET `/catalog/categories` - Get all available drink categories

**Description**: Get all available drink categories.

**Authentication**: None required

**Response**:
```json
{
  "categories": ["string"]
}
```

**Error Responses**:
- `500 Internal Server Error`: Failed to retrieve categories

#### GET `/catalog/popular` - Get popular drinks

**Description**: Get popular drinks based on user interactions.

**Authentication**: None required

**Query Parameters**:
- `limit`: int (default: 20, max: 100)

**Response**:
```json
{
  "drinks": [Drink objects]
}
```

**Error Responses**:
- `500 Internal Server Error`: Failed to retrieve popular drinks

#### GET `/catalog/alcoholic` - Get alcoholic drinks

**Description**: Get alcoholic drinks (requires age verification).

**Authentication**: Required (Bearer token) + Age verification

**Query Parameters**:
- `limit`: int (default: 20, max: 100)

**Response**: Same as popular drinks response

**Error Responses**:
- `403 Forbidden`: Age verification required or user under legal drinking age
- `500 Internal Server Error`: Failed to retrieve alcoholic drinks

#### GET `/catalog/statistics` - Get catalog statistics

**Description**: Get overall catalog statistics.

**Authentication**: None required

**Response**: Catalog statistics object

**Error Responses**:
- `500 Internal Server Error`: Failed to retrieve statistics

#### GET `/catalog/ingredients/{ingredient_name}` - Get drinks by ingredient

**Description**: Get drinks containing a specific ingredient.

**Authentication**: None required

**Path Parameters**:
- `ingredient_name`: string

**Query Parameters**:
- `exclude_allergens`: bool (default: true)

**Response**: Same as popular drinks response

**Error Responses**:
- `500 Internal Server Error`: Failed to retrieve drinks

#### GET `/catalog/user/similar` - Get similar drinks based on user favorites

**Description**: Get drinks similar to user's favorites.

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `limit`: int (default: 10, max: 50)

**Response**:
```json
{
  "drink_ids": ["int"],
  "similar_drinks": [
    {
      "drink": "Drink object",
      "similarity_score": "float",
      "match_reasons": ["string"]
    }
  ],
  "count": "int",
  "recommendation_type": "string"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: No favorites found

#### GET `/catalog/{drink_id}/similar` - Get similar drinks

**Description**: Get drinks similar to a specific drink.

**Authentication**: None required

**Path Parameters**:
- `drink_id`: int

**Query Parameters**:
- `limit`: int (default: 10, max: 50)

**Response**: Same as user similar drinks response

**Error Responses**:
- `404 Not Found`: Drink not found
- `500 Internal Server Error`: Failed to retrieve similar drinks

## Preferences API

### Base Path: `/preferences`

#### GET `/preferences` - Get user preferences

**Description**: Get current user's drink preferences.

**Authentication**: Required (Bearer token)

**Response**:
```json
{
  "user_id": "int",
  "sweetness_preference": "int (1-10)",
  "bitterness_preference": "int (1-10)",
  "caffeine_limit": "int",
  "calorie_limit": "int",
  "preferred_price_tier": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

#### PUT `/preferences` - Update user preferences

**Description**: Create or update current user's drink preferences.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "sweetness_preference": "optional int (1-10)",
  "bitterness_preference": "optional int (1-10)",
  "caffeine_limit": "optional int",
  "calorie_limit": "optional int",
  "preferred_price_tier": "optional string"
}
```

**Response**: Same as GET preferences response

**Error Responses**:
- `400 Bad Request`: Invalid input or failed to update
- `401 Unauthorized`: Invalid or missing token

## User Drinks API

### Base Path: `/user-drinks`

#### GET `/user-drinks/favorites` - Get user's favorite drinks

**Description**: Get all drinks marked as favorites by the current user.

**Authentication**: Required (Bearer token)

**Response**:
```json
{
  "favorites": [
    {
      "drink_id": "int",
      "name": "string",
      "description": "string",
      "category": "string",
      "price_tier": "string",
      "sweetness_level": "int",
      "caffeine_content": "int",
      "sugar_content": "float",
      "calorie_content": "int",
      "image_url": "optional string",
      "is_alcoholic": "bool",
      "alcohol_content": "float",
      "temperature": "string",
      "serving_size": "float",
      "serving_unit": "string",
      "created_at": "datetime",
      "updated_at": "datetime",
      "ingredients": [
        {
          "ingredient_name": "string",
          "quantity": "optional string",
          "is_allergen": "bool"
        }
      ]
    }
  ],
  "total_count": "int"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

#### GET `/user-drinks/statistics` - Get user's drink interaction statistics

**Description**: Get statistics about user's drink interactions.

**Authentication**: Required (Bearer token)

**Response**: User drink statistics object

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

#### GET `/user-drinks/{drink_id}` - Get user interaction info

**Description**: Get current user's interaction information about a specific drink.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `drink_id`: int

**Response**:
```json
{
  "user_id": "int",
  "drink_id": "int",
  "times_consumed": "int",
  "is_favorite": "bool",
  "rating": "float",
  "is_not_for_me": "bool",
  "viewed_at": "datetime",
  "last_consumed": "optional datetime"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Drink not found

#### PUT `/user-drinks/{drink_id}` - Update user interaction

**Description**: Update user's interaction with a specific drink.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `drink_id`: int

**Request Body**:
```json
{
  "times_consumed": "optional int",
  "is_favorite": "optional bool",
  "rating": "optional float (0.0-5.0)",
  "is_not_for_me": "optional bool"
}
```

**Response**: Same as GET user interaction response

**Error Responses**:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Drink not found

## Authentication Requirements

### Endpoints Requiring Authentication

The following endpoints require a valid JWT Bearer token in the Authorization header:

**Authentication API:**
- `POST /auth/logout`
- `GET /auth/me`
- `PUT /auth/me`
- `GET /auth/statistics`
- `DELETE /auth/delete-account`
- `POST /auth/refresh-token`

**Preferences API:**
- `GET /preferences`
- `PUT /preferences`

**User Drinks API:**
- `GET /user-drinks/favorites`
- `GET /user-drinks/statistics`
- `GET /user-drinks/{drink_id}`
- `PUT /user-drinks/{drink_id}`

**Catalog API:**
- `GET /catalog/alcoholic` (also requires age verification)
- `GET /catalog/user/similar`

### Authentication Header Format

```
Authorization: Bearer <your_jwt_token>
```

### Age Verification

The `/catalog/alcoholic` endpoint requires both authentication and age verification. The user must:
1. Be authenticated (have a valid JWT token)
2. Have a date of birth set in their profile
3. Be of legal drinking age (21+ years)

## Error Handling

All endpoints follow consistent error response patterns:

**Error Response Format**:
```json
{
  "error": "string",
  "message": "string",
  "details": "optional object"
}
```

**Common HTTP Status Codes**:
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input or request
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Access denied (e.g., age verification failed)
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server-side error

## Rate Limiting

The API implements rate limiting to prevent abuse. When rate limited, responses will include:

```
X-RateLimit-Limit: <limit>
X-RateLimit-Remaining: <remaining>
X-RateLimit-Reset: <reset_timestamp>
```

## API Versioning

The current API version is `1.0.0`. All endpoints are prefixed with their respective base paths as documented above.
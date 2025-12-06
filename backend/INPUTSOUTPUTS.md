# DrinkWise API - Inputs and Outputs Documentation

This document provides JSON schemas for all API endpoints in the DrinkWise backend system.

## Table of Contents
- [Authentication Endpoints](#authentication-endpoints)
- [User Preferences](#user-preferences)
- [Drink Catalog](#drink-catalog)
- [Taste Quiz System](#taste-quiz-system)
- [User-Drink Interactions](#user-drink-interactions)
- [Recommendation System](#recommendation-system)

---

## Authentication Endpoints

### POST /auth/register
**Register a new user with 2FA email verification**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "minLength": 3,
      "maxLength": 50
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "password": {
      "type": "string",
      "minLength": 8,
      "maxLength": 128
    },
    "confirmpassword": {
      "type": "string",
      "minLength": 8,
      "maxLength": 128
    },
    "date_of_birth": {
      "type": "string",
      "format": "date-time",
      "nullable": true
    }
  },
  "required": ["username", "email", "password", "confirmpassword"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer"
    },
    "username": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "joindate": {
      "type": "string",
      "format": "date-time"
    },
    "is_verified": {
      "type": "boolean"
    },
    "date_of_birth": {
      "type": "string",
      "format": "date-time",
      "nullable": true
    },
    "questionnaire_finished": {
      "type": "boolean"
    },
    "verification_completed": {
      "type": "boolean"
    },
    "access_token": {
      "type": "string"
    },
    "token_type": {
      "type": "string",
      "enum": ["bearer"]
    }

  }
}
```

### POST /auth/login
**User authentication and access token generation**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "minLength": 3,
      "maxLength": 50
    },
    "password": {
      "type": "string",
      "minLength": 8,
      "maxLength": 128
    }
  },
  "required": ["username", "password"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer"
    },
    "username": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "joindate": {
      "type": "string",
      "format": "date-time"
    },
    "access_token": {
      "type": "string"
    },
    "token_type": {
      "type": "string",
      "enum": ["bearer"]
    },
    "is_verified": {
      "type": "boolean"
    },
    "questionnaire_finished": {
      "type": "boolean"
    },
        "date_of_birth": {
      "type": "string",
      "format": "date-time",
      "nullable": true
    },
  }
}
```

### POST /auth/logout
**User session termination**

**Input Schema:**
```
No body required - uses Bearer token in Authorization header
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "enum": ["Logged out successfully"]
    }
  }
}
```

### POST /auth/forgot-password
**Forgot Password - User inputs code from email and new password**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email"
    },
    "verification_code": {
      "type": "string"
    },
    "new_password": {
      "type": "string",
      "minLength": 8,
      "maxLength": 128
    },
    "confirm_password": {
      "type": "string",
      "minLength": 8,
      "maxLength": 128
    }
  },
  "required": ["email", "verification_code", "new_password", "confirm_password"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "enum": ["Password reset successfully"]
    },
    "user_id": {
      "type": "integer"
    }
  }
}
```

### GET /auth/me
**Get current user profile**

**Input Schema:**
```
No body required - uses Bearer token in Authorization header
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer"
    },
    "username": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "joindate": {
      "type": "string",
      "format": "date-time"
    },
    "is_verified": {
      "type": "boolean"
    },
    "verification_completed": {
      "type": "boolean"
    },
    "questionnaire_finished": {
      "type": "boolean"
    },
        "date_of_birth": {
      "type": "string",
      "format": "date-time",
      "nullable": true
    },
        "access_token": {
      "type": "string"
    },
    "token_type": {
      "type": "string",
      "enum": ["bearer"]
    },
  }
}
```

### PUT /auth/me
**Update current user profile**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "minLength": 3,
      "maxLength": 50,
      "nullable": true
    },
    "date_of_birth": {
      "type": "string",
      "format": "date-time",
      "nullable": true
    }
  }
}
```

**Output Schema:** Same as GET /auth/me

---

## User Preferences

### GET /preferences
**Get user profile drink preferences**

**Input Schema:**
```
No body required - uses Bearer token in Authorization header
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer"
    },
    "sweetness_preference": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10
    },
    "bitterness_preference": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10
    },
    "sugar_limit": {
      "type": "number",
      "minimum": 0.0
    },
    "caffeine_limit": {
      "type": "integer",
      "minimum": 0
    },
    "calorie_limit": {
      "type": "integer",
      "minimum": 0
    },
    "preferred_price_tier": {
      "type": "string",
      "enum": ["$", "$$", "$$$"]
    },
    "time_sensitivity": {
      "type": "object",
      "nullable": true
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### POST /preferences
**Update user profile drink preferences**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "sweetness_preference": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "nullable": true
    },
    "bitterness_preference": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "nullable": true
    },
    "sugar_limit": {
      "type": "number",
      "minimum": 0.0,
      "nullable": true
    },
    "caffeine_limit": {
      "type": "integer",
      "minimum": 0,
      "nullable": true
    },
    "calorie_limit": {
      "type": "integer",
      "minimum": 0,
      "nullable": true
    },
    "preferred_price_tier": {
      "type": "string",
      "enum": ["$", "$$", "$$$"],
      "nullable": true
    },

  }
}
```

**Output Schema:** Same as GET /preferences

---

## Drink Catalog

### GET /catalog/drinks
**Search and filter drinks**

**Input Schema:**
```
Query Parameters:
- category: string (optional)
- price_tier: string (optional, enum: ["$", "$$", "$$$"])
- max_sweetness: integer (optional, 1-10)
- min_caffeine: integer (optional, >=0)
- max_caffeine: integer (optional, >=0)
- is_alcoholic: boolean (optional)
- excluded_ingredients: string (optional, comma-separated)
- search_text: string (optional)
- page: integer (optional, default: 1)
- limit: integer (optional, default: 20)
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "drinks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "drink_id": {
            "type": "integer"
          },
          "name": {
            "type": "string",
            "maxLength": 200
          },
          "description": {
            "type": "string"
          },
          "category": {
            "type": "string",
            "maxLength": 100
          },
          "price_tier": {
            "type": "string",
            "enum": ["$", "$$", "$$$"]
          },
          "sweetness_level": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10
          },
          "caffeine_content": {
            "type": "integer",
            "minimum": 0
          },
          "sugar_content": {
            "type": "number",
            "minimum": 0.0
          },
          "calorie_content": {
            "type": "integer",
            "minimum": 0
          },
          "image_url": {
            "type": "string",
            "nullable": true
          },
          "is_alcoholic": {
            "type": "boolean"
          },
          "alcohol_content": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 100.0
          },
          "safety_flags": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "nullable": true
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          },
          "updated_at": {
            "type": "string",
            "format": "date-time"
          },
          "ingredients": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "ingredient_name": {"type": "string"},
                "quantity": {"type": "string", "nullable": true},
                "is_allergen": {"type": "boolean"}
              }
            }
          },
          "tags": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "total": {
      "type": "integer"
    },
    "page": {
      "type": "integer"
    },
    "limit": {
      "type": "integer"
    },
    "total_pages": {
      "type": "integer"
    }
  }
}
```

### GET /catalog/drinks/{drink_id}
**Get detailed drink information**

**Input Schema:**
```
Path Parameter:
- drink_id: integer (required)
```

**Output Schema:** Individual drink object from the drinks array in GET /catalog/drinks

### GET /catalog/categories
**Get all available drink categories**

**Input Schema:**
```
No parameters required
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "categories": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

### GET /catalog/popular
**Get popular drinks**

**Input Schema:**
```
Query Parameters:
- limit: integer (optional, default: 20)
```

**Output Schema:** Array of drink objects

### GET /catalog/alcoholic
**Get alcoholic drinks (requires age verification)**

**Input Schema:**
```
Query Parameters:
- limit: integer (optional, default: 20)
```

**Output Schema:** Array of drink objects (alcoholic only)

---

## Taste Quiz System

### GET /quiz/questions
**Get questions and answers that user has seen**

**Input Schema:**
```
No body required - uses Bearer token in Authorization header
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "questions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "question_id": {
            "type": "integer"
          },
          "question_text": {
            "type": "string"
          },
          "is_active": {
            "type": "boolean"
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          },
          "options": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "option_id": {
                  "type": "integer"
                },
                "option_text": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    },
    "total_questions": {
      "type": "integer"
    }
  }
}
```

### POST /quiz/submit
**Updates / answers the question that user has been given**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "answers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "question_id": {
            "type": "integer"
          },
          "option_id": {
            "type": "integer"
          }
        },
        "required": ["question_id", "option_id"]
      }
    }
  },
  "required": ["answers"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string"
    },
    "answers_submitted": {
      "type": "integer"
    },
    "quiz_completed": {
      "type": "boolean"
    }
  }
}
```

### GET /quiz/provide
**Provides a list of questions and options to answer**

**Input Schema:**
```
Query Parameters:
- count: integer (optional, default: 8)
```

**Output Schema:** Same as GET /quiz/questions

---

## User-Drink Interactions

### GET /user-drinks/{drink_id}
**Gets the user interaction info about the drink**

**Input Schema:**
```
Path Parameter:
- drink_id: integer (required)
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer"
    },
    "drink_id": {
      "type": "integer"
    },
    "times_consumed": {
      "type": "integer",
      "minimum": 0
    },
    "is_favorite": {
      "type": "boolean"
    },
    "rating": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 5.0
    },
    "is_not_for_me": {
      "type": "boolean"
    },
    "viewed_at": {
      "type": "string",
      "format": "date-time"
    },
    "last_consumed": {
      "type": "string",
      "format": "date-time",
      "nullable": true
    }
  }
}
```

### PUT /user-drinks/{drink_id}
**Updates the user interaction info about the drink**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "times_consumed": {
      "type": "integer",
      "minimum": 0,
      "nullable": true
    },
    "is_favorite": {
      "type": "boolean",
      "nullable": true
    },
    "rating": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 5.0,
      "nullable": true
    },
    "is_not_for_me": {
      "type": "boolean",
      "nullable": true
    }
  }
}
```

**Output Schema:** Same as GET /user-drinks/{drink_id}

### GET /user-favorites
**Get user's favorite drinks**

**Input Schema:**
```
No body required - uses Bearer token in Authorization header
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "favorites": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "drink_id": {"type": "integer"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "category": {"type": "string"},
          "price_tier": {"type": "string", "enum": ["$", "$$", "$$$"]},
          "sweetness_level": {"type": "integer"},
          "caffeine_content": {"type": "integer"},
          "sugar_content": {"type": "number"},
          "calorie_content": {"type": "integer"},
          "image_url": {"type": "string", "nullable": true},
          "is_alcoholic": {"type": "boolean"},
          "alcohol_content": {"type": "number"},
          "safety_flags": {"type": "array", "items": {"type": "string"}},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"},
          "ingredients": {"type": "array"},
          "tags": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "total_count": {
      "type": "integer"
    }
  }
}
```

---

## Recommendation System

### GET /recommendations/drinks
**Drink-to-drink, drinks-drinks recommendation**

**Input Schema:**
```
Query Parameters:
- drink_id: integer (optional, base drink for similar recommendations)
- limit: integer (optional, default: 10)
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "drink_id": {
      "type": "integer",
      "description": "Base drink ID for recommendations"
    },
    "similar_drinks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "drink_id": {"type": "integer"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "category": {"type": "string"},
          "price_tier": {"type": "string", "enum": ["$", "$$", "$$$"]},
          "sweetness_level": {"type": "integer"},
          "caffeine_content": {"type": "integer"},
          "sugar_content": {"type": "number"},
          "calorie_content": {"type": "integer"},
          "image_url": {"type": "string", "nullable": true},
          "is_alcoholic": {"type": "boolean"},
          "alcohol_content": {"type": "number"},
          "safety_flags": {"type": "array", "items": {"type": "string"}},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"},
          "similarity_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
        }
      }
    },
    "count": {
      "type": "integer"
    },
    "recommendation_type": {
      "type": "string",
      "enum": ["similar", "collaborative", "content"]
    }
  }
}
```

### GET /recommendations/users
**User-to-user drink recommendation**

**Input Schema:**
```
Query Parameters:
- limit: integer (optional, default: 10)
- recommendation_type: string (optional, enum: ["hybrid", "collaborative", "content"])
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "drink": {
            "type": "object",
            "properties": {
              "drink_id": {"type": "integer"},
              "name": {"type": "string"},
              "description": {"type": "string"},
              "category": {"type": "string"},
              "price_tier": {"type": "string", "enum": ["$", "$$", "$$$"]},
              "sweetness_level": {"type": "integer"},
              "caffeine_content": {"type": "integer"},
              "sugar_content": {"type": "number"},
              "calorie_content": {"type": "integer"},
              "image_url": {"type": "string", "nullable": true},
              "is_alcoholic": {"type": "boolean"},
              "alcohol_content": {"type": "number"},
              "safety_flags": {"type": "array", "items": {"type": "string"}},
              "created_at": {"type": "string", "format": "date-time"},
              "updated_at": {"type": "string", "format": "date-time"}
            }
          },
          "score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
          },
          "explanation": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Reasons why this drink is recommended"
          }
        }
      }
    },
    "total_count": {
      "type": "integer"
    },
    "recommendation_type": {
      "type": "string",
      "enum": ["hybrid", "collaborative", "content"]
    }
  }
}
```

<!-- ### POST /recommendations/feedback
**Submit feedback on recommendations to improve future suggestions**

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "drink_id": {
      "type": "integer"
    },
    "feedback_type": {
      "type": "string",
      "enum": ["not_for_me", "love_it", "too_sweet", "too_bitter", "too_expensive", "perfect"]
    },
    "feedback_text": {
      "type": "string",
      "nullable": true
    }
  },
  "required": ["drink_id", "feedback_type"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string"
    },
    "feedback_type": {
      "type": "string"
    },
    "drink_id": {
      "type": "integer"
    }
  }
}
```

### GET /recommendations/similar/{drink_id}
**Get drinks similar to a given drink**

**Input Schema:**
```
Path Parameter:
- drink_id: integer (required)

Query Parameters:
- limit: integer (optional, default: 10)
```

**Output Schema:** Same as GET /recommendations/drinks

---

## Health Check

### GET /api/v0/health
**Health check endpoint**

**Input Schema:**
```
No parameters required
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["healthy"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "version": {
      "type": "string",
      "default": "1.0.0"
    }
  }
}
```

---

## Error Responses

All endpoints may return error responses with the following schema:

```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "details": {
      "type": "object",
      "nullable": true
    }
  }
}
```

**Common HTTP Status Codes:**
- 200: Success
- 400: Bad Request (validation error)
- 401: Unauthorized (invalid or missing token)
- 403: Forbidden (age verification required)
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

---

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Age-restricted endpoints (alcoholic drinks) require additional age verification through the `/auth/verify-age` endpoint.

---

*Last updated: 2025-12-05*
*API Version: 1.0.0*
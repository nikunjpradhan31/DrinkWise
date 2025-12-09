# DrinkWise Backend Unit Tests

This directory contains unit tests for all backend services in the DrinkWise application.

## Test Files

- `test_auth_service.py` - Tests for authentication service (user registration, login, password management)
- `test_catalog_service.py` - Tests for catalog service (drink search, filtering, recommendations)
- `test_email_service.py` - Tests for email service (verification, password reset emails)
- `test_preference_service.py` - Tests for preference service (user taste preferences)
- `test_user_drinks_service.py` - Tests for user-drinks service (favorites, ratings, consumption tracking)

## Running Tests

To run all unit tests:

```bash
cd /home/nikunj/Desktop/ProgramFiles/DrinkWise
pytest backend/unit_tests/
```

To run tests for a specific service:

```bash
pytest backend/unit_tests/test_auth_service.py
```

## Test Coverage

The unit tests cover:
- Service initialization and dependency injection
- Database operations (create, read, update, delete)
- Business logic and validation
- Error handling and edge cases
- Integration with Pydantic models

## Mocking Strategy

All tests use mocking to isolate the services from:
- Database dependencies (SQLAlchemy)
- External services (email, authentication middleware)
- Other services

This ensures fast, reliable tests that focus on business logic.

## Test Structure

Each test file follows a similar pattern:
1. Fixtures for mock dependencies
2. Tests for happy paths (successful operations)
3. Tests for error cases (validation errors, not found, etc.)
4. Tests for edge cases (empty results, defaults, etc.)
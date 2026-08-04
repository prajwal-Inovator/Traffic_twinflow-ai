# backend/tests/unit/test_user_repo.py
import pytest
from app.repositories.user_repo import UserRepository
from app.models.user import User, UserRole

@pytest.mark.asyncio
async def test_create_user(db_client):
    repo = UserRepository(db_client)
    user_data = {
        "email": "test@example.com",
        "hashed_password": "hashed",
        "full_name": "Test User",
        "role": UserRole.DRIVER,
    }
    user = await repo.create(user_data)
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.DRIVER

@pytest.mark.asyncio
async def test_get_user_by_email(db_client):
    repo = UserRepository(db_client)
    user_data = {
        "email": "test@example.com",
        "hashed_password": "hashed",
        "full_name": "Test User",
        "role": UserRole.AUTHORITY,
    }
    created = await repo.create(user_data)
    found = await repo.get_by_email("test@example.com")
    assert found is not None
    assert found.id == created.id
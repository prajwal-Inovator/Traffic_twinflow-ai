# backend/tests/unit/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from app.schemas.auth_schemas import UserCreate
from app.core.exceptions import AuthenticationError, ValidationError

@pytest.mark.asyncio
async def test_register_user(db_client):
    repo = UserRepository(db_client)
    service = AuthService(repo)
    user_data = UserCreate(
        email="new@test.com",
        password="password123",
        full_name="New User",
        role="driver"
    )
    user = await service.register_user(user_data)
    assert user.email == "new@test.com"

@pytest.mark.asyncio
async def test_register_duplicate_email(db_client):
    repo = UserRepository(db_client)
    service = AuthService(repo)
    user_data = UserCreate(
        email="duplicate@test.com",
        password="password123",
        full_name="Duplicate User",
        role="driver"
    )
    await service.register_user(user_data)
    with pytest.raises(ValidationError):
        await service.register_user(user_data)

@pytest.mark.asyncio
async def test_authenticate_user(db_client):
    repo = UserRepository(db_client)
    service = AuthService(repo)
    user_data = UserCreate(
        email="auth@test.com",
        password="securepass",
        full_name="Auth User",
        role="admin"
    )
    await service.register_user(user_data)
    user = await service.authenticate_user("auth@test.com", "securepass")
    assert user is not None
    assert user.email == "auth@test.com"

@pytest.mark.asyncio
async def test_authenticate_wrong_password(db_client):
    repo = UserRepository(db_client)
    service = AuthService(repo)
    user_data = UserCreate(
        email="auth@test.com",
        password="securepass",
        full_name="Auth User",
        role="admin"
    )
    await service.register_user(user_data)
    with pytest.raises(AuthenticationError):
        await service.authenticate_user("auth@test.com", "wrongpass")
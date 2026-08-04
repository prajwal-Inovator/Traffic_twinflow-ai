# backend/tests/conftest.py
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.core.redis import get_redis
import redis.asyncio as aioredis
import os

# Test database
TEST_MONGO_URI = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/test_twinflow")
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_client():
    client = AsyncIOMotorClient(TEST_MONGO_URI)
    db = client.get_database()
    yield db
    # Clean up after test
    await client.drop_database(db.name)
    client.close()

@pytest.fixture(scope="function")
async def redis_client():
    client = await aioredis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    await client.flushdb()
    await client.close()

@pytest.fixture(scope="function")
def test_client(db_client, redis_client):
    # Override dependency
    async def override_get_db():
        yield db_client
    app.dependency_overrides[get_db] = override_get_db

    async def override_get_redis():
        yield redis_client
    app.dependency_overrides[get_redis] = override_get_redis

    with TestClient(app) as client:
        yield client

@pytest.fixture
def auth_headers(test_client):
    # Create test user and get token
    response = test_client.post("/api/v1/auth/register", json={
        "email": "test@twinflow.ai",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "admin"
    })
    assert response.status_code == 201
    data = response.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}
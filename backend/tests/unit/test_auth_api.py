# backend/tests/integration/test_auth_api.py
import pytest
from app.core.security import decode_token

def test_register(test_client):
    response = test_client.post("/api/v1/auth/register", json={
        "email": "api@test.com",
        "password": "api123",
        "full_name": "API Test User",
        "role": "driver"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login(test_client):
    # First register
    test_client.post("/api/v1/auth/register", json={
        "email": "login@test.com",
        "password": "login123",
        "full_name": "Login Test",
        "role": "admin"
    })
    response = test_client.post("/api/v1/auth/login", json={
        "email": "login@test.com",
        "password": "login123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_get_current_user(test_client, auth_headers):
    response = test_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@twinflow.ai"
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_successful_registration():
    email = f"test_{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data

def test_duplicate_registration():
    email = f"test_{uuid.uuid4()}@example.com"
    payload = {"email": email, "password": "password123", "full_name": "Test User"}
    client.post("/api/v1/auth/register", json=payload)
    
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "The user with this email already exists in the system."

def test_successful_login():
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"}
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_wrong_password():
    email = f"test_{uuid.uuid4()}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"}
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "wrongpassword"}
    )
    assert response.status_code == 400

def test_nonexistent_user_login():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": f"nonexistent_{uuid.uuid4()}@example.com", "password": "password123"}
    )
    assert response.status_code == 400

def test_missing_token():
    response = client.post(
        "/api/v1/conversations/",
        json={"title": "Test"}
    )
    assert response.status_code == 401

def test_invalid_token():
    response = client.post(
        "/api/v1/conversations/",
        headers={"Authorization": "Bearer invalidtoken123"},
        json={"title": "Test"}
    )
    assert response.status_code == 401

def test_expired_token():
    import time
    from app.core import security
    
    # Create token expired 1 hour ago
    from datetime import timedelta
    expired_token = security.create_access_token(
        subject=1, expires_delta=timedelta(hours=-1)
    )
    
    response = client.post(
        "/api/v1/conversations/",
        headers={"Authorization": f"Bearer {expired_token}"},
        json={"title": "Test"}
    )
    assert response.status_code == 401

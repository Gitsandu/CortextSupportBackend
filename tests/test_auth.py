import pytest
from fastapi import status

def test_register_user(client):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data

def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    user_data = {
        "email": "test1@example.com",
        "username": "duplicate",
        "password": "testpassword",
        "full_name": "Test User"
    }
    
    # First registration should succeed
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Second registration with same username should fail
    user_data["email"] = "test2@example.com"
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client):
    """Test successful login."""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "testpassword",
        "full_name": "Login User"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Then try to login
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    response = client.post(
        "/api/v1/auth/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

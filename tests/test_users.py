import pytest
from fastapi import status

def test_get_current_user(client, auth_headers):
    """Test getting the current user with valid token."""
    headers = auth_headers()
    response = client.get("/api/v1/users/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "username" in data
    assert "hashed_password" not in data

def test_get_current_user_unauthorized(client):
    """Test getting current user without token."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_current_user(client, auth_headers):
    """Test updating the current user."""
    headers = auth_headers()
    
    # Get current user first
    response = client.get("/api/v1/users/me", headers=headers)
    user_id = response.json()["id"]
    
    # Update user data
    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com"
    }
    
    response = client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

def test_update_password(client, auth_headers):
    """Test updating the current user's password."""
    headers = auth_headers()
    
    # Update password
    update_data = {
        "password": "newpassword123"
    }
    
    response = client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK

def test_delete_current_user(client, auth_headers):
    """Test deleting the current user."""
    # Create a new user and get auth headers
    username = "tobedeleted"
    password = "testpassword"
    headers = auth_headers(username=username, password=password)
    
    # Delete the user
    response = client.delete("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Try to access the user again (should fail)
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

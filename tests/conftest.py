import asyncio
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".env.test")

# Override environment variables for testing
os.environ["MONGODB_DB_NAME"] = "test_fastapi_mongodb"

from app.main import app
from app.db.session import db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module", autouse=True)
async def setup_test_db():
    """Set up test database before tests and clean up after."""
    # Connect to test database
    test_db = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))[os.getenv("MONGODB_DB_NAME")]
    db.database = test_db
    
    yield  # This is where the testing happens
    
    # Clean up: Drop the test database after tests
    await test_db.client.drop_database(test_db.name)

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for test requests."""
    async def _auth_headers(username: str = "testuser", password: str = "testpassword"):
        # First create a user
        user_data = {
            "email": f"{username}@example.com",
            "username": username,
            "password": password,
            "full_name": "Test User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Then login to get the token
        login_data = {
            "username": username,
            "password": password
        }
        response = client.post(
            "/api/v1/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    return _auth_headers

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from ....schemas.user import Token, UserCreate, UserInDB, UserResponse
from ....services.user_service import UserService
from ....core.security import create_access_token, get_password_hash
from ....core.config import settings

router = APIRouter(tags=["auth"], prefix="/auth")

@router.post(
    "/test-token",
    response_model=UserResponse,
    summary="Test access token validity",
    description="""
    Validate an access token and return user information.
    
    **Authentication:** Required (JWT Token)
    
    **Permissions:**
    - Any authenticated user
    
    **Returns:**
    - Current user's information if token is valid
    
    **Notes:**
    - Useful for checking token validity from client-side
    - Returns 401 if token is invalid or expired
    """,
    response_description="Current user's information if token is valid",
    responses={
        200: {"description": "Token is valid"},
        401: {"description": "Invalid or expired token"},
        403: {"description": "Insufficient permissions"}
    }
)
async def test_token():
    """
    Test access token validity.
    """
    # TO DO: implement test token logic

@router.post(
    "/login/access-token",
    response_model=Token,
    summary="OAuth2 compatible token login",
    description="""
    Authenticate user and retrieve an access token for API access.
    
    **Authentication:** Not required
    
    **Request Body:**
    - `username`: User's email or username
    - `password`: User's password
    
    **Returns:**
    - `access_token`: JWT token for authenticated requests
    - `token_type`: Type of token (always 'bearer')
    
    **Notes:**
    - Token expires in 30 minutes by default
    - Include token in Authorization header as: `Bearer <token>`
    """,
    response_description="Authentication token and type",
    responses={
        200: {"description": "Successfully authenticated"},
        400: {"description": "Invalid request format"},
        401: {"description": "Incorrect username or password"},
        500: {"description": "Internal server error"}
    }
)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await UserService.authenticate_user(
        username=form_data.username, password=form_data.password
    )
    
    access_token = UserService.create_access_token_for_user(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    description="""
    Register a new user account in the system.
    
    **Authentication:** Not required
    
    **Request Body:**
    - `email`: Must be a valid and unique email address
    - `username`: Must be unique (3-50 characters)
    - `password`: At least 8 characters with mixed case and numbers
    - `full_name`: Optional display name (2-100 characters)
    
    **Returns:**
    - Newly created user object (without password hash)
    
    **Notes:**
    - Email verification may be required
    - Default role is 'user'
    - Passwords are hashed before storage
    """,
    response_description="Successfully created user account",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Username or email already exists"},
        422: {"description": "Validation error"}
    }
)
async def create_user(user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = await UserService.create_user(user_in)
    return user

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from bson import ObjectId
from jose import JWTError, jwt

from ....schemas.user import UserInDB, UserCreate, UserUpdate, UserResponse
from ....schemas.common import PaginationParams, PaginatedResponse
from ....services.user_service import UserService
from ....core.security import get_current_active_user, get_current_active_superuser, get_password_hash
from ....core.config import settings

router = APIRouter(tags=["users"], prefix="/users")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user_service = UserService()
    user = await user_service.get_by_username(username=username)
    if user is None:
        raise credentials_exception
    return user

@router.get(
    "/", 
    response_model=PaginatedResponse[UserResponse],
    summary="Get users",
    description="""
    Retrieve a list of users.
    
    **Authentication:** Required (JWT Token)
    
    **Permissions:**
    - Admin users can view all users
    - Regular users can only view their own profile
    
    **Parameters:**
    - skip: Number of users to skip (default: 0)
    - limit: Number of users to return (default: 10, max: 100)
    
    **Returns:**
    - Paginated response with list of user objects and metadata
    """,
    response_description="The paginated list of users",
    responses={
        200: {"description": "Successfully retrieved user data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"}
    }
)
async def read_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    """
    Get a paginated list of users.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (1-100)
        current_user: The currently authenticated user
        
    Returns:
        Paginated response with users and metadata
    """
    user_service = UserService()
    result = await user_service.get_users(skip=skip, limit=limit, current_user=current_user)
    return result

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="""
    Retrieve a user by their unique ID.
    
    **Authentication:** Required (JWT Token)
    
    **Permissions:**
    - Admin users can view any user
    - Regular users can only view their own profile
    
    **Parameters:**
    - user_id: UUID of the user to retrieve
    
    **Returns:**
    - User object with all user details
    """,
    response_description="The requested user's information",
    responses={
        200: {"description": "Successfully retrieved user data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"}
    }
)
async def read_user_by_id(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific user by ID.
    
    - Admin users can view any user
    - Regular users can only view their own profile
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only allow admins to access other users' data
    if not current_user.is_superuser and str(user.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="""
    Retrieve the currently authenticated user's information.
    
    **Authentication:** Required (JWT Token)
    
    **Permissions:**
    - Any authenticated user
    
    **Returns:**
    - User object with all user details
    """,
    response_description="The current user's information",
    responses={
        200: {"description": "Successfully retrieved user data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"}
    }
)
async def read_user_me(
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    
    Returns the currently authenticated user's profile information.
    """
    return current_user

@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="""
    Update the currently authenticated user's information.
    
    **Authentication:** Required (JWT Token)
    
    **Permissions:**
    - User can only update their own profile
    
    **Notes:**
    - Partial updates are supported
    - Email must be unique
    - Password must be at least 8 characters
    
    **Returns:**
    - Updated user object
    """,
    response_description="The updated user information",
    responses={
        200: {"description": "Successfully updated user data"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        409: {"description": "Email already registered"}
    }
)
async def update_user_me(
    user_in: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """
    Update the current user's information.
    
    Args:
        user_in: The user data to update
        current_user: The currently authenticated user
        
    Returns:
        UserInDB: The updated user data
        
    Raises:
        HTTPException: If update data is invalid or user is not authenticated
    """
    if user_in.password:
        user_in.hashed_password = get_password_hash(user_in.password)
    return await UserService.update_user(current_user.id, user_in)

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user",
    description="""
    Permanently delete the current user's account.
    
    **Authentication:** Required (JWT Token)
    
    **Permissions:**
    - User can only delete their own account
    
    **Notes:**
    - This action is irreversible
    - All user data will be permanently removed
    - Active sessions will be invalidated
    
    **Returns:**
    - No content (204) on success
    """,
    responses={
        204: {"description": "User successfully deleted"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"}
    }
)
async def delete_user_me(
    current_user: UserInDB = Depends(get_current_active_user)
) -> None:
    """
    Delete the current user's account.
    
    Args:
        current_user: The currently authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If user is not authenticated
    """
    """
    Delete own user.
    """
    await UserService.delete_user(current_user.id)
    return None

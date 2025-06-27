from typing import Optional, List, Dict, Any, Union
from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument
from bson import ObjectId
from datetime import datetime, timedelta

from ..db.session import get_database
from ..schemas.user import UserCreate, UserUpdate, UserInDB, UserResponse, Token, TokenData
from ..schemas.common import PaginatedResponse
from ..core.security import create_access_token, get_password_hash, verify_password
from ..core.config import settings
from ..db.pagination import CRUDPaginatedMongo

class UserService(CRUDPaginatedMongo):
    """Service for user-related operations."""
    
    def __init__(self):
        """Initialize UserService with database connection and collection."""
        db = get_database()
        super().__init__(db.users, UserResponse)
    
    @staticmethod
    def _convert_to_response(user: Optional[Dict[str, Any]]) -> Optional[UserResponse]:
        """Convert MongoDB document to UserResponse.
        
        Args:
            user: MongoDB document or None
            
        Returns:
            UserResponse or None if user is None
        """
        if not user:
            return None
        user["id"] = str(user["_id"])
        return UserResponse(**user)
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """Get a user by ID."""
        if not ObjectId.is_valid(user_id):
            return None
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._convert_to_response(user)
    
    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get a user by email."""
        user = await self.collection.find_one({"email": email})
        return self._convert_to_response(user)
    
    async def get_by_username(self, username: str) -> Optional[UserResponse]:
        """Get a user by username."""
        user = await self.collection.find_one({"username": username})
        return self._convert_to_response(user)
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 10,
        current_user: Optional[UserInDB] = None
    ) -> dict:
        """
        Get a paginated list of users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return (1-100)
            current_user: The currently authenticated user (for permission checks)
            
        Returns:
            dict: Paginated response with users and metadata
        """
        # Ensure limit is within bounds
        limit = max(1, min(100, limit))
        
        # If not an admin, only return the current user's data
        if current_user and not getattr(current_user, 'is_superuser', False):
            user = await self.get_user(str(current_user.id))
            return {
                "items": [user] if user else [],
                "total": 1 if user else 0,
                "page": 1,
                "page_size": 1,
                "total_pages": 1
            }
            
        # For admins, return all users with pagination
        total = await self.collection.count_documents({})
        cursor = self.collection.find().skip(skip).limit(limit)
        users = [self._convert_to_response(user) async for user in cursor]
        
        return {
            "items": users,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "page_size": min(limit, len(users)) if users else 0,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    
    async def create_user(self, user_in: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if user with email already exists
        if await self.get_by_email(user_in.email):
            return None
        
        # Check if username is taken
        if await self.get_by_username(user_in.username):
            return None
        
        # Hash password
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        
        # Insert new user
        result = await self.collection.insert_one(user_data)
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return self._convert_to_response(created_user)

    @staticmethod
    async def update_user(user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        # Check if user exists
        existing_user = await UserRepository.get(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # If email is being updated, check if it's already in use
        if user_update.email and user_update.email != existing_user.email:
            email_exists = await UserRepository.get_by_email(user_update.email)
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # If username is being updated, check if it's already in use
        if user_update.username and user_update.username != existing_user.username:
            username_exists = await UserRepository.get_by_username(user_update.username)
            if username_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        return await UserRepository.update(user_id, user_update)

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        # Check if user exists
        existing_user = await UserRepository.get(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return await UserRepository.delete(user_id)

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
        user = await UserRepository.authenticate(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    def create_access_token_for_user(user: UserInDB) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token

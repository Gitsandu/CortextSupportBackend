from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr = Field(
        ...,
        description="The email address of the user",
        json_schema_extra={"example": "user@example.com"}
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="A unique username for the user",
        json_schema_extra={"example": "johndoe"}
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="The full name of the user",
        json_schema_extra={"example": "John Doe"}
    )
    role: UserRole = Field(
        default=UserRole.USER,
        description="The role of the user in the system"
    )

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="The password for the user account. Must be at least 8 characters long.",
        json_schema_extra={"example": "strongpassword123"}
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "strongpassword123"
            }
        }
    )

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(
        default=None,
        description="New email address for the user",
        json_schema_extra={"example": "new.email@example.com"}
    )
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="New username for the user",
        json_schema_extra={"example": "newusername"}
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="New full name for the user",
        json_schema_extra={"example": "New Name"}
    )
    password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=100,
        description="New password for the user. Must be at least 8 characters long.",
        json_schema_extra={"example": "newstrongpassword123"}
    )
    role: Optional[UserRole] = Field(
        default=None,
        description="New role for the user"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "new.email@example.com",
                "username": "newusername",
                "full_name": "New Name",
                "password": "newstrongpassword123",
                "role": "user"
            }
        }
    )

class UserInDB(UserBase):
    id: str = Field(..., description="The unique identifier for the user")
    disabled: bool = Field(
        default=False,
        description="Whether the user account is disabled"
    )
    is_superuser: bool = Field(
        default=False,
        description="Whether the user has superuser privileges"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the user was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the user was last updated"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "disabled": False,
                "is_superuser": False,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }
    )

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token for authentication")
    token_type: str = Field(default="bearer", description="Type of the token, typically 'bearer'")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

class UserResponse(UserBase):
    """Response model for user data (excludes sensitive information)."""
    id: str = Field(..., description="The unique identifier for the user")
    disabled: bool = Field(
        default=False,
        description="Whether the user account is disabled"
    )
    is_superuser: bool = Field(
        default=False,
        description="Whether the user has superuser privileges"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the user was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the user was last updated"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "disabled": False,
                "is_superuser": False,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }
    )


class TokenData(BaseModel):
    username: Optional[str] = Field(
        default=None,
        description="The username extracted from the JWT token"
    )
    scopes: List[str] = Field(
        default_factory=list,
        description="List of scopes/roles associated with the token"
    )

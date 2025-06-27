from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from ..base import DocumentBase

class User(DocumentBase):
    """User model for MongoDB."""
    email: EmailStr
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    disabled: bool = False
    is_superuser: bool = False
    last_login: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "disabled": False,
                "is_superuser": False
            }
        }

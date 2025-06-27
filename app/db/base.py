from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class DocumentBase(BaseModel):
    """Base model for MongoDB documents."""
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Override dict method to handle ObjectId and datetime serialization."""
        data = super().dict(*args, **kwargs)
        if '_id' in data and data['_id'] is None:
            data.pop('_id')
        if 'id' in data and data['id'] is None:
            data.pop('id')
        return data

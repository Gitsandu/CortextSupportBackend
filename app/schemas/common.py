from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number starting from 1")
    page_size: int = Field(10, ge=1, le=100, alias="pageSize", description="Number of items per page (1-100)")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "pageSize": 10,
                "totalPages": 0
            }
        }
    )
    
    items: List[T] = Field(..., description="List of items in the current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., alias="pageSize", description="Number of items per page")
    total_pages: int = Field(..., alias="totalPages", description="Total number of pages")

class ErrorResponse(BaseModel):
    """Standard error response."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "An error occurred",
                "code": "error_code",
                "errors": {"field": ["error1", "error2"]}
            }
        }
    )
    
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code for programmatic handling")
    errors: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")

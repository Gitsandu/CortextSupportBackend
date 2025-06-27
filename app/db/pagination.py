from typing import TypeVar, Type, Any, Optional, List, Dict, Union
from pymongo.collection import Collection
from pymongo import ReturnDocument
from bson import ObjectId

from ..schemas.common import PaginationParams, PaginatedResponse

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=dict)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=dict)

class CRUDPaginatedMongo:
    """
    CRUD operations with pagination support for MongoDB collections.
    """
    
    def __init__(self, collection: Collection, response_model: Type[ModelType]):
        """
        Initialize with MongoDB collection and response model.
        
        Args:
            collection: MongoDB collection instance
            response_model: Pydantic model for response serialization
        """
        self.collection = collection
        self.model = response_model
    
    async def get_multi(
        self, 
        pagination: PaginationParams,
        query: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None
    ) -> PaginatedResponse[ModelType]:
        """
        Retrieve multiple items with pagination.
        
        Args:
            pagination: Pagination parameters (page, page_size)
            query: MongoDB query filter
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            Paginated response with items and metadata
        """
        query = query or {}
        skip = (pagination.page - 1) * pagination.page_size
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Calculate total pages
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        # Apply pagination and sorting
        cursor = self.collection.find(query).skip(skip).limit(pagination.page_size)
        
        if sort:
            cursor = cursor.sort(sort)
        
        # Convert to model instances
        items = [self.model(**item) for item in await cursor.to_list(length=None)]
        
        return {
            "items": items,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": total_pages
        }
    
    async def get(self, id: Union[str, ObjectId]) -> Optional[ModelType]:
        """Get a single item by ID."""
        if not ObjectId.is_valid(id):
            return None
            
        item = await self.collection.find_one({"_id": ObjectId(id) if isinstance(id, str) else id})
        return self.model(**item) if item else None
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new item."""
        result = await self.collection.insert_one(obj_in)
        created = await self.collection.find_one({"_id": result.inserted_id})
        return self.model(**created)
    
    async def update(
        self, 
        id: Union[str, ObjectId], 
        obj_in: UpdateSchemaType,
        return_updated: bool = True
    ) -> Optional[ModelType]:
        """Update an existing item."""
        if not ObjectId.is_valid(id):
            return None
            
        # Remove None values to prevent overriding with None
        update_data = {k: v for k, v in obj_in.dict().items() if v is not None}
        
        if not update_data:
            return await self.get(id)
            
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(id) if isinstance(id, str) else id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER if return_updated else ReturnDocument.BEFORE
        )
        
        return self.model(**result) if result else None
    
    async def delete(self, id: Union[str, ObjectId]) -> bool:
        """Delete an item by ID."""
        if not ObjectId.is_valid(id):
            return False
            
        result = await self.collection.delete_one({"_id": ObjectId(id) if isinstance(id, str) else id})
        return result.deleted_count > 0

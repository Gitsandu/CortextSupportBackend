from typing import Optional, List
from bson import ObjectId
from ..db.session import get_database
from ..db.models.user import User
from ..schemas.user import UserInDB, UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password

class UserRepository:
    COLLECTION_NAME = "users"

    @classmethod
    async def get_collection(cls):
        db = await get_database()
        return db[cls.COLLECTION_NAME]

    @classmethod
    async def get(cls, user_id: str) -> Optional[UserInDB]:
        collection = await cls.get_collection()
        user = await collection.find_one({"_id": ObjectId(user_id)})
        return UserInDB(**user) if user else None

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[UserInDB]:
        collection = await cls.get_collection()
        user = await collection.find_one({"email": email})
        return UserInDB(**user) if user else None

    @classmethod
    async def get_by_username(cls, username: str) -> Optional[UserInDB]:
        collection = await cls.get_collection()
        user = await collection.find_one({"username": username})
        return UserInDB(**user) if user else None

    @classmethod
    async def create(cls, user: UserCreate) -> UserInDB:
        collection = await cls.get_collection()
        hashed_password = get_password_hash(user.password)
        user_dict = user.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        
        result = await collection.insert_one(user_dict)
        created_user = await collection.find_one({"_id": result.inserted_id})
        return UserInDB(**created_user)

    @classmethod
    async def update(cls, user_id: str, user: UserUpdate) -> Optional[UserInDB]:
        collection = await cls.get_collection()
        update_data = user.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        if not update_data:
            return await cls.get(user_id)
            
        await collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return await cls.get(user_id)

    @classmethod
    async def delete(cls, user_id: str) -> bool:
        collection = await cls.get_collection()
        result = await collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @classmethod
    async def authenticate(cls, username: str, password: str) -> Optional[UserInDB]:
        user = await cls.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

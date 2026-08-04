# backend/app/repositories/base.py
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel
from bson import ObjectId

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: Type[ModelType]):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]
        self.model_class = model_class

    async def create(self, data: Dict[str, Any]) -> ModelType:
        result = await self.collection.insert_one(data)
        created = await self.get_by_id(str(result.inserted_id))
        return created

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        if not ObjectId.is_valid(id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(id)})
        if doc:
            return self.model_class(**doc)
        return None

    async def get_one(self, filter: Dict[str, Any]) -> Optional[ModelType]:
        doc = await self.collection.find_one(filter)
        if doc:
            return self.model_class(**doc)
        return None

    async def get_many(self, filter: Dict[str, Any], limit: int = 100, skip: int = 0) -> List[ModelType]:
        cursor = self.collection.find(filter).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self.model_class(**doc) for doc in docs]

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[ModelType]:
        if not ObjectId.is_valid(id):
            return None
        # Remove _id if present
        data.pop("_id", None)
        result = await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data, "$currentDate": {"updated_at": True}},
        )
        if result.modified_count:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
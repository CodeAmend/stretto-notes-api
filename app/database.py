# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from bson import ObjectId

# MongoDB client
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

# Collections
users_collection = db[settings.USER_COLLECTION]
sessions_collection = db[settings.SESSION_COLLECTION]
practice_collection = db[settings.PRACTICE_COLLECTION]
journeys_collection = db[settings.JOURNEY_COLLECTION]

# Helper class for ObjectId handling
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema

        def validate_object_id(v, info):
            if isinstance(v, ObjectId):
                return v
            if isinstance(v, str) and ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId")

        return core_schema.with_info_plain_validator_function(
            validate_object_id,
            serialization=core_schema.to_string_ser_schema()
        )

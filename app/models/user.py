# app/models/user.py

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: Optional[str] = Field(default=None, alias="_id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_admin: Optional[bool] = False
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v: Any) -> Optional[str]:
        """Convert ObjectId to string"""
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
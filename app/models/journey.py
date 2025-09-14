# app/models/journey.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.database import PyObjectId

class JourneyBase(BaseModel):
    title: str
    practice_item_ids: List[str] = []
    goal: Optional[str] = None

class JourneyCreate(JourneyBase):
    pass

class JourneyUpdate(BaseModel):
    title: Optional[str] = None
    practice_item_ids: Optional[List[str]] = None
    goal: Optional[str] = None

class Journey(JourneyBase):
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

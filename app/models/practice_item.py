# app/models/practice_item.py

from pydantic import BaseModel, Field
from typing import Optional, List
from app.database import PyObjectId

class PracticeItemBase(BaseModel):
    title: str
    composer: Optional[str] = None
    genre: Optional[str] = None
    tags: List[str] = []

class PracticeItemCreate(PracticeItemBase):
    pass

class PracticeItem(PracticeItemBase):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

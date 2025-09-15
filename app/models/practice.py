# app/models/practice.py

from pydantic import BaseModel, Field
from typing import Optional, List
from app.database import PyObjectId

class PracticeBase(BaseModel):
    title: str
    composer: Optional[str] = None
    subject_type: Optional[str] = None

class PracticeCreate(PracticeBase):
    pass

class Practice(PracticeBase):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

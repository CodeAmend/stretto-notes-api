# app/models/session.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.database import PyObjectId

class SessionBase(BaseModel):
    subject_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    insights: List[Dict[str, Any]] = []
    ai_suggestions: List[Dict[str, Any]] = []
    insight_counts: Dict[str, int] = {}
    session_summary: Optional[str] = None
    session_journal: Optional[str] = None
    session_focus: Optional[str] = None
    full_transcript: Optional[str] = None
    is_active: bool = False

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    insights: Optional[List[Dict[str, Any]]] = None
    ai_suggestions: Optional[List[Dict[str, Any]]] = None
    insight_counts: Optional[Dict[str, int]] = None
    session_summary: Optional[str] = None
    session_journal: Optional[str] = None
    session_focus: Optional[str] = None
    full_transcript: Optional[str] = None
    is_active: Optional[bool] = None

class Session(SessionBase):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

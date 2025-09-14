# app/routers/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from app.auth import get_current_user
from app.database import sessions_collection
from app.models.user import User
from app.models.session import Session, SessionCreate, SessionUpdate

router = APIRouter()

@router.get("/", response_model=List[Session])
async def get_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all sessions for current user."""
    sessions = await sessions_collection.find(
        {"user_id": str(current_user.id)}
    ).skip(skip).limit(limit).to_list(limit)
    return sessions

@router.post("/", response_model=Session)
async def create_session(
    session: SessionCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new session."""
    session_dict = session.dict()
    session_dict["user_id"] = str(current_user.id)
    result = await sessions_collection.insert_one(session_dict)
    created_session = await sessions_collection.find_one({"_id": result.inserted_id})
    return Session.model_validate(created_session)

@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific session."""
    if not ObjectId.is_valid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    session = await sessions_collection.find_one({
        "_id": ObjectId(session_id),
        "user_id": str(current_user.id)
    })
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return Session(**session)

@router.put("/{session_id}", response_model=Session)
async def update_session(
    session_id: str,
    session_update: SessionUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a session."""
    if not ObjectId.is_valid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Remove None values
    update_data = {k: v for k, v in session_update.dict().items() if v is not None}
    
    if update_data:
        result = await sessions_collection.update_one(
            {"_id": ObjectId(session_id), "user_id": str(current_user.id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
    
    updated_session = await sessions_collection.find_one({"_id": ObjectId(session_id)})
    return Session.model_validate(updated_session)

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a session."""
    if not ObjectId.is_valid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    result = await sessions_collection.delete_one({
        "_id": ObjectId(session_id),
        "user_id": str(current_user.id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}

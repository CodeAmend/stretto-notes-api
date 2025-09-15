# app/routers/practice.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from app.auth import get_current_user
from app.database import practice_collection
from app.models.user import User
from app.models.practice import Practice, PracticeCreate

router = APIRouter()

@router.get("/", response_model=List[Practice])
async def get_practice(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all practice for current user."""
    practices = await practice_collection.find(
        {"user_id": str(current_user.id)}
    ).skip(skip).limit(limit).to_list(limit)
    return practices

@router.post("/", response_model=Practice)
async def create_practice(
    practice: PracticeCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new practice."""
    practice_dict = practice.dict()
    practice_dict["user_id"] = str(current_user.id)
    result = await practice_collection.insert_one(practice_dict)
    created_practice = await practice_collection.find_one({"_id": result.inserted_id})
    return Practice.model_validate(created_practice)

@router.get("/{practice_id}", response_model=Practice)
async def get_practice_by_id(
    practice_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific practice."""
    if not ObjectId.is_valid(practice_id):
        raise HTTPException(status_code=400, detail="Invalid practice ID")

    practice = await practice_collection.find_one({
        "_id": ObjectId(practice_id),
        "user_id": str(current_user.id)
    })
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    return Practice(**practice)

@router.delete("/{practice_id}")
async def delete_practice(
    practice_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a practice."""
    if not ObjectId.is_valid(practice_id):
        raise HTTPException(status_code=400, detail="Invalid practice ID")

    result = await practice_collection.delete_one({
        "_id": ObjectId(practice_id),
        "user_id": str(current_user.id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    return {"message": "Practice deleted successfully"}


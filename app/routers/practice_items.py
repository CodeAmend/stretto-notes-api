# app/routers/practice_items.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from app.auth import get_current_user
from app.database import practice_items_collection
from app.models.user import User
from app.models.practice_item import PracticeItem, PracticeItemCreate

router = APIRouter()

@router.get("/", response_model=List[PracticeItem])
async def get_practice_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all practice items for current user."""
    items = await practice_items_collection.find(
        {"user_id": str(current_user.id)}
    ).skip(skip).limit(limit).to_list(limit)
    return items

@router.post("/", response_model=PracticeItem)
async def create_practice_item(
    item: PracticeItemCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new practice item."""
    item_dict = item.dict()
    item_dict["user_id"] = str(current_user.id)
    result = await practice_items_collection.insert_one(item_dict)
    created_item = await practice_items_collection.find_one({"_id": result.inserted_id})
    return PracticeItem.model_validate(created_item)

@router.get("/{item_id}", response_model=PracticeItem)
async def get_practice_item(
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific practice item."""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")
    
    item = await practice_items_collection.find_one({
        "_id": ObjectId(item_id),
        "user_id": str(current_user.id)
    })
    if not item:
        raise HTTPException(status_code=404, detail="Practice item not found")
    return PracticeItem(**item)

@router.delete("/{item_id}")
async def delete_practice_item(
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a practice item."""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")
    
    result = await practice_items_collection.delete_one({
        "_id": ObjectId(item_id),
        "user_id": str(current_user.id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Practice item not found")
    
    return {"message": "Practice item deleted successfully"}


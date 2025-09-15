# app/routers/journeys.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from app.auth import get_current_user
from app.database import journeys_collection
from app.models.user import User
from app.models.journey import Journey, JourneyCreate, JourneyUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Journey])
async def get_journeys(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all journeys for current user."""
    journeys = await journeys_collection.find(
        {"user_id": str(current_user.id)}
    ).skip(skip).limit(limit).to_list(limit)
    return journeys

@router.post("/", response_model=Journey)
async def create_journey(
    journey: JourneyCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new journey."""
    journey_dict = journey.dict()
    journey_dict["user_id"] = str(current_user.id)
    journey_dict["created_at"] = datetime.utcnow()
    journey_dict["updated_at"] = datetime.utcnow()
    result = await journeys_collection.insert_one(journey_dict)
    created_journey = await journeys_collection.find_one({"_id": result.inserted_id})
    return Journey.model_validate(created_journey)

@router.get("/{journey_id}", response_model=Journey)
async def get_journey(
    journey_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific journey."""
    if not ObjectId.is_valid(journey_id):
        raise HTTPException(status_code=400, detail="Invalid journey ID")
    
    journey = await journeys_collection.find_one({
        "_id": ObjectId(journey_id),
        "user_id": str(current_user.id)
    })
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return Journey(**journey)

@router.put("/{journey_id}", response_model=Journey)
async def update_journey(
    journey_id: str,
    journey_update: JourneyUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a journey."""
    if not ObjectId.is_valid(journey_id):
        raise HTTPException(status_code=400, detail="Invalid journey ID")
    
    # Remove None values
    update_data = {k: v for k, v in journey_update.dict().items() if v is not None}
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        result = await journeys_collection.update_one(
            {"_id": ObjectId(journey_id), "user_id": str(current_user.id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Journey not found")
    
    updated_journey = await journeys_collection.find_one({"_id": ObjectId(journey_id)})
    return Journey.model_validate(updated_journey)

@router.delete("/{journey_id}")
async def delete_journey(
    journey_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a journey."""
    if not ObjectId.is_valid(journey_id):
        raise HTTPException(status_code=400, detail="Invalid journey ID")
    
    result = await journeys_collection.delete_one({
        "_id": ObjectId(journey_id),
        "user_id": str(current_user.id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    return {"message": "Journey deleted successfully"}

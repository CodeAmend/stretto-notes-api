# app/routers/auth.py
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from app.database import users_collection
from app.models.user import User, UserCreate, Token
from app.config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register a new user."""
    try:
        # Log registration attempt
        logger.info(f"Registration attempt for email: {user.email}")
        
        # Check if user exists
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"Registration failed - email already exists: {user.email}")
            raise HTTPException(
                status_code=400, 
                detail=f"Email {user.email} is already registered"
            )
        
        # Create new user
        user_dict = user.model_dump()
        user_dict["password"] = get_password_hash(user_dict["password"])
        user_dict["created_at"] = datetime.utcnow()
        user_dict["is_admin"] = False  # Default to non-admin
        
        # Insert into database
        result = await users_collection.insert_one(user_dict)
        
        # Retrieve the created user WITHOUT the password field
        created_user = await users_collection.find_one(
            {"_id": result.inserted_id},
            {"password": 0}  # Exclude password field from response
        )
        
        if not created_user:
            logger.error(f"Failed to retrieve created user for email: {user.email}")
            raise HTTPException(
                status_code=500,
                detail="User was created but could not be retrieved"
            )
        
        logger.info(f"Successfully registered user: {user.email}")
        logger.debug(f"Created user data: {created_user}")
        
        # Convert MongoDB document to User model
        # Make sure _id is properly handled
        if "_id" in created_user:
            created_user["id"] = str(created_user["_id"])
        
        return User(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    try:
        logger.info(f"Login attempt for username: {form_data.username}")
        
        # Authenticate user
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Login failed - invalid credentials for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.get("/health")
async def health_check():
    """Health check endpoint to verify API and database connectivity."""
    try:
        # Check database connection
        await users_collection.find_one({})
        return {
            "status": "healthy",
            "service": "StrettoNotes API",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )
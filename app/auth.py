# app/auth.py

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import settings
from app.database import users_collection
from app.models.user import User, TokenData
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

async def get_user(email: str) -> Optional[User]:
    """Get user by email (without password)."""
    try:
        # Exclude password field when fetching user
        user = await users_collection.find_one(
            {"email": email},
            {"password": 0}  # Exclude password from result
        )
        if user:
            # Ensure _id is converted to string for the id field
            if "_id" in user:
                user["id"] = str(user["_id"])
            return User(**user)
        return None
    except Exception as e:
        logger.error(f"Error getting user {email}: {str(e)}")
        return None

async def authenticate_user(email: str, password: str):
    """Authenticate user with email and password."""
    try:
        # Get user WITH password for authentication only
        user_with_password = await users_collection.find_one({"email": email})
        if not user_with_password:
            logger.warning(f"User not found: {email}")
            return False
        
        if not verify_password(password, user_with_password["password"]):
            logger.warning(f"Invalid password for user: {email}")
            return False
        
        # Return user WITHOUT password
        user_dict = {k: v for k, v in user_with_password.items() if k != "password"}
        if "_id" in user_dict:
            user_dict["id"] = str(user_dict["_id"])
        
        return User(**user_dict)
    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            logger.error("No email in token payload")
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
    
    if token_data.email is None:
        raise credentials_exception
    
    user = await get_user(email=token_data.email)
    if user is None:
        logger.error(f"User not found for token: {token_data.email}")
        raise credentials_exception
    
    return user
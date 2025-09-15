# debug_registration.py
"""
Debug script to test user registration locally
Run: python debug_registration.py
"""

import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv
import json
from bson import ObjectId

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def json_encoder(obj):
    """JSON encoder for MongoDB ObjectId and datetime"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

async def test_registration():
    """Test the registration process step by step"""
    
    # Import settings for consistent configuration
    from app.config import settings

    print("🔍 Testing User Registration Process")
    print("=" * 50)

    # Connect to MongoDB
    print(f"\n1. Connecting to MongoDB...")
    print(f"   URL: {settings.MONGODB_URL[:30]}...")
    print(f"   Database: {settings.DATABASE_NAME}")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    users_collection = db[settings.USER_COLLECTION]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("   ✅ Connected successfully")
        
        # Create test user data
        test_email = f"test_{datetime.now().timestamp()}@example.com"
        user_data = {
            "email": test_email,
            "password": pwd_context.hash("testpassword123"),
            "full_name": "Test User",
            "created_at": datetime.utcnow(),
            "is_admin": False
        }
        
        print(f"\n2. Creating user: {test_email}")
        print(f"   User data (without password hash):")
        display_data = {k: v for k, v in user_data.items() if k != "password"}
        print(f"   {json.dumps(display_data, default=json_encoder, indent=2)}")
        
        # Insert user
        result = await users_collection.insert_one(user_data)
        print(f"   ✅ User inserted with ID: {result.inserted_id}")
        
        # Retrieve user WITH password (like in authentication)
        print(f"\n3. Retrieving user WITH password (for auth check)...")
        user_with_password = await users_collection.find_one({"_id": result.inserted_id})
        if user_with_password:
            print(f"   ✅ Found user, has password: {'password' in user_with_password}")
        else:
            print(f"   ❌ User not found")
            return

        # Retrieve user WITHOUT password (for response)
        print(f"\n4. Retrieving user WITHOUT password (for API response)...")
        user_without_password = await users_collection.find_one(
            {"_id": result.inserted_id},
            {"password": 0}
        )

        if user_without_password:
            print(f"   Retrieved data:")
            print(f"   {json.dumps(user_without_password, default=json_encoder, indent=2)}")

            # Test field conversion
            print(f"\n5. Testing field conversion for Pydantic...")
            if "_id" in user_without_password:
                user_without_password["id"] = str(user_without_password["_id"])
                print(f"   ✅ Converted _id to id: {user_without_password['id']}")
        else:
            print(f"   ❌ User not found")
            return
        
        # Try to create a User model (simulating what the API does)
        print(f"\n6. Simulating Pydantic User model creation...")
        try:
            from app.models.user import User
            if user_without_password:
                user_model = User(**user_without_password)
                print(f"   ✅ User model created successfully")
                print(f"   Model data: {user_model.model_dump()}")
        except ImportError:
            print("   ⚠️  Cannot import User model (run from project root)")
        except Exception as e:
            print(f"   ❌ Error creating User model: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
        
        # Clean up - delete test user
        print(f"\n7. Cleaning up...")
        await users_collection.delete_one({"_id": result.inserted_id})
        print(f"   ✅ Test user deleted")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\n✅ Test complete")

if __name__ == "__main__":
    asyncio.run(test_registration())
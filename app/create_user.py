# create_user.py
"""
Command-line script to create users for StrettoNotes API
Usage: python create_user.py
"""

import asyncio
import getpass
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    """Interactive user creation"""

    # Import settings for consistent configuration
    from app.config import settings

    print("🎵 StrettoNotes User Creation Tool")
    print("-" * 40)

    # Connect to MongoDB
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    users_collection = db[settings.USER_COLLECTION]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB\n")
        
        # Get user count
        user_count = await users_collection.count_documents({})
        print(f"Current number of users: {user_count}\n")
        
        # Get user input
        email = input("Enter email address: ").strip()
        
        # Check if user exists
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return
        
        full_name = input("Enter full name: ").strip()
        
        # Get password with confirmation
        while True:
            password = getpass.getpass("Enter password: ")
            password_confirm = getpass.getpass("Confirm password: ")
            
            if password != password_confirm:
                print("❌ Passwords don't match. Try again.\n")
            elif len(password) < 6:
                print("❌ Password must be at least 6 characters.\n")
            else:
                break
        
        # Ask if admin
        is_admin = input("Is this an admin user? (y/N): ").strip().lower() == 'y'
        
        # Create user
        user_dict = {
            "email": email,
            "password": pwd_context.hash(password),
            "full_name": full_name,
            "is_admin": is_admin,
            "created_at": datetime.utcnow()
        }
        
        print(f"\nCreating user: {email}...")
        result = await users_collection.insert_one(user_dict)
        
        if result.inserted_id:
            print(f"✅ User created successfully!")
            print(f"   Email: {email}")
            print(f"   Name: {full_name}")
            print(f"   Admin: {'Yes' if is_admin else 'No'}")
            print(f"   ID: {result.inserted_id}")
        else:
            print("❌ Failed to create user")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

async def list_users():
    """List all users"""

    # Import settings for consistent configuration
    from app.config import settings

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    users_collection = db[settings.USER_COLLECTION]
    
    try:
        users = await users_collection.find({}).to_list(None)
        
        print("\n📋 Registered Users:")
        print("-" * 60)
        
        if not users:
            print("No users found.")
        else:
            for user in users:
                admin_badge = "👑" if user.get("is_admin") else "  "
                print(f"{admin_badge} {user['email']:<30} {user.get('full_name', 'N/A')}")
        
        print(f"\nTotal users: {len(users)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

async def main():
    """Main menu"""
    
    print("\n🎵 StrettoNotes User Management")
    print("1. Create new user")
    print("2. List all users")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        await create_user()
    elif choice == "2":
        await list_users()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid option")

if __name__ == "__main__":
    asyncio.run(main())
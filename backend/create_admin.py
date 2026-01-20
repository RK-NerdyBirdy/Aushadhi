#!/usr/bin/env python3
"""
Create a superuser admin account
"""
import os
from dotenv import load_dotenv
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.database import Base
from app.models.user import User
from app.core.security import get_password_hash

# Load environment variables
load_dotenv()

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin():
    """Create a superuser admin account"""
    db = SessionLocal()
    
    try:
        # Admin details
        admin_email = "admin@gmail.com"
        admin_password = "admin@123"  # Change this to a secure password
        admin_name = "System Administrator"
        hospital_id = "HOSP001"  # Special hospital ID for admin
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.user_email == admin_email).first()
        if existing_admin:
            print(f"❌ Admin user with email {admin_email} already exists!")
            return
        
        # Create admin user
        admin_user = User(
            user_id=str(uuid.uuid4()),
            hospital_id=hospital_id,
            user_name=admin_name,
            user_email=admin_email,
            hashed_password=get_password_hash(admin_password),
            user_role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   User ID: {admin_user.user_id}")
        print(f"\n⚠️  IMPORTANT: Change this password immediately in production!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating superuser admin account...\n")
    create_admin()

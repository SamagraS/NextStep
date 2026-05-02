import asyncio
import json
import os
import sys

# Add backend to sys.path to allow imports
sys.path.append(os.path.abspath("backend"))

from app.core.config import get_settings
from app.db.database import Database
from app.services.auth import AuthService
from app.services.persistence import PersistenceService
from jose import jwt

async def test_auth():
    print("--- Starting Auth Verification ---")
    settings = get_settings()
    # Use a temporary DB for testing or the actual one
    database = Database(settings.database_url)
    await database.initialize()
    
    auth_service = AuthService(settings)
    persistence = PersistenceService(database)
    
    # 1. Seed users
    print("Seeding demo users...")
    await persistence.seed_demo_users(auth_service)
    
    # 2. Test Success Login (Student)
    print("Testing Student Login...")
    user = await persistence.get_user_by_email("priya@example.com")
    assert user is not None
    assert user["role"] == "student"
    assert auth_service.verify_password("password123", user["password_hash"])
    
    token_data = {"sub": user["email"], "role": user["role"]}
    token = auth_service.create_access_token(token_data)
    decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert decoded["sub"] == "priya@example.com"
    assert decoded["role"] == "student"
    print("Student Login OK.")
    
    # 3. Test Success Login (Underwriter)
    print("Testing Underwriter Login...")
    user_uw = await persistence.get_user_by_email("underwriter@nextstep.com")
    assert user_uw is not None
    assert user_uw["role"] == "underwriter"
    assert auth_service.verify_password("uwpass", user_uw["password_hash"])
    print("Underwriter Login OK.")
    
    # 4. Test Success Login (Portfolio Manager)
    print("Testing Portfolio Manager Login...")
    user_pm = await persistence.get_user_by_email("manager@nextstep.com")
    assert user_pm is not None
    assert user_pm["role"] == "portfolio_manager"
    assert auth_service.verify_password("pmpass", user_pm["password_hash"])
    print("Portfolio Manager Login OK.")
    
    # 5. Test Invalid Password
    print("Testing Invalid Password...")
    assert not auth_service.verify_password("wrongpass", user["password_hash"])
    print("Invalid Password Detection OK.")
    
    # 6. Test Non-existent User
    print("Testing Non-existent User...")
    non_user = await persistence.get_user_by_email("none@example.com")
    assert non_user is None
    print("Non-existent User Detection OK.")
    
    await database.close()
    print("--- Auth Verification Complete: ALL PASSED ---")

if __name__ == "__main__":
    asyncio.run(test_auth())

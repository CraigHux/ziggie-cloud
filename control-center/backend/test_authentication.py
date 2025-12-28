"""
Authentication System Test Script
Tests the JWT authentication implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.db import init_db, AsyncSessionLocal
from database.models import User
from middleware.auth import hash_password, verify_password, create_access_token, decode_access_token
from config import settings
from sqlalchemy import select


async def test_password_hashing():
    """Test password hashing and verification."""
    print("\n=== Testing Password Hashing ===")

    password = "testpassword123"

    # Hash password
    hashed = hash_password(password)
    print(f"✓ Password hashed successfully")
    print(f"  Original: {password}")
    print(f"  Hashed: {hashed[:50]}...")

    # Verify correct password
    assert verify_password(password, hashed), "Password verification failed!"
    print(f"✓ Correct password verified successfully")

    # Verify incorrect password
    assert not verify_password("wrongpassword", hashed), "Wrong password should not verify!"
    print(f"✓ Incorrect password rejected successfully")


async def test_jwt_tokens():
    """Test JWT token creation and verification."""
    print("\n=== Testing JWT Tokens ===")

    # Create token
    token_data = {
        "sub": "testuser",
        "user_id": 1,
        "role": "user"
    }

    token = create_access_token(token_data)
    print(f"✓ JWT token created successfully")
    print(f"  Token: {token[:50]}...")

    # Decode token
    decoded = decode_access_token(token)
    print(f"✓ JWT token decoded successfully")
    print(f"  Username: {decoded['sub']}")
    print(f"  User ID: {decoded['user_id']}")
    print(f"  Role: {decoded['role']}")
    print(f"  Expires: {decoded['exp']}")

    # Verify token data
    assert decoded["sub"] == "testuser", "Username mismatch!"
    assert decoded["user_id"] == 1, "User ID mismatch!"
    assert decoded["role"] == "user", "Role mismatch!"
    print(f"✓ Token data verified successfully")


async def test_database_user():
    """Test user creation and database operations."""
    print("\n=== Testing Database User Operations ===")

    # Initialize database
    await init_db()
    print(f"✓ Database initialized")

    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        result = await session.execute(
            select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
        )
        admin = result.scalar_one_or_none()

        if admin:
            print(f"✓ Default admin user found")
            print(f"  Username: {admin.username}")
            print(f"  Role: {admin.role}")
            print(f"  Active: {admin.is_active}")
            print(f"  Created: {admin.created_at}")

            # Verify admin password
            is_valid = verify_password(settings.DEFAULT_ADMIN_PASSWORD, admin.hashed_password)
            if is_valid:
                print(f"✓ Admin password verified successfully")
            else:
                print(f"✗ Admin password verification failed!")
        else:
            print(f"✗ Default admin user not found!")

        # Create test user
        test_user = User(
            username="testuser",
            hashed_password=hash_password("testpass123"),
            email="test@example.com",
            full_name="Test User",
            role="user",
            is_active=True
        )

        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

        print(f"✓ Test user created successfully")
        print(f"  ID: {test_user.id}")
        print(f"  Username: {test_user.username}")
        print(f"  Email: {test_user.email}")

        # Fetch user
        result = await session.execute(
            select(User).where(User.username == "testuser")
        )
        fetched_user = result.scalar_one_or_none()

        assert fetched_user is not None, "User not found in database!"
        print(f"✓ User fetched from database successfully")

        # Clean up test user
        await session.delete(test_user)
        await session.commit()
        print(f"✓ Test user cleaned up")


async def test_role_hierarchy():
    """Test role-based access control."""
    print("\n=== Testing Role-Based Access Control ===")

    roles = ["admin", "user", "readonly"]

    for role in roles:
        token = create_access_token({
            "sub": f"test_{role}",
            "user_id": 1,
            "role": role
        })

        decoded = decode_access_token(token)
        print(f"✓ {role.upper()} role token created and verified")
        assert decoded["role"] == role, f"Role mismatch for {role}!"


async def run_all_tests():
    """Run all authentication tests."""
    print("=" * 60)
    print("AUTHENTICATION SYSTEM TEST SUITE")
    print("=" * 60)

    try:
        # Test password hashing
        await test_password_hashing()

        # Test JWT tokens
        await test_jwt_tokens()

        # Test role hierarchy
        await test_role_hierarchy()

        # Test database operations
        await test_database_user()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nAuthentication system is working correctly!")
        print("\nNext steps:")
        print("1. Start the server: python main.py")
        print("2. Login with default credentials:")
        print(f"   Username: {settings.DEFAULT_ADMIN_USERNAME}")
        print(f"   Password: {settings.DEFAULT_ADMIN_PASSWORD}")
        print("3. Change the default admin password immediately!")

    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        sys.exit(1)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_all_tests())

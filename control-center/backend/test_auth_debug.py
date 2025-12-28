"""
Debug script to test JWT authentication flow
"""
import asyncio
import jwt
from datetime import datetime, timedelta
from sqlalchemy import select
from config import settings
from database import get_db, User
from middleware.auth import create_access_token, decode_access_token

async def test_auth_flow():
    """Test the complete authentication flow"""

    print("=" * 80)
    print("JWT AUTHENTICATION FLOW DEBUG")
    print("=" * 80)

    # Test 1: Token creation
    print("\n1. Testing Token Creation")
    print("-" * 80)
    test_data = {
        "sub": "admin",
        "user_id": 1,
        "role": "admin"
    }

    token = create_access_token(test_data)
    print(f"[OK] Token created successfully")
    print(f"Token (first 50 chars): {token[:50]}...")

    # Test 2: Token decoding
    print("\n2. Testing Token Decoding")
    print("-" * 80)
    try:
        payload = decode_access_token(token)
        print(f"[OK] Token decoded successfully")
        print(f"Payload: {payload}")
    except Exception as e:
        print(f"[FAIL] Token decode failed: {e}")
        return

    # Test 3: Check database connection and user lookup
    print("\n3. Testing Database Connection & User Lookup")
    print("-" * 80)
    async for db in get_db():
        try:
            username = payload.get("sub")
            user_id = payload.get("user_id")

            print(f"Looking for user: username='{username}', user_id={user_id}")

            # First, check if user exists by ID only
            result = await db.execute(select(User).where(User.id == user_id))
            user_by_id = result.scalar_one_or_none()

            if user_by_id:
                print(f"[OK] User found by ID: {user_by_id.id}, {user_by_id.username}, is_active={user_by_id.is_active}")
            else:
                print(f"[FAIL] No user found with ID={user_id}")

            # Now check with both conditions (as in get_current_user)
            result = await db.execute(
                select(User).where(User.id == user_id, User.username == username)
            )
            user = result.scalar_one_or_none()

            if user:
                print(f"[OK] User found with both conditions: {user.id}, {user.username}, is_active={user.is_active}")

                # Check is_active
                if not user.is_active:
                    print(f"[FAIL] User account is INACTIVE - this would cause 403 Forbidden")
                else:
                    print(f"[OK] User account is ACTIVE")
            else:
                print(f"[FAIL] No user found with both ID={user_id} AND username='{username}'")

                # Let's check if username exists but with different ID
                result = await db.execute(select(User).where(User.username == username))
                user_by_name = result.scalar_one_or_none()
                if user_by_name:
                    print(f"  -> User '{username}' exists but with ID={user_by_name.id} (token has ID={user_id})")
                    print(f"  -> This is the problem! Token user_id doesn't match database user.id")

        except Exception as e:
            print(f"[FAIL] Database query failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break

    # Test 4: Manual JWT decode to see raw payload
    print("\n4. Raw JWT Decode (without verification)")
    print("-" * 80)
    try:
        raw_payload = jwt.decode(token, options={"verify_signature": False})
        print(f"Raw payload: {raw_payload}")
        print(f"  - sub: {raw_payload.get('sub')}")
        print(f"  - user_id: {raw_payload.get('user_id')}")
        print(f"  - role: {raw_payload.get('role')}")
        print(f"  - exp: {raw_payload.get('exp')} ({datetime.fromtimestamp(raw_payload.get('exp'))})")
        print(f"  - iat: {raw_payload.get('iat')} ({datetime.fromtimestamp(raw_payload.get('iat'))})")
    except Exception as e:
        print(f"[FAIL] Raw decode failed: {e}")

    # Test 5: Check JWT settings
    print("\n5. JWT Configuration")
    print("-" * 80)
    print(f"JWT_SECRET: {'*' * 20} (length: {len(settings.JWT_SECRET)})")
    print(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"JWT_EXPIRATION_HOURS: {settings.JWT_EXPIRATION_HOURS}")

    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_auth_flow())

"""Reset admin password to admin123"""
import asyncio
import sys
from sqlalchemy import select
from database import AsyncSessionLocal
from database.models import User
from middleware.auth import hash_password

async def reset_admin_password():
    """Reset the admin user's password to 'admin123'"""
    async with AsyncSessionLocal() as session:
        # Find admin user
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            print("ERROR: Admin user not found")
            return False

        # Reset password
        new_password = "admin123"
        admin_user.hashed_password = hash_password(new_password)
        await session.commit()

        print(f"SUCCESS: Admin password reset to '{new_password}'")
        return True

if __name__ == "__main__":
    result = asyncio.run(reset_admin_password())
    sys.exit(0 if result else 1)

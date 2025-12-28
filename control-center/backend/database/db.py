"""Database initialization and session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select
from database.models import Base, User
from config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.DEBUG
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables and create default admin user and services."""
    # Import here to avoid circular dependency
    from middleware.auth import hash_password
    from database.models import Service

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create default admin user if it doesn't exist
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print(f"Default admin user created: {settings.DEFAULT_ADMIN_USERNAME}")
        else:
            print(f"Admin user already exists: {settings.DEFAULT_ADMIN_USERNAME}")

    # Seed default services
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Service))
        existing_services = result.scalars().all()

        if not existing_services:
            # Define default services
            default_services = [
                Service(
                    name="control-center-backend",
                    description="Control Center Backend API",
                    command="python main.py",
                    cwd=str(settings.BASE_DIR),
                    port=settings.PORT,
                    is_system=True,
                    status="stopped",
                    health="unknown"
                ),
                Service(
                    name="control-center-frontend",
                    description="Control Center Frontend (React)",
                    command="npm run dev",
                    cwd=str(settings.BASE_DIR.parent / "frontend"),
                    port=3000,
                    is_system=True,
                    status="stopped",
                    health="unknown"
                ),
                Service(
                    name="comfyui",
                    description="ComfyUI Image Generation Service",
                    command=str(settings.COMFYUI_PYTHON_PATH) + " main.py --windows-standalone-build --cpu",
                    cwd=str(settings.COMFYUI_DIR),
                    port=8188,
                    is_system=False,
                    status="stopped",
                    health="unknown"
                ),
                Service(
                    name="kb-scheduler",
                    description="Knowledge Base Scheduler",
                    command="python manage.py schedule",
                    cwd=str(settings.KB_SCHEDULER_PATH),
                    port=None,
                    is_system=False,
                    status="stopped",
                    health="unknown"
                ),
            ]

            for service in default_services:
                session.add(service)

            await session.commit()
            print(f"Default services seeded: {len(default_services)} services added")
        else:
            print(f"Services already exist in database: {len(existing_services)} services found")


async def get_db():
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

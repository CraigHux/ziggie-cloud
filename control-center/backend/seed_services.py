"""Seed initial services into the database."""
import asyncio
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from config import settings
from database.models import Base, Service


async def seed_services():
    """Seed initial services into the database."""
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Define default services
        default_services = [
            {
                "name": "control-center-backend",
                "description": "Control Center Backend API",
                "command": "python main.py",
                "cwd": str(settings.BASE_DIR),
                "port": settings.PORT,
                "is_system": True,
            },
            {
                "name": "control-center-frontend",
                "description": "Control Center Frontend (React)",
                "command": "npm run dev",
                "cwd": str(settings.BASE_DIR.parent / "frontend"),
                "port": 3000,
                "is_system": True,
            },
            {
                "name": "comfyui",
                "description": "ComfyUI Image Generation Service",
                "command": str(settings.COMFYUI_PYTHON_PATH) + " main.py --windows-standalone-build --cpu",
                "cwd": str(settings.COMFYUI_DIR),
                "port": 8188,
                "is_system": False,
            },
            {
                "name": "kb-scheduler",
                "description": "Knowledge Base Scheduler",
                "command": "python manage.py schedule",
                "cwd": str(settings.KB_SCHEDULER_PATH),
                "port": None,
                "is_system": False,
            },
        ]

        # Check which services already exist
        existing_services = await session.execute(select(Service))
        existing_names = {s.name for s in existing_services.scalars()}

        # Add missing services
        added_count = 0
        for service_data in default_services:
            if service_data["name"] not in existing_names:
                service = Service(
                    name=service_data["name"],
                    description=service_data["description"],
                    command=service_data["command"],
                    cwd=service_data["cwd"],
                    port=service_data["port"],
                    is_system=service_data["is_system"],
                    status="stopped",
                    health="unknown"
                )
                session.add(service)
                added_count += 1
                print(f"Added service: {service_data['name']}")
            else:
                print(f"Service already exists: {service_data['name']}")

        # Commit changes
        if added_count > 0:
            await session.commit()
            print(f"\nSeeded {added_count} new services successfully!")
        else:
            print("\nAll default services already exist in database.")

        # Display all services
        all_services = await session.execute(select(Service).order_by(Service.name))
        services = all_services.scalars().all()
        print(f"\nTotal services in database: {len(services)}")
        for service in services:
            print(f"  - {service.name}: {service.description}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_services())

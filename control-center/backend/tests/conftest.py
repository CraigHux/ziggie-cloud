"""
Pytest configuration and fixtures for Control Center Backend tests
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application"""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_system_stats():
    """Mock system statistics data"""
    return {
        "cpu": 45.2,
        "memory": 62.3,
        "disk": 78.5,
        "uptime": 86400,
        "timestamp": "2025-11-07T12:00:00"
    }


@pytest.fixture
def mock_service_data():
    """Mock service information"""
    return {
        "comfyui": {
            "name": "ComfyUI",
            "status": "running",
            "pid": 12345,
            "port": 8188,
            "uptime": 3600
        },
        "knowledge-base": {
            "name": "Knowledge Base",
            "status": "stopped",
            "pid": None,
            "port": 5000,
            "uptime": 0
        }
    }


@pytest.fixture
def mock_agent_data():
    """Mock agent information"""
    return {
        "total": 584,
        "active": 4,
        "agents": [
            {
                "id": "L1.1",
                "name": "Art Director",
                "status": "active",
                "last_run": "2025-11-07T11:30:00"
            },
            {
                "id": "L1.2",
                "name": "Character Pipeline",
                "status": "idle",
                "last_run": "2025-11-07T10:00:00"
            }
        ]
    }


@pytest.fixture
def mock_kb_data():
    """Mock knowledge base data"""
    return {
        "total_files": 7,
        "creators": 38,
        "categories": ["comfyui-workflows", "ip-adapter-knowledge", "tutorials"],
        "recent_files": [
            {
                "filename": "instasd-E2E_TEST_001-20251107.md",
                "agent": "character-pipeline",
                "created": "2025-11-07T09:00:00",
                "confidence": 95
            }
        ]
    }


@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    import sqlite3
    from tempfile import NamedTemporaryFile

    # Create temporary database
    temp_db = NamedTemporaryFile(delete=False, suffix='.db')
    conn = sqlite3.connect(temp_db.name)

    # Create test tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT,
            pid INTEGER,
            port INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT,
            last_run TEXT
        )
    """)

    conn.commit()

    yield conn

    # Cleanup
    conn.close()
    Path(temp_db.name).unlink()

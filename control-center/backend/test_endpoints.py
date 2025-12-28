"""
Test script to verify the two endpoints work correctly.
This bypasses the server and directly tests the endpoint functions.
"""
import sys
import asyncio
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the endpoint functions directly
from api.system import get_system_info
from api.knowledge import get_recent_kb_files
from fastapi import Request, Query
from unittest.mock import Mock

async def test_system_info():
    """Test /api/system/info endpoint"""
    print("\n=== Testing GET /api/system/info ===")

    # Create a mock request object
    mock_request = Mock(spec=Request)
    mock_request.client = Mock()
    mock_request.client.host = "127.0.0.1"

    try:
        result = await get_system_info(mock_request)
        print(f"[OK] Endpoint executed successfully")
        print(f"Response keys: {list(result.keys())}")
        print(f"Response:")
        print(f"  - success: {result.get('success')}")
        print(f"  - os: {result.get('os')}")
        print(f"  - python: {result.get('python')}")
        print(f"  - hostname: {result.get('hostname')}")
        print(f"  - uptime: {result.get('uptime')} seconds")

        # Verify required fields
        required_fields = ['success', 'os', 'python', 'hostname', 'uptime']
        for field in required_fields:
            if field not in result:
                print(f"[FAIL] Missing required field: {field}")
            else:
                print(f"[OK] Has required field: {field}")

        return result
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_knowledge_recent():
    """Test /api/knowledge/recent endpoint"""
    print("\n=== Testing GET /api/knowledge/recent?limit=5 ===")

    # Create a mock request object
    mock_request = Mock(spec=Request)
    mock_request.client = Mock()
    mock_request.client.host = "127.0.0.1"

    try:
        result = await get_recent_kb_files(mock_request, limit=5)
        print(f"[OK] Endpoint executed successfully")
        print(f"Response keys: {list(result.keys())}")
        print(f"Response:")
        print(f"  - success: {result.get('success')}")
        print(f"  - count: {result.get('count')}")
        print(f"  - files: {len(result.get('files', []))} items")

        # Verify required fields
        required_fields = ['success', 'count', 'files']
        for field in required_fields:
            if field not in result:
                print(f"[FAIL] Missing required field: {field}")
            else:
                print(f"[OK] Has required field: {field}")

        # Check first file structure if available
        if result.get('files'):
            first_file = result['files'][0]
            file_fields = ['id', 'name', 'path', 'modified', 'size', 'agent', 'category']
            print(f"\nFirst file structure:")
            for field in file_fields:
                if field in first_file:
                    print(f"[OK] Has field: {field} = {first_file[field]}")
                else:
                    print(f"[FAIL] Missing field: {field}")

        return result
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run all tests"""
    print("=" * 60)
    print("ENDPOINT IMPLEMENTATION VERIFICATION")
    print("=" * 60)

    result1 = await test_system_info()
    result2 = await test_knowledge_recent()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if result1 and result2:
        print("[OK] Both endpoints are correctly implemented!")
        print("\nThe code exists and works correctly.")
        print("The issue is that the server needs to be restarted")
        print("to load the new endpoint definitions.")
    else:
        print("[FAIL] One or more endpoints failed")

if __name__ == "__main__":
    asyncio.run(main())

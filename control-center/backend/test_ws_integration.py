"""
Integration test for WebSocket connectivity.
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_public_websocket():
    """Test public WebSocket at /ws"""
    uri = "ws://127.0.0.1:54112/ws"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected successfully")

            # Receive 3 messages
            for i in range(3):
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"\nMessage {i+1}:")
                print(f"  Type: {data.get('type')}")
                print(f"  Timestamp: {data.get('timestamp')}")
                print(f"  CPU: {data.get('cpu', {}).get('usage')}%")
                print(f"  Memory: {data.get('memory', {}).get('percent')}%")
                print(f"  Disk: {data.get('disk', {}).get('percent')}%")

            print("\n[OK] WebSocket test PASSED")
            return True

    except asyncio.TimeoutError:
        print("[FAIL] Timeout waiting for WebSocket message")
        return False
    except Exception as e:
        print(f"[FAIL] WebSocket error: {e}")
        return False

async def test_metrics_websocket():
    """Test metrics WebSocket at /api/system/metrics"""
    uri = "ws://127.0.0.1:54112/api/system/metrics"
    print(f"\nConnecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected successfully")

            # Receive 3 messages
            for i in range(3):
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"\nMetrics {i+1}:")
                print(f"  CPU: {data.get('cpu')}%")
                print(f"  Memory: {data.get('memory')}%")
                print(f"  Disk: {data.get('disk')}%")
                print(f"  Timestamp: {data.get('timestamp')}")

            print("\n[OK] Metrics WebSocket test PASSED")
            return True

    except asyncio.TimeoutError:
        print("[FAIL] Timeout waiting for metrics")
        return False
    except Exception as e:
        print("[FAIL] Metrics WebSocket error:", e)
        return False

async def main():
    """Run all WebSocket tests"""
    print("=" * 60)
    print("WebSocket Integration Tests")
    print("=" * 60)

    result1 = await test_public_websocket()
    result2 = await test_metrics_websocket()

    print("\n" + "=" * 60)
    print(f"Results: Public WS: {'PASS' if result1 else 'FAIL'}, Metrics WS: {'PASS' if result2 else 'FAIL'}")
    print("=" * 60)

    return result1 and result2

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

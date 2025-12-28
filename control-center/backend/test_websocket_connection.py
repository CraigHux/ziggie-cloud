"""Test WebSocket connection to verify real-time system stats."""
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Connect to WebSocket and receive a few messages."""
    # Test public WebSocket endpoint (no auth required)
    uri = "ws://127.0.0.1:54112/ws"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected successfully!")

            # Receive 5 messages
            for i in range(5):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"\n[Message {i+1}]")
                print(f"  Type: {data.get('type')}")
                print(f"  Timestamp: {data.get('timestamp')}")
                print(f"  CPU Usage: {data.get('cpu', {}).get('usage')}%")
                print(f"  Memory: {data.get('memory', {}).get('percent')}%")
                print(f"  Disk: {data.get('disk', {}).get('percent')}%")

                if i < 4:
                    await asyncio.sleep(0.5)

            print("\n[OK] WebSocket test completed successfully!")
            return True

    except Exception as e:
        print(f"[FAIL] WebSocket connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    exit(0 if result else 1)

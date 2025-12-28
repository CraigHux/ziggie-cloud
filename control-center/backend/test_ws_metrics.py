#!/usr/bin/env python3
"""Test WebSocket metrics endpoint."""
import asyncio
import websockets
import json
import sys


async def test_metrics_websocket():
    """Test the public metrics WebSocket endpoint."""
    uri = "ws://127.0.0.1:54112/api/system/metrics"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            print("\nReceiving metrics (first 5 messages):\n")

            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3)
                    data = json.loads(message)
                    print(f"[{i+1}] {json.dumps(data, indent=2)}")
                except asyncio.TimeoutError:
                    print(f"[{i+1}] Timeout waiting for message")
                except Exception as e:
                    print(f"[{i+1}] Error: {e}")

            print("\nTest completed successfully!")

    except Exception as e:
        print(f"WebSocket connection error: {e}")
        sys.exit(1)


async def test_concurrent_connections():
    """Test multiple concurrent connections."""
    uri = "ws://127.0.0.1:54112/api/system/metrics"
    print(f"Testing {uri} with multiple concurrent clients...\n")

    async def client_task(client_id):
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Client {client_id}: Connected")

                # Receive first message
                message = await asyncio.wait_for(websocket.recv(), timeout=3)
                data = json.loads(message)

                print(f"Client {client_id}: Received metrics - CPU: {data['cpu']}%, Memory: {data['memory']}%, Disk: {data['disk']}%")

        except Exception as e:
            print(f"Client {client_id}: Error - {e}")

    try:
        # Create 3 concurrent clients
        await asyncio.gather(
            client_task(1),
            client_task(2),
            client_task(3)
        )
        print("\nConcurrent test completed successfully!")

    except Exception as e:
        print(f"Concurrent test error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("WebSocket Metrics Endpoint Test")
    print("=" * 60)
    print()

    # Test basic connection
    asyncio.run(test_metrics_websocket())

    print("\n" + "=" * 60)
    print("Testing Concurrent Connections")
    print("=" * 60)
    print()

    # Test concurrent connections
    asyncio.run(test_concurrent_connections())

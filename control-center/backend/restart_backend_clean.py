"""
Clean restart script for Control Center Backend
Kills all existing instances and starts a fresh one
"""
import psutil
import subprocess
import time
import sys

def kill_backend_processes():
    """Kill all processes listening on port 54112"""
    killed = []

    # Find all processes using port 54112
    for conn in psutil.net_connections():
        if conn.laddr.port == 54112 and conn.status == 'LISTEN':
            try:
                process = psutil.Process(conn.pid)
                print(f"Killing process {conn.pid}: {process.name()}")
                process.kill()
                killed.append(conn.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"Could not kill process {conn.pid}: {e}")

    # Wait for processes to die
    time.sleep(2)

    # Verify they're dead
    still_alive = []
    for pid in killed:
        try:
            process = psutil.Process(pid)
            if process.is_running():
                still_alive.append(pid)
        except psutil.NoSuchProcess:
            pass

    if still_alive:
        print(f"Warning: Some processes still alive: {still_alive}")
        return False

    print(f"Successfully killed {len(killed)} backend processes")
    return True

def start_backend():
    """Start the backend server"""
    print("Starting Control Center Backend...")

    # Start the backend
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=r"C:\Ziggie\control-center\backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

    print(f"Backend started with PID: {process.pid}")
    print(f"Listening on http://127.0.0.1:54112")
    print("\nWaiting for server to be ready...")

    # Wait for server to start
    time.sleep(3)

    # Check if it's running
    try:
        import requests
        response = requests.get("http://127.0.0.1:54112/health", timeout=5)
        if response.status_code == 200:
            print("Backend is healthy and responding!")
            return True
    except Exception as e:
        print(f"Backend may not be ready yet: {e}")
        print("Check logs manually")

    return False

if __name__ == "__main__":
    print("=" * 60)
    print("Control Center Backend - Clean Restart")
    print("=" * 60)
    print()

    # Step 1: Kill existing processes
    print("Step 1: Killing existing backend processes...")
    kill_backend_processes()
    print()

    # Step 2: Start new instance
    print("Step 2: Starting new backend instance...")
    start_backend()
    print()

    print("=" * 60)
    print("Restart complete!")
    print("=" * 60)

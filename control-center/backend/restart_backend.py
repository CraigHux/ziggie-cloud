"""Script to restart the Control Center backend"""
import subprocess
import time
import sys
import psutil

def kill_backend_processes():
    """Kill all Python processes listening on port 54112"""
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if it's a Python process
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                # Check if it's running the backend
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('control-center' in str(arg) and 'backend' in str(arg) for arg in cmdline):
                    print(f"Killing backend process {proc.info['pid']}")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Also check by port
    for conn in psutil.net_connections():
        if conn.laddr.port == 54112 and conn.status == 'LISTEN':
            try:
                proc = psutil.Process(conn.pid)
                print(f"Killing process {conn.pid} on port 54112")
                proc.kill()
                killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    print(f"Killed {killed_count} backend processes")
    time.sleep(2)
    return killed_count

def start_backend():
    """Start the backend server"""
    print("Starting Control Center backend...")
    import os
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    # Start in background
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    print(f"Backend started with PID {proc.pid}")
    print("Backend is running at http://127.0.0.1:54112")
    return proc.pid

if __name__ == "__main__":
    print("=== Control Center Backend Restart ===\n")
    kill_backend_processes()
    start_backend()
    print("\nBackend restart complete!")

"""Force kill all backend processes on port 54112"""
import psutil
import time

pids_to_kill = []

# Find all processes using port 54112
for conn in psutil.net_connections():
    if conn.laddr.port == 54112 and conn.status == 'LISTEN':
        if conn.pid not in pids_to_kill:
            pids_to_kill.append(conn.pid)

print(f"Found {len(pids_to_kill)} processes on port 54112: {pids_to_kill}")

# Kill them all
for pid in pids_to_kill:
    try:
        p = psutil.Process(pid)
        print(f"Killing PID {pid}: {p.name()}")
        p.terminate()  # Try graceful first
    except Exception as e:
        print(f"Error terminating {pid}: {e}")

# Wait
time.sleep(2)

# Force kill any survivors
for pid in pids_to_kill:
    try:
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            print(f"Force killing PID {pid}")
            p.kill()
    except Exception as e:
        print(f"Error force killing {pid}: {e}")

time.sleep(1)

# Verify
still_alive = [pid for pid in pids_to_kill if psutil.pid_exists(pid)]
if still_alive:
    print(f"WARNING: Some processes still alive: {still_alive}")
else:
    print("All processes killed successfully!")

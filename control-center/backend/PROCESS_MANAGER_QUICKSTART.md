# Process Manager Quick Reference

## Overview
The Control Center backend now uses PID file singleton pattern to prevent duplicate processes.

## Normal Operations

### Starting the Backend
```bash
cd C:\Ziggie\control-center\backend
python main.py
```

**Expected Output:**
```
Process lock acquired (PID: 12345)
Initializing Control Center backend...
```

### Stopping the Backend
**Windows:**
```bash
# Find the PID
type backend.pid

# Stop gracefully (Ctrl+C in the terminal)
# Or force stop:
taskkill /F /PID <pid>
```

**Linux:**
```bash
# Stop gracefully
kill $(cat backend.pid)

# Or force stop
kill -9 $(cat backend.pid)
```

## Error Scenarios

### Already Running Error
```
ERROR: Backend already running!
Another instance is running with PID: 12345
```

**Solution:** Stop the existing instance first, then start again.

### Stale PID File (After Crash)
```
Found stale PID file (PID 12345 not running), removing...
Successfully acquired process lock (PID: 67890)
```

**Action:** None needed - automatically recovered.

### Corrupted PID File
```
ERROR: PID file contains invalid content: ...
Successfully acquired process lock (PID: 67890)
```

**Action:** None needed - automatically recovered.

## Troubleshooting

### Backend Won't Start
1. Check if backend is already running:
   ```bash
   python -c "from process_manager import is_backend_running; print(is_backend_running())"
   ```

2. If shows False but still can't start, manually remove PID file:
   ```bash
   rm backend.pid
   ```

3. Try starting again

### Multiple Instances Detected
1. List all Python processes:
   ```bash
   # Windows
   tasklist | findstr python

   # Linux
   ps aux | grep python
   ```

2. Stop all backend processes:
   ```bash
   # Windows
   taskkill /F /PID <pid>

   # Linux
   kill <pid>
   ```

3. Remove PID file:
   ```bash
   rm backend.pid
   ```

4. Start fresh

### Permission Errors
If you see "Permission denied" errors:

1. Check PID file permissions:
   ```bash
   ls -l backend.pid
   ```

2. Ensure you have write access to backend directory

3. If needed, delete PID file manually:
   ```bash
   rm -f backend.pid
   ```

## File Locations

- **PID File:** `C:\Ziggie\control-center\backend\backend.pid`
- **Process Manager:** `C:\Ziggie\control-center\backend\process_manager.py`
- **Main Application:** `C:\Ziggie\control-center\backend\main.py`
- **Backup:** `C:\Ziggie\control-center\backend\main.py.backup`

## Monitoring

### Check Backend Status
```python
from process_manager import ProcessManager

pm = ProcessManager('backend.pid')
running_pid = pm.get_running_pid()

if running_pid:
    print(f"Backend running with PID: {running_pid}")
else:
    print("Backend not running")
```

### Get PID File Location
```python
from process_manager import ProcessManager

pm = ProcessManager('backend.pid')
print(f"PID file: {pm.get_pid_file_path()}")
```

## Rollback (If Needed)

If issues arise, restore original main.py:

```bash
cd C:\Ziggie\control-center\backend
cp main.py.backup main.py
rm backend.pid
python main.py
```

## Support

For issues or questions, see full documentation:
- `C:\Ziggie\agent-reports\L2_PID_FILE_IMPLEMENTATION.md`

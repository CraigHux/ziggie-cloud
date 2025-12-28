# Control Center Backend - Deployment Guide

Quick start guide for getting the backend up and running.

## Prerequisites

- Windows 10/11
- Python 3.8 or higher
- ComfyUI installed at `C:\ComfyUI`
- Meow Ping RTS project at `C:\meowping-rts`

## Quick Start (3 Steps)

### Step 1: Install Dependencies

**Option A - Automatic (Recommended):**
```batch
install.bat
```

**Option B - Manual:**
```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python quick_check.py
```

This checks:
- Python version compatibility
- All dependencies installed
- Required paths exist
- Port 8080 is available
- All critical files present

### Step 3: Start Server

**Option A - Automatic:**
```batch
run.bat
```

**Option B - Manual:**
```bash
python main.py
```

The server will start on: **http://127.0.0.1:8080**

## Verification

### Test API Endpoints

```bash
python test_server.py
```

### Access Documentation

Open in browser:
- Swagger UI: http://127.0.0.1:8080/docs
- ReDoc: http://127.0.0.1:8080/redoc

### Quick API Test

```bash
# Windows PowerShell
Invoke-WebRequest http://127.0.0.1:8080/health

# Or use curl
curl http://127.0.0.1:8080/health
```

## Common Issues & Solutions

### Issue: "Port 8080 already in use"

**Solution 1 - Find and stop the process:**
```bash
netstat -ano | findstr :8080
taskkill /PID <pid> /F
```

**Solution 2 - Change the port:**
Edit `config.py`:
```python
PORT: int = 8081  # Change to different port
```

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

Or run:
```batch
install.bat
```

### Issue: "Path not found" errors

**Solution:**
Check the paths in `config.py` match your installation:
```python
COMFYUI_DIR: Path = Path(r"C:\ComfyUI")
MEOWPING_DIR: Path = Path(r"C:\meowping-rts")
```

### Issue: Database errors

**Solution:**
Delete the database and let it recreate:
```bash
del control-center.db
python main.py
```

### Issue: Service won't start

**Check logs:**
```
backend/logs/comfyui.log
backend/logs/kb_scheduler.log
```

**Verify paths in config.py:**
- Command exists
- Working directory exists
- Permissions are correct

## Configuration

### Environment Variables

Create `.env` file (optional):
```env
HOST=127.0.0.1
PORT=8080
DEBUG=True
CORS_ORIGINS=["http://localhost:3000"]
WS_UPDATE_INTERVAL=2
```

### Adding New Services

Edit `config.py`, add to `SERVICES` dict:
```python
"my_service": {
    "name": "My Service Name",
    "command": ["python", "script.py"],
    "cwd": r"C:\path\to\service",
    "port": 3000,
    "log_file": "my_service.log"
}
```

### CORS Configuration

To allow additional origins, edit `config.py`:
```python
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000"
]
```

## Production Deployment

### 1. Disable Debug Mode

Edit `config.py`:
```python
DEBUG: bool = False
```

### 2. Use Production Server

Install gunicorn:
```bash
pip install gunicorn
```

Run with:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. Setup as Windows Service

Use NSSM (Non-Sucking Service Manager):
```bash
nssm install ControlCenter "C:\path\to\python.exe" "C:\meowping-rts\control-center\backend\main.py"
```

### 4. Setup Logging

Configure logging in `main.py` or use uvicorn logging:
```bash
uvicorn main:app --log-config logging.json
```

## API Usage Examples

### Get System Stats
```bash
curl http://127.0.0.1:8080/api/system/stats
```

### List Services
```bash
curl http://127.0.0.1:8080/api/services
```

### Start ComfyUI
```bash
curl -X POST http://127.0.0.1:8080/api/services/comfyui/start
```

### Stop ComfyUI
```bash
curl -X POST http://127.0.0.1:8080/api/services/comfyui/stop
```

### Get Service Logs
```bash
curl http://127.0.0.1:8080/api/services/comfyui/logs?lines=50
```

### Search Knowledge Base
```bash
curl "http://127.0.0.1:8080/api/knowledge/search?query=unity&limit=10"
```

## WebSocket Examples

### JavaScript - System Stats
```javascript
const ws = new WebSocket('ws://127.0.0.1:8080/api/system/ws');

ws.onopen = () => {
    console.log('Connected to system stats');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('CPU:', data.cpu.usage_percent + '%');
    console.log('RAM:', data.memory.percent + '%');
    console.log('Disk:', data.disk.percent + '%');
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from system stats');
};
```

### JavaScript - Service Status
```javascript
const ws = new WebSocket('ws://127.0.0.1:8080/api/services/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    data.services.forEach(service => {
        console.log(`${service.name}: ${service.status}`);
        if (service.pid) {
            console.log(`  PID: ${service.pid}, Port: ${service.port}`);
        }
    });
};
```

## Monitoring

### Check Server Status
```bash
curl http://127.0.0.1:8080/health
```

### View Logs
```bash
# Server logs (if using file logging)
type backend\logs\server.log

# Service logs
type backend\logs\comfyui.log
type backend\logs\kb_scheduler.log
```

### Monitor System Resources
```bash
curl http://127.0.0.1:8080/api/system/stats | python -m json.tool
```

## Backup & Restore

### Backup Database
```bash
copy control-center.db control-center.db.backup
```

### Backup Configuration
```bash
copy config.py config.py.backup
copy .env .env.backup
```

### Restore
```bash
copy control-center.db.backup control-center.db
copy config.py.backup config.py
copy .env.backup .env
```

## Troubleshooting Commands

### Check if server is running
```bash
netstat -ano | findstr :8080
```

### Check Python processes
```bash
tasklist | findstr python
```

### Check service status
```bash
curl http://127.0.0.1:8080/api/services
```

### Check open ports
```bash
curl http://127.0.0.1:8080/api/system/ports
```

### Test database connection
```bash
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

## Performance Tuning

### Adjust WebSocket Update Interval
Edit `config.py`:
```python
WS_UPDATE_INTERVAL: int = 5  # Slower updates (less CPU)
```

### Limit Process Scanning
Edit `api/system.py`:
```python
return {
    "processes": processes[:25]  # Return top 25 instead of 50
}
```

### Adjust Port Scan Range
Edit `config.py`:
```python
PORT_SCAN_START: int = 8000
PORT_SCAN_END: int = 9000
```

## Security Considerations

1. **Local Only**: Server binds to 127.0.0.1 (localhost)
2. **CORS**: Restricted to specific origins
3. **No Auth**: Not designed for remote access
4. **Process Control**: Only manages configured services
5. **Path Access**: Limited to configured directories

## Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Clean Logs
```bash
del /Q backend\logs\*.log
```

### Reset Database
```bash
del control-center.db
python main.py
```

## Getting Help

1. Check logs in `backend/logs/`
2. Run system check: `python quick_check.py`
3. Test endpoints: `python test_server.py`
4. Review API docs: http://127.0.0.1:8080/docs
5. Check PROJECT_SUMMARY.md for details

## Next Steps

After deployment:

1. Start the React frontend (port 3000)
2. Open the dashboard in browser
3. Start monitoring services
4. Configure additional services as needed
5. Set up automated knowledge base scans

## Support & Documentation

- **API Reference**: API_DOCS.md
- **Project Overview**: PROJECT_SUMMARY.md
- **User Guide**: README.md
- **This Guide**: DEPLOYMENT_GUIDE.md

---

**Server Ready!** Access at: http://127.0.0.1:8080

# Configuration Guide

## Overview

The Control Center backend has been updated to use environment variables for all configuration values, removing hardcoded paths and secrets from the source code.

## Environment Variables

All configuration is now managed through environment variables. Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

### Available Configuration Options

#### Server Configuration
- `HOST`: Server host address (default: `127.0.0.1`)
- `PORT`: Server port (default: `54112`)
- `DEBUG`: Enable debug mode (default: `true`)

#### CORS Configuration
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: `http://localhost:3000,http://localhost:3001`)

#### Database Configuration
- `DATABASE_URL`: Database connection URL (default: `sqlite+aiosqlite:///control-center.db`)

#### Directory Paths
- `COMFYUI_DIR`: Path to ComfyUI installation (default: `C:\ComfyUI`)
- `MEOWPING_DIR`: Path to Meowping/Ziggie directory (default: `C:\Ziggie`)
- `AI_AGENTS_ROOT`: Path to AI agents root directory (default: `C:\Ziggie\ai-agents`)

#### Service-Specific Paths
- `COMFYUI_PYTHON_PATH`: Path to ComfyUI Python executable (default: `C:\ComfyUI\python_embeded\python.exe`)
- `KB_SCHEDULER_PATH`: Path to Knowledge Base scheduler (default: `C:\Ziggie\ai-agents\knowledge-base`)

#### API Keys
- `KEYS_API_DIR`: Directory containing API key files (default: `C:\Ziggie\Keys-api`)
- `YOUTUBE_API_KEY_FILE`: Path to YouTube API key file (default: `C:\Ziggie\Keys-api\meowping-youtube-api.txt`)

#### WebSocket Configuration
- `WS_UPDATE_INTERVAL`: WebSocket update interval in seconds (default: `2`)

#### Port Scanning Configuration
- `PORT_SCAN_START`: Start of port scanning range (default: `3000`)
- `PORT_SCAN_END`: End of port scanning range (default: `9000`)

## Using the Configuration

### Loading YouTube API Key

The configuration includes a helper method to load the YouTube API key:

```python
from config import settings

api_key = settings.load_youtube_api_key()
```

### Accessing Service Configurations

Service configurations are dynamically built from environment variables:

```python
from config import settings

comfyui_config = settings.SERVICES['comfyui']
kb_scheduler_config = settings.SERVICES['kb_scheduler']
```

### CORS Origins

CORS origins can be specified as either:
- A comma-separated string in .env: `CORS_ORIGINS=http://localhost:3000,http://localhost:3001`
- The default Python list in code (if no .env value is provided)

## Security Best Practices

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Use `.env.example`** - Keep this updated with all required variables (without sensitive values)
3. **Protect API keys** - Store them in the `KEYS_API_DIR` directory, which should also be in `.gitignore`
4. **Environment-specific configs** - Use different `.env` files for development, staging, and production

## Migration from Hardcoded Values

All previously hardcoded values have been:
1. Moved to environment variables with sensible defaults
2. Documented in `.env.example`
3. Made configurable without code changes

The default values match the current system configuration, so no immediate changes are required unless deploying to a different environment.

## Dependencies

The configuration system uses:
- `pydantic-settings`: For type-safe configuration management
- `python-dotenv`: For loading `.env` files (already in `requirements.txt`)

Both dependencies are already installed and configured.

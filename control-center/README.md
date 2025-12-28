# Ziggie Control Center

**Version:** 1.0.0
**Architecture:** Docker-based microservices
**Purpose:** Unified management platform for multiple workspaces including Meow Ping RTS, ComfyUI, and AI Agent systems

---

## Overview

Ziggie Control Center is a comprehensive web-based dashboard for managing multiple development workspaces and AI systems. Built with Docker containerization, it provides real-time monitoring, service control, and integration with AI agents and knowledge base systems.

### Key Features

- **Multi-Workspace Management:** Manage Meow Ping RTS, ComfyUI, and additional workspaces
- **Real-Time Monitoring:** System stats, service status, process management
- **Service Control:** Start, stop, and monitor services with live logs
- **Agent Dashboard:** Monitor and invoke 584 AI agents across 3 tiers
- **Knowledge Base Integration:** Manage automated learning from 50+ YouTube creators
- **WebSocket Support:** Real-time updates via WebSocket connections
- **Beautiful UI:** Modern React dashboard with Material-UI components
- **RESTful API:** Complete REST API for programmatic access

---

## Architecture

### Service Stack

```
┌────────────────────────────────────────┐
│      Ziggie Control Center             │
├────────────────────────────────────────┤
│  Frontend    │    Backend    │ Database │
│  React/Vite │  FastAPI      │ MongoDB  │
│  Port: 3001 │  Port: 54112  │ 27018    │
└────────────────────────────────────────┘
```

### Components

1. **Frontend (React/Vite)**
   - Location: `frontend/`
   - Port: 3001
   - Technologies: React 18, Material-UI, TypeScript, Vite

2. **Backend API (FastAPI)**
   - Location: `backend/`
   - Port: 54112
   - Technologies: Python 3.11+, FastAPI, SQLAlchemy, Pydantic

3. **Database (MongoDB)**
   - Port: 27018
   - Storage: Persistent data for services, agents, knowledge

### Workspace Integrations

- **Meow Ping RTS:** Game development workspace
- **ComfyUI:** AI image generation and workflow engine
- **AI Agents:** 584 agents across 3 tier hierarchy
- **Knowledge Base:** Automated learning pipeline

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Minimum 4GB RAM available
- Ports 3001, 54112, 27018 available

### Start All Services

```bash
# Navigate to project root
cd C:\Ziggie

# Start services with docker-compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Access Control Center

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3001 | 3001 |
| Backend API | http://localhost:54112 | 54112 |
| API Docs | http://localhost:54112/docs | 54112 |
| MongoDB | localhost:27018 | 27018 |

### Health Checks

```bash
# Frontend health
curl http://localhost:3001

# Backend health
curl http://localhost:54112/health

# MongoDB connectivity
docker-compose exec mongo mongosh --eval "db.adminCommand('ping')"
```

---

## Frontend Setup

### Prerequisites
- Node.js 18+ installed
- Backend running on port 54112

### Configuration

1. **Create environment file:**
   ```bash
   cd frontend
   cp .env.example .env
   ```

2. **Configure backend URL** (if different from default):
   Edit `.env` and set:
   ```
   VITE_API_URL=http://127.0.0.1:54112/api
   VITE_WS_URL=ws://127.0.0.1:54112/api/system/ws
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Access the application:**
   Open http://localhost:3001
   Default credentials: admin / admin123

### Troubleshooting

**Problem:** Frontend shows "Network Error" or "Cannot connect to backend"
**Solution:** Check that `.env` file exists and has correct backend URL (port 54112, not 8080)

**Problem:** Changes to .env not taking effect
**Solution:** Restart the dev server with `npm run dev`

---

## Port Mapping Reference

| Service | Port | Purpose | Access |
|---------|------|---------|--------|
| Frontend | 3001 | React dashboard | http://localhost:3001 |
| Backend API | 54112 | FastAPI REST API | http://localhost:54112 |
| MongoDB | 27018 | Database | localhost:27018 |

---

## Docker Compose Configuration

### Basic Setup

```yaml
version: '3.8'
services:
  frontend:
    build: ./control-center/frontend
    ports:
      - "3001:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:54112

  backend:
    build: ./control-center/backend
    ports:
      - "54112:8080"
    depends_on:
      - mongo
    environment:
      - MONGODB_URI=mongodb://mongo:27017/ziggie
      - PYTHONUNBUFFERED=1

  mongo:
    image: mongo:latest
    ports:
      - "27018:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=ziggie

volumes:
  mongo_data:
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove data
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose restart
```

---

## API Documentation

### System Monitoring Endpoints

```bash
# Get system statistics
GET /api/system/stats

# List running processes
GET /api/system/processes

# List open ports and services
GET /api/system/ports

# WebSocket for real-time system updates
WS /api/system/ws
```

### Service Control Endpoints

```bash
# List all services
GET /api/services

# Get service status
GET /api/services/{service_name}/status

# Start a service
POST /api/services/{service_name}/start

# Stop a service
POST /api/services/{service_name}/stop

# Get service logs
GET /api/services/{service_name}/logs?lines=100

# WebSocket for real-time service updates
WS /api/services/ws
```

### Agent Endpoints

```bash
# Get agent summary
GET /api/agents/summary

# List all agents
GET /api/agents

# Get agent details
GET /api/agents/{agent_id}

# Invoke an agent
POST /api/agents/{agent_id}/invoke
```

### Knowledge Base Endpoints

```bash
# Get recent knowledge files
GET /api/knowledge/recent

# Update knowledge base
POST /api/knowledge/update

# Search knowledge
GET /api/knowledge/search?q=query
```

### Health & Status

```bash
# Health check
GET /health

# API info
GET /

# API documentation (OpenAPI/Swagger)
GET /docs
```

---

## Features

### Dashboard

Real-time overview of system status and services:
- **System Stats:** CPU, RAM, and disk usage graphs
- **Service Status:** Quick view of all managed services
- **Quick Actions:** One-click service controls
- **Agent Summary:** Overview of agent hierarchy and status
- **Recent Activity:** Latest knowledge base updates

### Services Management

Complete lifecycle management for services:
- **Start/Stop/Restart:** Service control buttons
- **Live Logs:** Real-time log streaming
- **Status Monitoring:** Service health indicators
- **Port Detection:** Automatic port discovery
- **Auto-refresh:** Optional automatic status updates

### System Monitor

Detailed system information and process management:
- **Resource Charts:** CPU, RAM, and disk usage over time
- **Process List:** Sortable and searchable process table
- **Port Scanner:** View all open ports and services
- **System Info:** Hardware and OS information

### Agent Management

Monitor and interact with AI agent system:
- **Agent Browser:** Browse all 584 agents
- **Agent Details:** View agent capabilities and status
- **Agent Invocation:** Queue tasks for agents
- **Agent Logs:** View execution history

### Knowledge Base

Manage automated learning system:
- **Knowledge Browser:** View knowledge files
- **Knowledge Search:** Search across knowledge base
- **Source Management:** View and manage content sources
- **Update Status:** Monitor knowledge base updates

---

## Development Workflow

### Local Setup (without Docker)

```bash
# Install backend dependencies
cd control-center/backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start backend (Terminal 1)
cd control-center/backend
python main.py

# Start frontend (Terminal 2)
cd control-center/frontend
npm run dev

# Access at http://localhost:3001
```

### Docker Development Workflow

```bash
# Start services
docker-compose up -d

# Make code changes
# Edit files in frontend/ or backend/

# Rebuild if needed
docker-compose build

# Restart services
docker-compose restart

# Check logs
docker-compose logs -f
```

### Adding New Features

1. **Backend:**
   - Add endpoint in `backend/api/`
   - Update models in `backend/database/models.py`
   - Add tests in `tests/`

2. **Frontend:**
   - Create component in `frontend/src/components/`
   - Add page/route in `frontend/src/App.jsx`
   - Add API call in `frontend/src/services/api.js`

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :3001

# Kill process
taskkill /PID <PID> /F

# Or use different port in docker-compose.yml
ports:
  - "3002:3000"
```

### Container Won't Start

```bash
# Check logs
docker-compose logs -f backend

# Rebuild without cache
docker-compose build --no-cache

# Check Docker daemon
docker ps
```

### API Connection Failed

```bash
# Verify backend is running
docker-compose ps

# Check backend logs
docker-compose logs -f backend

# Test health endpoint
curl http://localhost:54112/health
```

### Frontend Can't Connect to Backend

```bash
# Check .env in frontend directory
cat control-center/frontend/.env

# Verify API URL matches:
REACT_APP_API_URL=http://localhost:54112

# Restart frontend
docker-compose restart frontend
```

### Database Connection Issues

```bash
# Check MongoDB is running
docker-compose ps

# Test MongoDB connection
docker-compose exec mongo mongosh

# View MongoDB logs
docker-compose logs mongo

# Reset MongoDB (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### WebSocket Connection Issues

```bash
# Check WebSocket URL in browser console
# Should be: ws://localhost:54112/api/system/ws

# Verify backend is running
curl http://localhost:54112/health

# Check firewall settings
```

---

## Component Documentation

### Frontend Documentation

See `frontend/README.md` for:
- Project structure
- Component architecture
- API integration
- Theme customization
- Development guidelines

### Backend Documentation

See `backend/README.md` for:
- API endpoints
- Database models
- Service control logic
- Process management
- Configuration guide

---

## Environment Variables

### Frontend (.env)

```
REACT_APP_API_URL=http://localhost:54112
REACT_APP_WS_URL=ws://localhost:54112
REACT_APP_ENV=development
```

### Backend (.env)

```
MONGODB_URI=mongodb://mongo:27017/ziggie
DATABASE_NAME=ziggie
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

### Docker Compose (.env)

```
COMPOSE_PROJECT_NAME=ziggie
ENVIRONMENT=development
```

---

## Performance Considerations

- **Frontend Load Time:** <1 second
- **API Response Time:** <500ms
- **WebSocket Update Interval:** 2 seconds
- **System Stats Refresh:** Every 2 seconds
- **Service Status Refresh:** Real-time via WebSocket

---

## Security

### Best Practices

- Backend binds to localhost (127.0.0.1)
- CORS restricted to frontend origin
- API keys stored in environment variables
- Database credentials in environment variables
- Proper error handling without sensitive info exposure

### Deployment Security

- Use environment variables for sensitive data
- Don't commit `.env` files to Git
- Enable authentication for production
- Use HTTPS in production
- Implement rate limiting
- Enable CORS properly for production domains

---

## Backup & Data

### MongoDB Data Backup

```bash
# Create backup
docker-compose exec mongo mongodump --out /data/backup

# Restore backup
docker-compose exec mongo mongorestore /data/backup
```

### Database Reset

```bash
# WARNING: This deletes all data
docker-compose down -v

# Start fresh
docker-compose up -d
```

---

## Workspace Integration Guide

### Adding a New Workspace

1. Create workspace configuration in MongoDB
2. Add service definition to backend config
3. Create dashboard panel in frontend
4. Add API endpoints for workspace control
5. Update documentation

### Example: Integrating a New Service

```python
# backend/config.py
SERVICES = {
    "new_workspace": {
        "name": "New Workspace",
        "command": ["python", "workspace.py"],
        "cwd": r"C:\path\to\workspace",
        "port": 5000,
        "log_file": "new_workspace.log"
    }
}
```

---

## Advanced Configuration

### Environment-Specific Setup

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Custom MongoDB Configuration

Edit docker-compose.yml to add MongoDB options:

```yaml
mongo:
  image: mongo:latest
  ports:
    - "27018:27017"
  volumes:
    - mongo_data:/data/db
    - ./mongo.conf:/etc/mongod.conf
  environment:
    - MONGO_INITDB_DATABASE=ziggie
  command: mongod --config /etc/mongod.conf
```

---

## Getting Help

### Resources

1. **API Documentation:** http://localhost:54112/docs
2. **Component READMEs:**
   - Frontend: `frontend/README.md`
   - Backend: `backend/README.md`
3. **Troubleshooting:** See "Troubleshooting" section above
4. **Logs:** `docker-compose logs -f [service]`

### Common Issues

Check the troubleshooting section for solutions to:
- Port conflicts
- Connection issues
- Container startup failures
- Database problems
- WebSocket issues

---

## License

Part of Ziggie Control Center project. MIT License.

---

## Support

**Project:** Ziggie Control Center - Meow Ping RTS Development Platform
**Date:** November 2025
**Version:** 1.0.0

For issues, questions, or contributions:
1. Check documentation
2. Review troubleshooting section
3. Check application logs
4. Review GitHub issues

---

**Welcome to Ziggie Control Center**

*Start with: `docker-compose up -d`*
*Access dashboard at: http://localhost:3001*
*API documentation at: http://localhost:54112/docs*

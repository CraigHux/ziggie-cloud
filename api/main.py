from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
from datetime import datetime

app = FastAPI(
    title="Ziggie API",
    description="Core API for Ziggie AI Command Center",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MCP_GATEWAY_URL = os.getenv("MCP_GATEWAY_URL", "http://mcp-gateway:8080")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")

# Models
class ChatRequest(BaseModel):
    message: str
    model: str = "mistral:7b"
    system_prompt: Optional[str] = "You are Ziggie, a helpful AI assistant."

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: str

class AgentConfig(BaseModel):
    name: str
    description: str
    model: str = "mistral:7b"
    system_prompt: str
    tools: List[str] = []

# In-memory agent store (replace with DB in production)
agents = {}

# Health endpoints
@app.get("/health")
def health():
    return {"status": "ok", "service": "ziggie-api", "version": "1.0.0"}

@app.get("/")
def root():
    return {
        "service": "Ziggie API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "agents": "/api/agents",
            "models": "/api/models",
            "workflows": "/api/workflows"
        }
    }

# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to Ollama and get a response"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": request.model,
                    "prompt": request.message,
                    "system": request.system_prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            return ChatResponse(
                response=data.get("response", ""),
                model=request.model,
                timestamp=datetime.utcnow().isoformat()
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

# Models endpoints
@app.get("/api/models")
async def list_models():
    """List available Ollama models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

# Agent endpoints
@app.get("/api/agents")
def list_agents():
    """List all configured agents"""
    return {"agents": list(agents.values())}

@app.post("/api/agents")
def create_agent(agent: AgentConfig):
    """Create a new agent configuration"""
    agent_id = f"agent_{len(agents) + 1}"
    agents[agent_id] = {
        "id": agent_id,
        "name": agent.name,
        "description": agent.description,
        "model": agent.model,
        "system_prompt": agent.system_prompt,
        "tools": agent.tools,
        "created_at": datetime.utcnow().isoformat()
    }
    return agents[agent_id]

@app.get("/api/agents/{agent_id}")
def get_agent(agent_id: str):
    """Get a specific agent configuration"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents[agent_id]

@app.delete("/api/agents/{agent_id}")
def delete_agent(agent_id: str):
    """Delete an agent configuration"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    del agents[agent_id]
    return {"message": "Agent deleted"}

# Workflow endpoints
@app.get("/api/workflows")
async def list_workflows():
    """List n8n workflows (placeholder - needs n8n API key)"""
    return {
        "workflows": [
            {"id": "lH3SqIY0NliSVGWf", "name": "Ziggie Health Monitor", "active": True},
            {"id": "oMfyxkQPqanvoTFP", "name": "GitHub Webhook Handler", "active": True}
        ],
        "note": "Connect n8n API for real-time data"
    }

# System status
@app.get("/api/status")
async def system_status():
    """Get overall system status"""
    status = {"services": {}}
    
    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            status["services"]["ollama"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        status["services"]["ollama"] = "unreachable"
    
    # Check MCP Gateway
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{MCP_GATEWAY_URL}/health")
            status["services"]["mcp_gateway"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        status["services"]["mcp_gateway"] = "unreachable"
    
    status["timestamp"] = datetime.utcnow().isoformat()
    return status

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import os
import asyncio
import json
from datetime import datetime
import uuid

app = FastAPI(
    title="Ziggie Sim Studio",
    description="Agent Simulation and Testing Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

class AgentProfile(BaseModel):
    name: str
    description: str
    model: str = "mistral:7b"
    system_prompt: str
    personality: Dict[str, Any] = {}
    tools: List[str] = []

class SimulationConfig(BaseModel):
    agent_id: str
    scenario: str
    max_turns: int = 10
    temperature: float = 0.7

class Message(BaseModel):
    role: str
    content: str
    timestamp: str = None
    metadata: Dict[str, Any] = {}

agents: Dict[str, Dict] = {}
simulations: Dict[str, Dict] = {}
conversations: Dict[str, List[Dict]] = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "sim-studio", "version": "1.0.0"}

@app.get("/")
def root():
    return {
        "service": "Ziggie Sim Studio",
        "version": "1.0.0",
        "description": "Agent Simulation and Testing Platform",
        "endpoints": {
            "agents": "/api/agents",
            "simulations": "/api/simulations",
            "scenarios": "/api/scenarios",
            "templates": "/api/templates"
        }
    }

@app.get("/api/agents")
def list_agents():
    return {"agents": list(agents.values())}

@app.post("/api/agents")
def create_agent(profile: AgentProfile):
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"
    agents[agent_id] = {
        "id": agent_id,
        **profile.dict(),
        "created_at": datetime.utcnow().isoformat()
    }
    return agents[agent_id]

@app.get("/api/agents/{agent_id}")
def get_agent(agent_id: str):
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents[agent_id]

@app.delete("/api/agents/{agent_id}")
def delete_agent(agent_id: str):
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    del agents[agent_id]
    return {"message": "Agent deleted"}

@app.post("/api/simulations")
def create_simulation(config: SimulationConfig):
    if config.agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    sim_id = f"sim_{uuid.uuid4().hex[:8]}"
    simulations[sim_id] = {
        "id": sim_id,
        "agent_id": config.agent_id,
        "scenario": config.scenario,
        "max_turns": config.max_turns,
        "temperature": config.temperature,
        "status": "created",
        "turns": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    conversations[sim_id] = []
    return simulations[sim_id]

@app.get("/api/simulations")
def list_simulations():
    return {"simulations": list(simulations.values())}

@app.get("/api/simulations/{sim_id}")
def get_simulation(sim_id: str):
    if sim_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {
        "simulation": simulations[sim_id],
        "conversation": conversations.get(sim_id, [])
    }

@app.post("/api/simulations/{sim_id}/chat")
async def simulation_chat(sim_id: str, message: Message):
    if sim_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    sim = simulations[sim_id]
    agent = agents.get(sim["agent_id"])
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    user_msg = {"role": "user", "content": message.content, "timestamp": datetime.utcnow().isoformat()}
    conversations[sim_id].append(user_msg)
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            context = "\n".join([f"{m['role']}: {m['content']}" for m in conversations[sim_id][-10:]])
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": agent["model"],
                    "prompt": f"{context}\nagent:",
                    "system": agent["system_prompt"],
                    "stream": False,
                    "options": {"temperature": sim["temperature"]}
                }
            )
            response.raise_for_status()
            data = response.json()
            agent_msg = {
                "role": "agent",
                "content": data.get("response", "").strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"model": agent["model"]}
            }
            conversations[sim_id].append(agent_msg)
            sim["turns"] += 1
            sim["status"] = "running"
            if sim["turns"] >= sim["max_turns"]:
                sim["status"] = "completed"
            return {"user": user_msg, "agent": agent_msg, "simulation": sim}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

@app.get("/api/scenarios")
def list_scenarios():
    return {
        "scenarios": [
            {"id": "customer_support", "name": "Customer Support", "description": "Test agent handling customer inquiries"},
            {"id": "code_review", "name": "Code Review", "description": "Test agent reviewing code"},
            {"id": "creative_writing", "name": "Creative Writing", "description": "Test creative writing abilities"},
            {"id": "problem_solving", "name": "Problem Solving", "description": "Test reasoning and problem-solving"}
        ]
    }

@app.get("/api/templates")
def list_templates():
    return {
        "templates": [
            {"id": "assistant", "name": "General Assistant", "model": "mistral:7b", "system_prompt": "You are a helpful AI assistant named Ziggie."},
            {"id": "coder", "name": "Code Assistant", "model": "mistral:7b", "system_prompt": "You are an expert programmer."},
            {"id": "analyst", "name": "Data Analyst", "model": "mistral:7b", "system_prompt": "You are a data analyst."}
        ]
    }

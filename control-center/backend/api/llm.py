"""
LLM API Endpoints
Handles interactions with Ollama LLM service for AI-powered features.
"""

import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import httpx

from middleware.auth import get_current_user, UserResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/llm", tags=["llm"])

# Get Ollama URL from settings
OLLAMA_BASE_URL = settings.OLLAMA_URL


# Request/Response Models
class GenerateRequest(BaseModel):
    """Generate text request model."""
    model: str = Field(default="llama3.2", description="Model to use for generation")
    prompt: str = Field(..., min_length=1, max_length=4000, description="Prompt text")
    stream: bool = Field(default=False, description="Enable streaming response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for sampling")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4096, description="Max tokens to generate")


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    """Chat request model."""
    model: str = Field(default="llama3.2", description="Model to use for chat")
    messages: list[ChatMessage] = Field(..., min_items=1, description="Chat history")
    stream: bool = Field(default=False, description="Enable streaming response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for sampling")


# Endpoints
@router.get("")
async def get_llm_api_info():
    """
    Get LLM API information and available endpoints.
    Public endpoint for API discovery.
    """
    return {
        "service": "Ziggie LLM API",
        "version": "1.0.0",
        "ollama_url": OLLAMA_BASE_URL,
        "endpoints": {
            "status": "GET /api/llm/status - Health check (public)",
            "models": "GET /api/llm/models - List available models (auth required)",
            "generate": "POST /api/llm/generate - Generate text (auth required)",
            "chat": "POST /api/llm/chat - Chat completion (auth required)"
        },
        "documentation": "http://localhost:54112/docs#/llm"
    }


@router.get("/status")
async def get_status():
    """
    Get Ollama service status (public endpoint).
    Returns service availability and version info.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/version")
            if response.status_code == 200:
                return {
                    "status": "online",
                    "service": "ollama",
                    "url": OLLAMA_BASE_URL,
                    "version": response.json()
                }
            else:
                return {
                    "status": "degraded",
                    "service": "ollama",
                    "url": OLLAMA_BASE_URL,
                    "error": "Service returned non-200 status"
                }
    except Exception as e:
        logger.error(f"Failed to get Ollama status: {e}")
        return {
            "status": "offline",
            "service": "ollama",
            "url": OLLAMA_BASE_URL,
            "error": str(e)
        }


@router.get("/models")
async def list_models(current_user: UserResponse = Depends(get_current_user)):
    """
    List available LLM models (requires authentication).
    Returns list of models with metadata.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Ollama service timeout while listing models"
        )
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve models: {str(e)}"
        )


@router.post("/generate")
async def generate_text(
    request: GenerateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate text using Ollama (requires authentication).
    Supports both streaming and non-streaming responses.
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Build Ollama request
            ollama_request = {
                "model": request.model,
                "prompt": request.prompt,
                "stream": request.stream,
                "options": {
                    "temperature": request.temperature
                }
            }

            if request.max_tokens:
                ollama_request["options"]["num_predict"] = request.max_tokens

            # Log request for audit
            logger.info(
                f"LLM generate request: user={current_user.username}, "
                f"model={request.model}, prompt_length={len(request.prompt)}"
            )

            # Send request to Ollama
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=ollama_request
            )
            response.raise_for_status()

            # Handle streaming vs non-streaming
            if request.stream:
                return StreamingResponse(
                    response.aiter_bytes(),
                    media_type="application/x-ndjson"
                )
            else:
                result = response.json()
                logger.info(
                    f"LLM generate complete: user={current_user.username}, "
                    f"tokens={result.get('eval_count', 0)}"
                )
                return result

    except httpx.TimeoutException:
        logger.error(f"LLM generation timeout for user {current_user.username}")
        raise HTTPException(
            status_code=504,
            detail="LLM generation timeout (>120s)"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama HTTP error: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Ollama service error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate text: {str(e)}"
        )


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Chat with LLM using conversation history (requires authentication).
    Supports both streaming and non-streaming responses.
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Build Ollama chat request
            ollama_request = {
                "model": request.model,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in request.messages
                ],
                "stream": request.stream,
                "options": {
                    "temperature": request.temperature
                }
            }

            # Log request for audit
            logger.info(
                f"LLM chat request: user={current_user.username}, "
                f"model={request.model}, messages={len(request.messages)}"
            )

            # Send request to Ollama
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=ollama_request
            )
            response.raise_for_status()

            # Handle streaming vs non-streaming
            if request.stream:
                return StreamingResponse(
                    response.aiter_bytes(),
                    media_type="application/x-ndjson"
                )
            else:
                result = response.json()
                logger.info(
                    f"LLM chat complete: user={current_user.username}"
                )
                return result

    except httpx.TimeoutException:
        logger.error(f"LLM chat timeout for user {current_user.username}")
        raise HTTPException(
            status_code=504,
            detail="LLM chat timeout (>120s)"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama HTTP error: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Ollama service error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"LLM chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete chat: {str(e)}"
        )

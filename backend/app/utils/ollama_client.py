"""
Ollama Client — direct HTTP calls to the Ollama REST API.
No SDK, no LangChain — just httpx.
"""

import httpx
from app.config import settings


async def generate(prompt: str, system_prompt: str = "") -> str:
    """
    Send a prompt to Ollama and get the full response.
    Uses the /api/generate endpoint with stream=false.
    """
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    if system_prompt:
        payload["system"] = system_prompt

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


async def generate_stream(prompt: str, system_prompt: str = ""):
    """
    Send a prompt to Ollama and stream the response token by token.
    Yields strings as they arrive.
    """
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
    }

    if system_prompt:
        payload["system"] = system_prompt

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    import json
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done", False):
                        break


async def check_health() -> dict:
    """Check if Ollama is reachable and list available models."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            return {
                "status": "connected",
                "models": models,
                "configured_model": settings.OLLAMA_MODEL,
            }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "configured_model": settings.OLLAMA_MODEL,
        }

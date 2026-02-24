"""
FastAPI application entry point.
Sets up CORS, includes routers, and initializes the vector store on startup.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.vector_store import vector_store
from app.utils import ollama_client
from app.models import HealthResponse
from app.routers import documents, query


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load vector store from disk on startup."""
    print("[Startup] Loading vector store from disk...")
    vector_store.load()
    print(f"[Startup] Vector store loaded: {vector_store.total_chunks} chunks")
    yield
    print("[Shutdown] Saving vector store...")
    vector_store.save()
    print("[Shutdown] Done.")


app = FastAPI(
    title="RAG System API",
    description="A Retrieval-Augmented Generation system built from scratch with Python — no LangChain or LlamaIndex.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check system health — backend, Ollama, and vector store status."""
    ollama_status = await ollama_client.check_health()
    return HealthResponse(
        status="ok",
        ollama=ollama_status,
        total_documents=len(vector_store.get_all_doc_ids()),
        total_chunks=vector_store.total_chunks,
    )

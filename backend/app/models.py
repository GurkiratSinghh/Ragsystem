"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class SourceInfo(BaseModel):
    filename: str
    chunk_index: int
    score: float
    text_preview: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
    num_chunks_searched: int
    error: Optional[str] = None


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    num_chunks: int
    upload_time: Optional[str] = None


class UploadResponse(BaseModel):
    message: str
    doc_id: str
    filename: str
    num_chunks: int
    total_chunks_in_store: int


class DeleteResponse(BaseModel):
    message: str
    doc_id: str
    chunks_removed: int


class HealthResponse(BaseModel):
    status: str
    ollama: dict
    total_documents: int
    total_chunks: int

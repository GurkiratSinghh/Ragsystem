"""
Query endpoint — accepts a question and returns RAG-generated answer.
"""

from fastapi import APIRouter
from app.models import QueryRequest, QueryResponse
from app.core import rag_pipeline

router = APIRouter(prefix="/api", tags=["Query"])


@router.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question about the uploaded documents.
    The RAG pipeline will:
    1. Embed the question
    2. Retrieve relevant chunks
    3. Generate an answer using Ollama
    """
    result = await rag_pipeline.query(
        question=request.question,
        top_k=request.top_k,
    )

    return QueryResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        num_chunks_searched=result.get("num_chunks_searched", 0),
        error=result.get("error"),
    )

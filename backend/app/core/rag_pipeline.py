"""
RAG Pipeline — orchestrates the full Retrieval-Augmented Generation flow.
1. Embed the user query with SBERT
2. Retrieve top-k relevant chunks from the vector store
3. Build a context-enriched prompt
4. Call Ollama for generation
5. Return the answer with source references
"""

from app.core.embedder import embedder
from app.core.vector_store import vector_store
from app.utils import ollama_client
from app.config import settings


SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.
Follow these rules strictly:
1. ONLY use information from the provided context to answer the question.
2. If the context doesn't contain enough information, say "I don't have enough information in the provided documents to answer this question."
3. Be concise and accurate in your responses.
4. When possible, mention which part of the document your answer comes from.
5. Do not make up or hallucinate any information."""


def build_prompt(query: str, context_chunks: list[dict]) -> str:
    """Build the RAG prompt with retrieved context."""
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk.get("filename", "Unknown")
        text = chunk.get("text", "")
        context_parts.append(f"[Source {i}: {source}]\n{text}")

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""Context from uploaded documents:

{context}

---

User Question: {query}

Please answer the question based ONLY on the context provided above."""

    return prompt


async def query(question: str, top_k: int = None) -> dict:
    """
    Full RAG pipeline:
    1. Embed the question
    2. Retrieve relevant chunks
    3. Generate answer via Ollama
    4. Return answer + sources
    """
    if top_k is None:
        top_k = settings.TOP_K

    # Step 1: Embed the query
    query_embedding = embedder.embed_query(question)

    # Step 2: Retrieve top-k chunks
    results = vector_store.search(query_embedding, top_k=top_k)

    if not results:
        return {
            "answer": "No documents have been uploaded yet. Please upload some documents first, then ask your question.",
            "sources": [],
            "num_chunks_searched": vector_store.total_chunks,
        }

    # Step 3: Build prompt
    prompt = build_prompt(question, results)

    # Step 4: Generate answer via Ollama
    try:
        answer = await ollama_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
    except Exception as e:
        return {
            "answer": f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running with model '{settings.OLLAMA_MODEL}'.",
            "sources": [],
            "error": str(e),
        }

    # Step 5: Return answer + sources
    sources = [
        {
            "filename": r.get("filename", "Unknown"),
            "chunk_index": r.get("chunk_index", 0),
            "score": round(r.get("score", 0), 4),
            "text_preview": r.get("text", "")[:200] + "..."
                if len(r.get("text", "")) > 200 else r.get("text", ""),
        }
        for r in results
    ]

    return {
        "answer": answer,
        "sources": sources,
        "num_chunks_searched": vector_store.total_chunks,
    }

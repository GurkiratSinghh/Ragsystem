"""
Document management endpoints — upload, list, and delete documents.
"""

import os
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.core.document_processor import process_file
from app.core.chunker import chunk_text
from app.core.embedder import embedder
from app.core.vector_store import vector_store
from app.models import UploadResponse, DocumentInfo, DeleteResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# Simple metadata store for uploaded documents
DOCS_META_PATH = os.path.join(settings.DATA_DIR, "documents_meta.json")


def _load_docs_meta() -> dict:
    if os.path.exists(DOCS_META_PATH):
        with open(DOCS_META_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_docs_meta(meta: dict):
    with open(DOCS_META_PATH, "w") as f:
        json.dump(meta, f, indent=2)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document (PDF, TXT, or DOCX), process it, and add to vector store."""

    # Validate file type
    allowed_extensions = {".pdf", ".txt", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {list(allowed_extensions)}"
        )

    # Generate unique doc ID
    doc_id = str(uuid.uuid4())[:8]

    # Save uploaded file to disk
    file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{file.filename}")
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Extract text
    try:
        text = process_file(file_path)
    except ValueError as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

    # Chunk the text
    chunks = chunk_text(
        text,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        doc_id=doc_id,
        filename=file.filename,
    )

    if not chunks:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="No text chunks could be created from this file.")

    # Embed the chunks
    texts_to_embed = [c["text"] for c in chunks]
    embeddings = embedder.embed_texts(texts_to_embed)

    # Add to vector store
    vector_store.add(embeddings, chunks)

    # Save document metadata
    docs_meta = _load_docs_meta()
    docs_meta[doc_id] = {
        "filename": file.filename,
        "file_path": file_path,
        "num_chunks": len(chunks),
        "upload_time": datetime.now().isoformat(),
    }
    _save_docs_meta(docs_meta)

    return UploadResponse(
        message=f"Document '{file.filename}' uploaded and processed successfully.",
        doc_id=doc_id,
        filename=file.filename,
        num_chunks=len(chunks),
        total_chunks_in_store=vector_store.total_chunks,
    )


@router.get("/", response_model=list[DocumentInfo])
async def list_documents():
    """List all uploaded documents."""
    docs_meta = _load_docs_meta()
    documents = []
    for doc_id, meta in docs_meta.items():
        documents.append(
            DocumentInfo(
                doc_id=doc_id,
                filename=meta["filename"],
                num_chunks=meta["num_chunks"],
                upload_time=meta.get("upload_time"),
            )
        )
    return documents


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    """Delete a document and remove its chunks from the vector store."""
    docs_meta = _load_docs_meta()

    if doc_id not in docs_meta:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    # Remove from vector store
    chunks_removed = vector_store.delete_by_doc_id(doc_id)

    # Delete the file from disk
    file_path = docs_meta[doc_id].get("file_path", "")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    # Remove from metadata
    filename = docs_meta[doc_id]["filename"]
    del docs_meta[doc_id]
    _save_docs_meta(docs_meta)

    return DeleteResponse(
        message=f"Document '{filename}' deleted successfully.",
        doc_id=doc_id,
        chunks_removed=chunks_removed,
    )

"""
Vector Store — NumPy-based in-memory vector store with cosine similarity search.
Persists to disk as .npy (embeddings) + .json (metadata).
No external vector DB needed.
"""

import os
import json
import numpy as np
from typing import Optional
from app.config import settings


class VectorStore:
    """
    Simple vector store using NumPy arrays.
    Supports add, search, delete, save, and load operations.
    """

    def __init__(self):
        self.embeddings: Optional[np.ndarray] = None  # shape: (n, dim)
        self.chunks: list[dict] = []  # metadata for each embedding
        self._embeddings_path = os.path.join(settings.DATA_DIR, "embeddings.npy")
        self._chunks_path = os.path.join(settings.DATA_DIR, "chunks.json")

    def add(self, embeddings: np.ndarray, chunks: list[dict]):
        """
        Add embeddings and their corresponding chunk metadata.
        embeddings: np.ndarray of shape (n, dim)
        chunks: list of dicts with 'text', 'doc_id', 'filename', 'chunk_index'
        """
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        self.chunks.extend(chunks)
        self.save()

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict]:
        """
        Find the top-k most similar chunks using cosine similarity.
        Returns list of dicts: [{...chunk_metadata, "score": float}, ...]
        """
        if self.embeddings is None or len(self.chunks) == 0:
            return []

        # Cosine similarity: dot(a, b) / (||a|| * ||b||)
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        emb_norms = self.embeddings / (
            np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-10
        )
        similarities = np.dot(emb_norms, query_norm)

        # Get top-k indices
        top_k = min(top_k, len(similarities))
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            result = {**self.chunks[idx], "score": float(similarities[idx])}
            results.append(result)

        return results

    def delete_by_doc_id(self, doc_id: str) -> int:
        """
        Remove all chunks belonging to a specific document.
        Returns the number of chunks removed.
        """
        if not self.chunks:
            return 0

        # Find indices to keep
        keep_indices = [i for i, c in enumerate(self.chunks) if c.get("doc_id") != doc_id]
        removed = len(self.chunks) - len(keep_indices)

        if removed == 0:
            return 0

        if keep_indices:
            self.embeddings = self.embeddings[keep_indices]
            self.chunks = [self.chunks[i] for i in keep_indices]
        else:
            self.embeddings = None
            self.chunks = []

        self.save()
        return removed

    def save(self):
        """Persist embeddings and chunk metadata to disk."""
        if self.embeddings is not None:
            np.save(self._embeddings_path, self.embeddings)
        elif os.path.exists(self._embeddings_path):
            os.remove(self._embeddings_path)

        with open(self._chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

    def load(self):
        """Load embeddings and chunk metadata from disk."""
        if os.path.exists(self._embeddings_path):
            self.embeddings = np.load(self._embeddings_path)
        else:
            self.embeddings = None

        if os.path.exists(self._chunks_path):
            with open(self._chunks_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        else:
            self.chunks = []

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    def get_all_doc_ids(self) -> list[str]:
        """Get unique document IDs in the store."""
        return list(set(c.get("doc_id", "") for c in self.chunks))


# Global instance
vector_store = VectorStore()

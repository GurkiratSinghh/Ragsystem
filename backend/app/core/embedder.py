"""
SBERT Embedder — wraps sentence-transformers for embedding texts and queries.
Loads the model once (singleton) to avoid repeated loading overhead.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings


class Embedder:
    """Singleton-style SBERT embedding wrapper."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            print(f"[Embedder] Loading SBERT model: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print("[Embedder] Model loaded successfully.")

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Embed a list of texts into dense vectors.
        Returns: np.ndarray of shape (len(texts), embedding_dim)
        """
        self._load_model()
        embeddings = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.
        Returns: np.ndarray of shape (embedding_dim,)
        """
        self._load_model()
        embedding = self._model.encode([query], show_progress_bar=False, convert_to_numpy=True)
        return embedding[0]

    @property
    def embedding_dim(self) -> int:
        """Get the dimensionality of the embeddings."""
        self._load_model()
        return self._model.get_sentence_embedding_dimension()


# Global instance
embedder = Embedder()

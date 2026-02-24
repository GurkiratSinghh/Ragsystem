"""
Text chunker — splits extracted text into overlapping chunks.
Attempts to split on sentence boundaries for better context preservation.
"""

import re
from typing import Optional


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    doc_id: Optional[str] = None,
    filename: Optional[str] = None,
) -> list[dict]:
    """
    Split text into overlapping chunks, preserving sentence boundaries.

    Returns a list of dicts:
        [{"text": "...", "doc_id": "...", "filename": "...", "chunk_index": 0}, ...]
    """
    if not text.strip():
        return []

    # Split into sentences using regex
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""
    current_start = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # If adding this sentence exceeds chunk_size, save current and start new
        if len(current_chunk) + len(sentence) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())

            # Create overlap by keeping the last `chunk_overlap` characters
            if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                current_chunk = current_chunk[-chunk_overlap:] + " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Build metadata-rich chunk dicts
    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            "text": chunk,
            "doc_id": doc_id or "unknown",
            "filename": filename or "unknown",
            "chunk_index": i,
        })

    return result

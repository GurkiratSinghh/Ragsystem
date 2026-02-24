"""
Document processor — extracts raw text from PDF, DOCX, and TXT files.
No LangChain or LlamaIndex — just PyPDF2 and python-docx.
"""

import os
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyPDF2."""
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    doc = Document(file_path)
    text_parts = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text)
    return "\n\n".join(text_parts)


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def process_file(file_path: str) -> str:
    """
    Auto-detect file type and extract text.
    Raises ValueError for unsupported file types.
    """
    ext = os.path.splitext(file_path)[1].lower()

    extractors = {
        ".pdf": extract_text_from_pdf,
        ".docx": extract_text_from_docx,
        ".txt": extract_text_from_txt,
    }

    if ext not in extractors:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(extractors.keys())}")

    text = extractors[ext](file_path)

    if not text.strip():
        raise ValueError(f"No text could be extracted from {os.path.basename(file_path)}")

    return text

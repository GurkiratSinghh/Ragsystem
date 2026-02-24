/**
 * API Client — all HTTP calls to the FastAPI backend.
 */

const API_BASE = 'http://localhost:8000/api';

export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
}

export async function listDocuments() {
    const response = await fetch(`${API_BASE}/documents/`);
    if (!response.ok) throw new Error('Failed to fetch documents');
    return response.json();
}

export async function deleteDocument(docId) {
    const response = await fetch(`${API_BASE}/documents/${docId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Delete failed');
    }

    return response.json();
}

export async function queryDocuments(question, topK = null) {
    const body = { question };
    if (topK) body.top_k = topK;

    const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Query failed');
    }

    return response.json();
}

export async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (!response.ok) throw new Error('Backend unreachable');
        return response.json();
    } catch (err) {
        return {
            status: 'error',
            ollama: { status: 'disconnected' },
            total_documents: 0,
            total_chunks: 0,
            error: err.message,
        };
    }
}

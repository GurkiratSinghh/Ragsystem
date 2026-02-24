import { useState, useEffect } from 'react';
import { listDocuments, deleteDocument } from '../api/client';

export default function DocumentList({ refreshKey }) {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [deleting, setDeleting] = useState(null);

    const fetchDocs = async () => {
        setLoading(true);
        try {
            const docs = await listDocuments();
            setDocuments(docs);
        } catch (err) {
            console.error('Failed to fetch documents:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDocs();
    }, [refreshKey]);

    const handleDelete = async (docId, filename) => {
        if (!confirm(`Delete "${filename}"?`)) return;

        setDeleting(docId);
        try {
            await deleteDocument(docId);
            setDocuments((prev) => prev.filter((d) => d.doc_id !== docId));
        } catch (err) {
            alert('Delete failed: ' + err.message);
        } finally {
            setDeleting(null);
        }
    };

    return (
        <div className="doc-list-section">
            <h3 className="section-title">
                <span className="icon">📚</span> Documents
                <span className="badge">{documents.length}</span>
            </h3>

            {loading ? (
                <div className="doc-loading">
                    <div className="spinner small" />
                </div>
            ) : documents.length === 0 ? (
                <p className="empty-state">No documents uploaded yet</p>
            ) : (
                <div className="doc-list">
                    {documents.map((doc) => (
                        <div key={doc.doc_id} className="doc-item">
                            <div className="doc-info">
                                <span className="doc-icon">
                                    {doc.filename.endsWith('.pdf')
                                        ? '📕'
                                        : doc.filename.endsWith('.docx')
                                            ? '📘'
                                            : '📝'}
                                </span>
                                <div className="doc-details">
                                    <span className="doc-name" title={doc.filename}>
                                        {doc.filename}
                                    </span>
                                    <span className="doc-meta">{doc.num_chunks} chunks</span>
                                </div>
                            </div>
                            <button
                                className="delete-btn"
                                onClick={() => handleDelete(doc.doc_id, doc.filename)}
                                disabled={deleting === doc.doc_id}
                                title="Delete document"
                            >
                                {deleting === doc.doc_id ? '⏳' : '🗑️'}
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

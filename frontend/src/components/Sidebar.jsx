import { useState, useEffect } from 'react';
import { checkHealth } from '../api/client';
import DocumentUpload from './DocumentUpload';
import DocumentList from './DocumentList';

export default function Sidebar() {
    const [health, setHealth] = useState(null);
    const [refreshKey, setRefreshKey] = useState(0);

    useEffect(() => {
        const fetchHealth = async () => {
            const h = await checkHealth();
            setHealth(h);
        };
        fetchHealth();
        const interval = setInterval(fetchHealth, 15000);
        return () => clearInterval(interval);
    }, []);

    const handleUploadSuccess = () => {
        setRefreshKey((k) => k + 1);
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <h1 className="logo">
                    <span className="logo-icon">🧠</span> RAG System
                </h1>
                <p className="logo-subtitle">Pure Python • No Frameworks</p>
            </div>

            {/* Status Indicators */}
            <div className="status-bar">
                <div className={`status-item ${health?.status === 'ok' ? 'online' : 'offline'}`}>
                    <span className="status-dot" />
                    Backend
                </div>
                <div
                    className={`status-item ${health?.ollama?.status === 'connected' ? 'online' : 'offline'
                        }`}
                >
                    <span className="status-dot" />
                    Ollama
                </div>
                <div className="status-item info">
                    <span className="status-count">{health?.total_chunks || 0}</span> chunks
                </div>
            </div>

            <div className="sidebar-content">
                <DocumentUpload onUploadSuccess={handleUploadSuccess} />
                <DocumentList refreshKey={refreshKey} />
            </div>

            <div className="sidebar-footer">
                <p>Built with SBERT + Ollama + FastAPI</p>
            </div>
        </aside>
    );
}

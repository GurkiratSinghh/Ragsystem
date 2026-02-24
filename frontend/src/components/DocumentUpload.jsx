import { useState, useRef, useCallback } from 'react';
import { uploadDocument } from '../api/client';

export default function DocumentUpload({ onUploadSuccess }) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null);
    const fileInputRef = useRef(null);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) handleFile(files[0]);
    }, []);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
        e.target.value = '';
    };

    const handleFile = async (file) => {
        const allowed = ['.pdf', '.txt', '.docx'];
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowed.includes(ext)) {
            setUploadStatus({ type: 'error', message: `Unsupported file type: ${ext}` });
            return;
        }

        setUploading(true);
        setUploadStatus(null);

        try {
            const result = await uploadDocument(file);
            setUploadStatus({
                type: 'success',
                message: `"${result.filename}" uploaded — ${result.num_chunks} chunks created`,
            });
            if (onUploadSuccess) onUploadSuccess();
        } catch (err) {
            setUploadStatus({ type: 'error', message: err.message });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="upload-section">
            <h3 className="section-title">
                <span className="icon">📄</span> Upload Documents
            </h3>

            <div
                className={`drop-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => !uploading && fileInputRef.current?.click()}
            >
                {uploading ? (
                    <div className="upload-progress">
                        <div className="spinner" />
                        <p>Processing document...</p>
                    </div>
                ) : (
                    <>
                        <div className="drop-icon">⬆️</div>
                        <p className="drop-text">
                            Drag & drop or <span className="browse-link">browse</span>
                        </p>
                        <p className="drop-hint">PDF, TXT, DOCX supported</p>
                    </>
                )}
            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.docx"
                onChange={handleFileSelect}
                hidden
            />

            {uploadStatus && (
                <div className={`upload-status ${uploadStatus.type}`}>
                    <span>{uploadStatus.type === 'success' ? '✅' : '❌'}</span>
                    {uploadStatus.message}
                </div>
            )}
        </div>
    );
}

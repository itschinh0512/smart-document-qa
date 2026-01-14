import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = ({ baseUrl, onUploadSuccess }) => {
    const [loading, setLoading] = useState(false);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file); // Sends as string($binary)

        setLoading(true);
        try {
            await axios.post(`${baseUrl}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert("Document indexed successfully!");
            onUploadSuccess();
        } catch (err) {
            alert("Upload failed. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="upload-bar">
            <div>
                <strong>PDF Document</strong>
                <p style={{ margin: 0, fontSize: '0.8rem', color: '#888' }}>Upload for RAG indexing</p>
            </div>
            <input type="file" onChange={handleFileChange} accept=".pdf" id="pdf-input" hidden />
            <button onClick={() => document.getElementById('pdf-input').click()} disabled={loading}>
                {loading ? "Processing..." : "Upload PDF"}
            </button>
        </div>
    );
};

export default FileUpload;
import React from 'react';

const Sidebar = ({ health, stats, topK, setTopK }) => {
    return (
        <div className="sidebar">
            <h3>Smart Document Q&A</h3>
            <div className="status-badge" style={{ color: health === 'Online' ? '#10b981' : '#ef4444' }}>
                ● System {health}
            </div>

            <div className="stat-item">
                <small>Total Documents</small>
                <h4>{stats.total_docs || 0}</h4>
            </div>

            <div className="control-group">
                <label><small>Context Depth (Top-K)</small></label>
                <input
                    type="range" min="1" max="10"
                    value={topK}
                    onChange={(e) => setTopK(parseInt(e.target.value))}
                />
                <center>{topK}</center>
            </div>
        </div>
    );
};

export default Sidebar;
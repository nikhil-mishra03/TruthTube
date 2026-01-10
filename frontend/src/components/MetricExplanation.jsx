import { useState } from 'react';
import './MetricExplanation.css';

const METRICS = [
    {
        id: 'density',
        icon: '🧠',
        name: 'Density',
        description: 'The frequency of valuable information and insights provided in the video. Higher score means more substance.',
        color: '#8b5cf6',
    },
    {
        id: 'redundancy',
        icon: '🗑️',
        name: 'Redundancy',
        description: 'The amount of repetitive or unnecessary information. Lower score is better.',
        color: '#ef4444',
    },
    {
        id: 'title',
        icon: '🔍',
        name: 'Title Match',
        description: 'How accurately the video title reflects the actual content. Higher score indicates better relevance.',
        color: '#06b6d4',
    },
    {
        id: 'originality',
        icon: '💡',
        name: 'Originality',
        description: 'The uniqueness and novelty of the content and perspectives presented. Higher score suggests fresh insights.',
        color: '#ec4899',
    },
];

export default function MetricExplanation() {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <div className="metric-explanation">
            <button
                className="explanation-header"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <h3>Metric Explanation</h3>
                <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▲</span>
            </button>

            {isExpanded && (
                <div className="explanation-grid">
                    {METRICS.map((metric) => (
                        <div key={metric.id} className="metric-item">
                            <div className="metric-header">
                                <span className="metric-icon">{metric.icon}</span>
                                <span className="metric-name" style={{ color: metric.color }}>
                                    {metric.name}:
                                </span>
                            </div>
                            <p className="metric-description">{metric.description}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

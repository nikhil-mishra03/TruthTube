import { useState } from 'react';
import './DeepAnalysis.css';

/**
 * Deep analysis section showing detailed information for all videos
 */
export default function DeepAnalysis({ videos }) {
    const [expandedVideo, setExpandedVideo] = useState(null);

    if (!videos || videos.length === 0) return null;

    const toggleVideo = (id) => {
        setExpandedVideo(expandedVideo === id ? null : id);
    };

    return (
        <div className="deep-analysis">
            <h2 className="section-title">🔬 Deep Analysis</h2>
            <p className="section-subtitle">Detailed breakdown of each video's content</p>

            <div className="analysis-list">
                {videos.map((video, index) => (
                    <div key={video.youtube_id} className="analysis-item">
                        <button
                            className="analysis-header"
                            onClick={() => toggleVideo(video.youtube_id)}
                        >
                            <div className="header-left">
                                <span className="rank-indicator">#{index + 1}</span>
                                <span className="video-name">{video.title}</span>
                            </div>
                            <span className={`expand-arrow ${expandedVideo === video.youtube_id ? 'expanded' : ''}`}>
                                ▼
                            </span>
                        </button>

                        {expandedVideo === video.youtube_id && (
                            <div className="analysis-content">
                                <div className="analysis-grid">
                                    {/* Key Facts */}
                                    <div className="analysis-block">
                                        <h4>📝 Key Facts Extracted</h4>
                                        <ul className="facts-list">
                                            {video.density.key_facts.map((fact, i) => (
                                                <li key={i}>{fact}</li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Title Analysis */}
                                    <div className="analysis-block">
                                        <h4>🎯 Title Relevance</h4>
                                        <p className="analysis-text">
                                            {video.title_relevance.explanation}
                                        </p>
                                        {video.title_relevance.is_clickbait && (
                                            <div className="warning-badge">
                                                ⚠️ Potential clickbait detected
                                            </div>
                                        )}
                                    </div>

                                    {/* Redundancy Examples */}
                                    <div className="analysis-block">
                                        <h4>🔄 Redundancy Notes</h4>
                                        {video.redundancy.examples && video.redundancy.examples.length > 0 ? (
                                            <ul className="examples-list">
                                                {video.redundancy.examples.map((example, i) => (
                                                    <li key={i}>{example}</li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <p className="analysis-text">No significant redundancy detected.</p>
                                        )}
                                    </div>

                                    {/* Originality */}
                                    <div className="analysis-block">
                                        <h4>✨ Unique Aspects</h4>
                                        {video.originality.unique_aspects && video.originality.unique_aspects.length > 0 ? (
                                            <ul className="unique-list">
                                                {video.originality.unique_aspects.map((aspect, i) => (
                                                    <li key={i}>{aspect}</li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <p className="analysis-text">Single video - no comparison available.</p>
                                        )}
                                    </div>
                                </div>

                                {/* Quick Stats */}
                                <div className="quick-stats">
                                    <div className="stat">
                                        <span className="stat-label">Duration</span>
                                        <span className="stat-value">{Math.floor(video.duration_seconds / 60)} min</span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Facts Found</span>
                                        <span className="stat-value">{video.density.facts_count}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Insights/Min</span>
                                        <span className="stat-value">{video.density.insights_per_minute.toFixed(1)}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Filler %</span>
                                        <span className="stat-value">{video.redundancy.filler_percentage}%</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

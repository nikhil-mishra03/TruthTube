import MetricCircle from './MetricCircle';
import './ResultCard.css';

/**
 * Card displaying video analysis results
 * @param {Object} props
 * @param {Object} props.video - Video analysis data
 * @param {number} props.rank - Video rank
 */
export default function ResultCard({ video, rank }) {
    const getRankBadge = () => {
        if (rank === 1) return { emoji: '🏆', text: 'Best Choice', class: 'gold' };
        if (rank === 2) return { emoji: '👍', text: 'Good Alternative', class: 'silver' };
        return { emoji: '📊', text: `Rank #${rank}`, class: 'default' };
    };

    const badge = getRankBadge();

    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className={`result-card ${badge.class}`}>
            <div className="rank-badge">
                <span className="rank-emoji">{badge.emoji}</span>
                <span className="rank-text">{badge.text}</span>
            </div>

            <div className="card-content">
                <div className="video-info">
                    <img
                        src={video.thumbnail_url}
                        alt={video.title}
                        className="thumbnail"
                    />
                    <div className="video-details">
                        <h3 className="video-title">{video.title}</h3>
                        <span className="video-duration">{formatDuration(video.duration_seconds)}</span>
                    </div>
                </div>

                <div className="metrics-grid">
                    <MetricCircle
                        value={video.density.score}
                        label="Density"
                        color="density"
                    />
                    <MetricCircle
                        value={video.redundancy.score}
                        label="Redundancy"
                        color="redundancy"
                        inverted={true}
                    />
                    <MetricCircle
                        value={video.title_relevance.score}
                        label="Title Match"
                        color="title"
                    />
                    <MetricCircle
                        value={video.originality.score}
                        label="Originality"
                        color="originality"
                    />
                </div>

                <div className="key-facts">
                    <h4>Key Facts</h4>
                    <ul>
                        {video.density.key_facts.slice(0, 3).map((fact, i) => (
                            <li key={i}>{fact}</li>
                        ))}
                    </ul>
                </div>

                {video.title_relevance.is_clickbait && (
                    <div className="clickbait-warning">
                        ⚠️ Potential clickbait detected
                    </div>
                )}

                <p className="recommendation">{video.recommendation}</p>
            </div>
        </div>
    );
}

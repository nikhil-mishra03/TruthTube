import MetricCircle from './MetricCircle';
import './VideoCard.css';

/**
 * Compact video card for results grid (horizontal layout)
 */
export default function VideoCard({ video, rank, onClick, animationDelay = 0 }) {
    const getRankBadge = () => {
        if (rank === 1) return { emoji: '🏆', text: '#1', class: 'gold' };
        if (rank === 2) return { emoji: '👍', text: '#2', class: 'silver' };
        if (rank === 3) return { emoji: '🥉', text: '#3', class: 'bronze' };
        return { emoji: '📊', text: `#${rank}`, class: 'default' };
    };

    const badge = getRankBadge();

    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const getRecommendation = () => {
        if (rank === 1) return "Highly recommended: Excellent density of information, strong title match, and original content.";
        if (rank === 2) return "Solid choice: Good title match and reasonable originality, though some redundancy exists.";
        return "Worth watching: Contains useful information with room for improvement.";
    };

    return (
        <div
            className={`video-card ${badge.class}`}
            onClick={onClick}
            style={{ animationDelay: `${animationDelay}ms` }}
        >
            <div className="card-header">
                <div className="thumbnail-container">
                    <img
                        src={video.thumbnail_url}
                        alt={video.title}
                        className="thumbnail"
                    />
                    <span className="duration-badge">{formatDuration(video.duration_seconds)}</span>
                </div>

                <div className="video-info">
                    <h3 className="video-title">{video.title}</h3>
                    <p className="recommendation">{getRecommendation()}</p>
                </div>

                <div className={`rank-badge ${badge.class}`}>
                    <span className="rank-emoji">{badge.emoji}</span>
                    <span className="rank-number">{badge.text}</span>
                </div>
            </div>

            <div className="metrics-row">
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
        </div>
    );
}

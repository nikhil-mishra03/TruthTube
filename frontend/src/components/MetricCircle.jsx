import './MetricCircle.css';

/**
 * Circular progress indicator for metrics
 * @param {Object} props
 * @param {number} props.value - Score value (0-100)
 * @param {string} props.label - Metric label
 * @param {string} props.color - Color theme (density, redundancy, title, originality)
 * @param {boolean} props.inverted - If true, lower is better (for redundancy)
 */
export default function MetricCircle({ value, label, color = 'default', inverted = false }) {
    const radius = 36;
    const circumference = 2 * Math.PI * radius;
    const progress = (value / 100) * circumference;
    const offset = circumference - progress;

    // Determine color class based on score (higher is better, unless inverted)
    const getScoreClass = () => {
        const effectiveScore = inverted ? (100 - value) : value;
        if (effectiveScore >= 70) return 'good';
        if (effectiveScore >= 40) return 'medium';
        return 'poor';
    };

    return (
        <div className={`metric-circle ${color}`}>
            <svg viewBox="0 0 80 80" className="circle-svg">
                <circle
                    className="circle-bg"
                    cx="40"
                    cy="40"
                    r={radius}
                />
                <circle
                    className={`circle-progress ${getScoreClass()}`}
                    cx="40"
                    cy="40"
                    r={radius}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className="circle-content">
                <span className="circle-value">{value}</span>
            </div>
            <span className="circle-label">{label}</span>
        </div>
    );
}

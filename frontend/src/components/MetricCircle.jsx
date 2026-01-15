import { useEffect, useState } from 'react';
import './MetricCircle.css';

/**
 * Circular progress indicator for metrics with animation
 * @param {Object} props
 * @param {number} props.value - Score value (0-100)
 * @param {string} props.label - Metric label
 * @param {string} props.color - Color theme (density, redundancy, title, originality)
 * @param {boolean} props.inverted - If true, lower is better (for redundancy)
 */
export default function MetricCircle({ value, label, color = 'default', inverted = false }) {
    const [animatedValue, setAnimatedValue] = useState(0);
    const radius = 36;
    const circumference = 2 * Math.PI * radius;
    const progress = (animatedValue / 100) * circumference;
    const offset = circumference - progress;

    // Animate the value from 0 to target
    useEffect(() => {
        // Reset to 0 first for re-animation
        setAnimatedValue(0);

        // Small delay to ensure CSS transition kicks in
        const timeout = setTimeout(() => {
            setAnimatedValue(value);
        }, 100);

        return () => clearTimeout(timeout);
    }, [value]);

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
                {/* Glow filter */}
                <defs>
                    <filter id={`glow-${color}`} x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>
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
                    filter={`url(#glow-${color})`}
                />
            </svg>
            <div className="circle-content">
                <span className="circle-value">{Math.round(animatedValue)}</span>
            </div>
            <span className="circle-label">{label}</span>
        </div>
    );
}

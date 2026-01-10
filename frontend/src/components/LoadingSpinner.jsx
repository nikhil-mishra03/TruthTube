import './LoadingSpinner.css';

export default function LoadingSpinner({ message = 'Analyzing videos...' }) {
    return (
        <div className="loading-container">
            <div className="spinner">
                <div className="spinner-ring"></div>
                <div className="spinner-ring"></div>
                <div className="spinner-ring"></div>
            </div>
            <p className="loading-message">{message}</p>
            <p className="loading-hint">This may take 30-60 seconds</p>
        </div>
    );
}

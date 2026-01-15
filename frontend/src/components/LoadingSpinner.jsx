import { useEffect, useState } from 'react';
import './LoadingSpinner.css';

const STEPS = [
    { id: 1, text: 'Validating URLs', icon: '🔗' },
    { id: 2, text: 'Fetching video data', icon: '📥' },
    { id: 3, text: 'Analyzing content density', icon: '🧠' },
    { id: 4, text: 'Checking redundancy', icon: '🔄' },
    { id: 5, text: 'Evaluating title match', icon: '🎯' },
    { id: 6, text: 'Comparing originality', icon: '✨' },
    { id: 7, text: 'Ranking videos', icon: '🏆' },
];

export default function LoadingSpinner({ message = 'Analyzing videos...' }) {
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        // Simulate step progression
        const stepDurations = [500, 2000, 8000, 8000, 5000, 8000, 2000];
        let stepIndex = 0;
        let timeout;

        const advanceStep = () => {
            if (stepIndex < STEPS.length) {
                setCurrentStep(stepIndex);
                timeout = setTimeout(() => {
                    stepIndex++;
                    advanceStep();
                }, stepDurations[stepIndex] || 3000);
            }
        };

        advanceStep();
        return () => clearTimeout(timeout);
    }, []);

    return (
        <div className="loading-container">
            <div className="loading-header">
                <div className="spinner">
                    <div className="spinner-ring"></div>
                    <div className="spinner-ring"></div>
                    <div className="spinner-ring"></div>
                </div>
                <p className="loading-message">{message}</p>
            </div>

            <div className="steps-container">
                {STEPS.map((step, index) => (
                    <div
                        key={step.id}
                        className={`step ${index < currentStep ? 'completed' : ''} ${index === currentStep ? 'active' : ''}`}
                    >
                        <span className="step-icon">{step.icon}</span>
                        <span className="step-text">{step.text}</span>
                        {index < currentStep && <span className="step-check">✓</span>}
                        {index === currentStep && <span className="step-dots">...</span>}
                    </div>
                ))}
            </div>

            <p className="loading-hint">This may take 30-60 seconds</p>
        </div>
    );
}

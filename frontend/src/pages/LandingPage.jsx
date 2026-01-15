import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

export default function LandingPage() {
    const navigate = useNavigate();

    const scrollToSection = (id) => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="landing-page">
            {/* Hero Section */}
            <section className="hero">
                <div className="hero-content">
                    <h1 className="hero-title">
                        <span className="title-gradient">TruthTube</span>
                    </h1>
                    <p className="hero-tagline">Find the Best Video to Watch</p>
                    <p className="hero-description">
                        Stop wasting time on clickbait. Get AI-powered analysis to find the most informative YouTube videos.
                    </p>
                    <div className="hero-buttons">
                        <button className="btn-primary" onClick={() => navigate('/analyze')}>
                            🔍 Try It Now
                        </button>
                        <button className="btn-secondary" onClick={() => scrollToSection('how-it-works')}>
                            Learn More ↓
                        </button>
                    </div>
                </div>

                {/* Demo Mockup */}
                <div className="hero-mockup">
                    <div className="mockup-card">
                        <div className="mockup-header">
                            <div className="mockup-dot"></div>
                            <div className="mockup-dot"></div>
                            <div className="mockup-dot"></div>
                        </div>
                        <div className="mockup-content">
                            <div className="mockup-video">
                                <div className="video-thumb">▶</div>
                                <div className="video-info">
                                    <div className="info-line"></div>
                                    <div className="info-line short"></div>
                                </div>
                            </div>
                            <div className="mockup-metrics">
                                <div className="metric-preview density">
                                    <div className="metric-ring"></div>
                                    <span>85%</span>
                                </div>
                                <div className="metric-preview redundancy">
                                    <div className="metric-ring"></div>
                                    <span>12%</span>
                                </div>
                                <div className="metric-preview title">
                                    <div className="metric-ring"></div>
                                    <span>92%</span>
                                </div>
                                <div className="metric-preview originality">
                                    <div className="metric-ring"></div>
                                    <span>78%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className="how-it-works">
                <h2 className="section-title">How It Works</h2>
                <div className="steps-container">
                    <div className="step">
                        <div className="step-icon">🔗</div>
                        <h3>1. Paste URLs</h3>
                        <p>Simply paste multiple YouTube video URLs that you want to compare</p>
                    </div>
                    <div className="step-connector">↓</div>
                    <div className="step">
                        <div className="step-icon">🤖</div>
                        <h3>2. AI Analyzes</h3>
                        <p>Our AI evaluates content density, redundancy, and originality</p>
                    </div>
                    <div className="step-connector">↓</div>
                    <div className="step">
                        <div className="step-icon">🏆</div>
                        <h3>3. Get Rankings</h3>
                        <p>Receive a ranked list of the most valuable videos to watch</p>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features">
                <h2 className="section-title">What We Analyze</h2>
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon density">🧠</div>
                        <h3>Density</h3>
                        <p>Measures information per minute. Higher score means more substance and valuable insights.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon redundancy">🔄</div>
                        <h3>Redundancy</h3>
                        <p>Identifies repetitive or unnecessary content. Lower score is better - less filler.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon title">🎯</div>
                        <h3>Title Match</h3>
                        <p>Checks if the content delivers on the title's promise. Detects clickbait.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon originality">✨</div>
                        <h3>Originality</h3>
                        <p>Compares uniqueness against other videos. Higher score means fresh perspectives.</p>
                    </div>
                </div>
            </section>

            {/* Stats Section - Hidden until we have real data */}
            {/* 
      <section className="stats">
        <div className="stat">
          <span className="stat-number">0</span>
          <span className="stat-label">Videos Analyzed</span>
        </div>
        <div className="stat">
          <span className="stat-number">0</span>
          <span className="stat-label">Hours Saved</span>
        </div>
        <div className="stat">
          <span className="stat-number">4</span>
          <span className="stat-label">AI Metrics</span>
        </div>
      </section>
      */}

            {/* CTA Section */}
            <section className="cta">
                <h2>Ready to find the best video?</h2>
                <p>Stop guessing. Start analyzing.</p>
                <button className="btn-primary large" onClick={() => navigate('/analyze')}>
                    🔍 Start Analyzing
                </button>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <p>Powered by AI • TruthTube 2024</p>
            </footer>
        </div>
    );
}

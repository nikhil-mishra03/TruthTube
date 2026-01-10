import { useState } from 'react';
import { analyzeVideos } from './services/api';
import ResultCard from './components/ResultCard';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

// Helper to create a URL object with unique ID
const createUrlEntry = (value = '') => ({
  id: crypto.randomUUID(),
  value,
});

function App() {
  // Use objects with unique IDs instead of plain strings
  const [urls, setUrls] = useState([
    createUrlEntry(),
    createUrlEntry(),
    createUrlEntry(),
  ]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUrlChange = (id, value) => {
    setUrls(prevUrls =>
      prevUrls.map(urlObj =>
        urlObj.id === id ? { ...urlObj, value } : urlObj
      )
    );
  };

  const addUrlField = () => {
    if (urls.length < 5) {
      setUrls(prevUrls => [...prevUrls, createUrlEntry()]);
    }
  };

  const removeUrlField = (id) => {
    if (urls.length > 1) {
      setUrls(prevUrls => prevUrls.filter(urlObj => urlObj.id !== id));
    }
  };

  const handleAnalyze = async () => {
    // Filter out empty URLs and extract values
    const validUrls = urls
      .map(urlObj => urlObj.value.trim())
      .filter(url => url !== '');

    if (validUrls.length < 1) {
      setError('Please enter at least 1 YouTube URL');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await analyzeVideos(validUrls);
      setResults(data);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const isValidYoutubeUrl = (url) => {
    if (!url) return true; // Empty is okay
    return url.includes('youtube.com/watch') || url.includes('youtu.be/');
  };

  return (
    <div className="app">
      <header className="header">
        <h1 className="logo">
          <span className="logo-icon">📺</span>
          TruthTube
        </h1>
        <p className="tagline">Find the best video to watch</p>
      </header>

      <main className="main">
        <section className="input-section">
          <h2>Enter YouTube URLs</h2>
          <p className="input-hint">Add 1-5 YouTube video URLs to compare</p>

          <div className="url-inputs">
            {urls.map((urlObj, index) => (
              <div key={urlObj.id} className="url-input-row">
                <input
                  type="text"
                  value={urlObj.value}
                  onChange={(e) => handleUrlChange(urlObj.id, e.target.value)}
                  placeholder={`Paste YouTube URL ${index + 1} here...`}
                  className={`url-input ${urlObj.value && !isValidYoutubeUrl(urlObj.value) ? 'invalid' : ''}`}
                />
                {urls.length > 1 && (
                  <button
                    className="remove-btn"
                    onClick={() => removeUrlField(urlObj.id)}
                    title="Remove URL"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>

          {urls.length < 5 && (
            <button className="add-url-btn" onClick={addUrlField}>
              + Add another URL
            </button>
          )}

          <button
            className="analyze-btn"
            onClick={handleAnalyze}
            disabled={loading || urls.every(u => !u.value.trim())}
          >
            {loading ? 'Analyzing...' : '🔍 Analyze Videos'}
          </button>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </section>

        {loading && <LoadingSpinner />}

        {results && (
          <section className="results-section">
            <h2>Analysis Results</h2>
            <p className="results-summary">{results.summary}</p>

            <div className="results-grid">
              {results.videos.map((video) => (
                <ResultCard
                  key={video.youtube_id}
                  video={video}
                  rank={video.overall_rank}
                />
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Powered by AI analysis • TruthTube 2024</p>
      </footer>
    </div>
  );
}

export default App;

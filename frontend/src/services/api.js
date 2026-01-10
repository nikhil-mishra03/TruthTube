const API_BASE = 'http://localhost:8001';

/**
 * Analyze YouTube videos for quality metrics
 * @param {string[]} urls - List of YouTube URLs to analyze
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeVideos(urls) {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ urls }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Analysis failed');
  }

  return response.json();
}

/**
 * Check API health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/health`);
  return response.json();
}

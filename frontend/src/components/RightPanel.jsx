import React from 'react';

function RightPanel({ posts }) {

  // Calculate privacy stats from posts
  const total = posts.length;
  const high = posts.filter(p => p.risk_level === 'HIGH').length;
  const medium = posts.filter(p => p.risk_level === 'MEDIUM').length;
  const low = posts.filter(p => p.risk_level === 'LOW').length;

  return (
    <div className="right-panel">

      {/* SEARCH BOX */}
      <div className="search-box">
        <span>🔍</span>
        <input placeholder="Search PrivGuard" />
      </div>

      {/* PRIVACY STATS */}
      <div className="stats-card">
        <div className="stats-title">Privacy stats</div>

        <div className="stat-row">
          <span className="stat-label">Total posts</span>
          <span className="stat-value">{total}</span>
        </div>

        <div className="stat-row">
          <span className="stat-label">High risk blocked</span>
          <span className="stat-value stat-red">{high}</span>
        </div>

        <div className="stat-row">
          <span className="stat-label">Medium risk</span>
          <span className="stat-value stat-amber">{medium}</span>
        </div>

        <div className="stat-row">
          <span className="stat-label">Safe posts</span>
          <span className="stat-value stat-green">{low}</span>
        </div>

      </div>

      {/* ABOUT CARD */}
      <div className="stats-card">
        <div className="stats-title">About PrivGuard</div>
        <p className="about-text">
          Smart microblogging platform with AI-powered privacy protection.
          We scan every post before publishing to keep your personal
          information safe.
        </p>
        <div className="about-tags">
          <span className="about-tag">spaCy NLP</span>
          <span className="about-tag">Regex</span>
          <span className="about-tag">FastAPI</span>
          <span className="about-tag">React</span>
        </div>
      </div>

    </div>
  );
}

export default RightPanel;
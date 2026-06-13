// ============================================
// Feed.jsx
// PURPOSE: Displays all published posts
// Shows each post as a card with risk badge
// Posts are ordered newest first
// ============================================

import React from 'react';

// ── COMPONENT ────────────────────────────────────────────────
// Props received from App.js:
// posts → array of post objects from database

function Feed({ posts }) {

  // ── RISK BADGE HELPER ─────────────────────────────────────
  // Returns the correct CSS class and emoji for each risk level
  const getRiskBadge = (level) => {
    switch(level) {
      case 'HIGH':
        return { className: 'badge-high', label: '🔴 High Risk' };
      case 'MEDIUM':
        return { className: 'badge-medium', label: '🟡 Medium Risk' };
      default:
        return { className: 'badge-low', label: '🟢 Low Risk' };
    }
  };

  return (
    <div className="feed-section">

      {/* FEED HEADER */}
      <div className="feed-header">
        <span className="feed-title">Recent Posts</span>
        <span className="feed-count">{posts.length} posts</span>
      </div>

      {/* EMPTY STATE → shown when no posts yet */}
      {posts.length === 0 && (
        <div className="empty-feed">
          <div className="empty-icon">📭</div>
          <div className="empty-text">No posts yet. Be the first to post!</div>
        </div>
      )}

      {/* POSTS LIST */}
      {/* map() loops through each post and creates a card */}
      {posts.map((post) => {
        const badge = getRiskBadge(post.risk_level);
        return (
          <div key={post.id} className="post-card">

            {/* POST HEADER */}
            <div className="post-header">
              <div className="post-user">
                <div className="avatar avatar-sm">MM</div>
                <div>
                  <div className="post-name">Mahimashree M</div>
                  <div className="post-time">{post.timestamp}</div>
                </div>
              </div>
              {/* RISK BADGE */}
              <span className={`risk-badge ${badge.className}`}>
                {badge.label}
              </span>
            </div>

            {/* POST CONTENT */}
            <p className="post-content">{post.content}</p>

            {/* POST FOOTER */}
            <div className="post-footer">
              <span className="post-score">
                Risk score: {post.risk_score}/100
              </span>
              <div className="post-actions">
                <span className="post-action">❤️ Like</span>
                <span className="post-action">💬 Comment</span>
                <span className="post-action">🔗 Share</span>
              </div>
            </div>

          </div>
        );
      })}
    </div>
  );
}

export default Feed;
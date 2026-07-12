import React from 'react';

function Feed({ posts }) {

  const getRiskBadge = (level) => {
    switch(level) {
      case 'HIGH': return { cls: 'badge-high', label: '🔴 High risk' };
      case 'MEDIUM': return { cls: 'badge-medium', label: '🟡 Medium risk' };
      default: return { cls: 'badge-low', label: '🟢 Low risk' };
    }
  };

  if (posts.length === 0) {
    return (
      <div className="empty-feed">
        <div className="empty-icon">📭</div>
        <div className="empty-text">No posts yet. Be the first to post!</div>
      </div>
    );
  }

  return (
    <div className="feed">
      {posts.map((post) => {
        const badge = getRiskBadge(post.risk_level);
        return (
          <div key={post.id} className="post-card">

            <div className="avatar avatar-post">MM</div>

            <div className="post-content">
              <div className="post-header">
                <span className="post-name">Mahimashree M</span>
                <span className="post-handle">@MMahimashree</span>
                <span className="post-dot">·</span>
                <span className="post-time">{post.timestamp}</span>
              </div>

              <p className="post-text">{post.content}</p>

              <span className={`post-badge ${badge.cls}`}>
                {badge.label} · {post.risk_score}/100
              </span>

              <div className="post-actions">
                <span className="post-action">💬 <span>Reply</span></span>
                <span className="post-action">🔁 <span>Repost</span></span>
                <span className="post-action">❤️ <span>Like</span></span>
                <span className="post-action">📊 <span>Views</span></span>
                <span className="post-action">🔗 <span>Share</span></span>
              </div>
            </div>

          </div>
        );
      })}
    </div>
  );
}

export default Feed;
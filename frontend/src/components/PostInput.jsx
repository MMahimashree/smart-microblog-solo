import React from 'react';

function PostInput({ postText, setPostText, onPublish, isLoading }) {
  const MAX_CHARS = 280;
  const charsLeft = MAX_CHARS - postText.length;
  const counterColor = charsLeft < 20 ? '#E24B4A' : charsLeft < 50 ? '#BA7517' : '#8b98a5';

  return (
    <div className="composer">
      <div className="avatar">MM</div>
      <div className="composer-right">

        <textarea
          className="composer-input"
          placeholder="What's happening? (We'll keep it safe 🛡️)"
          value={postText}
          onChange={(e) => setPostText(e.target.value)}
          maxLength={MAX_CHARS}
          rows={3}
        />

        <div className="composer-footer">
          <div className="composer-actions">
            <div className="icon-btn" title="Add photo">📷</div>
            <div className="icon-btn" title="Add emoji">😊</div>
            <div className="icon-btn" title="Add location">📍</div>
          </div>
          <div className="composer-right-actions">
            <span style={{ fontSize: '13px', color: counterColor }}>
              {charsLeft}
            </span>
            <div className="composer-divider"></div>
            <button
              className="publish-btn"
              onClick={onPublish}
              disabled={isLoading || !postText.trim()}
            >
              {isLoading ? '🔍 Scanning...' : 'Post'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

export default PostInput;
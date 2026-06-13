// ============================================
// PostInput.jsx
// PURPOSE: The post composer component
// This is where the user types their post
// Contains: text area, character count, publish button
// ============================================

import React from 'react';
// React is needed in every component file

// ── COMPONENT ────────────────────────────────────────────────
// Props received from App.js:
// postText → current text in the text area
// setPostText → function to update the text
// onPublish → function to call when publish clicked
// isLoading → true when backend is processing

function PostInput({ postText, setPostText, onPublish, isLoading }) {

  // Maximum characters allowed (like Twitter's 280)
  const MAX_CHARS = 280;

  // How many characters are left
  const charsLeft = MAX_CHARS - postText.length;

  // Change color of counter when getting close to limit
  const counterColor = charsLeft < 20 ? '#E24B4A' : charsLeft < 50 ? '#BA7517' : '#888780';

  return (
    <div className="composer-card">

      {/* COMPOSER HEADER */}
      <div className="composer-header">
        <div className="avatar">MM</div>
        <div className="composer-label">
          What's on your mind? <span className="label-sub">(We'll keep it safe)</span>
        </div>
      </div>

      {/* TEXT AREA */}
      {/* onChange fires every time user types a character */}
      {/* e.target.value = whatever is currently in the text area */}
      <textarea
        className="post-textarea"
        placeholder="Type your post here... We'll scan it for sensitive info before publishing."
        value={postText}
        onChange={(e) => setPostText(e.target.value)}
        maxLength={MAX_CHARS}
        rows={4}
      />

      {/* COMPOSER FOOTER */}
      <div className="composer-footer">

        {/* CHARACTER COUNT */}
        <span style={{ fontSize: '12px', color: counterColor, fontWeight: charsLeft < 20 ? '500' : '400' }}>
          {charsLeft} characters left
        </span>

        {/* PUBLISH BUTTON */}
        {/* disabled when loading OR when text is empty */}
        <button
          className="publish-btn"
          onClick={onPublish}
          disabled={isLoading || !postText.trim()}
        >
          {isLoading ? (
            // Show scanning animation when loading
            <span>🔍 Scanning...</span>
          ) : (
            <span>🚀 Publish</span>
          )}
        </button>

      </div>
    </div>
  );
}

export default PostInput;
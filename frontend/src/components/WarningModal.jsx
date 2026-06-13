// ============================================
// WarningModal.jsx
// PURPOSE: Warning popup shown when HIGH risk detected
// Contains: what was found, countdown timer, action buttons
// This is the most important feature of our project!
// ============================================

import React, { useState, useEffect } from 'react';
// useState → to store the countdown number
// useEffect → to run the timer every second

// ── COMPONENT ────────────────────────────────────────────────
// Props received from App.js:
// warning → the risk result object from backend
// onConfirm → called when user clicks Post Anyway
// onCancel → called when user clicks Cancel and Edit

function WarningModal({ warning, onConfirm, onCancel }) {

  // countdown stores the current timer value (starts at 10)
  const [countdown, setCountdown] = useState(10);

  // ── COUNTDOWN TIMER ───────────────────────────────────────
  // useEffect runs when component appears on screen
  // setInterval runs a function every 1000ms (1 second)
  useEffect(() => {

    // Reset countdown to 10 every time modal opens
    setCountdown(10);

    // setInterval = run this function every 1 second
    const timer = setInterval(() => {
      setCountdown((prev) => {
        // prev = current countdown value
        if (prev <= 1) {
          // Stop the timer when it reaches 0
          clearInterval(timer);
          return 0;
        }
        // Subtract 1 each second
        return prev - 1;
      });
    }, 1000); // 1000 milliseconds = 1 second

    // Cleanup → stop the timer when modal closes
    // This prevents memory leaks
    return () => clearInterval(timer);

  }, [warning]); // re-run when warning changes (new modal open)

  // ── DETECTED ENTITIES ─────────────────────────────────────
  // Build a list of what was detected to show to user
  const entities = warning.detected_entities;

  return (
    <div className="warning-card">

      {/* WARNING HEADER */}
      <div className="warning-header">
        <span className="warning-icon">⚠️</span>
        <div>
          <div className="warning-title">Privacy risk detected!</div>
          <div className="warning-subtitle">Risk score: {warning.risk_score}/100</div>
        </div>
        <span className="risk-badge-high">HIGH</span>
      </div>

      {/* RECOMMENDATION MESSAGE */}
      <p className="warning-message">{warning.recommendation}</p>

      {/* DETECTED ENTITIES LIST */}
      {/* Only show sections that have detected items */}
      <div className="entities-section">
        <div className="entities-label">What we found:</div>
        <div className="entity-pills">

          {entities.phones.length > 0 && entities.phones.map((phone, i) => (
            <span key={i} className="entity-pill pill-red">
              📱 Phone: {phone}
            </span>
          ))}

          {entities.emails.length > 0 && entities.emails.map((email, i) => (
            <span key={i} className="entity-pill pill-red">
              📧 Email: {email}
            </span>
          ))}

          {entities.persons.length > 0 && entities.persons.map((person, i) => (
            <span key={i} className="entity-pill pill-amber">
              👤 Name: {person}
            </span>
          ))}

          {entities.locations.length > 0 && entities.locations.map((loc, i) => (
            <span key={i} className="entity-pill pill-amber">
              📍 Location: {loc}
            </span>
          ))}

        </div>
      </div>

      {/* COUNTDOWN TIMER */}
      <div className="countdown-section">
        <div className="countdown-number">{countdown}</div>
        <div className="countdown-text">
          {countdown > 0
            ? 'seconds before you can post anyway'
            : 'You can now post or edit your message'}
        </div>
      </div>

      {/* ACTION BUTTONS */}
      <div className="warning-actions">

        {/* CANCEL BUTTON → always enabled */}
        <button className="btn-cancel" onClick={onCancel}>
          ✏️ Cancel and Edit
        </button>

        {/* POST ANYWAY BUTTON → disabled until countdown = 0 */}
        {/* countdown > 0 = disabled, countdown = 0 = enabled */}
        <button
          className="btn-post-anyway"
          onClick={onConfirm}
          disabled={countdown > 0}
          style={{ opacity: countdown > 0 ? 0.5 : 1 }}
        >
          {countdown > 0 ? `Post Anyway (${countdown}s)` : 'Post Anyway'}
        </button>

      </div>
    </div>
  );
}

export default WarningModal;
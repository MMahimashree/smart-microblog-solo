import React, { useState, useEffect } from 'react';

function WarningModal({ warning, onConfirm, onCancel }) {
  const [countdown, setCountdown] = useState(10);

  useEffect(() => {
    setCountdown(10);
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) { clearInterval(timer); return 0; }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [warning]);

  const entities = warning.detected_entities;

  return (
    <div className="warning-bar">

      {/* HEADER */}
      <div className="warning-top">
        <span className="warning-icon">⚠️</span>
        <span className="warning-title">Privacy risk detected</span>
        <span className="risk-badge-high">HIGH · {warning.risk_score}/100</span>
      </div>

      {/* DETECTED ENTITIES */}
      <div className="warning-pills">
        {entities.phones.map((p, i) => (
          <span key={i} className="warning-pill">📱 {p}</span>
        ))}
        {entities.emails.map((e, i) => (
          <span key={i} className="warning-pill">📧 {e}</span>
        ))}
        {entities.persons.map((p, i) => (
          <span key={i} className="warning-pill">👤 {p}</span>
        ))}
        {entities.locations.map((l, i) => (
          <span key={i} className="warning-pill">📍 {l}</span>
        ))}
      </div>

      {/* COUNTDOWN */}
      <div className="countdown-row">
        <div className="countdown-num">{String(countdown).padStart(2, '0')}</div>
        <div className="countdown-label">
          {countdown > 0
            ? 'seconds before you can post anyway'
            : 'You can now post or go back and edit'}
        </div>
      </div>

      {/* BUTTONS */}
      <div className="warning-btns">
        <button className="btn-cancel" onClick={onCancel}>
          ✏️ Cancel and edit
        </button>
        <button
          className="btn-post-anyway"
          onClick={onConfirm}
          disabled={countdown > 0}
          style={{ opacity: countdown > 0 ? 0.5 : 1 }}
        >
          {countdown > 0 ? `Post anyway (${countdown}s)` : 'Post anyway'}
        </button>
      </div>

    </div>
  );
}

export default WarningModal;
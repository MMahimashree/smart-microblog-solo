import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiAlertTriangle, FiAlertCircle } from 'react-icons/fi';
import './WarningModal.css';

const COUNTDOWN_SECONDS = 10;

const RISK_META = {
  MEDIUM: {
    color: 'var(--risk-medium)',
    softBg: 'var(--risk-medium-soft)',
    icon: FiAlertCircle,
    title: 'This post looks a little risky',
    subtitle: 'Objective 3: real-time privacy warning — review before you publish.',
  },
  HIGH: {
    color: 'var(--risk-high)',
    softBg: 'var(--risk-high-soft)',
    icon: FiAlertTriangle,
    title: 'High-risk PII detected',
    subtitle: `Objective 3: a ${COUNTDOWN_SECONDS}-second mandatory review delay applies before this post can go live.`,
  },
};

export default function WarningModal({ level, scan, onCancel, onConfirm }) {
  const meta = RISK_META[level] || RISK_META.MEDIUM;
  const Icon = meta.icon;
  const isHigh = level === 'HIGH';
  const [secondsLeft, setSecondsLeft] = useState(isHigh ? COUNTDOWN_SECONDS : 0);

  useEffect(() => {
    if (!isHigh || secondsLeft <= 0) return;
    const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [isHigh, secondsLeft]);

  const entities = Object.entries(scan?.entities || {}).filter(([, v]) =>
    Array.isArray(v) ? v.length > 0 : Boolean(v)
  );
  const locked = isHigh && secondsLeft > 0;
  const progressPct = isHigh ? ((COUNTDOWN_SECONDS - secondsLeft) / COUNTDOWN_SECONDS) * 100 : 100;

  return (
    <AnimatePresence>
      <motion.div
        className="modal__overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onCancel}
      >
        <motion.div
          className="modal__panel"
          initial={{ opacity: 0, scale: 0.94, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96 }}
          transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="modal__header">
            <div className="modal__icon" style={{ background: meta.softBg, color: meta.color }}>
              <Icon size={22} />
            </div>
            <div>
              <div className="modal__title">{meta.title}</div>
              <div className="modal__subtitle">{meta.subtitle}</div>
            </div>
          </div>

          <div className="modal__score-row">
            <span className="modal__section-label" style={{ marginBottom: 0 }}>
              Risk score
            </span>
            <span className="modal__score-value" style={{ color: meta.color }}>
              {scan?.riskScore} · {level}
            </span>
          </div>

          {entities.length > 0 && (
            <>
              <div className="modal__section-label">Detected in this post</div>
              <div className="modal__entities">
                {entities.map(([type, value]) => (
                  <div key={type} className="modal__entity-row">
                    <span>{formatLabel(type)}</span>
                    <span className="modal__entity-value">
                      {Array.isArray(value) ? value.join(', ') : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}

          {scan?.recommendation && <div className="modal__recommendation">{scan.recommendation}</div>}

          <div className="modal__actions">
            <button className="modal__btn modal__btn--cancel" onClick={onCancel}>
              Cancel &amp; edit
            </button>
            <button
              className="modal__btn modal__btn--confirm"
              style={{ background: meta.color }}
              disabled={locked}
              onClick={onConfirm}
            >
              <span
                className="modal__btn-progress"
                style={{ width: `${progressPct}%`, transition: 'width 1s linear' }}
              />
              <span style={{ position: 'relative' }}>
                {locked ? `Post anyway (${secondsLeft}s)` : 'Post anyway'}
              </span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

function formatLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
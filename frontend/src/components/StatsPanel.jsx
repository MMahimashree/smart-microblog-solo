import { motion } from 'framer-motion';
import './StatsPanel.css';

const RADIUS = 42;
const STROKE = 10;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const SEGMENTS = [
  { key: 'low', label: 'Safe', color: 'var(--risk-low)' },
  { key: 'medium', label: 'Medium', color: 'var(--risk-medium)' },
  { key: 'high', label: 'High', color: 'var(--risk-high)' },
];

export default function StatsPanel({ stats }) {
  const { total, low, medium, high } = stats;
  const safeTotal = total || 1;

  let cursor = 0;
  const arcs = SEGMENTS.map((seg) => {
    const value = stats[seg.key] || 0;
    const fraction = value / safeTotal;
    const length = fraction * CIRCUMFERENCE;
    const arc = { ...seg, value, length, offset: -cursor };
    cursor += length;
    return arc;
  });

  return (
    <div className="glass-card stats">
      <div className="stats__title">Privacy stats</div>

      <div className="stats__ring-row">
        <div className="stats__ring">
          <svg viewBox="0 0 100 100">
            <circle className="stats__ring-track" cx="50" cy="50" r={RADIUS} strokeWidth={STROKE} />
            {total > 0 &&
              arcs.map((arc) =>
                arc.length > 0 ? (
                  <motion.circle
                    key={arc.key}
                    cx="50"
                    cy="50"
                    r={RADIUS}
                    stroke={arc.color}
                    strokeWidth={STROKE}
                    strokeLinecap="round"
                    fill="none"
                    strokeDasharray={CIRCUMFERENCE}
                    initial={{ strokeDashoffset: CIRCUMFERENCE }}
                    animate={{ strokeDashoffset: CIRCUMFERENCE - arc.length }}
                    transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                    transform={`rotate(${(arc.offset / CIRCUMFERENCE) * 360 - 90} 50 50)`}
                    style={{ transformOrigin: '50px 50px' }}
                  />
                ) : null
              )}
          </svg>
          <div className="stats__ring-center">
            <motion.span
              key={total}
              className="stats__ring-total"
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              {total}
            </motion.span>
            <span className="stats__ring-label">posts</span>
          </div>
        </div>

        <div className="stats__legend">
          {SEGMENTS.map((seg) => (
            <div className="stats__legend-item" key={seg.key}>
              <span className="stats__legend-dot" style={{ background: seg.color }} />
              <span className="stats__legend-text">{seg.label}</span>
              <span className="stats__legend-value">{stats[seg.key] || 0}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="stats__bars">
        <BarRow label="Safe posts" value={low} total={total} color="var(--risk-low)" />
        <BarRow label="Medium risk" value={medium} total={total} color="var(--risk-medium)" />
        <BarRow label="High risk" value={high} total={total} color="var(--risk-high)" />
      </div>
    </div>
  );
}

function BarRow({ label, value, total, color }) {
  const pct = total ? Math.round((value / total) * 100) : 0;
  return (
    <div className="stats__bar-row">
      <div className="stats__bar-head">
        <span>{label}</span>
        <span className="stats__bar-pct">{pct}%</span>
      </div>
      <div className="stats__bar-track">
        <motion.div
          className="stats__bar-fill"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
    </div>
  );
}
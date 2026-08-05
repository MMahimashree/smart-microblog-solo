const LABELS = {
  LOW: { text: 'Low', dot: 'var(--risk-low)', bg: 'var(--risk-low-soft)', fg: '#0d8a45' },
  MEDIUM: { text: 'Medium', dot: 'var(--risk-medium)', bg: 'var(--risk-medium-soft)', fg: '#b5760a' },
  HIGH: { text: 'High', dot: 'var(--risk-high)', bg: 'var(--risk-high-soft)', fg: '#c81f2a' },
};

export default function RiskBadge({ level = 'LOW', score }) {
  const meta = LABELS[level] || LABELS.LOW;
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        padding: '4px 10px 4px 8px',
        borderRadius: 999,
        background: meta.bg,
        fontSize: 'var(--fs-xs)',
        fontWeight: 700,
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-mono)',
        letterSpacing: '0.01em',
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: 999,
          background: meta.dot,
          boxShadow: `0 0 0 3px ${meta.bg}`,
        }}
      />
      {meta.text}
      {typeof score === 'number' && <span style={{ opacity: 0.55, fontWeight: 500 }}>· {score}</span>}
    </span>
  );
}
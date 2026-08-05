import { useOutletContext } from 'react-router-dom';

// Placeholder — full redesign coming in a later step.
export default function Notifications() {
  useOutletContext();
  return (
    <main className="main-col">
      <div className="page-header">
        <h1>Notifications</h1>
        <p>Redesign coming in the next step</p>
      </div>
      <div className="page-body" style={{ padding: 40, color: 'var(--text-tertiary)', fontSize: '0.875rem' }}>
        This page is next in the queue — say "next" and I'll fill it in.
      </div>
    </main>
  );
}

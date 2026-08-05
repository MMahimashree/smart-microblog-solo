import { FiSearch } from 'react-icons/fi';

export default function SearchBar({ value, onChange }) {
  return (
    <div
      className="card"
      style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 16px' }}
    >
      <FiSearch size={16} color="var(--text-tertiary)" />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search posts"
        style={{
          border: 'none',
          background: 'transparent',
          outline: 'none',
          width: '100%',
          fontSize: '0.875rem',
          color: 'var(--text-primary)',
        }}
      />
    </div>
  );
}
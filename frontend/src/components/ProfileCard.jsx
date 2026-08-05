import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiCalendar } from 'react-icons/fi';
import { getProfile, getCurrentUsername } from '../api/client';

export default function ProfileCard({ postsCount = 0 }) {
  const username = getCurrentUsername();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getProfile(username)
      .then((p) => {
        if (!cancelled) setProfile(p);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [username]);

  const avatarSrc =
    profile?.profileImage ||
    `https://api.dicebear.com/7.x/thumbs/svg?seed=${encodeURIComponent(username)}`;

  return (
    <Link to="/profile" className="card" style={{ padding: 'var(--sp-4)', display: 'block' }}>
      <img
        src={avatarSrc}
        alt=""
        style={{
          width: 52,
          height: 52,
          borderRadius: 999,
          marginBottom: 10,
          objectFit: 'cover',
          background: 'var(--brand-soft)',
        }}
      />
      <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.05rem' }}>
        {username}
      </div>
      <div style={{ color: 'var(--text-tertiary)', fontSize: '0.8125rem', marginBottom: 8 }}>
        @{username}
      </div>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 10 }}>
        {profile?.bio || 'No bio yet — tap to add one.'}
      </p>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          fontSize: '0.8125rem',
          color: 'var(--text-tertiary)',
          marginBottom: 10,
        }}
      >
        <FiCalendar size={14} /> {profile?.joinedDate ? 'Member' : 'New here'}
      </div>
      <div style={{ display: 'flex', gap: 16, fontSize: '0.8125rem' }}>
        <span>
          <strong>{postsCount}</strong> <span style={{ color: 'var(--text-tertiary)' }}>Posts</span>
        </span>
      </div>
    </Link>
  );
}
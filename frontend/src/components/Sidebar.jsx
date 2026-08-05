import { NavLink } from 'react-router-dom';
import {
  FiHome,
  FiCompass,
  FiBell,
  FiMail,
  FiBookmark,
  FiUser,
  FiSettings,
  FiSun,
  FiMoon,
  FiShield,
} from 'react-icons/fi';
import { useTheme } from '../context/ThemeContext';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/', label: 'Home', icon: FiHome, end: true },
  { to: '/explore', label: 'Explore', icon: FiCompass },
  { to: '/notifications', label: 'Notifications', icon: FiBell },
  { to: '/messages', label: 'Messages', icon: FiMail },
  { to: '/bookmarks', label: 'Bookmarks', icon: FiBookmark },
  { to: '/profile', label: 'Profile', icon: FiUser },
  { to: '/settings', label: 'Settings', icon: FiSettings },
];

export default function Sidebar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__brand-mark">
          <FiShield size={18} />
        </span>
        <span className="sidebar__brand-text">Privacy Guard</span>
      </div>

      <nav className="sidebar__nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `sidebar__item ${isActive ? 'sidebar__item--active' : ''}`
            }
          >
            <span className="sidebar__icon">
              <Icon size={22} />
            </span>
            <span className="sidebar__label">{label}</span>
          </NavLink>
        ))}
      </nav>

      <button className="sidebar__theme-toggle" onClick={toggleTheme}>
        {theme === 'light' ? <FiMoon size={18} /> : <FiSun size={18} />}
        <span className="sidebar__label">{theme === 'light' ? 'Dark mode' : 'Light mode'}</span>
      </button>
    </aside>
  );
}
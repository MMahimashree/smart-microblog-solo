import React from 'react';

function Sidebar() {
  return (
    <div className="sidebar">

      {/* LOGO */}
      <div style={{
        width: '44px',
        height: '44px',
        borderRadius: '12px',
        background: '#534AB7',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '4px'
      }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L4 6V12C4 16.4 7.4 20.5 12 22C16.6 20.5 20 16.4 20 12V6L12 2Z" fill="white"/>
          <path d="M10 12L8 10L7 11L10 14L17 7L16 6L10 12Z" fill="#534AB7"/>
        </svg>
      </div>

      {/* NAV ITEMS */}
      <div className="nav-item active" title="Home">🏠</div>
      <div className="nav-item" title="Search">🔍</div>
      <div className="nav-item" title="Notifications">🔔</div>
      <div className="nav-item" title="Messages">✉️</div>
      <div className="nav-item" title="Profile">👤</div>

      {/* POST BUTTON */}
      <div className="sidebar-post-btn">✏️</div>

    </div>
  );
}

export default Sidebar;
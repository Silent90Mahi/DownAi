import PropTypes from 'prop-types';
import { useNavigate, useLocation } from 'react-router-dom';

const IconNav = ({ items, activeId }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const currentActiveId = activeId || items.find(item => location.pathname.startsWith(item.path))?.id;

  const handleItemClick = (item) => {
    if (item.onClick) item.onClick(item);
    else if (item.path) navigate(item.path);
  };

  return (
    <nav
      role="navigation"
      aria-label="Main navigation"
      style={{
        position: 'fixed',
        bottom: 0, left: 0, right: 0,
        zIndex: 50,
        background: 'rgba(10, 7, 18, 0.88)',
        borderTop: '1px solid rgba(139, 92, 246, 0.22)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        boxShadow: '0 -4px 30px rgba(0,0,0,0.5), 0 -1px 0 rgba(139,92,246,0.1)',
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        padding: '0.5rem 0.5rem max(0.5rem, env(safe-area-inset-bottom))',
        maxWidth: 600,
        margin: '0 auto',
      }}>
        {items.map((item) => {
          const isActive = item.id === currentActiveId;
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              type="button"
              onClick={() => handleItemClick(item)}
              aria-label={item.label || item.id}
              aria-current={isActive ? 'page' : undefined}
              style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minWidth: 64,
                minHeight: 52,
                padding: '0.5rem 1rem',
                borderRadius: '0.75rem',
                border: 'none',
                cursor: 'pointer',
                background: isActive
                  ? 'rgba(139,92,246,0.18)'
                  : 'transparent',
                color: isActive ? '#c4b5fd' : 'rgba(148,163,184,0.7)',
                boxShadow: isActive ? '0 0 14px rgba(139,92,246,0.2)' : 'none',
                transition: 'all 0.25s cubic-bezier(0.4,0,0.2,1)',
                outline: 'none',
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(139,92,246,0.09)';
                  e.currentTarget.style.color = '#a78bfa';
                }
              }}
              onMouseLeave={e => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'rgba(148,163,184,0.7)';
                }
              }}
            >
              {/* Active indicator bar */}
              {isActive && (
                <span style={{
                  position: 'absolute',
                  top: 0, left: '50%',
                  transform: 'translateX(-50%)',
                  width: '2rem', height: '2px',
                  background: 'linear-gradient(90deg, #7c3aed, #a855f7)',
                  borderRadius: '0 0 4px 4px',
                  boxShadow: '0 0 8px rgba(139,92,246,0.6)',
                }} />
              )}

              <div style={{
                transform: isActive ? 'scale(1.15)' : 'scale(1)',
                transition: 'transform 0.25s',
              }}>
                {Icon && <Icon size={24} strokeWidth={isActive ? 2.5 : 1.8} />}
              </div>

              {item.label && (
                <span style={{
                  marginTop: 3,
                  fontSize: '0.65rem',
                  fontWeight: isActive ? 700 : 500,
                  lineHeight: 1,
                  letterSpacing: isActive ? '0.02em' : 0,
                  display: 'block',
                }}>
                  {item.label}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};

IconNav.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      icon: PropTypes.elementType.isRequired,
      path: PropTypes.string,
      label: PropTypes.string,
      onClick: PropTypes.func,
    })
  ).isRequired,
  activeId: PropTypes.string,
};

export default IconNav;

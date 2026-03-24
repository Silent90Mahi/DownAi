import { useState, useEffect } from 'react';
import { useRealTime } from './RealTimeProvider';
import { Bell } from 'lucide-react';

const NotificationBadge = ({ onClick }) => {
  const { connected, unreadNotifications } = useRealTime();
  const [showPulse, setShowPulse] = useState(false);
  const [prevCount, setPrevCount] = useState(0);

  useEffect(() => {
    if (unreadNotifications > prevCount) {
      setShowPulse(true);
      const t = setTimeout(() => setShowPulse(false), 1000);
      return () => clearTimeout(t);
    }
    setPrevCount(unreadNotifications);
  }, [unreadNotifications, prevCount]);

  const count = unreadNotifications > 99 ? '99+' : unreadNotifications;

  return (
    <button
      onClick={onClick}
      style={{ position: 'relative', padding: 8, background: 'transparent', border: 'none', cursor: 'pointer', borderRadius: '50%', transition: 'background 0.2s' }}
      onMouseEnter={e => e.currentTarget.style.background = 'rgba(139,92,246,0.1)'}
      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
      aria-label={`Notifications (${unreadNotifications} unread)`}
    >
      <Bell size={22} style={{ color: 'var(--text-secondary)' }} />
      {unreadNotifications > 0 && (
        <span style={{ position: 'absolute', top: 2, right: 2, minWidth: 18, height: 18, paddingInline: 4, background: '#8b5cf6', borderRadius: 99, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 8px rgba(139,92,246,0.5)', transform: showPulse ? 'scale(1.25)' : 'scale(1)', transition: 'transform 0.2s' }}>
          <span style={{ color: '#fff', fontSize: '0.65rem', fontWeight: 800 }}>{count}</span>
        </span>
      )}
      {showPulse && <span style={{ position: 'absolute', top: 2, right: 2, width: 18, height: 18, background: '#8b5cf6', borderRadius: '50%', animation: 'ping 0.7s ease-out', opacity: 0.5 }} />}
      {connected && <span style={{ position: 'absolute', bottom: 4, right: 4, width: 7, height: 7, background: '#10b981', borderRadius: '50%', boxShadow: '0 0 6px #10b981', border: '1px solid rgba(13,10,26,0.8)' }} title="Connected" />}
    </button>
  );
};

export default NotificationBadge;

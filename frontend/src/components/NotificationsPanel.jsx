import { useState, useEffect, useCallback } from 'react';
import { notificationsAPI } from '../services/api';
import { Bell, X, Trash2 } from 'lucide-react';

const NotificationsPanel = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);

  const fetchNotifications = useCallback(async () => {
    try {
      const [notifsResponse, countResponse] = await Promise.all([
        notificationsAPI.getAll(false, 10),
        notificationsAPI.getUnreadCount(),
      ]);
      setNotifications(notifsResponse.data);
      setUnreadCount(countResponse.data.count);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, []);

  useEffect(() => {
    if (isOpen) fetchNotifications();
  }, [isOpen, fetchNotifications]);

  const markAsRead = async (notificationId) => {
    try {
      await notificationsAPI.markAsRead(notificationId);
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await notificationsAPI.markAllAsRead();
      setUnreadCount(0);
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const deleteOld = async () => {
    if (!confirm('Delete notifications older than 90 days?')) return;
    try {
      await notificationsAPI.deleteOld(90);
      fetchNotifications();
    } catch (error) {
      console.error('Failed to delete old notifications:', error);
    }
  };

  return (
    <>
      {/* Bell Icon */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'relative',
          padding: '6px',
          background: 'rgba(255,255,255,0.06)',
          border: '1px solid rgba(139,92,246,0.2)',
          borderRadius: 8,
          cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all 0.2s',
          color: isOpen ? '#c4b5fd' : 'rgba(148,163,184,0.8)',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = 'rgba(139,92,246,0.12)';
          e.currentTarget.style.borderColor = 'rgba(139,92,246,0.4)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'rgba(255,255,255,0.06)';
          e.currentTarget.style.borderColor = 'rgba(139,92,246,0.2)';
        }}
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute', top: -4, right: -4,
            minWidth: 18, height: 18,
            background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
            borderRadius: 99,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.65rem', fontWeight: 800, color: '#fff',
            boxShadow: '0 0 8px rgba(139,92,246,0.5)',
            padding: '0 4px',
          }}>
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <>
          <div
            style={{ position: 'fixed', inset: 0, zIndex: 39 }}
            onClick={() => setIsOpen(false)}
          />
          <div style={{
            position: 'fixed', top: 60, right: 16,
            width: 380,
            background: 'rgba(13, 10, 26, 0.95)',
            border: '1px solid rgba(139,92,246,0.3)',
            borderRadius: '1.25rem',
            backdropFilter: 'blur(24px)',
            WebkitBackdropFilter: 'blur(24px)',
            boxShadow: '0 25px 50px rgba(0,0,0,0.7), 0 0 30px rgba(139,92,246,0.1)',
            zIndex: 50,
            overflow: 'hidden',
            animation: 'scaleIn 0.2s ease-out',
          }}>
            {/* Header */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '1rem 1.25rem',
              borderBottom: '1px solid rgba(139,92,246,0.15)',
              background: 'rgba(139,92,246,0.06)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Bell size={16} style={{ color: '#a78bfa' }} />
                <h3 style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)', margin: 0 }}>
                  Notifications
                </h3>
                {unreadCount > 0 && (
                  <span style={{
                    background: 'rgba(139,92,246,0.2)',
                    border: '1px solid rgba(139,92,246,0.3)',
                    color: '#c4b5fd',
                    fontSize: '0.7rem', fontWeight: 700,
                    padding: '1px 7px', borderRadius: 99,
                  }}>
                    {unreadCount} new
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    style={{
                      fontSize: '0.75rem', fontWeight: 600, color: '#a78bfa',
                      background: 'none', border: 'none', cursor: 'pointer',
                    }}
                  >
                    Mark all read
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  style={{
                    padding: 4, borderRadius: 6, border: 'none',
                    background: 'rgba(255,255,255,0.06)', cursor: 'pointer',
                    color: 'var(--text-muted)', display: 'flex',
                  }}
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* List */}
            <div style={{ maxHeight: 380, overflowY: 'auto', padding: '0.75rem' }}>
              {notifications.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2.5rem 0' }}>
                  <Bell size={40} style={{ color: 'rgba(139,92,246,0.2)', margin: '0 auto 12px' }} />
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
                    No notifications yet
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {notifications.map((notif) => (
                    <div
                      key={notif.id}
                      onClick={() => !notif.is_read && markAsRead(notif.id)}
                      style={{
                        padding: '0.75rem',
                        borderRadius: 10,
                        background: notif.is_read
                          ? 'rgba(255,255,255,0.02)'
                          : 'rgba(139,92,246,0.08)',
                        border: notif.is_read
                          ? '1px solid rgba(255,255,255,0.04)'
                          : '1px solid rgba(139,92,246,0.2)',
                        cursor: notif.is_read ? 'default' : 'pointer',
                        transition: 'all 0.2s',
                        display: 'flex', gap: 10, alignItems: 'flex-start',
                      }}
                    >
                      <div style={{
                        width: 8, height: 8, borderRadius: '50%', marginTop: 6, flexShrink: 0,
                        background: notif.is_read ? 'rgba(255,255,255,0.1)' : '#8b5cf6',
                        boxShadow: notif.is_read ? 'none' : '0 0 6px rgba(139,92,246,0.5)',
                      }} />
                      <div style={{ flex: 1 }}>
                        <p style={{
                          fontWeight: 600, fontSize: '0.85rem',
                          color: notif.is_read ? 'var(--text-tertiary)' : 'var(--text-primary)',
                          margin: '0 0 3px',
                        }}>
                          {notif.title}
                        </p>
                        <p style={{
                          fontSize: '0.78rem',
                          color: notif.is_read ? 'var(--text-muted)' : 'var(--text-secondary)',
                          margin: '0 0 4px',
                        }}>
                          {notif.message}
                        </p>
                        <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>
                          {new Date(notif.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div style={{
              padding: '0.75rem 1.25rem',
              borderTop: '1px solid rgba(139,92,246,0.1)',
              background: 'rgba(0,0,0,0.2)',
            }}>
              <button
                onClick={deleteOld}
                style={{
                  fontSize: '0.75rem', fontWeight: 500,
                  color: 'var(--text-muted)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 5,
                  transition: 'color 0.2s',
                }}
                onMouseEnter={e => (e.currentTarget.style.color = '#fca5a5')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
              >
                <Trash2 size={12} />
                Clear old (90+ days)
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default NotificationsPanel;

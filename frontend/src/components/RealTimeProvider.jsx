import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import { useAuth } from '../contexts/AuthContext';

const RealTimeContext = createContext(null);

export const useRealTime = () => {
  const context = useContext(RealTimeContext);
  if (!context) {
    throw new Error('useRealTime must be used within RealTimeProvider');
  }
  return context;
};

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:6002/ws';

export const RealTimeProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const { connected, subscribe, send, connect, disconnect, error } = useWebSocket();
  
  const [orders, setOrders] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [messages, setMessages] = useState([]);
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  useEffect(() => {
    if (isAuthenticated && user) {
      connect(WS_URL);
    } else {
      disconnect();
    }
  }, [isAuthenticated, user, connect, disconnect]);

  useEffect(() => {
    if (!connected) return;

    const unsubscribers = [];

    unsubscribers.push(
      subscribe('orders', (data) => {
        if (data.action === 'update') {
          setOrders((prev) =>
            prev.map((order) =>
              order.id === data.order.id ? { ...order, ...data.order } : order
            )
          );
        } else if (data.action === 'create') {
          setOrders((prev) => [data.order, ...prev]);
        } else if (data.action === 'list') {
          setOrders(data.orders);
        }
      })
    );

    unsubscribers.push(
      subscribe('notifications', (data) => {
        if (data.action === 'create') {
          setNotifications((prev) => [data.notification, ...prev]);
          setUnreadNotifications((prev) => prev + 1);
        } else if (data.action === 'read') {
          setNotifications((prev) =>
            prev.map((n) =>
              n.id === data.notificationId ? { ...n, is_read: true } : n
            )
          );
          setUnreadNotifications((prev) => Math.max(0, prev - 1));
        } else if (data.action === 'read_all') {
          setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
          setUnreadNotifications(0);
        } else if (data.action === 'list') {
          setNotifications(data.notifications);
          setUnreadNotifications(data.notifications.filter((n) => !n.is_read).length);
        }
      })
    );

    unsubscribers.push(
      subscribe('messages', (data) => {
        if (data.action === 'create') {
          setMessages((prev) => [data.message, ...prev]);
        } else if (data.action === 'list') {
          setMessages(data.messages);
        }
      })
    );

    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, [connected, subscribe]);

  const sendOrderUpdate = useCallback(
    (orderId, status, trackingNumber) => {
      return send('orders', {
        action: 'update_status',
        orderId,
        status,
        trackingNumber,
      });
    },
    [send]
  );

  const markNotificationRead = useCallback(
    (notificationId) => {
      return send('notifications', {
        action: 'mark_read',
        notificationId,
      });
    },
    [send]
  );

  const markAllNotificationsRead = useCallback(() => {
    return send('notifications', { action: 'mark_all_read' });
  }, [send]);

  const sendMessage = useCallback(
    (recipientId, content) => {
      return send('messages', {
        action: 'send',
        recipientId,
        content,
      });
    },
    [send]
  );

  const value = {
    connected,
    error,
    orders,
    notifications,
    messages,
    unreadNotifications,
    sendOrderUpdate,
    markNotificationRead,
    markAllNotificationsRead,
    sendMessage,
    subscribe,
    send,
  };

  return (
    <RealTimeContext.Provider value={value}>
      {children}
    </RealTimeContext.Provider>
  );
};

export default RealTimeProvider;

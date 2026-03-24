import { useState, useEffect, useCallback, useRef } from 'react';

const RECONNECT_DELAY = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

const useWebSocket = () => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);
  
  const socketRef = useRef(null);
  const subscriptionsRef = useRef(new Map());
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const urlRef = useRef(null);

  const connect = useCallback((url) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    urlRef.current = url;
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const wsUrl = token ? `${url}?token=${token}` : url;
      const socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        setConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        
        subscriptionsRef.current.forEach((callback, channel) => {
          socket.send(JSON.stringify({ type: 'subscribe', channel }));
        });
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'message' && data.channel) {
            const callback = subscriptionsRef.current.get(data.channel);
            if (callback) {
              callback(data.payload);
            }
            setMessages((prev) => [...prev.slice(-99), data]);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      socket.onerror = (event) => {
        setError('WebSocket connection error');
        console.error('WebSocket error:', event);
      };

      socket.onclose = () => {
        setConnected(false);
        
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            if (urlRef.current) {
              connect(urlRef.current);
            }
          }, RECONNECT_DELAY * (reconnectAttemptsRef.current + 1));
        } else {
          setError('Connection lost. Please refresh the page.');
        }
      };

      socketRef.current = socket;
    } catch (err) {
      setError('Failed to establish WebSocket connection');
      console.error('WebSocket connection error:', err);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    
    setConnected(false);
    setMessages([]);
    subscriptionsRef.current.clear();
    reconnectAttemptsRef.current = 0;
  }, []);

  const subscribe = useCallback((channel, callback) => {
    subscriptionsRef.current.set(channel, callback);
    
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'subscribe', channel }));
    }
    
    return () => {
      subscriptionsRef.current.delete(channel);
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'unsubscribe', channel }));
      }
    };
  }, []);

  const send = useCallback((channel, data) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'message',
        channel,
        payload: data,
      }));
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connected,
    messages,
    subscribe,
    send,
    connect,
    disconnect,
    error,
  };
};

export default useWebSocket;

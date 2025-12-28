import { useState, useEffect, useCallback, useRef } from 'react';

// Use public WebSocket endpoint (no auth required)
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:54112/ws';
const WS_AUTH_URL = 'ws://127.0.0.1:54112/api/system/ws';

export const useWebSocket = (onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;

  const connect = useCallback(() => {
    try {
      // Try to get auth token and use authenticated endpoint if available
      const token = localStorage.getItem('auth_token');
      let wsUrl = WS_BASE_URL;

      // If token exists, try authenticated endpoint first
      if (token) {
        wsUrl = `${WS_AUTH_URL}?token=${token}`;
      }

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected to', wsUrl);
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (onMessage) {
            onMessage(data);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const timeout = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`Reconnecting in ${timeout}ms...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, timeout);
        } else {
          setError('Max reconnection attempts reached');
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError(err.message);
    }
  }, [onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const send = useCallback((data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    // Only connect if onMessage callback is provided
    if (onMessage !== null) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [connect, disconnect, onMessage]);

  return {
    isConnected,
    error,
    send,
    reconnect: connect,
  };
};

export default useWebSocket;

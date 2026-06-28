import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url: string;
  enabled?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket<T>(options: UseWebSocketOptions) {
  const { url, enabled = true, reconnectInterval = 3000, maxReconnectAttempts = 5 } = options;
  const [data, setData] = useState<T | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!enabled || wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const wsUrl = url.startsWith('ws') ? url : `ws${window.location.protocol === 'https:' ? 's' : ''}://${window.location.host}${url}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setConnected(true);
        setError(null);
        reconnectCountRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setData(message);
        } catch (err) {
          console.error('[v0] WebSocket message parse error:', err);
        }
      };

      ws.onerror = (event) => {
        setError('WebSocket connection error');
        setConnected(false);
      };

      ws.onclose = () => {
        setConnected(false);
        if (enabled && reconnectCountRef.current < maxReconnectAttempts) {
          reconnectCountRef.current++;
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, [url, enabled, reconnectInterval, maxReconnectAttempts]);

  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { data, connected, error, send };
}

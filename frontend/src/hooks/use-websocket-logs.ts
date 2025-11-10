import { useEffect, useRef, useState } from 'react';

export interface LogEntry {
  id?: string;
  timestamp: string;
  level: string | null;
  message: string;
  source: string | null;
  is_error?: boolean;
  is_anomaly?: boolean;
}

export function useWebSocketLogs(connectionId: string | null) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!connectionId) return;

    const ws = new WebSocket(`ws://localhost:8000/api/v1/live-logs/ws/${connectionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
      
      // Send ping every 30s to keep alive
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 30000);

      ws.addEventListener('close', () => clearInterval(pingInterval));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type === 'new_log') {
          setLogs((prev) => [message.data, ...prev].slice(0, 1000)); // Keep last 1000
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [connectionId]);

  return { logs, isConnected };
}

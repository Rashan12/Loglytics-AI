'use client';

import { useEffect, useState } from 'react';

export default function WebSocketStatus() {
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [showStatus, setShowStatus] = useState(false);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id || user.nic_number;

    if (!userId) {
      setShowStatus(false);
      return;
    }

    // Only show status if there's an error
    const connectWebSocket = () => {
      try {
        const websocket = new WebSocket(`ws://localhost:8000/ws/${userId}`);
        
        websocket.onopen = () => {
          console.log('WebSocket connected');
          setConnected(true);
          setShowStatus(false);
        };

        websocket.onclose = () => {
          console.log('WebSocket disconnected');
          setConnected(false);
          setShowStatus(true);
        };

        websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnected(false);
          setShowStatus(true);
        };

        setWs(websocket);
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        setConnected(false);
        setShowStatus(true);
      }
    };

    // Try to connect with a delay
    const timeout = setTimeout(connectWebSocket, 2000);

    return () => {
      clearTimeout(timeout);
      if (ws) {
        ws.close();
      }
    };
  }, []);

  // Don't show status if WebSocket is working fine
  if (!showStatus) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 z-50">
      <div className="w-3 h-3 rounded-full bg-red-500" />
      <span className="text-sm text-red-500">
        WebSocket Disconnected
      </span>
    </div>
  );
}

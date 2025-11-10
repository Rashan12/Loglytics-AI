'use client';

import { useEffect, useState } from 'react';
import { Bell } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Alert {
  id: string;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  read: boolean;
  created_at: string;
}

export function AlertBell() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchAlerts = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setAlerts([]);
        setUnreadCount(0);
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/live-logs/alerts?unread_only=true', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (response.status === 401) {
        console.warn('⚠️ Authentication failed for alerts. Token may be expired.');
        setAlerts([]);
        setUnreadCount(0);
        return;
      }

      if (response.ok) {
        const data = await response.json();
        // Backend returns array of alerts
        const alertsData = Array.isArray(data) ? data : [];
        setAlerts(alertsData);
        setUnreadCount(alertsData.length);
      } else if (response.status === 404) {
        // Endpoint not found - silently handle, no console output
        setAlerts([]);
        setUnreadCount(0);
      } else {
        // Only log non-404 errors
        if (response.status !== 401) {
          console.warn('⚠️ Failed to fetch alerts:', response.status);
        }
        setAlerts([]);
        setUnreadCount(0);
      }
    } catch (error) {
      // Silently handle all network errors - no console output
      setAlerts([]);
      setUnreadCount(0);
    }
  };

  const markAsRead = async (alertId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      await fetch(`http://localhost:8000/api/v1/live-logs/alerts/${alertId}/read`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      fetchAlerts();
    } catch (error) {
      console.error('Failed to mark alert as read:', error);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    // Poll for new alerts every 30 seconds
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/20 text-red-400';
      case 'high':
        return 'bg-orange-500/20 text-orange-400';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400';
      default:
        return 'bg-blue-500/20 text-blue-400';
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-red-500">
              {unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-96 bg-[#161B22] border-[#30363D]">
        <div className="p-4 border-b border-[#30363D]">
          <h3 className="font-semibold text-white">Notifications</h3>
          <p className="text-sm text-gray-400">{unreadCount} unread</p>
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {alerts.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No new notifications</p>
            </div>
          ) : (
            alerts.map((alert) => (
              <DropdownMenuItem
                key={alert.id}
                onClick={() => markAsRead(alert.id)}
                className="p-4 cursor-pointer hover:bg-[#1C2128] border-b border-[#30363D]/50"
              >
                <div className="space-y-2 w-full">
                  <div className="flex items-start justify-between">
                    <h4 className="font-semibold text-white text-sm">{alert.title}</h4>
                    <Badge className={`${getSeverityColor(alert.severity)} text-xs`}>
                      {alert.severity}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-400">{alert.description}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(alert.created_at).toLocaleString()}
                  </p>
                </div>
              </DropdownMenuItem>
            ))
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
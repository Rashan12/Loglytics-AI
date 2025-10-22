"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  X, 
  Bell, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Eye,
  EyeOff,
  Filter,
  RotateCcw
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { AlertCard } from "./AlertCard"
import { useLiveLogsStore } from "@/store/live-logs-store"

interface AlertsPanelProps {
  onClose: () => void
}

const severityColors = {
  low: "bg-blue-100 text-blue-800 border-blue-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  critical: "bg-red-100 text-red-800 border-red-200"
}

const severityIcons = {
  low: CheckCircle,
  medium: AlertTriangle,
  high: AlertTriangle,
  critical: AlertTriangle
}

export function AlertsPanel({ onClose }: AlertsPanelProps) {
  const {
    alerts,
    unreadAlerts,
    markAlertAsRead,
    markAllAlertsAsRead
  } = useLiveLogsStore()

  const [filter, setFilter] = React.useState<'all' | 'unread' | 'critical'>('all')
  const [severityFilter, setSeverityFilter] = React.useState<string>('all')

  // Filter alerts
  const filteredAlerts = React.useMemo(() => {
    return alerts.filter(alert => {
      const matchesFilter = filter === 'all' || 
        (filter === 'unread' && !alert.is_read) ||
        (filter === 'critical' && alert.severity === 'critical')
      
      const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter
      
      return matchesFilter && matchesSeverity
    })
  }, [alerts, filter, severityFilter])

  const severityCounts = React.useMemo(() => {
    return alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [alerts])

  const unreadCount = alerts.filter(alert => !alert.is_read).length
  const criticalCount = alerts.filter(alert => alert.severity === 'critical').length

  const handleMarkAllAsRead = () => {
    markAllAlertsAsRead()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <h2 className="text-lg font-semibold">Alerts</h2>
            {unreadAlerts > 0 && (
              <Badge variant="destructive" className="text-xs">
                {unreadAlerts}
              </Badge>
            )}
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2 mb-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleMarkAllAsRead}
            disabled={unreadCount === 0}
            className="text-xs"
          >
            <Eye className="h-3 w-3 mr-1" />
            Mark All Read
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFilter('unread')}
            className="text-xs"
          >
            <EyeOff className="h-3 w-3 mr-1" />
            Unread Only
          </Button>
        </div>

        {/* Filters */}
        <div className="space-y-2">
          <div className="flex gap-1">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
              className="text-xs"
            >
              All ({alerts.length})
            </Button>
            <Button
              variant={filter === 'unread' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('unread')}
              className="text-xs"
            >
              Unread ({unreadCount})
            </Button>
            <Button
              variant={filter === 'critical' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('critical')}
              className="text-xs"
            >
              Critical ({criticalCount})
            </Button>
          </div>

          <div className="flex gap-1">
            {Object.entries(severityCounts).map(([severity, count]) => (
              <Button
                key={severity}
                variant={severityFilter === severity ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSeverityFilter(severityFilter === severity ? 'all' : severity)}
                className="text-xs"
              >
                {severity} ({count})
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {filteredAlerts.length > 0 ? (
            filteredAlerts.map((alert, index) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <AlertCard
                  alert={alert}
                  onMarkAsRead={() => markAlertAsRead(alert.id)}
                />
              </motion.div>
            ))
          ) : (
            <div className="text-center py-12">
              <div className="text-muted-foreground">
                <Bell className="h-8 w-8 mx-auto mb-2" />
                <p>No alerts found</p>
                <p className="text-sm">
                  {filter === 'unread' 
                    ? "All alerts have been read"
                    : "No alerts match your filters"
                  }
                </p>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer Stats */}
      <div className="p-4 border-t bg-muted/50">
        <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
          <div>
            <div className="font-medium">Total Alerts</div>
            <div className="text-lg font-semibold text-foreground">{alerts.length}</div>
          </div>
          <div>
            <div className="font-medium">Unread</div>
            <div className="text-lg font-semibold text-foreground">{unreadCount}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

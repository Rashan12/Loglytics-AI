"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Eye, 
  ExternalLink,
  MessageSquare,
  Server
} from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { Alert } from "@/store/live-logs-store"

interface AlertCardProps {
  alert: Alert
  onMarkAsRead?: () => void
  onViewLogs?: () => void
  onDismiss?: () => void
}

const severityColors = {
  low: "bg-blue-50 border-blue-200",
  medium: "bg-yellow-50 border-yellow-200", 
  high: "bg-orange-50 border-orange-200",
  critical: "bg-red-50 border-red-200"
}

const severityBadgeColors = {
  low: "bg-blue-100 text-blue-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800", 
  critical: "bg-red-100 text-red-800"
}

const severityIcons = {
  low: CheckCircle,
  medium: AlertTriangle,
  high: AlertTriangle,
  critical: AlertTriangle
}

const alertTypeLabels = {
  error_threshold: "Error Threshold",
  keyword: "Keyword Match",
  anomaly: "Anomaly Detected",
  connection: "Connection Issue"
}

export function AlertCard({
  alert,
  onMarkAsRead,
  onViewLogs,
  onDismiss
}: AlertCardProps) {
  const SeverityIcon = severityIcons[alert.severity]
  
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return date.toLocaleDateString()
  }

  const getSeverityIconColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'text-blue-500'
      case 'medium': return 'text-yellow-500'
      case 'high': return 'text-orange-500'
      case 'critical': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="group"
    >
      <Card className={cn(
        "transition-all duration-200 hover:shadow-md",
        severityColors[alert.severity],
        !alert.is_read && "ring-2 ring-primary/20"
      )}>
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <SeverityIcon className={cn(
                  "h-4 w-4 flex-shrink-0",
                  getSeverityIconColor(alert.severity)
                )} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge
                      variant="outline"
                      className={cn("text-xs", severityBadgeColors[alert.severity])}
                    >
                      {alert.severity.toUpperCase()}
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {alertTypeLabels[alert.alert_type]}
                    </Badge>
                    {!alert.is_read && (
                      <div className="w-2 h-2 bg-primary rounded-full" />
                    )}
                  </div>
                  <h3 className="font-medium text-sm line-clamp-2">
                    {alert.message}
                  </h3>
                </div>
              </div>
            </div>

            {/* Connection Info */}
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Server className="h-3 w-3" />
              <span className="truncate">{alert.connection_name}</span>
            </div>

            {/* Timestamp */}
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{formatTimestamp(alert.timestamp)}</span>
            </div>

            {/* Details */}
            {alert.details && (
              <div className="text-xs text-muted-foreground bg-white/50 rounded p-2">
                <pre className="whitespace-pre-wrap break-words">
                  {typeof alert.details === 'string' 
                    ? alert.details 
                    : JSON.stringify(alert.details, null, 2)
                  }
                </pre>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-2 pt-2 border-t">
              <Button
                variant="outline"
                size="sm"
                onClick={onViewLogs}
                className="text-xs h-6"
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                View Logs
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={onMarkAsRead}
                className="text-xs h-6"
              >
                <Eye className="h-3 w-3 mr-1" />
                Mark Read
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={onDismiss}
                className="text-xs h-6"
              >
                Dismiss
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

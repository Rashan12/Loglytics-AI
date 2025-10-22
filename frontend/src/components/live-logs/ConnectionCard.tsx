"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Play, 
  Pause, 
  Settings, 
  Trash2, 
  MoreVertical,
  Clock,
  Activity,
  AlertTriangle,
  CheckCircle
} from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { LiveLogConnection } from "@/store/live-logs-store"

interface ConnectionCardProps {
  connection: LiveLogConnection
  isActive?: boolean
  onClick?: () => void
  onStart?: () => void
  onStop?: () => void
  onSettings?: () => void
  onDelete?: () => void
}

const providerIcons = {
  aws: "🟠",
  azure: "🔵", 
  gcp: "🟢"
}

const statusColors = {
  active: "bg-green-500",
  paused: "bg-yellow-500",
  error: "bg-red-500"
}

const statusIcons = {
  active: CheckCircle,
  paused: Pause,
  error: AlertTriangle
}

export function ConnectionCard({
  connection,
  isActive = false,
  onClick,
  onStart,
  onStop,
  onSettings,
  onDelete
}: ConnectionCardProps) {
  const StatusIcon = statusIcons[connection.status]
  
  const formatLastSync = (lastSync?: string) => {
    if (!lastSync) return "Never"
    
    const date = new Date(lastSync)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return `${Math.floor(diffMins / 1440)}d ago`
  }

  const handleAction = (e: React.MouseEvent, action: () => void) => {
    e.stopPropagation()
    action()
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        className={cn(
          "cursor-pointer transition-all duration-200 hover:shadow-md",
          isActive && "ring-2 ring-primary shadow-md",
          connection.status === "active" && "border-green-200",
          connection.status === "error" && "border-red-200"
        )}
        onClick={onClick}
      >
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <span className="text-lg">
                  {providerIcons[connection.cloud_provider]}
                </span>
                <div className="min-w-0 flex-1">
                  <h3 className="font-medium text-sm truncate">
                    {connection.connection_name}
                  </h3>
                  <p className="text-xs text-muted-foreground uppercase">
                    {connection.cloud_provider}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-1">
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  statusColors[connection.status],
                  connection.status === "active" && "animate-pulse"
                )} />
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreVertical className="h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    {connection.status === "active" ? (
                      <DropdownMenuItem onClick={(e) => handleAction(e, onStop || (() => {}))}>
                        <Pause className="h-4 w-4 mr-2" />
                        Pause
                      </DropdownMenuItem>
                    ) : (
                      <DropdownMenuItem onClick={(e) => handleAction(e, onStart || (() => {}))}>
                        <Play className="h-4 w-4 mr-2" />
                        Start
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem onClick={(e) => handleAction(e, onSettings || (() => {}))}>
                      <Settings className="h-4 w-4 mr-2" />
                      Settings
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={(e) => handleAction(e, onDelete || (() => {}))}
                      className="text-destructive"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            {/* Status */}
            <div className="flex items-center gap-2">
              <StatusIcon className={cn(
                "h-3 w-3",
                connection.status === "active" && "text-green-500",
                connection.status === "paused" && "text-yellow-500",
                connection.status === "error" && "text-red-500"
              )} />
              <Badge
                variant={connection.status === "active" ? "default" : "secondary"}
                className="text-xs"
              >
                {connection.status}
              </Badge>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3 text-muted-foreground" />
                <span className="text-muted-foreground">
                  {formatLastSync(connection.last_sync_at)}
                </span>
              </div>
              <div className="flex items-center gap-1">
                <Activity className="h-3 w-3 text-muted-foreground" />
                <span className="text-muted-foreground">
                  {connection.logs_per_second || 0}/s
                </span>
              </div>
            </div>

            {/* Quick Stats */}
            {(connection.logs_today || connection.errors_today) && (
              <div className="flex gap-2 text-xs">
                {connection.logs_today && (
                  <Badge variant="outline" className="text-xs">
                    {connection.logs_today.toLocaleString()} logs today
                  </Badge>
                )}
                {connection.errors_today && (
                  <Badge variant="destructive" className="text-xs">
                    {connection.errors_today} errors
                  </Badge>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

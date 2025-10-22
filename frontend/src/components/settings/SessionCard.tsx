"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Monitor, 
  Smartphone, 
  MapPin, 
  Clock, 
  Trash2,
  CheckCircle
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { ActiveSession } from "@/store/settings-store"

interface SessionCardProps {
  session: ActiveSession
  onRevoke: () => void
  isLoading?: boolean
}

export function SessionCard({ session, onRevoke, isLoading = false }: SessionCardProps) {
  const getDeviceIcon = (device: string) => {
    if (device.toLowerCase().includes('mobile') || device.toLowerCase().includes('phone')) {
      return <Smartphone className="h-4 w-4" />
    }
    return <Monitor className="h-4 w-4" />
  }

  const formatLastActive = (lastActive: string) => {
    const now = new Date()
    const active = new Date(lastActive)
    const diffInMinutes = Math.floor((now.getTime() - active.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) {
      return 'Just now'
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60)
      return `${hours} hour${hours > 1 ? 's' : ''} ago`
    } else {
      const days = Math.floor(diffInMinutes / 1440)
      return `${days} day${days > 1 ? 's' : ''} ago`
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative"
    >
      <Card className={session.is_current ? "border-primary bg-primary/5" : ""}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center">
                {getDeviceIcon(session.device)}
              </div>
              
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{session.device}</span>
                  {session.is_current && (
                    <Badge variant="default" className="text-xs">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Current
                    </Badge>
                  )}
                </div>
                
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {session.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatLastActive(session.last_active)}
                  </span>
                </div>
                
                <div className="text-xs text-muted-foreground">
                  {session.browser} • {session.ip_address}
                </div>
              </div>
            </div>
            
            {!session.is_current && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRevoke}
                disabled={isLoading}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

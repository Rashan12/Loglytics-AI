"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Activity, 
  Plus, 
  Grid3X3, 
  List, 
  Settings,
  Bell,
  MessageSquare,
  Wifi,
  WifiOff,
  AlertTriangle
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Live Logs Components
import { LiveLogsPage } from "@/components/live-logs/LiveLogsPage"
import { ConnectionsList } from "@/components/live-logs/ConnectionsList"
import { LogStream } from "@/components/live-logs/LogStream"
import { AlertsPanel } from "@/components/live-logs/AlertsPanel"
import { LiveLogChat } from "@/components/live-logs/LiveLogChat"
import { StatsPanel } from "@/components/live-logs/StatsPanel"

// Store
import { useLiveLogsStore } from "@/store/live-logs-store"

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 }
}

export default function LiveLogsPageRoute() {
  const {
    connections,
    activeConnection,
    viewMode,
    isConnected,
    unreadAlerts,
    setViewMode,
    setActiveConnection,
    refreshConnections
  } = useLiveLogsStore()

  const [showChat, setShowChat] = React.useState(false)
  const [showAlerts, setShowAlerts] = React.useState(false)

  const activeConnectionsCount = connections.filter(conn => conn.status === 'active').length
  const totalConnections = connections.length

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="min-h-screen bg-background"
    >
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Page Header */}
        <motion.div
          variants={cardVariants}
          className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0"
        >
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Activity className="h-8 w-8 text-primary" />
              Live Log Monitoring
            </h1>
            <p className="text-muted-foreground">
              Real-time log streaming and monitoring from cloud providers
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Connection Status */}
            <Badge 
              variant={isConnected ? "default" : "destructive"} 
              className="flex items-center gap-1"
            >
              {isConnected ? (
                <Wifi className="h-3 w-3" />
              ) : (
                <WifiOff className="h-3 w-3" />
              )}
              {isConnected ? "Connected" : "Disconnected"}
            </Badge>
            
            {/* Active Connections */}
            <Badge variant="outline" className="flex items-center gap-1">
              <Activity className="h-3 w-3" />
              {activeConnectionsCount} / {totalConnections} Active
            </Badge>
            
            {/* View Toggle */}
            <div className="flex items-center border rounded-lg">
              <Button
                variant={viewMode === "grid" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("grid")}
                className="rounded-r-none"
              >
                <Grid3X3 className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
                className="rounded-l-none"
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Alerts Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAlerts(!showAlerts)}
              className="relative"
            >
              <Bell className="h-4 w-4" />
              {unreadAlerts > 0 && (
                <Badge 
                  variant="destructive" 
                  className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs"
                >
                  {unreadAlerts}
                </Badge>
              )}
            </Button>
            
            {/* Chat Toggle */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowChat(!showChat)}
            >
              <MessageSquare className="h-4 w-4" />
            </Button>
          </div>
        </motion.div>

        {/* Main Content */}
        <motion.div variants={cardVariants} className="flex gap-6">
          {/* Left Sidebar - Connections */}
          <div className="w-80 flex-shrink-0">
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Connections</CardTitle>
                  <Button size="sm" variant="outline">
                    <Plus className="h-4 w-4 mr-1" />
                    New
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <ConnectionsList />
              </CardContent>
            </Card>
          </div>

          {/* Main Area */}
          <div className="flex-1 min-w-0">
            {activeConnection ? (
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          activeConnection.status === 'active' 
                            ? 'bg-green-500 animate-pulse' 
                            : activeConnection.status === 'paused'
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`} />
                        <CardTitle className="text-lg">{activeConnection.connection_name}</CardTitle>
                      </div>
                      <Badge variant="outline">
                        {activeConnection.cloud_provider.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">
                        {activeConnection.logs_per_second || 0} logs/sec
                      </Badge>
                      <Button size="sm" variant="outline">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <LogStream connection={activeConnection} />
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Activity className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Connection Selected</h3>
                  <p className="text-muted-foreground text-center mb-4">
                    Select a connection from the sidebar to start monitoring live logs
                  </p>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create New Connection
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Sidebar - Stats */}
          <div className="w-80 flex-shrink-0">
            <StatsPanel />
          </div>
        </motion.div>

        {/* Chat Panel - Sliding Drawer */}
        {showChat && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            className="fixed inset-y-0 right-0 w-96 bg-background border-l shadow-lg z-50"
          >
            <LiveLogChat onClose={() => setShowChat(false)} />
          </motion.div>
        )}

        {/* Alerts Panel - Sliding Drawer */}
        {showAlerts && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            className="fixed inset-y-0 right-0 w-96 bg-background border-l shadow-lg z-50"
          >
            <AlertsPanel onClose={() => setShowAlerts(false)} />
          </motion.div>
        )}

        {/* Overlay for drawers */}
        {(showChat || showAlerts) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 z-40"
            onClick={() => {
              setShowChat(false)
              setShowAlerts(false)
            }}
          />
        )}
      </div>
    </motion.div>
  )
}

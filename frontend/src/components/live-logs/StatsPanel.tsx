"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Activity, 
  AlertTriangle, 
  TrendingUp, 
  Clock,
  Database,
  Zap,
  BarChart3
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useLiveLogsStore } from "@/store/live-logs-store"

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function StatsPanel() {
  const {
    totalLogsToday,
    logsPerSecond,
    errorRate,
    topErrors,
    connections,
    activeConnection
  } = useLiveLogsStore()

  const activeConnections = connections.filter(conn => conn.status === 'active').length
  const totalConnections = connections.length

  // Mock real-time data updates
  const [realTimeStats, setRealTimeStats] = React.useState({
    logsPerSecond: logsPerSecond,
    errorRate: errorRate,
    activeConnections: activeConnections
  })

  React.useEffect(() => {
    const interval = setInterval(() => {
      setRealTimeStats(prev => ({
        logsPerSecond: Math.max(0, prev.logsPerSecond + (Math.random() - 0.5) * 2),
        errorRate: Math.max(0, Math.min(100, prev.errorRate + (Math.random() - 0.5) * 0.5)),
        activeConnections: activeConnections
      }))
    }, 1000)

    return () => clearInterval(interval)
  }, [activeConnections])

  const getErrorRateColor = (rate: number) => {
    if (rate < 1) return "text-green-600"
    if (rate < 5) return "text-yellow-600"
    return "text-red-600"
  }

  const getErrorRateStatus = (rate: number) => {
    if (rate < 1) return "Excellent"
    if (rate < 5) return "Good"
    if (rate < 10) return "Warning"
    return "Critical"
  }

  return (
    <div className="space-y-4">
      {/* Real-time Stats */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Real-time Stats
          </CardTitle>
          <CardDescription>
            Live monitoring metrics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <motion.div
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-2 gap-4"
          >
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {realTimeStats.logsPerSecond.toFixed(1)}
              </div>
              <div className="text-xs text-muted-foreground">Logs/sec</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${getErrorRateColor(realTimeStats.errorRate)}`}>
                {realTimeStats.errorRate.toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground">Error Rate</div>
            </div>
          </motion.div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>Error Rate</span>
              <span className={getErrorRateColor(realTimeStats.errorRate)}>
                {getErrorRateStatus(realTimeStats.errorRate)}
              </span>
            </div>
            <Progress 
              value={realTimeStats.errorRate} 
              className="h-2"
            />
          </div>
        </CardContent>
      </Card>

      {/* Connection Status */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Database className="h-5 w-5" />
            Connections
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm">Active</span>
            <Badge variant="default">
              {realTimeStats.activeConnections} / {totalConnections}
            </Badge>
          </div>
          
          <div className="space-y-2">
            {connections.slice(0, 3).map((conn) => (
              <div key={conn.id} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    conn.status === 'active' ? 'bg-green-500 animate-pulse' :
                    conn.status === 'paused' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <span className="truncate">{conn.connection_name}</span>
                </div>
                <span className="text-xs text-muted-foreground">
                  {conn.logs_per_second || 0}/s
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Today's Summary */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Today's Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-xl font-bold">
                {totalLogsToday.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">Total Logs</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-red-600">
                {Math.floor(totalLogsToday * (errorRate / 100)).toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">Errors</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>Log Volume</span>
              <span>Peak: {Math.floor(totalLogsToday / 24 * 1.5).toLocaleString()}/hr</span>
            </div>
            <Progress value={75} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Top Errors */}
      {topErrors.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Top Errors
            </CardTitle>
            <CardDescription>
              Most frequent errors (last hour)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {topErrors.slice(0, 5).map((error, index) => (
                <motion.div
                  key={index}
                  variants={cardVariants}
                  initial="hidden"
                  animate="visible"
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between text-sm"
                >
                  <div className="flex-1 min-w-0">
                    <div className="truncate" title={error.message}>
                      {error.message}
                    </div>
                  </div>
                  <Badge variant="destructive" className="text-xs">
                    {error.count}
                  </Badge>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Health */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Zap className="h-5 w-5" />
            System Health
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Overall Health</span>
              <Badge variant={errorRate < 5 ? "default" : "destructive"}>
                {errorRate < 5 ? "Healthy" : "Degraded"}
              </Badge>
            </div>
            <Progress 
              value={Math.max(0, 100 - errorRate * 10)} 
              className="h-2"
            />
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span>Uptime</span>
              <span>99.9%</span>
            </div>
            <div className="flex justify-between">
              <span>Latency</span>
              <span>45ms</span>
            </div>
            <div className="flex justify-between">
              <span>Throughput</span>
              <span>High</span>
            </div>
            <div className="flex justify-between">
              <span>Last Update</span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Now
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

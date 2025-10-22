'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LogEntry } from '@/types'
import { formatDate, getLogLevelColor, getLogLevelBgColor, truncateText } from '@/lib/utils'
import { Activity, Play, Pause, RotateCcw } from 'lucide-react'

export function LiveLogsViewer() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [selectedLogFile, setSelectedLogFile] = useState<number | null>(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  const startStreaming = () => {
    setIsStreaming(true)
    // In a real implementation, this would connect to WebSocket or Server-Sent Events
    // For now, we'll simulate with mock data
    simulateLogStream()
  }

  const stopStreaming = () => {
    setIsStreaming(false)
  }

  const clearLogs = () => {
    setLogs([])
  }

  const simulateLogStream = () => {
    const mockLogs: LogEntry[] = [
      {
        id: 1,
        log_file_id: 1,
        line_number: 1,
        timestamp: new Date().toISOString(),
        level: 'INFO',
        message: 'Application started successfully',
        source: 'app',
        created_at: new Date().toISOString(),
        is_anomaly: false
      },
      {
        id: 2,
        log_file_id: 1,
        line_number: 2,
        timestamp: new Date().toISOString(),
        level: 'WARN',
        message: 'High memory usage detected',
        source: 'monitor',
        created_at: new Date().toISOString(),
        is_anomaly: false
      },
      {
        id: 3,
        log_file_id: 1,
        line_number: 3,
        timestamp: new Date().toISOString(),
        level: 'ERROR',
        message: 'Database connection failed',
        source: 'database',
        created_at: new Date().toISOString(),
        is_anomaly: true
      }
    ]

    // Simulate streaming by adding logs one by one
    mockLogs.forEach((log, index) => {
      setTimeout(() => {
        if (isStreaming) {
          setLogs(prev => [...prev, { ...log, id: Date.now() + index }])
        }
      }, index * 1000)
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Live Logs</h2>
        <p className="text-muted-foreground">
          Real-time log monitoring and streaming
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Live Stream</span>
                {isStreaming && (
                  <Badge variant="destructive" className="animate-pulse">
                    LIVE
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>
                {isStreaming ? 'Streaming logs in real-time' : 'Start streaming to see live logs'}
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              {!isStreaming ? (
                <Button onClick={startStreaming}>
                  <Play className="h-4 w-4 mr-2" />
                  Start Stream
                </Button>
              ) : (
                <Button variant="destructive" onClick={stopStreaming}>
                  <Pause className="h-4 w-4 mr-2" />
                  Stop Stream
                </Button>
              )}
              <Button variant="outline" onClick={clearLogs}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Clear
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{logs.length} log entries</span>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={autoScroll}
                  onChange={(e) => setAutoScroll(e.target.checked)}
                  className="rounded"
                />
                <span>Auto-scroll</span>
              </label>
            </div>
            
            <div className="h-96 overflow-y-auto border rounded-lg bg-muted/20">
              {logs.length === 0 ? (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  <div className="text-center">
                    <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No logs yet. Start streaming to see live logs.</p>
                  </div>
                </div>
              ) : (
                <div className="p-4 space-y-2">
                  {logs.map((log) => (
                    <div
                      key={log.id}
                      className={`p-3 rounded-lg border-l-4 ${
                        log.is_anomaly ? 'border-red-500 bg-red-50 dark:bg-red-900/10' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <Badge
                              variant="outline"
                              className={`${getLogLevelBgColor(log.level || '')} ${getLogLevelColor(log.level || '')}`}
                            >
                              {log.level || 'UNKNOWN'}
                            </Badge>
                            {log.source && (
                              <Badge variant="secondary">{log.source}</Badge>
                            )}
                            {log.is_anomaly && (
                              <Badge variant="destructive">Anomaly</Badge>
                            )}
                          </div>
                          <p className="text-sm font-mono">
                            {truncateText(log.message, 200)}
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                            <span>Line {log.line_number}</span>
                            {log.timestamp && (
                              <span>{formatDate(log.timestamp)}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={logsEndRef} />
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

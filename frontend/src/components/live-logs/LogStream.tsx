"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Play, 
  Pause, 
  Download, 
  Trash2, 
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Settings
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { LogEntry } from "./LogEntry"
import { LogFilters } from "./LogFilters"
import { useLiveLogsStore } from "@/store/live-logs-store"
import { LiveLogConnection } from "@/store/live-logs-store"

interface LogStreamProps {
  connection: LiveLogConnection
}

export function LogStream({ connection }: LogStreamProps) {
  const {
    logs,
    filteredLogs,
    isStreaming,
    isPaused,
    autoScroll,
    setStreaming,
    setPaused,
    setAutoScroll,
    clearLogs,
    applyFilters
  } = useLiveLogsStore()

  const [showFilters, setShowFilters] = React.useState(false)
  const [searchQuery, setSearchQuery] = React.useState("")
  const scrollAreaRef = React.useRef<HTMLDivElement>(null)
  const [isAtBottom, setIsAtBottom] = React.useState(true)

  // Filter logs for this connection
  const connectionLogs = React.useMemo(() => {
    return filteredLogs.filter(log => log.connection_id === connection.id)
  }, [filteredLogs, connection.id])

  // Apply search filter
  const searchFilteredLogs = React.useMemo(() => {
    if (!searchQuery) return connectionLogs
    
    const query = searchQuery.toLowerCase()
    return connectionLogs.filter(log =>
      log.message.toLowerCase().includes(query) ||
      log.source?.toLowerCase().includes(query) ||
      log.service?.toLowerCase().includes(query) ||
      log.level.toLowerCase().includes(query)
    )
  }, [connectionLogs, searchQuery])

  // Auto-scroll to bottom when new logs arrive
  React.useEffect(() => {
    if (autoScroll && isAtBottom && scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }, [connectionLogs, autoScroll, isAtBottom])

  // Handle scroll events
  const handleScroll = (event: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = event.currentTarget
    const atBottom = scrollHeight - scrollTop - clientHeight < 10
    setIsAtBottom(atBottom)
  }

  const handleStartStreaming = () => {
    setStreaming(true)
    setPaused(false)
  }

  const handleStopStreaming = () => {
    setStreaming(false)
  }

  const handleTogglePause = () => {
    setPaused(!isPaused)
  }

  const handleClearLogs = () => {
    clearLogs()
  }

  const handleExportLogs = () => {
    const logsToExport = searchFilteredLogs.map(log => ({
      timestamp: log.timestamp,
      level: log.level,
      message: log.message,
      source: log.source,
      service: log.service
    }))
    
    const blob = new Blob([JSON.stringify(logsToExport, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs-${connection.connection_name}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const logLevelCounts = React.useMemo(() => {
    return connectionLogs.reduce((acc, log) => {
      acc[log.level] = (acc[log.level] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [connectionLogs])

  return (
    <div className="flex flex-col h-[600px]">
      {/* Header Controls */}
      <div className="p-4 border-b space-y-3">
        {/* Main Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {!isStreaming ? (
              <Button size="sm" onClick={handleStartStreaming}>
                <Play className="h-4 w-4 mr-1" />
                Start Streaming
              </Button>
            ) : (
              <Button size="sm" variant="outline" onClick={handleStopStreaming}>
                <Pause className="h-4 w-4 mr-1" />
                Stop Streaming
              </Button>
            )}
            
            {isStreaming && (
              <Button
                size="sm"
                variant={isPaused ? "default" : "outline"}
                onClick={handleTogglePause}
              >
                {isPaused ? (
                  <>
                    <Play className="h-4 w-4 mr-1" />
                    Resume
                  </>
                ) : (
                  <>
                    <Pause className="h-4 w-4 mr-1" />
                    Pause
                  </>
                )}
              </Button>
            )}
            
            <Button size="sm" variant="outline" onClick={handleClearLogs}>
              <Trash2 className="h-4 w-4 mr-1" />
              Clear
            </Button>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={autoScroll ? "default" : "outline"}
              onClick={() => setAutoScroll(!autoScroll)}
            >
              {autoScroll ? (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" />
                  Auto-scroll
                </>
              ) : (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" />
                  Manual
                </>
              )}
            </Button>
            
            <Button size="sm" variant="outline" onClick={handleExportLogs}>
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          
          <Button
            size="sm"
            variant={showFilters ? "default" : "outline"}
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4 mr-1" />
            Filters
          </Button>
        </div>

        {/* Log Level Counts */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Log levels:</span>
          {Object.entries(logLevelCounts).map(([level, count]) => (
            <Badge key={level} variant="outline" className="text-xs">
              {level}: {count}
            </Badge>
          ))}
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="border-b"
        >
          <LogFilters onApply={applyFilters} />
        </motion.div>
      )}

      {/* Logs Display */}
      <div className="flex-1 relative">
        <ScrollArea 
          ref={scrollAreaRef}
          className="h-full"
          onScrollCapture={handleScroll}
        >
          <div className="p-4 space-y-1">
            {searchFilteredLogs.length > 0 ? (
              searchFilteredLogs.map((log, index) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.01 }}
                >
                  <LogEntry log={log} />
                </motion.div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="text-muted-foreground">
                  {searchQuery ? (
                    <>
                      <Search className="h-8 w-8 mx-auto mb-2" />
                      <p>No logs match your search</p>
                    </>
                  ) : (
                    <>
                      <Play className="h-8 w-8 mx-auto mb-2" />
                      <p>No logs yet</p>
                      <p className="text-sm">Start streaming to see live logs</p>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Scroll to Bottom Button */}
        {!isAtBottom && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute bottom-4 right-4"
          >
            <Button
              size="sm"
              onClick={() => {
                const scrollElement = scrollAreaRef.current?.querySelector('[data-radix-scroll-area-viewport]')
                if (scrollElement) {
                  scrollElement.scrollTop = scrollElement.scrollHeight
                }
              }}
            >
              <ChevronDown className="h-4 w-4 mr-1" />
              Scroll to Bottom
            </Button>
          </motion.div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-3 border-t bg-muted/50">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-4">
            <span>Total: {connectionLogs.length.toLocaleString()}</span>
            <span>Filtered: {searchFilteredLogs.length.toLocaleString()}</span>
            {isStreaming && (
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Live
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {isPaused && (
              <Badge variant="secondary">Paused</Badge>
            )}
            <span>Last updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

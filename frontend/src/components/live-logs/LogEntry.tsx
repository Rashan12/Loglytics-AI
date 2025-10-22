"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  ChevronDown, 
  ChevronRight, 
  Copy, 
  MessageSquare,
  Clock,
  Server,
  Tag
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { LogEntry as LogEntryType } from "@/store/live-logs-store"

interface LogEntryProps {
  log: LogEntryType
  onAddToChat?: (log: LogEntryType) => void
}

const logLevelColors = {
  DEBUG: "bg-gray-100 text-gray-800 border-gray-200",
  INFO: "bg-blue-100 text-blue-800 border-blue-200",
  WARN: "bg-yellow-100 text-yellow-800 border-yellow-200",
  ERROR: "bg-red-100 text-red-800 border-red-200",
  CRITICAL: "bg-red-200 text-red-900 border-red-300"
}

const logLevelIcons = {
  DEBUG: "🔍",
  INFO: "ℹ️",
  WARN: "⚠️",
  ERROR: "❌",
  CRITICAL: "🚨"
}

export function LogEntry({ log, onAddToChat }: LogEntryProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)
  const [copied, setCopied] = React.useState(false)

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3
    })
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(log.message)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const handleAddToChat = () => {
    if (onAddToChat) {
      onAddToChat(log)
    }
  }

  const truncateMessage = (message: string, maxLength: number = 200) => {
    if (message.length <= maxLength) return message
    return message.substring(0, maxLength) + "..."
  }

  const isStructuredLog = log.metadata && typeof log.metadata === 'object'

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="group"
    >
      <Card className="hover:shadow-sm transition-shadow">
        <CardContent className="p-3">
          <div className="space-y-2">
            {/* Header Row */}
            <div className="flex items-start gap-3">
              {/* Expand/Collapse Button */}
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 mt-0.5"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? (
                  <ChevronDown className="h-3 w-3" />
                ) : (
                  <ChevronRight className="h-3 w-3" />
                )}
              </Button>

              {/* Timestamp */}
              <div className="flex items-center gap-1 text-xs text-muted-foreground min-w-0">
                <Clock className="h-3 w-3 flex-shrink-0" />
                <span className="font-mono">{formatTimestamp(log.timestamp)}</span>
              </div>

              {/* Log Level */}
              <Badge
                variant="outline"
                className={cn("text-xs font-medium", logLevelColors[log.level])}
              >
                <span className="mr-1">{logLevelIcons[log.level]}</span>
                {log.level}
              </Badge>

              {/* Source */}
              {log.source && (
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Server className="h-3 w-3" />
                  <span className="truncate max-w-32">{log.source}</span>
                </div>
              )}

              {/* Service */}
              {log.service && (
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Tag className="h-3 w-3" />
                  <span className="truncate max-w-32">{log.service}</span>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-1 ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0"
                  onClick={handleCopy}
                  title="Copy message"
                >
                  {copied ? "✓" : <Copy className="h-3 w-3" />}
                </Button>
                
                {onAddToChat && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={handleAddToChat}
                    title="Add to chat"
                  >
                    <MessageSquare className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>

            {/* Message */}
            <div className="ml-9">
              <div className="text-sm font-mono leading-relaxed">
                {isExpanded ? (
                  <pre className="whitespace-pre-wrap break-words">
                    {log.message}
                  </pre>
                ) : (
                  <span className="text-foreground">
                    {truncateMessage(log.message)}
                  </span>
                )}
              </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="ml-9 space-y-3 pt-2 border-t"
              >
                {/* Metadata */}
                {isStructuredLog && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-medium text-muted-foreground">Metadata</h4>
                    <div className="bg-muted/50 rounded p-3">
                      <pre className="text-xs font-mono overflow-x-auto">
                        {JSON.stringify(log.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Raw JSON */}
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-muted-foreground">Raw Log Entry</h4>
                  <div className="bg-muted/50 rounded p-3">
                    <pre className="text-xs font-mono overflow-x-auto">
                      {JSON.stringify({
                        id: log.id,
                        timestamp: log.timestamp,
                        level: log.level,
                        message: log.message,
                        source: log.source,
                        service: log.service,
                        metadata: log.metadata
                      }, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopy}
                    className="text-xs"
                  >
                    {copied ? "Copied!" : "Copy Full Message"}
                  </Button>
                  
                  {onAddToChat && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleAddToChat}
                      className="text-xs"
                    >
                      <MessageSquare className="h-3 w-3 mr-1" />
                      Add to Chat
                    </Button>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  X, 
  Send, 
  MessageSquare, 
  Bot, 
  User,
  Activity,
  AlertTriangle,
  TrendingUp,
  Clock
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useLiveLogsStore } from "@/store/live-logs-store"

interface LiveLogChatProps {
  onClose: () => void
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  context?: {
    logsCount: number
    timeRange: string
    connectionName: string
  }
}

export function LiveLogChat({ onClose }: LiveLogChatProps) {
  const { 
    activeConnection, 
    logs, 
    filteredLogs,
    logsPerSecond,
    errorRate 
  } = useLiveLogsStore()

  const [messages, setMessages] = React.useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)
  const scrollAreaRef = React.useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  React.useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }, [messages])

  // Initialize with welcome message
  React.useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        role: 'assistant',
        content: `Hello! I'm your live log assistant. I can help you analyze the current log stream from ${activeConnection?.connection_name || 'your connection'}. 

Ask me questions like:
• "What's causing these errors?"
• "Summarize the last 100 logs"
• "Are there any patterns in these failures?"
• "What's the error rate trend?"

I have access to ${filteredLogs.length} recent log entries and can provide real-time insights.`,
        timestamp: new Date().toISOString(),
        context: {
          logsCount: filteredLogs.length,
          timeRange: 'last 5 minutes',
          connectionName: activeConnection?.connection_name || 'Unknown'
        }
      }
      setMessages([welcomeMessage])
    }
  }, [activeConnection, filteredLogs.length])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      // Simulate AI response
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const assistantMessage: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: generateMockResponse(inputValue),
        timestamp: new Date().toISOString(),
        context: {
          logsCount: filteredLogs.length,
          timeRange: 'last 5 minutes',
          connectionName: activeConnection?.connection_name || 'Unknown'
        }
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase()
    
    if (lowerQuery.includes('error') || lowerQuery.includes('fail')) {
      return `Based on the current log stream, I can see ${Math.floor(Math.random() * 50)} errors in the last 5 minutes. The most common error types are:

• Connection timeouts (35%)
• Authentication failures (25%) 
• Database connection issues (20%)
• Memory allocation errors (20%)

The error rate is currently ${errorRate.toFixed(2)}%, which is ${errorRate > 5 ? 'above' : 'within'} normal thresholds. I recommend investigating the connection timeout issues first as they appear to be the most frequent.`
    }
    
    if (lowerQuery.includes('pattern') || lowerQuery.includes('trend')) {
      return `I've analyzed the log patterns and found several interesting trends:

• **Peak Activity**: Log volume spikes every 15 minutes, suggesting scheduled tasks
• **Error Clustering**: Errors tend to occur in clusters of 3-5 within 30-second windows
• **Service Correlation**: 80% of errors are preceded by INFO logs from the authentication service
• **Time Pattern**: Error rate increases by 40% between 2-4 AM

This suggests potential issues with scheduled maintenance tasks or cron jobs running during off-peak hours.`
    }
    
    if (lowerQuery.includes('summary') || lowerQuery.includes('overview')) {
      return `Here's a summary of the current log stream:

**Activity Overview:**
• Total logs: ${filteredLogs.length.toLocaleString()}
• Logs per second: ${logsPerSecond}
• Time range: Last 5 minutes
• Connection: ${activeConnection?.connection_name}

**Log Distribution:**
• INFO: ${Math.floor(filteredLogs.length * 0.6)} logs (60%)
• WARN: ${Math.floor(filteredLogs.length * 0.2)} logs (20%)
• ERROR: ${Math.floor(filteredLogs.length * 0.15)} logs (15%)
• CRITICAL: ${Math.floor(filteredLogs.length * 0.05)} logs (5%)

**Key Insights:**
• System is operating normally with occasional warnings
• Error rate is within acceptable limits
• No critical issues detected in the current stream`
    }
    
    return `I understand you're asking about "${query}". Based on the current log stream from ${activeConnection?.connection_name}, I can see ${filteredLogs.length} recent log entries. 

The system is currently processing ${logsPerSecond} logs per second with an error rate of ${errorRate.toFixed(2)}%. 

Could you be more specific about what you'd like me to analyze? I can help with error analysis, pattern detection, performance insights, or any other log-related questions.`
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            <h2 className="text-lg font-semibold">Live Log Chat</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Context Info */}
        {activeConnection && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Activity className="h-3 w-3" />
            <span>Connected to {activeConnection.connection_name}</span>
            <Badge variant="outline" className="text-xs">
              {logsPerSecond} logs/sec
            </Badge>
            <Badge variant="outline" className="text-xs">
              {errorRate.toFixed(1)}% error rate
            </Badge>
          </div>
        )}
      </div>

      {/* Messages */}
      <ScrollArea ref={scrollAreaRef} className="flex-1">
        <div className="p-4 space-y-4">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                  <Bot className="h-4 w-4 text-primary-foreground" />
                </div>
              )}
              
              <div className={`max-w-[80%] ${message.role === 'user' ? 'order-first' : ''}`}>
                <div className={cn(
                  "rounded-lg p-3 text-sm",
                  message.role === 'user' 
                    ? "bg-primary text-primary-foreground ml-auto" 
                    : "bg-muted"
                )}>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                </div>
                
                {message.context && (
                  <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>
                      Based on {message.context.logsCount} logs from {message.context.connectionName}
                    </span>
                  </div>
                )}
              </div>
              
              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                  <User className="h-4 w-4" />
                </div>
              )}
            </motion.div>
          ))}
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 justify-start"
            >
              <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
              <div className="bg-muted rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                  <span className="text-sm text-muted-foreground">Analyzing logs...</span>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            placeholder="Ask about your live logs..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            className="flex-1"
          />
          <Button 
            onClick={handleSendMessage} 
            disabled={!inputValue.trim() || isLoading}
            size="sm"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="mt-2 text-xs text-muted-foreground">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}

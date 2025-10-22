"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, X, ArrowUp, ArrowDown, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: string
  model?: "local" | "maverick"
  citations?: Citation[]
  isStreaming?: boolean
  files?: FileAttachment[]
}

interface Citation {
  id: string
  content: string
  source: string
  relevance: number
  logChunk: string
}

interface FileAttachment {
  id: string
  name: string
  size: number
  type: string
  url?: string
}

interface MessageSearchProps {
  messages: Message[]
  onMessageSelect: (messageId: string) => void
  isOpen: boolean
  onClose: () => void
}

export function MessageSearch({ messages, onMessageSelect, isOpen, onClose }: MessageSearchProps) {
  const [query, setQuery] = React.useState("")
  const [selectedIndex, setSelectedIndex] = React.useState(0)
  const [searchResults, setSearchResults] = React.useState<Message[]>([])
  const inputRef = React.useRef<HTMLInputElement>(null)

  // Focus input when opened
  React.useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Search messages
  React.useEffect(() => {
    if (!query.trim()) {
      setSearchResults([])
      setSelectedIndex(0)
      return
    }

    const results = messages.filter(message => 
      message.content.toLowerCase().includes(query.toLowerCase()) &&
      message.role !== "system"
    )
    
    setSearchResults(results)
    setSelectedIndex(0)
  }, [query, messages])

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      onClose()
    } else if (e.key === "ArrowDown") {
      e.preventDefault()
      setSelectedIndex(prev => Math.min(prev + 1, searchResults.length - 1))
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      setSelectedIndex(prev => Math.max(prev - 1, 0))
    } else if (e.key === "Enter" && searchResults.length > 0) {
      e.preventDefault()
      const selectedMessage = searchResults[selectedIndex]
      if (selectedMessage) {
        onMessageSelect(selectedMessage.id)
        onClose()
      }
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">
          {part}
        </mark>
      ) : part
    )
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        transition={{ duration: 0.2 }}
        className="absolute top-20 left-1/2 transform -translate-x-1/2 w-full max-w-2xl mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-background border border-border rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center space-x-3 p-4 border-b border-border">
            <Search className="h-5 w-5 text-muted-foreground" />
            <Input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search messages..."
              className="flex-1 border-0 bg-transparent focus-visible:ring-0"
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Results */}
          <div className="max-h-96 overflow-y-auto">
            {query.trim() && searchResults.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No messages found</p>
                <p className="text-sm">Try a different search term</p>
              </div>
            ) : query.trim() && searchResults.length > 0 ? (
              <div className="p-2">
                <div className="flex items-center justify-between mb-3 px-2">
                  <span className="text-sm text-muted-foreground">
                    {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
                  </span>
                  <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                    <ArrowUp className="h-3 w-3" />
                    <ArrowDown className="h-3 w-3" />
                    <span>to navigate</span>
                  </div>
                </div>
                
                <div className="space-y-1">
                  {searchResults.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        "p-3 rounded-lg cursor-pointer transition-colors",
                        index === selectedIndex
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-muted"
                      )}
                      onClick={() => {
                        onMessageSelect(message.id)
                        onClose()
                      }}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={cn(
                          "w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0",
                          message.role === "user" 
                            ? "bg-blue-500 text-white" 
                            : "bg-purple-500 text-white"
                        )}>
                          {message.role === "user" ? "U" : "A"}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <Badge 
                              variant={message.role === "user" ? "default" : "secondary"}
                              size="sm"
                            >
                              {message.role === "user" ? "You" : "AI"}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {formatTimestamp(message.timestamp)}
                            </span>
                          </div>
                          
                          <p className={cn(
                            "text-sm line-clamp-2",
                            index === selectedIndex 
                              ? "text-primary-foreground" 
                              : "text-foreground"
                          )}>
                            {highlightText(message.content, query)}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Search through your conversation</p>
                <p className="text-sm">Type to find specific messages</p>
              </div>
            )}
          </div>

          {/* Footer */}
          {query.trim() && searchResults.length > 0 && (
            <div className="p-3 border-t border-border bg-muted/30">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Press Enter to jump to message</span>
                <span>Esc to close</span>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

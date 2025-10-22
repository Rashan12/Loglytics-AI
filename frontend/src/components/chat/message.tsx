"use client"

import * as React from "react"
import { motion } from "framer-motion"
import {
  User,
  Bot,
  Copy,
  Edit,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { CodeBlock } from "./code-block"
import { CitationCard } from "./citation-card"
import { MessageActions } from "./message-actions"

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

interface MessageProps {
  message: Message
  isLast: boolean
  isStreaming?: boolean
}

export function Message({ message, isLast, isStreaming = false }: MessageProps) {
  const [showCitations, setShowCitations] = React.useState(false)
  const [isHovered, setIsHovered] = React.useState(false)
  const [feedback, setFeedback] = React.useState<"up" | "down" | null>(null)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    // TODO: Show toast notification
  }

  const handleEdit = () => {
    // TODO: Implement message editing
    console.log("Edit message:", message.id)
  }

  const handleRegenerate = () => {
    // TODO: Implement message regeneration
    console.log("Regenerate message:", message.id)
  }

  const handleFeedback = (type: "up" | "down") => {
    setFeedback(type)
    // TODO: Send feedback to API
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  // System message
  if (message.role === "system") {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="flex justify-center"
      >
        <div className="bg-muted/50 text-muted-foreground px-4 py-2 rounded-full text-sm">
          {message.content}
        </div>
      </motion.div>
    )
  }

  // User message
  if (message.role === "user") {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex justify-end"
        data-message-id={message.id}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="flex items-start space-x-3 max-w-[80%]">
          <div className="flex flex-col items-end space-y-2">
            {/* Files */}
            {message.files && message.files.length > 0 && (
              <div className="space-y-2">
                {message.files.map((file) => (
                  <div
                    key={file.id}
                    className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-sm"
                  >
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                        📄
                      </div>
                      <div>
                        <div className="font-medium">{file.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {formatFileSize(file.size)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Message content */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-lg">
              <div className="whitespace-pre-wrap break-words">
                {message.content}
              </div>
            </div>

            {/* Timestamp and actions */}
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <span>{formatTimestamp(message.timestamp)}</span>
              <AnimatePresence>
                {isHovered && isLast && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="flex items-center space-x-1"
                  >
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={handleCopy}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={handleEdit}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* User avatar */}
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
            <User className="h-4 w-4 text-primary-foreground" />
          </div>
        </div>
      </motion.div>
    )
  }

  // Assistant message
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="flex justify-start"
      data-message-id={message.id}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start space-x-3 max-w-[80%]">
        {/* AI avatar */}
        <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="h-4 w-4 text-white" />
        </div>

        <div className="flex flex-col space-y-2 flex-1">
          {/* Model badge */}
          {message.model && (
            <div className="flex items-center space-x-2">
              <Badge 
                variant={message.model === "maverick" ? "default" : "secondary"}
                size="sm"
              >
                {message.model === "maverick" ? (
                  <>
                    <Sparkles className="mr-1 h-3 w-3" />
                    Llama Maverick
                  </>
                ) : (
                  "Local LLM"
                )}
              </Badge>
              {isStreaming && (
                <Badge variant="outline" size="sm">
                  Streaming...
                </Badge>
              )}
            </div>
          )}

          {/* Message content */}
          <div className="bg-card border border-border rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <CodeBlock content={message.content} />
            </div>
          </div>

          {/* Citations */}
          {message.citations && message.citations.length > 0 && (
            <div className="space-y-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCitations(!showCitations)}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                {showCitations ? (
                  <>
                    <ChevronUp className="mr-1 h-3 w-3" />
                    Hide {message.citations.length} citations
                  </>
                ) : (
                  <>
                    <ChevronDown className="mr-1 h-3 w-3" />
                    Show {message.citations.length} citations
                  </>
                )}
              </Button>

              <AnimatePresence>
                {showCitations && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-2"
                  >
                    {message.citations.map((citation, index) => (
                      <CitationCard
                        key={citation.id}
                        citation={citation}
                        index={index + 1}
                      />
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Timestamp and actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <span>{formatTimestamp(message.timestamp)}</span>
              {message.content.length > 100 && (
                <span>• {message.content.length} chars</span>
              )}
            </div>

            <AnimatePresence>
              {isHovered && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center space-x-1"
                >
                  <MessageActions
                    message={message}
                    onCopy={handleCopy}
                    onEdit={handleEdit}
                    onRegenerate={handleRegenerate}
                    onFeedback={handleFeedback}
                    feedback={feedback}
                    isLast={isLast}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

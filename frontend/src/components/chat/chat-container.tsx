"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Message } from "./message"
import { TypingIndicator } from "./typing-indicator"

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

interface ChatContainerProps {
  messages: Message[]
  isLoading: boolean
  isStreaming: boolean
}

export function ChatContainer({ messages, isLoading, isStreaming }: ChatContainerProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Message
              message={message}
              isLast={index === messages.length - 1}
              isStreaming={isStreaming && index === messages.length - 1}
            />
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Typing Indicator */}
      <AnimatePresence>
        {(isLoading || isStreaming) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <TypingIndicator />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

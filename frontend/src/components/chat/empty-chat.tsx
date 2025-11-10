"use client"

import * as React from "react"
import { motion } from "framer-motion"
import {
  Bot,
} from "lucide-react"

interface EmptyChatProps {
  onSendMessage: (content: string, files?: File[]) => void
  onSuggestionClick?: (suggestion: string) => void
}

export function EmptyChat({ onSendMessage, onSuggestionClick }: EmptyChatProps) {
  const suggestions = [
    "Analyze the error patterns in my logs",
    "What are the most common issues in my logs?",
    "Show me performance bottlenecks",
    "Help me troubleshoot this error",
    "Generate a summary of my log data"
  ]

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-[#0A0E14] via-[#0D1117] to-[#0A0E14]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="p-8 text-center"
      >
        <div className="space-y-4">
          <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto shadow-2xl">
            <Bot className="h-10 w-10 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white">Start a New Conversation</h2>
            <p className="text-gray-400 mt-2 text-lg">
              Ask questions about your logs, upload files, or get AI-powered insights
            </p>
          </div>
        </div>
      </motion.div>

      {/* Suggestions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex-1 flex items-center justify-center px-8"
      >
        <div className="max-w-4xl w-full">
          <h3 className="text-xl font-semibold text-white mb-6 text-center">
            Try asking about:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {suggestions.map((suggestion, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                onClick={() => onSuggestionClick?.(suggestion)}
                className="p-4 bg-[#161B22] hover:bg-[#1C2128] border border-[#30363D] hover:border-blue-600/50 rounded-xl text-left text-gray-300 hover:text-white transition-all shadow-lg hover:shadow-blue-600/20"
              >
                <p className="text-sm font-medium">{suggestion}</p>
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  )
}

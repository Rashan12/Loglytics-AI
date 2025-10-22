"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Bot, Sparkles } from "lucide-react"

interface TypingIndicatorProps {
  model?: "local" | "maverick"
}

export function TypingIndicator({ model = "local" }: TypingIndicatorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="flex justify-start"
    >
      <div className="flex items-start space-x-3 max-w-[80%]">
        {/* AI avatar */}
        <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
          {model === "maverick" ? (
            <Sparkles className="h-4 w-4 text-white" />
          ) : (
            <Bot className="h-4 w-4 text-white" />
          )}
        </div>

        <div className="flex flex-col space-y-2 flex-1">
          {/* Model badge */}
          <div className="flex items-center space-x-2">
            <div className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
              {model === "maverick" ? "Llama Maverick" : "Local LLM"}
            </div>
          </div>

          {/* Typing animation */}
          <div className="bg-card border border-border rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">
                {model === "maverick" ? "Llama Maverick is analyzing" : "AI is thinking"}
              </span>
              <div className="flex space-x-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-primary rounded-full"
                    animate={{
                      scale: [1, 1.3, 1],
                      opacity: [0.4, 1, 0.4],
                    }}
                    transition={{
                      duration: 1.2,
                      repeat: Infinity,
                      delay: i * 0.15,
                      ease: "easeInOut",
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

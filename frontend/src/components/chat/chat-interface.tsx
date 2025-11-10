'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ChatMessage } from '@/types'
import { chatService } from '@/services/chat-service'
import { formatDate } from '@/lib/utils'
import { MessageSquare, Send, Bot, User, Sparkles } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { ChatInput } from './chat-input'
import { ModelSelector } from './model-selector'
import { Message } from './message'

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState<"local" | "maverick">("maverick")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    initializeChat()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const initializeChat = async () => {
    try {
      const sessionId = `session_${Date.now()}`
      const session = await chatService.createChatSession({
        session_id: sessionId,
        title: 'New Chat Session'
      })
      setCurrentSessionId(sessionId)
      
      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: 0,
        session_id: session.id,
        role: 'assistant',
        content: 'Hello! I\'m Loglytics AI. I can help you analyze your logs, detect patterns, and answer questions about your system. How can I assist you today?',
        created_at: new Date().toISOString()
      }
      setMessages([welcomeMessage])
    } catch (error) {
      toast.error('Failed to initialize chat')
    }
  }

  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!content.trim() && (!files || files.length === 0) || !currentSessionId || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now(),
      session_id: 0,
      role: 'user',
      content: content || (files && files.length > 0 ? '📎 Uploaded file for analysis' : ''),
      created_at: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await chatService.sendMessage(currentSessionId, {
        role: 'user',
        content: content
      })
      
      setMessages(prev => [...prev, response])
    } catch (error) {
      toast.error('Failed to send message')
      // Add error message
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        session_id: 0,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Chat Header */}
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      >
        <div className="flex h-16 items-center justify-between px-4">
          {/* Left side */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold">AI Assistant</h1>
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <span>{messages.length} messages</span>
                  <span>•</span>
                  <span>Ready to help</span>
                </div>
              </div>
            </div>
          </div>

          {/* Center - Model Selector */}
          <div className="flex-1 max-w-md mx-4">
            <ModelSelector 
              currentModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-2">
            {isLoading && (
              <Badge variant="outline" className="text-xs">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  <span>Thinking...</span>
                </div>
              </Badge>
            )}
          </div>
        </div>
      </motion.header>

      {/* Messages Container */}
      <div className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto">
                <Sparkles className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Welcome to Loglytics AI</h3>
                <p className="text-muted-foreground">Start a conversation to analyze your logs</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="relative h-full">
            <div className="h-full overflow-y-auto px-4 py-6">
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <Message
                    key={message.id}
                    message={{
                      id: message.id.toString(),
                      role: message.role as "user" | "assistant" | "system",
                      content: message.content,
                      timestamp: message.created_at,
                      model: selectedModel,
                    }}
                    isLast={index === messages.length - 1}
                    isStreaming={isLoading && index === messages.length - 1}
                  />
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-3 max-w-[80%]">
                      <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="bg-card border border-border rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                          </div>
                          <span className="text-sm text-muted-foreground">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <motion.div
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="sticky bottom-0 w-full border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      >
        <div className="p-4">
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask about your logs..."
          />
        </div>
      </motion.div>
    </div>
  )
}

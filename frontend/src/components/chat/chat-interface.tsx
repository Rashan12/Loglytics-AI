'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ChatMessage } from '@/types'
import { chatService } from '@/services/chat-service'
import { formatDate } from '@/lib/utils'
import { MessageSquare, Send, Bot, User } from 'lucide-react'
import { toast } from 'react-hot-toast'

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
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

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentSessionId || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now(),
      session_id: 0,
      role: 'user',
      content: inputMessage,
      created_at: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await chatService.sendMessage(currentSessionId, {
        role: 'user',
        content: inputMessage
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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">AI Chat Assistant</h2>
        <p className="text-muted-foreground">
          Ask questions about your logs and get AI-powered insights
        </p>
      </div>

      <Card className="h-[600px] flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Chat Session</span>
            {currentSessionId && (
              <Badge variant="outline">Active</Badge>
            )}
          </CardTitle>
          <CardDescription>
            {messages.length} messages in this session
          </CardDescription>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    <div className="flex-shrink-0">
                      {message.role === 'user' ? (
                        <User className="h-4 w-4 mt-1" />
                      ) : (
                        <Bot className="h-4 w-4 mt-1" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {formatDate(message.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-4 w-4" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="flex space-x-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your logs..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              onClick={sendMessage} 
              disabled={!inputMessage.trim() || isLoading}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

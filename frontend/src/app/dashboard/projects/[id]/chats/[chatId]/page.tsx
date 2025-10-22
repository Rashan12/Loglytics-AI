"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useParams, useRouter } from "next/navigation"
import {
  ArrowLeft,
  MoreHorizontal,
  Edit,
  Trash2,
  RotateCcw,
  Download,
  Share,
  Settings,
  X,
  Send,
  Paperclip,
  Bot,
  User,
  Sparkles,
  Search,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/store/auth-store"
import { useChatStore } from "@/store/chat-store"
import { ChatContainer } from "@/components/chat/chat-container"
import { ChatInput } from "@/components/chat/chat-input"
import { ModelSelector } from "@/components/chat/model-selector"
import { EmptyChat } from "@/components/chat/empty-chat"
import { MessageSearch } from "@/components/chat/message-search"
import { ChatExport } from "@/components/chat/chat-export"

interface Chat {
  id: string
  title: string
  projectId: string
  model: "local" | "maverick"
  createdAt: string
  updatedAt: string
  messageCount: number
}

const mockChat: Chat = {
  id: "1",
  title: "API Error Analysis",
  projectId: "1",
  model: "local",
  createdAt: "2024-01-15T10:30:00Z",
  updatedAt: "2024-01-15T10:30:00Z",
  messageCount: 0,
}

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuthStore()
  const { 
    messages, 
    isLoading, 
    isStreaming, 
    currentChat, 
    setCurrentChat,
    sendMessage,
    stopGeneration,
    clearChat,
    deleteChat,
  } = useChatStore()

  const [isEditingTitle, setIsEditingTitle] = React.useState(false)
  const [chatTitle, setChatTitle] = React.useState(mockChat.title)
  const [showScrollButton, setShowScrollButton] = React.useState(false)
  const [showSearch, setShowSearch] = React.useState(false)
  const [showExport, setShowExport] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)
  const messagesContainerRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    setCurrentChat(mockChat)
  }, [setCurrentChat])

  React.useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  React.useEffect(() => {
    // Show scroll button when not at bottom
    const container = messagesContainerRef.current
    if (!container) return

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container
      setShowScrollButton(scrollTop < scrollHeight - clientHeight - 100)
    }

    container.addEventListener("scroll", handleScroll)
    return () => container.removeEventListener("scroll", handleScroll)
  }, [])

  const handleTitleEdit = () => {
    setIsEditingTitle(true)
  }

  const handleTitleSave = () => {
    setIsEditingTitle(false)
    // TODO: Update chat title via API
  }

  const handleTitleCancel = () => {
    setChatTitle(mockChat.title)
    setIsEditingTitle(false)
  }

  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!content.trim() && (!files || files.length === 0)) return
    
    await sendMessage(content, files)
  }

  const handleStopGeneration = () => {
    stopGeneration()
  }

  const handleClearChat = () => {
    clearChat()
  }

  const handleDeleteChat = () => {
    deleteChat()
    router.push(`/dashboard/projects/${params.id}`)
  }

  const handleScrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleBackToProjects = () => {
    router.push(`/dashboard/projects/${params.id}`)
  }

  const handleMessageSelect = (messageId: string) => {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`)
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: "smooth", block: "center" })
      // Highlight the message briefly
      messageElement.classList.add("ring-2", "ring-primary", "ring-opacity-50")
      setTimeout(() => {
        messageElement.classList.remove("ring-2", "ring-primary", "ring-opacity-50")
      }, 3000)
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
            <Button
              variant="ghost"
              size="icon"
              onClick={handleBackToProjects}
              className="h-8 w-8"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
              <div>
                {isEditingTitle ? (
                  <Input
                    value={chatTitle}
                    onChange={(e) => setChatTitle(e.target.value)}
                    onBlur={handleTitleSave}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleTitleSave()
                      if (e.key === "Escape") handleTitleCancel()
                    }}
                    className="h-8 text-lg font-semibold"
                    autoFocus
                  />
                ) : (
                  <h1 
                    className="text-lg font-semibold cursor-pointer hover:bg-accent px-2 py-1 rounded"
                    onClick={handleTitleEdit}
                  >
                    {chatTitle}
                  </h1>
                )}
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <span>{mockChat.messageCount} messages</span>
                  <span>•</span>
                  <span>Updated {new Date(mockChat.updatedAt).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Center - Model Selector */}
          <div className="flex-1 max-w-md mx-4">
            <ModelSelector 
              currentModel={mockChat.model}
              onModelChange={(model) => {
                // TODO: Update model via API
                console.log("Model changed to:", model)
              }}
            />
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-2">
            {isStreaming && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleStopGeneration}
                className="text-destructive hover:text-destructive"
              >
                <X className="mr-2 h-4 w-4" />
                Stop
              </Button>
            )}
            
            {/* Search Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowSearch(true)}
              className="h-8 w-8"
              title="Search messages"
            >
              <Search className="h-4 w-4" />
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={handleTitleEdit}>
                  <Edit className="mr-2 h-4 w-4" />
                  Rename Chat
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleClearChat}>
                  <RotateCcw className="mr-2 h-4 w-4" />
                  Clear History
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setShowExport(true)}>
                  <Download className="mr-2 h-4 w-4" />
                  Export Chat
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Share className="mr-2 h-4 w-4" />
                  Share Chat
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={handleDeleteChat}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete Chat
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </motion.header>

      {/* Messages Container */}
      <div className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <EmptyChat onSendMessage={handleSendMessage} />
        ) : (
          <div className="relative h-full">
            <div
              ref={messagesContainerRef}
              className="h-full overflow-y-auto px-4 py-6"
            >
              <ChatContainer 
                messages={messages}
                isLoading={isLoading}
                isStreaming={isStreaming}
              />
              <div ref={messagesEndRef} />
            </div>

            {/* Scroll to Bottom Button */}
            <AnimatePresence>
              {showScrollButton && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="absolute bottom-20 right-6 z-10"
                >
                  <Button
                    size="icon"
                    className="h-10 w-10 rounded-full shadow-lg"
                    onClick={handleScrollToBottom}
                  >
                    <ArrowLeft className="h-4 w-4 rotate-90" />
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
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
            disabled={isStreaming}
            placeholder="Ask about your logs..."
          />
        </div>
      </motion.div>

      {/* Message Search Modal */}
      <MessageSearch
        messages={messages}
        onMessageSelect={handleMessageSelect}
        isOpen={showSearch}
        onClose={() => setShowSearch(false)}
      />

      {/* Chat Export Modal */}
      <ChatExport
        chat={mockChat}
        messages={messages}
        isOpen={showExport}
        onClose={() => setShowExport(false)}
      />
    </div>
  )
}

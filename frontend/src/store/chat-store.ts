"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"

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

interface Chat {
  id: string
  title: string
  projectId: string
  model: "local" | "maverick"
  createdAt: string
  updatedAt: string
  messageCount: number
  messages: Message[]
}

interface ChatState {
  // Current chat
  currentChat: Chat | null
  messages: Message[]
  isLoading: boolean
  isStreaming: boolean
  
  // Chat management
  chats: Chat[]
  
  // Actions
  setCurrentChat: (chat: Chat | null) => void
  addMessage: (message: Omit<Message, "id" | "timestamp">) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  deleteMessage: (id: string) => void
  clearMessages: () => void
  
  // Chat operations
  createChat: (projectId: string, title: string, model: "local" | "maverick") => void
  updateChat: (id: string, updates: Partial<Chat>) => void
  deleteChat: (id: string) => void
  loadChat: (id: string) => void
  
  // Message operations
  sendMessage: (content: string, files?: File[]) => Promise<void>
  stopGeneration: () => void
  
  // Streaming
  startStreaming: () => void
  stopStreaming: () => void
  updateStreamingMessage: (content: string) => void
}

// Helper function to upload files
const uploadFiles = async (files: File[]) => {
  const uploadedFiles = []
  
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await fetch('/api/v1/logs/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      })
      
      if (response.ok) {
        const result = await response.json()
        uploadedFiles.push({
          id: result.id,
          name: file.name,
          size: file.size,
          type: file.type,
          url: result.url,
        })
      }
    } catch (error) {
      console.error('Failed to upload file:', file.name, error)
    }
  }
  
  return uploadedFiles
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentChat: null,
      messages: [],
      isLoading: false,
      isStreaming: false,
      chats: [],

      // Chat management
      setCurrentChat: (chat) => {
        set({ currentChat: chat, messages: chat?.messages || [] })
      },

      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: Math.random().toString(36).substr(2, 9),
          timestamp: new Date().toISOString(),
        }
        
        set((state) => ({
          messages: [...state.messages, newMessage],
          currentChat: state.currentChat ? {
            ...state.currentChat,
            messages: [
              ...(state.currentChat.messages || []),  // ✅ Safe with fallback
              newMessage
            ],
            messageCount: (state.currentChat.messageCount || 0) + 1,
            updatedAt: new Date().toISOString(),
          } : null,
        }))
      },

      updateMessage: (id, updates) => {
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg
          ),
          currentChat: state.currentChat ? {
            ...state.currentChat,
            messages: (state.currentChat.messages || []).map((msg) =>
              msg.id === id ? { ...msg, ...updates } : msg
            ),
          } : null,
        }))
      },

      deleteMessage: (id) => {
        set((state) => ({
          messages: state.messages.filter((msg) => msg.id !== id),
          currentChat: state.currentChat ? {
            ...state.currentChat,
            messages: (state.currentChat.messages || []).filter((msg) => msg.id !== id),
            messageCount: Math.max(0, (state.currentChat.messageCount || 0) - 1),
          } : null,
        }))
      },

      clearMessages: () => {
        set((state) => ({
          messages: [],
          currentChat: state.currentChat ? {
            ...state.currentChat,
            messages: [],
            messageCount: 0,
          } : null,
        }))
      },

      // Chat operations
      createChat: (projectId, title, model) => {
        const newChat: Chat = {
          id: Math.random().toString(36).substr(2, 9),
          title,
          projectId,
          model,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 0,
          messages: [],  // ✅ Initialize as empty array
        }
        
        set((state) => ({
          chats: [...state.chats, newChat],
          currentChat: newChat,
          messages: [],
        }))
      },

      updateChat: (id, updates) => {
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.id === id ? { ...chat, ...updates } : chat
          ),
          currentChat: state.currentChat?.id === id
            ? { ...state.currentChat, ...updates }
            : state.currentChat,
        }))
      },

      deleteChat: (id) => {
        set((state) => ({
          chats: state.chats.filter((chat) => chat.id !== id),
          currentChat: state.currentChat?.id === id ? null : state.currentChat,
          messages: state.currentChat?.id === id ? [] : state.messages,
        }))
      },

      loadChat: (id) => {
        const chat = get().chats.find((c) => c.id === id)
        if (chat) {
          set({ currentChat: chat, messages: chat.messages })
        }
      },

      // Message operations
      sendMessage: async (content, files) => {
        const { currentChat, addMessage, startStreaming, stopStreaming } = get()
        
        if (!currentChat) return

        // Add user message
        addMessage({
          role: "user",
          content,
          files: files?.map((file) => ({
            id: Math.random().toString(36).substr(2, 9),
            name: file.name,
            size: file.size,
            type: file.type,
          })),
        })

        // Start streaming
        startStreaming()
        
        // Add assistant message placeholder
        const assistantMessageId = Math.random().toString(36).substr(2, 9)
        addMessage({
          role: "assistant",
          content: "",
          model: currentChat.model,
          isStreaming: true,
        })

        try {
          // Upload files if any
          let uploadedFiles = []
          if (files && files.length > 0) {
            uploadedFiles = await uploadFiles(files)
          }

          // Send message to API
          const response = await fetch(`/api/v1/chats/${currentChat.id}/messages`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify({
              content,
              files: uploadedFiles,
              model: currentChat.model,
            }),
          })

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }

          // Handle streaming response
          const reader = response.body?.getReader()
          if (!reader) {
            throw new Error('No response body')
          }

          const decoder = new TextDecoder()
          let currentContent = ""

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value)
            const lines = chunk.split('\n')

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  
                  if (data.type === 'content') {
                    currentContent += data.content
                    get().updateMessage(assistantMessageId, { content: currentContent })
                  } else if (data.type === 'citations') {
                    get().updateMessage(assistantMessageId, { 
                      content: currentContent,
                      citations: data.citations 
                    })
                  } else if (data.type === 'done') {
                    get().updateMessage(assistantMessageId, {
                      content: currentContent,
                      isStreaming: false,
                      citations: data.citations || [],
                    })
                    break
                  }
                } catch (e) {
                  console.warn('Failed to parse SSE data:', e)
                }
              }
            }
          }
          
        } catch (error) {
          console.error("Error sending message:", error)
          get().updateMessage(assistantMessageId, {
            content: "Sorry, I encountered an error while processing your request. Please try again.",
            isStreaming: false,
          })
        } finally {
          stopStreaming()
        }
      },

      stopGeneration: () => {
        set((state) => ({
          isStreaming: false,
          messages: state.messages.map((msg) =>
            msg.isStreaming ? { ...msg, isStreaming: false } : msg
          ),
        }))
      },

      // Streaming
      startStreaming: () => {
        set({ isStreaming: true })
      },

      stopStreaming: () => {
        set({ isStreaming: false })
      },

      updateStreamingMessage: (content) => {
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.isStreaming ? { ...msg, content } : msg
          ),
        }))
      },
    }),
    {
      name: "chat-store",
      partialize: (state) => ({
        chats: state.chats,
        currentChat: state.currentChat,
      }),
    }
  )
)

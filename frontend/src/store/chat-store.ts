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
  selectedModel: "local" | "maverick"
  
  // Chat management
  chats: Chat[]
  chatMessages: Record<string, Message[]>
  
  // Actions
  setCurrentChat: (chat: Chat | null) => void
  addMessage: (message: Omit<Message, "id" | "timestamp">) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  deleteMessage: (id: string) => void
  clearMessages: () => void
  
  // Model selection
  setSelectedModel: (model: "local" | "maverick") => void
  
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
      selectedModel: "maverick", // Default to maverick model
      chats: [],
      
      // Per-chat message storage
      chatMessages: {} as Record<string, Message[]>,

      // Chat management
      setCurrentChat: (chat) => {
        const chatId = chat?.id || 'default'
        const messages = chat ? (get().chatMessages[chatId] || chat.messages || []) : []
        set({ currentChat: chat, messages })
      },

      // Model selection
      setSelectedModel: (model) => {
        set({ selectedModel: model })
      },

      // Add message helper respects provided id/timestamps
      addMessage: (message) => {
        const nowIso = new Date().toISOString()
        const newMessage: Message = {
          ...message,
          id: (message as any).id || Math.random().toString(36).substr(2, 9),
          timestamp: (message as any).timestamp || nowIso,
          // @ts-ignore attach optional fallbacks used by UI
          createdAt: (message as any).createdAt || nowIso,
          // @ts-ignore
          created_at: (message as any).created_at || nowIso,
        }
        set((state) => {
          const chatId = state.currentChat?.id || 'default'
          const updatedMessages = [...(state.chatMessages[chatId] || []), newMessage]
          return {
            messages: updatedMessages,
            chatMessages: {
              ...state.chatMessages,
              [chatId]: updatedMessages
            },
            currentChat: state.currentChat ? {
              ...state.currentChat,
              messages: updatedMessages,
              messageCount: updatedMessages.length,
              updatedAt: nowIso,
            } : state.currentChat,
          }
        })
      },

      updateMessage: (id, updates) => {
        set((state) => {
          const chatId = state.currentChat?.id || 'default'
          const updatedMessages = state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg
          )
          return {
            messages: [...updatedMessages],
            chatMessages: {
              ...state.chatMessages,
              [chatId]: [...updatedMessages]
            },
            currentChat: state.currentChat ? {
              ...state.currentChat,
              messages: [...updatedMessages],
            } : null,
          }
        })
      },

      deleteMessage: (id) => {
        set((state) => {
          const chatId = state.currentChat?.id || 'default'
          const updatedMessages = state.messages.filter((msg) => msg.id !== id)
          
          return {
            messages: updatedMessages,
            chatMessages: {
              ...state.chatMessages,
              [chatId]: updatedMessages
            },
            currentChat: state.currentChat ? {
              ...state.currentChat,
              messages: updatedMessages,
              messageCount: Math.max(0, updatedMessages.length),
            } : null,
          }
        })
      },

      clearMessages: () => {
        set((state) => {
          const chatId = state.currentChat?.id || 'default'
          
          return {
            messages: [],
            chatMessages: {
              ...state.chatMessages,
              [chatId]: []
            },
            currentChat: state.currentChat ? {
              ...state.currentChat,
              messages: [],
              messageCount: 0,
            } : null,
          }
        })
      },

      // Chat operations
      createChat: (projectId, title, model) => {
        // Check if chat already exists for this project
        const existingChat = get().chats.find(c => c.projectId === projectId)
        if (existingChat) {
          set({ currentChat: existingChat, messages: get().chatMessages[existingChat.id] || [] })
          return
        }
        
        const chatId = Math.random().toString(36).substr(2, 9)
        const newChat: Chat = {
          id: chatId,
          title,
          projectId,
          model,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 0,
          messages: [],
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
          const messages = get().chatMessages[id] || chat.messages || []
          set({ currentChat: chat, messages })
        }
      },

      // Message operations
      sendMessage: async (content, files) => {
        const { currentChat, selectedModel, addMessage, startStreaming, stopStreaming } = get()
        
        // For AI Assistant page, we don't need a currentChat
        // Use selectedModel instead of currentChat.model
        const model = currentChat?.model || selectedModel

        // Add user message
        const userMessageId = Math.random().toString(36).substr(2, 9);
        const now = new Date().toISOString();
        addMessage({
          role: "user",
          content,
          files: files?.map((file) => ({
            id: Math.random().toString(36).substr(2, 9),
            name: file.name,
            size: file.size,
            type: file.type,
          })),
          id: userMessageId,
          timestamp: now,
          createdAt: now,
          created_at: now,
        });

        // Start streaming
        startStreaming();

        // Add assistant message placeholder with deterministic id
        const assistantMessageId = `assistant_${userMessageId}`;
        addMessage({
          role: "assistant",
          content: "",
          model: model,
          isStreaming: true,
          id: assistantMessageId,
          timestamp: now,
          createdAt: now,
          created_at: now,
        });

        try {
          // Use the configured API client instead of fetch
          const api = (await import('@/lib/api')).default
          
          
          const formData = new FormData()
          
          if (files && files.length > 0) {
            formData.append('file', files[0])
            
          }
          
          formData.append('message', content)
          
          const response = await api.post('/chat', formData, {
            headers: {
              'Content-Type': undefined // Let Axios set the correct Content-Type for FormData
            }
          })

          const data = response.data
          
          get().updateMessage(assistantMessageId, {
            content: data.response || "I've analyzed your request. What would you like to know?",
            isStreaming: false,
            citations: data.citations || [],
            timestamp: new Date().toISOString(),
            createdAt: new Date().toISOString(),
            created_at: new Date().toISOString(),
          })
          
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
        chatMessages: state.chatMessages,
      }),
    }
  )
)

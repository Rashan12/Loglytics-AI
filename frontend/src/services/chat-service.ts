import { api } from '@/lib/api'
import { ChatSession, ChatMessage } from '@/types'

export const chatService = {
  async createChatSession(sessionData: {
    session_id: string
    title?: string
    context?: any
  }): Promise<ChatSession> {
    const response = await api.post('/chat/sessions', sessionData)
    return response.data
  },

  async getChatSessions(page: number = 1, size: number = 20): Promise<ChatSession[]> {
    const response = await api.get('/chat/sessions', {
      params: { skip: (page - 1) * size, limit: size }
    })
    return response.data
  },

  async getChatSession(sessionId: string): Promise<ChatSession> {
    const response = await api.get(`/chat/sessions/${sessionId}`)
    return response.data
  },

  async sendMessage(sessionId: string, message: {
    role: string
    content: string
    metadata?: any
  }): Promise<ChatMessage> {
    const response = await api.post(`/chat/sessions/${sessionId}/messages`, message)
    return response.data
  },

  async getChatMessages(
    sessionId: string,
    page: number = 1,
    size: number = 50
  ): Promise<ChatMessage[]> {
    const response = await api.get(`/chat/sessions/${sessionId}/messages`, {
      params: { skip: (page - 1) * size, limit: size }
    })
    return response.data
  }
}

import { api } from '@/lib/api'
import { LogFile, LogEntry, PaginatedResponse } from '@/types'

export const logService = {
  async uploadLogFile(file: File): Promise<LogFile> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/logs/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },

  async getLogFiles(page: number = 1, size: number = 20): Promise<PaginatedResponse<LogFile>> {
    const response = await api.get('/logs', {
      params: { skip: (page - 1) * size, limit: size }
    })
    return response.data
  },

  async getLogFile(id: number): Promise<LogFile> {
    const response = await api.get(`/logs/${id}`)
    return response.data
  },

  async deleteLogFile(id: number): Promise<void> {
    await api.delete(`/logs/${id}`)
  },

  async getLogEntries(
    logFileId: number,
    page: number = 1,
    size: number = 50,
    filters?: {
      level?: string
      search?: string
      startDate?: string
      endDate?: string
    }
  ): Promise<PaginatedResponse<LogEntry>> {
    const response = await api.get(`/logs/${logFileId}/entries`, {
      params: {
        skip: (page - 1) * size,
        limit: size,
        ...filters
      }
    })
    return response.data
  }
}

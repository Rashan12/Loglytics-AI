import { api } from '@/lib/api'

export interface LiveLogConnection {
  id: string
  connection_name: string
  cloud_provider: 'aws' | 'azure' | 'gcp'
  status: 'active' | 'paused' | 'error'
  last_sync_at?: string
  created_at: string
  updated_at?: string
  logs_per_second?: number
  logs_today?: number
  errors_today?: number
  connection_config?: any
}

export interface CreateConnectionRequest {
  connection_name: string
  cloud_provider: 'aws' | 'azure' | 'gcp'
  connection_config: Record<string, any>
  project_id: string
}

export interface UpdateConnectionRequest {
  connection_name?: string
  connection_config?: Record<string, any>
  status?: 'active' | 'paused' | 'error'
}

export interface TestConnectionRequest {
  connection_config: Record<string, any>
  cloud_provider: 'aws' | 'azure' | 'gcp'
}

export interface TestConnectionResponse {
  success: boolean
  message: string
  details?: any
}

export interface LogEntry {
  id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
  message: string
  source?: string
  service?: string
  metadata?: any
  connection_id: string
}

export interface Alert {
  id: string
  timestamp: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  connection_id: string
  connection_name: string
  is_read: boolean
  alert_type: 'error_threshold' | 'keyword' | 'anomaly' | 'connection'
  details?: any
}

export interface ConnectionStats {
  total_logs_today: number
  logs_per_second: number
  error_rate: number
  top_errors: Array<{ message: string; count: number }>
  active_connections: number
  total_connections: number
}

export const liveLogsService = {
  // Connection Management
  async getConnections(projectId: string): Promise<LiveLogConnection[]> {
    const response = await api.get(`/live-logs/connections/${projectId}`)
    return response.data
  },

  async getConnection(connectionId: string): Promise<LiveLogConnection> {
    const response = await api.get(`/live-logs/connections/${connectionId}`)
    return response.data
  },

  async createConnection(data: CreateConnectionRequest): Promise<LiveLogConnection> {
    const response = await api.post('/live-logs/connections', data)
    return response.data
  },

  async updateConnection(connectionId: string, data: UpdateConnectionRequest): Promise<LiveLogConnection> {
    const response = await api.put(`/live-logs/connections/${connectionId}`, data)
    return response.data
  },

  async deleteConnection(connectionId: string): Promise<void> {
    await api.delete(`/live-logs/connections/${connectionId}`)
  },

  async testConnection(data: TestConnectionRequest): Promise<TestConnectionResponse> {
    const response = await api.post('/live-logs/connections/test', data)
    return response.data
  },

  // Stream Management
  async startStream(connectionId: string): Promise<void> {
    await api.post(`/live-logs/connections/${connectionId}/start`)
  },

  async stopStream(connectionId: string): Promise<void> {
    await api.post(`/live-logs/connections/${connectionId}/stop`)
  },

  async pauseStream(connectionId: string): Promise<void> {
    await api.post(`/live-logs/connections/${connectionId}/pause`)
  },

  async resumeStream(connectionId: string): Promise<void> {
    await api.post(`/live-logs/connections/${connectionId}/resume`)
  },

  // Log Data
  async getRecentLogs(
    projectId: string,
    limit: number = 100,
    connectionId?: string
  ): Promise<LogEntry[]> {
    const params: any = { limit }
    if (connectionId) params.connection_id = connectionId

    const response = await api.get(`/live-logs/stream/${projectId}`, { params })
    return response.data.logs
  },

  async getLogsByTimeRange(
    projectId: string,
    startTime: string,
    endTime: string,
    connectionId?: string
  ): Promise<LogEntry[]> {
    const params: any = {
      start_time: startTime,
      end_time: endTime
    }
    if (connectionId) params.connection_id = connectionId

    const response = await api.get(`/live-logs/stream/${projectId}`, { params })
    return response.data.logs
  },

  // Alerts
  async getAlerts(
    projectId: string,
    unreadOnly: boolean = false,
    severity?: string
  ): Promise<Alert[]> {
    const params: any = {}
    if (unreadOnly) params.unread = true
    if (severity) params.severity = severity

    const response = await api.get(`/alerts`, { params })
    return response.data.alerts
  },

  async markAlertAsRead(alertId: string): Promise<void> {
    await api.put(`/alerts/${alertId}/read`)
  },

  async markAllAlertsAsRead(projectId: string): Promise<void> {
    await api.put(`/alerts/read-all`, { project_id: projectId })
  },

  async dismissAlert(alertId: string): Promise<void> {
    await api.delete(`/alerts/${alertId}`)
  },

  // Statistics
  async getConnectionStats(projectId: string): Promise<ConnectionStats> {
    const response = await api.get(`/live-logs/stats/${projectId}`)
    return response.data
  },

  async getConnectionMetrics(connectionId: string): Promise<{
    logs_per_second: number
    error_rate: number
    logs_today: number
    errors_today: number
  }> {
    const response = await api.get(`/live-logs/connections/${connectionId}/metrics`)
    return response.data
  },

  // Export
  async exportLogs(
    projectId: string,
    format: 'json' | 'csv' | 'txt',
    startTime?: string,
    endTime?: string,
    connectionId?: string
  ): Promise<Blob> {
    const params: any = { format }
    if (startTime) params.start_time = startTime
    if (endTime) params.end_time = endTime
    if (connectionId) params.connection_id = connectionId

    const response = await api.get(`/live-logs/export/${projectId}`, {
      params,
      responseType: 'blob'
    })
    return response.data
  },

  // Health Check
  async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy'
    message: string
    services: Record<string, boolean>
  }> {
    const response = await api.get('/live-logs/health')
    return response.data
  }
}

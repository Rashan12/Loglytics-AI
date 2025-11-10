import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { useAuthStore } from './auth-store'

export interface LiveLogConnection {
  id: string
  name: string
  platform: 'aws' | 'azure' | 'gcp' | 'docker'
  status: 'active' | 'inactive' | 'error' | 'testing' | 'paused'
  api_key_prefix: string
  tenant_id: string
  last_seen: string | null
  total_logs_received: number
  logs_per_minute: number
  created_at: string
}

export interface LiveLogConnectionDetail extends LiveLogConnection {
  api_key?: string // Only available on creation
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

export interface LiveLogsState {
  // Connections
  connections: LiveLogConnection[]
  activeConnection: string | null
  isLoading: boolean
  error: string | null
  
  // Logs
  logs: LogEntry[]
  filteredLogs: LogEntry[]
  isStreaming: boolean
  isPaused: boolean
  autoScroll: boolean
  
  // Filters
  logLevels: string[]
  timeRange: string
  sourceFilter: string
  
  // Stats
  logsPerSecond: number
  errorRate: number
  
  // Alerts
  alerts: Alert[]
  unreadAlerts: Alert[]
  
  // Connection management
  reconnectAttempts: number
  
  // Helper function to get token
  getToken: () => string | null
  
  // Actions
  fetchConnections: () => Promise<void>
  createConnection: (name: string, platform: string, projectId?: string) => Promise<LiveLogConnectionDetail>
  deleteConnection: (id: string) => Promise<void>
  testConnection: (tenantId: string, apiKey: string) => Promise<boolean>
  setActiveConnection: (id: string | null) => void
  
  // Streaming actions
  setStreaming: (streaming: boolean) => void
  setPaused: (paused: boolean) => void
  setAutoScroll: (autoScroll: boolean) => void
  clearLogs: () => void
  
  // Filter actions
  setLogLevels: (levels: string[]) => void
  setTimeRange: (range: string) => void
  setSourceFilter: (source: string) => void
  applyFilters: () => void
  
  // Alert actions
  fetchAlerts: () => Promise<void>
  markAlertAsRead: (alertId: string) => Promise<void>
  markAllAlertsAsRead: () => Promise<void>
  
  // WebSocket actions
  addLog: (log: LogEntry) => void
  addAlert: (alert: Alert) => void
  updateStats: (stats: { logsPerSecond: number; errorRate: number }) => void
  setConnected: (connected: boolean) => void
  setConnectionError: (error: string | null) => void
  incrementReconnectAttempts: () => void
  resetReconnectAttempts: () => void
}

export const useLiveLogsStore = create<LiveLogsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        connections: [],
        activeConnection: null,
        isLoading: false,
        error: null,
        logs: [],
        filteredLogs: [],
        isStreaming: false,
        isPaused: false,
        autoScroll: true,
        logLevels: [],
        timeRange: '',
        sourceFilter: '',
        logsPerSecond: 0,
        errorRate: 0,
        alerts: [],
        unreadAlerts: [],
        reconnectAttempts: 0,

        // Helper function to get token
        getToken: () => {
          // Try auth store first (most reliable)
          const { token } = useAuthStore.getState()
          if (token) return token
          
          // Fallback to localStorage
          const localToken = localStorage.getItem('access_token')
          if (localToken) return localToken
          
          return null
        },

        // Actions
        fetchConnections: async () => {
          set({ isLoading: true, error: null })
          try {
            const token = get().getToken()
            
            if (!token) {
              throw new Error('No authentication token found. Please log in again.')
            }

            const response = await fetch('http://localhost:8000/api/v1/live-logs/connections', {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            })

            if (response.status === 401) {
              // Token expired or invalid - redirect to login
              localStorage.removeItem('access_token')
              useAuthStore.getState().logout()
              window.location.href = '/login'
              throw new Error('Session expired. Please log in again.')
            }

            if (!response.ok) {
              const errorData = await response.json().catch(() => ({}))
              throw new Error(errorData.detail || 'Failed to fetch connections')
            }

            const data = await response.json()
            set({ connections: data, isLoading: false })
          } catch (error) {
            set({ error: (error as Error).message, isLoading: false })
          }
        },

        createConnection: async (name: string, platform: string, projectId?: string) => {
          set({ isLoading: true, error: null })
          try {
            const token = get().getToken()
            
            if (!token) {
              throw new Error('No authentication token found. Please log in again.')
            }

            const response = await fetch('http://localhost:8000/api/v1/live-logs/connections', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ name, platform, project_id: projectId }),
            })

            if (response.status === 401) {
              // Token expired or invalid - redirect to login
              localStorage.removeItem('access_token')
              useAuthStore.getState().logout()
              window.location.href = '/login'
              throw new Error('Session expired. Please log in again.')
            }

            if (!response.ok) {
              const errorData = await response.json().catch(() => ({}))
              throw new Error(errorData.detail || 'Failed to create connection')
            }

            const data = await response.json()
            
            // Refresh connections list
            await get().fetchConnections()
            
            set({ isLoading: false })
            return data
          } catch (error) {
            set({ error: (error as Error).message, isLoading: false })
            throw error
          }
        },

        deleteConnection: async (id: string) => {
          set({ isLoading: true, error: null })
          try {
            const token = get().getToken()
            
            if (!token) {
              throw new Error('No authentication token found. Please log in again.')
            }

            const response = await fetch(`http://localhost:8000/api/v1/live-logs/connections/${id}`, {
              method: 'DELETE',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            })

            if (response.status === 401) {
              // Token expired or invalid - redirect to login
              localStorage.removeItem('access_token')
              useAuthStore.getState().logout()
              window.location.href = '/login'
              throw new Error('Session expired. Please log in again.')
            }

            if (!response.ok) {
              const errorData = await response.json().catch(() => ({}))
              throw new Error(errorData.detail || 'Failed to delete connection')
            }

            // Refresh connections list
            await get().fetchConnections()
            
            set({ isLoading: false })
          } catch (error) {
            set({ error: (error as Error).message, isLoading: false })
            throw error
          }
        },

        testConnection: async (tenantId: string, apiKey: string) => {
          try {
            const response = await fetch('http://localhost:8000/api/v1/live-logs/ingest/test', {
              headers: {
                'Authorization': `Bearer ${apiKey}`,
                'X-Tenant-ID': tenantId,
              },
            })

            return response.ok
          } catch (error) {
            return false
          }
        },

        setActiveConnection: (id: string | null) => {
          set({ activeConnection: id })
        },

        // Streaming actions
        setStreaming: (streaming: boolean) => {
          set({ isStreaming: streaming })
        },

        setPaused: (paused: boolean) => {
          set({ isPaused: paused })
        },

        setAutoScroll: (autoScroll: boolean) => {
          set({ autoScroll })
        },

        clearLogs: () => {
          set({ logs: [], filteredLogs: [] })
        },

        // Filter actions
        setLogLevels: (levels: string[]) => {
          set({ logLevels: levels })
        },

        setTimeRange: (range: string) => {
          set({ timeRange: range })
        },

        setSourceFilter: (source: string) => {
          set({ sourceFilter: source })
        },

        applyFilters: () => {
          const { logs, logLevels, timeRange, sourceFilter } = get()
          
          let filtered = logs
          
          // Filter by log levels
          if (logLevels.length > 0) {
            filtered = filtered.filter(log => logLevels.includes(log.level))
          }
          
          // Filter by source
          if (sourceFilter) {
            filtered = filtered.filter(log => 
              log.source?.toLowerCase().includes(sourceFilter.toLowerCase())
            )
          }
          
          // Filter by time range
          const now = new Date()
          const timeRanges = {
            'last_hour': 60 * 60 * 1000,
            'last_24h': 24 * 60 * 60 * 1000,
            'last_7d': 7 * 24 * 60 * 60 * 1000,
            'last_30d': 30 * 24 * 60 * 60 * 1000
          }
          
          if (timeRange in timeRanges) {
            const cutoff = new Date(now.getTime() - timeRanges[timeRange as keyof typeof timeRanges])
            filtered = filtered.filter(log => new Date(log.timestamp) >= cutoff)
          }
          
          set({ filteredLogs: filtered })
        },

        // Alert actions
        fetchAlerts: async () => {
          try {
            const token = get().getToken()
            
            if (!token) {
              return // Silently fail if no token
            }

            const response = await fetch('http://localhost:8000/api/v1/live-logs/alerts', {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            })

            if (response.status === 401) {
              // Token expired - clear and logout
              localStorage.removeItem('access_token')
              useAuthStore.getState().logout()
              return
            }

            if (response.ok) {
              const alerts = await response.json()
              const unreadAlerts = alerts.filter((alert: Alert) => !alert.is_read)
              set({ alerts, unreadAlerts })
            }
          } catch (error) {
            console.error('Failed to fetch alerts:', error)
          }
        },

        markAlertAsRead: async (alertId: string) => {
          try {
            const token = get().getToken()
            
            if (!token) {
              return // Silently fail if no token
            }

            const response = await fetch(`http://localhost:8000/api/v1/live-logs/alerts/${alertId}/read`, {
              method: 'PATCH',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            })

            if (response.status === 401) {
              // Token expired - clear and logout
              localStorage.removeItem('access_token')
              useAuthStore.getState().logout()
              return
            }

            if (response.ok) {
              // Update local state
              const { alerts } = get()
              const updatedAlerts = alerts.map(alert => 
                alert.id === alertId ? { ...alert, is_read: true } : alert
              )
              const unreadAlerts = updatedAlerts.filter(alert => !alert.is_read)
              set({ alerts: updatedAlerts, unreadAlerts })
            }
          } catch (error) {
            console.error('Failed to mark alert as read:', error)
          }
        },

        markAllAlertsAsRead: async () => {
          try {
            const token = get().getToken()
            
            if (!token) {
              return // Silently fail if no token
            }

            const response = await fetch('http://localhost:8000/api/v1/live-logs/alerts/mark-all-read', {
              method: 'PATCH',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            })

            if (response.status === 401) {
              // Token expired - clear and logout
              localStorage.removeItem('access_token')
              useAuthStore.getState().logout()
              return
            }

            if (response.ok) {
              // Update local state
              const { alerts } = get()
              const updatedAlerts = alerts.map(alert => ({ ...alert, is_read: true }))
              set({ alerts: updatedAlerts, unreadAlerts: [] })
            }
          } catch (error) {
            console.error('Failed to mark all alerts as read:', error)
          }
        },

        // WebSocket actions
        addLog: (log: LogEntry) => {
          const { logs } = get()
          const newLogs = [log, ...logs].slice(0, 1000) // Keep only last 1000 logs
          set({ logs: newLogs })
        },

        addAlert: (alert: Alert) => {
          const { alerts, unreadAlerts } = get()
          const newAlerts = [alert, ...alerts]
          const newUnreadAlerts = [alert, ...unreadAlerts]
          set({ alerts: newAlerts, unreadAlerts: newUnreadAlerts })
        },

        updateStats: (stats: { logsPerSecond: number; errorRate: number }) => {
          set({ logsPerSecond: stats.logsPerSecond, errorRate: stats.errorRate })
        },

        setConnected: (connected: boolean) => {
          set({ isStreaming: connected })
        },

        setConnectionError: (error: string | null) => {
          set({ error })
        },

        incrementReconnectAttempts: () => {
          const { reconnectAttempts } = get()
          set({ reconnectAttempts: reconnectAttempts + 1 })
        },

        resetReconnectAttempts: () => {
          set({ reconnectAttempts: 0 })
        },
      }),
      {
        name: 'live-logs-store',
        partialize: (state) => ({
          connections: state.connections,
        })
      }
    ),
    {
      name: 'live-logs-store'
    }
  )
)

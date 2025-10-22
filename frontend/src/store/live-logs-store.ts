import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

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
  activeConnection: LiveLogConnection | null
  selectedConnectionId: string | null
  
  // Logs
  logs: LogEntry[]
  filteredLogs: LogEntry[]
  logBuffer: LogEntry[]
  isStreaming: boolean
  isPaused: boolean
  autoScroll: boolean
  
  // Filters
  logLevels: string[]
  searchQuery: string
  timeRange: string
  sourceFilter: string
  
  // View
  viewMode: 'grid' | 'list'
  showChat: boolean
  showAlerts: boolean
  
  // WebSocket
  isConnected: boolean
  connectionError: string | null
  reconnectAttempts: number
  
  // Alerts
  alerts: Alert[]
  unreadAlerts: number
  
  // Stats
  totalLogsToday: number
  logsPerSecond: number
  errorRate: number
  topErrors: Array<{ message: string; count: number }>
  
  // Actions
  setConnections: (connections: LiveLogConnection[]) => void
  setActiveConnection: (connection: LiveLogConnection | null) => void
  addConnection: (connection: LiveLogConnection) => void
  updateConnection: (id: string, updates: Partial<LiveLogConnection>) => void
  deleteConnection: (id: string) => void
  
  addLog: (log: LogEntry) => void
  addLogs: (logs: LogEntry[]) => void
  clearLogs: () => void
  setStreaming: (streaming: boolean) => void
  setPaused: (paused: boolean) => void
  setAutoScroll: (autoScroll: boolean) => void
  
  setLogLevels: (levels: string[]) => void
  setSearchQuery: (query: string) => void
  setTimeRange: (range: string) => void
  setSourceFilter: (source: string) => void
  applyFilters: () => void
  
  setViewMode: (mode: 'grid' | 'list') => void
  setShowChat: (show: boolean) => void
  setShowAlerts: (show: boolean) => void
  
  setConnected: (connected: boolean) => void
  setConnectionError: (error: string | null) => void
  incrementReconnectAttempts: () => void
  resetReconnectAttempts: () => void
  
  addAlert: (alert: Alert) => void
  markAlertAsRead: (alertId: string) => void
  markAllAlertsAsRead: () => void
  setAlerts: (alerts: Alert[]) => void
  
  updateStats: (stats: {
    totalLogsToday: number
    logsPerSecond: number
    errorRate: number
    topErrors: Array<{ message: string; count: number }>
  }) => void
  
  refreshConnections: () => Promise<void>
  startStreaming: (connectionId: string) => Promise<void>
  stopStreaming: (connectionId: string) => Promise<void>
}

export const useLiveLogsStore = create<LiveLogsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        connections: [],
        activeConnection: null,
        selectedConnectionId: null,
        
        logs: [],
        filteredLogs: [],
        logBuffer: [],
        isStreaming: false,
        isPaused: false,
        autoScroll: true,
        
        logLevels: ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
        searchQuery: '',
        timeRange: 'last_5m',
        sourceFilter: '',
        
        viewMode: 'grid',
        showChat: false,
        showAlerts: false,
        
        isConnected: false,
        connectionError: null,
        reconnectAttempts: 0,
        
        alerts: [],
        unreadAlerts: 0,
        
        totalLogsToday: 0,
        logsPerSecond: 0,
        errorRate: 0,
        topErrors: [],
        
        // Actions
        setConnections: (connections) => set({ connections }),
        setActiveConnection: (connection) => set({ 
          activeConnection: connection,
          selectedConnectionId: connection?.id || null
        }),
        addConnection: (connection) => set((state) => ({
          connections: [...state.connections, connection]
        })),
        updateConnection: (id, updates) => set((state) => ({
          connections: state.connections.map(conn => 
            conn.id === id ? { ...conn, ...updates } : conn
          ),
          activeConnection: state.activeConnection?.id === id 
            ? { ...state.activeConnection, ...updates }
            : state.activeConnection
        })),
        deleteConnection: (id) => set((state) => ({
          connections: state.connections.filter(conn => conn.id !== id),
          activeConnection: state.activeConnection?.id === id ? null : state.activeConnection
        })),
        
        addLog: (log) => set((state) => {
          const newLogs = [log, ...state.logs].slice(0, 10000) // Keep last 10k logs
          return {
            logs: newLogs,
            logBuffer: state.isPaused ? [...state.logBuffer, log] : state.logBuffer
          }
        }),
        addLogs: (logs) => set((state) => {
          const newLogs = [...logs, ...state.logs].slice(0, 10000)
          return {
            logs: newLogs,
            logBuffer: state.isPaused ? [...state.logBuffer, ...logs] : state.logBuffer
          }
        }),
        clearLogs: () => set({ logs: [], filteredLogs: [], logBuffer: [] }),
        setStreaming: (streaming) => set({ isStreaming: streaming }),
        setPaused: (paused) => set((state) => ({
          isPaused: paused,
          logs: paused ? state.logs : [...state.logs, ...state.logBuffer],
          logBuffer: paused ? state.logBuffer : []
        })),
        setAutoScroll: (autoScroll) => set({ autoScroll }),
        
        setLogLevels: (levels) => set({ logLevels: levels }),
        setSearchQuery: (query) => set({ searchQuery: query }),
        setTimeRange: (range) => set({ timeRange: range }),
        setSourceFilter: (source) => set({ sourceFilter: source }),
        applyFilters: () => {
          const state = get()
          let filtered = state.logs
          
          // Filter by log levels
          if (state.logLevels.length > 0) {
            filtered = filtered.filter(log => state.logLevels.includes(log.level))
          }
          
          // Filter by search query
          if (state.searchQuery) {
            const query = state.searchQuery.toLowerCase()
            filtered = filtered.filter(log => 
              log.message.toLowerCase().includes(query) ||
              log.source?.toLowerCase().includes(query) ||
              log.service?.toLowerCase().includes(query)
            )
          }
          
          // Filter by source
          if (state.sourceFilter) {
            filtered = filtered.filter(log => log.source === state.sourceFilter)
          }
          
          // Filter by time range
          if (state.timeRange !== 'all') {
            const now = new Date()
            let cutoff: Date
            
            switch (state.timeRange) {
              case 'last_5m':
                cutoff = new Date(now.getTime() - 5 * 60 * 1000)
                break
              case 'last_15m':
                cutoff = new Date(now.getTime() - 15 * 60 * 1000)
                break
              case 'last_1h':
                cutoff = new Date(now.getTime() - 60 * 60 * 1000)
                break
              case 'last_6h':
                cutoff = new Date(now.getTime() - 6 * 60 * 60 * 1000)
                break
              case 'last_24h':
                cutoff = new Date(now.getTime() - 24 * 60 * 60 * 1000)
                break
              default:
                cutoff = new Date(0)
            }
            
            filtered = filtered.filter(log => new Date(log.timestamp) >= cutoff)
          }
          
          set({ filteredLogs: filtered })
        },
        
        setViewMode: (mode) => set({ viewMode: mode }),
        setShowChat: (show) => set({ showChat: show }),
        setShowAlerts: (show) => set({ showAlerts: show }),
        
        setConnected: (connected) => set({ isConnected: connected }),
        setConnectionError: (error) => set({ connectionError: error }),
        incrementReconnectAttempts: () => set((state) => ({
          reconnectAttempts: state.reconnectAttempts + 1
        })),
        resetReconnectAttempts: () => set({ reconnectAttempts: 0 }),
        
        addAlert: (alert) => set((state) => ({
          alerts: [alert, ...state.alerts].slice(0, 1000), // Keep last 1k alerts
          unreadAlerts: state.unreadAlerts + 1
        })),
        markAlertAsRead: (alertId) => set((state) => ({
          alerts: state.alerts.map(alert => 
            alert.id === alertId ? { ...alert, is_read: true } : alert
          ),
          unreadAlerts: Math.max(0, state.unreadAlerts - 1)
        })),
        markAllAlertsAsRead: () => set((state) => ({
          alerts: state.alerts.map(alert => ({ ...alert, is_read: true })),
          unreadAlerts: 0
        })),
        setAlerts: (alerts) => set((state) => ({
          alerts,
          unreadAlerts: alerts.filter(alert => !alert.is_read).length
        })),
        
        updateStats: (stats) => set(stats),
        
        refreshConnections: async () => {
          try {
            // This will be implemented with actual API calls
            // For now, just simulate loading
            await new Promise(resolve => setTimeout(resolve, 1000))
          } catch (error) {
            console.error('Failed to refresh connections:', error)
          }
        },
        
        startStreaming: async (connectionId) => {
          try {
            set({ isStreaming: true, isPaused: false })
            // WebSocket connection logic will be implemented here
          } catch (error) {
            console.error('Failed to start streaming:', error)
            set({ isStreaming: false })
          }
        },
        
        stopStreaming: async (connectionId) => {
          try {
            set({ isStreaming: false })
            // WebSocket disconnection logic will be implemented here
          } catch (error) {
            console.error('Failed to stop streaming:', error)
          }
        }
      }),
      {
        name: 'live-logs-store',
        partialize: (state) => ({
          viewMode: state.viewMode,
          logLevels: state.logLevels,
          timeRange: state.timeRange,
          autoScroll: state.autoScroll
        })
      }
    ),
    {
      name: 'live-logs-store'
    }
  )
)

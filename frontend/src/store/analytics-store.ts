import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export interface DateRange {
  from: Date
  to: Date
  preset?: 'last_hour' | 'last_24h' | 'last_7d' | 'last_30d' | 'custom'
}

export interface LogLevel {
  DEBUG: boolean
  INFO: boolean
  WARN: boolean
  ERROR: boolean
  CRITICAL: boolean
}

export interface AnalyticsState {
  // Data
  overviewData: any | null
  errorData: any | null
  performanceData: any | null
  anomalyData: any | null
  insightsData: any | null
  
  // UI State
  isLoading: boolean
  error: string | null
  lastUpdated: number | null
  
  // Filters
  selectedProject: string | null
  dateRange: DateRange
  logLevels: LogLevel
  
  // Settings
  autoRefresh: boolean
  refreshInterval: number
  
  // Actions
  setOverviewData: (data: any) => void
  setErrorData: (data: any) => void
  setPerformanceData: (data: any) => void
  setAnomalyData: (data: any) => void
  setInsightsData: (data: any) => void
  
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setLastUpdated: (timestamp: number) => void
  
  setSelectedProject: (projectId: string | null) => void
  setDateRange: (range: DateRange) => void
  setLogLevels: (levels: LogLevel) => void
  
  toggleAutoRefresh: () => void
  setRefreshInterval: (interval: number) => void
  
  refreshData: () => Promise<void>
  clearData: () => void
}

const defaultDateRange: DateRange = {
  from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
  to: new Date(),
  preset: 'last_7d'
}

const defaultLogLevels: LogLevel = {
  DEBUG: true,
  INFO: true,
  WARN: true,
  ERROR: true,
  CRITICAL: true
}

export const useAnalyticsStore = create<AnalyticsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        overviewData: null,
        errorData: null,
        performanceData: null,
        anomalyData: null,
        insightsData: null,
        
        isLoading: false,
        error: null,
        lastUpdated: null,
        
        selectedProject: null,
        dateRange: defaultDateRange,
        logLevels: defaultLogLevels,
        
        autoRefresh: false,
        refreshInterval: 30000, // 30 seconds
        
        // Actions
        setOverviewData: (data) => set({ overviewData: data }),
        setErrorData: (data) => set({ errorData: data }),
        setPerformanceData: (data) => set({ performanceData: data }),
        setAnomalyData: (data) => set({ anomalyData: data }),
        setInsightsData: (data) => set({ insightsData: data }),
        
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setLastUpdated: (timestamp) => set({ lastUpdated: timestamp }),
        
        setSelectedProject: (projectId) => set({ selectedProject: projectId }),
        setDateRange: (range) => set({ dateRange: range }),
        setLogLevels: (levels) => set({ logLevels: levels }),
        
        toggleAutoRefresh: () => set((state) => ({ autoRefresh: !state.autoRefresh })),
        setRefreshInterval: (interval) => set({ refreshInterval: interval }),
        
        refreshData: async () => {
          const state = get()
          set({ isLoading: true, error: null })
          
          try {
            // Import analytics service dynamically to avoid circular imports
            const { analyticsService } = await import('@/services/analytics-service')
            
            if (!state.selectedProject) {
              throw new Error('No project selected')
            }

            // Fetch all analytics data in parallel
            const [overviewData, errorData, performanceData, anomalyData, insightsData] = await Promise.all([
              analyticsService.getAnalyticsOverview(
                state.selectedProject,
                state.dateRange.from.toISOString(),
                state.dateRange.to.toISOString(),
                Object.keys(state.logLevels).filter(level => state.logLevels[level as keyof LogLevel])
              ),
              analyticsService.getErrorAnalysis(
                state.selectedProject,
                state.dateRange.from.toISOString(),
                state.dateRange.to.toISOString()
              ),
              analyticsService.getPerformanceAnalysis(
                state.selectedProject,
                state.dateRange.from.toISOString(),
                state.dateRange.to.toISOString()
              ),
              analyticsService.detectAnomalies(0, 0.8), // Using legacy method for now
              analyticsService.getAIInsights(
                state.selectedProject,
                state.dateRange.from.toISOString(),
                state.dateRange.to.toISOString()
              )
            ])
            
            set({ 
              overviewData,
              errorData,
              performanceData,
              anomalyData,
              insightsData,
              isLoading: false, 
              lastUpdated: Date.now(),
              error: null 
            })
          } catch (error) {
            set({ 
              isLoading: false, 
              error: error instanceof Error ? error.message : 'Unknown error' 
            })
          }
        },
        
        clearData: () => set({
          overviewData: null,
          errorData: null,
          performanceData: null,
          anomalyData: null,
          insightsData: null,
          error: null
        })
      }),
      {
        name: 'analytics-store',
        partialize: (state) => ({
          selectedProject: state.selectedProject,
          dateRange: state.dateRange,
          logLevels: state.logLevels,
          autoRefresh: state.autoRefresh,
          refreshInterval: state.refreshInterval
        })
      }
    ),
    {
      name: 'analytics-store'
    }
  )
)

// Auto-refresh functionality
let refreshInterval: NodeJS.Timeout | null = null

export const startAutoRefresh = () => {
  const state = useAnalyticsStore.getState()
  if (state.autoRefresh && !refreshInterval) {
    refreshInterval = setInterval(() => {
      state.refreshData()
    }, state.refreshInterval)
  }
}

export const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Subscribe to auto-refresh changes
useAnalyticsStore.subscribe(
  (state) => state.autoRefresh,
  (autoRefresh) => {
    if (autoRefresh) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  }
)

// Subscribe to refresh interval changes
useAnalyticsStore.subscribe(
  (state) => state.refreshInterval,
  (interval) => {
    if (useAnalyticsStore.getState().autoRefresh) {
      stopAutoRefresh()
      startAutoRefresh()
    }
  }
)

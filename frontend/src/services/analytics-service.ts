import { api } from '@/lib/api'
import { Analysis, PaginatedResponse } from '@/types'

export const analyticsService = {
  // Legacy methods
  async createAnalysis(analysisData: {
    name: string
    description?: string
    analysis_type: string
    log_file_id?: number
    results: any
  }): Promise<Analysis> {
    const response = await api.post('/analytics', analysisData)
    return response.data
  },

  async getAnalyses(
    page: number = 1,
    size: number = 20,
    analysisType?: string
  ): Promise<PaginatedResponse<Analysis>> {
    const response = await api.get('/analytics', {
      params: {
        skip: (page - 1) * size,
        limit: size,
        analysis_type: analysisType
      }
    })
    return response.data
  },

  async getAnalysis(id: number): Promise<Analysis> {
    const response = await api.get(`/analytics/${id}`)
    return response.data
  },

  async analyzePatterns(logFileId: number, patternType: string = 'error'): Promise<any> {
    const response = await api.post('/analytics/patterns', {
      log_file_id: logFileId,
      pattern_type: patternType
    })
    return response.data
  },

  async detectAnomalies(logFileId: number, threshold: number = 0.8): Promise<any> {
    const response = await api.post('/analytics/anomalies', {
      log_file_id: logFileId,
      threshold
    })
    return response.data
  },

  async getOverviewStats(logFileId?: number, days: number = 7): Promise<any> {
    const response = await api.get('/analytics/stats/overview', {
      params: {
        log_file_id: logFileId,
        days
      }
    })
    return response.data
  },

  // New Dashboard Analytics Methods
  async getAnalyticsOverview(
    projectId: string,
    startDate?: string,
    endDate?: string,
    logLevels?: string[],
    forceRefresh: boolean = false
  ): Promise<any> {
    const params: any = {
      force_refresh: forceRefresh
    }
    
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    if (logLevels) params.log_levels = logLevels.join(',')

    const response = await api.get(`/analytics/overview/${projectId}`, { params })
    return response.data
  },

  async getLogTimeline(
    projectId: string,
    startDate?: string,
    endDate?: string,
    granularity: 'hour' | 'day' = 'hour',
    logLevels?: string[]
  ): Promise<any> {
    const params: any = {
      granularity
    }
    
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    if (logLevels) params.log_levels = logLevels.join(',')

    const response = await api.get(`/analytics/timeline/${projectId}`, { params })
    return response.data
  },

  async getErrorAnalysis(
    projectId: string,
    startDate?: string,
    endDate?: string,
    limit: number = 10
  ): Promise<any> {
    const params: any = { limit }
    
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await api.get(`/analytics/errors/${projectId}`, { params })
    return response.data
  },

  async getPerformanceAnalysis(
    projectId: string,
    startDate?: string,
    endDate?: string
  ): Promise<any> {
    const params: any = {}
    
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await api.get(`/analytics/performance/${projectId}`, { params })
    return response.data
  },

  async getAIInsights(
    projectId: string,
    startDate?: string,
    endDate?: string
  ): Promise<any> {
    const params: any = {}
    
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await api.get(`/analytics/insights/${projectId}`, { params })
    return response.data
  },

  async exportAnalyticsData(
    projectId: string,
    format: 'pdf' | 'csv' | 'json' | 'png',
    startDate?: string,
    endDate?: string
  ): Promise<any> {
    const params: any = { format }
    
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await api.post(`/analytics/export/${projectId}`, null, { params })
    return response.data
  }
}

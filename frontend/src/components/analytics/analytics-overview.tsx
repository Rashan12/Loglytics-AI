'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { BarChart3, TrendingUp, AlertTriangle, Activity } from 'lucide-react'
import { analyticsService } from '@/services/analytics-service'
import { formatDate } from '@/lib/utils'

interface OverviewStats {
  total_entries: number
  error_entries: number
  warning_entries: number
  recent_entries: number
  error_rate: number
  top_error_sources: Array<{ source: string; count: number }>
  analysis_period_days: number
  analysis_timestamp: string
}

export function AnalyticsOverview() {
  const [stats, setStats] = useState<OverviewStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadOverviewStats()
  }, [])

  const loadOverviewStats = async () => {
    try {
      const data = await analyticsService.getOverviewStats(undefined, 7)
      setStats(data)
    } catch (error) {
      console.error('Failed to load overview stats:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-muted animate-pulse rounded" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-muted animate-pulse rounded" />
          ))}
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">No data available</h3>
        <p className="text-muted-foreground">
          Upload some log files to see analytics
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Analytics Overview</h2>
        <p className="text-muted-foreground">
          Insights from your log data over the last {stats.analysis_period_days} days
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Entries</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_entries.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +{stats.recent_entries} in last 24h
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(stats.error_rate * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.error_entries} errors out of {stats.total_entries} entries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Warnings</CardTitle>
            <TrendingUp className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.warning_entries.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Warning level entries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.recent_entries.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Entries in last 24 hours
            </p>
          </CardContent>
        </Card>
      </div>

      {stats.top_error_sources.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top Error Sources</CardTitle>
            <CardDescription>
              Sources generating the most errors
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.top_error_sources.map((source, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline">{source.source || 'Unknown'}</Badge>
                  </div>
                  <div className="text-sm font-medium">{source.count} errors</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex justify-between items-center">
        <div className="text-sm text-muted-foreground">
          Last updated: {formatDate(stats.analysis_timestamp)}
        </div>
        <Button onClick={loadOverviewStats}>
          Refresh Data
        </Button>
      </div>
    </div>
  )
}

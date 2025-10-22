"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

// Chart Components
import { LogTimeline } from "./LogTimeline"
import { LogLevelPie } from "./LogLevelPie"
import { TopErrorsBar } from "./TopErrorsBar"
import { ErrorTrends } from "./ErrorTrends"
import { PerformanceChart } from "./PerformanceChart"
import { AnomalyScatter } from "./AnomalyScatter"
import { ServiceBreakdown } from "./ServiceBreakdown"

// Stats Components
import { StatsCard } from "./StatsCard"

// Store
import { useAnalyticsStore } from "@/store/analytics-store"

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function AnalyticsDashboard() {
  const { 
    overviewData, 
    isLoading, 
    error,
    selectedProject,
    dateRange,
    logLevels
  } = useAnalyticsStore()

  // Mock data for demonstration - will be replaced with real API data
  const mockStats = {
    totalLogs: 2478321,
    totalErrors: 1847,
    errorRate: 0.74,
    mtbf: 12.5
  }

  const mockTimelineData = [
    { time: "2024-01-01 00:00", DEBUG: 120, INFO: 450, WARN: 23, ERROR: 8, CRITICAL: 1 },
    { time: "2024-01-01 01:00", DEBUG: 98, INFO: 380, WARN: 31, ERROR: 12, CRITICAL: 2 },
    { time: "2024-01-01 02:00", DEBUG: 87, INFO: 320, WARN: 19, ERROR: 15, CRITICAL: 3 },
    { time: "2024-01-01 03:00", DEBUG: 76, INFO: 290, WARN: 25, ERROR: 9, CRITICAL: 1 },
    { time: "2024-01-01 04:00", DEBUG: 65, INFO: 250, WARN: 17, ERROR: 6, CRITICAL: 0 },
    { time: "2024-01-01 05:00", DEBUG: 89, INFO: 340, WARN: 28, ERROR: 11, CRITICAL: 2 },
    { time: "2024-01-01 06:00", DEBUG: 112, INFO: 420, WARN: 35, ERROR: 14, CRITICAL: 1 },
    { time: "2024-01-01 07:00", DEBUG: 145, INFO: 580, WARN: 42, ERROR: 18, CRITICAL: 3 },
    { time: "2024-01-01 08:00", DEBUG: 178, INFO: 720, WARN: 55, ERROR: 22, CRITICAL: 4 },
    { time: "2024-01-01 09:00", DEBUG: 201, INFO: 890, WARN: 68, ERROR: 28, CRITICAL: 5 },
    { time: "2024-01-01 10:00", DEBUG: 234, INFO: 1050, WARN: 72, ERROR: 31, CRITICAL: 6 },
    { time: "2024-01-01 11:00", DEBUG: 267, INFO: 1180, WARN: 78, ERROR: 35, CRITICAL: 7 },
    { time: "2024-01-01 12:00", DEBUG: 289, INFO: 1320, WARN: 85, ERROR: 38, CRITICAL: 8 },
    { time: "2024-01-01 13:00", DEBUG: 312, INFO: 1450, WARN: 92, ERROR: 42, CRITICAL: 9 },
    { time: "2024-01-01 14:00", DEBUG: 298, INFO: 1380, WARN: 88, ERROR: 39, CRITICAL: 7 },
    { time: "2024-01-01 15:00", DEBUG: 275, INFO: 1250, WARN: 82, ERROR: 36, CRITICAL: 6 },
    { time: "2024-01-01 16:00", DEBUG: 256, INFO: 1120, WARN: 75, ERROR: 33, CRITICAL: 5 },
    { time: "2024-01-01 17:00", DEBUG: 234, INFO: 980, WARN: 68, ERROR: 29, CRITICAL: 4 },
    { time: "2024-01-01 18:00", DEBUG: 198, INFO: 820, WARN: 58, ERROR: 24, CRITICAL: 3 },
    { time: "2024-01-01 19:00", DEBUG: 167, INFO: 680, WARN: 48, ERROR: 19, CRITICAL: 2 },
    { time: "2024-01-01 20:00", DEBUG: 145, INFO: 580, WARN: 38, ERROR: 15, CRITICAL: 1 },
    { time: "2024-01-01 21:00", DEBUG: 123, INFO: 480, WARN: 32, ERROR: 12, CRITICAL: 1 },
    { time: "2024-01-01 22:00", DEBUG: 98, INFO: 380, WARN: 28, ERROR: 9, CRITICAL: 0 },
    { time: "2024-01-01 23:00", DEBUG: 87, INFO: 320, WARN: 25, ERROR: 7, CRITICAL: 1 }
  ]

  const mockLogLevelData = [
    { name: "DEBUG", value: 15420, color: "#10b981" },
    { name: "INFO", value: 8920, color: "#3b82f6" },
    { name: "WARN", value: 1230, color: "#f59e0b" },
    { name: "ERROR", value: 456, color: "#ef4444" },
    { name: "CRITICAL", value: 89, color: "#7c2d12" }
  ]

  const mockTopErrors = [
    { message: "Connection timeout to database", count: 234 },
    { message: "Authentication failed for user", count: 189 },
    { message: "Memory allocation failed", count: 156 },
    { message: "File not found: config.json", count: 134 },
    { message: "Network unreachable", count: 112 },
    { message: "Permission denied", count: 98 },
    { message: "Invalid JSON format", count: 87 },
    { message: "SSL certificate expired", count: 76 },
    { message: "Queue overflow", count: 65 },
    { message: "Rate limit exceeded", count: 54 }
  ]

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-destructive mb-2">Error Loading Data</h3>
            <p className="text-muted-foreground">{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Quick Stats Row */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Logs Analyzed"
          value={mockStats.totalLogs.toLocaleString()}
          change="+12%"
          changeType="positive"
          icon="Database"
          isLoading={isLoading}
        />
        <StatsCard
          title="Total Errors"
          value={mockStats.totalErrors.toLocaleString()}
          change="-8%"
          changeType="positive"
          icon="AlertTriangle"
          isLoading={isLoading}
        />
        <StatsCard
          title="Error Rate"
          value={`${mockStats.errorRate}%`}
          change="-0.3%"
          changeType="positive"
          icon="TrendingDown"
          isLoading={isLoading}
        />
        <StatsCard
          title="MTBF (Hours)"
          value={mockStats.mtbf.toString()}
          change="+2.1h"
          changeType="positive"
          icon="Clock"
          isLoading={isLoading}
        />
      </motion.div>

      {/* Charts Grid */}
      <motion.div variants={itemVariants} className="grid gap-6">
        {/* Row 1: Log Timeline + Log Level Distribution */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Log Timeline</CardTitle>
              <CardDescription>
                Log volume over time by severity level
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <LogTimeline data={mockTimelineData} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Log Level Distribution</CardTitle>
              <CardDescription>
                Breakdown of logs by severity level
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <LogLevelPie data={mockLogLevelData} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Row 2: Top Errors + Error Trends */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Top Errors</CardTitle>
              <CardDescription>
                Most frequent error messages
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <TopErrorsBar data={mockTopErrors} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Error Frequency Trends</CardTitle>
              <CardDescription>
                Error count over time with anomaly detection
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <ErrorTrends data={mockTimelineData} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Row 3: Performance Metrics + Anomaly Scores */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
              <CardDescription>
                Response times and throughput metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <PerformanceChart data={mockTimelineData} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Anomaly Scores</CardTitle>
              <CardDescription>
                Anomaly detection scores over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <AnomalyScatter data={mockTimelineData} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Row 4: Service/Component Breakdown */}
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Service Breakdown</CardTitle>
              <CardDescription>
                Error distribution by service/component
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-80 w-full" />
              ) : (
                <ServiceBreakdown data={mockTopErrors} />
              )}
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </motion.div>
  )
}

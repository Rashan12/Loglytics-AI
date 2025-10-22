"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  BarChart3, 
  RefreshCw, 
  Download, 
  Calendar,
  Filter,
  Settings,
  AlertTriangle,
  Activity,
  TrendingUp,
  Clock
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Analytics Components
import { AnalyticsDashboard } from "@/components/analytics/AnalyticsDashboard"
import { DateRangePicker } from "@/components/analytics/DateRangePicker"
import { FilterControls } from "@/components/analytics/FilterControls"
import { ExportMenu } from "@/components/analytics/ExportMenu"
import { InsightsPanel } from "@/components/analytics/InsightsPanel"

// Store
import { useAnalyticsStore, startAutoRefresh, stopAutoRefresh } from "@/store/analytics-store"

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

const cardVariants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 }
}

export default function AnalyticsPage() {
  const {
    selectedProject,
    dateRange,
    logLevels,
    isLoading,
    lastUpdated,
    autoRefresh,
    refreshData,
    setDateRange,
    setLogLevels,
    setSelectedProject,
    toggleAutoRefresh
  } = useAnalyticsStore()

  const [activeTab, setActiveTab] = React.useState("overview")

  const handleRefresh = React.useCallback(() => {
    refreshData()
  }, [refreshData])

  const handleExport = React.useCallback((format: string) => {
    // Export functionality will be implemented
    console.log(`Exporting as ${format}`)
  }, [])

  // Initialize auto-refresh on mount
  React.useEffect(() => {
    if (autoRefresh) {
      startAutoRefresh()
    }
    
    return () => {
      stopAutoRefresh()
    }
  }, [autoRefresh])

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="min-h-screen bg-background"
    >
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Page Header */}
        <motion.div
          variants={cardVariants}
          className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0"
        >
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <BarChart3 className="h-8 w-8 text-primary" />
              Log Analytics
            </h1>
            <p className="text-muted-foreground">
              Comprehensive insights and visualizations for your log data
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Last updated: {lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : 'Never'}
            </Badge>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            
            <ExportMenu onExport={handleExport} />
          </div>
        </motion.div>

        {/* Controls Row */}
        <motion.div
          variants={cardVariants}
          className="grid gap-4 md:grid-cols-3"
        >
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Date Range
              </CardTitle>
            </CardHeader>
            <CardContent>
              <DateRangePicker
                value={dateRange}
                onChange={setDateRange}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Filters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FilterControls
                logLevels={logLevels}
                onLogLevelsChange={setLogLevels}
                selectedProject={selectedProject}
                onProjectChange={setSelectedProject}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Auto Refresh</span>
                <Button
                  variant={autoRefresh ? "default" : "outline"}
                  size="sm"
                  onClick={toggleAutoRefresh}
                >
                  {autoRefresh ? "ON" : "OFF"}
                </Button>
              </div>
              
              <Separator />
              
              <div className="text-xs text-muted-foreground">
                <div>Refresh every 30 seconds</div>
                <div>Data cached for 5 minutes</div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Main Analytics Content */}
        <motion.div variants={cardVariants}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="errors" className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Errors
              </TabsTrigger>
              <TabsTrigger value="performance" className="flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Performance
              </TabsTrigger>
              <TabsTrigger value="insights" className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                AI Insights
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <AnalyticsDashboard />
            </TabsContent>

            <TabsContent value="errors" className="space-y-6">
              <div className="text-center py-12">
                <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Error Analysis</h3>
                <p className="text-muted-foreground">
                  Detailed error analysis and trends coming soon
                </p>
              </div>
            </TabsContent>

            <TabsContent value="performance" className="space-y-6">
              <div className="text-center py-12">
                <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Performance Metrics</h3>
                <p className="text-muted-foreground">
                  Performance analysis and monitoring coming soon
                </p>
              </div>
            </TabsContent>

            <TabsContent value="insights" className="space-y-6">
              <InsightsPanel />
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </motion.div>
  )
}

"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Lightbulb,
  ArrowRight,
  RefreshCw,
  ChevronDown,
  ChevronUp
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

interface Insight {
  id: string
  type: "insight" | "recommendation" | "alert"
  title: string
  description: string
  severity: "low" | "medium" | "high"
  confidence: number
  actionable: boolean
  category: string
  timestamp: string
  relatedMetrics?: string[]
}

interface InsightsPanelProps {
  className?: string
}

const mockInsights: Insight[] = [
  {
    id: "1",
    type: "insight",
    title: "Error Rate Spike Detected",
    description: "Errors increased by 35% in the last 24 hours, primarily between 2-4 AM. This pattern suggests a possible cron job or scheduled task issue.",
    severity: "high",
    confidence: 0.87,
    actionable: true,
    category: "Error Analysis",
    timestamp: "2024-01-15T10:30:00Z",
    relatedMetrics: ["Error Rate", "Timeline Analysis"]
  },
  {
    id: "2",
    type: "recommendation",
    title: "Database Connection Pool Optimization",
    description: "Consider increasing the database connection pool size. Current timeout errors suggest insufficient connections during peak hours.",
    severity: "medium",
    confidence: 0.72,
    actionable: true,
    category: "Performance",
    timestamp: "2024-01-15T09:15:00Z",
    relatedMetrics: ["Response Time", "Database Errors"]
  },
  {
    id: "3",
    type: "alert",
    title: "Service X Error Rate Above Threshold",
    description: "Service X has 3x more errors than the average. Root cause likely related to recent deployment at 2024-01-15 08:45:00.",
    severity: "high",
    confidence: 0.91,
    actionable: true,
    category: "Service Health",
    timestamp: "2024-01-15T08:50:00Z",
    relatedMetrics: ["Service Breakdown", "Deployment Timeline"]
  },
  {
    id: "4",
    type: "insight",
    title: "Memory Usage Pattern Identified",
    description: "Memory usage shows a clear pattern with spikes every 6 hours, suggesting a memory leak in scheduled processes.",
    severity: "medium",
    confidence: 0.68,
    actionable: true,
    category: "Resource Usage",
    timestamp: "2024-01-15T07:20:00Z",
    relatedMetrics: ["Memory Usage", "Process Analysis"]
  },
  {
    id: "5",
    type: "recommendation",
    title: "Set Up Automated Alerting",
    description: "Configure alerts for error rate > 10/min and response time > 500ms to catch issues early.",
    severity: "low",
    confidence: 0.85,
    actionable: true,
    category: "Monitoring",
    timestamp: "2024-01-15T06:45:00Z",
    relatedMetrics: ["Error Rate", "Response Time"]
  }
]

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  hover: { scale: 1.02 }
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

export function InsightsPanel({ className }: InsightsPanelProps) {
  const [isLoading, setIsLoading] = React.useState(false)
  const [expandedInsight, setExpandedInsight] = React.useState<string | null>(null)
  const [filter, setFilter] = React.useState<"all" | "insight" | "recommendation" | "alert">("all")

  const handleRefresh = async () => {
    setIsLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsLoading(false)
  }

  const filteredInsights = mockInsights.filter(insight => 
    filter === "all" || insight.type === filter
  )

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high": return "text-red-500 bg-red-50 border-red-200"
      case "medium": return "text-yellow-500 bg-yellow-50 border-yellow-200"
      case "low": return "text-green-500 bg-green-50 border-green-200"
      default: return "text-gray-500 bg-gray-50 border-gray-200"
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "insight": return Brain
      case "recommendation": return Lightbulb
      case "alert": return AlertTriangle
      default: return CheckCircle
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "insight": return "text-blue-500"
      case "recommendation": return "text-purple-500"
      case "alert": return "text-red-500"
      default: return "text-gray-500"
    }
  }

  if (isLoading) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-8 w-20" />
        </div>
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <div className="space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-2/3" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={cn("space-y-6", className)}
    >
      {/* Header */}
      <motion.div variants={cardVariants} className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            AI Insights
          </h2>
          <p className="text-muted-foreground">
            Intelligent analysis and recommendations based on your log data
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          className="flex items-center gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </motion.div>

      {/* Filter Tabs */}
      <motion.div variants={cardVariants} className="flex gap-2">
        {[
          { key: "all", label: "All", count: mockInsights.length },
          { key: "insight", label: "Insights", count: mockInsights.filter(i => i.type === "insight").length },
          { key: "recommendation", label: "Recommendations", count: mockInsights.filter(i => i.type === "recommendation").length },
          { key: "alert", label: "Alerts", count: mockInsights.filter(i => i.type === "alert").length }
        ].map((tab) => (
          <Button
            key={tab.key}
            variant={filter === tab.key ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter(tab.key as any)}
            className="flex items-center gap-2"
          >
            {tab.label}
            <Badge variant="secondary" className="text-xs">
              {tab.count}
            </Badge>
          </Button>
        ))}
      </motion.div>

      {/* Insights List */}
      <div className="space-y-4">
        {filteredInsights.map((insight, index) => {
          const TypeIcon = getTypeIcon(insight.type)
          const isExpanded = expandedInsight === insight.id
          
          return (
            <motion.div
              key={insight.id}
              variants={cardVariants}
              whileHover="hover"
            >
              <Card className="overflow-hidden">
                <CardContent className="p-0">
                  <div
                    className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => setExpandedInsight(isExpanded ? null : insight.id)}
                  >
                    <div className="flex items-start gap-3">
                      <div className={cn("p-2 rounded-lg", getSeverityColor(insight.severity))}>
                        <TypeIcon className={cn("h-4 w-4", getTypeColor(insight.type))} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-sm mb-1">{insight.title}</h3>
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {insight.description}
                            </p>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Badge
                              variant={insight.severity === "high" ? "destructive" : insight.severity === "medium" ? "default" : "secondary"}
                              className="text-xs"
                            >
                              {insight.severity}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {Math.round(insight.confidence * 100)}%
                            </Badge>
                            {isExpanded ? (
                              <ChevronUp className="h-4 w-4 text-muted-foreground" />
                            ) : (
                              <ChevronDown className="h-4 w-4 text-muted-foreground" />
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                          <span>{insight.category}</span>
                          <span>•</span>
                          <span>{new Date(insight.timestamp).toLocaleString()}</span>
                          {insight.actionable && (
                            <>
                              <span>•</span>
                              <span className="text-green-600 font-medium">Actionable</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Expanded Content */}
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="border-t bg-muted/25"
                    >
                      <div className="p-4 space-y-4">
                        <div>
                          <h4 className="font-medium text-sm mb-2">Full Description</h4>
                          <p className="text-sm text-muted-foreground">
                            {insight.description}
                          </p>
                        </div>
                        
                        {insight.relatedMetrics && (
                          <div>
                            <h4 className="font-medium text-sm mb-2">Related Metrics</h4>
                            <div className="flex flex-wrap gap-2">
                              {insight.relatedMetrics.map((metric) => (
                                <Badge key={metric} variant="outline" className="text-xs">
                                  {metric}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {insight.actionable && (
                          <div className="flex gap-2">
                            <Button size="sm" className="flex items-center gap-2">
                              <CheckCircle className="h-3 w-3" />
                              Mark as Resolved
                            </Button>
                            <Button size="sm" variant="outline" className="flex items-center gap-2">
                              <ArrowRight className="h-3 w-3" />
                              View Details
                            </Button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Summary Stats */}
      <motion.div variants={cardVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Insights Summary</CardTitle>
            <CardDescription>
              Overview of AI-generated insights and recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-500">
                  {mockInsights.filter(i => i.type === "insight").length}
                </div>
                <div className="text-sm text-muted-foreground">Insights</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-500">
                  {mockInsights.filter(i => i.type === "recommendation").length}
                </div>
                <div className="text-sm text-muted-foreground">Recommendations</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-500">
                  {mockInsights.filter(i => i.type === "alert").length}
                </div>
                <div className="text-sm text-muted-foreground">Alerts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-500">
                  {mockInsights.filter(i => i.actionable).length}
                </div>
                <div className="text-sm text-muted-foreground">Actionable</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}

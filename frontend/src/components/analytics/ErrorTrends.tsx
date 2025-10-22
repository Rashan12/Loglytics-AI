"use client"

import * as React from "react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Scatter,
  ComposedChart
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ErrorTrendsProps {
  data: Array<{
    time: string
    DEBUG?: number
    INFO?: number
    WARN?: number
    ERROR?: number
    CRITICAL?: number
  }>
  className?: string
}

export function ErrorTrends({ data, className }: ErrorTrendsProps) {
  const [showAnomalies, setShowAnomalies] = React.useState(true)
  const [threshold, setThreshold] = React.useState(20)

  // Calculate error count and anomalies
  const processedData = React.useMemo(() => {
    return data.map(item => {
      const errorCount = (item.ERROR || 0) + (item.CRITICAL || 0)
      const isAnomaly = errorCount > threshold
      
      return {
        ...item,
        errorCount,
        isAnomaly,
        anomalyScore: isAnomaly ? Math.min(errorCount / threshold, 2) : 0
      }
    })
  }, [data, threshold])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <Card className="p-3">
          <CardContent className="p-0">
            <div className="space-y-2">
              <div className="font-medium text-sm">{label}</div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Errors:</span>
                <Badge variant={data.isAnomaly ? "destructive" : "secondary"}>
                  {data.errorCount}
                </Badge>
              </div>
              {data.isAnomaly && (
                <div className="flex items-center justify-between">
                  <span className="text-sm">Anomaly Score:</span>
                  <Badge variant="destructive">
                    {data.anomalyScore.toFixed(2)}
                  </Badge>
                </div>
              )}
              <div className="text-xs text-muted-foreground">
                Threshold: {threshold}
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }
    return null
  }

  const AnomalyDot = (props: any) => {
    const { cx, cy, payload } = props
    if (!payload.isAnomaly) return null
    
    return (
      <circle
        cx={cx}
        cy={cy}
        r={6}
        fill="#ef4444"
        stroke="#dc2626"
        strokeWidth={2}
        className="animate-pulse"
      />
    )
  }

  return (
    <div className={cn("w-full", className)}>
      {/* Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showAnomalies}
              onChange={(e) => setShowAnomalies(e.target.checked)}
              className="rounded"
            />
            Show Anomalies
          </label>
          <div className="flex items-center gap-2 text-sm">
            <label>Threshold:</label>
            <input
              type="range"
              min="5"
              max="50"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-20"
            />
            <span className="text-xs text-muted-foreground">{threshold}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            {processedData.filter(item => item.isAnomaly).length} anomalies
          </Badge>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart
          data={processedData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value)
              return date.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })
            }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Error trend line */}
          <Line
            type="monotone"
            dataKey="errorCount"
            stroke="#ef4444"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, stroke: "#ef4444", strokeWidth: 2 }}
          />
          
          {/* Threshold reference line */}
          <ReferenceLine 
            y={threshold} 
            stroke="#f59e0b" 
            strokeDasharray="5 5"
            label={{ value: "Threshold", position: "topRight" }}
          />
          
          {/* Anomaly markers */}
          {showAnomalies && (
            <Scatter
              dataKey="errorCount"
              fill="#ef4444"
              shape={<AnomalyDot />}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-red-500" />
          Error Count
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-amber-500 border-dashed border-t" />
          Threshold
        </div>
        {showAnomalies && (
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-red-500 rounded-full" />
            Anomalies
          </div>
        )}
      </div>
    </div>
  )
}

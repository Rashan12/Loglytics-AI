"use client"

import * as React from "react"
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface AnomalyScatterProps {
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

export function AnomalyScatter({ data, className }: AnomalyScatterProps) {
  const [threshold, setThreshold] = React.useState(0.7)
  const [selectedPoint, setSelectedPoint] = React.useState<any>(null)

  // Calculate anomaly scores based on log data
  const anomalyData = React.useMemo(() => {
    return data.map((item, index) => {
      const totalLogs = (item.DEBUG || 0) + (item.INFO || 0) + (item.WARN || 0) + (item.ERROR || 0) + (item.CRITICAL || 0)
      const errorCount = (item.ERROR || 0) + (item.CRITICAL || 0)
      
      // Calculate anomaly score based on multiple factors
      const errorRate = totalLogs > 0 ? errorCount / totalLogs : 0
      const volumeAnomaly = totalLogs > 1000 ? 0.3 : 0 // High volume
      const errorAnomaly = errorRate > 0.1 ? 0.5 : 0 // High error rate
      const timeAnomaly = (index % 24 >= 2 && index % 24 <= 6) ? 0.2 : 0 // Night hours
      const randomAnomaly = Math.random() * 0.3 // Random factor
      
      const anomalyScore = Math.min(1, volumeAnomaly + errorAnomaly + timeAnomaly + randomAnomaly)
      
      return {
        ...item,
        timestamp: new Date(item.time).getTime(),
        anomalyScore,
        severity: anomalyScore > 0.8 ? 'high' : anomalyScore > 0.5 ? 'medium' : 'low',
        totalLogs,
        errorCount,
        errorRate: errorRate * 100
      }
    })
  }, [data])

  const getColor = (severity: string) => {
    switch (severity) {
      case 'high': return '#dc2626'
      case 'medium': return '#f59e0b'
      case 'low': return '#10b981'
      default: return '#6b7280'
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <Card className="p-3">
          <CardContent className="p-0">
            <div className="space-y-2">
              <div className="font-medium text-sm">
                {new Date(data.timestamp).toLocaleString()}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Anomaly Score:</span>
                <Badge 
                  variant={data.severity === 'high' ? 'destructive' : data.severity === 'medium' ? 'default' : 'secondary'}
                >
                  {data.anomalyScore.toFixed(3)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Severity:</span>
                <Badge 
                  variant={data.severity === 'high' ? 'destructive' : data.severity === 'medium' ? 'default' : 'secondary'}
                >
                  {data.severity}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Total Logs:</span>
                <span className="text-sm">{data.totalLogs}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Error Rate:</span>
                <span className="text-sm">{data.errorRate.toFixed(1)}%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }
    return null
  }

  const CustomCell = (props: any) => {
    const { cx, cy, payload } = props
    const isSelected = selectedPoint?.timestamp === payload.timestamp
    const isAboveThreshold = payload.anomalyScore > threshold
    
    return (
      <circle
        cx={cx}
        cy={cy}
        r={isSelected ? 8 : isAboveThreshold ? 6 : 4}
        fill={getColor(payload.severity)}
        stroke={isSelected ? "#000" : isAboveThreshold ? "#fff" : "transparent"}
        strokeWidth={isSelected ? 2 : isAboveThreshold ? 1 : 0}
        className="cursor-pointer transition-all duration-200 hover:r-6"
        onClick={() => setSelectedPoint(isSelected ? null : payload)}
      />
    )
  }

  const highAnomalies = anomalyData.filter(item => item.severity === 'high').length
  const mediumAnomalies = anomalyData.filter(item => item.severity === 'medium').length
  const lowAnomalies = anomalyData.filter(item => item.severity === 'low').length

  return (
    <div className={cn("w-full", className)}>
      {/* Controls and Stats */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm">
            <label>Threshold:</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-20"
            />
            <span className="text-xs text-muted-foreground">{threshold}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge variant="destructive" className="text-xs">
            {highAnomalies} High
          </Badge>
          <Badge variant="default" className="text-xs">
            {mediumAnomalies} Medium
          </Badge>
          <Badge variant="secondary" className="text-xs">
            {lowAnomalies} Low
          </Badge>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart
          data={anomalyData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            type="number"
            dataKey="timestamp"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value)
              return date.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })
            }}
            label={{ value: 'Time', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            domain={[0, 1]}
            label={{ value: 'Anomaly Score', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Threshold line */}
          <ReferenceLine 
            y={threshold} 
            stroke="#f59e0b" 
            strokeDasharray="5 5"
            label={{ value: "Threshold", position: "topRight" }}
          />
          
          {/* Anomaly points */}
          <Scatter
            dataKey="anomalyScore"
            shape={<CustomCell />}
          />
        </ScatterChart>
      </ResponsiveContainer>
      
      {/* Selected Point Details */}
      {selectedPoint && (
        <Card className="mt-4 border-primary/20">
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-sm">Selected Anomaly</h4>
                <button
                  onClick={() => setSelectedPoint(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>Time: {new Date(selectedPoint.timestamp).toLocaleString()}</div>
                <div>Score: {selectedPoint.anomalyScore.toFixed(3)}</div>
                <div>Severity: {selectedPoint.severity}</div>
                <div>Logs: {selectedPoint.totalLogs}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-600 rounded-full" />
          High Risk
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-amber-500 rounded-full" />
          Medium Risk
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded-full" />
          Low Risk
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-amber-500 border-dashed border-t" />
          Threshold
        </div>
      </div>
    </div>
  )
}

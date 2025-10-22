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
  Legend,
  ReferenceLine
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface PerformanceChartProps {
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

export function PerformanceChart({ data, className }: PerformanceChartProps) {
  const [activeMetrics, setActiveMetrics] = React.useState({
    responseTime: true,
    throughput: true,
    errorRate: true
  })

  // Mock performance data - in real implementation, this would come from API
  const performanceData = React.useMemo(() => {
    return data.map((item, index) => {
      const totalLogs = (item.DEBUG || 0) + (item.INFO || 0) + (item.WARN || 0) + (item.ERROR || 0) + (item.CRITICAL || 0)
      const errorCount = (item.ERROR || 0) + (item.CRITICAL || 0)
      
      // Simulate performance metrics based on log data
      const baseResponseTime = 150 + Math.sin(index * 0.1) * 50 + Math.random() * 30
      const baseThroughput = totalLogs * 0.8 + Math.random() * 100
      const errorRate = totalLogs > 0 ? (errorCount / totalLogs) * 100 : 0
      
      return {
        ...item,
        responseTime: Math.max(50, baseResponseTime),
        throughput: Math.max(0, baseThroughput),
        errorRate: Math.min(100, errorRate),
        cpuUsage: 60 + Math.sin(index * 0.15) * 20 + Math.random() * 10,
        memoryUsage: 70 + Math.cos(index * 0.12) * 15 + Math.random() * 8
      }
    })
  }, [data])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Card className="p-3">
          <CardContent className="p-0">
            <div className="space-y-2">
              <div className="font-medium text-sm">{label}</div>
              {payload.map((entry: any, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-sm">{entry.name}:</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {entry.value.toFixed(2)}{entry.unit || ''}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )
    }
    return null
  }

  const CustomLegend = ({ payload }: any) => {
    return (
      <div className="flex flex-wrap gap-2 justify-center mt-4">
        {payload?.map((entry: any, index: number) => {
          const metric = entry.dataKey as keyof typeof activeMetrics
          const isActive = activeMetrics[metric]
          
          return (
            <button
              key={index}
              onClick={() => setActiveMetrics(prev => ({
                ...prev,
                [metric]: !prev[metric]
              }))}
              className={cn(
                "flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium transition-all",
                isActive 
                  ? "bg-primary/10 text-primary border border-primary/20" 
                  : "bg-muted text-muted-foreground border border-muted"
              )}
            >
              <div 
                className="w-2 h-2 rounded-full" 
                style={{ backgroundColor: isActive ? entry.color : "#94a3b8" }}
              />
              {entry.value}
            </button>
          )
        })}
      </div>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={performanceData}
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
          <YAxis 
            yAxisId="left"
            tick={{ fontSize: 12 }}
            label={{ value: 'Response Time (ms)', angle: -90, position: 'insideLeft' }}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
            label={{ value: 'Throughput (req/s)', angle: 90, position: 'insideRight' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
          
          {/* Response Time */}
          {activeMetrics.responseTime && (
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="responseTime"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, stroke: "#3b82f6", strokeWidth: 2 }}
              name="Response Time"
              unit="ms"
            />
          )}
          
          {/* Throughput */}
          {activeMetrics.throughput && (
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="throughput"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, stroke: "#10b981", strokeWidth: 2 }}
              name="Throughput"
              unit=" req/s"
            />
          )}
          
          {/* Error Rate */}
          {activeMetrics.errorRate && (
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="errorRate"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, stroke: "#ef4444", strokeWidth: 2 }}
              name="Error Rate"
              unit="%"
            />
          )}
          
          {/* Performance thresholds */}
          <ReferenceLine 
            yAxisId="left"
            y={200} 
            stroke="#f59e0b" 
            strokeDasharray="5 5"
            label={{ value: "Slow Response", position: "topRight" }}
          />
          <ReferenceLine 
            yAxisId="left"
            y={5} 
            stroke="#ef4444" 
            strokeDasharray="5 5"
            label={{ value: "High Error Rate", position: "topRight" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

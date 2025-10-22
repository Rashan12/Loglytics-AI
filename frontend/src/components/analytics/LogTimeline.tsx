"use client"

import * as React from "react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface LogTimelineProps {
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

const logLevelColors = {
  DEBUG: "#10b981",
  INFO: "#3b82f6", 
  WARN: "#f59e0b",
  ERROR: "#ef4444",
  CRITICAL: "#7c2d12"
}

const logLevelNames = {
  DEBUG: "Debug",
  INFO: "Info",
  WARN: "Warning", 
  ERROR: "Error",
  CRITICAL: "Critical"
}

export function LogTimeline({ data, className }: LogTimelineProps) {
  const [activeLines, setActiveLines] = React.useState({
    DEBUG: true,
    INFO: true,
    WARN: true,
    ERROR: true,
    CRITICAL: true
  })

  const toggleLine = (level: keyof typeof activeLines) => {
    setActiveLines(prev => ({
      ...prev,
      [level]: !prev[level]
    }))
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Card className="p-3">
          <CardContent className="p-0">
            <p className="font-medium mb-2">{label}</p>
            <div className="space-y-1">
              {payload.map((entry: any, index: number) => (
                <div key={index} className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-sm">
                    {logLevelNames[entry.dataKey as keyof typeof logLevelNames]}: {entry.value}
                  </span>
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
          const level = entry.dataKey as keyof typeof activeLines
          const isActive = activeLines[level]
          
          return (
            <button
              key={index}
              onClick={() => toggleLine(level)}
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
              {logLevelNames[level]}
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
          data={data}
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
          <Legend content={<CustomLegend />} />
          
          {Object.entries(logLevelColors).map(([level, color]) => {
            const levelKey = level as keyof typeof activeLines
            if (!activeLines[levelKey]) return null
            
            return (
              <Line
                key={level}
                type="monotone"
                dataKey={level}
                stroke={color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, stroke: color, strokeWidth: 2 }}
                connectNulls={false}
              />
            )
          })}
          
          <Brush 
            dataKey="time"
            height={30}
            tickFormatter={(value) => {
              const date = new Date(value)
              return date.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

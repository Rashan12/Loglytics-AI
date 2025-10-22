"use client"

import * as React from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface TopErrorsBarProps {
  data: Array<{
    message: string
    count: number
  }>
  className?: string
}

export function TopErrorsBar({ data, className }: TopErrorsBarProps) {
  const [selectedError, setSelectedError] = React.useState<string | null>(null)

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <Card className="p-3 max-w-xs">
          <CardContent className="p-0">
            <div className="space-y-2">
              <div className="font-medium text-sm">Error Details</div>
              <div className="text-xs text-muted-foreground break-words">
                {data.message}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Count:</span>
                <Badge variant="secondary">{data.count.toLocaleString()}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }
    return null
  }

  const CustomBar = (props: any) => {
    const { payload, fill, x, y, width, height } = props
    const isSelected = selectedError === payload.message
    
    return (
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={isSelected ? fill : fill}
        opacity={isSelected ? 1 : 0.8}
        rx={4}
        ry={4}
        className="transition-all duration-200 hover:opacity-100 cursor-pointer"
        onClick={() => setSelectedError(isSelected ? null : payload.message)}
      />
    )
  }

  // Sort data by count and take top 10
  const sortedData = [...data]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
    .map((item, index) => ({
      ...item,
      index: index + 1,
      truncatedMessage: item.message.length > 30 
        ? item.message.substring(0, 30) + "..." 
        : item.message
    }))

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={sortedData}
          layout="horizontal"
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
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => value.toLocaleString()}
          />
          <YAxis 
            type="category" 
            dataKey="truncatedMessage"
            tick={{ fontSize: 11 }}
            width={200}
            interval={0}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="count" 
            fill="#ef4444"
            shape={<CustomBar />}
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
      
      {/* Selected Error Details */}
      {selectedError && (
        <Card className="mt-4 border-primary/20">
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-sm">Selected Error</h4>
                <button
                  onClick={() => setSelectedError(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </div>
              <p className="text-sm text-muted-foreground break-words">
                {selectedError}
              </p>
              <div className="flex items-center gap-2">
                <Badge variant="destructive">
                  {data.find(item => item.message === selectedError)?.count.toLocaleString()} occurrences
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

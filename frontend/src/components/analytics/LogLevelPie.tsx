"use client"

import * as React from "react"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface LogLevelPieProps {
  data: Array<{
    name: string
    value: number
    color: string
  }>
  className?: string
}

const RADIAN = Math.PI / 180

const renderCustomizedLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
  name
}: any) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)

  return (
    <text 
      x={x} 
      y={y} 
      fill="white" 
      textAnchor={x > cx ? 'start' : 'end'} 
      dominantBaseline="central"
      fontSize={12}
      fontWeight="bold"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

export function LogLevelPie({ data, className }: LogLevelPieProps) {
  const [activeIndex, setActiveIndex] = React.useState<number | null>(null)

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <Card className="p-3">
          <CardContent className="p-0">
            <div className="flex items-center gap-2 mb-1">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: data.color }}
              />
              <span className="font-medium">{data.name}</span>
            </div>
            <div className="text-sm text-muted-foreground">
              Count: {data.value.toLocaleString()}
            </div>
            <div className="text-sm text-muted-foreground">
              Percentage: {((data.value / data.total) * 100).toFixed(1)}%
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
        {payload?.map((entry: any, index: number) => (
          <button
            key={index}
            onClick={() => setActiveIndex(activeIndex === index ? null : index)}
            className={cn(
              "flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium transition-all",
              activeIndex === index
                ? "bg-primary/10 text-primary border border-primary/20"
                : "bg-muted text-muted-foreground border border-muted"
            )}
          >
            <div 
              className="w-2 h-2 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            {entry.value}
          </button>
        ))}
      </div>
    )
  }

  // Calculate total for percentage calculations
  const total = data.reduce((sum, item) => sum + item.value, 0)

  // Add total to each data point for tooltip
  const dataWithTotal = data.map(item => ({ ...item, total }))

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={dataWithTotal}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomizedLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
            activeIndex={activeIndex}
            onMouseEnter={(_, index) => setActiveIndex(index)}
            onMouseLeave={() => setActiveIndex(null)}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color}
                stroke={activeIndex === index ? entry.color : "transparent"}
                strokeWidth={activeIndex === index ? 3 : 0}
                style={{
                  filter: activeIndex === null || activeIndex === index 
                    ? 'none' 
                    : 'opacity(0.3)'
                }}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-2 gap-2">
        {data.map((item, index) => (
          <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2">
              <div 
                className="w-2 h-2 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-xs font-medium">{item.name}</span>
            </div>
            <Badge variant="secondary" className="text-xs">
              {item.value.toLocaleString()}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  )
}

"use client"

import * as React from "react"
import {
  Treemap,
  ResponsiveContainer,
  Tooltip
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ServiceBreakdownProps {
  data: Array<{
    message: string
    count: number
  }>
  className?: string
}

export function ServiceBreakdown({ data, className }: ServiceBreakdownProps) {
  const [selectedService, setSelectedService] = React.useState<string | null>(null)

  // Transform error data into service breakdown
  const serviceData = React.useMemo(() => {
    const serviceMap = new Map<string, { count: number; errors: string[] }>()
    
    data.forEach(item => {
      // Extract service name from error message (simple heuristic)
      let serviceName = "Unknown"
      
      if (item.message.toLowerCase().includes("database")) {
        serviceName = "Database"
      } else if (item.message.toLowerCase().includes("api")) {
        serviceName = "API Gateway"
      } else if (item.message.toLowerCase().includes("auth")) {
        serviceName = "Authentication"
      } else if (item.message.toLowerCase().includes("payment")) {
        serviceName = "Payment Service"
      } else if (item.message.toLowerCase().includes("email")) {
        serviceName = "Email Service"
      } else if (item.message.toLowerCase().includes("cache")) {
        serviceName = "Cache Service"
      } else if (item.message.toLowerCase().includes("queue")) {
        serviceName = "Queue Service"
      } else if (item.message.toLowerCase().includes("storage")) {
        serviceName = "Storage Service"
      } else if (item.message.toLowerCase().includes("network")) {
        serviceName = "Network"
      } else if (item.message.toLowerCase().includes("timeout")) {
        serviceName = "Timeout Issues"
      } else {
        serviceName = "Other"
      }
      
      if (serviceMap.has(serviceName)) {
        const existing = serviceMap.get(serviceName)!
        existing.count += item.count
        existing.errors.push(item.message)
      } else {
        serviceMap.set(serviceName, {
          count: item.count,
          errors: [item.message]
        })
      }
    })
    
    // Convert to array and calculate percentages
    const total = Array.from(serviceMap.values()).reduce((sum, item) => sum + item.count, 0)
    
    return Array.from(serviceMap.entries()).map(([name, data]) => ({
      name,
      count: data.count,
      percentage: (data.count / total) * 100,
      errors: data.errors,
      color: getServiceColor(name)
    })).sort((a, b) => b.count - a.count)
  }, [data])

  const getServiceColor = (serviceName: string) => {
    const colors = [
      "#ef4444", "#f59e0b", "#10b981", "#3b82f6", 
      "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"
    ]
    const hash = serviceName.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0)
      return a & a
    }, 0)
    return colors[Math.abs(hash) % colors.length]
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <Card className="p-3">
          <CardContent className="p-0">
            <div className="space-y-2">
              <div className="font-medium text-sm">{data.name}</div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Errors:</span>
                <Badge variant="destructive">{data.count.toLocaleString()}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Percentage:</span>
                <span className="text-sm">{data.percentage.toFixed(1)}%</span>
              </div>
              <div className="text-xs text-muted-foreground">
                Click to view details
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }
    return null
  }

  const CustomContent = (props: any) => {
    const { root, depth, x, y, width, height, index, payload, colors, rank, name } = props
    const isSelected = selectedService === payload.name
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: isSelected ? payload.color : payload.color,
            stroke: isSelected ? "#000" : "#fff",
            strokeWidth: isSelected ? 2 : 1,
            strokeOpacity: 0.8,
            opacity: isSelected ? 1 : 0.8
          }}
          onClick={() => setSelectedService(isSelected ? null : payload.name)}
          className="cursor-pointer transition-all duration-200"
        />
        {width > 60 && height > 20 && (
          <text
            x={x + width / 2}
            y={y + height / 2}
            textAnchor="middle"
            fill="white"
            fontSize={12}
            fontWeight="bold"
            className="pointer-events-none"
          >
            {payload.name}
          </text>
        )}
        {width > 80 && height > 30 && (
          <text
            x={x + width / 2}
            y={y + height / 2 + 12}
            textAnchor="middle"
            fill="white"
            fontSize={10}
            className="pointer-events-none"
          >
            {payload.count.toLocaleString()}
          </text>
        )}
      </g>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={300}>
        <Treemap
          data={serviceData}
          dataKey="count"
          ratio={4/3}
          stroke="#fff"
          fill="#8884d8"
          content={<CustomContent />}
        >
          <Tooltip content={<CustomTooltip />} />
        </Treemap>
      </ResponsiveContainer>
      
      {/* Service List */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2">
        {serviceData.map((service, index) => (
          <div
            key={index}
            className={cn(
              "flex items-center justify-between p-2 rounded-lg border cursor-pointer transition-all",
              selectedService === service.name
                ? "border-primary bg-primary/5"
                : "border-muted hover:border-primary/50"
            )}
            onClick={() => setSelectedService(selectedService === service.name ? null : service.name)}
          >
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: service.color }}
              />
              <span className="text-sm font-medium">{service.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                {service.count.toLocaleString()}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {service.percentage.toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {/* Selected Service Details */}
      {selectedService && (
        <Card className="mt-4 border-primary/20">
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-sm">{selectedService} Details</h4>
                <button
                  onClick={() => setSelectedService(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Error Count:</span> {serviceData.find(s => s.name === selectedService)?.count.toLocaleString()}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Percentage:</span> {serviceData.find(s => s.name === selectedService)?.percentage.toFixed(1)}%
                </div>
              </div>
              
              <div className="space-y-1">
                <div className="text-sm font-medium">Sample Errors:</div>
                <div className="max-h-32 overflow-y-auto space-y-1">
                  {serviceData
                    .find(s => s.name === selectedService)
                    ?.errors.slice(0, 5)
                    .map((error, index) => (
                      <div key={index} className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                        {error.length > 80 ? error.substring(0, 80) + "..." : error}
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

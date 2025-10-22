"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Database, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Clock,
  Activity,
  BarChart3,
  Zap
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface StatsCardProps {
  title: string
  value: string
  change?: string
  changeType?: "positive" | "negative" | "neutral"
  icon?: string
  description?: string
  isLoading?: boolean
  className?: string
}

const iconMap = {
  Database,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Clock,
  Activity,
  BarChart3,
  Zap
}

const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
  hover: { scale: 1.02 }
}

export function StatsCard({
  title,
  value,
  change,
  changeType = "neutral",
  icon = "BarChart3",
  description,
  isLoading = false,
  className
}: StatsCardProps) {
  const IconComponent = iconMap[icon as keyof typeof iconMap] || BarChart3

  if (isLoading) {
    return (
      <Card className={cn("relative overflow-hidden", className)}>
        <CardHeader className="pb-2">
          <Skeleton className="h-4 w-24" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-3 w-16" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className="h-full"
    >
      <Card className={cn("relative overflow-hidden h-full", className)}>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {title}
            </CardTitle>
            <div className="p-2 rounded-lg bg-primary/10">
              <IconComponent className="h-4 w-4 text-primary" />
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{value}</span>
              {change && (
                <Badge
                  variant={changeType === "positive" ? "default" : changeType === "negative" ? "destructive" : "secondary"}
                  className="text-xs"
                >
                  {changeType === "positive" && <TrendingUp className="h-3 w-3 mr-1" />}
                  {changeType === "negative" && <TrendingDown className="h-3 w-3 mr-1" />}
                  {change}
                </Badge>
              )}
            </div>
            
            {description && (
              <CardDescription className="text-xs">
                {description}
              </CardDescription>
            )}
          </div>
        </CardContent>

        {/* Subtle gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
      </Card>
    </motion.div>
  )
}

"use client"

import * as React from "react"
import { Filter, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { LogLevel } from "@/store/analytics-store"

interface FilterControlsProps {
  logLevels: LogLevel
  onLogLevelsChange: (levels: LogLevel) => void
  selectedProject: string | null
  onProjectChange: (projectId: string | null) => void
  className?: string
}

const logLevelOptions = [
  { key: "DEBUG" as const, label: "Debug", color: "bg-green-500" },
  { key: "INFO" as const, label: "Info", color: "bg-blue-500" },
  { key: "WARN" as const, label: "Warning", color: "bg-yellow-500" },
  { key: "ERROR" as const, label: "Error", color: "bg-red-500" },
  { key: "CRITICAL" as const, label: "Critical", color: "bg-red-800" }
]

// Mock projects - in real implementation, this would come from API
const mockProjects = [
  { id: "all", name: "All Projects" },
  { id: "proj-1", name: "E-commerce Platform" },
  { id: "proj-2", name: "Mobile App Backend" },
  { id: "proj-3", name: "Payment Service" },
  { id: "proj-4", name: "User Management" },
  { id: "proj-5", name: "Analytics Service" }
]

export function FilterControls({
  logLevels,
  onLogLevelsChange,
  selectedProject,
  onProjectChange,
  className
}: FilterControlsProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)

  const handleLogLevelChange = (level: keyof LogLevel, checked: boolean) => {
    onLogLevelsChange({
      ...logLevels,
      [level]: checked
    })
  }

  const handleSelectAll = () => {
    const allSelected = Object.values(logLevels).every(Boolean)
    const newLevels = Object.keys(logLevels).reduce((acc, key) => {
      acc[key as keyof LogLevel] = !allSelected
      return acc
    }, {} as LogLevel)
    onLogLevelsChange(newLevels)
  }

  const handleClearAll = () => {
    onLogLevelsChange({
      DEBUG: false,
      INFO: false,
      WARN: false,
      ERROR: false,
      CRITICAL: false
    })
  }

  const selectedCount = Object.values(logLevels).filter(Boolean).length
  const allSelected = selectedCount === Object.keys(logLevels).length

  return (
    <div className={cn("space-y-3", className)}>
      {/* Project Filter */}
      <div className="space-y-2">
        <Label className="text-xs font-medium">Project</Label>
        <Select
          value={selectedProject || "all"}
          onValueChange={(value) => onProjectChange(value === "all" ? null : value)}
        >
          <SelectTrigger className="h-8">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {mockProjects.map((project) => (
              <SelectItem key={project.id} value={project.id}>
                {project.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Log Level Filter */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-xs font-medium">Log Levels</Label>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="h-6 px-2 text-xs"
          >
            <Filter className="h-3 w-3 mr-1" />
            {selectedCount > 0 && (
              <Badge variant="secondary" className="ml-1 h-4 px-1 text-xs">
                {selectedCount}
              </Badge>
            )}
          </Button>
        </div>

        {isExpanded && (
          <div className="space-y-3 p-3 border rounded-lg bg-muted/50">
            {/* Quick Actions */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
                className="h-6 px-2 text-xs"
              >
                {allSelected ? "Deselect All" : "Select All"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearAll}
                className="h-6 px-2 text-xs"
              >
                Clear All
              </Button>
            </div>

            {/* Log Level Checkboxes */}
            <div className="space-y-2">
              {logLevelOptions.map((option) => (
                <div key={option.key} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.key}
                    checked={logLevels[option.key]}
                    onCheckedChange={(checked) => 
                      handleLogLevelChange(option.key, checked as boolean)
                    }
                    className="h-4 w-4"
                  />
                  <Label
                    htmlFor={option.key}
                    className="flex items-center gap-2 text-sm cursor-pointer"
                  >
                    <div className={cn("w-2 h-2 rounded-full", option.color)} />
                    {option.label}
                  </Label>
                </div>
              ))}
            </div>

            {/* Selected Summary */}
            {selectedCount > 0 && (
              <div className="pt-2 border-t">
                <div className="flex flex-wrap gap-1">
                  {logLevelOptions
                    .filter(option => logLevels[option.key])
                    .map((option) => (
                      <Badge
                        key={option.key}
                        variant="secondary"
                        className="text-xs h-5"
                      >
                        <div className={cn("w-1.5 h-1.5 rounded-full mr-1", option.color)} />
                        {option.label}
                      </Badge>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Compact View */}
        {!isExpanded && selectedCount > 0 && (
          <div className="flex flex-wrap gap-1">
            {logLevelOptions
              .filter(option => logLevels[option.key])
              .map((option) => (
                <Badge
                  key={option.key}
                  variant="secondary"
                  className="text-xs h-5"
                >
                  <div className={cn("w-1.5 h-1.5 rounded-full mr-1", option.color)} />
                  {option.label}
                </Badge>
              ))}
            {selectedCount > 3 && (
              <Badge variant="outline" className="text-xs h-5">
                +{selectedCount - 3} more
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Active Filters Summary */}
      {(selectedProject !== null || selectedCount < Object.keys(logLevels).length) && (
        <div className="pt-2 border-t">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Active Filters</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                onProjectChange(null)
                onLogLevelsChange({
                  DEBUG: true,
                  INFO: true,
                  WARN: true,
                  ERROR: true,
                  CRITICAL: true
                })
              }}
              className="h-4 px-1 text-xs"
            >
              <X className="h-3 w-3 mr-1" />
              Clear All
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

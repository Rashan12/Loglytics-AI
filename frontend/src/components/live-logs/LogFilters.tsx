"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { X, RotateCcw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useLiveLogsStore } from "@/store/live-logs-store"

interface LogFiltersProps {
  onApply: () => void
}

const logLevels = [
  { value: 'DEBUG', label: 'Debug', color: 'bg-gray-500' },
  { value: 'INFO', label: 'Info', color: 'bg-blue-500' },
  { value: 'WARN', label: 'Warning', color: 'bg-yellow-500' },
  { value: 'ERROR', label: 'Error', color: 'bg-red-500' },
  { value: 'CRITICAL', label: 'Critical', color: 'bg-red-700' }
]

const timeRanges = [
  { value: 'all', label: 'All Time' },
  { value: 'last_5m', label: 'Last 5 minutes' },
  { value: 'last_15m', label: 'Last 15 minutes' },
  { value: 'last_1h', label: 'Last 1 hour' },
  { value: 'last_6h', label: 'Last 6 hours' },
  { value: 'last_24h', label: 'Last 24 hours' }
]

export function LogFilters({ onApply }: LogFiltersProps) {
  const {
    logLevels: selectedLevels,
    timeRange,
    sourceFilter,
    setLogLevels,
    setTimeRange,
    setSourceFilter,
    applyFilters
  } = useLiveLogsStore()

  const [keywordFilter, setKeywordFilter] = React.useState("")
  const [regexEnabled, setRegexEnabled] = React.useState(false)

  const handleLogLevelToggle = (level: string) => {
    const newLevels = selectedLevels.includes(level)
      ? selectedLevels.filter(l => l !== level)
      : [...selectedLevels, level]
    setLogLevels(newLevels)
  }

  const handleSelectAllLevels = () => {
    setLogLevels(logLevels.map(l => l.value))
  }

  const handleClearAllLevels = () => {
    setLogLevels([])
  }

  const handleResetFilters = () => {
    setLogLevels(logLevels.map(l => l.value))
    setTimeRange('all')
    setSourceFilter('')
    setKeywordFilter('')
    setRegexEnabled(false)
    applyFilters()
  }

  const handleApplyFilters = () => {
    // Apply keyword filter to the store
    // This would be implemented in the store
    applyFilters()
    onApply()
  }

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      className="p-4 space-y-4"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Filter Logs</h3>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleResetFilters}
            className="text-xs"
          >
            <RotateCcw className="h-3 w-3 mr-1" />
            Reset
          </Button>
          <Button size="sm" onClick={handleApplyFilters} className="text-xs">
            Apply Filters
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Log Levels */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs font-medium">Log Levels</Label>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSelectAllLevels}
                className="text-xs h-6 px-2"
              >
                All
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearAllLevels}
                className="text-xs h-6 px-2"
              >
                None
              </Button>
            </div>
          </div>
          <div className="space-y-1">
            {logLevels.map((level) => (
              <div key={level.value} className="flex items-center space-x-2">
                <Checkbox
                  id={level.value}
                  checked={selectedLevels.includes(level.value)}
                  onCheckedChange={() => handleLogLevelToggle(level.value)}
                  className="h-4 w-4"
                />
                <Label
                  htmlFor={level.value}
                  className="flex items-center gap-2 text-xs cursor-pointer"
                >
                  <div className={`w-2 h-2 rounded-full ${level.color}`} />
                  {level.label}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Time Range */}
        <div className="space-y-2">
          <Label className="text-xs font-medium">Time Range</Label>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="h-8">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {timeRanges.map((range) => (
                <SelectItem key={range.value} value={range.value}>
                  {range.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Source Filter */}
        <div className="space-y-2">
          <Label className="text-xs font-medium">Source</Label>
          <Input
            placeholder="Filter by source..."
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="h-8"
          />
        </div>

        {/* Keyword Filter */}
        <div className="space-y-2">
          <Label className="text-xs font-medium">Keyword Search</Label>
          <div className="space-y-1">
            <Input
              placeholder="Search in messages..."
              value={keywordFilter}
              onChange={(e) => setKeywordFilter(e.target.value)}
              className="h-8"
            />
            <div className="flex items-center space-x-2">
              <Checkbox
                id="regex"
                checked={regexEnabled}
                onCheckedChange={setRegexEnabled}
                className="h-3 w-3"
              />
              <Label htmlFor="regex" className="text-xs cursor-pointer">
                Use regex
              </Label>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Filter Buttons */}
      <div className="space-y-2">
        <Label className="text-xs font-medium">Quick Filters</Label>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setLogLevels(['ERROR', 'CRITICAL'])}
            className="text-xs h-6"
          >
            Errors Only
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setLogLevels(['WARN'])}
            className="text-xs h-6"
          >
            Warnings Only
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setLogLevels(['INFO'])}
            className="text-xs h-6"
          >
            Info Only
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setTimeRange('last_5m')}
            className="text-xs h-6"
          >
            Last 5 Minutes
          </Button>
        </div>
      </div>

      {/* Active Filters Summary */}
      {(selectedLevels.length < logLevels.length || timeRange !== 'all' || sourceFilter || keywordFilter) && (
        <div className="space-y-2">
          <Label className="text-xs font-medium">Active Filters</Label>
          <div className="flex flex-wrap gap-1">
            {selectedLevels.length < logLevels.length && (
              <Badge variant="secondary" className="text-xs">
                Levels: {selectedLevels.join(', ')}
              </Badge>
            )}
            {timeRange !== 'all' && (
              <Badge variant="secondary" className="text-xs">
                Time: {timeRanges.find(r => r.value === timeRange)?.label}
              </Badge>
            )}
            {sourceFilter && (
              <Badge variant="secondary" className="text-xs">
                Source: {sourceFilter}
              </Badge>
            )}
            {keywordFilter && (
              <Badge variant="secondary" className="text-xs">
                Keyword: {keywordFilter}
              </Badge>
            )}
          </div>
        </div>
      )}
    </motion.div>
  )
}

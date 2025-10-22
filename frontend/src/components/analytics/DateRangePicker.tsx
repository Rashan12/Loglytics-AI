"use client"

import * as React from "react"
import { Calendar, Clock } from "lucide-react"
import { format } from "date-fns"

import { Button } from "@/components/ui/button"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"
import { DateRange } from "@/store/analytics-store"

interface DateRangePickerProps {
  value: DateRange
  onChange: (range: DateRange) => void
  className?: string
}

const presets = [
  {
    label: "Last Hour",
    value: "last_hour" as const,
    getValue: () => ({
      from: new Date(Date.now() - 60 * 60 * 1000),
      to: new Date(),
      preset: "last_hour" as const
    })
  },
  {
    label: "Last 24 Hours",
    value: "last_24h" as const,
    getValue: () => ({
      from: new Date(Date.now() - 24 * 60 * 60 * 1000),
      to: new Date(),
      preset: "last_24h" as const
    })
  },
  {
    label: "Last 7 Days",
    value: "last_7d" as const,
    getValue: () => ({
      from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      to: new Date(),
      preset: "last_7d" as const
    })
  },
  {
    label: "Last 30 Days",
    value: "last_30d" as const,
    getValue: () => ({
      from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      to: new Date(),
      preset: "last_30d" as const
    })
  },
  {
    label: "Custom Range",
    value: "custom" as const,
    getValue: () => ({
      from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      to: new Date(),
      preset: "custom" as const
    })
  }
]

export function DateRangePicker({ value, onChange, className }: DateRangePickerProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const [tempRange, setTempRange] = React.useState<DateRange>(value)

  const handlePresetChange = (presetValue: string) => {
    const preset = presets.find(p => p.value === presetValue)
    if (preset) {
      const newRange = preset.getValue()
      setTempRange(newRange)
      onChange(newRange)
    }
  }

  const handleDateSelect = (selectedDate: Date | undefined) => {
    if (!selectedDate) return

    if (!tempRange.from || (tempRange.from && tempRange.to)) {
      // Start new range
      setTempRange({
        from: selectedDate,
        to: undefined,
        preset: "custom"
      })
    } else {
      // Complete range
      const newRange = {
        from: tempRange.from,
        to: selectedDate,
        preset: "custom" as const
      }
      setTempRange(newRange)
      onChange(newRange)
    }
  }

  const handleApply = () => {
    if (tempRange.from && tempRange.to) {
      onChange(tempRange)
      setIsOpen(false)
    }
  }

  const handleCancel = () => {
    setTempRange(value)
    setIsOpen(false)
  }

  const formatDateRange = (range: DateRange) => {
    if (!range.from) return "Select date range"
    
    if (range.preset && range.preset !== "custom") {
      const preset = presets.find(p => p.value === range.preset)
      return preset?.label || "Custom Range"
    }
    
    if (range.to) {
      return `${format(range.from, "MMM dd")} - ${format(range.to, "MMM dd, yyyy")}`
    }
    
    return format(range.from, "MMM dd, yyyy")
  }

  return (
    <div className={cn("space-y-2", className)}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-full justify-start text-left font-normal",
              !value.from && "text-muted-foreground"
            )}
          >
            <Calendar className="mr-2 h-4 w-4" />
            {formatDateRange(value)}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <div className="flex">
            <div className="p-3 border-r">
              <div className="space-y-2">
                <div className="text-sm font-medium">Quick Select</div>
                <Select
                  value={value.preset || "custom"}
                  onValueChange={handlePresetChange}
                >
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {presets.map((preset) => (
                      <SelectItem key={preset.value} value={preset.value}>
                        {preset.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="p-3">
              <CalendarComponent
                mode="range"
                selected={{
                  from: tempRange.from,
                  to: tempRange.to
                }}
                onSelect={handleDateSelect}
                numberOfMonths={2}
                disabled={(date) => date > new Date() || date < new Date("1900-01-01")}
              />
              
              <div className="flex justify-end gap-2 pt-3 border-t">
                <Button variant="outline" size="sm" onClick={handleCancel}>
                  Cancel
                </Button>
                <Button 
                  size="sm" 
                  onClick={handleApply}
                  disabled={!tempRange.from || !tempRange.to}
                >
                  Apply
                </Button>
              </div>
            </div>
          </div>
        </PopoverContent>
      </Popover>
      
      {/* Current Range Info */}
      {value.from && value.to && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>
            {Math.ceil((value.to.getTime() - value.from.getTime()) / (1000 * 60 * 60 * 24))} days
          </span>
        </div>
      )}
    </div>
  )
}

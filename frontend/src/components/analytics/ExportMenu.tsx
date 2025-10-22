"use client"

import * as React from "react"
import { Download, FileText, Image, Share2, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ExportMenuProps {
  onExport: (format: string) => void
  className?: string
}

const exportOptions = [
  {
    id: "pdf",
    label: "PDF Report",
    description: "Complete analytics report with charts",
    icon: FileText,
    format: "pdf"
  },
  {
    id: "csv",
    label: "CSV Data",
    description: "Raw data in CSV format",
    icon: FileText,
    format: "csv"
  },
  {
    id: "json",
    label: "JSON Data",
    description: "Structured data in JSON format",
    icon: FileText,
    format: "json"
  },
  {
    id: "png",
    label: "PNG Images",
    description: "Charts as PNG images",
    icon: Image,
    format: "png"
  },
  {
    id: "share",
    label: "Share Link",
    description: "Generate shareable link",
    icon: Share2,
    format: "share"
  }
]

export function ExportMenu({ onExport, className }: ExportMenuProps) {
  const [isExporting, setIsExporting] = React.useState<string | null>(null)

  const handleExport = async (format: string) => {
    setIsExporting(format)
    
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 2000))
      onExport(format)
    } catch (error) {
      console.error("Export failed:", error)
    } finally {
      setIsExporting(null)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className={cn("flex items-center gap-2", className)}>
          <Download className="h-4 w-4" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel>Export Options</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {exportOptions.map((option) => {
          const Icon = option.icon
          const isCurrentlyExporting = isExporting === option.format
          
          return (
            <DropdownMenuItem
              key={option.id}
              onClick={() => handleExport(option.format)}
              disabled={isCurrentlyExporting}
              className="flex items-start gap-3 p-3"
            >
              <div className="flex-shrink-0 mt-0.5">
                {isCurrentlyExporting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{option.label}</span>
                  {isCurrentlyExporting && (
                    <Badge variant="secondary" className="text-xs">
                      Exporting...
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {option.description}
                </p>
              </div>
            </DropdownMenuItem>
          )
        })}
        
        <DropdownMenuSeparator />
        <div className="p-2">
          <div className="text-xs text-muted-foreground">
            <div>• PDF includes all charts and insights</div>
            <div>• CSV/JSON contain raw data</div>
            <div>• PNG exports individual charts</div>
          </div>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

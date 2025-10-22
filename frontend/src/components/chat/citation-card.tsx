"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { ExternalLink, FileText, Calendar, Hash } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface Citation {
  id: string
  content: string
  source: string
  relevance: number
  logChunk: string
}

interface CitationCardProps {
  citation: Citation
  index: number
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 0.8) return "text-emerald-500 bg-emerald-500/10"
    if (relevance >= 0.6) return "text-amber-500 bg-amber-500/10"
    return "text-red-500 bg-red-500/10"
  }

  const getRelevanceLabel = (relevance: number) => {
    if (relevance >= 0.8) return "High"
    if (relevance >= 0.6) return "Medium"
    return "Low"
  }

  const formatRelevance = (relevance: number) => {
    return Math.round(relevance * 100)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="border border-border rounded-lg bg-muted/30 p-3 space-y-2"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs font-medium">
            {index}
          </div>
          <div className="flex items-center space-x-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">{citation.source}</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge 
            variant="outline" 
            className={cn("text-xs", getRelevanceColor(citation.relevance))}
          >
            {getRelevanceLabel(citation.relevance)} ({formatRelevance(citation.relevance)}%)
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground line-clamp-2">
          {citation.content}
        </p>
        
        {/* Expanded content */}
        <motion.div
          initial={false}
          animate={{ height: isExpanded ? "auto" : 0 }}
          transition={{ duration: 0.3 }}
          className="overflow-hidden"
        >
          <div className="space-y-3 pt-2 border-t border-border">
            {/* Log chunk */}
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Hash className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Original Log Entry</span>
              </div>
              <div className="bg-muted rounded-lg p-3">
                <pre className="text-xs text-muted-foreground whitespace-pre-wrap break-words">
                  {citation.logChunk}
                </pre>
              </div>
            </div>

            {/* Metadata */}
            <div className="flex items-center space-x-4 text-xs text-muted-foreground">
              <div className="flex items-center space-x-1">
                <Calendar className="h-3 w-3" />
                <span>Found in logs</span>
              </div>
              <div className="flex items-center space-x-1">
                <FileText className="h-3 w-3" />
                <span>Source: {citation.source}</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-border">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs"
        >
          {isExpanded ? "Show Less" : "Show More"}
        </Button>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => {
              // TODO: Navigate to source
              console.log("Navigate to source:", citation.source)
            }}
          >
            <ExternalLink className="mr-1 h-3 w-3" />
            View Source
          </Button>
        </div>
      </div>
    </motion.div>
  )
}

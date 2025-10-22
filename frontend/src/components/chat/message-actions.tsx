"use client"

import * as React from "react"
import { motion } from "framer-motion"
import {
  Copy,
  Edit,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  MoreHorizontal,
  ExternalLink,
  Flag,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: string
  model?: "local" | "maverick"
  citations?: Citation[]
  isStreaming?: boolean
  files?: FileAttachment[]
}

interface Citation {
  id: string
  content: string
  source: string
  relevance: number
  logChunk: string
}

interface FileAttachment {
  id: string
  name: string
  size: number
  type: string
  url?: string
}

interface MessageActionsProps {
  message: Message
  onCopy: () => void
  onEdit: () => void
  onRegenerate: () => void
  onFeedback: (type: "up" | "down") => void
  feedback: "up" | "down" | null
  isLast: boolean
}

export function MessageActions({
  message,
  onCopy,
  onEdit,
  onRegenerate,
  onFeedback,
  feedback,
  isLast,
}: MessageActionsProps) {
  const [isHovered, setIsHovered] = React.useState(false)

  const handleShare = () => {
    // TODO: Implement message sharing
    console.log("Share message:", message.id)
  }

  const handleReport = () => {
    // TODO: Implement message reporting
    console.log("Report message:", message.id)
  }

  const handleViewSource = () => {
    // TODO: Implement source viewing
    console.log("View source for message:", message.id)
  }

  return (
    <div className="flex items-center space-x-1">
      {/* Copy Button */}
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6"
        onClick={onCopy}
        title="Copy message"
      >
        <Copy className="h-3 w-3" />
      </Button>

      {/* Feedback Buttons (only for assistant messages) */}
      {message.role === "assistant" && (
        <>
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-6 w-6",
              feedback === "up" && "text-emerald-500 bg-emerald-500/10"
            )}
            onClick={() => onFeedback("up")}
            title="Good response"
          >
            <ThumbsUp className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-6 w-6",
              feedback === "down" && "text-red-500 bg-red-500/10"
            )}
            onClick={() => onFeedback("down")}
            title="Poor response"
          >
            <ThumbsDown className="h-3 w-3" />
          </Button>
        </>
      )}

      {/* More Actions */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            title="More actions"
          >
            <MoreHorizontal className="h-3 w-3" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          {/* Edit (only for user messages) */}
          {message.role === "user" && (
            <DropdownMenuItem onClick={onEdit}>
              <Edit className="mr-2 h-4 w-4" />
              Edit Message
            </DropdownMenuItem>
          )}

          {/* Regenerate (only for assistant messages) */}
          {message.role === "assistant" && isLast && (
            <DropdownMenuItem onClick={onRegenerate}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Regenerate Response
            </DropdownMenuItem>
          )}

          {/* View Source (if citations exist) */}
          {message.citations && message.citations.length > 0 && (
            <DropdownMenuItem onClick={handleViewSource}>
              <ExternalLink className="mr-2 h-4 w-4" />
              View Sources
            </DropdownMenuItem>
          )}

          <DropdownMenuSeparator />

          {/* Share */}
          <DropdownMenuItem onClick={handleShare}>
            <ExternalLink className="mr-2 h-4 w-4" />
            Share Message
          </DropdownMenuItem>

          {/* Report */}
          <DropdownMenuItem onClick={handleReport}>
            <Flag className="mr-2 h-4 w-4" />
            Report Issue
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Download, FileText, X, Calendar, User, Bot, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
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

interface Chat {
  id: string
  title: string
  projectId: string
  model: "local" | "maverick"
  createdAt: string
  updatedAt: string
  messageCount: number
  messages: Message[]
}

interface ChatExportProps {
  chat: Chat
  messages: Message[]
  isOpen: boolean
  onClose: () => void
}

export function ChatExport({ chat, messages, isOpen, onClose }: ChatExportProps) {
  const [exportFormat, setExportFormat] = React.useState<"txt" | "md" | "json">("txt")
  const [isExporting, setIsExporting] = React.useState(false)
  const [exported, setExported] = React.useState(false)

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const generateTextExport = () => {
    let content = `Chat Export: ${chat.title}\n`
    content += `Generated: ${new Date().toLocaleString()}\n`
    content += `Model: ${chat.model === "maverick" ? "Llama Maverick" : "Local LLM"}\n`
    content += `Messages: ${messages.length}\n`
    content += `${"=".repeat(50)}\n\n`

    messages.forEach((message, index) => {
      if (message.role === "system") return

      const role = message.role === "user" ? "User" : "AI Assistant"
      const timestamp = formatTimestamp(message.timestamp)
      
      content += `[${index + 1}] ${role} - ${timestamp}\n`
      content += `${"-".repeat(30)}\n`
      
      if (message.files && message.files.length > 0) {
        content += "Attached Files:\n"
        message.files.forEach(file => {
          content += `  - ${file.name} (${formatFileSize(file.size)})\n`
        })
        content += "\n"
      }
      
      content += `${message.content}\n\n`
      
      if (message.citations && message.citations.length > 0) {
        content += "Citations:\n"
        message.citations.forEach((citation, i) => {
          content += `  ${i + 1}. ${citation.source} (${Math.round(citation.relevance * 100)}% relevance)\n`
          content += `     ${citation.content}\n\n`
        })
      }
      
      content += `${"=".repeat(50)}\n\n`
    })

    return content
  }

  const generateMarkdownExport = () => {
    let content = `# ${chat.title}\n\n`
    content += `**Generated:** ${new Date().toLocaleString()}\n`
    content += `**Model:** ${chat.model === "maverick" ? "Llama Maverick" : "Local LLM"}\n`
    content += `**Messages:** ${messages.length}\n\n`
    content += `---\n\n`

    messages.forEach((message, index) => {
      if (message.role === "system") return

      const role = message.role === "user" ? "User" : "AI Assistant"
      const timestamp = formatTimestamp(message.timestamp)
      
      content += `## ${index + 1}. ${role}\n\n`
      content += `*${timestamp}*\n\n`
      
      if (message.files && message.files.length > 0) {
        content += "**Attached Files:**\n"
        message.files.forEach(file => {
          content += `- ${file.name} (${formatFileSize(file.size)})\n`
        })
        content += "\n"
      }
      
      content += `${message.content}\n\n`
      
      if (message.citations && message.citations.length > 0) {
        content += "**Citations:**\n\n"
        message.citations.forEach((citation, i) => {
          content += `${i + 1}. **${citation.source}** (${Math.round(citation.relevance * 100)}% relevance)\n`
          content += `   ${citation.content}\n\n`
        })
      }
      
      content += `---\n\n`
    })

    return content
  }

  const generateJsonExport = () => {
    const exportData = {
      chat: {
        id: chat.id,
        title: chat.title,
        model: chat.model,
        createdAt: chat.createdAt,
        updatedAt: chat.updatedAt,
        messageCount: messages.length,
      },
      messages: messages.map(message => ({
        id: message.id,
        role: message.role,
        content: message.content,
        timestamp: message.timestamp,
        model: message.model,
        citations: message.citations,
        files: message.files,
      })),
      exportedAt: new Date().toISOString(),
    }

    return JSON.stringify(exportData, null, 2)
  }

  const handleExport = async () => {
    setIsExporting(true)
    
    try {
      let content: string
      let filename: string
      let mimeType: string

      switch (exportFormat) {
        case "txt":
          content = generateTextExport()
          filename = `${chat.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_chat.txt`
          mimeType = "text/plain"
          break
        case "md":
          content = generateMarkdownExport()
          filename = `${chat.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_chat.md`
          mimeType = "text/markdown"
          break
        case "json":
          content = generateJsonExport()
          filename = `${chat.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_chat.json`
          mimeType = "application/json"
          break
        default:
          throw new Error("Invalid export format")
      }

      // Create and download file
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setExported(true)
      setTimeout(() => {
        setExported(false)
        onClose()
      }, 2000)

    } catch (error) {
      console.error("Export failed:", error)
    } finally {
      setIsExporting(false)
    }
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        transition={{ duration: 0.2 }}
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-md mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-background border border-border rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center space-x-2">
              <Download className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold">Export Chat</h3>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4">
            {/* Chat Info */}
            <div className="space-y-2">
              <h4 className="font-medium">{chat.title}</h4>
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <Calendar className="h-4 w-4" />
                  <span>{formatTimestamp(chat.createdAt)}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <FileText className="h-4 w-4" />
                  <span>{messages.length} messages</span>
                </div>
              </div>
            </div>

            {/* Format Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Export Format</label>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="w-full justify-between">
                    {exportFormat === "txt" && "Plain Text (.txt)"}
                    {exportFormat === "md" && "Markdown (.md)"}
                    {exportFormat === "json" && "JSON (.json)"}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-full">
                  <DropdownMenuItem onClick={() => setExportFormat("txt")}>
                    <FileText className="mr-2 h-4 w-4" />
                    Plain Text (.txt)
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setExportFormat("md")}>
                    <FileText className="mr-2 h-4 w-4" />
                    Markdown (.md)
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setExportFormat("json")}>
                    <FileText className="mr-2 h-4 w-4" />
                    JSON (.json)
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* Preview */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Preview</label>
              <div className="bg-muted rounded-lg p-3 text-sm max-h-32 overflow-y-auto">
                {exportFormat === "txt" && (
                  <pre className="whitespace-pre-wrap text-xs">
                    {generateTextExport().slice(0, 200)}...
                  </pre>
                )}
                {exportFormat === "md" && (
                  <div className="text-xs">
                    {generateMarkdownExport().slice(0, 200)}...
                  </div>
                )}
                {exportFormat === "json" && (
                  <pre className="whitespace-pre-wrap text-xs">
                    {generateJsonExport().slice(0, 200)}...
                  </pre>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-2 p-4 border-t border-border">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              onClick={handleExport} 
              disabled={isExporting}
              className="min-w-[100px]"
            >
              {isExporting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Exporting...
                </>
              ) : exported ? (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Exported!
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </>
              )}
            </Button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

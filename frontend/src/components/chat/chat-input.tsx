"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Send,
  Paperclip,
  X,
  FileText,
  Image,
  Music,
  Video,
  Archive,
  Loader2,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { FileUpload } from "./file-upload"

interface FileAttachment {
  id: string
  name: string
  size: number
  type: string
  file: File
}

interface ChatInputProps {
  onSendMessage: (content: string, files?: File[]) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Ask about your logs..." 
}: ChatInputProps) {
  const [content, setContent] = React.useState("")
  const [attachedFiles, setAttachedFiles] = React.useState<FileAttachment[]>([])
  const [isComposing, setIsComposing] = React.useState(false)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  // Auto-save draft to localStorage
  React.useEffect(() => {
    const draftKey = 'chat-draft'
    const savedDraft = localStorage.getItem(draftKey)
    if (savedDraft && !content) {
      setContent(savedDraft)
    }
  }, [])

  React.useEffect(() => {
    const draftKey = 'chat-draft'
    if (content) {
      localStorage.setItem(draftKey, content)
    } else {
      localStorage.removeItem(draftKey)
    }
  }, [content])

  // Keyboard shortcuts
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K to focus input
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        textareaRef.current?.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value)
    autoResize()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleCompositionStart = () => {
    setIsComposing(true)
  }

  const handleCompositionEnd = () => {
    setIsComposing(false)
  }

  const autoResize = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
    }
  }

  const handleSend = () => {
    if (!content.trim() && attachedFiles.length === 0) return
    if (disabled) return

    const files = attachedFiles.map(f => f.file)
    onSendMessage(content, files)
    setContent("")
    setAttachedFiles([])
    
    // Clear draft from localStorage
    localStorage.removeItem('chat-draft')
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }
  }

  const handleFileUpload = (files: File[]) => {
    const newAttachments: FileAttachment[] = files.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      file,
    }))
    setAttachedFiles(prev => [...prev, ...newAttachments])
  }

  const handleRemoveFile = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) return Image
    if (type.startsWith("video/")) return Video
    if (type.startsWith("audio/")) return Music
    if (type.includes("zip") || type.includes("rar")) return Archive
    return FileText
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const canSend = content.trim().length > 0 || attachedFiles.length > 0

  return (
    <div className="space-y-4">
      {/* Attached Files */}
      <AnimatePresence>
        {attachedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-2"
          >
            <div className="text-sm font-medium text-muted-foreground">
              Attached Files ({attachedFiles.length})
            </div>
            <div className="flex flex-wrap gap-2">
              {attachedFiles.map((file) => {
                const Icon = getFileIcon(file.type)
                return (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="flex items-center space-x-2 bg-muted rounded-lg px-3 py-2 text-sm"
                  >
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <div className="truncate font-medium">{file.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {formatFileSize(file.size)}
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => handleRemoveFile(file.id)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </motion.div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="relative">
        <div className="flex items-end space-x-2 p-4 border border-border rounded-2xl bg-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2">
          {/* File Upload Button */}
          <FileUpload onFileUpload={handleFileUpload} disabled={disabled}>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              disabled={disabled}
            >
              <Paperclip className="h-4 w-4" />
            </Button>
          </FileUpload>

          {/* Text Input */}
          <div className="flex-1 min-w-0">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onCompositionStart={handleCompositionStart}
              onCompositionEnd={handleCompositionEnd}
              placeholder={placeholder}
              disabled={disabled}
              className={cn(
                "w-full resize-none border-0 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-0",
                "min-h-[24px] max-h-[200px]"
              )}
              rows={1}
            />
          </div>

          {/* Send Button */}
          <Button
            onClick={handleSend}
            disabled={!canSend || disabled || isComposing}
            size="icon"
            className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:opacity-50"
          >
            {disabled ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Character Count */}
        {content.length > 0 && (
          <div className="absolute -bottom-6 right-0 text-xs text-muted-foreground">
            {content.length} characters
          </div>
        )}
      </div>

      {/* Keyboard Shortcuts */}
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center space-x-4">
          <span>Press Enter to send, Shift+Enter for new line</span>
        </div>
        <div className="flex items-center space-x-2">
          <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">⌘</kbd>
          <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">K</kbd>
          <span>to focus</span>
        </div>
      </div>
    </div>
  )
}

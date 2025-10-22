"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Upload,
  FileText,
  Image,
  Music,
  Video,
  Archive,
  X,
  CheckCircle,
  AlertCircle,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

interface FileUploadProps {
  onFileUpload: (files: File[]) => void
  disabled?: boolean
  children: React.ReactNode
  maxSize?: number // in bytes
  acceptedTypes?: string[]
}

const MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024 // 10GB
const ACCEPTED_TYPES = [
  "text/plain",
  "text/csv",
  "application/json",
  "application/xml",
  "text/xml",
  "application/log",
  "text/log",
  "application/octet-stream",
  "image/*",
  "video/*",
  "audio/*",
  "application/zip",
  "application/x-rar-compressed",
]

export function FileUpload({
  onFileUpload,
  disabled = false,
  children,
  maxSize = MAX_FILE_SIZE,
  acceptedTypes = ACCEPTED_TYPES,
}: FileUploadProps) {
  const [isDragOver, setIsDragOver] = React.useState(false)
  const [uploadProgress, setUploadProgress] = React.useState<Record<string, number>>({})
  const [uploadStatus, setUploadStatus] = React.useState<Record<string, "uploading" | "success" | "error">>({})
  const fileInputRef = React.useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) {
      setIsDragOver(true)
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    if (disabled) return

    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      handleFiles(files)
    }
  }

  const handleFiles = async (files: File[]) => {
    const validFiles: File[] = []
    const errors: string[] = []

    // Validate files
    for (const file of files) {
      if (file.size > maxSize) {
        errors.push(`${file.name} is too large (max ${formatFileSize(maxSize)})`)
        continue
      }

      if (acceptedTypes.length > 0 && !acceptedTypes.some(type => {
        if (type.endsWith("/*")) {
          return file.type.startsWith(type.slice(0, -1))
        }
        return file.type === type
      })) {
        errors.push(`${file.name} is not a supported file type`)
        continue
      }

      validFiles.push(file)
    }

    if (errors.length > 0) {
      // TODO: Show error toast
      console.error("File upload errors:", errors)
    }

    if (validFiles.length > 0) {
      // Simulate upload progress
      for (const file of validFiles) {
        setUploadStatus(prev => ({ ...prev, [file.name]: "uploading" }))
        
        // Simulate progress
        for (let progress = 0; progress <= 100; progress += 10) {
          setUploadProgress(prev => ({ ...prev, [file.name]: progress }))
          await new Promise(resolve => setTimeout(resolve, 50))
        }
        
        setUploadStatus(prev => ({ ...prev, [file.name]: "success" }))
      }

      // Call the upload handler
      onFileUpload(validFiles)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) return Image
    if (type.startsWith("video/")) return Video
    if (type.startsWith("audio/")) return Music
    if (type.includes("zip") || type.includes("rar")) return Archive
    return FileText
  }

  return (
    <div className="relative">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className="relative"
      >
        {children}
        
        {/* Drag Overlay */}
        <AnimatePresence>
          {isDragOver && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-50 flex items-center justify-center bg-primary/10 border-2 border-dashed border-primary rounded-lg"
            >
              <div className="text-center">
                <Upload className="h-8 w-8 text-primary mx-auto mb-2" />
                <p className="text-sm font-medium text-primary">Drop files here</p>
                <p className="text-xs text-muted-foreground">
                  Max {formatFileSize(maxSize)} per file
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={acceptedTypes.join(",")}
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled}
      />

      {/* Upload Progress */}
      <AnimatePresence>
        {Object.keys(uploadProgress).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-full left-0 right-0 mt-2 bg-background border border-border rounded-lg shadow-lg p-4 z-50"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium">Uploading Files</h4>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => {
                    setUploadProgress({})
                    setUploadStatus({})
                  }}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
              
              {Object.entries(uploadProgress).map(([fileName, progress]) => {
                const status = uploadStatus[fileName]
                const Icon = getFileIcon("text/plain") // Default icon
                
                return (
                  <div key={fileName} className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium truncate flex-1">
                        {fileName}
                      </span>
                      <div className="flex items-center space-x-1">
                        {status === "success" && (
                          <CheckCircle className="h-4 w-4 text-emerald-500" />
                        )}
                        {status === "error" && (
                          <AlertCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="text-xs text-muted-foreground">
                          {progress}%
                        </span>
                      </div>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

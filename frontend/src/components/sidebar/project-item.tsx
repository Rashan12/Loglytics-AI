"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Database, ChevronRight, MoreHorizontal, Edit, Trash2, Share } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface Project {
  id: string
  name: string
  description?: string
  chatCount: number
  lastAccessed: string
}

interface ProjectItemProps {
  project: Project
  collapsed: boolean
  isExpanded: boolean
  onToggle: () => void
  onSelect: () => void
  onEdit: () => void
  onDelete: () => void
}

export function ProjectItem({
  project,
  collapsed,
  isExpanded,
  onToggle,
  onSelect,
  onEdit,
  onDelete,
}: ProjectItemProps) {
  const [isHovered, setIsHovered] = React.useState(false)

  if (collapsed) {
    return (
      <motion.div
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="relative"
      >
        <Button
          variant="ghost"
          size="icon"
          className="w-12 h-12"
          onClick={onSelect}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <Database className="h-5 w-5" />
        </Button>
        
        {/* Tooltip */}
        <AnimatePresence>
          {isHovered && (
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="absolute left-14 top-1/2 -translate-y-1/2 z-50"
            >
              <div className="bg-popover text-popover-foreground px-3 py-2 rounded-lg shadow-lg border text-sm whitespace-nowrap">
                {project.name}
                {project.chatCount > 0 && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {project.chatCount} chats
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    )
  }

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      className="group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-center space-x-2 p-2 rounded-lg hover:bg-accent transition-colors">
        {/* Expand/Collapse Button */}
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 p-0"
          onClick={onToggle}
        >
          <motion.div
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight className="h-4 w-4" />
          </motion.div>
        </Button>

        {/* Project Icon */}
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
            <Database className="h-4 w-4 text-primary" />
          </div>
        </div>

        {/* Project Info */}
        <div className="flex-1 min-w-0" onClick={onSelect}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-foreground truncate">
              {project.name}
            </h3>
            {project.chatCount > 0 && (
              <Badge variant="secondary" size="sm">
                {project.chatCount}
              </Badge>
            )}
          </div>
          {project.description && (
            <p className="text-xs text-muted-foreground truncate">
              {project.description}
            </p>
          )}
          <p className="text-xs text-muted-foreground">
            {new Date(project.lastAccessed).toLocaleDateString()}
          </p>
        </div>

        {/* Options Menu */}
        <AnimatePresence>
          {isHovered && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.2 }}
            >
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={onSelect}>
                    <Database className="mr-2 h-4 w-4" />
                    Open Project
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={onEdit}>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit Project
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Share className="mr-2 h-4 w-4" />
                    Share Project
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    onClick={onDelete}
                    className="text-destructive focus:text-destructive"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete Project
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

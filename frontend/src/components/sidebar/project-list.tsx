"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Database, ChevronRight, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ProjectItem } from "./project-item"
import { ChatList } from "./chat-list"

interface Project {
  id: string
  name: string
  description?: string
  chatCount: number
  lastAccessed: string
  isExpanded?: boolean
  chats: Chat[]
}

interface Chat {
  id: string
  title: string
  lastMessage?: string
  unreadCount: number
  updatedAt: string
}

interface ProjectListProps {
  collapsed: boolean
  projects?: Project[]
  loading?: boolean
  onProjectSelect?: (projectId: string) => void
  onProjectToggle?: (projectId: string) => void
  onProjectEdit?: (projectId: string) => void
  onProjectDelete?: (projectId: string) => void
  onChatSelect?: (projectId: string, chatId: string) => void
}

export function ProjectList({
  collapsed,
  projects = [],
  loading = false,
  onProjectSelect,
  onProjectToggle,
  onProjectEdit,
  onProjectDelete,
  onChatSelect,
}: ProjectListProps) {
  const [expandedProjects, setExpandedProjects] = React.useState<Set<string>>(new Set())

  const handleProjectToggle = (projectId: string) => {
    setExpandedProjects(prev => {
      const newSet = new Set(prev)
      if (newSet.has(projectId)) {
        newSet.delete(projectId)
      } else {
        newSet.add(projectId)
      }
      return newSet
    })
    onProjectToggle?.(projectId)
  }

  if (loading) {
    return (
      <div className="p-4 space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-12 bg-muted rounded-lg" />
          </div>
        ))}
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-4 text-center"
      >
        <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center mx-auto mb-3">
          <Database className="h-6 w-6 text-muted-foreground" />
        </div>
        <p className="text-sm text-muted-foreground">
          {collapsed ? "" : "No projects yet"}
        </p>
        {!collapsed && (
          <p className="text-xs text-muted-foreground mt-1">
            Create your first project to get started
          </p>
        )}
      </motion.div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-4 space-y-1">
        {projects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <ProjectItem
              project={project}
              collapsed={collapsed}
              isExpanded={expandedProjects.has(project.id)}
              onToggle={() => handleProjectToggle(project.id)}
              onSelect={() => onProjectSelect?.(project.id)}
              onEdit={() => onProjectEdit?.(project.id)}
              onDelete={() => onProjectDelete?.(project.id)}
            />
            
            {/* Chats for this project */}
            <AnimatePresence>
              {expandedProjects.has(project.id) && !collapsed && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="ml-6 mt-1"
                >
                  <ChatList
                    chats={project.chats}
                    onChatSelect={(chatId) => onChatSelect?.(project.id, chatId)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

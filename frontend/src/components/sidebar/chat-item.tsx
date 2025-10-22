"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { MessageSquare, MoreHorizontal, Edit, Trash2 } from "lucide-react"
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

interface Chat {
  id: string
  title: string
  lastMessage?: string
  unreadCount: number
  updatedAt: string
}

interface ChatItemProps {
  chat: Chat
  onSelect: () => void
  onEdit: () => void
  onDelete: () => void
}

export function ChatItem({
  chat,
  onSelect,
  onEdit,
  onDelete,
}: ChatItemProps) {
  const [isHovered, setIsHovered] = React.useState(false)

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      className="group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-center space-x-2 p-2 rounded-lg hover:bg-accent transition-colors">
        {/* Chat Icon */}
        <div className="flex-shrink-0">
          <div className="w-6 h-6 bg-blue-500/10 rounded-lg flex items-center justify-center">
            <MessageSquare className="h-3 w-3 text-blue-500" />
          </div>
        </div>

        {/* Chat Info */}
        <div className="flex-1 min-w-0" onClick={onSelect}>
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-medium text-foreground truncate">
              {chat.title}
            </h4>
            {chat.unreadCount > 0 && (
              <Badge variant="destructive" size="sm">
                {chat.unreadCount}
              </Badge>
            )}
          </div>
          {chat.lastMessage && (
            <p className="text-xs text-muted-foreground truncate">
              {chat.lastMessage}
            </p>
          )}
          <p className="text-xs text-muted-foreground">
            {new Date(chat.updatedAt).toLocaleDateString()}
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
                    <MoreHorizontal className="h-3 w-3" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40">
                  <DropdownMenuItem onClick={onSelect}>
                    <MessageSquare className="mr-2 h-3 w-3" />
                    Open Chat
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={onEdit}>
                    <Edit className="mr-2 h-3 w-3" />
                    Rename
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    onClick={onDelete}
                    className="text-destructive focus:text-destructive"
                  >
                    <Trash2 className="mr-2 h-3 w-3" />
                    Delete
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

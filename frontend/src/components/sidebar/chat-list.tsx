"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { ChatItem } from "./chat-item"

interface Chat {
  id: string
  title: string
  lastMessage?: string
  unreadCount: number
  updatedAt: string
}

interface ChatListProps {
  chats: Chat[]
  onChatSelect?: (chatId: string) => void
  onChatEdit?: (chatId: string) => void
  onChatDelete?: (chatId: string) => void
}

export function ChatList({
  chats,
  onChatSelect,
  onChatEdit,
  onChatDelete,
}: ChatListProps) {
  if (chats.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-2 text-center"
      >
        <p className="text-xs text-muted-foreground">
          No chats yet
        </p>
      </motion.div>
    )
  }

  return (
    <div className="space-y-1">
      {chats.map((chat, index) => (
        <motion.div
          key={chat.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2, delay: index * 0.05 }}
        >
          <ChatItem
            chat={chat}
            onSelect={() => onChatSelect?.(chat.id)}
            onEdit={() => onChatEdit?.(chat.id)}
            onDelete={() => onChatDelete?.(chat.id)}
          />
        </motion.div>
      ))}
    </div>
  )
}

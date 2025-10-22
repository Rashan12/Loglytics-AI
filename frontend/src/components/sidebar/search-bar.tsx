"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface SearchBarProps {
  collapsed: boolean
  placeholder?: string
  onSearch?: (query: string) => void
}

export function SearchBar({ 
  collapsed, 
  placeholder = "Search projects and chats...",
  onSearch 
}: SearchBarProps) {
  const [query, setQuery] = React.useState("")

  const handleSearch = (value: string) => {
    setQuery(value)
    onSearch?.(value)
  }

  if (collapsed) {
    return (
      <Button
        variant="ghost"
        size="icon"
        className="w-12 h-12"
        onClick={() => {
          // TODO: Open search modal
        }}
      >
        <Search className="h-4 w-4" />
      </Button>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          className="pl-10 bg-muted/50 border-muted focus:bg-background transition-colors"
        />
      </div>
    </motion.div>
  )
}

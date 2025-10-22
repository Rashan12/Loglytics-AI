"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface NewProjectButtonProps {
  collapsed: boolean
  onClick?: () => void
}

export function NewProjectButton({ collapsed, onClick }: NewProjectButtonProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Button
        onClick={onClick}
        className={cn(
          "w-full h-12 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300",
          collapsed && "px-0 w-12"
        )}
      >
        <Plus className={cn("h-5 w-5", !collapsed && "mr-2")} />
        <motion.span
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: collapsed ? 0 : 1, x: collapsed ? -10 : 0 }}
          transition={{ duration: 0.2 }}
          className={cn(collapsed && "hidden")}
        >
          New Project
        </motion.span>
      </Button>
    </motion.div>
  )
}

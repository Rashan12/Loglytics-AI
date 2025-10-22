"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Github, Mail } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface SocialLoginButtonsProps {
  onGoogleClick?: () => void
  onGithubClick?: () => void
  isLoading?: boolean
  className?: string
}

const socialProviders = [
  {
    name: "Google",
    icon: Mail,
    color: "text-red-500",
    bgColor: "bg-white hover:bg-gray-50",
    borderColor: "border-gray-300",
    onClick: "onGoogleClick",
  },
  {
    name: "GitHub",
    icon: Github,
    color: "text-gray-900",
    bgColor: "bg-gray-900 hover:bg-gray-800 text-white",
    borderColor: "border-gray-900",
    onClick: "onGithubClick",
  },
]

export function SocialLoginButtons({
  onGoogleClick,
  onGithubClick,
  isLoading = false,
  className,
}: SocialLoginButtonsProps) {
  const handleClick = (provider: typeof socialProviders[0]) => {
    if (isLoading) return

    if (provider.name === "Google" && onGoogleClick) {
      onGoogleClick()
    } else if (provider.name === "GitHub" && onGithubClick) {
      onGithubClick()
    }
  }

  return (
    <div className={cn("space-y-3", className)}>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-background text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {socialProviders.map((provider, index) => {
          const Icon = provider.icon
          return (
            <motion.div
              key={provider.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Button
                type="button"
                variant="outline"
                className={cn(
                  "w-full h-11 font-medium transition-all duration-200",
                  provider.bgColor,
                  provider.borderColor,
                  isLoading && "opacity-50 cursor-not-allowed"
                )}
                onClick={() => handleClick(provider)}
                disabled={isLoading}
              >
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center space-x-2"
                >
                  <Icon className={cn("h-4 w-4", provider.color)} />
                  <span>{provider.name}</span>
                </motion.div>
              </Button>
            </motion.div>
          )
        })}
      </div>

      {/* Coming Soon Badge */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="text-center"
      >
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          Social login coming soon
        </span>
      </motion.div>
    </div>
  )
}

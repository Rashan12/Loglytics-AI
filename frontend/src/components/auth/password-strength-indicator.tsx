"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Check, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface PasswordStrengthIndicatorProps {
  password: string
  className?: string
}

interface Requirement {
  label: string
  met: boolean
  test: (password: string) => boolean
}

const requirements: Requirement[] = [
  {
    label: "At least 8 characters",
    met: false,
    test: (password) => password.length >= 8,
  },
  {
    label: "One uppercase letter",
    met: false,
    test: (password) => /[A-Z]/.test(password),
  },
  {
    label: "One lowercase letter",
    met: false,
    test: (password) => /[a-z]/.test(password),
  },
  {
    label: "One number",
    met: false,
    test: (password) => /[0-9]/.test(password),
  },
  {
    label: "One special character",
    met: false,
    test: (password) => /[^A-Za-z0-9]/.test(password),
  },
]

export function PasswordStrengthIndicator({
  password,
  className,
}: PasswordStrengthIndicatorProps) {
  const [strength, setStrength] = React.useState({
    score: 0,
    feedback: "Very weak",
    requirements: requirements.map((req) => ({
      ...req,
      met: req.test(password),
    })),
  })

  React.useEffect(() => {
    const updatedRequirements = requirements.map((req) => ({
      ...req,
      met: req.test(password),
    }))

    const score = updatedRequirements.filter((req) => req.met).length
    const feedback = getPasswordFeedback(score)

    setStrength({
      score,
      feedback,
      requirements: updatedRequirements,
    })
  }, [password])

  if (!password) return null

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("space-y-3", className)}
    >
      {/* Strength Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Password strength</span>
          <span
            className={cn(
              "font-medium",
              strength.score === 0 && "text-red-500",
              strength.score === 1 && "text-red-500",
              strength.score === 2 && "text-orange-500",
              strength.score === 3 && "text-yellow-500",
              strength.score === 4 && "text-blue-500",
              strength.score === 5 && "text-emerald-500"
            )}
          >
            {strength.feedback}
          </span>
        </div>
        <div className="flex space-x-1">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              initial={{ width: 0 }}
              animate={{
                width: strength.score > i ? "100%" : "0%",
              }}
              transition={{ duration: 0.3, delay: i * 0.1 }}
              className={cn(
                "h-2 rounded-full",
                strength.score > i
                  ? strength.score <= 2
                    ? "bg-red-500"
                    : strength.score <= 3
                    ? "bg-orange-500"
                    : strength.score <= 4
                    ? "bg-blue-500"
                    : "bg-emerald-500"
                  : "bg-muted"
              )}
            />
          ))}
        </div>
      </div>

      {/* Requirements List */}
      <div className="space-y-2">
        {strength.requirements.map((requirement, index) => (
          <motion.div
            key={requirement.label}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2, delay: index * 0.05 }}
            className="flex items-center space-x-2 text-sm"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
            >
              {requirement.met ? (
                <Check className="h-4 w-4 text-emerald-500" />
              ) : (
                <X className="h-4 w-4 text-muted-foreground" />
              )}
            </motion.div>
            <span
              className={cn(
                requirement.met
                  ? "text-emerald-600 dark:text-emerald-400"
                  : "text-muted-foreground"
              )}
            >
              {requirement.label}
            </span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

const getPasswordFeedback = (score: number) => {
  if (score === 0) return "Very weak"
  if (score === 1) return "Weak"
  if (score === 2) return "Fair"
  if (score === 3) return "Good"
  if (score === 4) return "Strong"
  if (score === 5) return "Very strong"
  return "Weak"
}

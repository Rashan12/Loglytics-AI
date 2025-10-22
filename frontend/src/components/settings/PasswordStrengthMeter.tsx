"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Check, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface PasswordStrengthMeterProps {
  password: string
  className?: string
}

interface PasswordRequirement {
  label: string
  test: (password: string) => boolean
}

const requirements: PasswordRequirement[] = [
  {
    label: "At least 8 characters",
    test: (password) => password.length >= 8
  },
  {
    label: "Contains uppercase letter",
    test: (password) => /[A-Z]/.test(password)
  },
  {
    label: "Contains lowercase letter",
    test: (password) => /[a-z]/.test(password)
  },
  {
    label: "Contains number",
    test: (password) => /\d/.test(password)
  },
  {
    label: "Contains special character",
    test: (password) => /[!@#$%^&*(),.?":{}|<>]/.test(password)
  }
]

export function PasswordStrengthMeter({ password, className }: PasswordStrengthMeterProps) {
  const [strength, setStrength] = React.useState(0)
  const [strengthLabel, setStrengthLabel] = React.useState("")
  const [strengthColor, setStrengthColor] = React.useState("")

  React.useEffect(() => {
    if (!password) {
      setStrength(0)
      setStrengthLabel("")
      setStrengthColor("")
      return
    }

    const passedRequirements = requirements.filter(req => req.test(password))
    const strengthPercentage = (passedRequirements.length / requirements.length) * 100

    setStrength(strengthPercentage)

    if (strengthPercentage < 40) {
      setStrengthLabel("Weak")
      setStrengthColor("bg-red-500")
    } else if (strengthPercentage < 70) {
      setStrengthLabel("Fair")
      setStrengthColor("bg-yellow-500")
    } else if (strengthPercentage < 90) {
      setStrengthLabel("Good")
      setStrengthColor("bg-blue-500")
    } else {
      setStrengthLabel("Strong")
      setStrengthColor("bg-green-500")
    }
  }, [password])

  if (!password) return null

  return (
    <div className={cn("space-y-2", className)}>
      {/* Strength Bar */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Password strength</span>
          <span className={cn(
            "font-medium",
            strength < 40 && "text-red-500",
            strength >= 40 && strength < 70 && "text-yellow-500",
            strength >= 70 && strength < 90 && "text-blue-500",
            strength >= 90 && "text-green-500"
          )}>
            {strengthLabel}
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <motion.div
            className={cn("h-2 rounded-full transition-colors", strengthColor)}
            initial={{ width: 0 }}
            animate={{ width: `${strength}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Requirements */}
      <div className="space-y-1">
        {requirements.map((requirement, index) => {
          const passed = requirement.test(password)
          return (
            <motion.div
              key={requirement.label}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center gap-2 text-xs"
            >
              <div className={cn(
                "w-3 h-3 rounded-full flex items-center justify-center",
                passed ? "bg-green-500" : "bg-muted"
              )}>
                {passed ? (
                  <Check className="h-2 w-2 text-white" />
                ) : (
                  <X className="h-2 w-2 text-muted-foreground" />
                )}
              </div>
              <span className={cn(
                passed ? "text-green-600" : "text-muted-foreground"
              )}>
                {requirement.label}
              </span>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

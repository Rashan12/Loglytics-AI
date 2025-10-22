"use client"

import * as React from "react"
import { Eye, EyeOff } from "lucide-react"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export interface PasswordInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  showStrength?: boolean
  onStrengthChange?: (strength: { score: number; feedback: string }) => void
}

const PasswordInput = React.forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ className, showStrength = false, onStrengthChange, ...props }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false)
    const [password, setPassword] = React.useState("")

    React.useEffect(() => {
      if (showStrength && onStrengthChange) {
        const strength = validatePasswordStrength(password)
        onStrengthChange(strength)
      }
    }, [password, showStrength, onStrengthChange])

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setPassword(e.target.value)
      if (props.onChange) {
        props.onChange(e)
      }
    }

    return (
      <div className="relative">
        <Input
          type={showPassword ? "text" : "password"}
          className={cn("pr-10", className)}
          ref={ref}
          {...props}
          onChange={handlePasswordChange}
        />
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
          onClick={() => setShowPassword(!showPassword)}
        >
          {showPassword ? (
            <EyeOff className="h-4 w-4 text-muted-foreground" />
          ) : (
            <Eye className="h-4 w-4 text-muted-foreground" />
          )}
          <span className="sr-only">
            {showPassword ? "Hide password" : "Show password"}
          </span>
        </Button>
      </div>
    )
  }
)
PasswordInput.displayName = "PasswordInput"

// Password strength validation (simplified version)
const validatePasswordStrength = (password: string) => {
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  }

  const score = Object.values(requirements).filter(Boolean).length
  const feedback = getPasswordFeedback(score)

  return { score, feedback }
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

export { PasswordInput }

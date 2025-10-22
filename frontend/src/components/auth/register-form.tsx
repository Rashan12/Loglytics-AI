"use client"

import * as React from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { User, Mail, Lock, ArrowRight, Check, Eye, EyeOff } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { SocialLoginButtons } from "./social-login-buttons"
import { PasswordStrengthIndicator } from "./password-strength-indicator"
import { registerSchema, type RegisterFormData } from "@/lib/validation"
import { useAuthStore } from "@/store/auth-store"
import { apiClient, handleApiError } from "@/lib/api"

interface RegisterFormProps {
  onSuccess?: () => void
  className?: string
}

export function RegisterForm({ onSuccess, className }: RegisterFormProps) {
  const { login, setLoading, setError } = useAuthStore()
  const [showPassword, setShowPassword] = React.useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false)
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [passwordStrength, setPasswordStrength] = React.useState({
    score: 0,
    feedback: "Very weak",
  })

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    trigger,
    setValue,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    mode: "onChange",
    reValidateMode: "onChange",
  })

  const password = watch("password", "")
  const confirmPassword = watch("confirm_password", "")
  const termsAccepted = watch("terms_accepted", false)

  React.useEffect(() => {
    if (password) {
      const strength = validatePasswordStrength(password)
      setPasswordStrength(strength)
    }
  }, [password])

  // Re-validate form when confirm password changes
  React.useEffect(() => {
    if (confirmPassword) {
      trigger("confirm_password")
    }
  }, [confirmPassword, trigger])

  // Re-validate form when terms checkbox changes
  React.useEffect(() => {
    trigger("terms_accepted")
  }, [termsAccepted, trigger])

  // Debug form state
  React.useEffect(() => {
    const formData = watch()
    console.log("Form state:", { 
      isValid, 
      termsAccepted, 
      errors, 
      formData,
      hasErrors: Object.keys(errors).length > 0
    })
  }, [isValid, termsAccepted, errors, watch])

  const onSubmit = async (data: RegisterFormData) => {
    try {
      // Trigger validation for all fields
      const isFormValid = await trigger()
      if (!isFormValid) {
        console.log("Form validation failed:", errors)
        return
      }

      setIsSubmitting(true)
      setLoading(true)
      setError(null)

      // FIXED: Remove confirm_password and terms_accepted, only send what backend expects
      const registrationData = {
        email: data.email,
        password: data.password,
        full_name: data.full_name || undefined, // Send undefined if empty, backend will handle
      }

      console.log("Sending registration data:", registrationData) // Debug log

      // FIXED: Changed from "/api/v1/auth/register" to "/auth/register"
      const response = await apiClient.post<{
        access_token: string
        refresh_token: string
        token_type: string
        user: any
      }>("/auth/register", registrationData)

      const { access_token, refresh_token, user } = response.data

      // Store tokens and user data
      login(user, access_token, refresh_token)

      toast.success("Account created!", {
        description: "Welcome to Loglytics AI. Your account has been created successfully.",
      })

      onSuccess?.()
    } catch (error) {
      console.error("Registration error:", error) // Debug log
      const errorMessage = handleApiError(error)
      setError(errorMessage)
      toast.error("Registration failed", {
        description: errorMessage,
      })
    } finally {
      setIsSubmitting(false)
      setLoading(false)
    }
  }

  const handleSocialLogin = (provider: string) => {
    toast.info("Coming soon", {
      description: `${provider} login will be available soon.`,
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={className}
    >
      <div className="glass rounded-2xl p-8 shadow-2xl border border-white/20">
        {/* Header */}
        <div className="text-center space-y-2 mb-8">
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-3xl font-bold text-white"
          >
            Create account
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-white/70"
          >
            Get started with Loglytics AI today
          </motion.p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Full Name Field */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="space-y-2"
          >
            <label htmlFor="full_name" className="text-sm font-medium text-white">
              Full name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
              <Input
                id="full_name"
                type="text"
                placeholder="Enter your full name"
                className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                {...register("full_name")}
              />
            </div>
            {errors.full_name && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-red-400"
              >
                {errors.full_name.message}
              </motion.p>
            )}
          </motion.div>

          {/* Email Field */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="space-y-2"
          >
            <label htmlFor="email" className="text-sm font-medium text-white">
              Email address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                {...register("email")}
              />
            </div>
            {errors.email && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-red-400"
              >
                {errors.email.message}
              </motion.p>
            )}
          </motion.div>

          {/* Password Field */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="space-y-2"
          >
            <label htmlFor="password" className="text-sm font-medium text-white">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Create a password"
                className="pl-10 pr-10 bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                {...register("password")}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 hover:text-white transition-colors"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {errors.password && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-red-400"
              >
                {errors.password.message}
              </motion.p>
            )}
          </motion.div>

          {/* Password Strength Indicator */}
          {password && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              transition={{ duration: 0.3 }}
            >
              <PasswordStrengthIndicator password={password} />
            </motion.div>
          )}

          {/* Confirm Password Field */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="space-y-2"
          >
            <label htmlFor="confirm_password" className="text-sm font-medium text-white">
              Confirm password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
              <Input
                id="confirm_password"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm your password"
                className="pl-10 pr-10 bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                {...register("confirm_password")}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 hover:text-white transition-colors"
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {errors.confirm_password && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-red-400"
              >
                {errors.confirm_password.message}
              </motion.p>
            )}
          </motion.div>

          {/* Terms and Conditions */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="space-y-2"
          >
            <div className="flex items-start space-x-2">
              <Checkbox
                id="terms_accepted"
                className="mt-1 border-white/20 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-500"
                checked={termsAccepted}
                onCheckedChange={(checked) => {
                  // FIXED: Convert checked to boolean (Radix returns boolean | "indeterminate")
                  const value = checked === true
                  setValue("terms_accepted", value, { shouldValidate: true })
                }}
              />
              <label
                htmlFor="terms_accepted"
                className="text-sm text-white/70 cursor-pointer leading-relaxed"
              >
                I agree to the{" "}
                <Link
                  href="/terms"
                  className="text-blue-400 hover:text-blue-300 underline"
                >
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link
                  href="/privacy"
                  className="text-blue-400 hover:text-blue-300 underline"
                >
                  Privacy Policy
                </Link>
              </label>
            </div>
            {errors.terms_accepted && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-red-400"
              >
                {errors.terms_accepted.message}
              </motion.p>
            )}
          </motion.div>

          {/* Submit Button */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <Button
              type="submit"
              disabled={!isValid || isSubmitting}
              className={`w-full h-12 font-semibold rounded-lg shadow-lg transition-all duration-300 ${
                !isValid || isSubmitting
                  ? "bg-gray-500 text-gray-300 cursor-not-allowed opacity-50"
                  : "bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white hover:shadow-xl"
              }`}
            >
              {isSubmitting ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                />
              ) : (
                <>
                  Create account
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
            
            {/* Form validation message */}
            {!isValid && !isSubmitting && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mt-2"
              >
                <p className="text-sm text-amber-400">
                  {Object.keys(errors).length > 0 
                    ? "Please fix the errors above" 
                    : "Please fill in all required fields and accept the terms of service"
                  }
                </p>
              </motion.div>
            )}
          </motion.div>

          {/* Social Login */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.9 }}
          >
            <SocialLoginButtons
              onGoogleClick={() => handleSocialLogin("Google")}
              onGithubClick={() => handleSocialLogin("GitHub")}
              isLoading={isSubmitting}
            />
          </motion.div>

          {/* Sign In Link */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1.0 }}
            className="text-center"
          >
            <p className="text-white/70">
              Already have an account?{" "}
              <Link
                href="/login"
                className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
              >
                Sign in
              </Link>
            </p>
          </motion.div>
        </form>
      </div>
    </motion.div>
  )
}

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
"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form"
import { useAuthStore } from "@/store/auth-store"

export default function ForgotPasswordPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard")
    }
  }, [isAuthenticated, router])

  const handleSuccess = () => {
    // Success is handled within the component
  }

  return <ForgotPasswordForm onSuccess={handleSuccess} />
}

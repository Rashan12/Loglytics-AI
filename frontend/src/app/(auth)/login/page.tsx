"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { LoginForm } from "@/components/auth/login-form"
import { useAuthStore } from "@/store/auth-store"

export default function LoginPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard")
    }
  }, [isAuthenticated, router])

  const handleSuccess = () => {
    router.push("/dashboard")
  }

  return <LoginForm onSuccess={handleSuccess} />
}

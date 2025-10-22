"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { RegisterForm } from "@/components/auth/register-form"
import { useAuthStore } from "@/store/auth-store"

export default function RegisterPage() {
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

  return <RegisterForm onSuccess={handleSuccess} />
}

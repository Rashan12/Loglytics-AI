"use client"

import * as React from "react"

interface AuthLayoutProps {
  children: React.ReactNode
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  // Simple layout wrapper - pages handle their own full design
  return <>{children}</>
}

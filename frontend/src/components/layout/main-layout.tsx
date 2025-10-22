"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Toaster } from "sonner"

import { Sidebar } from "./sidebar"
import { Navbar } from "./navbar"
import { useUIStore } from "@/store/ui-store"

interface MainLayoutProps {
  children: React.ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  const { sidebarMobileOpen, setSidebarMobileOpen } = useUIStore()

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="hidden lg:flex">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarMobileOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 lg:hidden"
          onClick={() => setSidebarMobileOpen(false)}
        >
          <div className="absolute inset-0 bg-black/50" />
        </motion.div>
      )}

      {/* Mobile Sidebar */}
      <motion.div
        initial={{ x: "-100%" }}
        animate={{ x: sidebarMobileOpen ? 0 : "-100%" }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="fixed inset-y-0 left-0 z-50 w-64 lg:hidden"
      >
        <Sidebar />
      </motion.div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar 
          onMenuClick={() => setSidebarMobileOpen(true)}
          showMenuButton={true}
        />
        
        <main className="flex-1 overflow-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="h-full"
          >
            {children}
          </motion.div>
        </main>
      </div>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        expand={true}
        richColors={true}
        closeButton={true}
        duration={5000}
        toastOptions={{
          style: {
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            color: "hsl(var(--card-foreground))",
          },
        }}
      />
    </div>
  )
}

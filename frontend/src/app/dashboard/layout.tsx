"use client"

import * as React from "react"
import { motion } from "framer-motion"
import Sidebar from "@/components/Sidebar"
import TopBar from "@/components/TopBar"
import { Navbar } from "@/components/navbar/navbar"
import { useUIStore } from "@/store/ui-store"
import WebSocketStatus from "@/components/WebSocketStatus"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { sidebarCollapsed, sidebarMobileOpen, setSidebarMobileOpen } = useUIStore()

  return (
    <div className="min-h-screen bg-[#0A0E14] dark:bg-[#0A0E14] light:bg-gray-50">
      {/* Enhanced Sidebar */}
      <div className="hidden lg:block">
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
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
        </motion.div>
      )}

      {/* Mobile Sidebar */}
      <motion.div
        initial={{ x: "-100%" }}
        animate={{ x: sidebarMobileOpen ? 0 : "-100%" }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="fixed inset-y-0 left-0 z-50 w-80 lg:hidden"
      >
        <Sidebar />
      </motion.div>

      {/* Main Content Area with proper margin */}
      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'ml-20' : 'ml-72'}`}>
        <TopBar />
        
        <main className="pt-16 min-h-screen">
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
      
      {/* WebSocket Status Indicator */}
      <WebSocketStatus />
    </div>
  )
}

"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { usePathname, useRouter } from "next/navigation"
import {
  BarChart3,
  Bot,
  ChevronLeft,
  ChevronRight,
  FileText,
  Home,
  Logs,
  Settings,
  Zap,
  Activity,
  Database,
  MessageSquare,
  Search,
  Bell,
  HelpCircle,
  Plus,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useUIStore } from "@/store/ui-store"
import { useAuthStore } from "@/store/auth-store"
import { NewProjectButton } from "./new-project-button"
import { SearchBar } from "./search-bar"
import { ProjectList } from "./project-list"
import { UserProfile } from "./user-profile"

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: Home,
    current: false,
  },
  {
    name: "Analytics",
    href: "/dashboard/analytics",
    icon: BarChart3,
    current: false,
    badge: "New",
  },
  {
    name: "Live Logs",
    href: "/dashboard/live-logs",
    icon: Activity,
    current: false,
    badge: "Beta",
  },
  {
    name: "AI Assistant",
    href: "/dashboard/ai",
    icon: Bot,
    current: false,
  },
  {
    name: "RAG Search",
    href: "/dashboard/search",
    icon: Search,
    current: false,
  },
  {
    name: "Log Files",
    href: "/dashboard/logs",
    icon: FileText,
    current: false,
  },
]

const bottomNavigation = [
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
  {
    name: "Help",
    href: "/dashboard/help",
    icon: HelpCircle,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { sidebarCollapsed, toggleSidebar } = useUIStore()
  const { user } = useAuthStore()

  const handleNewProject = () => {
    router.push('/dashboard/new-project')
  }

  return (
    <motion.aside
      initial={false}
      animate={{
        width: sidebarCollapsed ? 64 : 320,
      }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className={cn(
        "flex h-full flex-col bg-card border-r border-border",
        "transition-all duration-300 ease-in-out"
      )}
    >
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border">
        <AnimatePresence mode="wait">
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-2"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <Zap className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-semibold text-foreground">
                Loglytics AI
              </span>
            </motion.div>
          )}
        </AnimatePresence>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="h-8 w-8"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* New Project Button */}
      <div className="p-4">
        <NewProjectButton collapsed={sidebarCollapsed} onClick={handleNewProject} />
      </div>

      {/* Search Bar */}
      <div className="px-4 pb-4">
        <SearchBar collapsed={sidebarCollapsed} />
      </div>

      {/* Projects & Chats */}
      <div className="flex-1 overflow-hidden">
        <ProjectList collapsed={sidebarCollapsed} />
      </div>

      {/* Divider */}
      <div className="border-t border-border" />

      {/* Navigation */}
      <nav className="p-4">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <motion.div
                key={item.name}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <a
                  href={item.href}
                  className={cn(
                    "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon
                    className={cn(
                      "h-5 w-5 flex-shrink-0",
                      sidebarCollapsed ? "mx-auto" : "mr-3"
                    )}
                  />
                  <AnimatePresence mode="wait">
                    {!sidebarCollapsed && (
                      <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                        className="flex items-center justify-between flex-1"
                      >
                        <span>{item.name}</span>
                        {item.badge && (
                          <Badge
                            variant={item.badge === "New" ? "success" : "info"}
                            size="sm"
                          >
                            {item.badge}
                          </Badge>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </a>
              </motion.div>
            )
          })}
        </div>
      </nav>

      {/* Bottom Navigation */}
      <div className="border-t border-border p-4">
        <div className="space-y-1">
          {bottomNavigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <motion.div
                key={item.name}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <a
                  href={item.href}
                  className={cn(
                    "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon
                    className={cn(
                      "h-5 w-5 flex-shrink-0",
                      sidebarCollapsed ? "mx-auto" : "mr-3"
                    )}
                  />
                  <AnimatePresence mode="wait">
                    {!sidebarCollapsed && (
                      <motion.span
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                      >
                        {item.name}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </a>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* User Profile */}
      <div className="border-t border-border p-4">
        <UserProfile collapsed={sidebarCollapsed} />
      </div>
    </motion.aside>
  )
}
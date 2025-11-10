'use client';

import { usePathname } from 'next/navigation';
import { useUIStore } from '@/store/ui-store';
import { useAuthStore } from '@/store/auth-store';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Activity,
  MessageSquare,
  FolderOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Search,
  FileText,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/dashboard/projects', icon: FolderOpen },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'AI Assistant', href: '/dashboard/ai', icon: MessageSquare },
  { name: 'RAG Search', href: '/dashboard/rag-search', icon: Search },
  { name: 'Log Files', href: '/dashboard/log-files', icon: FileText },
  { name: 'Live Logs', href: '/dashboard/live-logs', icon: Activity },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export default function Sidebar() {
  const { sidebarCollapsed: collapsed, toggleSidebar } = useUIStore();
  const { logout } = useAuthStore();
  const pathname = usePathname();

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="fixed left-0 top-0 h-screen bg-[#12172A] border-r border-[#1E293B] z-50 flex flex-col"
    >
      {/* Logo */}
      <div className="h-20 flex items-center px-6 border-b border-[#1E293B]">
        <AnimatePresence mode="wait">
          {!collapsed ? (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-3 flex-1"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] rounded-xl blur-lg opacity-50" />
                <div className="relative p-2 bg-gradient-to-br from-[#2E9BFF] to-[#8B5CF6] rounded-xl">
                  <Activity className="w-5 h-5 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-lg font-bold text-[#F9FAFB]">Loglytics AI</h1>
                <p className="text-xs text-[#64748B]">v1.0.0</p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="relative mx-auto"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] rounded-xl blur-lg opacity-50" />
              <div className="relative p-2 bg-gradient-to-br from-[#2E9BFF] to-[#8B5CF6] rounded-xl">
                <Activity className="w-5 h-5 text-white" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg bg-[#1E293B] hover:bg-[#334155] text-[#94A3B8] hover:text-[#2E9BFF] transition-all ml-auto"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          const Icon = item.icon;

          return (
            <Link key={item.name} href={item.href}>
              <motion.div
                whileHover={{ x: 4 }}
                transition={{ duration: 0.2 }}
                className={cn(
                  'relative flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200',
                  isActive
                    ? 'bg-gradient-to-r from-[#2E9BFF]/20 to-transparent text-[#2E9BFF]'
                    : 'text-[#94A3B8] hover:text-[#F9FAFB] hover:bg-[#1E293B]'
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-[#2E9BFF] to-[#8B5CF6] rounded-r-full"
                  />
                )}
                
                <Icon className="w-5 h-5 flex-shrink-0" />
                
                <AnimatePresence mode="wait">
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      transition={{ duration: 0.2 }}
                      className="text-sm font-medium whitespace-nowrap"
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="px-4 pb-6 border-t border-[#1E293B] pt-4">
        <button
          onClick={logout}
          className={cn(
            'flex items-center gap-3 px-3 py-3 rounded-xl w-full',
            'text-[#94A3B8] hover:text-[#EF4444] hover:bg-[#1E293B] transition-all duration-200'
          )}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="text-sm font-medium"
              >
                Logout
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { Sun, Moon, User } from 'lucide-react';
import { useUIStore } from '@/store/ui-store';
import { useTheme } from 'next-themes';
import { useAuthStore } from '@/store/auth-store';
import { motion } from 'framer-motion';
import { AlertBell } from '@/components/live-logs/alert-bell';
import { cn } from '@/lib/utils';

export default function TopBar() {
  const { sidebarCollapsed } = useUIStore();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const { user } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  const isDark = mounted && resolvedTheme === 'dark';
  const sidebarWidth = sidebarCollapsed ? 80 : 280;

  return (
    <motion.div
      initial={false}
      animate={{ left: sidebarWidth }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className={cn(
        "fixed top-0 right-0 h-20 z-40 px-8 flex items-center justify-between transition-colors duration-300",
        isDark 
          ? "bg-[#12172A]/80 border-[#2E9BFF]/20" 
          : "bg-white/80 border-gray-200"
      )}
      style={{
        backdropFilter: 'blur(24px)',
        borderBottom: '1px solid',
      }}
    >
      {/* Left side - System Status */}
      <div className="flex items-center gap-4">
        <div className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-full border transition-colors",
          isDark
            ? "bg-[#10B981]/10 border-[#10B981]/30"
            : "bg-green-50 border-green-200"
        )}>
          <div className={cn(
            "w-2 h-2 rounded-full animate-pulse",
            isDark ? "bg-[#10B981]" : "bg-green-500"
          )} />
          <span className={cn(
            "text-xs font-semibold",
            isDark ? "text-[#10B981]" : "text-green-700"
          )}>
            All systems operational
          </span>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        {/* WORKING Notification Bell - from live-logs */}
        <AlertBell />

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className={cn(
            "p-2.5 rounded-xl transition-all",
            isDark
              ? "bg-[#1E293B] hover:bg-[#334155] text-[#94A3B8] hover:text-[#2E9BFF]"
              : "bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-blue-600"
          )}
        >
          {!mounted ? (
            <div className="w-5 h-5" />
          ) : isDark ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>

        {/* Profile */}
        <button className={cn(
          "flex items-center gap-3 pl-3 pr-4 py-2 rounded-xl transition-all",
          isDark
            ? "bg-[#1E293B] hover:bg-[#334155]"
            : "bg-gray-100 hover:bg-gray-200"
        )}>
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#2E9BFF] to-[#8B5CF6] flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="text-left">
            <div className={cn(
              "text-sm font-semibold",
              isDark ? "text-[#F9FAFB]" : "text-gray-900"
            )}>
              {user?.full_name || 'User'}
            </div>
            <div className={cn(
              "text-xs",
              isDark ? "text-[#64748B]" : "text-gray-500"
            )}>
              {user?.email || 'user@example.com'}
            </div>
          </div>
        </button>
      </div>
    </motion.div>
  );
}


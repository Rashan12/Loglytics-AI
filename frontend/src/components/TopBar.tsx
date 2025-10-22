'use client';

import { useState, useEffect } from 'react';
import { Bell, Sun, Moon, Search, Command } from 'lucide-react';
import { useUIStore } from '@/store/ui-store';
import { useTheme } from 'next-themes';

export default function TopBar() {
  const { sidebarCollapsed } = useUIStore();
  const { theme, setTheme } = useTheme();
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(3);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <header className="h-16 bg-[#0F1419] dark:bg-[#0F1419] light:bg-white border-b border-[#30363D] dark:border-[#30363D] light:border-gray-200 sticky top-0 z-40 w-full">
      <div className="h-full px-8 flex items-center justify-between">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-400 dark:text-gray-400 light:text-gray-600">Dashboard</span>
          <span className="text-gray-600 dark:text-gray-600 light:text-gray-400">/</span>
          <span className="text-white dark:text-white light:text-gray-900 font-medium">Analytics</span>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-4">
          {/* Command Palette */}
          <button className="flex items-center gap-2 px-3 py-1.5 bg-[#161B22] dark:bg-[#161B22] light:bg-gray-100 border border-[#30363D] dark:border-[#30363D] light:border-gray-200 rounded-lg text-gray-400 dark:text-gray-400 light:text-gray-600 hover:text-white dark:hover:text-white light:hover:text-gray-900 hover:border-blue-600 transition-colors">
            <Command className="w-4 h-4" />
            <span className="text-sm">Quick Actions</span>
            <kbd className="px-1.5 py-0.5 bg-[#0F1419] dark:bg-[#0F1419] light:bg-gray-200 border border-[#30363D] dark:border-[#30363D] light:border-gray-300 rounded text-xs">⌘K</kbd>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-[#1C2128] dark:hover:bg-[#1C2128] light:hover:bg-gray-100 transition-colors group"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5 text-gray-400 group-hover:text-yellow-500 transition-colors" />
            ) : (
              <Moon className="w-5 h-5 text-gray-600 group-hover:text-blue-500 transition-colors" />
            )}
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg hover:bg-[#1C2128] dark:hover:bg-[#1C2128] light:hover:bg-gray-100 transition-colors"
            >
              <Bell className="w-5 h-5 text-gray-400 dark:text-gray-400 light:text-gray-600" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 top-12 w-96 bg-[#161B22] dark:bg-[#161B22] light:bg-white border border-[#30363D] dark:border-[#30363D] light:border-gray-200 rounded-lg shadow-2xl animate-slideUp">
                <div className="p-4 border-b border-[#30363D] dark:border-[#30363D] light:border-gray-200">
                  <h3 className="text-white dark:text-white light:text-gray-900 font-semibold">Notifications</h3>
                  <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600 mt-1">{unreadCount} unread</p>
                </div>

                <div className="max-h-96 overflow-y-auto">
                  {/* Notification Items */}
                  <div className="p-4 border-b border-[#30363D] dark:border-[#30363D] light:border-gray-200 hover:bg-[#1C2128] dark:hover:bg-[#1C2128] light:hover:bg-gray-50 cursor-pointer transition-colors">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm text-white dark:text-white light:text-gray-900 font-medium">High error rate detected</p>
                        <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600 mt-1">API Gateway showing 15% error rate</p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 light:text-gray-500 mt-2">2 minutes ago</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border-b border-[#30363D] dark:border-[#30363D] light:border-gray-200 hover:bg-[#1C2128] dark:hover:bg-[#1C2128] light:hover:bg-gray-50 cursor-pointer transition-colors">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm text-white dark:text-white light:text-gray-900 font-medium">Log file processed successfully</p>
                        <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600 mt-1">Mobile App logs (2.4 MB)</p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 light:text-gray-500 mt-2">5 minutes ago</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border-b border-[#30363D] dark:border-[#30363D] light:border-gray-200 hover:bg-[#1C2128] dark:hover:bg-[#1C2128] light:hover:bg-gray-50 cursor-pointer transition-colors">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm text-white dark:text-white light:text-gray-900 font-medium">Memory usage above 80%</p>
                        <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-600 mt-1">Database Cluster - Optimize queries</p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 light:text-gray-500 mt-2">2 hours ago</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-3 border-t border-[#30363D] dark:border-[#30363D] light:border-gray-200">
                  <button className="w-full text-center text-sm text-blue-500 hover:text-blue-400 font-medium transition-colors">
                    View All Notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* System Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs text-green-500 font-semibold">All systems operational</span>
          </div>
        </div>
      </div>
    </header>
  );
}

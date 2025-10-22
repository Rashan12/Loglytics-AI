'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useUIStore } from '@/store/ui-store';
import {
  LayoutDashboard,
  BarChart3,
  Activity,
  MessageSquare,
  Search,
  FileText,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Sparkles,
  FolderOpen,
} from 'lucide-react';

const navigationItems = [
  { 
    icon: LayoutDashboard, 
    label: 'Dashboard', 
    path: '/dashboard',
    badge: null 
  },
  { 
    icon: FolderOpen, 
    label: 'Projects', 
    path: '/dashboard/projects',
    badge: null 
  },
  { 
    icon: BarChart3, 
    label: 'Analytics', 
    path: '/dashboard/analytics',
    badge: { text: 'New', color: 'green' }
  },
  { 
    icon: Activity, 
    label: 'Live Logs', 
    path: '/dashboard/live-logs',
    badge: { text: 'Beta', color: 'blue' }
  },
  { 
    icon: MessageSquare, 
    label: 'AI Assistant', 
    path: '/dashboard/ai',
    badge: null
  },
  { 
    icon: Search, 
    label: 'RAG Search', 
    path: '/dashboard/search',
    badge: null
  },
  { 
    icon: FileText, 
    label: 'Log Files', 
    path: '/dashboard/logs',
    badge: null
  },
];

const bottomNavigationItems = [
  { icon: Settings, label: 'Settings', path: '/dashboard/settings' },
  { icon: HelpCircle, label: 'Help', path: '/dashboard/help' },
];

export default function Sidebar() {
  const { sidebarCollapsed: collapsed, toggleSidebar } = useUIStore();
  const router = useRouter();
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  return (
    <aside
      className={`
        fixed left-0 top-0 h-screen
        bg-[#0F1419] border-r border-[#30363D]
        transition-all duration-300 ease-in-out
        ${collapsed ? 'w-20' : 'w-72'}
        flex flex-col
        z-50
      `}
    >
      {/* Logo & Brand */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-[#30363D]">
        {!collapsed && (
          <div className="flex items-center gap-3 animate-fadeIn">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">Loglytics AI</h1>
              <p className="text-xs text-gray-400">Intelligent Analytics</p>
            </div>
          </div>
        )}
        
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-[#1C2128] transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronLeft className="w-5 h-5 text-gray-400" />
          )}
        </button>
      </div>

      {/* Search Bar (when expanded) */}
      {!collapsed && (
        <div className="px-4 py-4 animate-fadeIn">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs, projects..."
              className="w-full pl-10 pr-4 py-2 bg-[#161B22] border border-[#30363D] rounded-lg text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-600 transition-colors"
            />
          </div>
        </div>
      )}

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigationItems.map((item) => (
          <button
            key={item.path}
            onClick={() => router.push(item.path)}
            className={`
              w-full flex items-center gap-3 px-3 py-3 rounded-lg
              transition-all duration-200
              ${isActive(item.path)
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-600/20'
                : 'text-gray-400 hover:bg-[#1C2128] hover:text-white'
              }
              ${collapsed ? 'justify-center' : ''}
            `}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && (
              <>
                <span className="flex-1 text-left font-medium text-sm">
                  {item.label}
                </span>
                {item.badge && (
                  <span className={`
                    px-2 py-0.5 rounded-full text-xs font-semibold
                    ${item.badge.color === 'green' 
                      ? 'bg-green-500/10 text-green-500 border border-green-500/30'
                      : 'bg-blue-500/10 text-blue-500 border border-blue-500/30'
                    }
                  `}>
                    {item.badge.text}
                  </span>
                )}
              </>
            )}
          </button>
        ))}
      </nav>

      {/* Bottom Navigation */}
      <div className="px-3 py-4 space-y-1 border-t border-[#30363D]">
        {bottomNavigationItems.map((item) => (
          <button
            key={item.path}
            onClick={() => router.push(item.path)}
            className={`
              w-full flex items-center gap-3 px-3 py-3 rounded-lg
              transition-all duration-200
              ${isActive(item.path)
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                : 'text-gray-400 hover:bg-[#1C2128] hover:text-white'
              }
              ${collapsed ? 'justify-center' : ''}
            `}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && (
              <span className="flex-1 text-left font-medium text-sm">
                {item.label}
              </span>
            )}
          </button>
        ))}
        
        <button
          onClick={handleLogout}
          className={`
            w-full flex items-center gap-3 px-3 py-3 rounded-lg
            text-red-400 hover:bg-red-500/10 hover:text-red-300
            transition-all duration-200
            ${collapsed ? 'justify-center' : ''}
          `}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!collapsed && (
            <span className="flex-1 text-left font-medium text-sm">
              Logout
            </span>
          )}
        </button>
      </div>

      {/* User Profile (when expanded) */}
      {!collapsed && (
        <div className="px-3 py-4 border-t border-[#30363D] animate-fadeIn">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#1C2128] cursor-pointer transition-colors">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white font-semibold">
              R
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">Rashan Dissanayaka</p>
              <p className="text-xs text-gray-400 truncate">Free Plan</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

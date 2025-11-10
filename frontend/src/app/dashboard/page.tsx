'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';
import {
  FolderOpen,
  Activity,
  AlertTriangle,
  TrendingUp,
  Plus,
  MessageSquare,
  Upload,
  Zap,
  CheckCircle,
} from 'lucide-react';
import { StatCard } from '@/components/dashboard/stat-card';
import { GradientButton } from '@/components/ui/gradient-button';
import { cn } from '@/lib/utils';

export default function DashboardPage() {
  const router = useRouter();
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalLogs: 0,
    errorRate: 0,
    activeProjects: 0,
    aiInsights: 0
  });
  const [projects, setProjects] = useState<any[]>([]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';

  useEffect(() => {
    let isMounted = true;
    
    const loadDashboard = async () => {
      try {
        const token = localStorage.getItem('access_token');
        
        if (!token) {
          return;
        }
        
        console.log('📊 Loading dashboard data');
        
        // Load dashboard stats
        const statsResponse = await fetch('http://localhost:8000/api/v1/analytics/dashboard', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!isMounted) return;
        
        if (statsResponse.ok) {
          const data = await statsResponse.json();
          setStats({
            totalLogs: data.total_logs || 0,
            errorRate: data.error_rate || 0,
            activeProjects: data.active_projects || 0,
            aiInsights: data.ai_insights || 0
          });
          console.log('✅ Dashboard loaded');
        } else {
          console.log('Using default values (endpoint may not exist yet)');
        }

        // Load projects
        try {
          const projectsResponse = await fetch('http://localhost:8000/api/v1/projects', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (projectsResponse.ok) {
            const projectsData = await projectsResponse.json();
            if (projectsData.projects && Array.isArray(projectsData.projects)) {
              setProjects(projectsData.projects);
            }
          }
        } catch (err) {
          console.log('Projects load failed, continuing without projects');
        }
        
      } catch (error) {
        console.error('Dashboard load error:', error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    loadDashboard();
    
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className={cn(
        'min-h-screen transition-colors duration-300',
        isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50'
      )}>
        <motion.main
          initial={false}
          animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
          transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          className="pt-20"
        >
          <div className="p-8 max-w-[1800px] mx-auto">
            <div className="animate-pulse">
              <div className={cn(
                "h-8 rounded w-48 mb-8",
                isDark ? "bg-[rgba(26,31,58,0.6)]" : "bg-gray-200"
              )}></div>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-8">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className={cn(
                    "h-40 rounded-2xl",
                    isDark ? "bg-[rgba(26,31,58,0.6)]" : "bg-gray-100"
                  )}></div>
                ))}
              </div>
            </div>
          </div>
        </motion.main>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Projects',
      value: projects.length,
      icon: FolderOpen,
      trend: '12%',
      trendUp: true,
      gradient: 'bg-gradient-to-br from-[#2E9BFF]/20 to-[#00D9FF]/20',
    },
    {
      title: 'Active Projects',
      value: projects.filter((p: any) => p.is_active !== false).length,
      icon: Activity,
      trend: '8%',
      trendUp: true,
      gradient: 'bg-gradient-to-br from-[#10B981]/20 to-[#00D9FF]/20',
    },
    {
      title: 'Error Rate',
      value: '0.0%',
      icon: AlertTriangle,
      trend: '0.3%',
      trendUp: false,
      gradient: 'bg-gradient-to-br from-[#F59E0B]/20 to-[#EF4444]/20',
    },
    {
      title: 'AI Insights',
      value: '0',
      icon: TrendingUp,
      trend: '24%',
      trendUp: true,
      gradient: 'bg-gradient-to-br from-[#8B5CF6]/20 to-[#A78BFA]/20',
    },
  ];

  const containerClassName = cn(
    'min-h-screen transition-colors duration-300',
    isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50'
  );

  return (
    <div className={containerClassName}>
      {/* Main Content - Adjusts with sidebar */}
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20"
      >
        <div className="p-8 max-w-[1800px] mx-auto">
          {/* Hero Section - LARGER */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className={cn(
              'relative mb-8 p-8 rounded-2xl border overflow-hidden transition-colors',
              isDark
                ? 'bg-gradient-to-r from-[rgba(46,155,255,0.1)] to-transparent border-[#2E9BFF]/20'
                : 'bg-gradient-to-r from-blue-50 to-transparent border-blue-200'
            )}
          >
            {/* Grid Pattern */}
            <div
              className="absolute inset-0 opacity-10"
              style={{
                backgroundImage: `
                  linear-gradient(rgba(46,155,255,0.3) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(46,155,255,0.3) 1px, transparent 1px)
                `,
                backgroundSize: '32px 32px',
              }}
            />

            <div className="relative flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
              <div className="flex-1">
                <h1 className={cn(
                  'text-3xl font-bold mb-2',
                  isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                )}>
                  Welcome back! 👋
                </h1>
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  {new Date().toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center gap-3">
                <GradientButton
                  onClick={() => router.push('/dashboard/projects/new')}
                  className="flex items-center gap-2 px-4 py-2.5"
                >
                  <Plus className="w-4 h-4" />
                  New Project
                </GradientButton>
                <GradientButton
                  variant="secondary"
                  onClick={() => router.push('/dashboard/ai')}
                  className="flex items-center gap-2 px-4 py-2.5"
                >
                  <MessageSquare className="w-4 h-4" />
                  AI Chat
                </GradientButton>
                <GradientButton
                  variant="secondary"
                  className="flex items-center gap-2 px-4 py-2.5"
                >
                  <Upload className="w-4 h-4" />
                  Upload
                </GradientButton>
              </div>
            </div>
          </motion.div>

          {/* Stats Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8"
          >
            {statCards.map((stat, index) => (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 + index * 0.1 }}
              >
                <StatCard {...stat} isDark={isDark} />
              </motion.div>
            ))}
          </motion.div>

          {/* Main Content Grid - NO CHARTS */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Recent Projects */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="xl:col-span-2"
            >
              <div className={cn(
                'p-6 rounded-2xl border transition-colors',
                isDark
                  ? 'bg-[#1A1F3A]/60 backdrop-blur-xl border-[#2E3A5C]/50'
                  : 'bg-white border-gray-200 shadow-sm'
              )}>
                <div className="flex items-center justify-between mb-6">
                  <h2 className={cn(
                    'text-xl font-bold',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    Recent Projects
                  </h2>
                  <button
                    onClick={() => router.push('/dashboard/projects')}
                    className="text-sm text-[#2E9BFF] hover:text-[#00D9FF] font-semibold transition-colors"
                  >
                    View all →
                  </button>
                </div>

                {projects.length === 0 ? (
                  <div className="text-center py-12">
                    <FolderOpen className={cn(
                      'w-16 h-16 mx-auto mb-4 opacity-50',
                      isDark ? 'text-[#64748B]' : 'text-gray-400'
                    )} />
                    <p className={cn(
                      'text-base mb-4',
                      isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                    )}>
                      No projects yet
                    </p>
                    <GradientButton onClick={() => router.push('/dashboard/projects/new')}>
                      <Plus className="w-4 h-4 mr-2" />
                      Create your first project
                    </GradientButton>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {projects.slice(0, 5).map((project) => (
                      <motion.div
                        key={project.id}
                        whileHover={{ x: 4 }}
                        onClick={() => router.push(`/dashboard/projects/${project.id}`)}
                        className={cn(
                          'p-4 rounded-xl border cursor-pointer transition-all group',
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#1E293B] hover:border-[#2E9BFF]/50'
                            : 'bg-gray-50 border-gray-200 hover:border-blue-300 hover:shadow-md'
                        )}
                      >
                        <div className="flex items-center gap-4">
                          <div className="p-3 rounded-xl bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20 border border-[#2E9BFF]/30">
                            <FolderOpen className="w-5 h-5 text-[#2E9BFF]" />
                          </div>
                          <div className="flex-1">
                            <h3 className={cn(
                              'text-base font-semibold mb-1 group-hover:text-[#2E9BFF] transition-colors',
                              isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                            )}>
                              {project.name}
                            </h3>
                            <p className={cn(
                              'text-sm',
                              isDark ? 'text-[#64748B]' : 'text-gray-500'
                            )}>
                              {project.log_files_count || 0} files • Updated {new Date(project.updated_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="px-3 py-1 text-xs font-semibold rounded-full bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50">
                              Active
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>

            {/* Live Alerts Feed */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <div className={cn(
                'p-6 rounded-2xl border transition-colors',
                isDark
                  ? 'bg-[#1A1F3A]/60 backdrop-blur-xl border-[#2E3A5C]/50'
                  : 'bg-white border-gray-200 shadow-sm'
              )}>
                <div className="flex items-center justify-between mb-6">
                  <h2 className={cn(
                    'text-xl font-bold',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    Live Alerts
                  </h2>
                  <div className="flex items-center gap-2 px-2 py-1 rounded-full bg-[#2E9BFF]/20">
                    <div className="w-2 h-2 rounded-full bg-[#2E9BFF] animate-pulse" />
                    <span className="text-xs font-semibold text-[#2E9BFF]">Live</span>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    {
                      type: 'error',
                      title: 'High error rate detected',
                      source: 'production-api',
                      time: '2 min ago',
                      color: 'red',
                    },
                    {
                      type: 'warning',
                      title: 'Memory usage spike',
                      source: 'database-primary',
                      time: '5 min ago',
                      color: 'yellow',
                    },
                    {
                      type: 'info',
                      title: 'Deployment completed',
                      source: 'ci-cd-pipeline',
                      time: '12 min ago',
                      color: 'blue',
                    },
                  ].map((alert, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                      className={cn(
                        'p-4 rounded-xl border cursor-pointer transition-all',
                        isDark
                          ? 'bg-[#0D1117]/60 border-[#1E293B] hover:border-[#2E9BFF]/50'
                          : 'bg-gray-50 border-gray-200 hover:border-blue-300'
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${
                          alert.color === 'red' ? 'bg-[#EF4444]/20 text-[#EF4444]' :
                          alert.color === 'yellow' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' :
                          'bg-[#2E9BFF]/20 text-[#2E9BFF]'
                        }`}>
                          {alert.color === 'red' ? <AlertTriangle className="w-4 h-4" /> :
                           alert.color === 'yellow' ? <Zap className="w-4 h-4" /> :
                           <CheckCircle className="w-4 h-4" />}
                        </div>
                        <div className="flex-1">
                          <h4 className={cn(
                            'text-sm font-semibold mb-1',
                            isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                          )}>
                            {alert.title}
                          </h4>
                          <p className={cn(
                            'text-xs',
                            isDark ? 'text-[#64748B]' : 'text-gray-500'
                          )}>
                            {alert.source} • {alert.time}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <button className="w-full mt-4 px-4 py-3 text-sm font-semibold text-[#2E9BFF] hover:text-[#00D9FF] bg-[#2E9BFF]/10 hover:bg-[#2E9BFF]/20 rounded-xl transition-all">
                  View all alerts
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.main>
    </div>
  );
}

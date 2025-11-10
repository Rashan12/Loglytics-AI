'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';
import {
  Calendar,
  Download,
  Filter,
  TrendingUp,
  TrendingDown,
  Search,
  FileText,
  BarChart3,
  Clock,
  AlertTriangle,
  Activity,
  Loader2,
  X,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { API_V1 } from '@/config/api';

interface LogFile {
  id: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_status: string;
  created_at: string;
  entry_count?: number;
  analysis_count?: number;
}

export default function AnalyticsPage() {
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [timeRange, setTimeRange] = useState('24h');
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [logFiles, setLogFiles] = useState<LogFile[]>([]);
  const [selectedLogFile, setSelectedLogFile] = useState<string | null>(null);
  const [showFileSelector, setShowFileSelector] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';

  useEffect(() => {
    fetchLogFiles();
  }, []);

  useEffect(() => {
    const loadingTimeout = setTimeout(() => {
      console.warn('Analytics loading timeout - showing empty state');
      setLoading(false);
    }, 10000);
    
    fetchAnalytics().finally(() => {
      clearTimeout(loadingTimeout);
    });
  }, [timeRange, selectedLogFile]);

  const fetchLogFiles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await fetch(`${API_V1}/logs/files`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        console.error('❌ Authentication failed. Token may be expired.');
        return;
      }

      if (response.ok) {
        const data = await response.json();
        // Backend returns { files: [...], total: ... }
        const filesData = Array.isArray(data) ? data : (data.files || data.items || []);
        setLogFiles(filesData);
      } else if (response.status === 404) {
        // Endpoint not found - silently handle, no console output
        setLogFiles([]);
      } else {
        // Only log non-404 errors
        if (response.status !== 401) {
          console.warn('⚠️ Failed to fetch log files:', response.status);
        }
        setLogFiles([]);
      }
    } catch (error) {
      // Silently handle all network errors - no console output
      setLogFiles([]);
    }
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      const params = new URLSearchParams({
        time_range: timeRange,
        ...(selectedLogFile && { log_file_id: selectedLogFile }),
      });

      const response = await fetch(`${API_V1}/analytics/dashboard?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      } else {
        console.error('Failed to fetch analytics data');
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const params = new URLSearchParams({
        time_range: timeRange,
        ...(selectedLogFile && { log_file_id: selectedLogFile }),
      });

      const response = await fetch(`${API_V1}/analytics/dashboard?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-${timeRange}-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error exporting analytics:', error);
    }
  };

  const filteredLogFiles = logFiles.filter(file =>
    file.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const hasData = analyticsData && Object.keys(analyticsData).length > 0;

  // Calculate derived metrics
  const totalLogs = analyticsData?.total_logs || 0;
  const errorRate = analyticsData?.error_rate || 0;
  const avgResponseTime = analyticsData?.avgResponseTime || 'N/A';
  const activeServices = analyticsData?.activeServices || analyticsData?.active_projects || 0;

  return (
    <motion.main
      initial={false}
      animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="pt-20 min-h-screen"
    >
      <div className={cn(
        'px-8 py-6',
        isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50'
      )}>
        <div className="max-w-[1800px] mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] rounded-xl blur-lg opacity-50" />
                    <div className="relative p-2.5 bg-gradient-to-br from-[#2E9BFF] to-[#8B5CF6] rounded-xl">
                      <BarChart3 className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <h1 className={cn(
                    'text-3xl font-bold',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    Analytics Dashboard
                  </h1>
                </div>
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Comprehensive insights into your log data and system performance
                </p>
              </div>
            </div>
          </motion.div>

          {/* Controls */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-8"
          >
            <div className={cn(
              'p-6 rounded-2xl border backdrop-blur-xl',
              isDark
                ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                : 'bg-white/80 border-gray-200 shadow-lg'
            )}>
              <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
                <div className="flex flex-wrap gap-4 items-center">
                  {/* Time Range Selector */}
                  <div className="relative">
                    <select
                      value={timeRange}
                      onChange={(e) => setTimeRange(e.target.value)}
                      className={cn(
                        'px-4 py-2.5 pr-10 rounded-xl border transition-all focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20 appearance-none cursor-pointer',
                        isDark
                          ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] focus:border-[#2E9BFF]'
                          : 'bg-white border-gray-200 text-gray-900 focus:border-blue-500'
                      )}
                    >
                      <option value="1h">Last Hour</option>
                      <option value="24h">Last 24 Hours</option>
                      <option value="7d">Last 7 Days</option>
                      <option value="30d">Last 30 Days</option>
                    </select>
                    <Clock className={cn(
                      'absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none',
                      isDark ? 'text-[#64748B]' : 'text-gray-400'
                    )} />
                  </div>

                  {/* Log File Selector */}
                  <div className="relative">
                    <button
                      onClick={() => setShowFileSelector(!showFileSelector)}
                      className={cn(
                        'px-4 py-2.5 rounded-xl border transition-all flex items-center gap-2',
                        isDark
                          ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] hover:border-[#2E9BFF]/50 hover:bg-[#1A1F3A]/80'
                          : 'bg-white border-gray-200 text-gray-900 hover:border-blue-300 hover:bg-gray-50'
                      )}
                    >
                      <FileText className="w-4 h-4" />
                      <span className="text-sm font-medium">
                        {selectedLogFile 
                          ? logFiles.find(f => f.id === selectedLogFile)?.filename || 'Change File'
                          : 'Select Log File'}
                      </span>
                      <Filter className="w-4 h-4" />
                    </button>

                    <AnimatePresence>
                      {showFileSelector && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          transition={{ duration: 0.2 }}
                          className={cn(
                            'absolute top-full left-0 mt-2 w-80 rounded-xl border shadow-2xl z-50',
                            isDark
                              ? 'bg-[#1A1F3A] border-[#2E3A5C]/50'
                              : 'bg-white border-gray-200'
                          )}
                        >
                          <div className={cn(
                            'p-4 border-b',
                            isDark ? 'border-[#2E3A5C]/30' : 'border-gray-200'
                          )}>
                            <div className="relative">
                              <Search className={cn(
                                'absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4',
                                isDark ? 'text-[#64748B]' : 'text-gray-400'
                              )} />
                              <input
                                type="text"
                                placeholder="Search log files..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className={cn(
                                  'w-full pl-10 pr-4 py-2 rounded-lg border transition-all focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20',
                                  isDark
                                    ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                                    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                                )}
                              />
                            </div>
                          </div>
                          <div className="max-h-60 overflow-y-auto">
                            <button
                              onClick={() => {
                                setSelectedLogFile(null);
                                setShowFileSelector(false);
                              }}
                              className={cn(
                                'w-full text-left px-4 py-3 transition-all',
                                !selectedLogFile
                                  ? isDark
                                    ? 'bg-[#2E9BFF]/10 text-[#2E9BFF] border-l-2 border-[#2E9BFF]'
                                    : 'bg-blue-50 text-blue-600 border-l-2 border-blue-500'
                                  : isDark
                                  ? 'text-[#F9FAFB] hover:bg-[#1E293B]'
                                  : 'text-gray-900 hover:bg-gray-50'
                              )}
                            >
                              <div className="flex items-center gap-2">
                                <CheckCircle2 className={cn(
                                  'w-4 h-4',
                                  !selectedLogFile ? 'opacity-100' : 'opacity-0'
                                )} />
                                <span className="font-medium">All Log Files</span>
                              </div>
                            </button>
                            {filteredLogFiles.map((file) => (
                              <button
                                key={file.id}
                                onClick={() => {
                                  setSelectedLogFile(file.id);
                                  setShowFileSelector(false);
                                }}
                                className={cn(
                                  'w-full text-left px-4 py-3 transition-all border-t',
                                  selectedLogFile === file.id
                                    ? isDark
                                      ? 'bg-[#2E9BFF]/10 text-[#2E9BFF] border-l-2 border-[#2E9BFF]'
                                      : 'bg-blue-50 text-blue-600 border-l-2 border-blue-500'
                                    : isDark
                                    ? 'text-[#F9FAFB] hover:bg-[#1E293B] border-[#2E3A5C]/30'
                                    : 'text-gray-900 hover:bg-gray-50 border-gray-200'
                                )}
                              >
                                <div className="flex items-center gap-2 mb-1">
                                  <CheckCircle2 className={cn(
                                    'w-4 h-4',
                                    selectedLogFile === file.id ? 'opacity-100' : 'opacity-0'
                                  )} />
                                  <span className="font-medium text-sm">{file.filename}</span>
                                </div>
                                <div className={cn(
                                  'text-xs ml-6',
                                  isDark ? 'text-[#64748B]' : 'text-gray-500'
                                )}>
                                  {file.entry_count || 0} entries • {file.file_type}
                                </div>
                              </button>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>

                {/* Export Button */}
                <button
                  onClick={handleExport}
                  className={cn(
                    'px-4 py-2.5 rounded-xl font-semibold text-sm transition-all flex items-center gap-2',
                    'bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] text-white',
                    'shadow-[0_4px_20px_rgba(46,155,255,0.4)]',
                    'hover:scale-[1.02] hover:shadow-[0_8px_32px_rgba(46,155,255,0.6)]',
                    'active:scale-[0.98]'
                  )}
                >
                  <Download className="w-4 h-4" />
                  Export Data
                </button>
              </div>
            </div>
          </motion.div>

          {/* Loading State */}
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center py-20"
            >
              <div className="text-center">
                <div className={cn(
                  "w-16 h-16 border-4 rounded-full animate-spin mx-auto mb-4",
                  isDark ? "border-[#2E9BFF] border-t-transparent" : "border-blue-600 border-t-transparent"
                )} />
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Loading analytics data...
                </p>
              </div>
            </motion.div>
          )}

          {/* Empty State */}
          {!loading && !hasData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-center py-20"
            >
              <div className={cn(
                'p-12 rounded-2xl border text-center max-w-md',
                isDark
                  ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                  : 'bg-white border-gray-200 shadow-lg'
              )}>
                <div className="relative mx-auto w-20 h-20 mb-6">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20 rounded-2xl blur-xl" />
                  <TrendingUp className={cn(
                    'w-12 h-12 relative mx-auto',
                    isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                  )} />
                </div>
                <h3 className={cn(
                  'text-xl font-semibold mb-2',
                  isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                )}>
                  No Analytics Data
                </h3>
                <p className={cn(
                  'text-base mb-6',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Upload some log files to start seeing analytics insights.
                </p>
                <button
                  onClick={() => window.location.href = '/dashboard/log-files'}
                  className={cn(
                    'px-6 py-3 rounded-xl font-semibold text-sm transition-all',
                    'bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] text-white',
                    'shadow-[0_4px_20px_rgba(46,155,255,0.4)]',
                    'hover:scale-[1.02] hover:shadow-[0_8px_32px_rgba(46,155,255,0.6)]'
                  )}
                >
                  Upload Log Files
                </button>
              </div>
            </motion.div>
          )}

          {/* Analytics Content */}
          {!loading && hasData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="space-y-6"
            >
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Total Logs Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  className={cn(
                    'p-6 rounded-2xl border backdrop-blur-xl relative overflow-hidden',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                      : 'bg-white/80 border-gray-200 shadow-lg'
                  )}
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-[#2E9BFF]/10 to-transparent rounded-full blur-2xl" />
                  <div className="relative flex items-center justify-between">
                    <div>
                      <p className={cn(
                        'text-sm font-medium mb-2',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )}>
                        Total Logs
                      </p>
                      <p className={cn(
                        'text-3xl font-bold',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        {totalLogs.toLocaleString()}
                      </p>
                    </div>
                    <div className={cn(
                      'p-3 rounded-xl',
                      isDark ? 'bg-[#2E9BFF]/10' : 'bg-blue-50'
                    )}>
                      <FileText className={cn(
                        'w-6 h-6',
                        isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                      )} />
                    </div>
                  </div>
                </motion.div>

                {/* Error Rate Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 }}
                  className={cn(
                    'p-6 rounded-2xl border backdrop-blur-xl relative overflow-hidden',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                      : 'bg-white/80 border-gray-200 shadow-lg'
                  )}
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-[#EF4444]/10 to-transparent rounded-full blur-2xl" />
                  <div className="relative flex items-center justify-between">
                    <div>
                      <p className={cn(
                        'text-sm font-medium mb-2',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )}>
                        Error Rate
                      </p>
                      <p className={cn(
                        'text-3xl font-bold',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        {typeof errorRate === 'number' ? `${errorRate.toFixed(1)}%` : '0%'}
                      </p>
                    </div>
                    <div className={cn(
                      'p-3 rounded-xl',
                      isDark ? 'bg-[#EF4444]/10' : 'bg-red-50'
                    )}>
                      <TrendingDown className={cn(
                        'w-6 h-6',
                        isDark ? 'text-[#EF4444]' : 'text-red-600'
                      )} />
                    </div>
                  </div>
                </motion.div>

                {/* Avg Response Time Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.5 }}
                  className={cn(
                    'p-6 rounded-2xl border backdrop-blur-xl relative overflow-hidden',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                      : 'bg-white/80 border-gray-200 shadow-lg'
                  )}
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-[#10B981]/10 to-transparent rounded-full blur-2xl" />
                  <div className="relative flex items-center justify-between">
                    <div>
                      <p className={cn(
                        'text-sm font-medium mb-2',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )}>
                        Avg Response Time
                      </p>
                      <p className={cn(
                        'text-3xl font-bold',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        {typeof avgResponseTime === 'number' ? `${avgResponseTime}ms` : avgResponseTime}
                      </p>
                    </div>
                    <div className={cn(
                      'p-3 rounded-xl',
                      isDark ? 'bg-[#10B981]/10' : 'bg-green-50'
                    )}>
                      <TrendingUp className={cn(
                        'w-6 h-6',
                        isDark ? 'text-[#10B981]' : 'text-green-600'
                      )} />
                    </div>
                  </div>
                </motion.div>

                {/* Active Services Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.6 }}
                  className={cn(
                    'p-6 rounded-2xl border backdrop-blur-xl relative overflow-hidden',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                      : 'bg-white/80 border-gray-200 shadow-lg'
                  )}
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-[#8B5CF6]/10 to-transparent rounded-full blur-2xl" />
                  <div className="relative flex items-center justify-between">
                    <div>
                      <p className={cn(
                        'text-sm font-medium mb-2',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )}>
                        Active Services
                      </p>
                      <p className={cn(
                        'text-3xl font-bold',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        {activeServices}
                      </p>
                    </div>
                    <div className={cn(
                      'p-3 rounded-xl',
                      isDark ? 'bg-[#8B5CF6]/10' : 'bg-purple-50'
                    )}>
                      <Activity className={cn(
                        'w-6 h-6',
                        isDark ? 'text-[#8B5CF6]' : 'text-purple-600'
                      )} />
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* Additional Analytics Content */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 }}
                className={cn(
                  'p-6 rounded-2xl border backdrop-blur-xl',
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white/80 border-gray-200 shadow-lg'
                )}
              >
                <h3 className={cn(
                  'text-lg font-semibold mb-4',
                  isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                )}>
                  Analytics Details
                </h3>
                <div className={cn(
                  'space-y-2 text-sm',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>Time Range: <strong className={isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}>{timeRange}</strong></span>
                  </div>
                  {selectedLogFile && (
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      <span>Selected File: <strong className={isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}>{logFiles.find(f => f.id === selectedLogFile)?.filename}</strong></span>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" />
                    <span>Data Points: <strong className={isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}>{Object.keys(analyticsData).length}</strong></span>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.main>
  );
}
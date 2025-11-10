'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Activity,
  Pause,
  Play,
  Download,
  Trash2,
  Search,
  Wifi,
  WifiOff,
  AlertTriangle,
  Info,
  AlertCircle,
  CheckCircle,
  Zap,
  Eye,
  EyeOff,
  Settings,
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import TopBar from '@/components/TopBar';
import { useWebSocketLogs, LogEntry } from '@/hooks/use-websocket-logs';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';

export default function LiveLogViewerPage() {
  const params = useParams();
  const router = useRouter();
  const connectionId = params.connectionId as string;
  const { theme, resolvedTheme } = useTheme();
  const { sidebarCollapsed: collapsed } = useUIStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';

  const { logs: wsLogs, isConnected } = useWebSocketLogs(connectionId);
  const [historicalLogs, setHistoricalLogs] = useState<LogEntry[]>([]);
  const [allLogs, setAllLogs] = useState<LogEntry[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLevels, setSelectedLevels] = useState<Set<string>>(
    new Set(['ERROR', 'WARN', 'INFO', 'DEBUG'])
  );
  const [autoScroll, setAutoScroll] = useState(true);
  const [showMetadata, setShowMetadata] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    errors: 0,
    warnings: 0,
    info: 0,
  });

  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  // Fetch historical logs on mount
  useEffect(() => {
    const fetchHistoricalLogs = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(
          `http://localhost:8000/api/v1/live-logs/connections/${connectionId}/logs?limit=100`,
          {
            headers: { 'Authorization': `Bearer ${token}` },
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          setHistoricalLogs(data);
          // Initialize stats from historical logs
          const initialStats = {
            total: data.length,
            errors: data.filter((log: LogEntry) => log.level?.toUpperCase() === 'ERROR' || log.level?.toUpperCase() === 'FATAL').length,
            warnings: data.filter((log: LogEntry) => log.level?.toUpperCase() === 'WARN' || log.level?.toUpperCase() === 'WARNING').length,
            info: data.filter((log: LogEntry) => log.level?.toUpperCase() === 'INFO').length,
          };
          setStats(initialStats);
        }
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      }
    };

    fetchHistoricalLogs();
  }, [connectionId]);

  // Combine historical and WebSocket logs
  useEffect(() => {
    if (!isPaused) {
      const combined = [...wsLogs, ...historicalLogs];
      setAllLogs(combined);
      
      // Update stats from all logs
      setStats({
        total: combined.length,
        errors: combined.filter(log => log.level?.toUpperCase() === 'ERROR' || log.level?.toUpperCase() === 'FATAL').length,
        warnings: combined.filter(log => log.level?.toUpperCase() === 'WARN' || log.level?.toUpperCase() === 'WARNING').length,
        info: combined.filter(log => log.level?.toUpperCase() === 'INFO').length,
      });
    }
  }, [wsLogs, historicalLogs, isPaused]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && !isPaused && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [allLogs, autoScroll, isPaused]);

  const togglePause = () => {
    setIsPaused(!isPaused);
  };

  const clearLogs = () => {
    if (confirm('Are you sure you want to clear all logs?')) {
      setAllLogs([]);
      setHistoricalLogs([]);
      setStats({ total: 0, errors: 0, warnings: 0, info: 0 });
    }
  };

  const exportLogs = () => {
    const logsText = filteredLogs.map(log => 
      `[${log.timestamp}] [${log.level || 'INFO'}] ${log.message}${log.source ? ` [${log.source}]` : ''}`
    ).join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${connectionId}-${new Date().toISOString()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const toggleLevel = (level: string) => {
    const newLevels = new Set(selectedLevels);
    if (newLevels.has(level)) {
      newLevels.delete(level);
    } else {
      newLevels.add(level);
    }
    setSelectedLevels(newLevels);
  };

  const filteredLogs = allLogs.filter(log => {
    const level = log.level?.toUpperCase() || 'INFO';
    const matchesLevel = 
      selectedLevels.has(level) ||
      (level === 'FATAL' && selectedLevels.has('ERROR')) ||
      (level === 'WARNING' && selectedLevels.has('WARN'));
    
    const matchesSearch = !searchQuery || 
      log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.source?.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesLevel && matchesSearch;
  });

  const getLevelIcon = (level: string | null) => {
    const upperLevel = level?.toUpperCase() || 'INFO';
    switch (upperLevel) {
      case 'ERROR':
      case 'FATAL':
        return <AlertCircle className="w-4 h-4" />;
      case 'WARN':
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4" />;
      case 'INFO':
        return <Info className="w-4 h-4" />;
      case 'DEBUG':
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  const getLevelColor = (level: string | null) => {
    const upperLevel = level?.toUpperCase() || 'INFO';
    switch (upperLevel) {
      case 'ERROR':
      case 'FATAL':
        return {
          bg: 'bg-[#EF4444]/10',
          text: 'text-[#EF4444]',
          border: 'border-[#EF4444]/30',
        };
      case 'WARN':
      case 'WARNING':
        return {
          bg: 'bg-[#F59E0B]/10',
          text: 'text-[#F59E0B]',
          border: 'border-[#F59E0B]/30',
        };
      case 'INFO':
        return {
          bg: 'bg-[#2E9BFF]/10',
          text: 'text-[#2E9BFF]',
          border: 'border-[#2E9BFF]/30',
        };
      case 'DEBUG':
        return {
          bg: 'bg-[#10B981]/10',
          text: 'text-[#10B981]',
          border: 'border-[#10B981]/30',
        };
      default:
        return {
          bg: 'bg-[#64748B]/10',
          text: 'text-[#64748B]',
          border: 'border-[#64748B]/30',
        };
    }
  };

  if (!mounted) {
    return null;
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50'
    }`}>
      <Sidebar />
      <TopBar />

      {/* Main Content */}
      <motion.main
        initial={false}
        animate={{ marginLeft: collapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20 h-screen flex flex-col"
      >
        {/* Header */}
        <div className={`px-8 py-4 border-b ${
          isDark ? 'border-[#2E3A5C]/50' : 'border-gray-200'
        }`}>
          <div className="flex items-center justify-between">
            {/* Left: Title + Connection Status */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/dashboard/live-logs')}
                className={`p-2 rounded-lg transition-all ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50 text-[#F9FAFB]'
                    : 'bg-white border border-gray-200 hover:border-blue-300 text-gray-900'
                }`}
              >
                <ArrowLeft className="w-4 h-4" />
              </button>

              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#10B981] to-[#00D9FF] rounded-2xl blur-lg opacity-50 animate-pulse" />
                <div className="relative p-2.5 bg-gradient-to-br from-[#10B981] to-[#00D9FF] rounded-2xl">
                  <Activity className="w-5 h-5 text-white" />
                </div>
              </div>
              
              <div>
                <div className="flex items-center gap-3">
                  <h1 className={`text-xl font-bold ${
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  }`}>
                    Live Logs
                  </h1>
                  
                  {/* Connection Status */}
                  <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                    isConnected
                      ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50'
                      : 'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/50'
                  }`}>
                    {isConnected ? (
                      <>
                        <Wifi className="w-3 h-3" />
                        Connected
                      </>
                    ) : (
                      <>
                        <WifiOff className="w-3 h-3" />
                        Disconnected
                      </>
                    )}
                  </div>
                </div>
                <p className={`text-xs mt-0.5 ${
                  isDark ? 'text-[#64748B]' : 'text-gray-500'
                }`}>
                  Real-time log streaming • {filteredLogs.length} of {allLogs.length} logs
                </p>
              </div>
            </div>

            {/* Right: Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                onClick={togglePause}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50 text-[#F9FAFB]'
                    : 'bg-white border border-gray-200 hover:border-blue-300 text-gray-900'
                }`}
              >
                {isPaused ? (
                  <>
                    <Play className="w-4 h-4" />
                    <span className="text-sm font-medium">Resume</span>
                  </>
                ) : (
                  <>
                    <Pause className="w-4 h-4" />
                    <span className="text-sm font-medium">Pause</span>
                  </>
                )}
              </button>

              <button
                onClick={clearLogs}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  isDark
                    ? 'text-[#94A3B8] hover:text-[#EF4444] hover:bg-[#1E293B]'
                    : 'text-gray-600 hover:text-red-600 hover:bg-gray-100'
                }`}
              >
                <Trash2 className="w-4 h-4" />
                <span className="text-sm font-medium">Clear</span>
              </button>

              <button
                onClick={exportLogs}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50 text-[#F9FAFB]'
                    : 'bg-white border border-gray-200 hover:border-blue-300 text-gray-900'
                }`}
              >
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">Export</span>
              </button>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className={`p-3 rounded-lg ${
              isDark ? 'bg-[#1A1F3A]/60' : 'bg-white border border-gray-200'
            }`}>
              <div className="flex items-center gap-3">
                <Zap className="w-5 h-5 text-[#2E9BFF]" />
                <div>
                  <p className={`text-xs ${isDark ? 'text-[#64748B]' : 'text-gray-500'}`}>
                    Total
                  </p>
                  <p className={`text-xl font-bold ${isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}`}>
                    {stats.total}
                  </p>
                </div>
              </div>
            </div>

            <div className={`p-3 rounded-lg ${
              isDark ? 'bg-[#1A1F3A]/60' : 'bg-white border border-gray-200'
            }`}>
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-[#EF4444]" />
                <div>
                  <p className={`text-xs ${isDark ? 'text-[#64748B]' : 'text-gray-500'}`}>
                    Errors
                  </p>
                  <p className={`text-xl font-bold ${isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}`}>
                    {stats.errors}
                  </p>
                </div>
              </div>
            </div>

            <div className={`p-3 rounded-lg ${
              isDark ? 'bg-[#1A1F3A]/60' : 'bg-white border border-gray-200'
            }`}>
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-[#F59E0B]" />
                <div>
                  <p className={`text-xs ${isDark ? 'text-[#64748B]' : 'text-gray-500'}`}>
                    Warnings
                  </p>
                  <p className={`text-xl font-bold ${isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}`}>
                    {stats.warnings}
                  </p>
                </div>
              </div>
            </div>

            <div className={`p-3 rounded-lg ${
              isDark ? 'bg-[#1A1F3A]/60' : 'bg-white border border-gray-200'
            }`}>
              <div className="flex items-center gap-3">
                <Info className="w-5 h-5 text-[#2E9BFF]" />
                <div>
                  <p className={`text-xs ${isDark ? 'text-[#64748B]' : 'text-gray-500'}`}>
                    Info
                  </p>
                  <p className={`text-xl font-bold ${isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}`}>
                    {stats.info}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Controls Bar */}
        <div className={`px-8 py-3 border-b ${
          isDark ? 'border-[#2E3A5C]/50' : 'border-gray-200'
        }`}>
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="flex-1 relative max-w-md">
              <Search className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${
                isDark ? 'text-[#64748B]' : 'text-gray-400'
              }`} />
              <input
                type="text"
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={`w-full pl-10 pr-4 py-2 rounded-lg border transition-all text-sm ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                    : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                } focus:outline-none focus:ring-1 focus:ring-[#2E9BFF]/20`}
              />
            </div>

            {/* Level Filters */}
            <div className="flex items-center gap-2">
              {['ERROR', 'WARN', 'INFO', 'DEBUG'].map((level) => {
                const colors = getLevelColor(level);
                const isSelected = selectedLevels.has(level);

                return (
                  <button
                    key={level}
                    onClick={() => toggleLevel(level)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isSelected
                        ? `${colors.bg} ${colors.text} border ${colors.border}`
                        : isDark
                        ? 'bg-[#1A1F3A]/30 border border-[#2E3A5C]/50 text-[#64748B] hover:border-[#2E9BFF]/30'
                        : 'bg-gray-100 border border-gray-200 text-gray-500 hover:border-blue-200'
                    }`}
                  >
                    {level}
                  </button>
                );
              })}
            </div>

            {/* Auto-scroll Toggle */}
            <button
              onClick={() => setAutoScroll(!autoScroll)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                autoScroll
                  ? 'bg-[#2E9BFF]/20 text-[#2E9BFF] border border-[#2E9BFF]/50'
                  : isDark
                  ? 'bg-[#1A1F3A]/60 border border-[#2E3A5C]/50 text-[#94A3B8]'
                  : 'bg-gray-100 border border-gray-200 text-gray-600'
              }`}
            >
              {autoScroll ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
              Auto-scroll
            </button>

            {/* Show Metadata Toggle */}
            <button
              onClick={() => setShowMetadata(!showMetadata)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                showMetadata
                  ? 'bg-[#2E9BFF]/20 text-[#2E9BFF] border border-[#2E9BFF]/50'
                  : isDark
                  ? 'bg-[#1A1F3A]/60 border border-[#2E3A5C]/50 text-[#94A3B8]'
                  : 'bg-gray-100 border border-gray-200 text-gray-600'
              }`}
            >
              <Settings className="w-3 h-3" />
              Metadata
            </button>
          </div>
        </div>

        {/* Logs Display */}
        <div
          ref={logsContainerRef}
          className="flex-1 overflow-y-auto px-8 py-4"
        >
          {filteredLogs.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Activity className={`w-16 h-16 mx-auto mb-4 ${
                  isDark ? 'text-[#64748B]' : 'text-gray-400'
                }`} />
                <p className={`text-base ${
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                }`}>
                  {allLogs.length === 0 
                    ? 'Waiting for logs...' 
                    : 'No logs match the current filters'}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-1 font-mono text-sm">
              <AnimatePresence>
                {filteredLogs.map((log, index) => {
                  const colors = getLevelColor(log.level);
                  
                  return (
                    <motion.div
                      key={`${log.id || log.timestamp}-${index}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.2 }}
                      className={`flex items-start gap-3 px-4 py-2.5 rounded-lg ${
                        isDark
                          ? 'bg-[#1A1F3A]/40 hover:bg-[#1A1F3A]/60'
                          : 'bg-white hover:bg-gray-50'
                      } border ${isDark ? 'border-[#2E3A5C]/30' : 'border-gray-200'} transition-colors`}
                    >
                      {/* Timestamp */}
                      <span className={`flex-shrink-0 text-xs ${
                        isDark ? 'text-[#64748B]' : 'text-gray-500'
                      }`}>
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>

                      {/* Level Badge */}
                      <span className={`flex-shrink-0 flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-semibold ${
                        colors.bg
                      } ${colors.text} border ${colors.border}`}>
                        {getLevelIcon(log.level)}
                        {log.level || 'INFO'}
                      </span>

                      {/* Source */}
                      {log.source && (
                        <span className={`flex-shrink-0 text-xs ${
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        }`}>
                          [{log.source}]
                        </span>
                      )}

                      {/* Message */}
                      <span className={`flex-1 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        {log.message}
                      </span>

                      {/* Metadata */}
                      {showMetadata && log.is_error !== undefined && (
                        <div className={`flex-shrink-0 text-xs ${
                          isDark ? 'text-[#64748B]' : 'text-gray-500'
                        }`}>
                          {log.is_error && 'Error '}
                          {log.is_anomaly && 'Anomaly'}
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </AnimatePresence>
              <div ref={logsEndRef} />
            </div>
          )}
        </div>

        {/* Footer Status */}
        <div className={`px-8 py-3 border-t ${
          isDark ? 'border-[#2E3A5C]/50 bg-[#0A0E1A]' : 'border-gray-200 bg-white'
        }`}>
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-4">
              <span className={isDark ? 'text-[#64748B]' : 'text-gray-500'}>
                Showing {filteredLogs.length} of {allLogs.length} logs
              </span>
              {isPaused && (
                <span className="flex items-center gap-2 text-[#F59E0B]">
                  <Pause className="w-3 h-3" />
                  Streaming paused
                </span>
              )}
            </div>
            <span className={isDark ? 'text-[#64748B]' : 'text-gray-500'}>
              Auto-scroll: {autoScroll ? 'ON' : 'OFF'} • Metadata: {showMetadata ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
      </motion.main>
    </div>
  );
}